================
Step 07: Layouts
================

In :doc:`../step05/index` we talked about a main template. Great idea
which makes a big impact on UX productivity.

However, a little bit more is needed. The main template usually needs data
and methods to fill in some of its blocks (e.g. the ``site_menu``).
With our view classes approach, the class properties we used as the
"Template API" were co-mingled with view-specific properties.

Sure would be nice to have a discrete, standalone place to find the
template *and* the template API, apart from each view.

For this tutorial we are inventing the idea of a *Layout*,
which is exactly that combination: one (or more) templates and the
logic those templates need.

Goals
=====

- Help UX developers keep global stuff apart from the specific stuff

- Decrease test writing

- Support multiple look and feels in a site

Objectives
==========

- Make an abstract base class (no ``__init__``) in a ``layouts.py``
  module

- Each supported main template is its own property on that ``Layouts``
  class

- View classes then subclass from the project's ``Layouts`` class

- Split the ``tests.py`` into unit and functional tests for the views,
  and unit tests for the ``Layouts`` module

Steps
=====

#. ``$ cd ../../creatingux; mkdir step07; cd step07``

#. (Unchanged) Copy the following into ``step07/application.py``:

   .. literalinclude:: application.py
      :linenos:

#. Copy the following into ``step07/views.py``:

   .. literalinclude:: views.py
      :linenos:

#. Copy the following into ``step07/layouts.py``:

   .. literalinclude:: layouts.py
      :linenos:

#. Copy the following into ``step07/dummy_data.py``:

   .. literalinclude:: dummy_data.py
      :linenos:

#. Copy the following "global template" into
   ``step07/templates/global_layout.pt``:

   .. literalinclude:: templates/global_layout.pt
      :language: html
      :linenos:

#. Copy the following into ``step07/templates/index.pt``:

   .. literalinclude:: templates/index.pt
      :language: html
      :linenos:

#. Copy the following into ``step07/templates/about.pt``:

   .. literalinclude:: templates/about.pt
      :language: html
      :linenos:

#. Copy the following into ``step07/templates/company.pt``:

   .. literalinclude:: templates/company.pt
      :language: html
      :linenos:

#. Copy the following into ``step07/templates/people.pt``:

   .. literalinclude:: templates/people.pt
      :language: html
      :linenos:

#. Copy the following into ``step07/test_views.py``:

   .. literalinclude:: test_views.py
      :linenos:

#. Copy the following into ``step07/test_layout.py``:

   .. literalinclude:: test_layout.py
      :linenos:

#. ``$ nosetests`` should report running 8 tests.

#. ``$ python application.py``

#. Open ``http://127.0.0.1:8080/`` in your browser.

Extra Credit
============

#. How might we support multiple layouts? Give it a try.

Analysis
========

One might start thinking that layouts shouldn't be hardwired. You
should be able to make a layout (template and template API) and
register it. Views could then grab the one they want,
perhaps from a dictionary. Perhaps even support theme switching. Such
pluggability is an *anti-goal*. Custom UX projects should specifically
make and name what they create.

Discussion
==========

- Is such a pattern really needed?

- What are some other, previous "Template API" ideas?

- Would a UX developer want to know that a property came from the
  layout instead of the view?

- How does this relate to the idea of a "theme"?
