.. _traversal_in_views:

Using Traversal in Pyramid Views
================================

A trivial example of how to use :term:`traversal` in your view code.

You may remember that a Pyramid :term:`view` is called with a
:term:`context` argument.

.. code-block:: python

    def my_view(context, request):
        return render_view_to_response(context, request)


When using traversal, ``context`` will be the :term:`resource` object
that was found by traversal.  Configuring which resources a view
responds to can be done easily via either the ``@view.config``
decorator.

.. code-block:: python

    from models import MyResource

    @view_config(context=MyResource)
    def my_view(context, request):
        return render_view_to_response(context, request)

or via ``config.add_view``::

    from models import MyResource
    config = Configurator()
    config.add_view('myapp.views.my_view', context=MyResource)

Either way, any request that triggers traversal and traverses to a
``MyResource`` instance will result in calling this view with that
instance as the ``context`` argument.

Optional: Using Interfaces
--------------------------

If your resource classes implement :term:`interfaces <interface>`,
you can configure your views by interface. This is one way to decouple
view code from a specific resource implementation.

.. code-block:: python

    # models.py
    from zope.interface import implements
    from zope.interface import Interface
    
    class IMyResource(Interface):
        pass
    
    class MyResource(object):
        implements(IMyResource)
    
    # views.py
    from models import IMyResource
    
    @view_config(context=IMyResource)
    def my_view(context, request):
        return render_view_to_response(context, request)


See Also
--------

- :ref:`much_ado_about_traversal_chapter`

- :ref:`comparing_traversal_and_dispatch`

- The "Virginia" sample application: https://github.com/Pylons/virginia/blob/master/virginia/views.py

- ZODB and Traversal in Pyramid tutorial: https://docs.pylonsproject.org/projects/pyramid/en/latest/tutorials/wiki/index.html#bfg-wiki-tutorial

- Resources which implement interfaces: https://docs.pylonsproject.org/projects/pyramid/en/latest/narr/resources.html#resources-which-implement-interfaces
