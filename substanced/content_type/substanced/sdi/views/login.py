from pyramid.httpexceptions import (
    HTTPForbidden,
    HTTPFound
    )
from pyramid.renderers import get_renderer
from pyramid.session import check_csrf_token
from pyramid.security import (
    remember,
    forget,
    Authenticated,
    NO_PERMISSION_REQUIRED,
    )

from ...util import get_oid

from .. import mgmt_view

from substanced.interfaces import IUserLocator
from substanced.principal import DefaultUserLocator
from substanced.event import LoggedIn

@mgmt_view(
    name='login',
    renderer='templates/login.pt',
    tab_condition=False,
    permission=NO_PERMISSION_REQUIRED
    )
@mgmt_view(
    renderer='templates/login.pt',
    context=HTTPForbidden,
    permission=NO_PERMISSION_REQUIRED,
    tab_condition=False
    )
@mgmt_view(
    renderer='templates/forbidden.pt',
    context=HTTPForbidden,
    permission=NO_PERMISSION_REQUIRED,
    effective_principals=Authenticated,
    tab_condition=False
    )
def login(context, request):
    login_url = request.sdiapi.mgmt_path(request.context, 'login')
    referrer = request.url
    if '/auditstream-sse' in referrer:
        # If we're being invoked as the result of a failed request to the
        # auditstream sse view, bail.  Otherwise the came_from will be set to
        # the auditstream URL, and the user who this happens to will eventually
        # be redirected to it and they'll be left scratching their head when
        # they see e.g. "id: 0-10\ndata: " when they log in successfully.
        return HTTPForbidden()
    if login_url in referrer:
        # never use the login form itself as came_from
        referrer = request.sdiapi.mgmt_path(request.virtual_root)
    came_from = request.session.setdefault('sdi.came_from', referrer)
    login = ''
    password = ''
    if 'form.submitted' in request.params:
        try:
            check_csrf_token(request)
        except:
            request.session.flash('Failed login (CSRF)', 'error')
        else:
            login = request.params['login']
            password = request.params['password']
            adapter = request.registry.queryMultiAdapter(
                (context, request),
                IUserLocator
                )
            if adapter is None:
                adapter = DefaultUserLocator(context, request)
            user = adapter.get_user_by_login(login)
            if user is not None and user.check_password(password):
                request.session.pop('sdi.came_from', None)
                headers = remember(request, get_oid(user))
                request.registry.notify(LoggedIn(login, user, context, request))
                return HTTPFound(location = came_from, headers = headers)
            request.session.flash('Failed login', 'error')

    # Pass this through FBO views (e.g., forbidden) which use its macros.
    template = get_renderer('substanced.sdi.views:templates/login.pt'
                           ).implementation()
    return dict(
        url = request.sdiapi.mgmt_path(request.virtual_root, '@@login'),
        came_from = came_from,
        login = login,
        password = password,
        login_template = template,
        )

@mgmt_view(
    name='logout',
    tab_condition=False,
    permission=NO_PERMISSION_REQUIRED
    )
def logout(request):
    headers = forget(request)
    return HTTPFound(location = request.sdiapi.mgmt_path(request.context),
                     headers = headers)
