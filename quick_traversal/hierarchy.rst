========================
3: Traversal Hierarchies
========================

Objects with subobjects and views, all via URLs.

Background
==========

In :doc:`siteroot` we took the simplest possible step: a root object with
little need for the stitching together of a tree known as traversal.

In this step we remain simple, but make a basic hierarchy::

    /
       doc1
       doc2
       folder1/
          doc1


Objectives
==========

- Use a multi-level nested hierarchy of Python objects.

- Show how ``__name__`` and ``__parent__`` glue the hierarchy together.

- Use objects which last between requests.

Steps
=====

#. We are going to use the previous step as our starting point:

   .. code-block:: bash

    $ cd ..; cp -r siteroot hierarchy; cd hierarchy
    $ $VENV/bin/python setup.py develop

#. Provide a richer set of objects in ``hierarchy/tutorial/resources.py``:

   .. literalinclude:: hierarchy/tutorial/resources.py
      :linenos:

#. Have ``hierarchy/tutorial/views.py`` show information about the resource
   tree:

   .. literalinclude:: hierarchy/tutorial/views.py
      :linenos:
      :emphasize-lines: 1,9

#. Update the ``hierarchy/tutorial/templates/home.jinja2`` view template:

   .. literalinclude:: hierarchy/tutorial/templates/home.jinja2
      :language: jinja
      :linenos:
      :emphasize-lines: 4-12

#. The ``hierarchy/tutorial/templates/breadcrumbs.jinja2`` template now has a
   hierarchy to show:

   .. literalinclude:: hierarchy/tutorial/templates/breadcrumbs.jinja2
      :language: jinja
      :linenos:

#. Update the tests in ``hierarchy/tutorial/tests.py``:

   .. literalinclude:: hierarchy/tutorial/tests.py
      :linenos:
      :emphasize-lines: 8,13,26-28

#. Now run the tests:

   .. code-block:: bash


    $ $VENV/bin/nosetests tutorial
    ..
    ----------------------------------------------------------------------
    Ran 2 tests in 0.141s

    OK

#. Run your Pyramid application with:

   .. code-block:: bash

    $ $VENV/bin/pserve development.ini --reload

#. Open http://localhost:6543/ in your browser.

Analysis
========

In this example we have to manage our tree by assigning ``__name__`` as an
identifier on each child, and ``__parent__`` as a reference to the parent. The
template used now shows different information based on the object URL to which
you traversed.

We also show that ``@view_config`` can set a "default" view on a context by
omitting the ``@name`` attribute. Thus, if you visit
``http://localhost:6543/folder1/`` without providing anything after, the
configured default view is used.

Extra Credit
============

#. In ``resources.py``, we moved the instantiation of ``root`` out to global
   scope. Why?

#. If you go to a resource that doesn't exist, will Pyramid handle it
   gracefully?

#. If you ask for a default view on a resource and none is configured, will
   Pyramid handle it gracefully?
