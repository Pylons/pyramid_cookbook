import random

from persistent.list import PersistentList
import BTrees
import colander
from persistent import Persistent
from pyramid.compat import is_nonstr_iter
from pyramid.traversal import (
    resource_path_tuple,
    find_resource,
    )
from zope.interface import implementer
from zope.interface.interfaces import IInterface

from ..event import subscribe_will_be_removed
from ..interfaces import IObjectMap
from ..util import (
    get_oid,
    get_factory_type,
    set_oid,
    find_objectmap,
    )
from .._compat import INT_TYPES

"""
Pathindex data structure of object map:

{pathtuple:{level:set_of_objectids, ...}, ...}

>>> map = ObjectMap()

If a object map with an otherwise empty pathindex has ``add('/a/b/c')``
called on it, and the objectid for ``/a/b/c`` winds up being ``1``, the path
index will end up looking like this:

>>> map.add('/a/b/c')
>>> map.pathindex

{(u'',):                  {3: set([1])},
 (u'', u'a'):             {2: set([1])},
 (u'', u'a', u'b'):       {1: set([1])},
 (u'', u'a', u'b', u'c'): {0: set([1])}}

(Level 0 is "this path")

If we then ``add('/a')`` and the result winds up as objectid 2, the pathindex
will look like this:

>>> map.add('/a')
>>> map.pathindex

{(u'',):                  {1: set([2]), 3: set([1])},
 (u'', u'a'):             {0: set([2]), 2: set([1])},
 (u'', u'a', u'b'):       {1: set([1])},
 (u'', u'a', u'b', u'c'): {0: set([1])}}

If we then add '/z' (and its objectid is 3):

>>> map.add('/z')
>>> map.pathindex

{(u'',):                  {1: set([2, 3]), 3: set([1])},
 (u'', u'a'):             {0: set([2]), 2: set([1])},
 (u'', u'a', u'b'):       {1: set([1])},
 (u'', u'a', u'b', u'c'): {0: set([1])},
 (u'', u'z'):             {0: set([3])}}

And so on and so forth as more items are added.  It is an error to attempt to
add an item to object map with a path that already exists in the object
map.

If '/a' (objectid 2) is then removed, the pathindex is adjusted to remove
references to the objectid represented by '/a' *and* any children
(in this case, there's a child at '/a/b/c').

>>> map.remove(2)
>>> map.pathindex

{(u'',):      {1: set([3])},
 (u'', u'z'): {0: set([3])}}
 
"""

_marker = object()

