import datetime

from zope.interface.interfaces import IObjectEvent

from zope.interface import (
    Interface,
    Attribute,
    )

from zope.interface.interface import InterfaceClass

class IPropertySheet(Interface):
    """ Interface for objects with a set of properties defined by a Colander
    schema.  The class :class:`substanced.property.PropertySheet` (which is
    meant to be subclassed for specialization) implements this interface."""
    context = Attribute('The context of the property sheet (a resource)')
    request = Attribute('The current request')
    schema = Attribute('The Colander schema instance which defines '
                       'the fields related to this property sheet')

    def get():
        """ Return a dictionary representing the current property state
        compatible with the schema for serialization"""

    def set(struct, omit=()):
        """ Accept ``struct`` (a dictionary representing the property state)
        and persist it to the context, refraining from persisting the keys in
        the struct that are named in ``omit`` (a sequence of strings or a
        string).  The data structure will have already been validated against
        the propertysheet schema.

        You can return a value from this method.  It will be passed as
        ``changed`` into the ``after_set`` method.  It should be ``False`` if
        your ``set`` implementation *did not* change any persistent data.  Any
        other return value will be conventionally interpreted as the
        implementation having changed persistent data.
        """

    def after_set(changed):
        """ Perform operations after a successful set.  ``changed`` is the
        value returned from the ``set`` method.

        The default propertysheet implementation sends an ObjectModified event
        if the ``changed`` value is not ``False.``
        """

class IObjectMap(Interface):
    """ A map of objects to paths and a reference engine """
    def objectid_for(obj_or_path_tuple):
        """ Return the object id for obj_or_path_tuple """

    def path_for(objectid):
        """ Return the path tuple for objectid """

    def object_for(objectid):
        """ Return the object associated with ``objectid`` or ``None`` if the
        object cannot be found."""

    def add(obj):
        """ Add a new object to the object map.  Assigns a new objectid to
        obj.__oid__ to the object if it doesn't already have one.  The
        object's path or objectid must not already exist in the map.  Returns
        the object id.
        """

    def remove(obj_objectid_or_path_tuple):
        """ Removes an object from the object map using the object itself, an
        object id, or a path tuple.  Returns a set of objectids (children,
        inclusive) removed as the result of removing this object from the
        object map."""

    def pathlookup(obj_or_path_tuple, depth=None, include_origin=True):
        """ Returns an iterator of document ids within
        obj_or_path_tuple (a traversable object or a path tuple).  If depth
        is specified, returns only objects at that depth.  If
        ``include_origin`` is ``True``, returns the docid of the object
        passed as ``obj_or_path_tuple`` in the returned set, otherwise it
        omits it."""

    def connect(src, target, reftype):
        """Connect ``src_object`` to ``target_object`` using the reference
        type ``reftype``.  ``src`` and ``target`` may be objects or object
        identifiers."""

    def disconnect(src, target, reftype):
        """Disonnect ``src_object`` from ``target_object`` using the
        reference type ``reftype``. ``src`` and ``target`` may be objects or
        object identifiers"""

    def sources(obj, reftype):
        """ Return a generator consisting of objects which have ``obj`` as a
        relationship source using ``reftype``.  ``obj`` can be an object or
        an object id."""

    def targets(obj, reftype):
        """ Return a generator consisting of objects which have ``obj`` as a
        relationship target using ``reftype``. ``obj`` can be an object or an
        object id."""

    def targetids(obj, reftype):
        """ Return a set of objectids which have ``obj`` as a relationship
        target using ``reftype``.  ``obj`` can be an object or an object id."""

    def sourceids(obj, reftype):
        """ Return a set of objectids which have ``obj`` as a relationship
        source using ``reftype``.  ``obj`` can be an object or an object id."""

class IObjectWillBeAdded(IObjectEvent):
    """ An event type sent when an before an object is added """
    object = Attribute('The object being added')
    parent = Attribute('The folder to which the object is being added')
    name = Attribute('The name which the object is being added to the folder '
                     'with')
    moving = Attribute('None or the folder from which the object being added '
                       'was moved')
    loading = Attribute('Boolean indicating that this add is part of a load '
                        '(during a dump load process)')
    duplicating = Attribute('The object being duplicated or ``None``')

