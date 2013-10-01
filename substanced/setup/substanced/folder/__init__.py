import random
import string

import BTrees
from BTrees.Length import Length
from persistent import (
    Persistent,
    )
from persistent.interfaces import IPersistent
from pyramid.compat import string_types
from pyramid.location import (
    lineage,
    inside,
    )
from pyramid.threadlocal import get_current_registry
from pyramid.traversal import resource_path_tuple
from zope.copy.interfaces import (
    ICopyHook,
    ResumeCopy
    )
from zope.copy import copy
from zope.interface import (
    implementer,
    )

from ..content import content
from ..event import (
    ObjectAdded,
    ObjectWillBeAdded,
    ObjectRemoved,
    ObjectWillBeRemoved,
    )
from ..interfaces import (
    IFolder,
    IAutoNamingFolder,
    marker,
    )
from ..objectmap import find_objectmap
from ..stats import statsd_timer
from ..util import (
    get_oid,
    postorder,
    find_service,
    find_services,
    )
from .._compat import STRING_TYPES
from .._compat import u


class FolderKeyError(KeyError):
    pass

@content(
    'Folder',
    icon='icon-folder-close',
    add_view='add_folder',
    )
@implementer(IFolder)
class Folder(Persistent):
    """ A folder implementation which acts much like a Python dictionary.

    Keys must be Unicode strings; values must be arbitrary Python objects.
    """
    family = BTrees.family64

    __name__ = None
    __parent__ = None

    # Default uses ordering of underlying BTree.
    _order = None # tuple of names
    _order_oids = None # tuple of oids
    _reorderable = None

    def __init__(self, data=None, family=None):
        """ Constructor.  Data may be an initial dictionary mapping object
        name to object. """
        if family is not None:
            self.family = family
        if data is None:
            data = {}
        self.data = self.family.OO.BTree(data)
        self._num_objects = Length(len(data))

    def set_order(self, names, reorderable=None):
        """ Sets the folder order. ``names`` is a list of names for existing
        folder items, in the desired order.  All names that currently exist in
        the folder must be mentioned in ``names``, or a :exc:`ValueError` will
        be raised.

        If ``reorderable`` is passed, value, it must be ``None``, ``True`` or
        ``False``.  If it is ``None``, the reorderable flag will not be reset
        from its current value.  If it is anything except ``None``, it will be
        treated as a boolean and the reorderable flag will be set to that
        value.  The ``reorderable`` value of a folder will be returned by that
        folder's :meth:`~substanced.folder.Folder.is_reorderable` method.  The
        :meth:`~substanced.folder.Folder.is_reorderable` method is used by the
        SDI folder contents view to indicate that the folder can or cannot be
        reordered via the web UI.

        If ``reorderable`` is set to ``True``, the
        :meth:`~substanced.folder.Folder.reorder` method will work properly,
        otherwise it will raise a :exc:`ValueError` when called.
        """
        nameset = set(names)
        if len(self) != len(nameset):
            raise ValueError('Must specify all names when calling set_order')

        if len(names) != len(nameset):
            raise ValueError('No repeated items allowed in names')

        order = []
        order_oids = []

        for name in names:
            assert(isinstance(name, string_types))
            name = u(name)
            oid = get_oid(self[name])
            order.append(name)
            order_oids.append(oid)

        self._order = tuple(order)
        self._order_oids = tuple(order_oids)
        assert(len(self._order) == len(self._order_oids))

        if reorderable is not None:
            self._reorderable = bool(reorderable)

    def unset_order(self):
        """ Remove set order from a folder, making it unordered, and
        non-reorderable."""
        if self._order is not None:
            del self._order
        if self._order_oids is not None:
            del self._order_oids
        if self._reorderable is not None:
            del self._reorderable

    def reorder(self, names, before):
        """ Move one or more items from a folder into new positions inside that
        folder. ``names`` is a list of ids of existing folder subobject names,
        which will be inserted in order before the item named ``before``. All
        other items are left in the original order. If ``before`` is ``None``,
        the items will be appended after the last item in the current order. If
        this method is called on a folder which does not have an order set, or
        which is not reorderable, a :exc:`ValueError` will be raised. A
        :exc:`KeyError` is raised, if ``before`` does not correspond to any
        item, and is not ``None``."""
        if not self._reorderable:
            raise ValueError('Folder is not reorderable')

        before_idx = None

        if len(set(names)) != len(names):
            raise ValueError('No repeated values allowed in names')

        if before is not None:
            if not before in self._order:
                raise FolderKeyError(before)
            before_idx = self._order.index(before)

        assert(len(self._order) == len(self._order_oids))

        order_names = list(self._order)
        order_oids = list(self._order_oids)

        reorder_names = []
        reorder_oids = []

        for name in names:
            assert(isinstance(name, string_types))
            name = u(name)
            if not name in order_names:
                raise FolderKeyError(name)
            idx = order_names.index(name)
            oid = order_oids[idx]
            order_names[idx] = None
            order_oids[idx] = None
            reorder_names.append(name)
            reorder_oids.append(oid)

        assert(len(reorder_names) == len(reorder_oids))

        # NB: technically we could use filter(None, oids) and filter(None,
        # names) because names cannot be empty string and oid 0 is disallowed,
        # but just in case this becomes untrue later we define "filt" instead

        def filt(L):
            return [x for x in L if x is not None]

        if before_idx is None:
            order_names = filt(order_names)
            order_names.extend(reorder_names)
            order_oids = filt(order_oids)
            order_oids.extend(reorder_oids)
        else:
            before_idx_names = filt(order_names[:before_idx])
            after_idx_names = filt(order_names[before_idx:])
            before_idx_oids = filt(order_oids[:before_idx])
            after_idx_oids = filt(order_oids[before_idx:])
            assert(
                len(before_idx_names+after_idx_names) ==
                len(before_idx_oids+after_idx_oids)
                )
            order_names =  before_idx_names + reorder_names + after_idx_names
            order_oids = before_idx_oids + reorder_oids + after_idx_oids

        for oid, name in zip(order_oids, order_names):
            # belt and suspenders check
            assert oid == get_oid(self[name])

        self._order = tuple(order_names)
        self._order_oids = tuple(order_oids)

    def is_ordered(self):
        """ Return true if the folder has a manually set ordering, false
        otherwise."""
        return self._order is not None

    def is_reorderable(self):
        """ Return true if the folder can be reordered, false otherwise."""
        return self._reorderable

    def sort(self, oids, reverse=False, limit=None, **kw):
        # used by the hypatia resultset "sort" method when the folder contents
        # view uses us as a "sort index"
        if self._order_oids is not None:
            ids = [oid for oid in self._order_oids if oid in oids]
        else:
            ids = []
            for resource in self.values():
                oid = get_oid(resource)
                if oid in oids:
                    ids.append(oid)
        if reverse:
            ids = ids[::-1]
        if limit is not None:
            ids = ids[:limit]
        return ids

    def find_service(self, service_name):
        """ Return a service named by ``service_name`` in this folder *or any
        parent service folder* or ``None`` if no such service exists.  A
        shortcut for :func:`substanced.service.find_service`."""
        return find_service(self, service_name)

    def find_services(self, service_name):
        """ Returns a sequence of service objects named by ``service_name``
        in this folder's lineage or an empty sequence if no such service
        exists.  A shortcut for :func:`substanced.service.find_services`"""
        return find_services(self, service_name)

    def add_service(self, name, obj, registry=None, **kw):
        """ Add a service to this folder named ``name``."""
        if registry is None:
            registry = get_current_registry()
        kw['registry'] = registry
        self.add(name, obj, **kw)
        obj.__is_service__ = True

    def keys(self):
        """ Return an iterable sequence of object names present in the folder.

        Respect order, if set.
        """
        if self._order is not None:
            return self._order
        return self.data.keys()

    order = property(keys, set_order, unset_order) # b/c

    def __iter__(self):
        """ An alias for ``keys``
        """
        return iter(self.keys())

    def values(self):
        """ Return an iterable sequence of the values present in the folder.

        Respect ``order``, if set.
        """
        if self._order is not None:
            return [self.data[name] for name in self.keys()]
        return self.data.values()

    def items(self):
        """ Return an iterable sequence of (name, value) pairs in the folder.

        Respect ``order``, if set.
        """
        if self._order is not None:
            return [(name, self.data[name]) for name in self.keys()]
        return self.data.items()

    def __len__(self):
        """ Return the number of objects in the folder.
        """
        return self._num_objects()

    def __nonzero__(self):
        """ Return ``True`` unconditionally.
        """
        return True
    __bool__ = __nonzero__

    def __repr__(self):
        klass = self.__class__
        classname = '%s.%s' % (klass.__module__, klass.__name__)
        return '<%s object %r at %#x>' % (classname,
                                          self.__name__,
                                          id(self))

    def __getitem__(self, name):
        """ Return the object named ``name`` added to this folder or raise
        ``KeyError`` if no such object exists.  ``name`` must be a Unicode
        object or directly decodeable to Unicode using the system default
        encoding.
        """
        with statsd_timer('folder.get'):
            name = u(name)
            return self.data[name]

    def get(self, name, default=None):
        """ Return the object named by ``name`` or the default.

        ``name`` must be a Unicode object or a bytestring object.

        If ``name`` is a bytestring object, it must be decodable using the
        system default encoding.
        """
        with statsd_timer('folder.get'):
            name = u(name)
            return self.data.get(name, default)

    def __contains__(self, name):
        """ Does the container contains an object named by name?

        ``name`` must be a Unicode object or a bytestring object.

        If ``name`` is a bytestring object, it must be decodable using the
        system default encoding.
        """
        name = u(name)
        return name in self.data

    def __setitem__(self, name, other):
        """ Set object ``other' into this folder under the name ``name``.

        ``name`` must be a Unicode object or a bytestring object.

        If ``name`` is a bytestring object, it must be decodable using the
        system default encoding.

        ``name`` cannot be the empty string.

        When ``other`` is seated into this folder, it will also be decorated
        with a ``__parent__`` attribute (a reference to the folder into which
        it is being seated) and ``__name__`` attribute (the name passed in to
        this function.  It must not already have a ``__parent__`` attribute
        before being seated into the folder, or an exception will be raised.

        If a value already exists in the foldr under the name ``name``, raise
        :exc:`KeyError`.

        When this method is called, the object will be added to the objectmap,
        an :class:`substanced.event.ObjectWillBeAdded` event will be emitted
        before the object obtains a ``__name__`` or ``__parent__`` value, then
        a :class:`substanced.event.ObjectAdded` will be emitted after the
        object obtains a ``__name__`` and ``__parent__`` value.
        """
        return self.add(name, other)

    def validate_name(self, name, reserved_names=()):
        """
        Validate the ``name`` passed to ensure that it's addable to the folder.
        Returns the name decoded to Unicode if it passes all addable checks.
        It's not addable if:

        - the name is not decodeable to Unicode.

        - the name starts with ``@@`` (conflicts with explicit view names).

        - the name has slashes in it (WSGI limitation).

        - the name is empty.

        If any of these conditions are untrue, raise a :exc:`ValueError`.  If
        the name passed is in the list of ``reserved_names``, raise a
        :exc:`ValueError`.
        """
        if not isinstance(name, STRING_TYPES):
            raise ValueError("Name must be a string rather than a %s" %
                             name.__class__.__name__)
        if not name:
            raise ValueError("Name must not be empty")

        try:
            name = u(name)
        except UnicodeDecodeError: #pragma NO COVER (on Py3k)
            raise ValueError('Name "%s" not decodeable to unicode' % name)

        if name in reserved_names:
            raise ValueError('%s is a reserved name' % name)

        if name.startswith('@@'):
            raise ValueError('Names which start with "@@" are not allowed')

        if '/' in name:
            raise ValueError('Names which contain a slash ("/") are not '
                             'allowed')

        return name

    def check_name(self, name, reserved_names=()):
        """ Perform all the validation checks implied by
        :meth:`~substanced.folder.Folder.validate_name` against the ``name``
        supplied but also fail with a
        :class:`~substanced.folder.FolderKeyError` if an object with the name
        ``name`` already exists in the folder."""

        name = self.validate_name(name, reserved_names=reserved_names)

        if name in self.data:
            raise FolderKeyError('An object named %s already exists' % name)

        return name

    def add(self, name, other, send_events=True, reserved_names=(),
            duplicating=None, moving=None, loading=False, registry=None):
        """ Same as ``__setitem__``.

        If ``send_events`` is False, suppress the sending of folder events.
        Don't allow names in the ``reserved_names`` sequence to be added.

        If ``duplicating`` not ``None``, it must be the object which is being
        duplicated; a result of a non-``None`` duplicating means that oids will
        be replaced in objectmap.  If ``moving`` is not ``None``, it must be
        the folder from which the object is moving; this will be the ``moving``
        attribute of events sent by this function too.  If ``loading`` is
        ``True``, the ``loading`` attribute of events sent as a result of
        calling this method will be ``True`` too.

        This method returns the name used to place the subobject in the
        folder (a derivation of ``name``, usually the result of
        ``self.check_name(name)``).
        """
        if registry is None:
            registry = get_current_registry()

        name = self.check_name(name, reserved_names)

        if getattr(other, '__parent__', None):
            raise ValueError(
                'obj %s added to folder %s already has a __parent__ attribute, '
                'please remove it completely from its existing parent (%s) '
                'before trying to readd it to this one' % (
                    other, self, self.__parent__)
                )

        with statsd_timer('folder.add'):

            objectmap = find_objectmap(self)

            if objectmap is not None:

                basepath = resource_path_tuple(self)

                for node in postorder(other):
                    node_path = node_path_tuple(node)
                    path_tuple = basepath + (name,) + node_path[1:]
                    # the below gives node an objectid; if the will-be-added
                    # event is the result of a duplication, replace the oid of
                    # the node with a new one
                    objectmap.add(
                        node,
                        path_tuple,
                        duplicating=duplicating is not None,
                        moving=moving is not None,
                        )

            if send_events:
                event = ObjectWillBeAdded(
                    other, self, name, duplicating=duplicating, moving=moving,
                    loading=loading,
                    )
                self._notify(event, registry)

            other.__parent__ = self
            other.__name__ = name

            self.data[name] = other
            self._num_objects.change(1)

            if self._order is not None:
                oid = get_oid(other)
                self._order += (name,)
                self._order_oids += (oid,)

            if send_events:
                event = ObjectAdded(
                    other, self, name, duplicating=duplicating, moving=moving,
                    loading=loading,
                    )
                self._notify(event, registry)

            return name

    def pop(self, name, default=marker, registry=None):
        """ Remove the item stored in the under ``name`` and return it.

        If ``name`` doesn't exist in the folder, and ``default`` **is not**
        passed, raise a :exc:`KeyError`.

        If ``name`` doesn't exist in the folder, and ``default`` **is**
        passed, return ``default``.

        When the object stored under ``name`` is removed from this folder,
        remove its ``__parent__`` and ``__name__`` values.

        When this method is called, emit an
        :class:`substanced.event.ObjectWillBeRemoved` event before the
        object loses its ``__name__`` or ``__parent__`` values.  Emit an
        :class:`substanced.event.ObjectRemoved` after the object loses its
        ``__name__`` and ``__parent__`` value,
        """
        if registry is None:
            registry = get_current_registry()
        try:
            result = self.remove(name, registry=registry)
        except KeyError:
            if default is marker:
                raise
            return default
        return result

    def _notify(self, event, registry=None):
        if registry is None:
            registry = get_current_registry()
        registry.subscribers((event, event.object, self), None)

    def __delitem__(self, name):
        """ Remove the object from this folder stored under ``name``.

        ``name`` must be a Unicode object or a bytestring object.

        If ``name`` is a bytestring object, it must be decodable using the
        system default encoding.

        If no object is stored in the folder under ``name``, raise a
        :exc:`KeyError`.

        When the object stored under ``name`` is removed from this folder,
        remove its ``__parent__`` and ``__name__`` values.

        When this method is called, the removed object will be removed from the
        objectmap, a :class:`substanced.event.ObjectWillBeRemoved` event will
        be emitted before the object loses its ``__name__`` or ``__parent__``
        values and a :class:`substanced.event.ObjectRemoved` will be emitted
        after the object loses its ``__name__`` and ``__parent__`` value,
        """
        return self.remove(name)

    def remove(self, name, send_events=True, moving=None, loading=False,
               registry=None):
        """ Same thing as ``__delitem__``.

        If ``send_events`` is false, suppress the sending of folder events.

        If ``moving`` is not ``None``, the ``moving`` argument must be the
        folder to which the named object will be moving.  This value will be
        passed along as the ``moving`` attribute of the events sent as the
        result of this action.  If ``loading`` is ``True``, the ``loading``
        attribute of events sent as a result of calling this method will be
        ``True`` too.
        """
        name = u(name)
        other = self.data[name]
        oid = get_oid(other, None)

        if registry is None:
            registry = get_current_registry()

        with statsd_timer('folder.remove'):

            if send_events:
                event = ObjectWillBeRemoved(
                    other, self, name, moving=moving, loading=loading
                    )
                self._notify(event, registry)

            if hasattr(other, '__parent__'):
                del other.__parent__

            if hasattr(other, '__name__'):
                del other.__name__

            del self.data[name]
            self._num_objects.change(-1)

            if self._order is not None:
                assert(len(self._order) == len(self._order_oids))
                idx = self._order.index(name)
                order = list(self._order)
                order.pop(idx)
                order_oids = list(self._order_oids)
                order_oids.pop(idx)
                self._order = tuple(order)
                self._order_oids = tuple(order_oids)

            objectmap = find_objectmap(self)

            removed_oids = set([oid])

            if objectmap is not None and oid is not None:
                removed_oids = objectmap.remove(oid, moving=moving is not None)

            if send_events:
                event = ObjectRemoved(other, self, name, removed_oids,
                                      moving=moving, loading=loading)
                self._notify(event, registry)

            return other

    def copy(self, name, other, newname=None, registry=None):
        """
        Copy a subobject named ``name`` from this folder to the folder
        represented by ``other``.  If ``newname`` is not none, it is used as
        the target object name; otherwise the existing subobject name is
        used.
        """
        if newname is None:
            newname = name

        if registry is None:
            registry = get_current_registry()

        with statsd_timer('folder.copy'):
            obj = self[name]
            newobj = copy(obj)
            return other.add(
                newname, newobj, duplicating=obj, registry=registry
                )

    def move(self, name, other, newname=None, registry=None):
        """
        Move a subobject named ``name`` from this folder to the folder
        represented by ``other``.  If ``newname`` is not none, it is used as
        the target object name; otherwise the existing subobject name is
        used.

        This operation is done in terms of a remove and an add.  The Removed
        and WillBeRemoved events as well as the Added and WillBeAdded events
        sent will indicate that the object is moving.
        """
        if newname is None:
            newname = name
        if registry is None:
            registry = get_current_registry()
        ob = self.remove(
            name,
            moving=other,
            registry=registry
            )
        other.add(
            newname,
            ob,
            moving=self,
            registry=registry
            )
        return ob

    def rename(self, oldname, newname, registry=None):
        """
        Rename a subobject from oldname to newname.

        This operation is done in terms of a remove and an add.  The Removed
        and WillBeRemoved events sent will indicate that the object is
        moving.
        """
        if registry is None:
            registry = get_current_registry()
        return self.move(oldname, self, newname, registry=registry)

    def replace(self, name, newobject, send_events=True, registry=None):
        """ Replace an existing object named ``name`` in this folder with a
        new object ``newobject``.  If there isn't an object named ``name`` in
        this folder, an exception will *not* be raised; instead, the new
        object will just be added.

        This operation is done in terms of a remove and an add.  The Removed
        and WillBeRemoved events will be sent for the old object, and the
        WillBeAdded and Added events will be sent for the new object.
        """
        if registry is None:
            registry = get_current_registry()
        if name in self:
            self.remove(name, send_events=send_events)
        self.add(name, newobject, send_events=send_events, registry=registry)

    def load(self, name, newobject, registry=None):
        """ A replace method used by the code that loads an existing dump.
        Events sent during this replace will have a true ``loading`` flag."""
        if registry is None:
            registry = get_current_registry()
        if name in self:
            self.remove(name, loading=True)
        self.add(name, newobject, loading=True, registry=registry)

