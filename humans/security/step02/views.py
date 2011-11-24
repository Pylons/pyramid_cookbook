from pyramid.view import view_config

from pyramid.httpexceptions import HTTPFound
from pyramid.httpexceptions import HTTPForbidden
from pyramid.security import remember
from pyramid.security import forget

# Get our database that manages users
from usersdb import USERS
from pyramid.security import has_permission

class ProjectorViews(object):
    def __init__(self, context, request):
        self.context = context
        self.request = request

    @view_config(renderer="templates/default_view.pt",
                 permission='view')
    def default_view(self):
        can_i_edit = has_permission("edit", self.context,
                                    self.request)
        return dict(page_title="Site View",
                    can_i_edit=can_i_edit)

    @view_config(renderer="templates/default_view.pt",
                 permission='edit',
                 name="edit")
    def edit_view(self):
        return dict(page_title="Edit Site")

    @view_config(renderer="templates/login.pt", context=HTTPForbidden)
    @view_config(renderer="templates/login.pt", name="login.html")
    def login(self):
        request = self.request
        login_url = request.resource_url(request.context, 'login.html')
        referrer = request.url
        if referrer == login_url:
            referrer = '/' # never use the login form itself as came_from
        came_from = request.params.get('came_from', referrer)
        message = ''
        login = ''
        password = ''
        if 'form.submitted' in request.params:
            login = request.params['login']
            password = request.params['password']
            if USERS.get(login) == password:
                headers = remember(request, login)
                return HTTPFound(location=came_from,
                                 headers=headers)
            message = 'Failed login'

        return dict(
            page_title="Login",
            message=message,
            url=request.application_url + '/login.html',
            came_from=came_from,
            login=login,
            password=password,
            )

    @view_config(name="logout.html")
    def logout(self):
        headers = forget(self.request)
        url = self.request.resource_url(self.context, 'login.html')
        return HTTPFound(location=url, headers=headers)


