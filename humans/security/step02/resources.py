from pyramid.security import Allow
from pyramid.security import Everyone

class Folder(dict):
    def __init__(self, name, parent, title):
        self.__name__ = name
        self.__parent__ = parent
        self.title = title


class SiteFolder(Folder):
    __acl__ = [
        (Allow, Everyone, 'view'),
        (Allow, 'group:editors', 'edit')
    ]


class Document(object):
    def __init__(self, name, parent, title):
        self.__name__ = name
        self.__parent__ = parent
        self.title = title

root = SiteFolder('', None, 'Projector Site')

from pyramid.security import DENY_ALL

def bootstrap(request):
    # Let's make:
    # /
    #   doc1
    #   doc2
    #   folder1/
    #      doc1
    doc1 = Document('doc1', root, 'Document 01')
    root['doc1'] = doc1
    doc2 = Document('doc2', root, 'Document 02')
    doc2.__acl__ = [
        (Allow, Everyone, 'view'),
        (Allow, 'group:admin', 'edit'),
        DENY_ALL
    ]
    root['doc2'] = doc2
    folder1 = Folder('folder1', root, 'Folder 01')
    root['folder1'] = folder1

    return root