class IObjectAdded(IObjectEvent):
    """ An event type sent when an object is added """
    object = Attribute('The object being added')
    parent = Attribute('The folder to which the object is being added')
    name = Attribute('The name of the object within the folder')
    moving = Attribute('None or the folder from which the object being added '
                       'was moved')
    loading = Attribute('Boolean indicating that this add is part of a load '
                        '(during a dump load process)')
    duplicating = Attribute('The object being duplicated or ``None``')

class IObjectWillBeRemoved(IObjectEvent):
    """ An event type sent before an object is removed """
    object = Attribute('The object being removed')
    parent = Attribute('The folder from which the object is being removed')
    name = Attribute('The name of the object within the folder')
    moving = Attribute('None or the folder to which the object being removed '
                       'will be moved')
    loading = Attribute('Boolean indicating that this remove is part of a load '
                        '(during a dump load process)')

class IObjectRemoved(IObjectEvent):
    """ An event type sent when an object is removed """
    object = Attribute('The object being removed')
    parent = Attribute('The folder from which the object is being removed')
    name = Attribute('The name of the object within the folder')
    moving = Attribute('None or the folder to which the object being removed '
                       'will be moved')
    loading = Attribute('Boolean indicating that this remove is part of a load '
                        '(during a dump load process)')
    removed_oids = Attribute('The set of oids removed as the result of '
                             'this object being removed (including the oid '
                             'of the object itself).  This may be any number '
                             'of oids if the object was folderish')

class IObjectModified(IObjectEvent):
    """ May be sent when an object is modified """
    object = Attribute('The object being modified')

class IACLModified(IObjectEvent):
    """ May be sent when an object's ACL is modified """
    object = Attribute('The object being modified')
    old_acl = Attribute('The object ACL before the modification')
    new_acl = Attribute('The object ACL after the modification')

class IContentCreated(Interface):
    """ An event type sent when a Substance D content object is created 
    via ``registry.content.create``"""
    object = Attribute('The freshly created content object.  It will not yet '
                       'have been seated into any folder.')
    content_type = Attribute('The content type of the object that was created')
    meta = Attribute('The metainformation about the content type in the '
                     'content registry')

class ILoggedIn(Interface):
    """ An event type sent when a user supplies a valid username and password
    to a login view.  Note that this event is not sent on *every* request that
    the user initiates, just ones which result in an interactive login."""
    login = Attribute('The login name used by the user')
    user = Attribute('The user object computed by Substance D')
    context = Attribute('The context resource that was active during login')
    request = Attribute('The request which resulted in the login')

class IRootAdded(Interface):
    """ An event type sent when the Substance D root object has a connection to
    the database as its ``_p_jar`` attribute. """
    object = Attribute('The root object')

