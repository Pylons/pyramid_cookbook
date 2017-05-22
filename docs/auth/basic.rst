HTTP Basic Authentication Policy
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

To adopt basic HTTP authentication, you can use build-in authentication policy
``BasicAuthAuthenticationPolicy``

Use it something like::

   from pyramid.authentication import BasicAuthAuthenticationPolicy

   def mycheck(credentials, request):
       pwd_ok = my_password_check(credentials['login'], credentials['password'])
       if not pwd_ok:
           return None
       return ['groups', 'that', 'login', 'is', 'member', 'of']

   config = Configurator(
                 authentication_policy=BasicAuthenticationPolicy(mycheck))
