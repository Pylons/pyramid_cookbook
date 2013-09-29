===================================
7: SQL Traversal and Adding Content
===================================

- Only changes in views
  - add_folder and add_document
    - Stacked another view_config
    - One-line change on adding content

Traverse through a resource tree of data stored in an RDBMS,
adding folders and documents at any point.

Background
==========



Goals
=====

- Introduce SQLAlchemy and SQLite into the project, including
  transaction awareness

- Provide a root object that is stored in the RDBMS and use that as
  our context

Steps
=====

#. We are going to use the siteroot step as our starting point:

   .. code-block:: bash

    $ cd ..; cp -r siteroot sqlroot; cd sqlroot

#. Introduce some new dependencies and a console script in
   ``sqlroot/setup.py``:

   .. literalinclude:: sqlroot/setup.py
      :linenos:

#. Now we can initialize our project:

   .. code-block:: bash

    $ $VENV/bin/python setup.py develop

#. Our configuration file at ``sqlroot/development.ini`` wires
   together some new pieces:

   .. literalinclude:: sqlroot/development.ini
    :language: ini

#. The ``setup.py`` had an entry point for a console script at
   ``sqlroot/tutorial/initialize_db.py`` gets
   some bootstrapping changes:

   .. literalinclude:: sqlroot/tutorial/initialize_db.py
      :linenos:

#. Our startup code in ``sqlroot/tutorial/__init__.py`` gets
   some bootstrapping changes:

   .. literalinclude:: sqlroot/tutorial/__init__.py
      :linenos:

#. Create ``sqlroot/tutorial/models.py`` with our SQLAlchemy
   model for our persistent root:

   .. literalinclude:: sqlroot/tutorial/models.py
      :linenos:

#. Let's run this console script, thus producing our database and table:

   .. code-block:: bash

    $ initialize_tutorial_db development.ini
    2013-09-29 15:42:23,564 INFO  [sqlalchemy.engine.base.Engine][MainThread] PRAGMA table_info("root")
    2013-09-29 15:42:23,565 INFO  [sqlalchemy.engine.base.Engine][MainThread] ()
    2013-09-29 15:42:23,566 INFO  [sqlalchemy.engine.base.Engine][MainThread]
    CREATE TABLE root (
        uid INTEGER NOT NULL,
        title TEXT,
        PRIMARY KEY (uid),
        UNIQUE (title)
    )


    2013-09-29 15:42:23,566 INFO  [sqlalchemy.engine.base.Engine][MainThread] ()
    2013-09-29 15:42:23,569 INFO  [sqlalchemy.engine.base.Engine][MainThread] COMMIT
    2013-09-29 15:42:23,572 INFO  [sqlalchemy.engine.base.Engine][MainThread] BEGIN (implicit)
    2013-09-29 15:42:23,573 INFO  [sqlalchemy.engine.base.Engine][MainThread] INSERT INTO root (title) VALUES (?)
    2013-09-29 15:42:23,573 INFO  [sqlalchemy.engine.base.Engine][MainThread] ('My SQLAlchemy Root',)
    2013-09-29 15:42:23,576 INFO  [sqlalchemy.engine.base.Engine][MainThread] COMMIT

#. Nothing changes in our views or templates.

#. Run your Pyramid application with:

   .. code-block:: bash

    $ $VENV/bin/pserve development.ini --reload

#. Open ``http://localhost:6543/`` in your browser.

Analysis
========

We perform the same kind of SQLAlchemy setup work that we saw in
:ref:`Databases Using SQLAlchemy <pyramid:qtut_databases>`. In this
case, our root factory returns an object from the database.

This ``models.Root`` instance is the ``context`` for our views and
templates. Rather than have our view/template code query the database,
our root factory gets the top and Pyramid does the rest by passing in a
``context``.

This point is emphasized by the fact that we didn't have to change our
view logic or our templates. They depended on a context. Pyramid found
the context and passed it into our views.

Extra Credit
============

#. What will Pyramid do if the database doesn't have a ``Root`` that
   matches the SQLAlchemy query?