@implementer(IObjectMap)
class ObjectMap(Persistent):
    
    _v_nextid = None
    _randrange = random.randrange

    family = BTrees.family64

    def __init__(self, root, family=None):
        if family is not None:
            self.family = family
        self.objectid_to_path = self.family.OO.BTree()
        self.path_to_objectid = self.family.OO.BTree()
        self.pathindex = self.family.OO.BTree()
        self.referencemap = ReferenceMap()
        self.extentmap = ExtentMap()
        self.root = root

    def new_objectid(self):
        """ Obtain an unused integer object identifier """
        while True:
            if self._v_nextid is None:
                self._v_nextid = self._randrange(self.family.minint, 
                                                 self.family.maxint)

            objectid = self._v_nextid

            if objectid > self.family.maxint:
                self._v_nextid = None
                continue
                
            self._v_nextid += 1

            # object id zero is reserved as "irresolveable"
            if objectid != 0 and not objectid in self.objectid_to_path:
                return objectid

            self._v_nextid = None

    def objectid_for(self, obj_or_path_tuple):
        """ Returns an objectid or ``None``, given an object or a path tuple"""
        if isinstance(obj_or_path_tuple, tuple):
            path_tuple = obj_or_path_tuple
        elif hasattr(obj_or_path_tuple, '__parent__'):
            path_tuple = resource_path_tuple(obj_or_path_tuple)
        else:
            raise ValueError(
                'objectid_for accepts a traversable object or a path tuple, '
                'got %s' % (obj_or_path_tuple,))
        return self.path_to_objectid.get(path_tuple)

    def path_for(self, objectid):
        """ Returns an path or ``None`` given an object id """
        return self.objectid_to_path.get(objectid)

    def object_for(self, objectid_or_path_tuple, context=None):
        """ Returns an object or ``None`` given an object id or a path tuple"""
        if isinstance(objectid_or_path_tuple, INT_TYPES):
            path_tuple = self.objectid_to_path.get(objectid_or_path_tuple)
        elif isinstance(objectid_or_path_tuple, tuple):
            path_tuple = objectid_or_path_tuple
        else:
            raise ValueError('Unknown input %s' % (objectid_or_path_tuple,))
        if path_tuple is None:
            return None
        try:
            return self._find_resource(context, path_tuple)
        except KeyError:
            return None

    def _find_resource(self, context, path_tuple): # replaced in tests
        if context is None:
            context = self.root
        return find_resource(context, path_tuple)

    def add(self, obj, path_tuple, duplicating=False, moving=False):
        """ Add a new object to the object map at the location specified by
        ``path_tuple`` (must be the path of the object in the object graph as
        a tuple, as returned by Pyramid's ``resource_path_tuple`` function).

        If ``duplicating`` is ``True``, replace the oid of the added object
        even if it already has one and adjust extents involving the new oid.

        If ``moving`` is ``True``, don't add any extents.

        It is an error to pass a true value for both ``duplicating`` and
        ``moving``.
        """
        if not isinstance(path_tuple, tuple):
            raise ValueError('path_tuple argument must be a tuple')

        if moving and duplicating:
            raise ValueError('Cannot be both moving and duplicating')

        objectid = get_oid(obj, _marker)

        if objectid is _marker or duplicating:
            objectid = self.new_objectid()
            set_oid(obj, objectid)

        elif objectid in self.objectid_to_path:
            raise ValueError('objectid %s already exists' % (objectid,))

        if path_tuple in self.path_to_objectid:
            raise ValueError('path %s already exists' % (path_tuple,))

        if (not moving) or duplicating:
            self.extentmap.add(obj, objectid)

        self.path_to_objectid[path_tuple] = objectid
        self.objectid_to_path[objectid] = path_tuple

        pathlen = len(path_tuple)

        for x in range(pathlen):
            els = path_tuple[:x+1]
            omap = self.pathindex.setdefault(els, self.family.IO.BTree())
            level = pathlen - len(els)
            oidset = omap.setdefault(level, self.family.IF.Set())
            oidset.add(objectid)

        return objectid

    def remove(self, obj_objectid_or_path_tuple, moving=False):
        """ Remove an object from the object map give an object, an object id
        or a path tuple.  If ``moving`` is ``False``, also remove any
        references added via ``connect`` and any extents related to the removed
        objects.

        Return a set of removed oids (including the oid related to the object
        passed).
        """
        if hasattr(obj_objectid_or_path_tuple, '__parent__'):
            path_tuple = resource_path_tuple(obj_objectid_or_path_tuple)
        elif isinstance(obj_objectid_or_path_tuple, INT_TYPES):
            path_tuple = self.objectid_to_path[obj_objectid_or_path_tuple]
        elif isinstance(obj_objectid_or_path_tuple, tuple):
            path_tuple = obj_objectid_or_path_tuple
        else:
            raise ValueError(
                'Value passed to remove must be a traversable '
                'object, an object id, or a path tuple, got %s' % (
                    (obj_objectid_or_path_tuple,)))

        pathlen = len(path_tuple)

        omap = self.pathindex.get(path_tuple)

        # rationale: if this key isn't present, no path added ever contained it
        if omap is None:
            return set()

        removed = self.family.IF.Set()
        items = omap.items()
        removepaths = []

        for k, dm in self.pathindex.items(min=path_tuple):
            if k[:pathlen] == path_tuple:
                for oidset in dm.values():
                    removed.update(oidset)
                    for oid in oidset:
                        if oid in self.objectid_to_path:
                            p = self.objectid_to_path[oid]
                            del self.objectid_to_path[oid]
                            del self.path_to_objectid[p]
                # dont mutate while iterating
                removepaths.append(k)
            else:
                break

        for k in removepaths:
            del self.pathindex[k]

        for x in range(pathlen-1):

            offset = x + 1
            els = path_tuple[:pathlen-offset]
            omap2 = self.pathindex[els]
            for level, oidset in items:

                i = level + offset
                oidset2 = omap2[i]

                for oid in oidset:
                    if oid in oidset2:
                        oidset2.remove(oid)
                        # adding to removed and removing from
                        # objectid_to_path and path_to_objectid should have
                        # been taken care of above in the for k, dm in
                        # self.pathindex.items() loop
                        assert oid in removed, oid
                        assert not oid in self.objectid_to_path, oid

                if not oidset2:
                    del omap2[i]

        if not moving:
            self.referencemap.remove(removed)
            self.extentmap.remove(removed)

        return removed

    def _get_path_tuple(self, obj_or_path_tuple):
        if hasattr(obj_or_path_tuple, '__parent__'):
            path_tuple = resource_path_tuple(obj_or_path_tuple)
        elif isinstance(obj_or_path_tuple, tuple):
            path_tuple = obj_or_path_tuple
        else:
            raise ValueError(
                'must provide a traversable object or a '
                'path tuple, got %s' % (obj_or_path_tuple,))
        return path_tuple
    
    def navgen(self, obj_or_path_tuple, depth=1):
        path_tuple = self._get_path_tuple(obj_or_path_tuple)
        return self._navgen(path_tuple, depth)

    def _navgen(self, path_tuple, depth):
        omap = self.pathindex.get(path_tuple)
        if omap is None:
            return []
        oidset = omap.get(1)
        result = []
        if oidset is None:
            return result
        newdepth = depth-1
        if newdepth > -1:
            for oid in oidset:
                pt = self.objectid_to_path[oid]
                result.append(
                    {'path':pt,
                     'children':self._navgen(pt, newdepth),
                     'name':pt[-1],
                     }
                    )
        return result

    def pathcount(self, obj_or_path_tuple, depth=None, include_origin=True):
        """ Return the total number of objectids under a given path given an
        object or a path tuple.  If ``depth`` is None, count all object ids
        under the path.  If ``depth`` is an integer, use that depth instead.
        If ``include_origin`` is ``True``, count the object identifier of the
        object that was passed, otherwise omit it."""
        path_tuple = self._get_path_tuple(obj_or_path_tuple)
        omap = self.pathindex.get(path_tuple)

        result = 0

        if omap is None:
            return result
        
        if depth is None:
            for d, oidset in omap.items():
                
                if d == 0 and not include_origin:
                    continue

                result += len(oidset)

        else:
            for d in range(depth+1):

                if d == 0 and not include_origin:
                    continue

                oidset = omap.get(d)

                if oidset is None:
                    continue
                else:
                    result += len(oidset)

        return result

    def pathlookup(self, obj_or_path_tuple, depth=None, include_origin=True):
        """ Return a set of objectids under a given path given an object or a
        path tuple.  If ``depth`` is None, return all object ids under the
        path.  If ``depth`` is an integer, use that depth instead.  If
        ``include_origin`` is ``True``, include the object identifier of the
        object that was passed, otherwise omit it from the returned set."""
        path_tuple = self._get_path_tuple(obj_or_path_tuple)
        omap = self.pathindex.get(path_tuple)

        result = self.family.IF.Set()

        if omap is None:
            return result
        
        if depth is None:
            for d, oidset in omap.items():
                
                if d == 0 and not include_origin:
                    continue

                result.update(oidset)

        else:
            for d in range(depth+1):

                if d == 0 and not include_origin:
                    continue

                oidset = omap.get(d)

                if oidset is None:
                    continue
                else:
                    result.update(oidset)

        return result

    def _refids_for(self, source, target):
        sourceid, targetid = get_oid(source, source), get_oid(target, target)
        if not sourceid in self.objectid_to_path:
            raise ValueError('source %s is not in objectmap' % (source,))
        if not targetid in self.objectid_to_path:
            raise ValueError('target %s is not in objectmap' % (target,))
        return sourceid, targetid

    def _refid_for(self, obj):
        oid = get_oid(obj, obj)
        if not oid in self.objectid_to_path:
            raise ValueError('oid %s is not in objectmap' % (obj,))
        return oid

    def order_sources(self, targetid, reftype, order=_marker):
        """ Set the ordering of the source ids of a reference relative to the
        ``targetid``.  ``order`` should be a tuple or list of oids or objects
        in the order that they should be kept in the reference map.  If the
        reftyp+targetid combination has existing reference values, the values
        in ``order`` must mention all of their oids, or a :exc:`ValueError`
        will be raised. You can unset an order for this targetid+reftype
        combination by passing ``None`` as the order."""
        if not order in (None, _marker):
            order = [ self._refid_for(x) for x in order ]
        return self.referencemap.order_sources(targetid, reftype, order)

    def order_targets(self, sourceid, reftype, order=_marker):
        """ Set the ordering of the target ids of a reference type.  ``order``
        should be a tuple (or list) of oids or objects in the order that they
        should be kept in the reference map.  If the reference type has
        existing reference values, the values in ``order`` must mention all of
        their oids, or a :exc:`ValueError` will be raised.  You can unset an
        ordering by passing ``None`` as the order. """
        if not order in (None, _marker):
            order = [ self._refid_for(x) for x in order ]
        return self.referencemap.order_targets(sourceid, reftype, order)
        
    def connect(self, source, target, reftype):
        """ Connect a source object or objectid to a target object or
        objectid using reference type ``reftype``"""
        sourceid, targetid = self._refids_for(source, target)
        self.referencemap.connect(sourceid, targetid, reftype)

    def disconnect(self, source, target, reftype):
        """ Disconnect a source object or objectid from a target object or
        objectid using reference type ``reftype``"""
        sourceid, targetid = self._refids_for(source, target)
        self.referencemap.disconnect(sourceid, targetid, reftype)

    # We make a copy of the set returned by ``targetids`` and ``sourceids``
    # because it's not atypical for callers to want to modify the
    # underlying bucket while iterating over the returned set.  For example:
    #
    # groups = objectmap.targetids(self, UserToGroup)
    # for group in groups:
    #    objectmap.disconnect(self, group, UserToGroup)
    #
    # if we don't make a copy, this kind of code will result in e.g.
    #
    #     for group in groups:
    # RuntimeError: the bucket being iterated changed size

    def _oidset(self, maybe_set):
        if isinstance(maybe_set, ListSet):
            return ListSet(maybe_set)
        return self.family.OO.Set(maybe_set)
    
    def sourceids(self, obj, reftype):
        """ Return a set of object identifiers of the objects connected to
        ``obj`` a source using reference type ``reftype``"""
        oid = self._refid_for(obj)
        return self._oidset(self.referencemap.sourceids(oid, reftype))

    def targetids(self, obj, reftype):
        """ Return a set of object identifiers of the objects connected to
        ``obj`` a target using reference type ``reftype``"""
        oid = self._refid_for(obj)
        return self._oidset(self.referencemap.targetids(oid, reftype))

    def sources(self, obj, reftype):
        """ Return a generator which will return the objects connected to
        ``obj`` as a source using reference type ``reftype``"""
        for oid in self.sourceids(obj, reftype):
            yield self.object_for(oid)

    def targets(self, obj, reftype):
        """ Return a generator which will return the objects connected to
        ``obj`` as a target using reference type ``reftype``"""
        for oid in self.targetids(obj, reftype):
            yield self.object_for(oid)

    def has_references(self, obj, reftype=None):
        """ Return true if the object participates in any reference as a source
        or a target.  ``obj`` may be an object or an oid."""
        oid = self._refid_for(obj)
        return self.referencemap.has_references(oid, reftype)

    def get_reftypes(self):
        """ Return a sequence of reference types known by this objectmap. """
        return self.referencemap.get_reftypes()

    def get_extent(self, name, default=()):
        """ Return the extent for ``name`` (typically a factory name, e.g. the
        dotted name of the content class).  It will be a TreeSet composed
        entirely of oids.  If no extent exist by this name, this will return
        the value of ``default``."""
        return self.extentmap.get(name, default)

