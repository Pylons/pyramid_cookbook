from pyramid.httpexceptions import HTTPFound
from pyramid.view import view_config
from pyramid.traversal import resource_path
from pyramid.traversal import find_resource
from pyramid.renderers import render_to_response

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

class SearchSchema(colander.Schema):
    term = colander.SchemaNode(colander.String())

class ProjectorViews(object):
    def __init__(self, context, request):
        self.context = context
        self.request = request
        self.root = self.request.root
        self.catalog = self.root.catalog
        self.document_map = self.root.document_map

    @view_config(renderer="templates/folder_view.pt")
    def folder_view(self):
        schema = SearchSchema()
        form = Form(schema, buttons=('submit',))
        if 'submit' in self.request.POST:
            term = self.request.POST['term']
            query = "'%s' in title or '%s' in content" % (term, term)
            num, results = self.catalog.query(query)
            results = [self.document_map.address_for_docid(result)
                       for result in results]
            results = [find_resource(self.root, result)
                      for result in results]
            values = {'num': num,
                      'results':results,
                      'request':self.request,
                      'context':self.context,
                      'term':term}
            return render_to_response('templates/search.pt', values)
        return {"search_form": form.render()}

    @view_config(name="add_folder", context=Folder, renderer="templates/form.pt")
    def add_folder(self):
        schema = FolderSchema()
        form = Form(schema, buttons=('submit',))
        if 'submit' in self.request.POST:
            # Make a new Folder
            title = self.request.POST['title']
            doc_id = self.document_map.new_docid()
            name = "folder%s" % doc_id
            new_folder = Folder(title)
            new_folder.__name__ = name
            new_folder.__parent__ = self.context
            self.context[name] = new_folder
            # map object path to catalog id
            path = resource_path(new_folder)
            self.document_map.add(path, doc_id) 
            # index new folder
            self.catalog.index_doc(doc_id, new_folder)
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
            doc_id = self.document_map.new_docid()
            name = "document%s" % doc_id
            new_document = Document(title, content)
            new_document.__name__ = name
            new_document.__parent__ = self.context
            self.context[name] = new_document
            # map object path to catalog id
            path = resource_path(new_document)
            self.document_map.add(path, doc_id) 
            # index new folder
            self.catalog.index_doc(doc_id, new_document)
            # Redirect to the new document
            url = self.request.resource_url(new_document)
            return HTTPFound(location=url)
        return {"form": form.render()}

    @view_config(renderer="templates/document_view.pt",
                 context=Document)
    def document_view(self):
        return {}
