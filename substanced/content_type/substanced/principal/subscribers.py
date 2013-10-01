from pyramid.security import Allow

from ..event import (
    subscribe_added,
    subscribe_will_be_removed,
    subscribe_acl_modified,
    )
from ..interfaces import (
    IUser,
    IPrincipal,
    UserToPasswordReset,
    PrincipalToACLBearing,
    )
from ..objectmap import find_objectmap
from ..util import (
    get_oid,
    postorder,
    set_acl,
    find_service,
    )
from .._compat import INT_TYPES

@subscribe_added(IUser)
def user_added(event):
    """ Give each user permission to change their own password."""
    if event.loading: # fbo dump/load
        return
    user = event.object
    user_oid = get_oid(user)
    # When a user is added to a user folder which is not yet seated in a place
    # that has an objectmap, the call to get_oid(user) above will raise an
    # AttributeError.
    set_acl(
        user,
        [(Allow, user_oid, ('sdi.view',
                            'sdi.edit-properties',
                            'sdi.change-password',
                           ))],
        registry=event.registry,
        )
    # When set_acl is called, it will end up sending an ACLModified event,
    # which will cause the acl_modified function below to be called.

@subscribe_will_be_removed(IUser)
def user_will_be_removed(event):
    """ Remove all password reset objects associated with a user when the user
    is removed """
    # if the principal service containing the user (or any other containment
    # parent of the user) is removed, this event won't be fired
    if event.moving is not None: # it's not really being removed
        return
    if event.loading: # fbo dump/load
        return
    user = event.object
    objectmap = find_objectmap(user)
    if objectmap is not None:
        resets = objectmap.targets(user, UserToPasswordReset)
        for reset in resets:
            reset.commit_suicide()

@subscribe_added(IPrincipal)
def principal_added(event):
    """ Prevent same-named users and groups from being added to the system.
    An :class:`substanced.event.IObjectAdded` event subscriber."""
    if event.loading: # fbo dump/load
        return

    # NB: don't return on event.moving; it's possible the user is being moved
    # between locations that have different user folders.

    # disallow same-named groups and users for human sanity (not because
    # same-named users and groups are disallowed by the system)
    principal = event.object
    principals = find_service(principal, 'principals')
    if principals is None:
        # fire when trying to add a principal to a folder which hasn't
        # yet been seated (raise an appropriate error, rather than letting
        # it fall through to erroring out on principals['groups'] below)
        raise ValueError(
            'No principals service in lineage when adding a principal'
            )

    principal_name = principal.__name__
    
    if IUser.providedBy(principal):
        # it's a user
        groups = principals['groups']
        if principal_name in groups:
            raise ValueError(
                'Cannot add a user with a login name the same as the '
                'group name %s' % principal_name
                )
    else:
        # it's a group
        users = principals['users']
        if principal_name in users:
            raise ValueError(
                'Cannot add a group with a name the same as the '
                'user with the login name %s' % principal_name
            )

_TO_APPEND = INT_TYPES + (tuple,)
def _referenceable_principals(acl):
    result = set()
    for ace in (acl or ()):
        principal_id = ace[1]
        if isinstance(principal_id, _TO_APPEND):
            result.add(principal_id)
    return result

@subscribe_added()
def acl_maybe_added(event):
    if event.moving is not None or event.loading:
        return False # meaningful only to tests

    obj = event.object
    objectmap = find_objectmap(obj)

    if objectmap is not None: # object might not yet be seated
        for resource in postorder(obj):
            acl = getattr(resource, '__acl__', None)
            if acl is not None:
                for princid in _referenceable_principals(acl):
                    objectmap.connect(
                        princid, resource, PrincipalToACLBearing
                        )

@subscribe_acl_modified()
def acl_modified(event):
    """ When the ACL of any object is modified, using the object map, form
    references between the principal objects named in the ACL and the
    ACL-bearing object."""
    objectmap = find_objectmap(event.object)

    if objectmap is not None: # object might not yet be seated

        old_principals = _referenceable_principals(event.old_acl)
        new_principals = _referenceable_principals(event.new_acl)

        principals_removed = old_principals.difference(new_principals)
        principals_added = new_principals.difference(old_principals)

        for princid in principals_removed:
            objectmap.disconnect(
                princid,
                event.object,
                PrincipalToACLBearing
                )

        for princid in principals_added:
            objectmap.connect(
                princid,
                event.object,
                PrincipalToACLBearing
                )