class ExtentMap(Persistent):

    family = BTrees.family64

    def __init__(self, family=None):
        self.extent_to_oids = self.family.OO.BTree()
        self.oid_to_extents = self.family.OO.BTree()

    def add(self, obj, oid):
        # NB: we currently treat only the factory type as an extent
        factory_type = get_factory_type(obj)
        extent = self.extent_to_oids.setdefault(
            factory_type,
            self.family.II.TreeSet()
            )
        extent.add(oid)
        rextent = self.oid_to_extents.setdefault(
            oid,
            self.family.OO.TreeSet()
            )
        rextent.add(factory_type)

    def remove(self, oids):
        for oid in oids:
            extent_names = self.oid_to_extents.get(oid)
            if extent_names is not None:
                del self.oid_to_extents[oid]
                for extent_name in extent_names:
                    eoids = self.extent_to_oids.get(extent_name, ())
                    if oid in eoids:
                        eoids.remove(oid)
                        if not eoids:
                            del self.extent_to_oids[extent_name]

    def get(self, name, default=None):
        return self.extent_to_oids.get(name, default)

class ReferenceMap(Persistent):
    
    family = BTrees.family64
    
    def __init__(self, refmap=None):
        if refmap is None:
            refmap = self.family.OO.BTree()
        self.refmap = refmap

    def order_sources(self, targetid, reftype, order=_marker):
        refset = self.refmap.setdefault(reftype, ReferenceSet())
        return refset.order_sources(targetid, order)

    def order_targets(self, sourceid, reftype, order=_marker):
        refset = self.refmap.setdefault(reftype, ReferenceSet())
        return refset.order_targets(sourceid, order)
        
    def connect(self, source, target, reftype):
        refset = self.refmap.setdefault(reftype, ReferenceSet())
        refset.connect(source, target)

    def disconnect(self, source, target, reftype):
        refset = self.refmap.get(reftype)
        if refset is not None:
            refset.disconnect(source, target)

    def targetids(self, oid, reftype):
        refset = self.refmap.get(reftype)
        if refset is not None:
            return refset.targetids(oid)
        return self.family.OO.Set()

    def sourceids(self, oid, reftype):
        refset = self.refmap.get(reftype)
        if refset is not None:
            return refset.sourceids(oid)
        return self.family.OO.Set()

    def remove(self, oids):
        for refset in self.refmap.values():
            refset.remove(oids)

    def get_reftypes(self):
        return self.refmap.keys()

    def has_references(self, oid, reftype=None):
        if reftype is None: # any reference type
            for reftype, refset in self.refmap.items():
                if refset.is_target(oid) or refset.is_source(oid):
                    return True
            return False
        else:
            refset = self.refmap[reftype]
            return refset.is_target(oid) or refset.is_source(oid)

