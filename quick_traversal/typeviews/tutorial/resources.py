class Folder(dict):
    def __init__(self, name, parent, title):
        self.__name__ = name
        self.__parent__ = parent
        self.title = title


class Root(Folder):
    pass


class Document(object):
    def __init__(self, name, parent, title):
        self.__name__ = name
        self.__parent__ = parent
        self.title = title

# Done outside bootstrap to persist from request to request
root = Root('', None, 'My Site')


def bootstrap(request):
    if not root.values():
        # No values yet, let's make:
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