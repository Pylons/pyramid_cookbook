import calendar
import itertools
import json
import math
import os
import pstats
import tempfile
import types
try:
    import cProfile as _profile
except ImportError: # pragma: no cover (pypy)
    import profile as _profile

from zope.interface import providedBy
from zope.interface.declarations import Declaration

from pyramid.location import lineage
from pyramid.threadlocal import get_current_registry

from ..interfaces import IFolder

from .._compat import (
    parse_qsl,
    urlsplit,
    urlunsplit,
    STRING_TYPES,
    INT_TYPES,
    )

_marker = object()

class JsonDict(dict):
    def __str__(self):
        return json.dumps(self)

def coarse_datetime_repr(date):
    """Convert a datetime to an integer with 100 second granularity.

    The granularity reduces the number of index entries in a fieldindex when
    it's used in an indexview to convert a datetime value to an integer.
    """
    timetime = calendar.timegm(date.timetuple())
    return int(timetime) // 100

def postorder(startnode):
    """ Walks over nodes in a folder recursively. Yields deepest nodes first."""
    def visit(node):
        if is_folder(node):
            for name, child in sorted(node.items()):
                for result in visit(child):
                    yield result
        yield node
    return visit(startnode)

def get_oid(resource, default=_marker):
    """ Return the object identifer of ``resource``.  If ``resource`` has no
    object identifier, raise an AttributeError exception unless ``default`` was
    passed a value; if ``default`` was passed a value, return the default in
    that case."""
    try:
        return resource.__oid__
    except AttributeError:
        if default is _marker:
            raise
        return default

oid_of = get_oid

def set_oid(resource, oid):
    """ Set the object id of the resource to oid."""
    resource.__oid__ = oid

def merge_url_qs(url, **kw):
    """ Merge the query string elements of a URL with the ones in ``kw``.
    If any query string element exists in ``url`` that also exists in
    ``kw``, replace it."""
    segments = urlsplit(url)
    extra_qs = [ '%s=%s' % (k, v) for (k, v) in 
                 parse_qsl(segments.query, keep_blank_values=1) 
                 if k not in kw ]
    qs = ''
    for k, v in sorted(kw.items()):
        qs += '%s=%s&' % (k, v)
    if extra_qs:
        qs += '&'.join(extra_qs)
    else:
        qs = qs[:-1]
    return urlunsplit(
        (segments.scheme, segments.netloc, segments.path, qs, segments.fragment)
        )

