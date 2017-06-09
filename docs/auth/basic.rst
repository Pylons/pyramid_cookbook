HTTP Basic Authentication Policy
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

To adopt basic HTTP authentication, you can use Pyramid's built-in authentication policy, :class:`pyramid.authentication.BasicAuthAuthenticationPolicy`.

Use it like this::

   from pyramid.authentication import BasicAuthAuthenticationPolicy

   def mycheck(username, password, request):
       pwd_ok = my_password_check(username, password)
       if not pwd_ok:
           return None
       return ['groups', 'that', 'login', 'is', 'member', 'of']

   config = Configurator(
                 authentication_policy=BasicAuthAuthenticationPolicy(mycheck))
