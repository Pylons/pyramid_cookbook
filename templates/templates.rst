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


Using a BeforeRender Event to Expose Chameleon ``base`` Template
----------------------------------------------------------------

To avoid defining the same basic things in each template in your application,
you can define one ``base`` tamplate, and inherit from it in other templates.

.. note:: Pyramid example application - `shootout
   <https://github.com/Pylons/shootout>`_ using this approach.

First, add subscriber within your Pyramid project's __init__.py:

.. code-block:: python
   :linenos:

   config.add_subscriber('YOURPROJECT.subscribers.add_base_template',
                         'pyramid.events.BeforeRender')

Then add the ``subscribers.py`` module to your project's directory:

.. code-block:: python
   :linenos:

   from pyramid.renderers import get_renderer

   def add_base_template(event):
       base = get_renderer('templates/base.pt').implementation()
       event.update({'base': base})

After this has been done, you can use your ``base`` template to extend other
templates. For example, the ``base`` template looks like this:

.. code-block:: html
   :linenos:

   <html xmlns="http://www.w3.org/1999/xhtml"
         xmlns:tal="http://xml.zope.org/namespaces/tal"
         xmlns:metal="http://xml.zope.org/namespaces/metal"
	 metal:define-macro="base">
       <head>
           <meta http-equiv="content-type" content="text/html; charset=utf-8" />
           <title>My page</title>
       </head>
       <body>
           <tal:block metal:define-slot="content">
           </tal:block>
       </body>
   </html>

Each template using the ``base`` template will look like this:

.. code-block:: html
   :linenos:

   <html xmlns="http://www.w3.org/1999/xhtml"
         xmlns:tal="http://xml.zope.org/namespaces/tal"
         xmlns:metal="http://xml.zope.org/namespaces/metal"
         metal:use-macro="base.macros['base']">
       <tal:block metal:fill-slot="content">
           My awesome content.
       </tal:block>
   </html>

The ``metal:use-macro="base.macros['base']"`` statement is essential here.
Content inside ``<tal:block metal:fill-slot="content"></tal:block>`` tags
will replace corresponding block in ``base`` template. You can define
as many slots in as you want. For more information please see
`Macro Expansion Template Attribute Language
<http://chameleon.repoze.org/docs/latest/metal.html>`_ documentation.

Using Building Blocks with Chameleon
------------------------------------

If you understood the ``base`` template chapter, using building blocks
is very simple and straight forward. In the ``subscribers.py``module
extend the ``add_base_template`` function like this:

.. code-block:: python
   :linenos:

   from pyramid.renderers import get_renderer
   
   @subscriber(BeforeRender)
   def add_base_template(event):
       base = get_renderer('templates/base.pt').implementation()
       blocks = get_renderer('templates/blocks.pt').implementation()
       event.update({'base': base,
                     'blocks': blocks,
                     })

Now, define your building blocks in ``templates/blocks.pt``. For
example:

.. code-block:: html
   :linenos:

   <html xmlns="http://www.w3.org/1999/xhtml"
         xmlns:tal="http://xml.zope.org/namespaces/tal"
         xmlns:metal="http://xml.zope.org/namespaces/metal">
     <tal:block metal:define-macro="base-paragraph">
       <p class="foo bar">
         <tal:block metal:define-slot="body">
         </tal:block>
       </p>
     </tal:block>
   
     <tal:block metal:define-macro="bold-paragraph"
                metal:extend-macro="macros['base-paragraph']">
       <tal:block metal:fill-slot="body">
         <b class="strong-class">
           <tal:block metal:define-slot="body"></tal:block>
         </b>
       </tal:block>
     </tal:block>
   </html>

You can now use these building blocks like this:

.. code-block:: html
   :linenos:

   <html xmlns="http://www.w3.org/1999/xhtml"
         xmlns:tal="http://xml.zope.org/namespaces/tal"
         xmlns:metal="http://xml.zope.org/namespaces/metal"
   	 metal:use-macro="base.macros['base']">
     <tal:block metal:fill-slot="content">
       <tal:block metal:use-macro="blocks.macros['base-paragraph']">
         <tal:block metal:fill-slot="body">
           My awesome paragraph.
         </tal:block>
       </tal:block>
   
       <tal:block metal:use-macro="blocks.macros['bold-paragraph']">
         <tal:block metal:fill-slot="body">
           My awesome paragraph in bold.
         </tal:block>
       </tal:block>
   
     </tal:block>
   </html>

Rendering ``None`` as the Empty String in Mako Templates
--------------------------------------------------------

For the following Mako template:

.. code-block:: html

   <p>${nunn}</p>

By default, Pyramid will render:

.. code-block:: html

   <p>None</p>

Some folks prefer the the value ``None`` to be rendered as the empty string
in a Mako template.  In other words, they'd rather the output be:

.. code-block:: html

   <p></p>

Use the following settings in your Pyramid configuration file to obtain this
behavior:

.. code-block:: ini

   [app:myapp]
   mako.imports = from markupsafe import escape_silent
   mako.default_filters = escape_silent

