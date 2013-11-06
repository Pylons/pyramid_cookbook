.. _single-file-tutorial:

Todo List Application in One File
===================================

This tutorial is intended to provide you with a feel of how a Pyramid web
application is created. The tutorial is very short, and focuses on the
creation of a minimal todo list application using common idioms. For brevity,
the tutorial uses a "single-file" application development approach
instead of the more complex (but more common) "scaffolds" described in
`the main Pyramid documentation
<http://docs.pylonsproject.org/projects/pyramid/en/latest/>`_.

At the end of the tutorial, you'll have a minimal application which:

- provides views to list, insert and close tasks

- uses route patterns to match your URLs to view code functions

- uses Mako Templates to render your views

- stores data in an SQLite database

Here's a screenshot of the final application:

.. image:: single_file_tasks.png

Step 1 - Organizing The Project
-------------------------------

.. note::

    For help getting Pyramid set up, try the `install guide
    <http://docs.pylonsproject.org/en/latest/docs/pyramid_install.html>`_.
    
    **New in Pyramid 1.5+:** If you're running Pyramid 1.5 or later, you need
    to install the mako template support separately as indicated `here
    <http://docs.pylonsproject.org/projects/pyramid/en/master/whatsnew-1.5.html>`_.

Before getting started, we will create the directory hierarchy needed for
our application layout. Create the following directory layout on your
filesystem:

.. code-block:: text

    /tasks
        /static
        /templates

Note that the ``tasks`` directory will not be used as a Python package,
it'll just serve as a container in which we can put our project.

Step 2 - Application Setup
--------------------------

To begin our application, start by adding a Python source file named
``tasks.py`` to the ``tasks`` directory.  We'll add a few basic imports
within the newly created file::

    import os
    import logging

    from pyramid.config import Configurator
    from pyramid.session import UnencryptedCookieSessionFactoryConfig

    from wsgiref.simple_server import make_server

Then we'll set up logging and the current working directory path::
    
    logging.basicConfig()
    log = logging.getLogger(__file__)
    
    here = os.path.dirname(os.path.abspath(__file__))

Finally, in a block that runs only when the file is directly executed
(i.e. not imported), we'll configure the Pyramid application,
establish rudimentary sessions, obtain the WSGI app,
and serve it::

    if __name__ == '__main__':
        # configuration settings
        settings = {}
        settings['reload_all'] = True
        settings['debug_all'] = True
        # session factory
        session_factory = UnencryptedCookieSessionFactoryConfig('itsaseekreet')
        # configuration setup
        config = Configurator(settings=settings, session_factory=session_factory)
        # serve app
        app = config.make_wsgi_app()
        server = make_server('0.0.0.0', 8080, app)
        server.serve_forever()

We now have the basic project layout needed to run our application, but
we still need to add database support, routing, views, and templates.

Step 3 - Database And Schema
----------------------------

To make things straightforward, we'll use the widely installed SQLite
database for our project. The schema for our tasks is simple: an **id**
to uniquely identify the task, a **name** not longer than 100 characters, and
a **closed** boolean to indicate if the task is closed or not.

Add to the ``tasks`` directory a file named ``schema.sql`` with the following
content:

.. literalinclude:: src/schema.sql
   :language: sql


Add a few more imports to the top of the ``tasks.py`` file::

    from pyramid.events import NewRequest
    from pyramid.events import subscriber
    from pyramid.events import ApplicationCreated
    import sqlite3

To make the process of creating the database slightly easier, rather than
requiring a user to execute the data import manually with SQLite, we'll create
a function that subscribes to a Pyramid system event for this purpose. By
subscribing a function to the ``ApplicationCreated`` event, each time we'll
start the application, our subscribed function will be executed.
Consequently, our database will be created or updated as necessary when the
application is started.

.. literalinclude:: src/tasks.py
   :lines: 72-80

We also need to make our database connection available to the application.
We'll provide the connection object as an attribute of the application's
request. By subscribing to the Pyramid ``NewRequest`` event we'll initialize
a connection to the database when a Pyramid request begins.  It will be
available as ``request.db``.  We'll arrange to close it down by the end of
the request lifecycle using the ``request.add_finished_callback`` method.

.. literalinclude:: src/tasks.py
   :lines: 61-70

To make those changes active, we'll have to specify the database location in
the configuration settings and make sure our ``@subscriber`` decorator is
scanned by the application at runtime using config.scan()::

    if __name__ == '__main__':
        ...
        settings['db'] = os.path.join(here, 'tasks.db')
        ...
        config.scan()
        ...

We now have the basic mechanism in place to create and talk to the database 
in the application through ``request.db``.

Step 4 - View Functions And Routes
----------------------------------

It's now time to expose some functionality to the world in the form of view
functions. We'll start by adding a few imports to our ``tasks.py`` file.  In
particular, we're going to import the ``view_config`` decorator, which will
let the application discover and register views::

    ...
    from pyramid.exceptions import NotFound
    from pyramid.httpexceptions import HTTPFound
    from pyramid.view import view_config
    ...

We'll now add some view functions to our application for listing, adding, and
closing todos. 

List View
+++++++++

