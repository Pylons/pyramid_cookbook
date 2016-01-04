==============================
1: Template Layout Preparation
==============================

Get a Twitter Bootstrap-themed set of Jinja2 templates in place.

Background
==========

In this traversal tutorial, we'll have a number of views and templates, each
with some styling and layout. Let's work efficiently and produce decent visual
appeal by getting some views and Jinja2 templates with our basic layout.

Objectives
==========

- Get a basic Pyramid project in place with views and templates based on
  ``pyramid_jinja2``.

- Have a "layout" master template and some included subtemplates.

Steps
=====

#. Let's start with an empty hierarchy of directories. Starting in a tutorial
   workspace (e.g., ``quick_traversal``):

   .. code-block:: bash

    $ mkdir -p layout/tutorial/templates
    $ cd layout

#. Make a ``layout/setup.py``:

   .. literalinclude:: layout/setup.py
      :linenos:

#. You can now install the project in development mode:

   .. code-block:: bash

    $ $VENV/bin/python setup.py develop

#. We need a configuration file at ``layout/development.ini``:

   .. literalinclude:: layout/development.ini
    :language: ini
    :linenos:

#. In ``layout/tutorial/__init__.py`` wire up ``pyramid_jinja2`` and scan for
   views:

   .. literalinclude:: layout/tutorial/__init__.py
      :linenos:

#. Our views in ``layout/tutorial/views.py`` just has a single view that will
   answer an incoming request for ``/hello``:

   .. literalinclude:: layout/tutorial/views.py
      :linenos:

#. The view's renderer points to a template at
   ``layout/tutorial/templates/site.jinja2``:

   .. literalinclude:: layout/tutorial/templates/site.jinja2
    :language: jinja
    :linenos:

#. That template asks to use a master "layout" template at
   ``layout/tutorial/templates/layout.jinja2``:

   .. literalinclude:: layout/tutorial/templates/layout.jinja2
    :language: jinja
    :linenos:

#. The layout includes a header at
   ``layout/tutorial/templates/header.jinja2``:

   .. literalinclude:: layout/tutorial/templates/header.jinja2
    :language: jinja
    :linenos:

#. The layout also includes a subtemplate for breadcrumbs at
   ``layout/tutorial/templates/breadcrumbs.jinja2``:

   .. literalinclude:: layout/tutorial/templates/breadcrumbs.jinja2
    :language: jinja
    :linenos:

#. Simplified tests in ``layout/tutorial/tests.py``:

   .. literalinclude:: layout/tutorial/tests.py
      :linenos:

#. Now run the tests:

   .. code-block:: bash

    $ $VENV/bin/nosetests tutorial
    .
    ----------------------------------------------------------------------
    Ran 2 tests in 0.141s

    OK

#. Run your Pyramid application with:

   .. code-block:: bash

    $ $VENV/bin/pserve development.ini --reload

#. Open ``http://localhost:6543/hello`` in your browser.

Analysis
========

The ``@view_config`` uses a new attribute: ``name='hello'``. This, as we'll see
in this traversal tutorial, makes a ``hello`` location available in URLs.

The view's renderer uses Jinja2's mechanism for pointing at a master layout and
filling certain areas from the view templates. The layout provides a basic HTML
layout and points at Twitter Bootstrap CSS on a content delivery network for
styling.