class IFolder(Interface):
    """ A Folder which stores objects using Unicode keys.

    All methods which accept a ``name`` argument expect the
    name to either be Unicode or a byte string decodable using the
    default system encoding or the UTF-8 encoding."""

    def set_order(value, reorderable=None):
        """Makes the folder orderable and sets its order to the list of
        names provided in value. Names should be existing names for objects
        contained in the folder at the time order is set.

        If ``reorderable`` is passed, value, it must be ``None``, ``True`` or
        ``False``.  If it is ``None``, the reorderable flag will not be reset
        from its current value.  If it is anything except ``None``, it will be
        treated as a boolean and the reorderable flag will be set to that
        value.  The ``reorderable`` value of a folder will be returned by that
        folder's :meth:`~substanced.folder.Folder.is_reorderable` method.

        The :meth:`~substanced.folder.Folder.is_reorderable` method is used by
        the SDI folder contents view to indicate that the folder can or cannot
        be reordered via the web UI.

        If ``reorderable`` is set to ``True``, the
        :meth:`~substanced.folder.Folder.reorder` method will work properly,
        otherwise it will raise a :exc:`ValueError` when called.
        """

    def unset_order():
        """Removes the folder internal ordering, making it an unordered
        folder."""

    def is_ordered():
        """ Return ``True`` if the folder has a manual ordering (e.g. its
        ``order`` attribute has been set), ``False`` otherwise."""

    def is_reorderable():
        """ Return true if the folder can be reordered, false otherwise."""

    def reorder(items, before):
        """ Move one or more items from a folder into new positions inside that
        folder. ``items`` is a list of ids of existing folder items, which will
        be inserted in order before the item named ``before``. All other items
        are left in the original order.  If this method is called on a folder
        which does not have an order set, or which is not reorderable, a
        :exc:`ValueError` will be raised."""

    def sort(oids, reverse=False, limit=None):
        """ Return the intersection of the oids of the folder's order with the
        oids passed in.  If ``reverse`` is True, reverse the result set.  If
        ``limit`` is an integer, return only that number of items (after
        reversing, if reverse is True)."""

    def keys():
        """ Return an iterable sequence of object names present in the folder.

        Respect ``order``, if set.
        """

    def __iter__():
        """ An alias for ``keys``.

        Respect ``order``, if set.
        """

    def values():
        """ Return an iterable sequence of the values present in the folder.

        Respect ``order``, if set.
        """

    def items():
        """ Return an iterable sequence of (name, value) pairs in the folder.

        Respect ``order``, if set.
        """

    def get(name, default=None):
        """ Return the object named by ``name`` or the default.

        ``name`` must be a Unicode object or a bytestring object.

        If ``name`` is a bytestring object, it must be decodable using the
        system default encoding or the UTF-8 encoding.
        """

    def __contains__(name):
        """ Does the container contains an object named by name?

        ``name`` must be a Unicode object or a bytestring object.

        If ``name`` is a bytestring object, it must be decodable using the
        system default encoding or the UTF-8 encoding.
        """

    def __nonzero__():
        """ Always return True
        """

    def __len__():
        """ Return the number of subobjects in this folder.
        """

    def __getitem__(name):
        """ Return the object represented by ``name`` in this folder or raise
        a KeyError if no such object exists. """

    def __setitem__(name, other):
        """ Set object ``other' into this folder under the name ``name``.

        ``name`` must be a Unicode object or a bytestring object.

        If ``name`` is a bytestring object, it must be decodable using the
        system default encoding or the UTF-8 encoding.

        ``name`` cannot be the empty string.

        When ``other`` is seated into this folder, it will also be
        decorated with a ``__parent__`` attribute (a reference to the
        folder into which it is being seated) and ``__name__``
        attribute (the name passed in to this function.

        If a value already exists in the foldr under the name ``name``, raise
        :exc:`KeyError`.

        When this method is called, emit an ``IObjectWillBeAdded`` event
        before the object obtains a ``__name__`` or ``__parent__`` value.
        Emit an ``IObjectAdded`` event after the object obtains a ``__name__``
        and ``__parent__`` value.
        """

    def add(name, other, send_events=True, reserved_names=(),
            duplicating=None, moving=None, loading=False, registry=None):
        """ Same as ``__setitem__``.

        If ``send_events`` is false, suppress the sending of folder events.
        Disallow the addition of the name provided is in the ``reserved_names``
        list.  If ``duplicating`` is not None, it must be the object being
        duplicated; when non-None, the ObjectWillBeAdded and ObjectAdded events
        sent will be marked as 'duplicating', which typically has the effect
        that the subobject's object id will be overwritten instead of reused.
        If ``registry`` is passed, it should be a Pyramid registry object;
        otherwise the ``pyramid.threadlocal.get_current_registry`` function is
        used to look up the current registry.

        This method returns the name used to place the subobject in the
        folder (a derivation of ``name``, usually the result of
        ``self.check_name(name)``).
        """

    def validate_name(name, reserved_names=()):
        """
        Checks the name passed for validity.  If the name is valid and is not
        present in ``reserved_names`` returns a validated name.  Otherwise a
        :exc:`ValueError` will be raised."""

    def check_name(name, reserved_names=()):
        """ Performs all checks associated with ``validate_name`` but also
        raises a :class:`substanced.folder.FolderKeyError` if an object with
        the name ``name`` already exists in the folder.  Returns the name (with
        any modifications) returned by ``validate_name``."""

    def pop(name, default=None):
        """ Remove the item stored in the under ``name`` and return it.

        If ``name`` doesn't exist in the folder, and ``default`` **is not**
        passed, raise a :exc:`KeyError`.

        If ``name`` doesn't exist in the folder, and ``default`` **is**
        passed, return ``default``.

        When the object stored under ``name`` is removed from this folder,
        remove its ``__parent__`` and ``__name__`` values.

        When this method is called, emit an ``IObjectWillBeRemoved`` event
        before the object loses its ``__name__`` or ``__parent__`` values.
        Emit an ``ObjectRemoved`` after the object loses its ``__name__``
        and ``__parent__`` value,
        """

    def __delitem__(name):
        """ Remove the object from this folder stored under ``name``.

        ``name`` must be a Unicode object or a bytestring object.

        If ``name`` is a bytestring object, it must be decodable using the
        system default encoding or the UTF-8 encoding.

        If no object is stored in the folder under ``name``, raise a
        :exc:`KeyError`.

        When the object stored under ``name`` is removed from this folder,
        remove its ``__parent__`` and ``__name__`` values.

        When this method is called, emit an ``IObjectWillBeRemoved`` event
        before the object loses its ``__name__`` or ``__parent__`` values.
        Emit an ``IObjectRemoved`` after the object loses its ``__name__``
        and ``__parent__`` value,
        """

    def remove(name, send_events=True, moving=None, loading=False):
        """ Same thing as ``__delitem__``.

        If ``send_events`` is false, suppress the sending of folder events.  If
        ``moving`` is not ``None``, it should be the folder object from which
        the object is being moved; the events sent will indicate that a move is
        in process.
        """

    def move(name, other, newname=None):
        """
        Move a subobject named ``name`` from this folder to the folder
        represented by ``other``.  If ``newname`` is not none, it is used as
        the target object name; otherwise the existing subobject name is
        used.

        This operation is done in terms of a remove and an add.  The Removed
        and WillBeRemoved events sent will indicate that the object is
        moving.
        """

    def rename(oldname, newname):
        """
        Rename a subobject from oldname to newname.

        This operation is done in terms of a remove and an add.  The Removed
        and WillBeRemoved events sent will indicate that the object is
        moving.
        """
    def replace(name, newobject):
        """ Replace an existing object named ``name`` in this folder with a
        new object ``newobject``.  If there isn't an object named ``name`` in
        this folder, an exception will *not* be raised; instead, the new
        object will just be added.

        This operation is done in terms of a remove and an add.  The Removed
        and WillBeRemoved events will be sent for the old object, and the
        WillBeAdded and Add events will be sent for the new object.
        """

    def load(name, newobject):
        """
        Same as :meth:`substanced.interfaces.IFolder.replace` except it causes
        the ``loading`` flag of added and removed events sent during the add
        and remove events implied by the replacement to be ``True``.
        """

