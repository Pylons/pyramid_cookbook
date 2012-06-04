Authentication and Authorization
++++++++++++++++++++++++++++++++

*This chapter is contributed by Eric Rasmussen.*

Pyramid has built-in authentication and authorization capibalities that make it
easy to restrict handler actions. Here is an overview of the steps you'll
generally need to take:

1) Create a root factory in your model that associates allow/deny directives
   with groups and permissions
2) Create users and groups in your model
3) Create a callback function to retrieve a list of groups a user is subscribed to based on their user ID
4) Make a "forbidden view" that will be invoked when a Forbidden exception is
   raised.
5) Create a login action that will check the username/password and remember the
   user if successful
6) Restrict access to handler actions by passing in a
   permission='somepermission' argument to ``@view_config``.
7) Wire it all together in your config

You can get started by adding an import statement and custom root factory to
your model::

    from pyramid.security import Allow, Everyone

    class RootFactory(object):
        __acl__ = [ (Allow, Everyone, "everybody"),
                    (Allow, "basic", "entry"),
                    (Allow, "secured", ("entry", "topsecret"))
                  ]
        def __init__(self, request):
            pass

The custom root factory generates objects that will be used as the context of
requests sent to your web application. The first attribute of the root factory
is the ACL, or access control list. It's a list of tuples that contain a
directive to handle the request (such as Allow or Deny), the group that is
granted or denied access to the resource, and a permission (or optionally a
tuple of permissions) to be associated with that group. 

The example access control list above indicates that we will allow everyone to
view pages with the 'everybody' permission, members of the basic group to view
pages restricted with the 'entry' permission, and members of the secured group
to view pages restricted with either the 'entry' or 'topsecret' permissions.
The special principal 'Everyone' is a built-in feature that allows any person
visiting your site (known as a principal) access to a given resource.

For a user to login, you can create a handler that validates the login and
password (or any additional criteria) submitted through a form. You'll
typically want to add the following imports::

    from pyramid.httpexceptions import HTTPFound
    from pyramid.security import remember, forget
 
Once you validate a user's login and password against the model, you can set
the headers to "remember" the user's ID, and then you can redirect the user to
the home page or url they were trying to access::

    # retrieve the userid from the model on valid login
    headers = remember(self.request, userid)
    return HTTPFound(location=someurl, headers=headers)

Note that in the call to the remember function, we're passing in the user ID we
retrieved from the database and stored in the variable 'userid' (an arbitrary
name used here as an example). However, you could just as easily pass in a
username or other unique identifier. Whatever you decide to "remember" is what
will be passed to the groupfinder callback function that returns a list of
groups a user belongs to. If you import ``authenticated_userid``, which is a
useful way to retrieve user information in a handler action, it will return the
information you set the headers to "remember".

To log a user out, you "forget" them, and use HTTPFound to redirect to another
url::

    headers = forget(self.request)
    return HTTPFound(location=someurl, headers=headers)

Before you restrict a handler action with a permission, you will need a
callback function to return a list of groups that a user ID belongs to. Here is
one way to implement it in your model, in this case assuming you have a Groups
object with a groupname attribute and a Users object with a mygroups relation
to Groups::

    def groupfinder(userid, request):
        user = Users.by_id(userid)
        return [g.groupname for g in user.mygroups]

As an example, you could now import and use the @action decorator to restrict
by permission, and authenticated_userid to retrieve the user's ID from the
request::

    from pyramid_handlers import action
    from pyramid.security import authenticated_userid
    from models import Users

    class MainHandler(object):
        def __init__(self, request):
            self.request = request
    
        @action(renderer="welcome.html", permission="entry")
        def index(self):
            userid = authenticated_userid(self.request)
            user = Users.by_id(userid)
            username = user.username
            return {"currentuser": username}

This gives us a very simple way to restrict handler actions and also obtain
information about the user. This example assumes we have a Users class with a
convenience class method called by_id to return the user object. You can then
access any of the object's attributes defined in your model (such as username,
email address, etc.), and pass those to a template as dictionary key/values in
your return statement.

If you would like a specific handler action to be called when a forbidden
exception is raised, you need to add a forbidden view.  This was covered
earlier, but for completelness::

    @view_config(renderer='myapp:templates/forbidden.html',
                 context='pyramid.exceptions.Forbidden')
    @action(renderer='forbidden.html')
    def forbidden(request):
        ...

The last step is to configure __init__.py to use your auth policy. Make sure to
add these imports::

    from pyramid.authentication import AuthTktAuthenticationPolicy
    from pyramid.authorization import ACLAuthorizationPolicy
    from .models import groupfinder

In your main function you'll want to define your auth policies so you can
include them in the call to Configurator::

        authn_policy = AuthTktAuthenticationPolicy('secretstring', 
           callback=groupfinder)
        authz_policy = ACLAuthorizationPolicy()
        config = Configurator(settings=settings, 
           root_factory='myapp.models.RootFactory',
           authentication_policy=authn_policy,
           authorization_policy=authz_policy)
        config.scan()

The capabilities for authentication and authorization in Pyramid are very easy
to get started with compared to using Pylons and repoze.what. The advantage is
easier to maintain code and built-in methods to handle common tasks like
remembering or forgetting users, setting permissions, and easily modifying the
groupfinder callback to work with your model. For cases where it's manageable
to set permissions in advance in your root factory and restrict individual
handler actions, this is by far the simplest way to get up and running while
still offering robust user and group management capabilities through your
model. 

However, if your application requires the ability to create/edit/delete
permissions (not just access through group membership), or you require the use
of advanced predicates, you can either build your own auth system (see the
Pyramid docs for details) or integrate an existing system like repoze.what.

You can also use "repoze.who" with Pyramid's authorization system if you want to
use Who's authenticators and configuration.
