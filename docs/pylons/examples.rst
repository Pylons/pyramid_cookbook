Route and View Examples
+++++++++++++++++++++++

Here are the most common kinds of routes and views.

1. Fixed controller and action.

   ::

        # Pylons
        map.connect("faq", "/help/faq", controller="help", action="faq")
        class HelpController(Base):
            def faq(self):
                ...

   ::

        # Pyramid
        config.add_route("faq", "/help/faq")
        @view_config(route_name="faq", renderer="...")
        def faq(self):   # In some arbitrary class.
            ...

   .

2. Fixed  controller and action, plus other routing variables.

   ::

        # Pylons
        map.connect("article", "/article/{id}", controller="foo",
            action="article")
        class FooController(Base):
            def article(self, id):
                ...

   ::

        # Pyramid
        config.add_route("article", "/article/{id}")
        @view_config(route_name="article")
        def article(self):   # In some arbitrary class.
            id = self.request.matchdict["id"]


   .

3. Variable controller and action.

   ::

        # Pylons
        map.connect("/{controller}/{action}")
        map.connect("/{controller/{action}/{id}")

   ::

        # Pyramid
        # Not possible.

   You can't choose a view class via a routing variable in Pyramid.

4. Fixed controller, variable action.

   ::

        # Pylons
        map.connect("help", "/help/{action}", controller="help")

   ::

        # Pyramid
        config.add_route("help", "/help/{action}")

        @view_config(route_name="help", match_param="action=help", ...)
        def help(self):   # In some arbitrary class.
            ...

   The 'pyramid_handlers' package provides an alternative for this.

Other Pyramid examples::

    # Home route.
    config.add_route("home", "/")

    # Multi-action route, excluding certain static URLs.
    config.add_route("main", "/{action}",
        path_info=r"/(?!favicon\.ico|robots\.txt|w3c)")



pyramid_handlers
================

"pyramid_handlers_" is an add-on package that provides a possibly more
convenient way to handle case #4 above, a route with an 'action' variable
naming a view. It works like this:

.. literalinclude:: code/pyramid_handlers.py
   :linenos:

The ``add_handler`` method (line 6) registers the route and then scans the
Hello class.  It registers as views all methods that have an ``@action``
decorator, using the method name as a view predicate, so that when that method
name appears in the 'action' part of the URL, Pyramid calls this view.

The ``__autoexpose__`` class attribute (line 11) can be a regex. If any method
name matches it, it will be registered as a view even if it doesn't have an
``@action`` decorator. The default autoexpose regex matches all methods that
begin with a letter, so you'll have to set it to None to prevent methods from
being automatically exposed. You can do this in a base class if you wish.

Note that ``@action`` decorators are *not* recognized by ``config.scan()``. 
They work only with ``config.add_hander``.

User reaction to "pyramid_handlers" has been mixed. A few people are using it,
but most people use ``@view_config`` because it's "standard Pyramid".


Resouce routes
==============

"pyramid_routehelper_" provides a ``config.add_resource`` method that behaves
like Pylons' ``map.resource``. It adds a suite of routes to
list/view/add/modify/delete a resource in a RESTful manner (following the Atom
publishing protocol).  See the source docstrings in the link for details.

Note: the word "resource" here is *not* related to traversal resources.

.. include::  ../links.rst
