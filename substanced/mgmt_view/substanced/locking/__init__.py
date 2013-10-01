""" Advisory exclusive DAV-style locks for content objects.

When a resource is locked, it is presumed that its SDI UI will display a
warning to users who do not hold the lock.  The locking service can also be
used by add-ons such as DAV implementations.
"""

import datetime
import uuid
import pytz

from zope.interface import implementer

from persistent import Persistent

import colander
import deform_bootstrap
import deform.widget

from pyramid.location import lineage
from pyramid.security import has_permission
from pyramid.threadlocal import get_current_registry
from pyramid.traversal import resource_path

from substanced.interfaces import (
    ILockService,
    WriteLock,
    UserToLock,
    )
from substanced.content import (
    content,
    service
    )
from substanced.folder import (
    _AutoNamingFolder,
    Folder,
    )
from substanced.objectmap import (
    reference_target_property,
    reference_targetid_property,
    )
from substanced.property import PropertySheet
from substanced.util import (
    find_objectmap,
    find_service,
    get_oid,
    )
from substanced.schema import Schema
from substanced._compat import INT_TYPES

class LockingError(Exception):
    def __init__(self, lock):
        self.lock = lock

class LockError(LockingError):
    """ Raised when a lock cannot be created due to a conflicting lock.

    Instances of this class have a ``lock`` attribute which is a
    :class:`substanced.locking.Lock` object, representing the conflicting
    lock.
    """

class UnlockError(LockingError):
    """ Raised when a lock cannot be removed

    This may be because the owner suplied in the unlock request does not
    match the owner of the lock, or becaues the lock no longer exists.

    Instances of this class have a ``lock`` attribute which is a
    :class:`substanced.locking.Lock` object, representing the conflicting lock,
    or ``None`` if there was no lock to unlock.
    """

def now():
    return datetime.datetime.utcnow().replace(tzinfo=pytz.UTC)

class LockOwnerSchema(colander.SchemaNode):
    title = 'Owner'
    schema_type = colander.Int

    @property
    def widget(self):
        context = self.bindings['context']
        principals = find_service(context, 'principals')
        if principals is None:
            values = [] # fbo dump/load
        else:
            values = [(get_oid(group), name) for name, group in
                      principals['users'].items()]
        return deform_bootstrap.widget.ChosenSingleWidget(values=values)

    def validator(self, node, value):
        context = self.bindings['context']
        objectmap = find_objectmap(context)
        if not value in objectmap.objectid_to_path:
            raise colander.Invalid(node, 'Not a valid userid %r' % value)

class LockResourceSchema(colander.SchemaNode):
    title = 'Resource Path'
    schema_type = colander.String
    widget = deform.widget.TextInputWidget()
    missing = colander.null

    def preparer(self, value):
        context = self.bindings['context']
        request = self.bindings['request']
        objectmap = find_objectmap(context)
        if value is colander.null:
            return colander.null
        try:
            resource = objectmap.object_for(tuple(value.split('/')))
        except ValueError:
            return None
        if not has_permission('sdi.lock', resource, request):
            return False
        return resource

    def validator(self, node, value):
        if value is None:
            raise colander.Invalid(node, 'Resource not found')
        if value is False:
            raise colander.Invalid(
                node,
                'You do not have permission to lock this resource'
                )

class LockSchema(Schema):
    ownerid = LockOwnerSchema()
    timeout = colander.SchemaNode(
        colander.Int(),
        validator=colander.Range(0),
        default=3600,
        title='Timeout (secs)',
        )
    infinite = colander.SchemaNode(
        colander.Boolean(),
        default=False,
        missing=False,
        title='Infinite?',
        description='Locks all descendants',
        )
    last_refresh = colander.SchemaNode(
        colander.DateTime(),
        title='Last Refresh',
        default=now(),
        )
    comment = colander.SchemaNode(
        colander.String(),
        validator=colander.Length(max=255),
        missing=None,
        title='Comment',
        )
    resource = LockResourceSchema()

class LockPropertySheet(PropertySheet):
    schema = LockSchema()

    def get(self):
        result = PropertySheet.get(self)
        resource = result.get('resource')
        if resource is None:
            resource = colander.null
        else:
            resource = resource_path(resource)
        result['resource'] = resource
        return result

    def set(self, appstruct):
        resource = appstruct.get('resource')
        if resource is colander.null:
            appstruct['resource'] = None
        return PropertySheet.set(self, appstruct)

@content(
    'Lock',
    icon='icon-lock',
    add_view='add_lock',
    propertysheets = (
        ('', LockPropertySheet),
        )
    )
