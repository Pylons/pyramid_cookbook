from .objectmap import ObjectMap
from .folder import Folder

def make_site():
    context = Folder()
    context.__oid__ = 1
    ObjectMap(context)
    users = Folder()
    users._oid__ = 2
    groups = Folder()
    groups.__oid__ = 3
    principals = Folder()
    principals.__oid__ = 4
    principals['groups'] = groups
    principals['users'] = users
    context.add_service('principals', principals)
    return context

