CouchDB and Pyramid
====================

If you want to use CouchDB (via the
`couchdbkit package <http://pypi.python.org/pypi/couchdbkit>`_)
in Pyramid, you can use the following pattern to make your CouchDB database
available as a ``request`` attribute. This example uses the starter scaffold.
(This follows the same pattern as the :doc:`mongodb` example.)

First add configuration values to your ``development.ini`` file, including your
CouchDB URI and a database name (the CouchDB database name, can be anything).

.. code-block:: ini
   :linenos:

    [app:main]
    # ... other settings ...
    couchdb.uri = http://localhost:5984/
    couchdb.db = mydb

Then in your ``__init__.py``, set things up such that the database is
attached to each new request::

    from pyramid.config import Configurator
    from couchdbkit import *


    def main(global_config, \**settings):
        """ This function returns a Pyramid WSGI application.
        """
        config = Configurator(settings=settings)
        config.registry.db = Server(uri=settings['couchdb.uri'])

        def add_couchdb(request):
            db = config.registry.db.get_or_create_db(settings['couchdb.db'])
            return db

        config.add_request_method(add_couchdb, 'db', reify=True)

        config.add_static_view('static', 'static', cache_max_age=3600)
        config.add_route('home', '/')
        config.scan()
        return config.make_wsgi_app()

.. note::

   ``Configurator.add_request_method`` has been available since Pyramid 1.4.
   You can use ``Configurator.set_request_property`` for Pyramid 1.3.

At this point, in view code, you can use ``request.db`` as the CouchDB database
connection.  For example::

    from pyramid.view import view_config

    @view_config(route_name='home', renderer='templates/mytemplate.pt')
    def my_view(request):
        """ Get info for server
        """
        return {
            'project': 'pyramid_couchdb_example',
            'info': request.db.info()
        }

Add info to home template:

.. code-block:: html
   :linenos:

    <p>${info}</p>

CouchDB Views
-------------

First let's create a view for our page data in CouchDB. We will use the
ApplicationCreated event and make sure our view containing our page data.
For more information on views in CouchDB see
`Introduction to CouchDB views <http://wiki.apache.org/couchdb/Introduction_to_CouchDB_views>`_.
In __init__.py::

    from pyramid.events import subscriber, ApplicationCreated

    @subscriber(ApplicationCreated)
    def application_created_subscriber(event):
        registry = event.app.registry
        db = registry.db.get_or_create_db(registry.settings['couchdb.db'])

        pages_view_exists = db.doc_exist('lists/pages')
        if pages_view_exists == False:
            design_doc = {
                '_id': '_design/lists',
                'language': 'javascript',
                'views': {
                    'pages': {
                        'map': '''
                            function(doc) {
                                if (doc.doc_type === 'Page') {
                                    emit([doc.page, doc._id], null)
                                }
                            }
                        '''
                    }
                }
            }
            db.save_doc(design_doc)

CouchDB Documents
-----------------

Now we can let's add some data to a document for our home page in a CouchDB
document in our view code if it doesn't exist::

    import datetime

    from couchdbkit import *

    class Page(Document):
        author = StringProperty()
        page = StringProperty()
        content = StringProperty()
        date = DateTimeProperty()

    @view_config(route_name='home', renderer='templates/mytemplate.pt')
    def my_view(request):

        def get_data():
            return list(request.db.view('lists/pages', startkey=['home'], \
                    endkey=['home', {}], include_docs=True))

        page_data = get_data()

        if not page_data:
            Page.set_db(request.db)
            home = Page(
                author='Wendall',
                content='Using CouchDB via couchdbkit!',
                page='home',
                date=datetime.datetime.utcnow()
            )
            # save page data
            home.save()
            page_data = get_data()

        doc = page_data[0].get('doc')

        return {
            'project': 'pyramid_couchdb_example',
            'info': request.db.info(),
            'author': doc.get('author'),
            'content': doc.get('content'),
            'date': doc.get('date')
        }

Then update your home template again to add your custom values:

.. code-block:: html
   :linenos:

    <p>
        ${author}<br />
        ${content}<br />
        ${date}<br />
    </p>
