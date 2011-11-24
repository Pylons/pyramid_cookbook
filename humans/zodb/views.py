from random import randint

from pyramid.httpexceptions import HTTPFound
from pyramid.view import view_config

import colander
from deform import Form
from deform.widget import TextAreaWidget

from resources import Folder
from resources import Document


class FolderSchema(colander.Schema):
    title = colander.SchemaNode(colander.String())


class DocumentSchema(colander.Schema):
    title = colander.SchemaNode(colander.String())
    content = colander.SchemaNode(colander.String(), widget=TextAreaWidget())


class ProjectorViews(object):
    def __init__(self, context, request):
        self.context = context
        self.request = request

    @view_config(renderer="templates/folder_view.pt", context=Folder)
    def folder_view(self):
        return {}

    @view_config(name="add_folder", context=Folder, renderer="templates/form.pt")
    def add_folder(self):
        schema = FolderSchema()
        form = Form(schema, buttons=('submit',))
        if 'submit' in self.request.POST:
            # Make a new Folder
            title = self.request.POST['title']
            name = str(randint(0,999999))
            new_folder = Folder(title)
            new_folder.__name__ = name
            new_folder.__parent__ = self.context
            self.context[name] = new_folder
            # Redirect to the new folder
            url = self.request.resource_url(new_folder)
            return HTTPFound(location=url)
        return {"form": form.render()}

    @view_config(name="add_document", context=Folder, renderer="templates/form.pt")
    def add_document(self):
        schema = DocumentSchema()
        form = Form(schema, buttons=('submit',))
        if 'submit' in self.request.POST:
            # Make a new Document
            title = self.request.POST['title']
            content = self.request.POST['content']
            name = str(randint(0,999999))
            new_document = Document(title, content)
            new_document.__name__ = name
            new_document.__parent__ = self.context
            self.context[name] = new_document
            # Redirect to the new document
            url = self.request.resource_url(new_document)
            return HTTPFound(location=url)
        return {"form": form.render()}

    @view_config(renderer="templates/document_view.pt",
                 context=Document)
    def document_view(self):
        return {}