class ListSet(PersistentList):
    """ A persistent subclass of the Python list class. It overrides the
    ``insert`` method to takes a single argument (the value) instead of an
    index and a value.  ``insert`` works like ``append``."""
    def insert(self, val):
        if not val in self:
            self.append(val)

    def __repr__(self):
        return '<ListSet: %s>' % PersistentList.__repr__(self)

class ReferenceSet(Persistent):
    
    family = BTrees.family64
    oidset_class = BTrees.family64.OO.Set
    oidlist_class = ListSet

    def __init__(self):
        self.src2target = self.family.OO.BTree()
        self.target2src = self.family.OO.BTree()

    def connect(self, source, target):
        targets = self.src2target.setdefault(source, self.oidset_class())
        targets.insert(target)
        sources = self.target2src.setdefault(target, self.oidset_class())
        sources.insert(source)

    def disconnect(self, source, target):
        targets = self.src2target.get(source)
        if targets is not None:
            try:
                targets.remove(target)
            except KeyError:
                pass
            
        sources = self.target2src.get(target)
        if sources is not None:
            try:
                sources.remove(source)
            except KeyError:
                pass

    def targetids(self, oid):
        return self.src2target.get(oid, self.oidset_class())

    def is_target(self, oid):
        return oid in self.target2src

    def sourceids(self, oid):
        return self.target2src.get(oid, self.oidset_class())

    def is_source(self, oid):
        return oid in self.src2target

    def remove(self, oidset):
        # XXX is there a way to make this less expensive?
        removed = self.family.OO.Set()
        for oid in oidset:
            if oid in self.src2target:
                removed.insert(oid)
                targets = self.src2target.pop(oid)
                for target in targets:
                    oidset = self.target2src.get(target)
                    oidset.remove(oid)
                    if not oidset:
                        del self.target2src[target]
            if oid in self.target2src:
                removed.insert(oid)
                sources = self.target2src.pop(oid)
                for source in sources:
                    oidset = self.src2target.get(source)
                    oidset.remove(oid)
                    if not oidset:
                        del self.src2target[source]
        return removed

    def order_targets(self, source, order=_marker):
        if order is _marker:
            order = []
        oids = self.src2target.get(source, self.oidset_class())
        if order is None:
            if isinstance(oids, self.oidlist_class):
                # if it's ordered, we unset the order by changing the
                # class of the oid set to OOSet
                oids = self.oidset_class(oids)
                self.src2target[source] = oids
            # if it's not ordered, we don't need to do anything (prevent
            # unnecessary database write)
        else:
            if set(oids) != set(order):
                raise ValueError(
                    'The oids/objects in the order passed must mention each '
                    'object in the existing set of oids, and may not mention '
                    'any others.  Order: %s vs. oids %s' % (
                        order, list(oids))
                    )
            newoids = self.oidlist_class(order)
            if newoids != oids: # prevent an unnecessary database write
                self.src2target[source] = newoids
                oids = newoids
        return oids

    def order_sources(self, target, order=_marker):
        if order is _marker:
            order = []
        oids = self.target2src.get(target, self.oidset_class())
        if order is None:
            if isinstance(oids, self.oidlist_class):
                # if it's ordered, we unset the order by changing the
                # class of the oid set to OOSet
                oids = self.oidset_class(oids)
                self.target2src[target] = oids
            # if it's not ordered, we don't need to do anything (prevent
            # unnecessary database write)
        else:
            if set(oids) != set(order):
                raise ValueError(
                    'The oids/objects in the order passed must mention each '
                    'object in the existing set of oids, and may not mention '
                    'any others.  Order: %s vs. oids %s' % (
                        order, list(oids))
                    )
            newoids = self.oidlist_class(order)
            if newoids != oids: # prevent an unnecessary database write
                self.target2src[target] = newoids
                oids = newoids
        return oids
            
