HTTP Basic Authentication Policy
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

To adopt basic HTTP authentication, you can use Pyramid's built-in authentication policy, :class:`pyramid.authentication.BasicAuthAuthenticationPolicy`.

This is a complete working example with very simple authentication and authorization::

   from pyramid.authentication import BasicAuthAuthenticationPolicy
   from pyramid.authorization import ACLAuthorizationPolicy
   from pyramid.config import Configurator
   from pyramid.httpexceptions import HTTPForbidden
   from pyramid.httpexceptions import HTTPUnauthorized
   from pyramid.security import ALL_PERMISSIONS
   from pyramid.security import Allow
   from pyramid.security import Authenticated
   from pyramid.security import forget
   from pyramid.view import forbidden_view_config
   from pyramid.view import view_config

   @view_config(route_name='home', renderer='json', permission='view')
   def home_view(request):
       return {
           'page': 'home',
           'userid': request.authenticated_userid,
           'principals': request.effective_principals,
           'context_type': str(type(request.context)),
       }

   @forbidden_view_config()
   def forbidden_view(request):
       if request.authenticated_userid is None:
           response = HTTPUnauthorized()
           response.headers.update(forget(request))

       # user is logged in but doesn't have permissions, reject wholesale
       else:
           response = HTTPForbidden()
       return response

   def check_credentials(username, password, request):
       if username == 'admin' and password == 'admin':
           # an empty list is enough to indicate logged-in... watch how this
           # affects the principals returned in the home view if you want to
           # expand ACLs later
           return []

   class Root:
       # dead simple, give everyone who is logged in any permission
       # (see the home_view for an example permission)
       __acl__ = (
           (Allow, Authenticated, ALL_PERMISSIONS),
       )

   def main(global_conf, **settings):
       config = Configurator(settings=settings)

       authn_policy = BasicAuthAuthenticationPolicy(check_credentials)
       config.set_authentication_policy(authn_policy)
       config.set_authorization_policy(ACLAuthorizationPolicy())
       config.set_root_factory(lambda request: Root())

       config.add_route('home', '/')

       config.scan(__name__)
       return config.make_wsgi_app()

   if __name__ == '__main__':
       from waitress import serve
       app = main({})
       serve(app, listen='localhost:8000')
