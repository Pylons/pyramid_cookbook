========================
2: Traversal Hierarchies
========================

Objects with subobjects and views, all via URLs.

Background
==========

In :doc:`../siteroot` we took the simplest possible step: a
root object with little need for the stitching-together of a tree known
as traversal.

In this step we remain simple, but make a basic hierarchy::

    /
       doc1
       doc2
       folder1/
          doc1


Objectives
==========

- Multi-level nested hierarchy of Python objects

- Show how ``__name__`` and ``__parent__`` glue the hierarchy together

- Objects which last between requests

Steps
=====

#. We are going to use the previous step as our starting point:

   .. code-block:: bash

    (env27)$ cd ..; cp -r siteroot hierarchy; cd hierarchy
    (env27)$ python setup.py develop

#. Provide a richer set of objects in
   ``hierarchy/tutorial/resources.py``:

   .. literalinclude:: hierarchy/tutorial/resources.py
      :linenos:

#. Have ``hierarchy/tutorial/views.py`` show information about
   the resource tree:

   .. literalinclude:: hierarchy/tutorial/views.py
      :linenos:

#. Get ``hierarchy/tutorial/home.pt`` to display this richer
   information:

   .. literalinclude:: hierarchy/tutorial/home.pt
      :language: html
      :linenos:

#. Simplified tests in ``hierarchy/tutorial/tests.py``:

   .. literalinclude:: hierarchy/tutorial/tests.py
      :linenos:

#. Now run the tests:

   .. code-block:: bash


    (env27)$ nosetests tutorial
    .
    ----------------------------------------------------------------------
    Ran 4 tests in 0.141s

    OK

#. Run your Pyramid application with:

   .. code-block:: bash

    (env27)$ pserve development.ini --reload

#. Open ``http://localhost:6543/`` in your browser.

Analysis
========

In this example we have to manage our tree by assigning ``__name__`` as
an identifier on each child and ``__parent__`` as a reference to the
parent.

The template used now shows different information based on the object
URL which you traversed to.

Extra Credit
============

#. In ``resources.py``, we moved the instantiation of ``root`` out to
   global scope. Why?

#. If you go to a resource that doesn't exist, will Pyramid handle it
   gracefully?

#. What happens if you use a ``__name__`` that already exists in the
   container?