def _reference_property(reftype, resolve, orientation='source'):
    def _get(self, resolve=resolve):
        objectmap = find_objectmap(self)
        if orientation == 'source':
            oids = list(objectmap.targetids(self, reftype))
        else:
            oids = list(objectmap.sourceids(self, reftype))
        if not oids:
            return None
        else:
            assert(len(oids)==1)
            oid = oids[0]
        if resolve:
            return objectmap.object_for(oid)
        return oid

    def _set(self, oid):
        if oid == colander.null: # fbo dump/load
            return
        _del(self)
        if oid is None:
            return
        objectmap = find_objectmap(self)
        if orientation == 'source':
            objectmap.connect(self, oid, reftype)
        else:
            objectmap.connect(oid, self, reftype)

    def _del(self):
        oid = _get(self, resolve=False)
        if oid is None:
            return
        objectmap = find_objectmap(self)
        if orientation == 'source':
            objectmap.disconnect(self, oid, reftype)
        else:
            objectmap.disconnect(oid, self, reftype)

    return property(_get, _set, _del)

def reference_sourceid_property(reftype):
    """
    Returns a property which, when set, establishes an :term:`object map
    reference` between the property's instance (the source) and another
    object in the objectmap (the target) based on the reference type
    ``reftype``.  It is comparable to a Python 'weakref' between the
    persistent object instance which the property is attached to and the
    persistent target object id; when the target object or the object upon
    which the property is defined is removed from the system, the reference
    is destroyed.

    The ``reftype`` argument is a :term:`reference type`, a hashable object
    that describes the type of the relation.  See
    :meth:`substanced.objectmap.ObjectMap.connect` for more information about
    reference types.

    You can set, get, and delete the value.  When you set the value, a
    relation is formed between the object which houses the property and the
    target object id.  When you get the value, the related value (or ``None``
    if no relation exists) is returned, when you delete the value, the
    relation is destroyed and the value will revert to ``None``.

    For example:

    .. code-block:: python
       :linenos:

       # definition

       from substanced.content import content
       from substanced.objectmap import reference_sourceid_property

       @content('Profile')
       class Profile(Persistent):
           user_id = reference_sourceid_property('profile-to-userid')

       # subsequent usage of the property in a view...

       profile = registry.content.create('Profile')
       somefolder['profile'] = profile
       profile.user_id = get_oid(request.user)
       print profile.user_id # will print the oid of the user

       # if the user is later deleted by unrelated code...

       print profile.user_id # will print None

       # or if you delete the value explicitly...

       del profile.user_id
       print profile.user_id # will print None

    """
    return _reference_property(reftype, resolve=False)

