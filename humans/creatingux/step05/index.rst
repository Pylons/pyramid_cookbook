===============================
Step 05: Making a Main Template
===============================

Making a templated UX, as we've seen, is easy to get started on.
Quickly, though, the UX designer starts to repeat things. In our
example, the "site menu" ``<ul>`` appears in each page template.

We want a "main" template with all the common stuff. Then,
each view's template simply jams the markup for that screen *into* a
spot in the main template.

ZPT has a "macros" facility for this, which we use in this step.

Goals
=====

- Productive UX development through re-use

Objectives
==========

- Move templates to their own directory

- Using ZPT macros, create a "main template" as a global layout which
  has the stuff common to all pages

- Change each view's template to grab the main template and fill in its
  slot with stuff unique to that view

Steps
=====

#. ``$ cd ../../creatingux; mkdir step05; cd step05``

#. (Unchanged) Copy the following into ``step05/application.py``:

   .. literalinclude:: application.py
      :linenos:

#. Copy the following into ``step05/views.py``:

   .. literalinclude:: views.py
      :linenos:

#. Copy the following "global template" into
   ``step05/templates/global_layout.pt``:

   .. literalinclude:: templates/global_layout.pt
      :language: html
      :linenos:

#. Copy the following into ``step05/templates/index.pt``:

   .. literalinclude:: templates/index.pt
      :language: html
      :linenos:

#. Copy the following into ``step05/templates/about.pt``:

   .. literalinclude:: templates/about.pt
      :language: html
      :linenos:

#. Copy the following into ``step05/templates/company.pt``:

   .. literalinclude:: templates/company.pt
      :language: html
      :linenos:

#. Copy the following into ``step05/templates/people.pt``:

   .. literalinclude:: templates/people.pt
      :language: html
      :linenos:

#. Copy the following into ``step05/tests.py``:

   .. literalinclude:: tests.py
      :linenos:

#. ``$ nosetests`` should report running 5 tests.

#. ``$ python application.py``

#. Open ``http://127.0.0.1:8080/`` in your browser.

Extra Credit
============

#. Do we really need to declare the XML namespaces for ``metal`` and
   ``tal``?

#. What happens if you try to fill a slot that doesn't exist?

Analysis
========

We had to add a little more ceremony to the unit tests, to get a proper
configuration.

Discussion
==========

- ZPT and macros have a very long history in Zope. Discuss the origins
  and lessons learned.
