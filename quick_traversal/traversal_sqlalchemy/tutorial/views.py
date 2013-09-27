from random import randint

from pyramid.decorator import reify
from pyramid.httpexceptions import HTTPFound
from pyramid.location import lineage
from pyramid.view import view_config

from .models import (
    DBSession,
    Root,
    Folder,
    Document
    )


class TutorialViews(object):
    def __init__(self, context, request):
        self.context = context
        self.request = request

    @view_config(renderer="templates/site.pt",
                 context=Root)
    def site(self):
        cv = list(self.context.values())
        return {"children": cv}

    @reify
    def parents(self):
        return reversed(list(lineage(self.context)))

    @view_config(renderer="templates/folder.pt",
                 context=Folder)
    def folder(self):
        cv = list(self.context.values())
        return {"children": cv}

    @view_config(name="add_folder", context=Root)
    @view_config(name="add_folder", context=Folder)
    def add_folder(self):
        # Make a new Folder
        title = self.request.POST['folder_title']
        name = str(randint(0, 999999))

        new_folder = Folder(title=title)
        DBSession.add(new_folder)
        self.context[name] = new_folder

        # Redirect to the new folder
        url = self.request.resource_url(new_folder)
        return HTTPFound(location=url)

    @view_config(name="add_document", context=Root)
    @view_config(name="add_document", context=Folder)
    def add_document(self):
        # Make a new Document
        title = self.request.POST['document_title']
        name = str(randint(0, 999999))
        new_document = Document(title=title)
        DBSession.add(new_document)
        self.context[name] = new_document

        # Redirect to the new document
        DBSession.flush()
        url = self.request.resource_url(new_document)
        return HTTPFound(location=url)

    @view_config(renderer="templates/document.pt",
                 context=Document)
    def document(self):
        return {}