def reference_targetid_property(reftype):
    """ Same as :func:`substanced.objectmap.reference_sourceid_property`,
    except the object upon which the property is defined is the *source* of
    the reference and any object assigned to the property is the target."""
    return _reference_property(reftype, resolve=False, orientation='target')

def reference_source_property(reftype):
    """
    Exactly like :func:`substanced.objectmap.reference_sourceid_property`,
    except its getter returns the *instance* related to the target instead of
    the target object id.  Likewise, its setter will accept another
    persistent object instance that has an object id.

    For example:

    .. code-block:: python
       :linenos:

       # definition

       from substanced.content import content
       from substanced.objectmap import reference_source_property

       @content('Profile')
       class Profile(Persistent):
           user = reference_source_property('profile-to-user')

       # subsequent usage of the property in a view...

       profile = registry.content.create('Profile')
       somefolder['profile'] = profile
       profile.user = request.user
       print profile.user # will print the user object

       # if the user is later deleted by unrelated code...

       print profile.user # will print None

       # or if you delete the value explicitly...

       del profile.user
       print profile.user # will print None
    
    """
    return _reference_property(reftype, resolve=True)

def reference_target_property(reftype):
    """ Same as :func:`substanced.objectmap.reference_source_property`,
    except the object upon which the property is defined is the *source* of
    the reference and any object assigned to the property is the target."""
    return _reference_property(reftype, resolve=True, orientation='target')

def _multireference_property(
    reftype,
    ignore_missing,
    resolve,
    orientation,
    ordered=False,
    ):

    def _get(self, resolve=resolve):
        objectmap = find_objectmap(self)
        return Multireference(
            self,
            objectmap,
            reftype,
            ignore_missing,
            resolve,
            orientation,
            ordered,
            )

    def _set(self, oids):
        if oids == colander.null: # fbo dump/load
            return
        if not is_nonstr_iter(oids):
            raise ValueError('Must be a sequence')
        iterable = _del(self)
        iterable.connect(oids)

    def _del(self):
        iterable = _get(self, resolve=False)
        iterable.clear()
        return iterable

    return property(_get, _set, _del)

def multireference_sourceid_property(
    reftype,
    ignore_missing=False,
    ordered=False
    ):
    """ Like :func:`substanced.objectmap.reference_sourceid_property`, but
    maintains a :class:`substanced.objectmap.Multireference` rather than an
    object id.  If ``ignore_missing`` is ``True``, attempts to connect or
    disconnect unresolveable object identifiers will not cause an exception.
    If ``order`` is ``True``, the relative ordering of references in a sequence
    will be maintained when you assign that sequence to the property and when
    you use the ``.connect`` method of the property."""
    return _multireference_property(
        reftype,
        ignore_missing=ignore_missing,
        resolve=False,
        orientation='source',
        ordered=ordered,
        )