class Batch(object):
    """
    Given a sequence named ``seq``, and a Pyramid request, return an
    object with the following attributes:

    ``items``

      A list representing a slice of ``seq``.  It will contain the number of
      elements in ``request.params['batch_size']`` or the ``default_size``
      number if such a key does not exist in request.params or the key is
      invalid.  The slice will begin at ``request.params['batch_num']`` or
      zero if such a key does not exist in ``request.params`` or the
      ``batch_num`` key could not successfully be converted to a positive
      integer.

    ``size``

      The value obtained from ``request.params['batch_size']`` or
      ``default_size`` if no ``batch_size`` parameter exists in
      ``request.params`` or the ``batch_size`` parameter could not
      successfully be converted to a positive interger.

    ``num``

      The value obtained from ``request.params['batch_num']`` or ``0`` if no
      ``batch_num`` parameter exists in ``request.params`` or if the
      ``batch_num`` parameter could not successfully be converted to a
      positive integer.  Batch numbers are indexed from zero, so batch ``0``
      is the first batch, batch ``1`` the second, and so forth.

    ``length``

      This is length of the current batch.  It is usually equal to ``size``
      but may be different in the very last batch.  For example, if the
      ``seq`` is ``[1,2,3,4]`` and the batch size is ``3``, the first batch's
      ``length`` will be ``3`` because the batch content will be ``[1,2,3]``;
      but the second and final batch's ``length`` will be ``1`` because the
      batch content will be ``[4]``.

    ``last``

      The batch number computed from the sequence length of the last batch
      (indexed from zero).

    ``first_url``

      The URL of the first batch.  This will be a URL with ``batch_num`` and
      ``batch_size`` in its query string.  The base URL will be taken from
      the ``url`` value passed to this function.  If a ``url`` value is not
      passed to this function, the URL will be taken from ``request.url``.
      This value will be ``None`` if the current ``batch_num`` is 0.
    
    ``prev_url``

      The URL of the previous batch.  This will be a URL with ``batch_num``
      and ``batch_size`` in its query string.  The base URL will be taken
      from the ``url`` value passed to this function.  If a ``url`` value is
      not passed to this function, the URL will be taken from
      ``request.url``.  This value will be ``None`` if there is no previous
      batch.

    ``next_url``

      The URL of the next batch.  This will be a URL with ``batch_num`` and
      ``batch_size`` in its query string.  The base URL will be taken from
      the ``url`` value passed to this function.  If a ``url`` value is not
      passed to this function, the URL will be taken from ``request.url``.
      This value will be ``None`` if there is no next batch.
        
    ``last_url``

      The URL of the next batch.  This will be a URL with ``batch_num`` and
      ``batch_size`` in its query string.  The base URL will be taken from
      the ``url`` value passed to this function.  If a ``url`` value is not
      passed to this function, the URL will be taken from ``request.url``.
      This value will be ``None`` if there is no next batch.

    ``required``
    
      ``True`` if either ``next_url`` or ``prev_url`` are ``True`` (meaning
      batching is required).

    ``multicolumn``

      ``True`` if the current view should be rendered in multiple columns.

    ``toggle_url``

      The URL to be used for the multicolumn/single column toggle button. The
      ``batch_size``, ``batch_num``, and ``multicolumn`` parameters are
      converted to their multicolumn or single column equivalents. If a user
      is viewing items 40-80 in multiple columns, the toggle will switch to
      items 40-50 in a single column. If a user is viewing items 50-60 in a
      single column, the toggle will switch to items 40-80 in multiple columns.

    ``toggle_text``

      The text to display on the multi-column/single column toggle.

    The ``seq`` passed must define ``__len__`` and ``__slice__`` methods.

    ``make_columns``

    A method to split ``items`` into a nested list representing columns.
    
    """
    def __init__(self, seq, request, url=None, default_size=10, toggle_size=40,
                 seqlen=None):
        if url is None:
            url = request.url

        try:
            num = int(request.params.get('batch_num', 0))
        except (TypeError, ValueError):
            num = 0
        if num < 0:
            num = 0

        try:
            size = int(request.params.get('batch_size', default_size))
        except (TypeError, ValueError):
            size = default_size
        if size < 1:
            size = default_size

        multicolumn = request.params.get('multicolumn', '') == 'True'

        # create multicolumn/single column toggle attributes
        if multicolumn:
            toggle_num = size * num / default_size
            toggle_size = default_size
            toggle_text = 'Single column'
        else:
            toggle_num = size * num / toggle_size
            toggle_text = 'Multi-column'

        start = num * size
        end = start + size
        items = list(itertools.islice(seq, start, end))
        length = len(items)
        if seqlen is None:
            # won't work if seq is a generator
            seqlen = len(seq)
        last = int(math.ceil(seqlen / float(size)) - 1)

        first_url = None
        prev_url = None
        next_url = None
        last_url = None
        toggle_url = None

        if num:
            first_url = merge_url_qs(url, batch_size=size, batch_num=0)
        if start >= size:
            prev_url = merge_url_qs(url, batch_size=size, batch_num=num-1)
        if seqlen > end:
            next_url = merge_url_qs(url, batch_size=size, batch_num=num+1)
        if size and (num < last):
            last_url = merge_url_qs(url, batch_size=size, batch_num=last)

        if prev_url or next_url:
            toggle_url = merge_url_qs(
                url,
                batch_size=toggle_size,
                batch_num=toggle_num,
                multicolumn=not multicolumn,
                )

        self.items = items
        self.num = num
        self.size = size
        self.length = length
        self.required = bool(prev_url or next_url)
        self.multicolumn = multicolumn
        self.toggle_url = toggle_url
        self.toggle_text = toggle_text
        self.first_url = first_url
        self.prev_url = prev_url
        self.next_url = next_url
        self.last_url = last_url
        self.last = last

    def make_columns(self, column_size=10, num_columns=4):
        """ Break ``self.items`` into a nested list representing columns."""
        columns = []
        for i in range(num_columns):
            start = i * column_size
            end = start + column_size
            part = self.items[start:end]
            columns.append(part)
        return columns

