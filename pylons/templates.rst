Templates
+++++++++

Pyramid includes adapters for two template engines, Mako and Chameleon. Mako is
Pylons' default engine so it will be familiar. Third-party adapters are
available for other engines: "pyramid_jinja2" (a Jinja2 adapter),
"pyramid_chameleon_gensi" (a partial Genshi emulator), etc. 

Mako configuration
==================

In order to use Mako as in Pylons, you must specify a template search path
in the settings:

.. code-block:: ini

   [app:main]
   ...
   mako.directories = pyramidapp:templates

This enables relative template paths like ``renderer="/mytemplate.mak"`` and
quasi-URL paths like ``renderer="/mytemplate.mak"``. It also allows templates
to inherit from other templates, import other templates, and include other
templates. Without this setting, the renderer arg will have to be in asset
spec syntax, and templates won't be able to invoke other templates. 

All settings with the "mako." prefix are passed to Mako's ``TemplateLookup``
constructor. E.g., 

.. code-block:: ini

   mako.strict_undefined = true
   mako.imports = 
        from mypackage import myfilter
   mako.filters = myfilter
   mako.module_directory = %(here)s/data/templates
   mako.preprocessor = mypackage.mako_preprocessor

Template filenames ending in ".mak" or ".mako" are sent to the Mako renderer.
If you prefer a different extension such as ".html", you can put this
in your main function::

    config.add_renderer(".html", "pyramid.mako_templating.renderer_factory")
    
If you have further questions about exactly how the Mako renderer is
implemented, it's best to look at the source: ``pyramid.mako_templating``. You
can reconcile that with the Mako documentation to confirm what argument values
cause what.

*Caution:* When I set "mako.strict_undefined" to true in an application that
didn't have Beacon sessons configured, it broke the debug toolbar. The toolbar
templates may have some sloppy placeholders not guarded by "% if".

*Caution 2:* Supposedly you can pass an asset spec instead of a template path
but I couldn't get it to work.
    

Chameleon
=========

Chameleon is an XML-based template language descended from Zope. It has some
similarities with Genshi. Its filename extension is .pt ("page template").  

Advantages of Chameleon:

* XML-based syntax.
* Template must be well-formed XHTML, suggesting (but not guaranteeing) that the
  output will be well-formed. If any variable placeholder is marked
  "structure", it's possible to insert invalid XML into the template.
* Good internationalization support in Pyramid.
* Speed is as fast as Mako. (Unusual for XML template languages.)
* Placeholder syntax "${varname or expression}" is common to Chameleon, Mako,
  and Genshi.
* Chameleon does have a text mode which accepts non-XML input, but you lose all
  control structures except "${varname}".

Disadvantages of Chameleon:

* XML-based syntax.
* Filenames must be in asset spec syntax, not relative paths:
  ``renderer="mypackage:templates/foo.pt"``, ``renderer="templates/foo.pt"``.
  You can't get rid of that "templates/" prefix without writing a wrapper
  ``view_config`` decorator.
* No template lookup, so you can't invoke one template from inside another
  without pre-loading the template into a variable.
* If template is not well-formed XML, the user will get an unconditional
  "Internal Server Error" rather than something that might look fine in the
  browser and which the user can at least read some content from.
* It doesn't work on all platforms Mako and Pyramid do. (Only CPython and
  Google App Engine.)

Renderer globals
================

Whenever a renderer invokes a template, the template namespace includes all the
variables in the view's return dict, plus the following system variables:

.. attribute:: request, req
   :noindex:

   The current request.

.. attribute:: view

   The view instance (for class-based views) or function (for function-based
   views). You can read instance attributes directly:  ``view.foo``.

.. attribute:: context
   :noindex:

   The context (same as ``request.context``).  (Not visible in Mako because
   Mako has a built-in variable with this name; use ``request.context``
   instead.)

.. attribute:: renderer_name
   :noindex:

   The fully-qualified renderer name; e.g., "zzz:templates/foo.mako".

.. attribute:: renderer_info
   :noindex:

   An object with attributes ``name``, ``package``, and ``type``.


The Akhet demo shows how to inject other variables into all templates, such as
a helpers module ``h``, a URL generator ``url``,  the session variable
``session``, etc.


Site template
=============

Most sites will use a site template combined with page templates to ensure
that all the pages have the same look and feel (header, sidebars, and footer).
Mako's inheritance makes it easy to make page templates inherit from a site
template. Here's a very simple site template:

.. code-block::  mako

    <!DOCTYPE html>
    <html>
      <head>
        <title>My Application</title>
      </head>
      <body>

    <!-- *** BEGIN page content *** -->
    ${self.body()}
    <!-- *** END page content ***-->

      </body>
    </html>

... and a page template that uses it:

.. code-block:: mako

    <%inherit file="/site.html" />

    <p>
      Welcome to <strong>${project}</strong>, an application ...
    </p>


A more elaborate example is in the Akhet demo.
