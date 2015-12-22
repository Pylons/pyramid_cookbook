from random import randint

from pyramid.httpexceptions import HTTPFound
from pyramid.location import lineage
from pyramid.view import view_config

from .resources import (
    Root,
    Folder,
    Document
    )


class TutorialViews(object):
    def __init__(self, context, request):
        self.context = context
        self.request = request
        self.parents = reversed(list(lineage(context)))

    @view_config(renderer='templates/root.jinja2',
                 context=Root)
    def root(self):
        page_title = 'Quick Tutorial: Root'
        return dict(page_title=page_title)

    @view_config(renderer='templates/folder.jinja2',
                 context=Folder)
    def folder(self):
        page_title = 'Quick Tutorial: Folder'
        return dict(page_title=page_title)

    @view_config(name='add_folder', context=Folder)
    def add_folder(self):
        # Make a new Folder
        title = self.request.POST['folder_title']
        name = str(randint(0, 999999))
        new_folder = Folder(title)
        new_folder.__name__ = name
        new_folder.__parent__ = self.context
        self.context[name] = new_folder

        # Redirect to the new folder
        url = self.request.resource_url(new_folder)
        return HTTPFound(location=url)

    @view_config(name='add_document', context=Folder)
    def add_document(self):
        # Make a new Document
        title = self.request.POST['document_title']
        name = str(randint(0, 999999))
        new_document = Document(title)
        new_document.__name__ = name
        new_document.__parent__ = self.context
        self.context[name] = new_document

        # Redirect to the new document
        url = self.request.resource_url(new_document)
        return HTTPFound(location=url)

    @view_config(renderer='templates/document.jinja2',
                 context=Document)
    def document(self):
        page_title = 'Quick Tutorial: Document'
        return dict(page_title=page_title)
