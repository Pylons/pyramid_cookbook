Static Files
++++++++++++

In Pylons, the application's "public" directory is configured as a static
overlay on "/", so that URL "/images/logo.png" goes to
"pylonsapp/public/images/logo.png". This is done using a middleware. Pyramid
does not have an exact equivalent but it does have a way to serve static files,
and add-on packages provide additional ways.


Static view
===========

This is Pyramid's default way to serve static files. As you'll remember from
the main function in an earlier chapter::

    config.add_static_view('static', 'static', cache_max_age=3600)

This tells Pyramid to publish the directory "pyramidapp/static" under URL
"/static", so that URL "/static/images/logo.png" goes to
"pyramidapp/static/images/logo.png". 

It's implemented using *traversal*, which we haven't talked about much in this
Guide. Traversal-based views have a *view name* which serves as a URL prefix or
component. The first argument is the view name ("static"), which implies it
matches URL "/static". The second argument is the asset spec for the directory
(relative to the application's Python package). The keyword arg is an option
which sets the HTTP expire headers to 3600 seconds (1 hour) in the future.
There are other keyword args for permissions and such.

Pyramid's static view has the following advantages over Pylons:

* It encourages all static files to go under a single URL prefix, so they're
  not scattered around the URL space.
* Methods to generate URLs are provided: ``request.static_url()`` and
  ``request.static_path()``.
* The deployment configuration (INI file) can override the base URL ("/static")
  to serve files from a separate static media server
  ("http://static.example.com/").
* The deployment configuration can also override items in the static directory,
  pointing to other subdirectories or files instead. This is called "overriding
  assets" in the Pyramid manual.

It has the following disadvantages compared to Pylons:

* Static URLs have the prefix "/static". 
* It can't serve top-level file URLs such as "/robots.txt" and "/favicon.ico".

You can serve any URL directory with a static view, so you could have a
separate view for each URL directory like this::

    config.add_static_view('images', 'static/images')
    config.add_static_view('stylesheets', 'static/stylesheets')
    config.add_static_view('javascript', 'static/javascript')

This configures URL "/images" pointing to directory "pyramidapp/static/images",
etc. 

If you're using Pyramid's authorization system, you can also make a separate
view for files that require a certain permission::

    config.add_static_view("private", "private", permission="admin")


Generating static URLs
----------------------

You can generate a URL to a static file like this:

.. code-block:: mako

   href="${request.static_url('static/images/logo.png')}

Top-level file URLs
-------------------

So how do you get around the problem of top-level file URLs? You can register
normal views for them, as shown later below. For "/favicon.ico", you can
replace it with an HTTP header in your site template:

.. code-block:: html

   <link rel="shortcut icon" href="${request.static_url('pyramidapp:static/favicon.ico')}" />

The standard Pyramid scaffolds actually do this. For "/robots.txt", you may
decide that this actually belongs to the webserver rather than the application,
and so you might have Apache serve it directly like this:

.. code-block:: apache

   Alias   /robots.txt   /var/www/static/norobots.txt

You can of course have Apache serve your static directory too:

.. code-block:: apache

   Alias   /static   /PATH-TO/PyramidApp/pyramidapp/static
   
But if you're using mod_proxy you'll have to disable proxying that directory
*early* in the virtualhost configuration:

.. code-block:: apache

   Alias ProxyPass   /static   !

If you're using RewriteRule in combination with other path directives like
Alias, read the RewriteRule flags documentation (especially "PT" and "F") to
ensure the directives cooperate as expected.

External static media server
----------------------------

To make your configuration flexible for a static media server:

.. code-block:: ini

    # In INI file
    static_assets = "static"
    # -OR-
    static_assets = "http://staticserver.com/"

Main function::

    config.add_static_view(settings["static_assets"], "zzz:static")

Now it will generate "http://mysite.com/static/foo.jpg" or
"http://staticserver.com/foo.jpg" depending on the configuration.


Static route
============

This strategy is available in Akhet. It overlays the static directory on top of
"/" like Pylons does, so you don't have to change your URLs or worry about
top-level file URLs.  ::

    config.include('akhet')
    # Put your regular routes here.
    config.add_static_route('zzz', 'static', cache_max_age=3600)
    # Arg 1 is the Python package containing the static files.
    # Arg 2 is the subdirectory in the package containing the files.

This registes a static route matching all URLs, and a view to serve it.
Actually, the route will have a predicate that checks whether the file exists,
and if it doesn't, the route won't match the URL. Still, it's good practice to
register the static route after your other routes. 

If you have another catchall route before it that might match some static URLs,
you'll have to exclude those URLs from the route as in this example::

    config.add_route("main", "/{action}",
        path_info=r"/(?!favicon\.ico|robots\.txt|w3c)")
    config.add_static_route('zzz', 'static', cache_max_age=3600)

The static route implementation does *not* generate URLs to static files, so
you'll have to do that on your own. Pylons never did it very effectively
either.


Other ways to serve top-level file URLs
=======================================

If you're using the static view and still need to serve top-level file URLs,
there are several ways to do it.

A manual file view
------------------

This is documented in the Pyramid manual in the Static Assets chapter. ::

    # Main function.
    config.add_route("favicon", "/favicon.ico")

    # Views module.
    import os
    from pyramid.response import FileResponse

    @view_config(route_name="favicon")
    def favicon_view(request):
        here = os.path.dirname(__file__)
        icon = os.path.join(here, "static", "favicon.ico")
        return FileResponse(icon, request=request)


Or if you're really curious how to configure the view for traversal without a
route::

    @view_config(name="favicon.ico")


pyramid_assetviews
------------------

"`pyramid_assetviews`_" is a third-party package for top-level file URLs. ::

    # In main function.
    config.include("pyramid_assetviews")
    config.add_asset_views("static", "robots.txt")  # Defines /robots.txt .

    # Or to register multiple files at once.
    filenames = ["robots.txt", "humans.txt", "favicon.ico"]
    config.add_asset_views("static", filenames=filenames, http_cache=3600)

Of course, if you have the files in the static directory they'll still be
visible as "/static/robots.txt" as well as "/robots.txt". If that bothers you,
make another directory outside the static directory for them.

.. _pyramid_assetviews: https://pyramid_assetviews.readthedocs.org/en/latest/

