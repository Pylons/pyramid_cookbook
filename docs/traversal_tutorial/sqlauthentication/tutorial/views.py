from random import randint

from pyramid.httpexceptions import HTTPFound
from pyramid.location import lineage
from pyramid.security import (
    remember,
    forget,
    authenticated_userid
    )
from pyramid.view import view_config

from .models import (
    Root,
    Folder,
    Document
    )
from .security import USERS


class TutorialViews(object):
    def __init__(self, context, request):
        self.context = context
        self.request = request
        self.parents = reversed(list(lineage(context)))
        self.logged_in = authenticated_userid(request)

    @view_config(renderer="templates/root.jinja2",
                 context=Root)
    def root(self):
        page_title = 'Quick Tutorial: Root'
        return dict(page_title=page_title)

    @view_config(renderer="templates/folder.jinja2",
                 context=Folder)
    def folder(self):
        page_title = 'Quick Tutorial: Folder'
        return dict(page_title=page_title)

    @view_config(name="add_folder", context=Root)
    @view_config(name="add_folder", context=Folder)
    def add_folder(self):
        # Make a new Folder
        title = self.request.POST['folder_title']
        name = str(randint(0, 999999))
        new_folder = Folder(title=title)
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
        self.context[name] = new_document

        # Redirect to the new document
        url = self.request.resource_url(new_document)
        return HTTPFound(location=url)

    @view_config(renderer="templates/document.jinja2",
                 context=Document)
    def document(self):
        page_title = 'Quick Tutorial: Document'
        return dict(page_title=page_title)

    @view_config(name='login', renderer='templates/login.jinja2')
    def login(self):
        request = self.request
        referrer = request.url
        message = ''
        login = ''
        password = ''
        if 'form.submitted' in request.params:
            login = request.params['login']
            password = request.params['password']
            if USERS.get(login) == password:
                headers = remember(request, login)
                return HTTPFound(location='/',
                                 headers=headers)
            message = 'Failed login'

        return dict(
            page_title='Login',
            message=message,
            url=request.application_url + '/login',
            login=login,
            password=password,
        )

    @view_config(name='logout')
    def logout(self):
        request = self.request
        headers = forget(request)
        url = request.resource_url(request.root)
        return HTTPFound(location=url,
                         headers=headers)