def chunks(stream, chunk_size=10000):
    """ Return a generator that will iterate over a stream (a filelike
    object) ``chunk_size`` bytes at a time."""
    while True:
        chunk = stream.read(chunk_size)
        if not chunk:
            break
        yield chunk

def acquire(resource, name, default=_marker):
    for node in lineage(resource):
        result = getattr(node, name, _marker)
        if result is not _marker:
            return result
    if default is _marker:
        raise AttributeError(name)
    return default

def get_all_permissions(registry):
    # we cache the set of all permissions, because it's a bit of an expensive
    # lookup
    permissions = getattr(registry, '_all_pyramid_permissions', None)

    if permissions is None:
        intrs = registry.introspector.get_category('permissions')
        if intrs is None:
            intrs = []
        permissions = [ intr['introspectable']['value'] for intr in intrs ]
        registry._all_pyramid_permissions = permissions

    return permissions

def renamer():
    """ Returns a property.  The getter of the property returns the
    ``__name__`` attribute of the instance on which it's defined.  The setter
    of the property calls ``rename()`` on the ``__parent__`` of the instance on
    which it's defined if the new value doesn't match the existing ``__name__``
    of the instance (this will cause ``__name__`` to be reset if the parent is
    a normal Substance D folder ).  Sample usage::

      class SomeContentType(Persistent):
          name = renamer()
    """
    def _get(self):
        return getattr(self, '__name__', None)

    def _set(self, newname):
        oldname = _get(self)
        if newname != oldname:
            parent = getattr(self, '__parent__', None)
            if parent is not None:
                parent.rename(oldname, newname)

    return property(_get, _set)

def set_acl(resource, new_acl, registry=None):
    """Change the ACL on resource to ``new_acl``, which may be a valid ACL or
    ``None``.  If ``new_acl`` is ``None``, any existing non-``None``
    ``__acl__`` attribute of the resource will be removed (via ``del
    resource.__acl__``).  Otherwise, if the resource's ``__acl__`` and the
    ``new_acl`` differ, set the resource's ``__acl__`` to ``new_acl`` via
    setattr.

    If the new ACL and the object's original ACL differ, send a
    :class:`substanced.event.ACLModified` event with the
    new ACL and the original ACL (the ``__acl__`` attribute of the resource, or
    ``None`` if it doesn't have one) as arguments to the event.

    This function will return ``True`` if a mutation to the resource's __acl__
    was performed, and ``False`` otherwise.

    If ``registry`` is passed, it should be a Pyramid registry; if it is not
    passed, this function will use the current threadlocal registry to send the
    event.
    """
    from ..event import ACLModified # avoid circdep
    old_acl = getattr(resource, '__acl__', None)
    if new_acl == old_acl:
        return False
    if new_acl is None:
        del resource.__acl__
    else:
        resource.__acl__ = new_acl
    event = ACLModified(resource, old_acl, new_acl)
    if registry is None:
        registry = get_current_registry()
    registry.subscribers((event, resource), None)
    return True

change_acl = set_acl # bw compat

def get_acl(resource, default=_marker):
    """ Return the ACL of the object or the default if the object has no ACL.
    If no default is passed, an :exc:`AttributeError` will be raised if the
    object doesn't have an ACL."""
    try:
        return resource.__acl__
    except AttributeError:
        if default is _marker:
            raise
        return default