class _AutoNamingFolder(object):
    def add_next(
        self,
        subobject,
        send_events=True,
        duplicating=None,
        moving=None,
        registry=None
        ):
        """Add a subobject, naming it automatically, giving it the name
        returned by this folder's ``next_name`` method.  It has the same
        effect as calling :meth:`substanced.folder.Folder.add`, but you
        needn't provide a name argument.

        This method returns the name of the subobject.
        """

        name = self.next_name(subobject)

        return self.add(
            name,
            subobject,
            send_events=send_events,
            duplicating=duplicating,
            moving=moving,
            registry=registry
            )

@implementer(IAutoNamingFolder)
class SequentialAutoNamingFolder(Folder, _AutoNamingFolder):
    """ An auto-naming folder which autonames a subobject by sequentially
    incrementing the maximum key of the folder.

    Example names: ``0000001``, then ``0000002``, and so on.

    This class implements the
    :class:`substanced.interfaces.IAutoNamingFolder` interface and inherits
    from :class:`substanced.folder.Folder`.

    This class is typically used as a base class for a custom content type.
    """

    _autoname_length = 7
    _autoname_start = -1
    _autoname_reset = False

    def __init__(
        self,
        data=None,
        family=None,
        autoname_length=None,
        autoname_start=None
        ):
        """ Constructor.  Data may be an initial dictionary mapping object
        name to object. Autoname length may be supplied.  If it is not, it
        will default to 7.  Autoname start may be supplied.  If it is not, it
        will default to -1."""
        if autoname_length is not None:
            self._autoname_length = autoname_length
        if autoname_start is not None:
            self._autoname_start = autoname_start

        super(SequentialAutoNamingFolder, self).__init__(
            data=data,
            family=family,
            )

    def next_name(self, subobject):
        """Return a name string based on:

        - intifying the maximum key of this folder and adding one.

        - zero-filling the left hand side of the result with as many zeroes
          as are in the value of this folder's ``autoname_length``
          constructor value.

        If the folder has no items in it, the initial value used as a name
        will be the value of this folder's ``autoname_start`` constructor
        value.
        """
        if self._autoname_reset:
            maxkey = self._autoname_start
            self._autoname_reset = False
        else:
            try:
                maxkey = self.data.maxKey()
            except ValueError: # empty tree
                maxkey = self._autoname_start
        name = self._zfill(int(maxkey) + 1)
        return name

    def _zfill(self, name):
        return str(int(name)).zfill(self._autoname_length)

    def add(self, name, other, send_events=True, reserved_names=(),
            duplicating=None, moving=None, loading=False, registry=None):
        """ The ``add`` method of a SequentialAutoNamingFolder will raise a
        :exc:`ValueError` if the ``name`` it is passed is not intifiable, as
        its ``next_name`` method relies on controlling the types of names
        that are added to it (they must be intifiable).  It will also
        zero-fill the name passed based on this folder's ``autoname_length``
        constructor value.  It otherwise just calls its superclass' ``add``
        method and returns the result."""
        try:
            int(name)
        except:
            raise ValueError(
                'You cannot call the add method of a %s with a name that '
                'is not intifiable; you passed %r' % (
                    self.__class__.__name__,
                    name
                    )
            )
        name = self._zfill(name)
        return super(SequentialAutoNamingFolder, self).add(
            name,
            other,
            send_events=send_events,
            reserved_names=reserved_names,
            duplicating=duplicating,
            moving=moving,
            loading=loading,
            registry=registry,
            )

