Other Pyramid Features
++++++++++++++++++++++

Shell
=====

Pyramid has a command to preload your application into an interactive Python
prompt. This can be useful for debugging or experimentation. The command is
"pshell", akin to "paster shell" in Pylons.

.. code-block:: sh

   $ pshell development.ini
   Python 2.6.5 (r265:79063, Apr 29 2010, 00:31:32)
   [GCC 4.4.3] on linux2
   Type "help" for more information.

   Environment:
     app          The WSGI application.
     registry     Active Pyramid registry.
     request      Active request object.
     root         Root of the default resource tree.
     root_factory Default root factory used to create `root`.

   >>>

It doesn't initialize quite as many globals as Pylons, but ``app`` and
``request`` will be the most useful.


Other commands
==============

Other commands available:

* proutes: list the application's routes. (Akin to Pylons "paster routes".)
* pviews: list the application's views.
* ptweens: list the application's tweens.
* prequest: load the application, process a specified URL, and print the
  response body on standard output.

Forms
=====

Pyramid does not include a form library. Pylons includes WebHelpers for form
generation and FormEncode for validation and error messages. These work under
Pyramid too. However, there's no built-in equivalent to Pylons' ``@validate``
decorator. Instead we recommend the "pyramid_simpleform_" package, which
replaces @validate with a more flexible structure. 

There are several other form libraries people use with Pyramid. These are
discussed in the regular Forms_ section in the Pyramid Community Cookbook.

WebHelpers
==========

WebHelpers is a third-party package containing HTML tag builders, text
functions, number formatting and statistical functions, and other generic
functions useful in templates and views. It's a Pylons dependency but is
optional in Pyramid.

The ``webhelpers.pylonslib`` subpackage does not work with Pyramid because it
depends on Pylons' special globals. ``webhelpers.mimehelper`` and
``webhelpers.paginate`` have Pylons-specific features that are disabled under
other frameworks.  WebHelpers has not been tested on Python 3.

The next version of WebHelpers may be released as a different distribution 
(WebHelpers2) with a subset of the current helpers ported to Python 3. It will
probably spin off Paginate and the Feed Generator to separate distribitions.


Events
======

The events framework provides hooks where you can insert your own code into the
request-processing sequence, similar to how Apache modules work. It standarizes
some customizations that were provided ad-hoc in Pylons or not at all. To use
it, write a callback function for one of the event types in ``pyramid.events``:
``ApplicationCreated``, ``ContextFound``, ``NewResponse``, ``BeforeRender``.
The callback takes an event argument which is specific to the event type.
You can register the event with ``@asubscriber`` or
``config.add_subscriber()``.  The Akhet demo has examples.

For more details see:

* `Using Events * <http://docs.pylonsproject.org/projects/pyramid/en/latest/narr/events.html>`_
* `Using The Before Render Event <http://docs.pylonsproject.org/projects/pyramid/en/latest/narr/hooks.html#using-the-before-render-event>`_
* `pyramid.event API <http://docs.pylonsproject.org/projects/pyramid/en/latest/api/events.html>`_

URL generation
==============

Pyramid does not come with a URL generator equivalent to "pylons.url".
Individual methods are available on the Request object to generate specific
kinds of URLs. Of these, route_url covers the normal case of generating a route
by name::

    request.route_url("route_name", variable1="value1")
    request.route_path("route_name", variable1="value1")
    request.route_url("search", _query={"q": "search term"}, _anchor="results")

As with all the \*_url vs \*_path methods, ``route_url`` generates an absolute
URL, while ``route_path`` generates a "slash" URL (without the scheme or host).
The ``_query`` argument is a dict of query parameters (or a sequence of
key-value pairs). The ``_anchor`` argument makes a URL with a "#results"
fragment. Other special keyword arguments are ``_scheme``, ``_host``,
``_port``, and ``_app_url``.

The advantage of using these methods rather than hardcoding the URL, is that it
automatically addds the application prefix (which may be something more than
"/" if the application is mounted on a sub-URL).

You can also pass additional positional arguments, and they will be appended
to the URL as components. This is not very useful with URL dispatch, it's more
of a traversal thing.

If the route is defined with a *pregenerator*, it will be called with the
positional and keyword arguments, and can modify them before the URL is
generated.

Akhet has a URLGenerator class, which you can use as shown in the Akhet demo to
make a ``url`` variable for your templates, using an event subscriber. Then you
can do things like this::

    url.route("route_name")          # Generate URL by route name.
    url("route_name")                # The same.
    url.app                          # The application's top-level URL.
    url.current()                    # The current request URL. (Used to
                                     # link to the same URL with different
                                     # match variables or query params.)

You can also customize it to do things like this::

    url.static("images/logo.png")    
    url.image("logo.png")            # Serve an image from the images dir.
    url.deform("...")                # Static file in the Deform package.

If "url" is too long for you, you can even name it "u"!


Utility scripts
===============

Pyramid has a documented way to write utility scripts for maintenance and the
like. See `Writing a Script`_.

Testing
=======

Pyramid makes it easier to write unit tests for your views. 

(XXX Need a comparison example.)

Internationalization
====================

Pyramid has support for internationalization. At this time it's documented
mainly for Chameleon templates, not Mako.


Higher-level frameworks
=======================

Pyramid provides a flexible foundation to build higher-level frameworks on.
Several have already been written.  There are also application scaffolds and
tarballs.

* Kotti_ is a content management system that both works out of the box and can
  be extended. 
* Ptah_ is a framework that aims to have as many features as Django. (But no
  ponies, and no cowbells.) It has a minimal CMS component.
* Khufu_ is a suite of scaffolds and utilities for Pyramid.
* The Akhet_ demo we have mentioned before. It's a working application in a
  tarball that you can copy code from.

At the opposite extreme, you can make a tiny Pyramid application in 14 lines of
Python without a scaffold.  The Pyramid manual has an example: `Hello World`_.
This is not possible with Pylons -- at least, not without distorting it
severely.


.. include::  ../links.rst

.. _Forms: ../forms/index.html
.. _Writing a Script: http://docs.pylonsproject.org/projects/pyramid/en/latest/narr/commandline.html?highlight=pshell#writing-a-script
.. _Hello World: http://docs.pylonsproject.org/projects/pyramid/en/latest/narr/firstapp.html#hello-world
