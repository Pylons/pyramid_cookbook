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

#. The ``Configurator`` needs to be told in ``tutorial/__init__.py``
   about the static files by
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
   that we need saved at ``tutorial/static/logo.png``. Click this link
   to download and save the image.

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

We made files and directories in ``tutorial/static`` available at the
URL ``static``. However, we used ``tutorial:static`` as the argument in
``add_static_view``. Pyramid uses a robust scheme called *asset
specifications* to work with static assets.

In our templates, we resolved the full path to a static asset in a
package by using ``request.static_url`` and passing in an asset
specification. ``route_url``, ``static_url``, and friends let you
refactor your URL structure, or even publish to a different root URL,
without breaking the links in your templates.

Finally, we're cheating by having mutable dummy data at module scope.
We will replace this shortly with database-driven data.

Extra Credit
============

#. Can you use ``add_static_view`` to serve up a directory listing with
   links to the contents in a directory?

#. Does Pyramid have support for setting cache parameters on static
   assets?

#. Can you also use asset specifications when naming the template for a
   view?

#. Can I provide a one-liner for including static assets in my Pyramid
   libraries?