=============================
Step 09: AJAX With JSON Views
=============================

Modern web development means AJAX. Through its renderer support,
Pyramid makes return JSON data from a view very easy and coherent with
the rest of the Pyramid architecture.

In this step we add a box to ach screen which fetches, format,
and re-fetches site news updates.

.. note::

   Our templates will include jQuery from the Google CDN.

Goals
=====

- Show Pyramid's support for AJAX

Objectives
==========

- Learn about the ``json`` renderer

- Add a test for the JSON response

- Include into the main template

Steps
=====

#. ``$ cd ../../creatingux; mkdir step09; cd step09``

#. Copy the following into ``step09/application.py``:

   .. literalinclude:: application.py
      :linenos:

#. ``$ mkdir static``

#. Copy the following into ``step09/static/global_layout.css``:

   .. literalinclude:: static/global_layout.css
      :language: css
      :linenos:

#. Copy the following into ``step09/static/global_layout.js``:

   .. literalinclude:: static/global_layout.js
      :language: js
      :linenos:

#. Copy the following into ``step09/views.py``:

   .. literalinclude:: views.py
      :linenos:

#. Copy the following into ``step09/layouts.py``:

   .. literalinclude:: layouts.py
      :linenos:

#. Copy the following into ``step09/dummy_data.py``:

   .. literalinclude:: dummy_data.py
      :linenos:

#. Copy the following "global template" into
   ``step09/templates/global_layout.pt``:

   .. literalinclude:: templates/global_layout.pt
      :language: html
      :linenos:

#. Copy the following into ``step09/templates/index.pt``:

   .. literalinclude:: templates/index.pt
      :language: html
      :linenos:

#. Copy the following into ``step09/templates/about.pt``:

   .. literalinclude:: templates/about.pt
      :language: html
      :linenos:

#. Copy the following into ``step09/templates/company.pt``:

   .. literalinclude:: templates/company.pt
      :language: html
      :linenos:

#. Copy the following into ``step09/templates/people.pt``:

   .. literalinclude:: templates/people.pt
      :language: html
      :linenos:

#. Copy the following into ``step09/test_views.py``:

   .. literalinclude:: test_views.py
      :linenos:

#. Copy the following into ``step09/test_layout.py``:

   .. literalinclude:: test_layout.py
      :linenos:

#. ``$ nosetests`` should report running 9 tests.

#. ``$ python application.py``

#. Open ``http://127.0.0.1:8080/`` in your browser.

Extra Credit
============

#. Rather than a static random dictionary, make a mutable global that
   gets appended to on each request, showing the time. Each request
   adds another item to the list.

#. Can WebTest provide any functional testing for AJAX?

Analysis
========

The JSON view is pretty fun. It looks very similar to our other views,
which is good. In fact, the whole pattern of simply returning data from
your view, and letting the machinery pass it into a renderer,
provides consistency and simplicity. Plus, tests are a lot easier to
write.

Discussion
==========

- How do other systems (Zope2, Zope3, Plone, Django,
  Pylons 1) approach this?
