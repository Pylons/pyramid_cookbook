======================================
Step 02: Basic Hierarchy for Traversal
======================================

In :doc:`../step01/index` we took the simplest possible step: a root
object with little need for the stitching-together of a tree known as
traversal.

In this step we remain simple, but make a basic hierarchy::

    /
       doc1
       doc2
       folder1/
          doc1


Goals
=====

- Multi-level nested hierarchy of Python objects

Objectives
==========

- Show how ``__name__`` and ``__parent__`` glue the hierarchy together

- Objects which last between requests

- Bring back templates

Steps
=====

#. ``$ cd ../../resources; mkdir step02; cd step02``

#. (Unchanged) Copy the following into ``step02/application.py``:

   .. literalinclude:: application.py
      :linenos:

#. Copy the following into ``step02/views.py``:

   .. literalinclude:: views.py
      :linenos:

#. Copy the following into ``step02/resources.py``:

   .. literalinclude:: resources.py
      :linenos:

#. Copy the following into ``step02/templates/default_view.pt``:

   .. literalinclude:: templates/default_view.pt
      :language: html
      :linenos:

#. Copy the following into ``step02/tests.py``:

   .. literalinclude:: tests.py
      :linenos:

#. ``$ nosetests`` should report running 2 tests.

#. ``$ python application.py``

#. Open ``http://127.0.0.1:8080/`` in your browser.

Extra Credit
============

#. In ``resources.py``, we moved the instantiation of ``root`` out to
   global scope. Why?

#. If you go to a resource that doesn't exist, will Pyramid handle it
   gracefully?

#. What happens if you use a ``__name__`` that already exists in the
   container?

Analysis
========

In this example we have to manage our tree by assigning ``__name__`` as
an identifier on each child and ``__parent__`` as a reference to the
parent.

The template used now shows different information based on the object
URL which you traversed to.

Discussion
==========

- Full discussion of how traversal and lookup works

- ``pyramid_traversaltools`` and other convenience tools (e.g.
  ``repoze.folder``)