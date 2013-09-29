=====================================
8: Authentication With Users From SQL
=====================================

- add a secret to development.ini
- __init__
- views.py
  - imports
  - set logged in user
  - login/logout views
- modify header.jinja2

Background
==========


Goals
=====



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

#. ``sqlroot/tutorial/views.py`` is almost unchanged from the
   version in the ``addcontent`` step:

   .. literalinclude:: sqlroot/tutorial/initialize_db.py
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
