from random import randint

from pyramid.httpexceptions import HTTPFound
from pyramid.view import view_config

from layouts import Layouts
from resources import Company
from resources import Document
from resources import Folder
from resources import People
from resources import Person
from resources import Project
from resources import Site

class ProjectorViews(Layouts):
    def __init__(self, context, request):
        self.context = context
        self.request = request

    def _add_container(self, klass):
        title = self.request.params['title']
        name = str(randint(0, 10000))
        self.context[name] = klass(name, self.context, title)
        url = self.request.resource_url(self.context,
                                        query={'msg': 'Added'})
        return HTTPFound(location=url)

    def _add_document(self, klass=Document):
        title = self.request.params['title']
        name = str(randint(0, 10000))
        self.context[name] = klass(name, self.context, title,
                                   '<p>Default</p>')
        url = self.request.resource_url(self.context,
                                        query={'msg': 'Added'})
        return HTTPFound(location=url)

    @view_config(renderer="templates/site.pt", context=Site)
    def site_view(self):
        if 'submit' in self.request.POST:
            return self._add_container(Company)
        return {"page_title": "Home"}

    @view_config(renderer="templates/company.pt", context=Company)
    def company_view(self):
        if 'submit' in self.request.POST:
            return self._add_container(Project)
        return {"page_title": self.context.title}

    @view_config(renderer="templates/project.pt", context=Project)
    def project_view(self):
        if 'folder' in self.request.POST:
            return self._add_container(Folder)
        if 'document' in self.request.POST:
            return self._add_document()
        return {"page_title": self.context.title}

    @view_config(renderer="templates/folder.pt", context=Folder)
    def folder_view(self):
        if 'folder' in self.request.POST:
            return self._add_container(Folder)
        if 'document' in self.request.POST:
            return self._add_document()
        return {"page_title": self.context.title}

    @view_config(renderer="templates/document.pt", context=Document)
    def document_view(self):
        return {"page_title": self.context.title}


    @view_config(renderer="templates/people.pt", context=People)
    def people_view(self):
        if 'submit' in self.request.POST:
            return self._add_document(Person)
        return {"page_title": self.context.title}

    @view_config(renderer="templates/person.pt", context=Person)
    def person_view(self):
        return {"page_title": self.context.title}


    @view_config(renderer="json", name="updates.json")
    def updates_view(self):
        return [
            randint(0, 100),
            randint(0, 100),
            randint(0, 100),
            randint(0, 100),
            888,
            ]


