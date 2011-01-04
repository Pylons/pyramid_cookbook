Using a Before Render Event to Expose an ``h`` Helper Object
------------------------------------------------------------

Pylons 1.X exposed a module conventionally named ``helpers.py`` as an ``h``
object in the top-level namespace of each Mako/Genshi/Jinja2 template which
it rendered.  You can emulate the same behavior in Pyramid by using a
``BeforeRender`` event subscriber.

First, create a module named ``helpers.py`` in your Pyramid package at the
top level (next to ``__init__.py``).  We'll import the Python standard
library ``string`` module to use later in a template.

.. code-block:: python
   :linenos:

   # helpers.py

   import string

In the top of the main ``__init__`` module of your Pyramid application
package, import the new ``helpers`` module you created, as well as the
``BeforeRender`` event type.  Underneath the imports create a function that
will act as an event subscriber.

.. code-block:: python
   :linenos:

   # __init__.py

   from pyramid.events import BeforeRender
   from myapp import helpers

   def add_renderer_globals(event):
      event['h'] = helpers

Within the ``main`` function in the same ``__init__``, wire the subscriber up
so that it is called when the ``BeforeRender`` event is emitted:

.. code-block:: python
   :linenos:

   def main(global_settings, **settings):
       config = Configurator(....) # existing code
       # .. existing config statements ... #
       config.add_subscriber(add_renderer_globals, BeforeRender)
       # .. other existing config statements and eventual config.make_app()

At this point, with in any view that uses any templating system as a Pyramid
renderer, you will have an omnipresent ``h`` top-level name that is a
reference to the ``helpers`` module you created.  For example, if you have a
view like this:

.. code-block:: python
   :linenos:

   @view_config(renderer='foo.pt')
   def aview(request):
       return {}

In the ``foo.pt`` Chameleon template, you can do this:

.. code-block:: text
   :linenos:

    ${h.string.uppercase}

The value inserted into the template as the result of this statement will be
``ABCDEFGHIJKLMNOPQRSTUVWXYZ`` (at least if you are using an English system).

You can add more imports and functions to ``helpers.py`` as necessary to make
features available in your templates.