def get_dotted_name(g):
    """ Return the dotted name of a global object. """
    name = g.__name__
    if isinstance(g, types.ModuleType):
        return name
    module = g.__module__
    return '.'.join((module, name))

def get_interfaces(obj, classes=True):
    """ Return the set of interfaces provided by ``obj``.  Include its
    __class__ if classes is True."""
    # we unwind all derived and immediate interfaces using spec.flattened()
    # (providedBy would just give us the immediate interfaces)
    provided_by = list(providedBy(obj))
    spec = Declaration(provided_by)
    ifaces = list(spec.flattened())
    if classes:
        ifaces = ifaces + [obj.__class__]
    return set(ifaces)

def get_content_type(resource, registry=None):
    """ Return the content type of a resource or ``None`` if the object has
    no content type.  If ``registry`` is not supplied, the current Pyramid
    registry will be looked up as a thread local in order to find the
    Substance D content registry."""
    if registry is None:
        registry = get_current_registry()

    return registry.content.typeof(resource)

def find_content(resource, content_type, registry=None):
    """ Return the first object in the :term:`lineage` of the resource that
    supplies the ``content_type``.  If ``registry`` is not supplied, the
    current Pyramid registry will be looked up as a thread local in order to
    find the Substance D content registry."""
    if registry is None:
        registry = get_current_registry()
    return registry.content.find(resource, content_type)

def _traverse_to(obj, names):
    for name in names:
        if not is_folder(obj):
            return None
        obj = obj.get(name, None)
        if obj is None:
            return None
    return obj

def _find_services(resource, name, subnames=(), one=False):
    L = []
    for obj in lineage(resource):
        if is_folder(obj):
            subobj = obj.get(name, None)
            if subobj is not None:
                if is_service(subobj):
                    if subnames:
                        subobj = _traverse_to(subobj, subnames)
                        if subobj is None:
                            continue
                    if one:
                        return subobj
                    L.append(subobj)
    if one:
        return None
    return L

def find_service(resource, name, *subnames):
    """ Find the first service named ``name`` in the lineage of ``resource``
    or return ``None`` if no such-named service could be found.

    If ``subnames`` is supplied, when a service named ``name`` is found in the
    lineage, it will attempt to traverse the service as a folder, finding a
    content object inside the service, and it will return it instead of the
    service object itself.  For example, ``find_service(resource, 'principals',
    'users')`` would find and return the ``users`` subobject in the
    ``principals`` service.  ``find_service(resource, 'principals', 'users',
    'fred')`` would find and return the fred subobject of the users subobject
    of the principals service, and so forth.  If ``subnames`` are supplied, and
    the named object cannot be found, the lineage search continues.
    """
    return _find_services(resource, name, subnames, one=True)
                
def find_services(resource, name, *subnames):
    """Finds all services named ``name`` in the lineage of ``resource`` and
    returns a sequence containing those service objects. The sequence will
    begin with the most deepest nested service and will end with the least
    deeply nested service.  Returns an empty sequence if no such-named
    service could be found.

    If ``subnames`` is supplied, when a service named ``name`` is found in the
    lineage, it will attempt to traverse the service as a folder, finding a
    content object inside the service, and this API will append this object
    rather than the service itself to the list of things returned.  For
    example, ``find_services(resource, 'principals', 'users')`` would find the
    ``users`` subobject in the ``principals`` service.
    ``find_services(resource, 'principals', 'users', 'fred')`` would find the
    fred subobject of the users subobject of the principals service, and so
    forth.  If ``subnames`` are supplied, whether or not the named object can
    be found, the lineage search continues.
    """
    return _find_services(resource, name, subnames)

def get_factory_type(resource):
    """ If the resource has a __factory_type__ attribute, return it.
    Otherwise return the full Python dotted name of the resource's class."""
    factory_type = getattr(resource, '__factory_type__', None)
    if factory_type is None:
        factory_type = get_dotted_name(resource.__class__)
    return factory_type

