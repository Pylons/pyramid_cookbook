=============
Configuration
=============

While writing a Substance D application is very similar to writing a
Pyramid application, there are a few extra considerations to keep in
mind.

Scan and Include
================

When writing Pyramid applications, the Configurator supports
``config.include`` and ``config.scan`` Because of ordering
effects, do all your ``config.include`` calls before any of your
``config.scan`` calls.

Using RelStorage
================

Content in Substance D is stored in a Python object database called the
`ZODB <http://en.wikipedia.org/wiki/Zope_Object_Database>`_. The ZODB
has
`deep integration <http://docs.pylonsproject.org/projects/pyramid_cookbook/en/latest/database/zodb_zeo.html>`_
with Pyramid. When developing Python applications that use ZODB,
you have a number of storage options:

- ``FileStorage`` is the simplest and is used in the development
  scaffolds for Substance D. That is, ``development.ini`` is configured
  use ``FileStorage``. Just a file on disk, no long-running server
  process.

- ``ZEO`` keeps a file on disk but runs a server process that manages
  transactions over a socket. This allows multiple app servers on
  multiple boxes, or background processes such as deferred indexing,
  to access the database.

- `RelStorage <http://pypi.python.org/pypi/RelStorage>`_
  stores and retrieves the Python objects from a
  relational database. This is the preferred deployment option for
  applications that need trusted reliability and scalability.

Switching between storages is mostly a matter of editing your
configuration file and choosing a different storage.

.. note::

    While RelStorage uses an RDBMS for transactions, storage, retrieval,
    failover, and other features, it does *not* use SQL or decompose
    your Python objects into columns and joined tables.

Although RelStorage supports a number of RDBMS packages,
we'll focus on PostgreSQL in these docs.

RelStorage + PostgreSQL Configuration
-------------------------------------

First, read the RelStorage docs, focusing on the
`PostgreSQL section <http://pypi.python.org/pypi/RelStorage/1.5.1#postgresql>`_
and the command line needed for database setup. In particular,
make sure that you:

- Have a system user account named ``database``::

    $ sudo su - postgres
    $ createuser --pwprompt zodbuser
    $ createdb -O zodbuser zodb

- The user that you created (e.g. ``zodbuser``) can make local
  connections

Next, we'll make some changes to some of the configuration files. In
your ``setup.py``, indicate that you need the ``RelStorage`` package as
the ``psycopg2`` Python binding for PostgreSQL. This presumes that the
binaries for the PostgreSQL client are available on your path.

In your configuration file (e.g. ``production.ini``), the
``[app:main]`` section should have::

  zodbconn.uri = zconfig://%(here)s/relstorage.conf

We thus need a ``relstorage.conf`` file::

    <zodb main>
      <relstorage>
        blob-dir ../var/blobs
        <postgresql>
          dsn dbname='zodb' user='zodbuser' host='localhost' password='zodbuser'
        </postgresql>
      </relstorage>
      cache-size 100000
    </zodb>

Resetting Your Substance D Database
-----------------------------------

During development you frequently need to blow away all your data and
start over. You can do this via evolution, but usually it isn't worth
the work.

This is very easy with ``FileStorage``: just ``rm var/Data.fs*`` and
restart your app server. It is also easy with ZEO: shut down the
supervisor service, remove the data as above, restart it,
and restart the app server.

With RelStorage, you get a rich set of existing tools such as
``pgadmin`` to browser and modify table data. You can, though,
do it the quickie way via ``bin/pshell`` and just delete the root
object, then commit the transaction.

If you need to remove evolve data as well, open up pshell and do
``root._p_jar.root()``. You'll see the *ZODB* root
(not the app root). Inside of it is the app root and the evolve data.
