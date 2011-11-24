class Folder(dict):
    def __init__(self, name, parent, title):
        self.__name__ = name
        self.__parent__ = parent
        self.title = title


class Document(object):
    def __init__(self, name, parent, title, body):
        self.__name__ = name
        self.__parent__ = parent
        self.title = title
        self.body = body


class Site(Folder):
    def bootstrap(self):

        # Document
        body = "<p>Project is a <em>project management system.</p>"
        root['about'] = Document('about', root, 'About Projector', body)

        # Some people
        people = People('people', root, 'People')
        root['people'] = people
        people['sstanton'] = Person('sstanton', people, 'Susan Stanton',
                                    '<p>Hello <em>Susan bio<em></p>')
        people['bbarker'] = Person('bbarker', people, 'Bob Barker',
                                   '<p>The <em>Bob bio</em> goes here</p>')

        # Some companies and projects and docs
        acme = Company('acme', root, 'ACME, Inc.')
        root['acme'] = acme
        project01 = Project('project01', acme, 'Project 01')
        acme['project01'] = project01
        project02 = Project('project02', acme, 'Project 02')
        acme['project02'] = project02
        project01['doc1'] = Document('doc1', project01, 'Document 01',
                                     '<p>Some doc of <em>stuff</em></p>')
        project01['doc2'] = Document('doc2', project01, 'Document 02',
                                     '<p>More <em>stuff</em></p>')
        folder1 = Folder('folder1', project01, 'Folder 1')
        project01['folder1'] = folder1
        folder1['doc3'] = Document('doc3', folder1, 'Document 3',
                                   '<p>A <em>really</em> deep down doc')



class People(Folder):
    pass


class Person(Document):
    pass


class Company(Folder):
    pass


class Project(Folder):
    pass

root = Site('', None, 'Home')
root.bootstrap()

def bootstrap(request):
    return root