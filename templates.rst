Templates
=========

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


Using a BeforeRender Event to Expose Chameleon ``base`` template
------------------------------------------------------------

To avoid defining the same basic things in each template in your application,
you can define one ``base`` tamplate, and inherit from it in other templates.

.. note:: Pyramid example application - `shootout
   <https://github.com/Pylons/shootout>`_ using this approach.

First, add subscriber within your Pyramid project's __init__.py:

.. code-block:: python
   :linenos:

   config.add_subscriber('YOURPROJECT.subscribers.add_base_template',
                         'pyramid.events.BeforeRender')

Then add a ``subscribers.py`` module to your project's directory:

.. code-block:: python
   :linenos:

   from pyramid.renderers import get_renderer

   def add_base_template(event):
       base = get_renderer('templates/base.pt').implementation()
       event.update({'base': base})

After this has been done, you can use your ``base`` template to extend other
templates. For example, for the ``base`` template that looks like this:

.. code-block:: html
   :linenos:

   <html xmlns="http://www.w3.org/1999/xhtml"
         xmlns:tal="http://xml.zope.org/namespaces/tal"
         xmlns:metal="http://xml.zope.org/namespaces/metal">
       <head>
           <meta http-equiv="content-type" content="text/html; charset=utf-8" />
           <title>My page</title>
       </head>
       <body>
           <tal:block metal:define-slot="content">
           </tal:block>
       </body>
   </html>

Each template which is using the ``base`` template will look like this:

.. code-block:: html
   :linenos:

   <html xmlns="http://www.w3.org/1999/xhtml"
         xmlns:tal="http://xml.zope.org/namespaces/tal"
         xmlns:metal="http://xml.zope.org/namespaces/metal"
         metal:use-macro="base">
       <tal:block metal:fill-slot="content">
           My awesome content.
       </tal:block>
   </html>

The ``metal:use-macro="base"`` statement is essential here.
Content inside ``<tal:block metal:fill-slot="content"></tal:block>`` tags
will replace corresponding block in ``base`` template. You can define
as many slots in as you want. For more information please see
`Macro Expansion Template Attribute Language
<http://chameleon.repoze.org/docs/latest/metal.html>`_ documentation.
