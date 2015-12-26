from random import randint

from pyramid.httpexceptions import HTTPFound
from pyramid.location import lineage
from pyramid.view import view_config

from .models import (
    Folder,
    Document
    )


class TutorialViews(object):
    def __init__(self, context, request):
        self.context = context
        self.request = request
        self.parents = reversed(list(lineage(context)))

    @view_config(renderer='templates/root.jinja2',
                 context=Folder, custom_predicates=[lambda c, r: c is r.root])
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
        new_folder = self.context[name] = Folder(title=title)

        # Redirect to the new folder
        url = self.request.resource_url(new_folder)
        return HTTPFound(location=url)

    @view_config(name='add_document', context=Folder)
    def add_document(self):
        # Make a new Document
        title = self.request.POST['document_title']
        name = str(randint(0, 999999))
        new_document = self.context[name] = Document(title=title)

        # Redirect to the new document
        url = self.request.resource_url(new_document)
        return HTTPFound(location=url)

    @view_config(renderer='templates/document.jinja2',
                 context=Document)
    def document(self):
        page_title = 'Quick Tutorial: Document'
        return dict(page_title=page_title)
