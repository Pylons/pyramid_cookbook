MongoDB and Pyramid
====================

Basics
------

If you want to use MongoDB (via PyMongo and perhaps GridFS) via Pyramid, you
can use the following pattern to make your Mongo database available as a
request attribute.

First add the MongoDB URI to your ``development.ini`` file. (Note: ``user``, ``password`` and ``port`` are not required.)

.. code-block:: ini
   :linenos:

    [app:myapp]
    # ... other settings ...
    mongo_uri = mongodb://user:password@host:port/database

Then in your ``__init__.py``, set things up such that the database is
attached to each new request:

.. code-block:: python
   :linenos:

   from pyramid.config import Configurator
   from pyramid.events import subscriber
   from pyramid.events import NewRequest

   from gridfs import GridFS
   from urlparse import urlparse
   import pymongo


   def main(global_config, **settings):
      """ This function returns a Pyramid WSGI application.
      """
      config = Configurator(settings=settings)
      config.add_static_view('static', 'static', cache_max_age=3600)

      db_url = urlparse(settings['mongo_uri'])
      conn = pymongo.Connection(host=db_url.hostname,
                                port=db_url.port)
      config.registry.settings['db_conn'] = conn

      def add_mongo_db(event):
          settings = event.request.registry.settings
          db = settings['db_conn'][db_url.path[1:]]
          if db_url.username and db_url.password:
              db.authenticate(db_url.username, db_url.password)
          event.request.db = db
          event.request.fs = GridFS(db)

      config.add_subscriber(add_mongo_db, NewRequest)

      config.add_route('dashboard', '/')
      # other routes and more config...
      config.scan()
      return config.make_wsgi_app()

At this point, in view code, you can use request.db as the PyMongo database
connection.  For example:

.. code-block:: python
   :linenos:

    @view_config(route_name='dashboard',
                 renderer="myapp:templates/dashboard.pt")
    def dashboard(request):
        vendors = request.db['vendors'].find()
        return {'vendors':vendors}

Scaffolds
---------

Niall O'Higgins provides a `pyramid_mongodb
<http://pypi.python.org/pypi/pyramid_mongodb/1.0>`_ scaffold for Pyramid that
provides an easy way to get started with Pyramid and MongoDB.

Video
-----

Niall O'Higgins provides a presentation he gave at a Mongo conference in San
Francisco at
https://www.10gen.com/presentation/mongosf-2011/mongodb-with-python-pylons-pyramid

Other Information
------------------

- Pyramid traversal and MongoDB:
  http://kusut.web.id/2011/03/27/pyramid-traversal-and-mongodb/

- Pyramid, Aket and MongoDB:
  http://niallohiggins.com/2011/05/18/mongodb-python-pyramid-akhet/
