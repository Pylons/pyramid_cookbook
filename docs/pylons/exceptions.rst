Exceptions, HTTP Errors, and Redirects
++++++++++++++++++++++++++++++++++++++


Issuing redirects and HTTP errors
=================================

Here's how to send redirects and HTTP errors in Pyramid compared to Pylons::

    # Pylons -- in controller action
    from pylons.controllers.util import abort, redirect
    abort(404)   # Not Found
    abort(403)   # Forbidden
    abort(400)   # Bad request; e.g., invalid query parameter
    abort(500)   # Internal server error
    redirect(url("section1"))   # Redirect (default 302 Found)

    # Pyramid -- in view code
    import pyramid.httpexceptions as exc
    raise exc.exception_response(400)   # Not Found
    raise exc.HTTPNotFound()            # Same thing
    return exc.HTTPNotFound()           # Same thing
    raise exc.HTTPForbidden()
    raise exc.HTTPBadRequest()
    raise exc.HTTPInternalServerError()
    raise exc.HTTPFound(request.route_url("section1"))   # Redirect

The ``pyramid.httpexceptions`` module has classes for all official HTTP
statuses. These classes inherit from both ``Response`` and ``Exception``, so
you can either return them or raise them.  Raising HTTP exceptions can make
your code structurally more readable. It's particularly useful in
subroutines where it can cut through several calling stack frames that would
otherwise each need an ``if`` to pass the error condition through.

Exception rules:

1. Pyramid internally raises ``HTTPNotFound`` if no route matches the request,
   or if no view matches the route and request. It raises ``HTTPForbidden`` if the
   request is denied based on the current authorization policy.

2. If an uncaught exception occurs during request processing, Pyramid will catch it 
   and look for an "exception view" that matches it.  An exception view is one
   whose *context* argument is the exception's class, an ancestor of it, or an
   interface it implements.  All other view predicates must also match;
   e.g., if a 'route_name' argument is specified, it must match the actual route
   name. (Thus an exception view is typically registered *without* a route
   name.) The view is called with the exception object as its *context*, and
   whatever response the view returns will be sent to the browser. You can thus
   use an exception view to customize the error screen shown to the user.

3. If no matching exception view is found, HTTP exceptions are their own
   response so they are sent to the browser. Standard HTTPExceptions have a
   simple error message and layout; subclasses can customize this.

4. Non-HTTPException responses propagate to the WSGI server. If the debug
   toolbar tween is enabled, it will catch the exception and display the
   interactive traceback. Otherwise the WSGI server will catch it and send its
   own "500 Internal Server Error" screen.

Here are the most popular HTTP exceptions:

=======================  ====  ========  ====================================== 
Class                    Code  Location  Meaning
=======================  ====  ========  ====================================== 
HTTPMovedPermanently      301  Y         Permanent redirect; client should 
                                         change bookmarks.
HTTPFound                 302  Y         Temporary redirect. [1]_
HTTPSeeOther              303  Y         Temporary redirect; client should use
                                         GET. [1]_
HTTPTemporaryRedirect     307  Y         Temporary redirect. [1]_
HTTPClientError           400  N         General user error; e.g., invalid 
                                         query param.
HTTPUnauthorized          401  N         User must authenticate.
HTTPForbidden             403  N         Authorization failure, or general 
                                         refusal.
HTTPNotFound              404  N         The URL is not recognized.
HTTPGone                  410  N         The resource formerly at this URL is 
                                         permanently gone; client should delete
                                         bookmarks.
HTTPInternalServerError   500  N         The server could not process the 
                                         request due to an internal error.
=======================  ====  ========  ====================================== 

The constructor args for classes with a "Y" in the location column are
``(location="", detail=None, headers=None, comment=None, ...)``. Otherwise the
constructor args are ``(detail=None, headers=None, comment=None, ...)``.

The ``location`` argument is optional at the Python level, but the HTTP spec 
requires a location that's an absolute URL, so it's effectively required.

The ``detail`` argument may be a plain-text string which will be incorporated
into the error screen. ``headers`` may be a list of HTTP headers (name-value
tuples) to add to the response. ``comment`` may be a plain-text string which is
not shown to the user. (XXX Is it logged?)


Exception views
===============

You can register an exception view for any exception class, although it's most
commonly used with ``HTTPNotFound`` or ``HTTPForbidden``.  Here's an example of
an exception view with a custom exception, borrowed from the Pyramid manual::

    from pyramid.response import Response

    class ValidationFailure(Exception):
        pass

    @view_config(context=ValidationFailure)
    def failed_validation(exc, request):
        # If the view has two formal arguments, the first is the context.
        # The context is always available as ``request.context`` too.
        msg = exc.args[0] if exc.args else ""
        response =  Response('Failed validation: %s' % msg)
        response.status_int = 500
        return response

For convenience, Pyramid has special decorators and configurator methods to
register a "Not Found" view or a "Forbidden" view. ``@notfound_view_config``
and ``@forbidden_view_config`` (defined in ``pyramid.view``) takes care of the
context argument for you.

Additionally, ``@notfound_view_config`` accepts an ``append_slash`` argument,
which can be used to enforce a trailing-slash convention. If your site defines
all its routes to end in a slash and you set ``append_slash=True``, then when
a slashless request doesn't match any route, Pyramid try again with a slash
appended to the request URL. If *that* matches a route, Pyramid will issue a
redirect to it. This is useful only for sites that prefer a trailing slash
("/dir/" and "/dir/a/"). Other sites prefer *not* to have a trailing slash
("/dir" and "/dir/a"), and there are no special features for this.


Reference
=========

* `HTTP exceptions <http://docs.pylonsproject.org/projects/pyramid/en/latest/api/httpexceptions.html>`_
* `HTTP exception usage and exception views <http://docs.pylonsproject.org/projects/pyramid/en/latest/narr/views.html#using-special-exceptions-in-view-callables>`_


.. [1] The three temporary redirect statuses are largely interchangeable
   but have slightly different purposes. Details in the HTTP status
   reference.
