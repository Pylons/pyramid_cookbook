from persistent import Persistent
from persistent.mapping import PersistentMapping

from repoze.catalog.indexes.text import CatalogTextIndex
from repoze.catalog.catalog import Catalog
from repoze.catalog.document import DocumentMap


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
        # add site folder
        root = SiteFolder('Projector Site')
        zodb_root['projector'] = root
        # add catalog and document map
        catalog = Catalog()
        catalog['title'] = CatalogTextIndex('title')
        catalog['content'] = CatalogTextIndex('content')
        root.catalog = catalog
        document_map = DocumentMap()
        root.document_map = document_map
    return zodb_root['projector']
