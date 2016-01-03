Custom Authentication Policy
%%%%%%%%%%%%%%%%%%%%%%%%%%%%

Here is an example of a custom AuthenticationPolicy, based off of
the native ``AuthTktAuthenticationPolicy``, but with added groups support.
This example implies you have a ``user`` attribute on your request
(see :ref:`user object`) and that the ``user`` should have a
``groups`` relation on it::

   from pyramid.authentication import AuthTktCookieHelper
   from pyramid.security import Everyone, Authenticated

   class MyAuthenticationPolicy(object):

       def __init__(self, settings):
           self.cookie = AuthTktCookieHelper(
               settings.get('auth.secret'),
               cookie_name=settings.get('auth.token') or 'auth_tkt',
               secure=asbool(settings.get('auth.secure')),
               timeout=asint(settings.get('auth.timeout')),
               reissue_time=asint(settings.get('auth.reissue_time')),
               max_age=asint(settings.get('auth.max_age')),
           )

       def remember(self, request, principal, **kw):
           return self.cookie.remember(request, principal, **kw)

       def forget(self, request):
           return self.cookie.forget(request)

       def unauthenticated_userid(self, request):
           result = self.cookie.identify(request)
           if result:
               return result['userid']

       def authenticated_userid(self, request):
           if request.user:
               return request.user.id

       def effective_principals(self, request):
           principals = [Everyone]
           user = request.user
           if user:
               principals += [Authenticated, 'u:%s' % user.id]
               principals.extend(('g:%s' % g.name for g in user.groups))
           return principals


Thanks to `raydeo` for this one.
