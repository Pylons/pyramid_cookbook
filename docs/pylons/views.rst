Views
+++++

The biggest difference between Pyramid and Pylons is how views are structured,
and how they invoke templates and access state variables. This is a large topic
because it touches on templates, renderers, request variables, URL generators,
and more, and several of these topics have many facets. So we'll just start
somewhere and keep going, and let it organize itself however it falls.

First let's review Pylons' view handling.  In Pylons, a view is called an
"action", and is a method in a controller class. Pylons has specific rules
about the controller's module name, class name, and base class. When Pylons
matches a URL to a route, it uses the routes 'controller' and 'action'
variables to look up the controller and action. It instantiates the controller
and calls the action. The action may take arguments with the same name as
routing variables in the route; Pylons will pass in the current values from the
route. The action normally returns a string, usually by calling
``render(template_name)`` to render a template. Alternatively, it can return a
WebOb ``Response``. The request's state data is handled by magic global
variables which contain the values for the current request. (This includes
equest parameters, response attributes, template variables, session variables,
URL generator, cache object, and an "application globals" object.)

View functions and view methods
===============================

A Pyramid *view callable* can be a function or a method, and it can be in any
location. The most basic form is a function that takes a request and returns a
response::

    from pyramid.response import Response

    def my_view(request):
        return Response("Hello, world!")

A view method may be in any class. A class containing view methods is
conventionally called a "view class" or a "handler". If a view is a method, the
request is passed to the class constructor, and the method is called without
arguments. ::

    class MyHandler(object):
        def __init__(self, request):
            self.request = request

        def my_view(self):
            return Response("Hello, classy world!")

The Pyramid structure has three major benefits.

* Most importantly, it's easier to test. A unit test can call a view with a
  fake request, and get back the dict that would have been passed
  to the template. It can inspect the data variables directly rather than
  parsing them out of the HTML.

* It's simpler and more modular. No magic globals.

* You have the freedom to organize views however you like.


Typical view usage
==================

Merely defining a view is not enough to make Pyramid use it. You have to
*register* the view, either by calling ``config.add_view()`` or using the
``@view_config`` decorator.

The most common way to use views is with the ``@view_config`` decorator. This
both marks the callable as a view and allows you to specify a template. It's
also common to define a base class for common code shared by view classes. The
following is borrowed from the Akhet demo. ::

    from pyramid.view import view_config

    class Handler(object):
        def __init__(self, request):
            self.request = request

    class Main(Handler):

        @view_config(route_name="home", renderer="index.mako")
        def index(self):
            return {"project": "Akhet Demo"}

The application's main function has a ``config.scan()`` line, which imports all
application modules looking for ``@view_config`` decorators. For each one it calls
``config.add_view(view)`` with the same keyword arguments. The scanner also
recognizes a few other decorators which we'll see later. If you know that all
your views are in a certain module or subpackage, you can scan only that one:
``config.scan(".views")``.