def is_folder(resource):
    """ Return ``True`` if the object is a folder, ``False`` if not. """
    return IFolder.providedBy(resource)

def is_service(resource):
    """ Returns ``True`` if the resource is a service, ``False`` if not. """
    return bool(getattr(resource, '__is_service__', False))

def find_catalogs(resource, name=None):
    """ Return all catalogs in the lineage.  If ``name`` is supplied, return
    only catalogs that have this name in the lineage, otherwise return all
    catalogs in the lineage."""
    catalogs = []
    catalog_containers = find_services(resource, 'catalogs')
    for catalog_container in catalog_containers:
        for cname, catalog in catalog_container.items():
            if name is None or name == cname:
                catalogs.append(catalog)
    return catalogs

def find_catalog(resource, name):
    """ Return the first catalog named ``name`` in the lineage of the resource
    """
    catalog_containers = find_services(resource, 'catalogs')
    for catalog_container in catalog_containers:
        for cname, catalog in catalog_container.items():
            if name == cname:
                return catalog

def find_index(resource, catalog_name, index_name):
    """ Find the first catalog named ``catalog_name`` in the lineage of the
    resource, and ask it for its ``index_name`` index; return the resulting
    index.  If either a catalog of the provided name or an index of the
    provided name does not exist, this function will return ``None``."""
    catalog = find_catalog(resource, catalog_name)
    if catalog is None:
        return None
    index = catalog.get(index_name)
    return index

def get_principal_repr(principal_or_id):
    """
    Given as ``principal_or_id`` a resource object that has a
    ``__principal_repr__`` method, return the result of calling that method
    (without arguments); it must be a string that uniquely identifies the
    principal amongst all principals in the system.
    
    Given as ``principal_or_id`` a resource object that does **not**
    have a ``__principal_repr__`` method, return the result of the
    stringification of the ``__oid__`` attribute of the resource object.

    Given an integer as ``principal_or_id``, return a stringification
    of the integer.

    Given any other string value, return it.
    """
    base_types = STRING_TYPES + INT_TYPES
    if isinstance(principal_or_id, base_types):
        return str(principal_or_id)
    prepr = getattr(principal_or_id, '__principal_repr__', None)
    if prepr is not None:
        return prepr()
    oid = get_oid(principal_or_id, None)
    if oid is not None:
        return str(oid)
    raise ValueError(principal_or_id)
            
def find_objectmap(context):
    """ Returns the object map for the root object in the lineage of the
    ``context`` or ``None`` if no objectmap can be found."""
    return acquire(context, '__objectmap__', None)

def get_icon_name(resource, request):
    """ Returns the content registry icon name of the resource or ``None`` if
    the resource type has no icon in the content registry."""
    icon = request.registry.content.metadata(resource, 'icon')
    if callable(icon):
        icon = icon(resource, request)
    return icon

def get_auditlog(context):
    """ Returns the current :class:`pyramid.audit.AuditLog` object or ``None``
    if no audit database is configured """
    conn = context._p_jar
    if conn is None:
        return None
    try:
        auditlogconn = conn.get_connection('audit')
    except KeyError:
        return None
    root = auditlogconn.root()
    auditlog = root.get('auditlog')
    if auditlog is not None:
        return auditlog

def profile(
    cmd,
    globals,
    locals,
    sort_order=(),
    callers=False
    ):# pragma: no cover
    """Allow for profiling of the entire process (e.g. during a bulk load)"""
    fd, fn = tempfile.mkstemp()
    try:
        try:
            _profile.runctx(cmd, globals, locals, fn)
        finally:
            stats = pstats.Stats(fn)
            stats.strip_dirs()
            # calls,time,cumulative and cumulative,calls,time are useful
            stats.sort_stats(*sort_order or ('cumulative', 'calls', 'time'))
            if callers:
                stats.print_callers(.3)
            else:
                stats.print_stats(.3)
    finally:
        os.remove(fn)

