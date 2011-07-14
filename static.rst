Serving Static Files
====================

These cookbook recipes deal with serving static files from the filesystem.

Serving a Single File from the Root
-----------------------------------

If you need to serve a single file such as ``/robots.txt`` or
``/favicon.ico`` that *must* be served from the root, you cannot use a
:term:`static view` to do it, as static views cannot serve files from the
root (a static view must have a nonempty prefix such as ``/static``).  To
work around this limitation, create views "by hand" that serve up the raw
file data.  Below is an example of creating two views: one serves up a
``/favicon.ico``, the other serves up ``/robots.txt``.

At startup time, both files are read into memory from files on disk using
plain Python.  A Response object is created for each.  This response is
served by a view which hooks up the static file's URL.

.. code-block::  python
   :linenos:

   # this module = myapp.views

   import os

   from pyramid.response import Response
   from pyramid.view import view_config

   # _here = /app/location/myapp

   _here = os.path.dirname(__file__)

   # _icon = /app/location/myapp/static/favicon.ico

   _icon = open(os.path.join(
                _here, 'static', 'favicon.ico')).read()
   _fi_response = Response(content_type='image/x-icon', 
                           body=_icon)

   # _robots = /app/location/myapp/static/robots.txt

   _robots = open(os.path.join(
                  _here, 'static', 'robots.txt')).read()
   _robots_response = Response(content_type='text/plain',
                               body=_robots)

   @view_config(name='favicon.ico')
   def favicon_view(context, request):
       return _fi_response

   @view_config(name='robots.txt')
   def robotstxt_view(context, request):
       return _robots_response

Root-Relative Custom Static View (URL Dispatch Only)
----------------------------------------------------

The :class:`pyramid.static.static_view` helper class generates a Pyramid view
callable.  This view callable can serve static assets from a directory.  An
instance of this class is actually used by the
:meth:`pyramid.config.Configurator.add_static_view` configuration method, so
its behavior is almost exactly the same once it's configured.

.. warning:: The following example *will not work* for applications that use
   :term:`traversal`, it will only work if you use :term:`URL dispatch`
   exclusively.  The root-relative route we'll be registering will always be
   matched before traversal takes place, subverting any views registered via
   ``add_view`` (at least those without a ``route_name``).  A
   :class:`pyramid.static.static_view` cannot be made root-relative when you
   use traversal.

To serve files within a directory located on your filesystem at
``/path/to/static/dir`` as the result of a "catchall" route hanging from the
root that exists at the end of your routing table, create an instance of the
:class:`pyramid.static.static_view` class inside a ``static.py`` file in your
application root as below.

.. ignore-next-block
.. code-block:: python
   :linenos:

   from pyramid.static import static_view
   www = static_view('/path/to/static/dir', use_subpath=True)

.. note:: For better cross-system flexibility, use an :term:`asset
   specification` as the argument to :class:`pyramid.static.static_view`
   instead of a physical absolute filesystem path, e.g. ``mypackage:static``
   instead of ``/path/to/mypackage/static``.

Subsequently, you may wire the files that are served by this view up to be
accessible as ``/<filename>`` using a configuration method in your
application's startup code.

.. code-block:: python
   :linenos:

   # .. every other add_route and/or add_handler declaration should come
   # before this one, as it will, by default, catch all requests

   config.add_route('catchall_static', '/*subpath', 'myapp.static.www')

The special name ``*subpath`` above is used by the
:class:`pyramid.static.static_view` view callable to signify the path of the
file relative to the directory you're serving.