class IAutoNamingFolder(IFolder):
    def next_name(subobject):
        """Return a name (a string) based on the autonaming policy for this
        folder.  ``subobject`` is the object being added to the folder.
        Implementations are free to ignore the ``subobject`` that is passed.
        Implementations which don't require the subobject to generate a name
        should support ``None`` as the ``subobject`` argument, in case
        calling code just needs to generate a name without actually adding a
        subobject."""

    def add_next(
        subobject,
        send_events=True,
        duplicating=None,
        moving=None,
        registry=None,
        ):
        """Add a subobject, naming it automatically, giving it the name
        returned by this folder's ``next_name`` method.  It has the same
        effect as calling :meth:`substanced.folder.Folder.add`, but you
        needn't provide a name argument.

        This method returns the name of the subobject.
        """

class ICatalog(Interface):
    """ A collection of indices. """

    objectids = Attribute(
        'a sequence of objectids that are cataloged in this catalog')

    def index_resource(resource, oid=None, action_mode=None):
        """Register the resource in indexes of this catalog using objectid
        ``oid``.  If ``oid`` is not supplied, the ``__oid__`` of the
        ``resource`` will be used.  ``action_mode``, if supplied, should be one
        of ``None``, :attr:`~substanced.interfaces.MODE_IMMEDIATE`,
        :attr:`~substanced.interfaces.MODE_ATCOMMIT` or
        :attr:`~substanced.interfaces.MODE_DEFERRED`."""

    def reindex_resource(resource, oid=None, action_mode=None):
        """Register the resource in indexes of this catalog using objectid
        ``oid``.  If ``oid`` is not supplied, the ``__oid__`` of the
        ``resource`` will be used.  ``action_mode``, if supplied, should be one
        of ``None``, :attr:`~substanced.interfaces.MODE_IMMEDIATE`,
        :attr:`~substanced.interfaces.MODE_ATCOMMIT` or
        :attr:`~substanced.interfaces.MODE_DEFERRED` indicating when the updates
        should take effect.  The ``action_mode`` value will overrule any
        action mode that a member index has been configured with.

        The result of calling this method is logically the same as calling
        ``unindex_resource``, then ``index_resource`` for the same resource/oid
        combination, but calling those two methods in succession is often more
        expensive than calling this single method, as member indexes can choose
        to do smarter things during a reindex than what they would do during an
        unindex then an index.
        """

    def unindex_resource(resource_or_oid, action_mode=None):
        """Deregister the resource in indexes of this catalog using objectid or
        resource ``resource_or_oid``.  If ``resource_or_oid`` is an integer, it
        will be used as the oid; if ``resource_or_oid`` is a resource, its
        ``__oid__`` attribute will be used as the oid.  ``action_mode``, if
        supplied, should be one of ``None``,
        :attr:`~substanced.interfaces.MODE_IMMEDIATE`,
        :attr:`~substanced.interfaces.MODE_ATCOMMIT` or
        :attr:`~substanced.interfaces.MODE_DEFERRED`."""

    def __getitem__(name):
        """ Return the index named ``name``"""

    def reset():
        """ Clear all indexes in this catalog and clear self.objectids. """

    def flush(immediate=True):
        """ Flush any pending indexing actions for all indexes in this catalog.
        If ``immediate`` is ``True``, *all* actions will be immediately
        executed.  If ``immediate`` is ``False``,
        :attr:`~substanced.interfaces.MODE_DEFERRED` actions will be sent to
        the actions processor if one is active, and all other actions will be
        executed immediately."""

    def reindex(dry_run=False, commit_interval=200, indexes=None, 
                path_re=None, output=None):
        """\
        Reindex all objects in this collection of indexes.

        If ``dry_run`` is ``True``, do no actual work but send what would be
        changed to the logger.

        ``commit_interval`` controls the number of objects indexed between
        each call to ``transaction.commit()`` (to control memory
        consumption).

        ``indexes``, if not ``None``, should be a list of index names that
        should be reindexed.  If ``indexes`` is ``None``, all indexes are
        reindexed.

        ``path_re``, if it is not ``None`` should be a regular expression
        object that will be matched against each object's path.  If the
        regular expression matches, the object will be reindexed, if it does
        not, it won't.

        ``output``, if passed should be one of ``None``, ``False`` or a
        function.  If it is a function, the function should accept a single
        message argument that will be used to record the actions taken during
        the reindex.  If ``False`` is passed, no output is done.  If ``None``
        is passed (the default), the output will wind up in the
        ``substanced.catalog`` Python logger output at ``info`` level.
        """

    def update_indexes(
        registry=None,
        dry_run=False,
        output=None,
        replace=False,
        reindex=False,
        **kw):
        """ Use the candidate indexes registered via
        ``config.add_catalog_factory`` to populate this catalog."""
                       
        
