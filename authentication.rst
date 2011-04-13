Making A "User Object" Available as a Request Attribute
-------------------------------------------------------

This is you: your application wants a "user object".  Pyramid is only willing
to supply you with a user *id* (via
``pyramid.security.authenticated_userid``). You don't want to create a
function that takes accepts a request object and returns a user object from
your domain model for efficiency reasons, and you want the user object to be
omnipresent as ``request.user``.

You've tried using a ``NewRequest`` subscriber to attach a user object to the
request, but the ``NewRequest`` susbcriber is called on every request, even
ones for static resources, and this bothers you (which it should).

Use a combination of a custom request factory and the
``pyramid.configuration.Config.set_request_factory`` method.  Here's the
custom request factory:

.. code-block:: python
   :linenos:

    from pyramid.decorator import reify
    from pyramid.request import Request
    from pyramid.security import unauthenticated_userid

    class RequestWithUserAttribute(Request):
        @reify
        def user(self):
            # <your database connection, however you get it, the below line
            # is just an example>
            dbconn = self.registry.settings['dbconn'] 
            userid = unauthenticated_userid(self)
            if userid is not None:
                # this should return None if the user doesn't exist
                # in the database
                return dbconn['users'].query({'id':userid})

``pyramid.decorator.reify`` is like the built-in Python ``property``
decorator, but makes sure that "user" turns into a "real" attribute of the
request after the first call rather than a property, which executes over and
over for each access.

Here's how you should use your new request factory in configuration code:

.. code-block:: python
   :linenos:

   config.set_request_factory(RequestWithUserAttribute)

Then in your view code, you should be able to happily do ``request.user`` to
obtain the "user object" related to that request.  It will return ``None`` if
there aren't any user credentials associated with the request, or if there
are user credentials associated with the request but the userid doesn't exist
in your database.  No inappropriate execution of ``authenticated_userid`` is
done (as would be if you used a ``NewRequest`` subscriber).

After doing such a thing, if your user object has a "groups" attribute, which
returns a list of groups that have ``name`` attributes, you can use the
following as a ``callback`` (aka ``groupfinder``) argument to most builtin
authentication policies.  For example:

.. code-block:: python
   :linenos:

   from pyramid.authentication import AuthTktAuthenticationPolicy

   def groupfinder(request, userid):
       user = request.user
       if user is not None:
           return [ group.name for group in request.user.groups ]
       return None

   authn_policy = AuthTktAuthenticationPolicy('seekrITT', callback=groupfinder)

Basic Authentication Policy
---------------------------

Here's an implementation of an HTTP basic auth Pyramid authentication policy:

.. code-block:: python
   :linenos:

   import binascii

   from zope.interface import implements

   from paste.httpheaders import AUTHORIZATION
   from paste.httpheaders import WWW_AUTHENTICATE

   from pyramid.interfaces import IAuthenticationPolicy
   from pyramid.security import Everyone
   from pyramid.security import Authenticated

   def _get_basicauth_credentials(request):
       authorization = AUTHORIZATION(request.environ)
       try:
           authmeth, auth = authorization.split(' ', 1)
       except ValueError: # not enough values to unpack
           return None
       if authmeth.lower() == 'basic':
           try:
               auth = auth.strip().decode('base64')
           except binascii.Error: # can't decode
               return None
           try:
               login, password = auth.split(':', 1)
           except ValueError: # not enough values to unpack
               return None
           return {'login':login, 'password':password}

       return None

   class BasicAuthenticationPolicy(object):
       """ A :app:`Pyramid` :term:`authentication policy` which
       obtains data from basic authentication headers.

       Constructor Arguments

       ``check``

           A callback passed the credentials and the request,
           expected to return None if the userid doesn't exist or a sequence
           of group identifiers (possibly empty) if the user does exist.
           Required.

       ``realm``

           Default: ``Realm``.  The Basic Auth realm string.

       """
       implements(IAuthenticationPolicy)

       def __init__(self, check, realm='Realm'):
           self.check = check
           self.realm = realm

       def authenticated_userid(self, request):
           credentials = _get_basicauth_credentials(request)
           if credentials is None:
               return None
           userid = credentials['login']
           if self.check(credentials, request) is not None: # is not None!
               return userid

       def effective_principals(self, request):
           effective_principals = [Everyone]
           credentials = _get_basicauth_credentials(request)
           if credentials is None:
               return effective_principals
           userid = credentials['login']
           groups = self.check(credentials, request)
           if groups is None: # is None!
               return effective_principals
           effective_principals.append(Authenticated)
           effective_principals.append(userid)
           effective_principals.extend(groups)
           return effective_principals

       def unauthenticated_userid(self, request):
           creds = self._get_credentials(request)
           if creds is not None:
               return creds['login']
           return None

       def remember(self, request, principal, **kw):
           return []

       def forget(self, request):
           head = WWW_AUTHENTICATE.tuples('Basic realm="%s"' % self.realm)
           return head

Use it something like:

.. code-block:: python
   :linenos:

   def mycheck(credentials, request):
       pwd_ok = my_password_check(credentials['login'], credentials['password'])
       if not pwd_ok:
           return None
       return ['groups', 'that', 'login', 'is', 'member', 'of']

   config = Configurator(
                 authentication_policy=BasicAuthenticationPolicy(mycheck))


Here is another example of a custom AuthenticationPolicy, based off of
the native ``AuthTktAuthenticationPolicy``, but with added groups support.
This example implies you have a ``user`` attribute on your request, like
the ``RequestWithUserAttribute`` version of the request above, and it has
a groups relation on it:

.. code-block:: python
   :linenos:

   class MyAuthenticationPolicy(object):
       implements(IAuthenticationPolicy)

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
