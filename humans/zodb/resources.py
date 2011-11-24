from persistent import Persistent
from persistent.mapping import PersistentMapping
import transaction

class Folder(PersistentMapping):
    def __init__(self, title):
        super(Folder, self).__init__()
        self.title = title


class SiteFolder(Folder):
    __name__ = None
    __parent__ = None


class Document(Persistent):
    def __init__(self, title, content):
        self.title = title
        self.content = content


def bootstrap(zodb_root):
    if not 'projector' in zodb_root:
        root = SiteFolder('Projector Site')
        zodb_root['projector'] = root
        transaction.commit()
    return zodb_root['projector']