def multireference_source_property(
    reftype,
    ignore_missing=False,
    ordered=False
    ):
    """ Like :func:`substanced.objectmap.reference_source_property`, but
    maintains a :class:`substanced.objectmap.Multireference` rather than a
    single object reference.  If ``ignore_missing`` is ``True``, attempts to
    connect or disconnect unresolveable object identifiers will not cause an
    exception.  If ``order`` is ``True``, the relative ordering of references
    in a sequence will be maintained when you assign that sequence to the
    property and when you use the ``.connect`` method of the property."""
    return _multireference_property(
        reftype,
        ignore_missing=ignore_missing,
        resolve=True,
        orientation='source',
        ordered=ordered,
        )

def multireference_targetid_property(
    reftype,
    ignore_missing=False,
    ordered=False,
    ):
    """ Like :func:`substanced.objectmap.reference_targetid_property`, but
    maintains a :class:`substanced.objectmap.Multireference` rather than an
    object id. If ``ignore_missing`` is ``True``, attempts to connect or
    disconnect unresolveable object identifiers will not cause an exception.
    If ``order`` is ``True``, the relative ordering of references in a sequence
    will be maintained when you assign that sequence to the property and when
    you use the ``.connect`` method of the property."""
    return _multireference_property(
        reftype,
        ignore_missing=ignore_missing,
        resolve=False,
        orientation='target',
        ordered=ordered,
        )

def multireference_target_property(
    reftype,
    ignore_missing=False,
    ordered=False,
    ):
    """ Like :func:`substanced.objectmap.reference_target_property`, but
    maintains a :class:`substanced.objectmap.Multireference` rather than a
    single object reference.  If ``ignore_missing`` is ``True``, attempts to
    connect or disconnect unresolveable object identifiers will not cause an
    exception.  If ``order`` is ``True``, the relative ordering of references
    in a sequence will be maintained when you assign that sequence to the
    property and when you use the ``.connect`` method of the property."""
    return _multireference_property(
        reftype,
        ignore_missing=ignore_missing,
        resolve=True,
        orientation='target',
        ordered=ordered,
        )

class Multireference(object):
    """ An iterable of objects (if ``resolve`` is true) or oids (if
    ``resolve`` is false).  Also supports the Python sequence protocol.

    Additionally supports ``connect``, ``disconnect``, and ``clear`` methods
    for mutating the relationships implied by the reference."""
    def __init__(
        self,
        context,
        objectmap,
        reftype,
        ignore_missing,
        resolve,
        orientation,
        ordered=False,
        ):
        self.context = context
        self.objectmap = objectmap
        self.reftype = reftype
        self.ignore_missing = ignore_missing
        self.resolve = resolve
        self.orientation = orientation
        self.ordered = ordered

    def get_oids(self):
        if self.orientation == 'source':
            oids = self.objectmap.targetids(self.context, self.reftype)
        else:
            oids = self.objectmap.sourceids(self.context, self.reftype)
        return oids
            
    def __nonzero__(self):
        """ Returns ``True`` if there are oids associated with this
        multireference, ``False`` if the oid list is empty. """
        return bool(self.get_oids())

    def __getitem__(self, i):
        """ Return the i'th element from the sequence of objects or object
        ids"""
        oid = self.get_oids()[i] # will barf if oids is not a ListSet
        if self.resolve:
            return self.objectmap.object_for(oid)
        return oid

    def __contains__(self, other):
        """ Return ``True`` if ``other`` is a member of the sequence managed
        by this multireference. """
        if self.resolve:
            object_for = self.objectmap.object_for
            for oid in self.get_oids():
                if object_for(oid) == other:
                    return True
            return False
        return other in self.get_oids()

    def __iter__(self):
        """ Return an iterable of object ids or objects. """
        if self.resolve:
            return iter((self.objectmap.object_for(oid) for oid in
                         self.get_oids()))
        return iter(self.get_oids())

    def __len__(self):
        """ Return the length of the sequence of objects implied by this
        multireference"""
        return len(self.get_oids())

    def set_ordered(self, ctx_oid):
        # intent: the below logic will be called, but it won't cause a write
        # if the reference is already ordered
        if self.orientation == 'source':
            self.objectmap.order_targets(ctx_oid, self.reftype, self.get_oids())
        else:
            self.objectmap.order_sources(ctx_oid, self.reftype, self.get_oids())

    def set_unordered(self, ctx_oid):
        # intent: the below logic will be called, but it won't cause a write
        # if the reference is already unordered
        if self.orientation == 'source':
            self.objectmap.order_targets(ctx_oid, self.reftype, None)
        else:
            self.objectmap.order_sources(ctx_oid, self.reftype, None)

    def connect(self, objects, ignore_missing=None):
        """ Connect ``objects`` to this reference's relationship. ``objects``
        should be a sequence of content objects or object identifiers."""
        ctx_oid = get_oid(self.context)
        if self.ordered:
            self.set_ordered(ctx_oid)
        else:
            self.set_unordered(ctx_oid)
        if ignore_missing is None:
            ignore_missing = self.ignore_missing
        for obj in objects:
            oid = get_oid(obj, obj)
            try:
                if self.orientation == 'source':
                    self.objectmap.connect(ctx_oid, oid, self.reftype)
                else:
                    self.objectmap.connect(oid, ctx_oid, self.reftype)
            except ValueError:
                if not ignore_missing:
                    raise

    def disconnect(self, objects, ignore_missing=None):
        """ Disconnect ``objects`` from this reference's relationship.
        ``objects`` should be a sequence of content objects or object
        identifiers."""
        if ignore_missing is None:
            ignore_missing = self.ignore_missing
        ctx_oid = get_oid(self.context)
        if self.ordered:
            self.set_ordered(ctx_oid)
        else:
            self.set_unordered(ctx_oid)
        for obj in objects:
            oid = get_oid(obj, obj)
            try:
                if self.orientation == 'source':
                    self.objectmap.disconnect(ctx_oid, oid, self.reftype)
                else:
                    self.objectmap.disconnect(oid, ctx_oid, self.reftype)
            except ValueError:
                if not ignore_missing:
                    raise

    def clear(self):
        """ Clear all references in this relationship. """
        self.disconnect(self.get_oids())