class IPrincipal(Interface):
    """ Marker interface representing a user or group """

class IUser(IPrincipal):
    """ Marker interface representing a user """

class IGroup(IPrincipal):
    """ Marker interface representing a group """

class IUsers(Interface):
    """ Marker interface representing a collection of users """

class IGroups(Interface):
    """ Marker interface representing a collection of groups """

class IPrincipals(Interface):
    """ Marker interface representing a container of users and groups """

class IPasswordResets(Interface):
    """ Marker interface representing a collection of password reset requests
    """

class IPasswordReset(Interface):
    """ Marker interface represent a password reset request """

class IFile(Interface):
    """ An object representing file content """

    blob = Attribute('The ZODB blob object holding the file content')

    mimetype = Attribute('The mimetype of the file content')

    def upload(stream, mimetype_hint=False):
        """ Replace the current contents of this file's blob with the
        contents of ``stream``.  ``mimetype_hint`` can be any of the
        folliwing:

        - ``None``, meaning don't reset the current mimetype.  This is the
          default.

        - A string containing a filename with an extension; the mimetype will
          be derived from the extension in the filename.

        - The constant :attr:`substanced.file.USE_MAGIC`, which will derive the
          content type using the ``python-magic`` library based on the
          stream's actual content.
        """

    def get_response(self, **kw):
        """ Return a WebOb-compatible response object which uses the blob
        content as the stream data and the mimetype of the file as the
        content type.  The ``**kw`` arguments will be passed to the
        ``pyramid.response.FileResponse`` constructor as its keyword
        arguments."""

    def get_size(self):
        """ Return the size in bytes of the data in the blob associated with
        the file"""

