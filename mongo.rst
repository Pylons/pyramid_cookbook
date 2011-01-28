MongoDB and Pyramid
====================

If you want to use MongoDB (via PyMongo and perhaps GridFS) via Pyramid, you
can use the following pattern to make your Mongo database available as a
request attribute.

First add some hair to your ``development.ini`` file, including a MongoDB URI
and a "db_name" (the Mongo database name, can be anything).

.. code-block:: ini
   :linenos:

    [app:myapp]
    # ... other settings ...
    db_uri = mongodb://localhost/
    db_name = myapp

Then in your ``__init__.py``, set things up such that the database is
attached to each new request:

.. code-block:: python
   :linenos:

   from pyramid.config import Configurator
   from pyramid.events import subscriber
   from pyramid.events import NewRequest

   from gridfs import GridFS
   import pymongo

   def main(global_config, **settings):
       config = Configurator(settings=settings)

       db_uri = settings['db_uri']
       conn = pymongo.Connection(db_uri)
       config.registry.settings['db_conn'] = conn
       config.add_subscriber(add_mongo_db, NewRequest)

       config.add_route('dashboard', '/')
       # other routes and more config...
       config.scan('myapp')

       return config.make_wsgi_app()

   def add_mongo_db(event):
       settings = event.request.registry.settings
       db = settings['db_conn'][settings['db_name']]
       event.request.db = db
       event.request.fs = GridFS(db)

At this point, in view code, you can use request.db as the PyMongo database
connection.  For example:

.. code-block:: python
   :linenos:

    @view_config(route_name='dashboard',
                 renderer="myapp:templates/dashboard.pt")
    def dashboard(request):
        vendors = request.db['vendors'].find()
        return {'vendors':vendors}