def has_references(context):
    objectmap = find_objectmap(context)
    if objectmap is None:
        return False
    oid = get_oid(context, None)
    if oid is None:
        return False
    return objectmap.has_references(oid)

class _ReferencedPredicate(object):
    has_references = staticmethod(has_references) # for testing
    
    def __init__(self, val, config):
        self.val = bool(val)
        self.registry = config.registry

    def text(self):
        return 'referenced = %s' % self.val

    phash = text

    def __call__(self, context, request):
        return self.has_references(context) == self.val

@subscribe_will_be_removed()
def referential_integrity(event):
    if event.moving is not None: # being moved
        return

    objectmap = find_objectmap(event.object)

    if objectmap is None:
        return

    reftypes = list(objectmap.get_reftypes())

    for oid in event.removed_oids:

        for reftype in reftypes:

            is_iface = IInterface.providedBy(reftype)

            if is_iface and reftype.queryTaggedValue('source_integrity', False):
                targetids = objectmap.targetids(oid, reftype)
                if oid in targetids:
                    targetids.remove(oid) # self-referential
                if targetids:
                    # object is a source
                    obj = objectmap.object_for(oid)
                    raise SourceIntegrityError(obj, reftype, targetids)

            if is_iface and reftype.queryTaggedValue('target_integrity', False):
                sourceids = objectmap.sourceids(oid, reftype)
                if oid in sourceids:
                    sourceids.remove(oid) # self-referential
                if sourceids:
                    # object is a target
                    obj = objectmap.object_for(oid)
                    raise TargetIntegrityError(obj, reftype, sourceids)

class ReferentialIntegrityError(Exception):
    """ Exception raised when a referential integrity constraint is violated.
    Raised before an object involved in a relation with an integrity constraint
    is removed from a folder.

    Attributes::

      obj: the object which would have been removed were its removal not
           prevented by the raising of this exception

      reftype: the reference type (usually a class)

      oids: the oids that reference the to-be-removed object.
    """
#    __name__ = '' # fbo resource_path_tuple
    def __init__(self, obj, reftype, oids):
        self.obj = obj
        self.reftype = reftype
        self.oids = oids

    def get_objects(self):
        """ Return the objects which hold a reference to the object inovlved in
        the integrity error. """
        objectmap = find_objectmap(self.obj)
        if objectmap is not None:
            for oid in self.oids:
                yield objectmap.object_for(oid)

    def get_paths(self):
        objectmap = find_objectmap(self.obj)
        if objectmap is not None:
            for oid in self.oids:
                yield '/'.join(objectmap.path_for(oid))
        

class SourceIntegrityError(ReferentialIntegrityError):
    pass

class TargetIntegrityError(ReferentialIntegrityError):
    pass


def includeme(config): # pragma: no cover
    config.add_view_predicate('referenced', _ReferencedPredicate)
    config.include('.evolve')

