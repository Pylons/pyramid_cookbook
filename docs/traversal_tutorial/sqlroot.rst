=======================
7: RDBMS Root Factories
=======================

Using SQLAlchemy to provide a persistent root resource via a resource factory.

Background
==========

In :doc:`zodb` we used a Python object database, the ZODB, for storing our
resource tree information. The ZODB is quite helpful at keeping a graph
structure that we can use for traversal's "location awareness".

Relational databases, though, aren't hierarchical. We can, however, use
SQLAlchemy's `adjacency list relationship
<http://docs.sqlalchemy.org/en/latest/orm/relationships.html#adjacency-list-relationships>`_
to provide a tree-like structure. We will do this in the next two steps.

In the first step, we get the basics in place: SQLAlchemy, a SQLite table,
transaction-awareness, and a root factory that gives us a context. We will use
:doc:`siteroot` as a starting point.

.. note::

  This step presumes you are familiar with the material in
  :ref:`pyramid:qtut_databases`.

.. note::

  Traversal's usage of SQLAlchemy's adjacency list relationship and polymorphic
  table inheritance came from `Kotti <https://pypi.python.org/pypi/Kotti>`_, a
  Pyramid-based CMS inspired by Plone. Daniel Nouri has advanced the ideas of
  first-class traversal in SQL databases with a variety of techniques and
  ideas. Kotti is certainly the place to look for the most modern approach to
  traversal hierarchies in SQL.

Goals
=====

- Introduce SQLAlchemy and SQLite into the project, including transaction
  awareness.

- Provide a root object that is stored in the RDBMS and use that as our
  context.

Steps
=====

#. We are going to use the siteroot step as our starting point:

   .. code-block:: bash

    $ cd ..; cp -r siteroot sqlroot; cd sqlroot

#. Introduce some new dependencies and a console script in
   ``sqlroot/setup.py``:

   .. literalinclude:: sqlroot/setup.py
      :linenos:
      :emphasize-lines: 6-8,17-18

#. Now we can initialize our project:

   .. code-block:: bash

    $ $VENV/bin/python setup.py develop

#. Our configuration file at ``sqlroot/development.ini`` wires together some
   new pieces:

   .. literalinclude:: sqlroot/development.ini
      :language: ini
      :emphasize-lines: 6-7,17,24-28

#. The ``setup.py`` has an entry point for a console script at
   ``sqlroot/tutorial/initialize_db.py``, so let's add that script:

   .. literalinclude:: sqlroot/tutorial/initialize_db.py
      :linenos:

#. Our startup code in ``sqlroot/tutorial/__init__.py`` gets
   some bootstrapping changes:

   .. literalinclude:: sqlroot/tutorial/__init__.py
      :linenos:
      :emphasize-lines: 3-9,13-16,18

#. Create ``sqlroot/tutorial/models.py`` with our SQLAlchemy model for our
   persistent root:

   .. literalinclude:: sqlroot/tutorial/models.py
      :linenos:

#. Let's run this console script, thus producing our database and table:

   .. code-block:: bash

    $ $VENV/bin/initialize_tutorial_db development.ini
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

#. Open http://localhost:6543/ in your browser.

Analysis
========

We perform the same kind of SQLAlchemy setup work that we saw in
:ref:`pyramid:qtut_databases`. In this case, our root factory returns an object
from the database.

This ``models.Root`` instance is the ``context`` for our views and templates.
Rather than have our view and template code query the database, our root
factory gets the top and Pyramid does the rest by passing in a ``context``.

This point is illustrated by the fact that we didn't have to change our view
logic or our templates. They depended on a context. Pyramid found the context
and passed it into our views.

Extra Credit
============

#. What will Pyramid do if the database doesn't have a ``Root`` that matches
   the SQLAlchemy query?
