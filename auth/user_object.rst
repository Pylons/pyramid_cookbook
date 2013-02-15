.. _user object:

Making A "User Object" Available as a Request Attribute
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

This is you: your application wants a "user object".
Pyramid is only willing to supply you with a user *id*
(via :meth:`pyramid.security.authenticated_userid`).
You don't want to create a
function that accepts a request object and returns a user object from
your domain model for efficiency reasons, and you want the user object to be
omnipresent as ``request.user``.

You've tried using a ``NewRequest`` subscriber to attach a user object to the
request, but the ``NewRequest`` susbcriber is called on every request, even
ones for static resources, and this bothers you (which it should).

A lazy property can be registered to the request via the
:meth:`pyramid.config.Configurator.add_request_method` API
(introduced in Pyramid 1.4; see below for older releases).
This allows you to specify a
callable that will be available on the request object, but will not actually
execute the function until accessed. The result of this function can also
be cached per-request, to eliminate the overhead of running the function
multiple times (this is done by setting ``reify=True``::

   from pyramid.security import unauthenticated_userid

   def get_user(request):
       # the below line is just an example, use your own method of
       # accessing a database connection here (this could even be another
       # request property such as request.db, implemented using this same
       # pattern).
       dbconn = request.registry.settings['dbconn']
       userid = unauthenticated_userid(request)
       if userid is not None:
           # this should return None if the user doesn't exist
           # in the database
           return dbconn['users'].query({'id':userid})

Here's how you should add your new request property in configuration code::

   config.add_request_method(get_user, 'user', reify=True)

Then in your view code, you should be able to happily do ``request.user`` to
obtain the "user object" related to that request.  It will return ``None`` if
there aren't any user credentials associated with the request, or if there
are user credentials associated with the request but the userid doesn't exist
in your database.  No inappropriate execution of ``authenticated_userid`` is
done (as would be if you used a ``NewRequest`` subscriber).

After doing such a thing, if your user object has a ``groups`` attribute,
which returns a list of groups that have ``name`` attributes, you can use the
following as a ``callback`` (aka ``groupfinder``) argument to most builtin
authentication policies.  For example::

   from pyramid.authentication import AuthTktAuthenticationPolicy

   def groupfinder(userid, request):
       user = request.user
       if user is not None:
           return [ group.name for group in request.user.groups ]
       return None

   authn_policy = AuthTktAuthenticationPolicy('seekrITT', callback=groupfinder)

Prior to Pyramid 1.4
====================

If you are using version 1.3, you can follow the same procedure as above,
except use this instead of ``add_request_method``::

   config.set_request_property(get_user, 'user', reify=True)

.. deprecated:: 1.4
   :meth:`~pyramid.config.Configurator.set_request_property`

Prior to ``set_request_property`` and ``add_request_method``,
a similar pattern could be used, but it required :ref:`registering
a new request factory <changing_the_request_factory>`
via :meth:`~pyramid.config.Configurator.set_request_factory`. This works
in the same way, but each application can only have one request factory
and so it is not very extensible for arbitrary properties.

The code for this method is below::

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

Here's how you should use your new request factory in configuration code::

   config.set_request_factory(RequestWithUserAttribute)
