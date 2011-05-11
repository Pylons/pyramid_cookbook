CouchDB and Pyramid
====================

If you want to use CouchDB (via the
`CouchDB package <http://pypi.python.org/pypi/CouchDB>`_)
in Pyramid, you
can use the following pattern to make your CouchDB database available as a
request attribute.  (This follows the same pattern as the :doc:`mongo` example.)

First add some hair to your ``development.ini`` file, including a CouchDB URI
and a "db_name" (the CouchDB database name, can be anything).

.. code-block:: ini
   :linenos:

    [app:myapp]
    # ... other settings ...
    couchdb_uri = http://user:password@localhost/
    db_name = myapp

Then in your ``__init__.py``, set things up such that the database is
attached to each new request:

.. code-block:: python
   :linenos:

    from pyramid.config import Configurator
    from pyramid.events import subscriber
    from pyramid.events import NewRequest

    import couchdb

    @subscriber(NewRequest)
    def add_couchdb_to_request(event):
        db = settings['db_server'][settings['db_name']]
        event.request.db = db

    def main(global_config, **settings):
        config = Configurator(settings=settings)

        db_server = couchdb.client.Server(settings['couchdb_uri'])
        config.registry.settings['db_server'] = db_server

        config.add_route('home', '/')

        # other routes and more config...
        config.scan('myapp')

        return config.make_wsgi_app()



At this point, in view code, you can use request.db as the CouchDB database
connection.  For example:

.. code-block:: python
   :linenos:

    @view_config(route_name='home', renderer="home.pt")
    def home_view(request):
        map_func = '''
            function(doc) {
            if (doc.type == 'MyDocumentType')
                emit(doc._id, doc);
            }'''
        documents = request.db.query(map_func)
        return {'documents': documents}


Permanent CouchDB Views
-----------------------

As per the
`CouchDB docs <http://wiki.apache.org/couchdb/Introduction_to_CouchDB_views>`_,
once your ad-hoc CouchDB view functions are
working correctly, you should move them into permanent views. For
example, to create a CouchDB view at startup:

.. code-block:: python
   :linenos:

    DESIGN_DOC_ID = '_design/myapp'

    @subscriber(ApplicationCreated)
    def application_created_subscriber(event):
        settings = event.app.registry.settings
        server = settings['db_server']
        try:
            db = server[settings['db_name']]
        except couchdb.http.ResourceNotFound:
            db = server.create(settings['db_name'])

        # We'll create some couchdb views so we don't have to do ad-hoc queries.
        home_view_map_func = '''
          function(doc) {
          if (doc.type == 'MyDocumentType')
             emit(doc._id, doc);
          }'''
        design_doc = db.get(DESIGN_DOC_ID, {'_id': DESIGN_DOC_ID})
        design_doc.update({
            "language": "javascript",
            "views": {
                "home": {
                    "map": home_view_map_func,
                    },
                }
            })
        _id, rev = db.save(design_doc)
        log.info('Updated design doc: id %s, revision %s' % (_id, rev))


Then you can update your Pyramid view code to call that view:

.. code-block:: python
   :linenos:

    @view_config(route_name='home', renderer="home.pt")
    def home_view(request):
        view_id = '%s/_view/home' % DESIGN_DOC_ID
        documents = request.db.view(view_id)
        return {'documents': documents}
