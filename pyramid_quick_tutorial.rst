Pyramid Quick Tutorial
======================

This tutorial is intended to give you a quick overview of the Pyramid Web 
Application Framework. Because Pyramid has few opinions on how to 
organize and develop your application, this tutorial focus on a minimal 
single file approach with common idioms to get a feel of basic Pyramid 
patterns. While those idioms and patterns are common, it is not suited to use 
this minimal approach to create a full fledged application. For this purpose 
Pyramid provides starter scaffolds, read more advanced documentation and 
tutorials.

Here's what you'll get at the end of the tutorial, a minimal application to 
view, insert and close tasks, backed by an SQLite database for storing your 
data, presented by Mako Templates to render your views and using the routes 
pattern to match your URLs to code functions.

.. image:: pyramid_quick_tutorial.png

Step 1 - Organizing The Project
-------------------------------

Before getting started, create the directory hierarchy needed for our 
application layout. The tasks directory will not be used as a python package, 
it'll just serves as a container to put and organize our project files.

.. code-block:: text

    /tasks
        /static
        /templates

Step 2 - Application Setup
-----------------

To begin with our application we'll start by creating a file name tasks.py 
to the tasks directory and add a few basic imports to the newly created file:

.. code-block:: python

    import os
    import logging
    
    from pyramid.config import Configurator
       
    from paste.httpserver import serve

Then setup logging and current working directory path:

.. code-block:: python
    
    logging.basicConfig()
    log = logging.getLogger(__file__)
    
    here = os.path.dirname(os.path.abspath(__file__))

Finally configure the Pyramid application registry, define the wsgi app 
and serve it.

.. code-block:: python
    
    if __name__ == '__main__':
        # configuration settings
        settings = {}
        settings['reload_all'] = True
        settings['debug_all'] = True
        # configuration setup
        config = Configurator(settings=settings)
        # serve app
        app = config.make_wsgi_app()
        serve(app, host='0.0.0.0')

We now have the basic application layout needed to build our project by 
adding database support, routing, views and templates.

Step 3 - Database And Schema
----------------------------

To make things simple and straightforward we'll use the widely installed 
SQLite database for our project. The schema for our tasks is also simple, 
an **id** to uniquely identify the task, a **name** not longer than 100 characters 
and a **closed** boolean to indicate if the task is closed or not.

Add to the tasks directory a file named schema.sql with the following content:

.. code-block:: sql

    CREATE TABLE IF NOT EXISTS tasks (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name CHAR(100) NOT NULL,
        closed BOOL NOT NULL
    );
    
    INSERT OR IGNORE INTO tasks (id, name, closed) VALUES (1, 'Start learning Pyramid', 0);
    INSERT OR IGNORE INTO tasks (id, name, closed) VALUES (2, 'Do quick tutorial', 0);
    INSERT OR IGNORE INTO tasks (id, name, closed) VALUES (3, 'Have some beer!', 0);

We'll continue by adding a few more imports to the tasks.py file:

.. code-block:: python

    ...
    from pyramid.events import NewRequest
    from pyramid.events import subscriber
    from pyramid.events import ApplicationCreated
    ...
    from paste.httpserver import serve
    import sqlite3
    ...

To make the process of creating the database a bit more friendly than 
executing the import manually with SQLite, we'll subscribe a function to a 
Pyramid system event for this purpose. By subscribing to the 
ApplicationCreated event, each time we'll start the application, our subscribed 
function will be executed and will create or update the database depending if 
it's the first time or not.

.. code-block:: python
    
    @subscriber(ApplicationCreated)
    def application_created_subscriber(event):
        log.warn('Initializing database...')
        f = open(os.path.join(here, 'schema.sql'), 'r')
        stmt = f.read()
        settings = event.app.registry.settings
        db = sqlite3.connect(settings['db'])
        db.executescript(stmt)
        db.commit()
        f.close()

We also need to make our database connection available to the application and 
a way to do it is through the application request. By subscribing to the 
Pyramid *NewRequest* event we'll initialize a connection to the database when 
the request begins and we'll manage to close it down by the end of its 
lifecycle using the *add_finished_callback* function.  

.. code-block:: python

    @subscriber(NewRequest)
    def new_request_subscriber(event):
        request = event.request
        settings = request.registry.settings
        request.db = sqlite3.connect(settings['db'])
        request.add_finished_callback(close_db_connection)

    def close_db_connection(request):
        request.db.close()

To make those changes working we have to specify where is the database 
location in the configuration settings and to make sure our @subscriber 
decorators are scanned by the application at runtime.

.. code-block:: python

    if __name__ == '__main__':
        ...
        settings['db'] = os.path.join(here, 'tasks.db')
        ...
        config.scan()
        ...

We now have the basic mechanism in place to create and talk to the database 
in the application through *request.db*.

Step 4 - Views Functions And Routes
-----------------------------------

It's now time to provide a way for the application to expose some 
functionalities to the world. We'll start by adding a few imports and 
specially the @view_config decorator to let the application discover 
and register our upcoming views.

.. code-block:: python

    ...
    from pyramid.exceptions import NotFound
    from pyramid.httpexceptions import HTTPFound
    from pyramid.session import UnencryptedCookieSessionFactoryConfig
    from pyramid.view import view_config
    ...

Then we'll add some functions to our application for listing, adding and 
closing todos. When using the @view_config decorator it's important to 
specify a route_name to match a defined route and a renderer file if the 
function is intended to return a template. The view function should then 
return a dictionary expected by the renderer to access variables.

