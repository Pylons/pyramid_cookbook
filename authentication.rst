Making A "User Object" Available as a Request Attribute
-------------------------------------------------------

This is you: your application wants a "user object".  Pyramid is only willing
to supply you with a user *id* (via
``pyramid.security.authenticated_userid``). You don't want to create a
function that takes accepts a request object and returns a user object from
your domain model for efficiency reasons, so you want the user object to be
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
                return dbconn['users'].query({'id':userid)})

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
