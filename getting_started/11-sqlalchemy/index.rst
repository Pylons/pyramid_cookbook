==============================
11: Databases Using SQLAlchemy
==============================

Our Pyramid-based wiki application now needs database-backed storage of
pages. This frequently means a SQL database. The Pyramid community
strongly supports the SQLAlchemy object-relational mapper (ORM) as a
convenient, Pythonic way to interface to databases.

In this step we hook up SQLAlchemy to a SQLite database table.

Objectives
==========

- Store pages in SQLite by using SQLAlchemy models

- Use SQLAlchemy queries to list/add/view/edit/delete pages

- Provide a database-initialize command by writing a Pyramid *console
  script* which can be run from the command line

.. note::

    The ``alchemy`` scaffold is really helpful for getting a
    SQLAlchemy project going, including generation of the console
    script. Since we want to see all the decisions,
    we will forgo convenience in this tutorial and wire it up ourselves.

Steps To Initialize Database
============================

#. As before, let's use the previous package as a starting point for
   a new distribution. Also, let's install the dependencies required
   for a SQLAlchemy-oriented Pyramid application and make a directory
   for the console script:

   .. code-block:: bash

    (env33)$ cd ..; cp -r step10 step11; cd step11
    (env33)$ python3.3 setup.py develop
    (env33)$ easy_install-3.3 sqlalchemy pyramid_tm zope.sqlalchemy

#. Our configuration file at ``development.ini`` wires together some
   new pieces:

   .. literalinclude:: development.ini
    :language: ini

#. This engine configuration now needs to be read into the application
   through changes in ``tutorial/__init__.py``:

   .. literalinclude:: tutorial/__init__.py
    :linenos:

#. We need a command-line script for initializing the database. Enter
   the following to initialize ``tutorial/scripts/__init__.py``:

   .. literalinclude:: tutorial/scripts/__init__.py

#. Now enter our console script at
   ``tutorial/scripts/initializedb.py``:

   .. literalinclude:: tutorial/scripts/initializedb.py

#. To wire up this new console script, our ``setup.py`` needs an entry
   point:

   .. literalinclude:: setup.py

#. The script references some models in ``tutorial/models.py``:

   .. literalinclude:: tutorial/models.py
    :linenos:

#. Let's run this console script, thus producing our database and table:

   .. code-block:: bash

    (env33)$ initialize_tutorial_db development.ini
    2013-03-12 10:13:56,972 INFO  [sqlalchemy.engine.base.Engine][MainThread] PRAGMA table_info("wikipages")
    2013-03-12 10:13:56,972 INFO  [sqlalchemy.engine.base.Engine][MainThread] ()
    2013-03-12 10:13:56,974 INFO  [sqlalchemy.engine.base.Engine][MainThread]
    CREATE TABLE wikipages (
        id INTEGER NOT NULL,
        title TEXT,
        body TEXT,
        PRIMARY KEY (id),
        UNIQUE (title)
    )


    2013-03-12 10:13:56,974 INFO  [sqlalchemy.engine.base.Engine][MainThread] ()
    2013-03-12 10:13:56,977 INFO  [sqlalchemy.engine.base.Engine][MainThread] COMMIT
    2013-03-12 10:13:56,981 INFO  [sqlalchemy.engine.base.Engine][MainThread] BEGIN (implicit)
    2013-03-12 10:13:56,983 INFO  [sqlalchemy.engine.base.Engine][MainThread] INSERT INTO wikipages (title, body) VALUES (?, ?)
    2013-03-12 10:13:56,983 INFO  [sqlalchemy.engine.base.Engine][MainThread] ('Root', '<p>Root</p>')
    2013-03-12 10:13:56,985 INFO  [sqlalchemy.engine.base.Engine][MainThread] COMMIT

    (env33)$ ls sqltutorial.sqlite
    sqltutorial.sqlite

Application Steps
=================

#. With our data now driven by SQLAlchemy queries,
   we need to update our ``tutorial/views.py``:

   .. literalinclude:: tutorial/views.py

#. The introduction of a relational database means significant changes
   in our ``tutorial/tests.py``:

   .. literalinclude:: tutorial/tests.py

#. Run the tests in your package using ``nose``:

   .. code-block:: bash

    (env33)$ nosetests .
    ..
    -----------------------------------------------------------------
    Ran 2 tests in 1.971s

    OK

#. Run the WSGI application:

   .. code-block:: bash

    (env33)$ pserve development.ini --reload

#. Open ``http://127.0.0.1:6547/`` in your browser.

Analysis
========


Extra Credit
============