class Lock(Persistent):
    """ A persistent object representing a lock.
    """
    owner = reference_target_property(UserToLock)
    resource = reference_target_property(WriteLock)
    ownerid = reference_targetid_property(UserToLock)
    resourceid = reference_targetid_property(WriteLock)

    def __init__(self,
                 infinite=False,
                 timeout=3600,
                 comment=None,
                 last_refresh=None,
                ):
        self.timeout = timeout
        self.comment=comment
        self.infinite = infinite
        # last_refresh must be a datetime.datetime object with a UTC tzinfo,
        # if provided
        if last_refresh is None:
            last_refresh = now()
        self.last_refresh = last_refresh

    def refresh(self, timeout=None, when=None): # "when" is for testing
        """ Refresh the lock.

        If the timeout is not None, set the timeout for this lock too.
        """
        if timeout is not None:
            self.timeout = timeout
        if when is None: # pragma: no cover
            when = now()
        self.last_refresh = when

    def expires(self):
        """ Return the future datetime at which this lock will expire.

        For invalid locks, the returned value indicates the point in the past
        at which the lock expired.
        """
        if self.timeout is None:
            return None
        return self.last_refresh + datetime.timedelta(seconds=self.timeout)

    def is_valid(self, when=None):
        """ Return True if the lock has not expired and its resource exists.
        """
        objectmap = find_objectmap(self)
        if objectmap is not None:
            # might be None if we're not yet seated
            if self.resourceid is None:
                return False
        if when is None: # pragma: no cover
            when = now()
        expires = self.expires()
        if expires is None:
            return True
        return expires >= when

    @property
    def depth(self):
        return 'infinity' if self.infinite else '0'

    def commit_suicide(self):
        """ Remove this lock from the lock service.
        """
        del self.__parent__[self.__name__]

@service(
    'Lock Service',
    icon='icon-briefcase',
    service_name='locks',
    add_view='add_lock_service',
    )
@implementer(ILockService)
class LockService(Folder, _AutoNamingFolder):
    __sdi_addable__ = ('Lock',)

    def next_name(self, subobject):
        lock_id = str(uuid.uuid4())
        return lock_id

    def _get_ownerid(self, owner_or_ownerid):
        ownerid = get_oid(owner_or_ownerid, None)
        if ownerid is None:
            ownerid = owner_or_ownerid
        if not isinstance(ownerid, INT_TYPES):
            raise ValueError(
                'Bad value for owner_or_ownerid %r' % owner_or_ownerid
                )
        return ownerid

    def borrow_lock(
        self,
        resource,
        owner_or_ownerid,
        locktype=WriteLock,
        ):
        """ Search for an existing, avlid lock on resource.

        If not found, return None.

        If owned by 'owner_or_ownerid', return it.

        Otherwise, raise LockError.
        """
        objectmap = find_objectmap(self)
        ownerid = self._get_ownerid(owner_or_ownerid)
        locks = objectmap.targets(resource, locktype)
        for lock in locks:
            if lock.is_valid():
                if lock.ownerid == ownerid:
                    return lock
                else:
                    raise LockError(lock)
            else:
                lock.commit_suicide()
                break

    def lock(
        self,
        resource,
        owner_or_ownerid,
        timeout=None,
        comment=None,
        locktype=WriteLock,
        infinite=False,
        ):
        # NB: callers should ensure that the user has 'sdi.lock' permission
        # on the resource before calling

        lock = self.borrow_lock(resource, owner_or_ownerid, locktype)
        if lock is not None:
            when = now()
            lock.refresh(timeout, when)
            return lock

        registry = get_current_registry()
        lock = registry.content.create('Lock',
                                       )
        self.add_next(lock) # NB: must add before setting ownerid/resource
        lock.ownerid = self._get_ownerid(owner_or_ownerid)
        lock.resource = resource
        lock.timeout = timeout
        lock.comment = comment
        lock.infinite = infinite
        return lock

    def unlock(
        self,
        resource,
        owner_or_ownerid,
        locktype=WriteLock,
        ):

        # NB: callers should ensure that the user has 'sdi.lock' permission
        # on the resource before calling
        objectmap = find_objectmap(self)
        ownerid = self._get_ownerid(owner_or_ownerid)
        locks = objectmap.targets(resource, locktype)
        lock = None
        for lock in locks:
            if not lock.is_valid():
                lock.commit_suicide()
            elif lock.ownerid == ownerid:
                lock.commit_suicide()
                break
        else: # nobreak
            raise UnlockError(lock)

    def unlock_token(
        self,
        token,
        owner_or_ownerid,
        ):

        # NB: callers should ensure that the user has 'sdi.lock' permission
        # on the resource before calling
        ownerid = self._get_ownerid(owner_or_ownerid)
        lock = self.get(token)
        if lock is None:
            raise UnlockError(None)
        if not lock.is_valid():
            lock.commit_suicide()
            raise UnlockError(None)
        if lock.ownerid != ownerid:
            raise UnlockError(lock)
        lock.commit_suicide()

    def discover(self, resource,
                 include_invalid=False,
                 include_lineage=True,
                 locktype=WriteLock):
        objectmap = find_objectmap(self)
        valid = []
        if include_lineage:
            resources = lineage(resource)
        else:
            resources = [resource]
        for res in resources:
            locks = objectmap.targets(res, locktype)
            for lock in locks:
                if include_invalid or lock.is_valid():
                    valid.append(lock)
        return valid

