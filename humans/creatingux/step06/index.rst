=====================
Step 06: View Classes
=====================

Free-standing functions are the regular way to do views. Many times,
though, you have several views that are closely related. For example,
a content type might have many different ways to look at it.

For some people, grouping these together makes logical sense. A view
class lets you group views, sharing some state assignments and helper
functions as class methods.

Even better, from a UX person's perspective, the methods on the view
class look like a "Template API" from the inside the namespace of the
view.

Goals
=====

- Explain the *why* as well as the what on view classes

- Show how templates interact with the app via the view class

Objectives
==========

- Move templates to their own directory

- Understand the structure of a view class's ``__init__`` and methods

- See how the ``@reify`` decorator can form a "Template API"

- Adapt template expressions to point through the view

- Change tests to instantiate the view class then call it

- Move the repetitive dummy data into its own module

Steps
=====

#. ``$ cd ../../creatingux; mkdir step06; cd step06``

#. (Unchanged) Copy the following into ``step06/application.py``:

   .. literalinclude:: application.py
      :linenos:

#. Copy the following into ``step06/views.py``:

   .. literalinclude:: views.py
      :linenos:

#. Copy the following into ``step06/dummy_data.py``:

   .. literalinclude:: dummy_data.py
      :linenos:

#. Copy the following "global template" into
   ``step06/templates/global_layout.pt``:

   .. literalinclude:: templates/global_layout.pt
      :language: html
      :linenos:

#. Copy the following into ``step06/templates/index.pt``:

   .. literalinclude:: templates/index.pt
      :language: html
      :linenos:

#. Copy the following into ``step06/templates/about.pt``:

   .. literalinclude:: templates/about.pt
      :language: html
      :linenos:

#. Copy the following into ``step06/templates/company.pt``:

   .. literalinclude:: templates/company.pt
      :language: html
      :linenos:

#. Copy the following into ``step06/templates/people.pt``:

   .. literalinclude:: templates/people.pt
      :language: html
      :linenos:

#. Copy the following into ``step06/tests.py``:

   .. literalinclude:: tests.py
      :linenos:

#. ``$ nosetests`` should report running 5 tests.

#. ``$ python application.py``

#. Open ``http://127.0.0.1:8080/`` in your browser.

Extra Credit
============

#. Why do some ZPT expressions need ``view.`` and some don't?

#. What exactly does ``@reify`` do?

#. Could you shorten your unit tests by making a ``DummyRequest
   ()`` in the test's ``__init__``?

#. If you do an expensive calculation for one view,
   does that increase performance in another view that doesn't need to
   recalculate it?

#. Where does ``@reify`` store the cached value?

Analysis
========

The idea of a view class can be used to form different patterns. In
this case, we want a unit of related work, join up the views for that
work, and craft our own little API that our templates use.

The test writing gets a little bit harder.

Discussion
==========

- What was the original need that spawned view classes?

- How do other system approach the idea?

- What is a "push page" and what need was it addressing?
