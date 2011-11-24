===========================
Storing content in the ZODB
===========================

Goals
=====

- Create a CRUD app that adds records to persistent storage.

.. warning::

  Caveat: this will likely only work on systems that have C compilation tools
  installed (XCode, Linux) *or* on Windows systems.  If you can't get ZODB
  installed properly you may need to pair up with someone who can.

Objectives
==========

- Install ``deform``.

- Install and include ``pyramid_tm``.

- Install and include ``pyramid_zodbconn``.

- Make our "content" classes inherit from ``Persistent``.

- Set up a database connection string in our application.

- Set up a root factory that serves the root from ZODB rather than from
  memory.

Steps
=====

#. ``easy_install pyramid_zodbconn pyramid_tm deform``.

#. ``mkdir zodb``

#. Copy the following into ``zodb/application.py``:

   .. literalinclude:: application.py
      :linenos:

#. Copy the following into ``zodb/views.py``:

   .. literalinclude:: views.py
      :linenos:

#. Copy the following into ``zodb/resources.py``:

   .. literalinclude:: resources.py
      :linenos:

#. ``$ python application.py``

#. Open ``http://127.0.0.1:8080/`` in your browser.

#. Add folders and documents.

Extra Credit
============

- Create a view that deletes a document.

- Remove the configuration line that includes ``pyramid_tm``.  What happens
  when you restart the application?  Are your changes persisted across
  restarts?

- What happens if you delete the files named ``Data.fs*``.

Analysis
========

We install ``pyramid_zodbconn`` to handle database connections to ZODB. This
pulls the ZODB3 package as well.

To enable ``pyramid_zodbconn``:

- We activate the package configuration using ``config.include``.

- We define a ``zodbconn.uri`` setting with the path to the Data.fs file.

- We put that setting in a dict and pass it to the ``Configurator``.

In the root factory, instead of using our old root object, we now get a
connection to the ZODB and create the object using that.

Our resources need a couple of small changes. Folders now inherit from
persistent.PersistentMapping and document from persistent.Persistent. Note
that Folder now needs to call super() on the __init__ method, or the
mapping will not initialize properly.

On the bootstrap, note the use of transaction.commit() to commit the
change. 

``pyramid_tm`` provides us with automatic transaction handling (one
transaction per request).  As a result, we don't need to commit a transaction
by hand.

We use the Deform package to autogenerate HTML forms.

Discussion
==========

- Note that you can add a folder to a folder, or a document to a folder.

- How does ``pyramid_tm`` work?  Why is centralized, automatic transaction
  management a good thing?



