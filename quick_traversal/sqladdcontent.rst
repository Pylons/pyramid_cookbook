===================================
8: SQL Traversal and Adding Content
===================================

Traverse through a resource tree of data stored in an RDBMS,
adding folders and documents at any point.

Background
==========

We now have SQLAlchemy providing us a persistent root. How do we
arrange an infinitely-nested URL space where URL segments point to
instances of our classes, nested inside of other instances?

SQLAlchemy, as mentioned previously, uses the adjacency list
relationship to allow self-joining in a table. This allows a resource
to store the identifier of its parent. With this we can make a generic
"Node" model in SQLAlchemy which holds the parts needed by Pyramid's
traversal.

In a nutshell, we are giving RDBMS data Python dictionary behavior,
using built-in SQLAlchemy relationships. This lets us define our own
kinds of containers and own kinds of types, nested in any way we like.

Goals
=====

- Recreate the :doc:`addcontent` and :doc:`zodb` steps, where you can
  add folders inside folders

- Extend traversal/dictionary behavior to SQLAlchemy models


Steps
=====

#. We are going to use the previous step as our starting point:

   .. code-block:: bash

    $ cd ..; cp -r sqlroot sqladdcontent; cd sqladdcontent
    $ $VENV/bin/python setup.py develop


#. Make a Python module for a generic ``Node`` base class that gives us
   traversal-y behavior in ``sqladdcontent/tutorial/sqltraversal.py``:

   .. literalinclude:: sqladdcontent/tutorial/sqltraversal.py
      :linenos:

#. ``sqladdcontent/tutorial/models.py`` is very simple,
   with the heavy lifting moved to the common module:

   .. literalinclude:: sqladdcontent/tutorial/models.py
      :linenos:

#. Our ``sqladdcontent/tutorial/views.py`` is almost unchanged from the
   version in the ``addcontent`` step:

   .. literalinclude:: sqladdcontent/tutorial/views.py
      :linenos:

#. Our templates are all unchanged from addcontent. Let's bring them
   back. Make a re-usable snippet in
   ``sqladdcontent/tutorial/templates/addform.jinja2`` for adding content:

   .. literalinclude:: sqladdcontent/tutorial/templates/addform.jinja2
      :language: html
      :linenos:

#. Need this snippet added to
   ``sqladdcontent/tutorial/templates/root.jinja2``:

   .. literalinclude:: sqladdcontent/tutorial/templates/root.jinja2
      :language: html
      :linenos:

#. Need a view template for ``folder`` at
   ``sqladdcontent/tutorial/templates/folder.jinja2``:

   .. literalinclude:: sqladdcontent/tutorial/templates/folder.jinja2
      :language: html
      :linenos:

#. Also need a view template for ``document`` at
   ``sqladdcontent/tutorial/templates/document.jinja2``:

   .. literalinclude:: sqladdcontent/tutorial/templates/document.jinja2
      :language: html
      :linenos:


#. Run your Pyramid application with:

   .. code-block:: bash

    $ $VENV/bin/pserve development.ini --reload

#. Open ``http://localhost:6543/`` in your browser.

Analysis
========

If we consider our views and templates as the bulk of our business
logic when handling web interactions, then this was an intriguing step.
We had no changes to our templates from the ``addcontent`` and
``zodb`` steps, and almost no change to the views. We made a one-line
change when creating a new object. We also had to "stack" an extra
``@view_config`` (although that can be solved in other ways.)

We gained a resource tree that gave us hierarchies. And for the most
part, these are already full-fledged "resources" in Pyramid:

- Traverse through a tree and match a view on a content type

- Know how to get to the parents of any resource (even if outside the
  current URL)

- All the traversal-oriented view predicates apply

- Ability to generate full URLs for any resource in the system

Even better, the data for the resource tree is stored in a table
separate from the core business data. Equally, the ORM code for moving
through the tree is in a separate module. You can stare at the data and
the code for your business objects and ignore the the Pyramid part.

This is most useful for projects starting with a blank slate,
with no existing data or schemas they have to adhere to. Retrofitting a
tree on non-tree data is possible, but harder.
