SQLAlchemy
==========

Basic Usage
-----------

You can get basic application template to use with SQLAlchemy by using
`alchemy` scaffold. Check the :ref:`narrative docs <creating_a_project>`
for more information.

Alternatively, you can try to follow
:ref:`wiki tutorial <bfg_sql_wiki_tutorial>` or
`blogr tutorial <http://pyramid-blogr.readthedocs.org>`_.

Using a Non-Global Session
--------------------------

It's sometimes advantageous to not use SQLAlchemy's thread-scoped sessions
(such as when you need to use Pyramid in an asynchronous system).
Thankfully, doing so is easy.  You can store a session factory in the
application's registry, and have the session factory called as a
side effect of asking the request object for an attribute.  The session
object will then have a lifetime matching that of the request.


We are going to use ``Configurator.add_request_method`` to add SQLAlchemy
session to request object and ``Request.add_finished_callback`` to close
said session.

.. note::

   ``Configurator.add_request_method`` has been available since Pyramid 1.4.
   You can use ``Configurator.set_request_property`` for Pyramid 1.3.


We'll assume you have an ``.ini`` file with ``sqlalchemy.`` settings that
specify your database properly::

   # __init__.py

   from pyramid.config import Configurator
   from sqlalchemy import engine_from_config
   from sqlalchemy.orm import sessionmaker

   def db(request):
       maker = request.registry.dbmaker
       session = maker()

       def cleanup(request):
           if request.exception is not None:
               session.rollback()
           else:
               session.commit()
           session.close()
       request.add_finished_callback(cleanup)

       return session


   def main(global_config, **settings):
       config = Configurator(settings=settings)
       engine = engine_from_config(settings, prefix='sqlalchemy.')
       config.registry.dbmaker = sessionmaker(bind=engine)
       config.add_request_method(db, reify=True)

       # .. rest of configuration ...

The SQLAlchemy session is now available in view code as ``request.db`` or
``config.registry.dbmaker()``.

Importing all SQLAlchemy Models
-------------------------------

If you've created a Pyramid project using a paster template, your SQLAlchemy
models will, by default, reside in a single file.  This is just by
convention.  If you'd rather have a directory for SQLAlchemy models rather
than a file, you can of course create a Python package full of model modules,
replacing the ``models.py`` file with a ``models`` directory which is a
Python package (a directory with an ``__init__.py`` in it), as per
:ref:`modifying_package_structure`.  However, due to the behavior of
SQLAlchemy's "declarative" configuration mode, all modules which hold active
SQLAlchemy models need to be imported before those models can successfully be
used.  So, if you use model classes with a declarative base, you need to
figure out a way to get all your model modules imported to be able to use
them in your application.

You might first create a ``models`` directory, replacing the ``models.py``
file, and within it a file named ``models/__init__.py``.  At that point, you
can add a submodule named ``models/mymodel.py`` that holds a single
``MyModel`` model class.  The ``models/__init__.py`` will define the
declarative base class and the global ``DBSession`` object, which each model
submodule (like ``models/mymodel.py``) will need to import.  Then all you
need is to add imports of each submodule within ``models/__init__.py``.

However, when you add ``models`` package submodule import statements to
``models/__init__.py``, this will lead to a circular import dependency.  The
``models/__init__.py`` module imports ``mymodel`` and ``models/mymodel.py``
imports the ``models`` package.  When you next try to start your application,
it will fail with an import error due to this circular dependency.

Pylons 1 solves this by creating a ``models/meta.py`` module, in which the
DBSession and declarative base objects are created.  The
``models/__init__.py`` file and each submodule of ``models`` imports
``DBSession`` and ``declarative_base`` from it.  Whenever you create a ``.py``
file in the ``models`` package, you're expected to add an import for it to
``models/__init__.py``.  The main program imports the ``models`` package,
which has the side effect of ensuring that all model classes have been
imported.  You can do this too, it works fine.

However, you can alternately use ``config.scan()`` for its side effects.
Using ``config.scan()`` allows you to avoid a circdep between
``models/__init__.py`` and ``models/themodel.py`` without creating a special
``models/meta.py``.

For example, if you do this in ``myapp/models/__init__.py``::

   from sqlalchemy.ext.declarative import declarative_base
   from sqlalchemy.orm import scoped_session, sessionmaker

   DBSession = scoped_session(sessionmaker())
   Base = declarative_base()

   def initialize_sql(engine):
       DBSession.configure(bind=engine)
       Base.metadata.bind = engine
       Base.metadata.create_all(engine)

And this in ``myapp/models/mymodel.py``::

   from myapp.models import Base
   from sqlalchemy import Column
   from sqlalchemy import Unicode
   from sqlalchemy import Integer

   class MyModel(Base):
       __tablename__ = 'models'
       id = Column(Integer, primary_key=True)
       name = Column(Unicode(255), unique=True)
       value = Column(Integer)
 
       def __init__(self, name, value):
           self.name = name
           self.value = value

And this in ``myapp/__init__.py``::

   from sqlalchemy import engine_from_config
 
   from myapp.models import initialize_sql
 
   def main(global_config, **settings):
       """ This function returns a Pyramid WSGI application.
       """
       config = Configurator(settings=settings)
       config.scan('myapp.models') # the "important" line
       engine = engine_from_config(settings, 'sqlalchemy.')
       initialize_sql(engine)
       # other statements here
       config.add_handler('main', '/{action}',
                        'myapp.handlers:MyHandler')
       return config.make_wsgi_app()

The important line above is ``config.scan('myapp.models')``.  ``config.scan``
has a side effect of performing a recursive import of the package name it is
given.  This side effect ensures that each file in ``myapp.models`` is
imported without requiring that you import each "by hand" within
``models/__init__.py``.  It won't import any models that live outside the
``myapp.models`` package, however.

Writing Tests For Pyramid + SQLAlchemy
--------------------------------------

John Anderson's blog entry describes a strategy for
`writing tests for systems which integrate Pyramid and SQLAlchemy
<http://www.sontek.net/blog/2011/12/01/writing_tests_for_pyramid_and_sqlalchemy.html>`_.