class IWorkflow(Interface):
    """ """

    def add_state(name, callback=None, **kw):
        """ """

    def add_transition(name, from_state, to_state, callback=None, **kw):
        """ """

    def check():
        """ """

    def state_of(content):
        """ """

    def has_state(content):
        """ """

    def get_states(content, request, from_state=None):
        """ """

    def initialize(content, request=None):
        """ """

    def reset(content, request=None):
        """ """

    def transition(content, request, transition_name):
        """ """
    def transition_to_state(content, request, to_state,
                            skip_same=True):
        """ """

    def get_transitions(content, request, from_state=None):
        """ """

class IDefaultWorkflow(Interface):
    """ Marker interface used internally for workflows that aren't
    associated with a particular content type"""

class IRoot(IFolder):
    pass

class ICatalogFactory(Interface):
    def replace(folder, reindex=False):
        """ Replace all the indexes in ``folder`` with the ones implied by this
        factory.  Reindex any added indexes if ``reindex`` is true."""

    def sync(folder, reindex=False):
        """ Synchronize all the indexes in ``folder`` with the ones implied by
        this factory.  Reindex any added indexes if ``reindex`` is true. """

class IIndexFactory(Interface):
    """ A factory for an index """

class IIndexView(Interface):
    def __call__(resource, default):
        """ Return a result for the index value related to the resource or the
        default."""

marker = object()

class ReferenceClass(InterfaceClass):
    def __init__(self, *arg, **kw):
        try:
            attrs = arg[2] or {}
        except IndexError:
            attrs = kw.get('attrs', {})
        si = attrs.pop('source_integrity', False)
        ti = attrs.pop('target_integrity', False)
        InterfaceClass.__init__(self, *arg, **kw)
        self.setTaggedValue('source_integrity', si)
        self.setTaggedValue('target_integrity', ti)

ReferenceType = ReferenceClass(
    "ReferenceType", __module__ = 'substanced.interfaces')

class UserToGroup(ReferenceType):
    pass

class PrincipalToACLBearing(ReferenceType):
    source_integrity = True

class UserToPasswordReset(ReferenceType):
    pass

class ISDIAPI(Interface):
    """  Easy access to common templating operations on all views.
    This object is available as ``request.sdiapi``.
    """

    main_template = Attribute("""The loaded ``master.pt`` which can
    be used in view templates with
    ``metal:use-macro="request.sdiapi.main_template"``.""")

    def get_macro(asset_spec, name=None):
        """ Return a Chameleon template macro based on the asset spec
        (e.g. ``somepackage:templates/foo.pt``) and the name.  If the name is
        None, the bare template implementation is returned, otherwise the named
        macro from within the template is returned. """

    def flash_with_undo(msg, queue='', allow_duplicate=True):
        """Display a Pyramid ``flash message`` to the appropriate
        queue with a button to allow an undo of the commit."""

    def mgmt_path(obj, *arg, **kw):
        """ Return the route_path inside the SDI for an object """

    def mgmt_url(obj, *arg, **kw):
        """ Return the route_url inside the SDI for an object """

    def breadcrumbs():
        """Return a sequence of dicts for the breadcrumb information.
        Each dict contains:

        - ``url``: The ``request.mgmt_path`` to that resource

        - ``name``: The resource ``__name__`` or 'Home' for the root

        - ``active``: Boolean representing whether the resource is
          in the breadcrumb is the current context

        - ``icon``: The full path to the icon for that resource type
        """

    def sdi_title():
        """ The ``sdi_title`` of the virtual root or "Substance D" if
         not defined """

    def mgmt_views(context):
        """ The list of management views on a resource """

