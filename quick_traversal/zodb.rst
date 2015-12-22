============================
6: Storing Resources In ZODB
============================

Store and retrieve resource tree containers and items in a database.

Background
==========

We now have a resource tree that can go infinitely deep, adding items and
subcontainers along the way. We obviously need a database, one that can support
hierarchies. ZODB is a transaction-based Python database that supports
transparent persistence. We will modify our application to work with the ZODB.

Along the way we will add the use of ``pyramid_tm``, a system for adding
transaction awareness to our code. With this we don't need to manually manage
our transaction begin/commit cycles in our application code. Instead,
transactions are setup transparently on request/response boundaries, outside
our application code.

Objectives
==========

- Create a CRUD app that adds records to persistent storage.

- Setup ``pyramid_tm`` and ``pyramid_zodbconn``.

- Make our "content" classes inherit from ``Persistent``.

- Set up a database connection string in our application.

- Set up a root factory that serves the root from ZODB rather than from memory.

Steps
=====

#. We are going to use the previous step as our starting point:

   .. code-block:: bash

    $ cd ..; cp -r addcontent zodb; cd zodb

#. Introduce some new dependencies in  ``zodb/setup.py``:

   .. literalinclude:: zodb/setup.py
      :linenos:
      :emphasize-lines: 6-8

#. We can now install our project:

   .. code-block:: bash

    $ $VENV/bin/python setup.py develop

#. Modify our ``zodb/development.ini`` to include some configuration and give
   database connection parameters:

   .. literalinclude:: zodb/development.ini
      :language: ini
      :linenos:
      :emphasize-lines: 6-8

#. Our startup code in ``zodb/tutorial/__init__.py`` gets some bootstrapping
   changes:

   .. literalinclude:: zodb/tutorial/__init__.py
      :linenos:
      :emphasize-lines: 2,7-10,13

#. Our views in ``zodb/tutorial/views.py`` have modest changes in
   ``add_folder`` and ``add_content`` for how new instances are made and put
   into a container:

   .. literalinclude:: zodb/tutorial/views.py
      :linenos:
      :emphasize-lines: 37-39,51-53

#. Make our resources persistent in ``zodb/tutorial/resources.py``:

   .. literalinclude:: zodb/tutorial/resources.py
      :linenos:
      :emphasize-lines: 1-8,13-19,23-

#. No changes to any templates!

#. Run your Pyramid application with:

   .. code-block:: bash

    $ $VENV/bin/pserve development.ini --reload

#. Open http://localhost:6543/ in your browser.

Analysis
========

We install ``pyramid_zodbconn`` to handle database connections to ZODB. This
pulls the ZODB3 package as well.

To enable ``pyramid_zodbconn``:

- We activate the package configuration using ``pyramid.includes``.

- We define a ``zodbconn.uri`` setting with the path to the Data.fs file.

In the root factory, instead of using our old root object, we now get a
connection to the ZODB and create the object using that.

Our resources need a couple of small changes. Folders now inherit from
``persistent.PersistentMapping`` and document from ``persistent.Persistent``.
Note that ``Folder`` now needs to call ``super()`` on the ``__init__`` method,
or the mapping will not initialize properly.

On the bootstrap, note the use of ``transaction.commit()`` to commit the
change. This is because on first startup, we want a root resource in place
before continuing.

ZODB has many modes of deployment. For example, ZEO is a pure-Python object
storage service across multiple processes and hosts. RelStorage lets you use a
RDBMS for storage/retrieval of your Python pickles.

Extra Credit
============

#. Create a view that deletes a document.

#. Remove the configuration line that includes ``pyramid_tm``.  What happens
   when you restart the application?  Are your changes persisted across
   restarts?

#. What happens if you delete the files named ``Data.fs*``?
