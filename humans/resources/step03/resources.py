class Folder(dict):
    def __init__(self, name, parent, title):
        self.__name__ = name
        self.__parent__ = parent
        self.title = title


class SiteFolder(Folder):
    pass


class Document(object):
    def __init__(self, name, parent, title):
        self.__name__ = name
        self.__parent__ = parent
        self.title = title


root = SiteFolder('', None, 'Projector Site')

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
    root['doc2'] = doc2
    folder1 = Folder('folder1', root, 'Folder 01')
    root['folder1'] = folder1

    # Only has to be unique in folder
    doc11 = Document('doc1', folder1, 'Document 01')
    folder1['doc1'] = doc11

    return root