class IEvolutionSteps(Interface):
    """ Utility for obtaining evolution step data """

class IIndexingActionProcessor(Interface):
    """ Processor of deferred indexing/unindexing actions of
    catalogs in the system"""

# MODE_ sentinels are classes so that when one is pickled, then unpickled, the
# result can be compared against an imported version using "is".  They are
# interfaces so they have a stable __hash__ (their __hash__ will be called as a
# result of substanced.catalog.factory is_stale and other stuff in there).

class MODE_IMMEDIATE(Interface):
    """ Sentinel indicating that an indexing action should take place as
    immediately as possible."""

class MODE_ATCOMMIT(Interface):
    """ Sentinel indicating that an indexing action should take place at the
    successful end of the current transaction."""

class MODE_DEFERRED(Interface):
    """ Sentinel indicating that an indexing action should be performed by an
    external indexing processor (e.g. ``drain_catalog_indexing``) if one is
    active at the successful end of the current transaction.  If an indexing
    processor is unavailable at the successful end of the current transaction,
    this mode will be taken to imply the same thing as
    :attr:`~substanced.interfaces.MODE_ATCOMMIT`."""

EARLIEST_DATE = datetime.datetime(1970, 1, 1)

class WriteLock(ReferenceType):
    """ Represents a DAV-style writelock.  It's a Substance D reference type
    from resource object to lock object"""

class UserToLock(ReferenceType):
    """ A reference type which represents the relationship from a user to
    his set of locks """

class ILockService(IAutoNamingFolder):
    def lock(resource, owner_or_ownerid, timeout=None, locktype=WriteLock):
        """

        Lock a resource using the lock service.  If the resource is already
        locked by the owner supplied as owner_or_ownerid, calling this method
        will refresh the lock.  If the resource is not already locked by
        another user, calling this method will create a new lock.  If the
        resource is already locked by a different user, a
        :class:`substanced.locking.LockError` will be raised.

        .. warning::

            Callers should assert that the owner has the ``sdi.lock``
            permission against the resource before calling this function to
            ensure that a user can't lock a resource he is not permitted to.

       """

    def unlock(resource, owner_or_ownerid):
        """

        Unlock a resource using the lock service.  If the resource is already
        locked by a user other than the owner supplied as owner_or_ownerid or
        the resource isn't already locked with this lock type, calling this
        method will raise a :class:`substanced.locking.LockError` exception.
        Otherwise the lock will be removed.

        .. warning::

           Callers should assert that the owner has the ``sdi.lock`` permission
           against the resource before calling this function to ensure that a
           user can't lock a resource he is not permitted to.
       """
        
class IUserLocator(Interface):
    """ Adapter responsible for returning a user by his login name and/or
    userid as well as group objects of a user by his userid."""
    
    def get_user_by_login(login):
        """ Return an IUser object or ``None`` if no such user exists. The
        ``login`` argument is the *login name* of the user, not an oid."""

    def get_user_by_userid(userid):
        """ Return an IUser object or ``None`` if no such user exists. The
        ``login`` argument is the *user id* of the user (usually an oid)."""

    def get_user_by_email(email):
        """ Return an IUser object or ``None`` if no such user exists. The
        ``email`` argument is the *email address* of the user."""
        
    def get_groupids(userid):
        """ Return all the group-related principal identifiers for a user with
        the user principal identifier ``userid`` as a sequence.  If no user
        exists under ``userid``, return ``None``."""
    
