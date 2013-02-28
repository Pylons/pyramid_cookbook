=============
5: Templating
=============

Web development usually involves HTML, and web frameworks generally
provide support for HTML generation using templating languages.

Pyramid provides bundled support for the Chameleon and Mako templating
engines, with active community support for bindings such as Jinja2.

Goals
=====

- Introduce concept of templating

- See how it changes how we develop views

Objectives
==========

- Create a template using Chameleon and asssociate it with a view

- Change our tests to reflect how we test when views don't render HTML
  directly

Steps
=====

#. Again, let's use the previous package as a starting point for a new
   distribution. Also, make a directory for the templates:

   .. code-block:: bash

    (env33)$ cd ..; cp -r step04 step05; cd step05
    (env33)$ python3.3 setup.py develop
    (env33)$ mkdir tutorial/templates

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
   the same on the string returned in ``views.py``.

Analysis
========

- Don't have to have a ``templates`` directory

- How does reload work

Extra Credit
============

#. What if I wanted to use Mako? Jinja2? Some brand new templating
   language?

