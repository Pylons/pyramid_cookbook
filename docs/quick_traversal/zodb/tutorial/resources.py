from persistent import Persistent
from persistent.mapping import PersistentMapping
import transaction


class Folder(PersistentMapping):
    def __init__(self, title):
        PersistentMapping.__init__(self)
        self.title = title


class Root(Folder):
    __name__ = None
    __parent__ = None


class Document(Persistent):
    def __init__(self, title):
        Persistent.__init__(self)
        self.title = title


def bootstrap(zodb_root):
    if not 'tutorial' in zodb_root:
        root = Root('My Site')
        zodb_root['tutorial'] = root
        transaction.commit()
    return zodb_root['tutorial']