def _get_lock_service(resource):
    locks = find_service(resource, 'locks')
    if locks is None:
        raise ValueError('No lock service in lineage')
    return locks

def lock_resource(
    resource,
    owner_or_ownerid,
    timeout=None,
    comment=None,
    locktype=WriteLock,
    infinite=False,
    ):
    """ Lock a resource using the lock service.

    If the resource is already locked by the owner supplied as
    owner_or_ownerid, refresh the lock using ``timeout``.

    If the resource is not already locked by another user, create a new lock
    with the given values.

    If the resource is already locked by a different user, raise a
    :class:`substanced.locking.LockError`

    If a Lock Service does not already exist in the lineage, a
    :exc:`ValueError` will be raised.

    .. warning::

       Callers should assert that the owner has the ``sdi.lock`` permission
       against the resource before calling this function to ensure that a user
       can't lock a resource he is not permitted to.

    """
    locks = _get_lock_service(resource)
    return locks.lock(
        resource,
        owner_or_ownerid,
        timeout=timeout,
        comment=comment,
        locktype=locktype,
        infinite=infinite,
        )

def could_lock_resource(
    resource,
    owner_or_ownerid,
    locktype=WriteLock,
    ):
    """ Check that a given owner could lock a resource using the lock service.

    If the resource is already locked by the owner supplied as
    owner_or_ownerid, calling this function will *not* refresh the lock.

    If the resource is not already locked by another user, calling this
    function will *not* create a new lock.

    If the resource is already locked by a different user, raise a
    :class:`substanced.locking.LockError`.

    If a Lock Service does not already exist in the lineage, a
    :exc:`ValueError` will be raised.

    .. warning::

       Callers should assert that the owner has the ``sdi.lock`` permission
       against the resource before calling this function to ensure that a user
       can't lock a resource he is not permitted to.
    """
    locks = _get_lock_service(resource)
    locks.borrow_lock(
        resource,
        owner_or_ownerid,
        locktype=locktype,
        ) # may raise LockError
    return True

def unlock_resource(
    resource,
    owner_or_ownerid,
    locktype=WriteLock,
    ):
    """ Unlock a resource using the lock service.

    If the resource is already locked by a user other than the owner supplied
    as ``owner_or_ownerid`` or the resource isn't already locked with this
    lock type, raise a :class:`substanced.locking.UnlockError` exception.

    Otherwise, remove the lock.

    If a Lock Service does not already exist in the lineage, a
    :exc:`ValueError` will be raised.

        .. warning::

           Callers should assert that the owner has the ``sdi.lock`` permission
           against the resource before calling this function to ensure that a
           user can't lock a resource he is not permitted to.

    """

    locks = _get_lock_service(resource)
    return locks.unlock(
        resource,
        owner_or_ownerid,
        locktype=locktype
        )

def unlock_token(
    resource,
    token,
    owner_or_ownerid,
    ):
    """ Remove a lock from the lock service based on its token.

    If the lock is owned by a user user other than the owner supplied as
    ``owner_or_ownerid`` or ``token`` doesn't identfiy a valid lock,
    raise a :class:`substanced.locking.UnlockError` exception.

    Otherwise remove the lock indicated by ``token``.

    If a Lock Service does not already exist in the lineage, a
    :exc:`ValueError` will be raised.

        .. warning::

           Callers should assert that the owner has the ``sdi.lock`` permission
           against the resource before calling this function to ensure that a
           user can't lock a resource he is not permitted to.

    """

    locks = _get_lock_service(resource)
    return locks.unlock_token(
        token,
        owner_or_ownerid,
        )

def discover_resource_locks(
    resource,
    include_invalid=False,
    include_lineage=True,
    locktype=WriteLock,
    ):
    """ Return locks related to ``resource`` for the given ``locktype``.

    Return a sequence of :class:`substanced.locking.Lock` objects.

    By default, only valid locks are returned.

    Invalid locks for the resource may exist, but they are not
    returned unless ``include_invalid`` is ``True``.

    Under normal circumstances, the length of the sequence returned will be
    either 0 (if there are no locks) or 1 (if there is any lock).

    In some special circumstances, however, when the
    :class:`substanced.locking.lock_resource` API is not used to create locks,
    there may be more than one lock of the same type related to a resource.
    """
    locks = _get_lock_service(resource)
    return locks.discover(
        resource,
        include_invalid=include_invalid,
        include_lineage=include_lineage,
        locktype=locktype
        )

def includeme(config): # pragma: no cover
    config.add_permission('sdi.lock')
    config.include('.views')
    config.include('.evolve')

