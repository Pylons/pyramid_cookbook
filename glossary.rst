.. _glossary:

Glossary
========

.. glossary::
   :sorted:

   traversal
     The act of descending "up" a tree of resource objects from a root
     resource in order to find a :term:`context` resource.  See the
     :ref:`traversal_chapter` chapter for more information.

   context
     An resource in the resource tree that is found during :term:`traversal`
     or :term:`URL dispatch` based on URL data; if it's found via traversal,
     it's usually a :term:`resource` object that is part of a resource tree;
     if it's found via :term:`URL dispatch`, it's a object manufactured on
     behalf of the route's "factory".  A context resource becomes the subject
     of a :term:`view`, and often has security information attached to
     it.  See the :ref:`traversal_chapter` chapter and the
     :ref:`urldispatch_chapter` chapter for more information about how a URL
     is resolved to a context resource.

   resource
     An object representing a node in the :term:`resource tree` of an
     application.  If :mod:`traversal` is used, a resource is an element in
     the resource tree traversed by the system.  When traversal is used, a
     resource becomes the :term:`context` of a :term:`view`.  If :mod:`url
     dispatch` is used, a single resource is generated for each request and
     is used as the context resource of a view.

   resource tree
     A nested set of dictionary-like objects, each of which is a
     :term:`resource`.  The act of :term:`traversal` uses the resource tree
     to find a :term:`context` resource.

   URL dispatch
     An alternative to :term:`traversal` as a mechanism for locating a
     :term:`context` resource for a :term:`view`.  When you use a
     :term:`route` in your Pyramid application via a :term:`route
     configuration`, you are using URL dispatch. See the
     :ref:`urldispatch_chapter` for more information.

   view
     Common vernacular for a :term:`view callable`.

   view callable
     A "view callable" is a callable Python object which is associated
     with a :term:`view configuration`; it returns a :term:`response`
     object .  A view callable accepts a single argument: ``request``,
     which will be an instance of a :term:`request` object.  An
     alternate calling convention allows a view to be defined as a
     callable which accepts a pair of arguments: ``context`` and
     ``request``: this calling convention is useful for
     traversal-based applications in which a :term:`context` is always
     very important.  A view callable is the primary mechanism by
     which a developer writes user interface code within
     Pyramid.  See :ref:`views_chapter` for more information
     about Pyramid view callables.

   request
     A ``WebOb`` request object.  See :ref:`webob_chapter` (narrative)
     and :ref:`request_module` (API documentation) for information
     about request objects.

   response
     An object that has three attributes: ``app_iter`` (representing an
     iterable body), ``headerlist`` (representing the http headers sent
     to the user agent), and ``status`` (representing the http status
     string sent to the user agent).  This is the interface defined for
     ``WebOb`` response objects.  See :ref:`webob_chapter` for
     information about response objects.

   router
     The :term:`WSGI` application created when you start a Pyramid
     application.  The router intercepts requests, invokes traversal and/or
     URL dispatch, calls view functions, and returns responses to the WSGI
     server on behalf of your Pyramid application.

   WSGI
     `Web Server Gateway Interface <http://wsgi.org/>`_.  This is a
     Python standard for connecting web applications to web servers,
     similar to the concept of Java Servlets.  Pyramid requires
     that your application be served as a WSGI application.

   view configuration
     View configuration is the act of associating a :term:`view callable`
     with configuration information.  This configuration information helps
     map a given :term:`request` to a particular view callable and it can
     influence the response of a view callable.  See
     :ref:`view_config_chapter` for more information about view
     configuration.

   route
     A single pattern matched by the :term:`url dispatch` subsystem,
     which generally resolves to a :term:`root factory` (and then
     ultimately a :term:`view`).  See also :term:`url dispatch`.

   root factory
     The "root factory" of an Pyramid application is called
     on every request sent to the application.  The root factory
     returns the traversal root of an application.

   route configuration
     Route configuration is the act of associating request parameters with a
     particular :term:`route` using pattern matching.  See
     :ref:`urldispatch_chapter` for more information about route
     configuration.

   asset
     Any file contained within a Python :term:`package` which is *not*
     a Python source code file.

   asset specification
     A colon-delimited identifier for an :term:`asset`.  The colon
     separates a Python :term:`package` name from a package subpath.
     For example, the asset specification
     ``my.package:static/baz.css`` identifies the file named
     ``baz.css`` in the ``static`` subdirectory of the ``my.package``
     Python :term:`package`.  See :ref:`asset_specifications` for more 
     info.

   package
     A directory on disk which contains an ``__init__.py`` file, making
     it recognizable to Python as a location which can be ``import`` -ed.
     A package exists to contain :term:`module` files.

   module
     A Python source file; a file on the filesystem that typically ends with
     the extension ``.py`` or ``.pyc``.  Modules often live in a 
     :term:`package`.

   static view
      A view added to a Pyramid application via
      :meth:`pyramid.config.Configurator.add_static_view`.