@implementer(IAutoNamingFolder)
class RandomAutoNamingFolder(Folder, _AutoNamingFolder):
    """An auto-naming folder which autonames a subobject using a random
    string.

    Example names: ``MXF937A``, ``FLTP2F9``.

    This class implements the
    :class:`substanced.interfaces.IAutoNamingFolder` interface and inherits
    from :class:`substanced.folder.Folder`.

    This class is typically used as a base class for a custom
    content type.    
    """

    _randomchoice = staticmethod(random.choice) # for testing
    _autoname_length = 7

    def __init__(self, data=None, family=None, autoname_length=None):
        """ Constructor.  Data may be an initial dictionary mapping object
        name to object. Autoname length may be supplied.  If it is not, it
        will default to 7."""
        if autoname_length is not None:
            self._autoname_length = autoname_length

        super(RandomAutoNamingFolder, self).__init__(
            data=data,
            family=family,
            )

    def next_name(self, subobject):
        """Return a name string based on generating a random string composed
        of digits and uppercase letters of a length determined by this
        folder's ``autoname_length`` constructor value.  It tries generatoing
        values continuously until one that is unused is found.
        """
        def randchar():
            return self._randomchoice(
                string.ascii_uppercase + string.digits
                )
        while True:
            name = ''.join([randchar() for x in range(self._autoname_length)])
            if not name in self:
                return name

