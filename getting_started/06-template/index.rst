=============
6: Templating
=============

Web development usually involves HTML, and web frameworks generally
provide support for HTML generation using templating languages.

Pyramid provides bundled support for the Chameleon and Mako templating
engines, with active community support for bindings such as Jinja2.

Objectives
==========

- Create a template using Chameleon and associate it with a view

- Change our tests to reflect how we test when views don't render HTML
  directly

Steps
=====

#. Again, let's use the previous package as a starting point for a new
   distribution. Also, make a directory for the templates:

   .. code-block:: bash

    (env33)$ cd ..; cp -r step05 step06; cd step06
    (env33)$ python3.3 setup.py develop
    (env33)$ mkdir tutorial/templates
    
#. Since we are using Chameleon, ``tutorial/__init__.py`` needs an additional
   configuration:
   
   .. literalinclude:: tutorial/__init__.py
       :linenos:

#. Our ``tutorial/views.py`` is now data-centric:

   .. literalinclude:: tutorial/views.py
       :linenos:

#. Create a Chameleon template in ``tutorial/templates/wiki_view.pt``:

   .. literalinclude:: tutorial/templates/wiki_view.pt
       :language: html
       :linenos:

#. Our ``tutorial/tests.py`` has a unit test which is also now
   data-centric:

   .. literalinclude:: tutorial/tests.py
       :linenos:

#. Run the tests in your package using ``nose``:

   .. code-block:: bash

    (env33)$ nosetests .
    ..
    -----------------------------------------------------------------
    Ran 2 tests in 1.971s

    OK

#. Run the WSGI application. Note the ``--reload``:

   .. code-block:: bash

    (env33)$ pserve development.ini --reload

#. Open ``http://127.0.0.1:6547/`` in your browser.

#. Edit the template and reload your browser to see the changes. Do
   the same on the ``title`` returned in ``views.py``.

Analysis
========

Our view function changed significantly. It is now a callable that
returns data, which makes test-writing much more meaningful. Our
``@view_config`` wraps the view with a ``renderer`` that is pointed at
a Chameleon template. Pyramid knows from the file suffix ``.pt`` that
this should use the Chameleon engine for rendering the response.

The use of a ``templates`` directory is purely a matter of taste. You
don't have to have a magically-named directory, or any subdirectory at
all.

Each kind of renderer (Chameleon, Mako, JSON, add-on renderers such as
Jinja) manage what goes into the namespace of the template. Chameleon
provides ``request`` automatically, for example, as well as the data
returned from the view.

The ``--reload`` argument to ``pserve`` makes it watch for changes to
certain kinds of files. For example, if you change a ``.py`` file,
the application will restart automatically.

Extra Credit
============

#. Will the application restart if I change my ``development.ini``
   configuration file? Give it a try.

#. What if I wanted to use Mako? Jinja2? Some brand new templating
   language?

#. There was a little bit of lag as I visited some views for the first
   time. What do you think was happening?

#. Can I write and register my own renderers? Should I? Can I share the
   renderers with other people?


