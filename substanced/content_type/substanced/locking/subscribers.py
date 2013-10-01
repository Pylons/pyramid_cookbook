from substanced.interfaces import IUser

from substanced.event import subscribe_will_be_removed
from substanced.util import find_objectmap

from . import (
    UserToLock,
    WriteLock,
    )

@subscribe_will_be_removed()
def delete_locks_for_resource(event):
    """ Remove all lock objects associated with an resource when it is about to
    be removed """
    if event.moving is not None: # it's not really being removed
        return
    if event.loading: # fbo dump/load
        return
    objectmap = find_objectmap(event.parent)
    if objectmap is not None: # might be None if parent is not seated
        for oid in event.removed_oids:
            locks = objectmap.targets(oid, WriteLock)
            for lock in locks:
                lock.commit_suicide()

@subscribe_will_be_removed(IUser)
def delete_locks_for_user(event):
    """ Remove all lock objects associated with a user when it is about to be
    removed"""
    # if the principal service containing the user is removed (or any parent of
    # the user) this event won't be fired
    if event.moving is not None: # it's not really being removed
        return
    if event.loading: # fbo dump/load
        return
    objectmap = find_objectmap(event.parent)
    if objectmap is not None: # might be None if parent is not seated
        locks = objectmap.targets(event.object, UserToLock)
        for lock in locks:
            lock.commit_suicide()