def node_path_tuple(resource):
    # cant use resource_path_tuple from pyramid, it wants everything to 
    # have a __name__
    return tuple(reversed([getattr(loc, '__name__', '') for 
                           loc in lineage(resource)]))

class CopyHook(object):
    def __init__(self, context):
        self.context = context
    
    def __call__(self, toplevel, register):
        context = self.context
        # We can't register for a more specific interface than IPersistent so
        # we have to check for __parent__ here (signifiying that the object is
        # located) and do something special rather than just registering a copy
        # hook for things that are guaranteed to have a __parent__ (such as
        # Zope's ILocation)
        if hasattr(context, '__parent__'):
            if not inside(self.context, toplevel):
                # Return the object if we *don't* want it copied.  I don't
                # really quite understand why we return it instead of returning
                # None, and why we raise an exception if we *do* want it copied
                # but mine is not to wonder why.
                return context
        # Otherwise, it's a persistent object that does live inside the object
        # we're copying or a nonpersistent object.  In such cases, we
        # definitely want to copy them and we signify this desire by raising
        # ResumeCopy.
        raise ResumeCopy

def includeme(config): # pragma: no cover
    # The ICopyHook adapter avoids dumping referenced objects that are not
    # located inside an object containment-wise when that object is copied.  If
    # it is not registered, every copy winds up dumping all the objects in the
    # database due to __parent__ pointers.
    config.registry.registerAdapter(CopyHook, (IPersistent,), ICopyHook)
    config.hook_zca() # required by zope.copy (it uses a global adapter lkup)
    
