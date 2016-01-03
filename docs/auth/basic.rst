Basic Authentication Policy
%%%%%%%%%%%%%%%%%%%%%%%%%%%

Here's an implementation of an HTTP basic auth Pyramid authentication policy::

   import binascii

   from paste.httpheaders import AUTHORIZATION
   from paste.httpheaders import WWW_AUTHENTICATE

   from pyramid.security import Everyone
   from pyramid.security import Authenticated

   def _get_basicauth_credentials(request):
       authorization = AUTHORIZATION(request.environ)
       try:
           authmeth, auth = authorization.split(' ', 1)
       except ValueError:  # not enough values to unpack
           return None
       if authmeth.lower() == 'basic':
           try:
               auth = auth.strip().decode('base64')
           except binascii.Error:  # can't decode
               return None
           try:
               login, password = auth.split(':', 1)
           except ValueError:  # not enough values to unpack
               return None
           return {'login': login, 'password': password}

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

       def __init__(self, check, realm='Realm'):
           self.check = check
           self.realm = realm

       def authenticated_userid(self, request):
           credentials = _get_basicauth_credentials(request)
           if credentials is None:
               return None
           userid = credentials['login']
           if self.check(credentials, request) is not None:  # is not None!
               return userid

       def effective_principals(self, request):
           effective_principals = [Everyone]
           credentials = _get_basicauth_credentials(request)
           if credentials is None:
               return effective_principals
           userid = credentials['login']
           groups = self.check(credentials, request)
           if groups is None:  # is None!
               return effective_principals
           effective_principals.append(Authenticated)
           effective_principals.append(userid)
           effective_principals.extend(groups)
           return effective_principals

       def unauthenticated_userid(self, request):
           creds = _get_basicauth_credentials(request)
           if creds is not None:
               return creds['login']
           return None

       def remember(self, request, principal, **kw):
           return []

       def forget(self, request):
           head = WWW_AUTHENTICATE.tuples('Basic realm="%s"' % self.realm)
           return head

Use it something like::

   def mycheck(credentials, request):
       pwd_ok = my_password_check(credentials['login'], credentials['password'])
       if not pwd_ok:
           return None
       return ['groups', 'that', 'login', 'is', 'member', 'of']

   config = Configurator(
                 authentication_policy=BasicAuthenticationPolicy(mycheck))
