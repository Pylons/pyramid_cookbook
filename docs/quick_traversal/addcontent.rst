==================================
5: Adding Resources To Hierarchies
==================================

Multiple views per type allowing addition of content anywhere in a resource
tree.

Background
==========

We now have multiple kinds of things, but only one view per resource type. We
need the ability to add things to containers, then view and edit resources.

We will use the previously mentioned concept of named views. A name is a part
of the URL that appears after the resource identifier. For example:

.. code-block:: python

  @view_config(context=Folder, name='add_document')

...means that this URL::

  http://localhost:6543/some_folder/add_document

...will match the view being configured. It's as if you have an object-oriented
web with operations on resources represented by a URL.

Goals
=====

- Allow adding and editing content in a resource tree.

- Create a simple form which POSTs data.

- Create a view which takes the POST data, creates a resource, and redirects to
  the newly-added resource.

- Create per-type named views.

Steps
=====

#. We are going to use the previous step as our starting point:

   .. code-block:: bash

    $ cd ..; cp -r typeviews addcontent; cd addcontent
    $ $VENV/bin/python setup.py develop


#. Our views in ``addcontent/tutorial/views.py`` need type-specific
   registrations:

   .. literalinclude:: addcontent/tutorial/views.py
      :linenos:
      :emphasize-lines: 1-3,14,32-54

#. Make a re-usable snippet in ``addcontent/tutorial/templates/addform.jinja2``
   for adding content:

   .. literalinclude:: addcontent/tutorial/templates/addform.jinja2
      :language: jinja
      :linenos:

#. Add this snippet to ``addcontent/tutorial/templates/root.jinja2``:

   .. literalinclude:: addcontent/tutorial/templates/root.jinja2
      :language: jinja
      :linenos:
      :emphasize-lines: 8-9

#. Forms are needed in ``addcontent/tutorial/templates/folder.jinja2``:

   .. literalinclude:: addcontent/tutorial/templates/folder.jinja2
      :language: jinja
      :linenos:
      :emphasize-lines: 7-8

#. ``$ $VENV/bin/nosetests`` should report running 4 tests.

#. Run your Pyramid application with:

   .. code-block:: bash

    $ $VENV/bin/pserve development.ini --reload

#. Open http://localhost:6543/ in your browser.

Analysis
========

Our views now represent a richer system, where form data can be processed to
modify content in the tree. We do this by attaching named views to resource
types, giving them a natural system for object-oriented operations.

To mimic uniqueness, we randomly choose a satisfactorily large number. For true
uniqueness, we would also need to check that the number does not already exist
at the same level of the resource tree.

We'll start to address a couple of issues brought up in the Extra Credit below
in the next step of this tutorial, :doc:`zodb`.

Extra Credit
============

1. What happens if you add folders and documents, then restart your app?

2. What happens if you remove the pseudo-random, pseudo-unique naming
   convention and replace it with a fixed value?
