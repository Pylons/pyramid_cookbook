from random import randint

from pyramid.decorator import reify
from pyramid.httpexceptions import HTTPFound
from pyramid.view import view_config

from resources import SiteFolder
from resources import Folder
from resources import Document


class ProjectorViews(object):
    def __init__(self, context, request):
        self.context = context
        self.request = request

    @view_config(renderer="templates/site_view.pt",
                 context=SiteFolder)
    def site_view(self):
        return {"children": self.context.values()}

    @reify
    def parent_info(self):
        parent = self.context.__parent__
        parent_url = self.request.resource_url(parent)
        return {
            'title': parent.title,
            'url': parent_url}

    @view_config(renderer="templates/folder_view.pt",
                 context=Folder)
    def folder_view(self):
        return {"children": self.context.values()}

    @view_config(name="add_folder", context=Folder)
    def add_folder_view(self):
        # Make a new Folder
        title = self.request.POST['folder_title']
        name = str(randint(0, 999999))
        new_folder = Folder(name, self.context, title)
        self.context[name] = new_folder

        # Redirect to the new folder
        url = self.request.resource_url(new_folder)
        return HTTPFound(location=url)

    @view_config(name="add_document", context=Folder)
    def add_document_view(self):
        # Make a new Document
        title = self.request.POST['document_title']
        name = str(randint(0, 999999))
        new_document = Document(name, self.context, title)
        self.context[name] = new_document

        # Redirect to the new document
        url = self.request.resource_url(new_document)
        return HTTPFound(location=url)

    @view_config(renderer="templates/document_view.pt",
                 context=Document)
    def document_view(self):
        return {}
