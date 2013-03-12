==============================
11: Databases Using SQLAlchemy
==============================



Objectives
==========

- Store pages in SQLite by using SQLAlchemy models

- Provide a database-initialize command by writing a Pyramid *console
  script* which can be run from the command line

.. note::

    The ``alchemy`` scaffold is really helpful for getting a
    SQLAlchemy project going, including generation of the console
    script. Since we want to see all the decisions,
    we will forgo convenience in this tutorial and wire it up ourselves.

Initializing the Database
=========================

Steps
=====

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

#. We need a command-line script for initializing the database. Enter
   the following to initialize ``tutorial/scripts/__init__.py``:

   .. literalinclude:: tutorial/scripts/__init__.py

#. Now enter our console script at
   ``tutorial/scripts/initializedb.py``:

   .. literalinclude:: tutorial/scripts/initializedb.py

#. To wire up a console script, our ``setup.py`` needs an entry point:

   .. literalinclude:: setup.py



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