This view is intended to show all open entries, according to our ``tasks``
table in the database. It uses the ``list.mako`` template available under the
``templates`` directory by defining it as the ``renderer`` in the
``view_config`` decorator. The results returned by the query are tuples but we
convert them into a dictionary for easier accessibility within the template.
The view function will pass a dictionary defining ``tasks`` to the
``list.mako`` template.

.. literalinclude:: src/tasks.py
   :lines: 23-27

When using the ``view_config`` decorator, it's important to specify a
``route_name`` to match a defined route, and a ``renderer`` if the function is
intended to render a template. The view function should then return a
dictionary defining the variables for the renderer to use.  Our ``list_view``
above does both.

New View
++++++++

This view lets the user add new tasks to the application. If a ``name`` is
provided to the form, a task is added to the database. Then an information
message is flashed to be displayed on the next request, and the user's browser
is redirected back to the *list_view*. If nothing is provided, a warning
message is flashed and the *new_view* is displayed again.

.. literalinclude:: src/tasks.py
   :lines: 30-42

.. warning::

    Be sure to use question marks when building SQL statements via
    ``db.execute``, otherwise your application will be vulnerable to SQL
    injection when using string formatting.

Close View
++++++++++

This view lets the user mark a task as closed, flashes a success message, and
redirects back to the *list_view* page.

.. literalinclude:: src/tasks.py
   :lines: 45-52

NotFound View
+++++++++++++

This view lets us customize the default ``NotFound`` view provided by Pyramid,
by using our own template. The ``NotFound`` view is displayed by Pyramid when
a URL cannot be mapped to a Pyramid view.  We'll add the template in a
subsequent step.

.. literalinclude:: src/tasks.py
   :lines: 55-57

Adding Routes
+++++++++++++

We finally need to add some routing elements to our application configuration
if we want our view functions to be matched to application URLs::

    ...
    # routes setup
    config.add_route('list', '/')
    config.add_route('new', '/new')
    config.add_route('close', '/close/{id}')
    ...

We've now added functionality to the application by defining views exposed
through the routes system.

Step 5 - View Templates
-----------------------

The views perform the work, but they need to render something that the web
browser understands: **HTML**.  We have seen that the view configuration
accepts a renderer argument with the name of a template. We'll use one of
the default templating engines supported out of the box by Pyramid: *Mako
Templates*.

We'll also use Mako template inheritance.  Template inheritance makes it
possible to reuse a generic layout across multiple templates, easing layout
maintenance and uniformity.

Create the following templates in the ``templates`` directory with the
respective content:

layout.mako
+++++++++++

This template contains the basic layout structure that will be shared with
other templates. Inside the body tag we've defined a block to display flash
messages sent by the application and another block to display the content of
the page inheriting this master layout by using the mako directive
``${next.body()}``.

.. literalinclude:: src/templates/layout.mako
   :language: html+mako

list.mako
+++++++++

This template is used by the ``list_view`` view function.  This template
extends the master ``layout.mako`` template by providing a listing of
tasks. The loop uses the passed ``tasks`` dictionary sent from the
``list_view`` function using Mako syntax. We also use the
``request.route_url`` function to generate a url based on a route name and
its arguments instead of statically defining the url path.

.. literalinclude:: src/templates/list.mako
   :language: html+mako

new.mako
++++++++

This template is used by the ``new_view`` view function.  The template
extends the master ``layout.mako`` template by providing a basic form to add
new tasks.

.. literalinclude:: src/templates/new.mako
   :language: html+mako

notfound.mako
+++++++++++++

This template extends the master ``layout.mako`` template.  We use it as the
template for our custom ``NotFound`` view.

.. literalinclude:: src/templates/notfound.mako
   :language: html+mako

Configuring Template Locations
++++++++++++++++++++++++++++++

To make it possible for views to find the templates they need by renderer
name, we now need to specify where the Mako templates can be found by
modifying the application configuration settings in ``tasks.py``::

    ...
    settings['mako.directories'] = os.path.join(here, 'templates')
    ...
    # add mako templating (for Pyramid 1.5+)
    config.include('pyramid_mako')
    ...

Step 6 - Styling Your Templates
-------------------------------

It's now time to add some styling to the application templates by adding a
**CSS** file named ``style.css`` to the ``static`` directory with the
following content:

.. literalinclude:: src/static/style.css
   :language: css

To cause this static file to be served by the application, we must add a
"static view" directive to the application configuration::

    ...
    config.add_static_view('static', os.path.join(here, 'static'))
    ...

Step 7 - Running The Application
--------------------------------

We have now completed all steps needed to run the application in its final
version. Before running it, here's the complete main code for ``tasks.py`` for
review:

.. literalinclude:: src/tasks.py
   :linenos:

And now let's run ``tasks.py``:

.. code-block:: bash

    $ python tasks.py 
    WARNING:tasks.py:Initializing database...

It will be listening on port 8080.

Conclusion
----------

This introduction to Pyramid was inspired by **flask** and **bottle** 
tutorials with the same minimalistic approach in mind. Big thanks Chris 
McDonough, Carlos de la Guardia, and Casey Duncan for their support and 
friendship.

