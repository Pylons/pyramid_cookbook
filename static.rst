Serving Static Files
====================

These cookbook recipes deal with serving static files from the filesystem.

Root-Relative Custom Static View (URL Dispatch Only)
----------------------------------------------------

The :class:`pyramid.view.static` helper class generates a Pyramid view
callable.  This view callable can serve static assets from a directory.  An
instance of this class is actually used by the
:meth:`pyramid.config.Configurator.add_static_view` configuration method, so
its behavior is almost exactly the same once it's configured.

.. warning:: The following example *will not work* for applications that use
   :term:`traversal`, it will only work if you use :term:`URL dispatch`
   exclusively.  The root-relative route we'll be registering will always be
   matched before traversal takes place, subverting any views registered via
   ``add_view`` (at least those without a ``route_name``).  A
   :class:`pyramid.view.static` static view cannot be made root-relative when
   you use traversal.

To serve files within a directory located on your filesystem at
``/path/to/static/dir`` as the result of a "catchall" route hanging from the
root that exists at the end of your routing table, create an instance of the
:class:`pyramid.view.static` class inside a ``static.py`` file in your
application root as below.

.. ignore-next-block
.. code-block:: python
   :linenos:

   from pyramid.view import static
   static_view = static('/path/to/static/dir')

.. note:: For better cross-system flexibility, use an :term:`asset
   specification` as the argument to :class:`pyramid.view.static` instead of
   a physical absolute filesystem path, e.g. ``mypackage:static`` instead of
   ``/path/to/mypackage/static``.

Subsequently, you may wire the files that are served by this view up to be
accessible as ``/<filename>`` using a configuration method in your
application's startup code.

.. code-block:: python
   :linenos:

   # .. every other add_route and/or add_handler declaration should come
   # before this one, as it will, by default, catch all requests

   config.add_route('catchall_static', '/*subpath', 'myapp.static.static_view')

The special name ``*subpath`` above is used by the
:class:`pyramid.view.static` view callable to signify the path of the file
relative to the directory you're serving.

