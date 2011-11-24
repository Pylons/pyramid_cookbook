====================
Using repoze.catalog
====================

Goals
=====

- Index and and search for content using ``repoze.catalog``, a Python
  indexing system tool based on ZODB.

.. warning::

  Caveat: this will likely only work on systems that have C compilation tools
  installed (XCode, Linux) *or* on Windows systems.  If you can't get
  ``repoze.catalog`` installed properly you may need to pair up with someone
  who can.

Objectives
==========

- Install ``repoze.catalog``.

- Index the ``title`` and ``content`` attributes of content we add to the
  system into fulltext indices.

- Search for, and find, content we've added to the system using fulltext
  queries.

Steps
=====

#. ``easy_install repoze.catalog``

#. ``mkdir catalog``

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

- Add another attribute to documents and folders named ``age`` (an integer)
  and use a ``repoze.catalog.FieldIndex`` to index and search the age of new
  documents.  See http://docs.repoze.org/catalog/

- Change the ``query = `` line in folder_view to not care about what's in
  ``title`` (instead, only care about what's in ``content``).

- Unindex a document.

Analysis
========

We made no changes to ``application.py``.

resources.py
------------

Note the imports of ``catalog`` and ``index`` from ``repoze.catalog``.

We create a catalog and two text indexes for title and content attributes.

We add the catalog *inside* the site folder. We also add a document map, which
helps us map actual content to catalog ids.

views.py
--------

On the add_folder and add_content views, we now index the document and add it
to the document map. We use the content ittem's path on the site to make the
map. 

To obtain a nice docid for the catalog, we use document_map.new_docid().

The path is obtained using the pyramid.traversal.resource_path() call.

After that we can index with catalog.index_doc().

The search view makes a query for all content with the search term either in
the title or the content of all catalogued items.

The [results] dance afterwards is to get the actual objects from the doc_id via
the document map.

Note the use of render_to_response to use the search template and not the one
configured for this view.

Discussion
==========

- ``repoze.catalog`` uses ZODB under the hood but isn't only for applications
  that use ZODB for business data storage.  Can be used like Lucene or
  Xapian.

- ``query`` value ``'foo' in title or 'foo' in content`` is a "CQE" (catalog
  query expression).  This is a declarative query system, not unlike SQL (but
  less expressive).