List View
+++++++++

This view is intended to show up all open entries, not closed ones according 
to our schema, from the database. It uses the *list.mako* template available 
under the templates directory and defined as the renderer in the *view_config* 
decorator. The results returned by the query are tuples but we might want to 
convert them into a dict for easier accessibility within the template. 
The view function will pass a dict defining *tasks* to the *list.mako* 
template.

.. code-block:: python

    @view_config(route_name='list', renderer='list.mako')
    def list_view(request):
        rs = request.db.execute("select id, name from tasks where closed = 0")
        tasks = [dict(id=row[0], name=row[1]) for row in rs.fetchall()]
        return {'tasks': tasks}

New View
++++++++

This view lets the user add new tasks to the application. If a *name* is 
provided to the form, a task is added to the database, an information 
message is flashed to be displayed on the next request and the request is 
redirected back to the *list_view*. If nothing is provided a warning message 
is flashed and the *new_view* is displayed again.

.. code-block:: python

    @view_config(route_name='new', renderer='new.mako')
    def new_view(request):
        if request.method == 'POST':
            if request.POST.get('name'):
                request.db.execute('insert into tasks (name, closed) values (?, ?)',
                                   [request.POST['name'], 0])
                request.db.commit()
                request.session.flash('New task was successfully added!')
                return HTTPFound(location=request.route_url('list'))
            else:
                request.session.flash('Please enter a name for the task!')
        return {}

.. warning::

    Be sure to use question marks when building SQL statements, otherwise 
    your application will be vulnerable to SQL injection when using string 
    formatting.

Close View
++++++++++

This view lets the user mark a task as closed, flsh a success message and 
redirects back to the *list_view* page.

.. code-block:: python

    @view_config(route_name='close')
    def close_view(request):
        task_id = int(request.matchdict['id'])
        request.db.execute("update tasks set closed = ? where id = ?", (1, task_id))
        request.db.commit()
        request.session.flash('Task was successfully closed!')
        return HTTPFound(location=request.route_url('list'))

NotFound View
+++++++++++++

This view lets customize the default NotFound view provided by Pyramid by 
using your own template.

.. code-block:: python

    @view_config(context='pyramid.exceptions.NotFound',
                 renderer='notfound.mako')
    def notfound_view(self):
        return {}

We finally need to add some routing elements in our application configuration 
if we want our view functions to be exposed.

.. code-block:: python

    ...
    # routes setup
    config.add_route('list', '/')
    config.add_route('new', '/new')
    config.add_route('close', '/close/{id}')
    ...

We now have the basic mechanism in place to add functionality to the 
application by defining views and expose them through the routes system.

Step 5 - View Templates
-----------------------

Next step is to provide the application what web browser knows; **HTML**. 
To ease HTML development we'll use one of the default templating engines 
supported out of the box by Pyramid; *Mako Templates*.

We'll also use template inheritance which makes it possible to reuse a 
generic layout across multiple templates, easing layout maintenance and 
uniformity.

Create the following templates into the *templates* directory with their 
respective content:

layout.mako
+++++++++++

This template contains the basic layout structure to be shared with other 
templates. Inside the body tag we have defined a block to display flash 
messages sent by the application and another block to display the content of 
the page inheriting this master layout using the mako directive 
*${next.body()}*.

.. literalinclude:: pyramid_quick_tutorial/templates/layout.mako
   :language: html+mako

list.mako
+++++++++

This template extends the master *layout.mako* template by providing a 
listing of tasks. The loop is done using the passed tasks dict sent from 
the *list_view* using the pythonic mako syntax. We also use the 
*request.route_url* function to generate a url based on a route name and its 
arguments instead of statically defining the url path.

.. literalinclude:: pyramid_quick_tutorial/templates/list.mako
   :language: html+mako

new.mako
++++++++

This template extends the master *layout.mako* template by providing a basic 
form to add new tasks.

.. literalinclude:: pyramid_quick_tutorial/templates/new.mako
   :language: html+mako

notfound.mako
+++++++++++++

This template extends the master *layout.mako* template by customizing the 
default *NotFound* view provided by Pyramid.

.. literalinclude:: pyramid_quick_tutorial/templates/notfound.mako
   :language: html+mako

To make those templates working we now have to specify where are the 
templates to mako into the application configuration settings.

.. code-block:: python

    ...
    settings['mako.directories'] = os.path.join(here, 'templates')
    ...

Step 6 - Styling Your Templates
-------------------------------

It's now time to add some styling to the application templates by adding a 
**CSS** file named *style.css* to the *static* directory with the following 
content:

.. literalinclude:: pyramid_quick_tutorial/static/style.css
   :language: css

To make this static file served by the application we must add a static view 
directive to the application configuration:

.. code-block:: python

    ...
    config.add_static_view('static', os.path.join(here, 'static'))
    ...

Step 7 - Running The Application
--------------------------------

We have now completed every steps needed to run the application in its final 
version. Before running it, here's the complete main code for *task.py* for 
review:

.. literalinclude:: pyramid_quick_tutorial/tasks.py
   :language: python

And now let's run *tasks*:

.. code-block:: bash

    $ python tasks.py 
    WARNING:tasks.py:Initializing database...
    serving on 0.0.0.0:8080 view at http://127.0.0.1:8080

Conclusion
----------

This introduction to Pyramid was inspired by **flask** and **bottle** 
tutorials with the same minimalistic approach in mind. Big thanks Chris 
McDonough, Carlos De La Guardia and Casey Duncan for their support and 
friendship.
