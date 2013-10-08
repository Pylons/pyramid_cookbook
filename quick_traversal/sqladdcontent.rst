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


#. ``sqladdcontent/tutorial/models.py`` gains a ``Node`` parent class
   and two more models (``Folder`` and ``Document``):

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
