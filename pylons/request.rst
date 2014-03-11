Request and Response
++++++++++++++++++++

Pylons magic globals
====================

Pylons has several magic globals that contain state data for the current
request. Here are the closest Pyramid equivalents:

pylons.request

    The request URL, query parameters, etc.  In Pyramid it's the ``request``
    argument to view functions and ``self.request`` in view methods (if your
    class constructor follows the normal pattern). In templates it's
    ``request`` or ``req`` (starting in Pyramid 1.3). In pshell or unit tests
    where you can't get it any other way, use ``request =
    pyramid.threadlocal.get_current_request()``.

pylons.response

    The HTTP response status and document. Pyramid does not have a global
    response object. Instead, your view should create a
    ``pyramid.response.Response`` instance and return it. If you're using a
    renderer, it will create a response object for you. 
    
    For convenience, there's a ``request.response`` object available which you
    can set attributes on and return, but it will have effect only if you
    return it.  If you're using a renderer, it will honor changes you make to
    ``request.response``.

pylons.session

    Session variables. See the Sessions chapter.

pylons.tmpl_context

    A scratch object for request-local data, usually used to pass varables
    to the template. In Pyramid, you return a dict of variables and let the
    renderer apply them to a template. Or you can render a template yourself in
    view code.

    If the view is a method, you can also set instance variables. The view
    instance is visible as ``view`` in templates. There are two main use cses
    for this. One, to set variables for the site template that would otherwise
    have to be in *every* return dict. Two, for variables that are specific to
    HTML rendering, when the view is registered with both an HTML renderer and
    a non-HTML renderer (e.g., JSON).

    Pyramid does have a port of "tmpl_context" at
    ``request.tmpl_context``, which is visible in templates as ``c``. However,
    it never caught on among Pyramid-Pylons users and is no longer documented.

pylons.app_globals

    Global variables shared across all requests. The nearest equivalent is
    ``request.registry.settings``.  This normally contains the application
    settings, but you can also store other things in it too.  (The registery is
    a singleton used internally by Pyramid.)

pylons.cache

    A cache object, used to automatically save the results of expensive
    calculations for a period of time, across multiple requests. Pyramid has no
    built-in equivalent, but you can set up a cache using "pyramid_beaker".
    You'll probably want to put the cache in the settings?

pylons.url

    A URL generator. Pyramid's request object has methods that generate URLs.
    See also the URL Generator chapter for a convenience object that reduces
    boilerplate code.


Request and response API
========================

Pylons uses WebOb's request and response objects. Pyramid uses subclasses of
these so all the familiar attributes and methods are there: ``params``,
``GET``, ``POST``, ``headers``, ``method``, ``charset``, ``date``, ``environ``,
``body``, and ``body_file``. The most commonly-used attribute is ``params``,
which is the query parameters and POST variables.

Pyramid adds several attributes and methods. ``context``, ``matchdict``,
``matched_route``, ``registry``, ``registry.settings``, ``session``, and
``tmpl_context`` access the request's state data and global application data. 
``route_path``, ``route_url``, ``resource_url``, and ``static_url`` generate
URLs.

Rather than repeating the existing documentation for these attributes and
methods, we'll just refer you to the original docs:

* `Pyramd Request and Response Objects <http://docs.pylonsproject.org/projects/pyramid/en/latest/narr/webob.html>`_
* `Pyramid Request API <http://docs.pylonsproject.org/projects/pyramid/en/latest/api/request.html#request-module>`_
* `Pyramid Response API <http://docs.pylonsproject.org/projects/pyramid/en/latest/api/response.html>`_
* `WebOb Request API <http://docs.webob.org/en/latest/reference.html#id1>`_
* `WebOb Response API <http://docs.webob.org/en/latest/reference.html#id2>`_

Response examples::

    response = request.response

    # -OR-
    from pyramid.response import Response
    response = Response

    # In either case.
    response.status = "200 OK"
    response.status_int = 200
    response.content_type = "text/plain"
    response.charset = "utf-8"
    response_headerlist = [
        ("Set-Cookie", "abc=123"), ("X-My-Header", "foo")]
    response_cache_for = 3600    # Seconds
    return response
