======================================
Step 08: CSS and JS With Static Assets
======================================

Web applications include many static assets in the UX: CSS and JS
files, images, etc. Web frameworks need to support productive
development by the UX team, but also the richness and complexity
required by the core developers and the deployment team.

It's a surprisingly hard problem, supporting all these needs while
keeping the simple case easy.

Pyramid accomplishes this using the view machinery and static assets.

Goals
=====

- Show Pyramid's support for static assets

Objectives
==========

- Add a static view to Pyramid's ``Configurator``

- Change the main template to includes the CSS and JS

- Change the templates to have a nicer layout

Steps
=====

#. ``$ cd ../../creatingux; mkdir step08; cd step08``

#. Copy the following into ``step08/application.py``:

   .. literalinclude:: application.py
      :linenos:

#. ``$ mkdir static``

#. Copy the following into ``step08/static/global_layout.css``:

   .. literalinclude:: static/global_layout.css
      :language: css
      :linenos:

#. Copy the following into ``step08/views.py``:

   .. literalinclude:: views.py
      :linenos:

#. Copy the following into ``step08/layouts.py``:

   .. literalinclude:: layouts.py
      :linenos:

#. Copy the following into ``step08/dummy_data.py``:

   .. literalinclude:: dummy_data.py
      :linenos:

#. Copy the following "global template" into
   ``step08/templates/global_layout.pt``:

   .. literalinclude:: templates/global_layout.pt
      :language: html
      :linenos:

#. Copy the following into ``step08/templates/index.pt``:

   .. literalinclude:: templates/index.pt
      :language: html
      :linenos:

#. Copy the following into ``step08/templates/about.pt``:

   .. literalinclude:: templates/about.pt
      :language: html
      :linenos:

#. Copy the following into ``step08/templates/company.pt``:

   .. literalinclude:: templates/company.pt
      :language: html
      :linenos:

#. Copy the following into ``step08/templates/people.pt``:

   .. literalinclude:: templates/people.pt
      :language: html
      :linenos:

#. Copy the following into ``step08/test_views.py``:

   .. literalinclude:: test_views.py
      :linenos:

#. Copy the following into ``step08/test_layout.py``:

   .. literalinclude:: test_layout.py
      :linenos:

#. ``$ nosetests`` should report running 8 tests.

#. ``$ python application.py``

#. Open ``http://127.0.0.1:8080/`` in your browser.

Analysis
========

Being able to point your Pyramid app at an entire directory and publish
it is a boon for quick development. We grabbed the ``configurator``
and, with one line, published a directory of assets. No need to
individually publish each file and set mime-type.

Setting expires headers is a fiddly part of the development cycle.

Extra Credit
============

#. Make a static file of JSON data in the ``static`` directory,
   then write a jQuery AJAX function that fetches it and shoves in a
   ``<ul>``.

#. Learn about ZPT's ``fill-slot`` to allow each view's template to
   include some custom CSS into the ``<head>``.

#. Will Pyramid recurse sub-directories? Can you get a directory
   listing of files in a static directory?

Analysis
========

Not much to cover. We have a config method that lets us jam in a new
part of the URL space, serving up static files.

Discussion
==========

- What does ``add_static_view`` do under the hood?

- What are some of the weird cases for deeper development (e.g.
  multi-site roots) and deployment (e.g. far-future expires)?

- Pyramid's extra support for, in Python code, resolving the URL path
  to directories that were "mounted" in configuration

- How this does or doesn't map to ZCML
