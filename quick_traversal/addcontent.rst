==================================
5: Adding Resources To Hierarchies
==================================

Multiple views per type allowing addition of content anywhere in a
resource tree.

Background
==========

We now have multiple kinds-of-things, but only one view per resource
type. We need the ability to add things to containers,
then view/edit resources.

We will use the previously-mentioned concept of named views. A name is a
part of the URL that appears after the resource identifier. For example::

  @view_config(context=Folder, name='add_document')

...means that this URL::

  http://localhost:6543/some_folder/add_document

...will match the view being configured. It's as if you have an
object-oriented web, with operations on resources represented by a URL.

Goals
=====

- Adding and editing content in a resource tree

- Simple form which POSTs data

- A view which takes the POST data, creates a resource, and redirects
  to the newly-added resource

- Per-type named views

Steps
=====

#. We are going to use the previous step as our starting point:

   .. code-block:: bash

    $ cd ..; cp -r typeviews addcontent; cd addcontent
    $ $VENV/bin/python setup.py develop


#. Our views in ``addcontent/tutorial/views.py`` need
   type-specific registrations:

   .. literalinclude:: addcontent/tutorial/views.py
      :linenos:

#. Make a re-usable snippet in
   ``addcontent/tutorial/templates/addform.jinja2`` for adding content:

   .. literalinclude:: addcontent/tutorial/templates/addform.jinja2
      :language: html
      :linenos:

#. Need this snippet added to
   ``addcontent/tutorial/templates/root.jinja2``:

   .. literalinclude:: addcontent/tutorial/templates/root.jinja2
      :language: html
      :linenos:

#. Forms also needed for
   ``addcontent/tutorial/templates/folder.jinja2``:

   .. literalinclude:: addcontent/tutorial/templates/folder.jinja2
      :language: html
      :linenos:

#. ``$ $VENV/bin/nosetests`` should report running 4 tests.

#. Run your Pyramid application with:

   .. code-block:: bash

    $ $VENV/bin/pserve development.ini --reload

#. Open ``http://localhost:6543/`` in your browser.

Analysis
========

Our views now represent a richer system, where form data can be
processed to modify content in the tree. We do this by attaching named
views to resource types, giving them a natural system for
object-oriented operations.

To enforce uniqueness, we randomly choose a satisfactorily large number.