The example's ``@view_config`` decorator has two arguments, 'route_name' and
'renderer'. The 'route_name' argument is *required* when using URL dispatch, to tell
Pyramid which route should invoke this view. The "renderer" argument names a
template to invoke. In this case, the view's return value is a dict of data
variables for the template. (This takes the place of Pylons' 'c' variable, and
mimics TurboGears' usage pattern.) The renderer takes care of creating a
Response object for you.

        
View configuration arguments
============================

The following arguments can be passed to ``@view_config`` or
``config.add_view``.  If you have certain argument values that are the same for
all of the views in a class, you can use ``@view_defaults`` on the *class* to
specify them in one place.

This list includes only arguments commonly used in Pylons-like applications.
The full list is in `View Configuration`_ in the Pyramid manual. The arguments
have the same predicate/non-predicate distinction as ``add_route`` arguments.
It's possible to register multiple views for a route, each with different
predicate arguments, to invoke a different view in different circumstances.

Some of the arguments are common to ``add_route`` and ``add_view``. In the
route's case it determines whether the route will match a URL. In the view's
case it determines whether the view will match the route.

route_name

    [predicate] The route to attach this view to. Required when using URL
    dispatch.

renderer

    [non-predicate] The name of a renderer or template. Discussed in Renderers
    below.

permission

    [non-predicate] A string naming a permission that the current user must
    have in order to invoke the view. 

http_cache

    [non-predicate] Affects the 'Expires' and 'Cache-Control' HTTP headers in
    the response.  This tells the browser whether to cache the response and for
    how long.  The value may be an integer specifying the number of seconds to
    cache, a ``datetime.timedelta`` instance, or zero to prevent caching. This
    is equivalent to calling ``request.response.cache_expires(value)`` within
    the view code.

context

    [predicate] This view will be chosen only if the *context* is an instance
    of this class or implements this interface. This is used with traversal,
    authorization, and exception views.

request_method

    [predicate] One of the strings "GET", "POST", "PUT", "DELETE', "HEAD".
    The request method must equal this in order for the view to be chosen.
    REST applications often register multiple views for the same route, each
    with a different request method.

request_param

    [predicate] This can be a string such as "foo", indicating that the request
    must have a query parameter or POST variable named "foo" in order for
    this view to be chosen. Alternatively, if the string contains "=" such as
    "foo=1", the request must both have this parameter *and* its value must be
    as specified, or this view won't be chosen.

match_param

    [predicate] Like request_param but refers to a routing variable in the
    matchdict. In addition to the "foo" and "foo=1" syntax, you can also pass a
    dict of key/value pairs: all these routing variables must be present and have
    the specified values.

xhr, accept, header, path_info

    [predicate] These work like the corresponding arguments to
    ``config.add_route``.

custom_predicates

    [predicate] The value is a list of functions. Each function should take a
    ``context`` and ``request`` argument, and return true or false whether the
    arguments are acceptable to the view. The view will be chosen only if all
    functions return true. Note that the function arguments are different than
    the corresponding option to ``config.add_route``.

One view option you will *not* use with URL dispatch is the "name" argument.
This is used only in traversal.


Renderers
=========

A *renderer* is a post-processor for a view. It converts the view's return
value into a Response. This allows the view to avoid repetitive boilerplate
code. Pyramid ships with the following renderers: Mako, Chameleon, String,
JSON, and JSONP. The Mako and Chameleon renderers takes a dict, invoke the
specified template on it, and return a Response. The String renderer converts
any type to a string. The JSON and JSONP renderers convert any type to JSON or
JSONP. (They use Python's ``json`` serializer, which accepts a limited variety
of types.)

The non-template renderers have a constant name: ``renderer="string"``,
``renderer="json"``, ``renderer="jsonp"``. The template renderers are invoked
by a template's filename extension, so ``renderer="mytemplate.mako"`` and
``renderer="mytemplate.mak"`` go to Mako. Note that you'll need to specify a
Mako search path in the INI file or main function:

.. code-block:: ini

   [app:main]
   mako.directories = my_app_package:templates

Supposedly you can pass an asset spec rather than a relative path for the Mako
renderer, and thus avoid defining a Mako search path, but I couldn't get it to
work. Chameleon templates end in .pt and must be specified as an asset spec.

You can register third-party renderers for other template engines, and you can
also re-register a renderer under a different filename extension.  The Akhet
demo has an example of making pyramid send templates ending in .html through Mako.

You can also invoke a renderer inside view code. ::

    from pyramid.renderers import render, render_to_response

    variables = {"dear": "Mr A", "sincerely": "Miss Z", 
        "date": datetime.date.today()}

    # Render a template to a string.
    letter = render("form_letter.mako", variables, request=self.request)

    # Render a template to a Response object.
    return render_to_response("mytemplate.mako", variables,
        request=self.request)


Debugging views
===============

If you're having trouble with a route or view not being chosen when you think
it should be, try setting "pyramid.debug_notfound" and/or
"pyramid.debug_routematch" to true in *development.ini*. It will log its
reasoning to the console.


Multiple views using the same callable
======================================

You can stack multiple ``@view_config`` onto the same view method or
function, in cases where the templates differ but the view logic is the 
same.  ::

        @view_config(route_name="help", renderer="help.mak")
        @view_config(route_name="faq", renderer="faq.mak")
        @view_config(route_name="privacy", renderer="privacy_policy.mak")
        def template(request):
            return {}

        @view_config(route_name="info", renderer="info.mak")
        @view-config(route_name="info_json", renderer="json")
        def info(request):
            return {}


.. include::  ../links.rst

.. _View Configuration:  http://docs.pylonsproject.org/projects/pyramid/en/latest/narr/viewconfig.html#view-configuration-parameters
