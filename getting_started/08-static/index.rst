================
8: Static Assets
================

Web applications include many static assets in the UX: CSS and JS files,
images, etc. Web frameworks need to support productive development by
the UX team, but also the richness and complexity required by the core
developers and the deployment team.

It’s a surprisingly hard problem, supporting all these needs while
keeping the simple case easy.

Pyramid accomplishes this using the view machinery and static assets.

Objectives
==========

- Use ``add_static_view`` serve a project directory at a URL

- Introduce some dummy data to provide dynamicism

Steps
=====

#. Again, let's use the previous package as a starting point for a new
   distribution, plus make a new directory for the static assets:

   .. code-block:: bash

    (env33)$ cd ..; cp -r step07 step08; cd step08
    (env33)$ mkdir tutorial/static
    (env33)$ python3.3 setup.py develop

#. The ``Configurator`` needs to be told about the static files by
   calling its ``add_static_view``:

    .. literalinclude:: tutorial/__init__.py
        :linenos:

#. Our ``tutorial/views.py`` has some extras with dummy data driving
   the listing and viewing:

   .. literalinclude:: tutorial/views.py
        :linenos:

#. Make a ``tutorial/static/wiki.css`` for the styling:

   .. literalinclude:: tutorial/static/wiki.css
    :language: css

#. We also have a :download:`logo PNG file <tutorial/static/logo.png>`
   that we need saved at ``tutorial/static/logo.png``.

#. The ``tutorial/templates/layout.pt`` includes the CSS on all pages,
   plus adds a logo that goes back to the wiki home:

   .. literalinclude:: tutorial/templates/layout.pt
    :linenos:
    :language: html

#. ``tutorial/templates/wiki_view.pt`` switches to a more-general
   syntax for computing URLs, plus iterates over the actual (dummy) data
   for listing each wiki page:

   .. literalinclude:: tutorial/templates/wiki_view.pt
    :linenos:
    :language: html

#. We also change ``tutorial/templates/wikipage_view.pt`` to use the
   ``route_url`` approach to URLs:

   .. literalinclude:: tutorial/templates/wikipage_view.pt
    :linenos:
    :language: html

#. Run the tests in your package using ``nose``:

   .. code-block:: bash

    (env33)$ nosetests .
    ..
    -----------------------------------------------------------------
    Ran 2 tests in 1.971s

    OK

#. Run the WSGI application:

   .. code-block:: bash

    (env33)$ pserve development.ini --reload

#. Open ``http://127.0.0.1:6547/`` in your browser.

Analysis
========

- Use request.route_url instead of ``/``
- Module-level dummy data structure



Extra Credit
============

