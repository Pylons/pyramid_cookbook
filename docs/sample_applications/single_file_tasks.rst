.. _single-file-tutorial:

Todo List Application in One File
=================================

This tutorial is intended to provide you with a feel of how a Pyramid web
application is created. The tutorial is very short, and focuses on the creation
of a minimal todo list application using common idioms. For brevity, the
tutorial uses a "single-file" application development approach instead of the
more complex (but more common) "scaffolds" described in the :ref:`main Pyramid
documentation <pyramid:index>`.

At the end of the tutorial, you'll have a minimal application which:

- provides views to list, insert and close tasks

- uses route patterns to match your URLs to view code functions

- uses Mako Templates to render your views

- stores data in an SQLite database

Here's a screenshot of the final application:

.. image:: single_file_tasks.png


Step 1 - Organizing the project
-------------------------------

.. note::

    For help getting Pyramid set up, try the guide :ref:`Installing Pyramid
    <pyramid:installing_chapter>`.
    
    To use Mako templates, you need to install the ``pyramid_mako`` add-on as
    indicated under `Major Backwards Incompatibilities under What's New In
    Pyramid 1.5
    <http://docs.pylonsproject.org/projects/pyramid/en/master/whatsnew-1.5.html#major-backwards-incompatibilities>`_.

    In short, you'll need to have both the ``pyramid`` and ``pyramid_mako``
    packages installed. Use ``easy_install pyramid pyramid_mako`` or ``pip
    install pyramid`` and ``pip install pyramid_mako`` to install these
    packages.

Before getting started, we will create the directory hierarchy needed for our
application layout. Create the following directory layout on your filesystem:

.. code-block:: text

    /tasks
        /static
        /templates

Note that the ``tasks`` directory will not be used as a Python package; it will
just serve as a container in which we can put our project.


Step 2 - Application setup
--------------------------

To begin our application, start by adding a Python source file named
``tasks.py`` to the ``tasks`` directory.  We'll add a few basic imports within
the newly created file.

.. code-block:: python
   :linenos:
   :lineno-start: 1

    import os
    import logging

    from pyramid.config import Configurator
    from pyramid.session import UnencryptedCookieSessionFactoryConfig

    from wsgiref.simple_server import make_server

Then we'll set up logging and the current working directory path.
    
.. code-block:: python
   :linenos:
   :lineno-start: 9

    logging.basicConfig()
    log = logging.getLogger(__file__)
    
    here = os.path.dirname(os.path.abspath(__file__))

Finally, in a block that runs only when the file is directly executed (i.e.,
not imported), we'll configure the Pyramid application, establish rudimentary
sessions, obtain the WSGI app, and serve it.

.. code-block:: python
   :linenos:
   :lineno-start: 14

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

We now have the basic project layout needed to run our application, but we
still need to add database support, routing, views, and templates.

Step 3 - Database and schema
----------------------------

To make things straightforward, we'll use the widely installed SQLite database
for our project. The schema for our tasks is simple: an ``id`` to uniquely
identify the task, a ``name`` not longer than 100 characters, and a ``closed``
boolean to indicate whether the task is closed.

Add to the ``tasks`` directory a file named ``schema.sql`` with the following
content:

.. literalinclude:: single_file_tasks_src/schema.sql
   :language: sql

Add a few more imports to the top of the ``tasks.py`` file as indicated by the
emphasized lines.

.. literalinclude:: single_file_tasks_src/tasks.py
   :language: python
   :lines: 1-8
   :linenos:
   :lineno-start: 1
   :emphasize-lines: 3,6-8

To make the process of creating the database slightly easier, rather than
requiring a user to execute the data import manually with SQLite, we'll create
a function that subscribes to a Pyramid system event for this purpose. By
subscribing a function to the ``ApplicationCreated`` event, for each time we
start the application, our subscribed function will be executed. Consequently,
our database will be created or updated as necessary when the application is
started.

.. literalinclude:: single_file_tasks_src/tasks.py
   :language: python
   :lines: 73-85
   :linenos:
   :lineno-start: 21
   :emphasize-lines: 1-9

We also need to make our database connection available to the application.
We'll provide the connection object as an attribute of the application's
request. By subscribing to the Pyramid ``NewRequest`` event, we'll initialize a
connection to the database when a Pyramid request begins.  It will be available
as ``request.db``.  We'll arrange to close it down by the end of the request
lifecycle using the ``request.add_finished_callback`` method.

.. literalinclude:: single_file_tasks_src/tasks.py
   :language: python
   :lines: 62-74
   :linenos:
   :lineno-start: 21
   :emphasize-lines: 1-10

To make those changes active, we'll have to specify the database location in
the configuration settings and make sure our ``@subscriber`` decorator is
scanned by the application at runtime using ``config.scan()``.

.. literalinclude:: single_file_tasks_src/tasks.py
   :language: python
   :lines: 85-90
   :linenos:
   :lineno-start: 44
   :emphasize-lines: 6


.. literalinclude:: single_file_tasks_src/tasks.py
   :language: python
   :lines: 104-106
   :linenos:
   :lineno-start: 54
   :emphasize-lines: 1-2

We now have the basic mechanism in place to create and talk to the database in
the application through ``request.db``.


Step 4 - View functions and routes
----------------------------------

It's now time to expose some functionality to the world in the form of view
functions. We'll start by adding a few imports to our ``tasks.py`` file.  In
particular, we're going to import the ``view_config`` decorator, which will
let the application discover and register views:

.. literalinclude:: single_file_tasks_src/tasks.py
   :language: python
   :lines: 8-12
   :linenos:
   :lineno-start: 8
   :emphasize-lines: 2-3,5

Note that our imports are sorted alphabetically within the ``pyramid``
Python-dotted name which makes them easier to find as their number increases.

We'll now add some view functions to our application for listing, adding, and
closing todos.


List view
+++++++++

This view is intended to show all open entries, according to our ``tasks``
table in the database. It uses the ``list.mako`` template available under the
``templates`` directory by defining it as the ``renderer`` in the
``view_config`` decorator. The results returned by the query are tuples, but we
convert them into a dictionary for easier accessibility within the template.
The view function will pass a dictionary defining ``tasks`` to the
``list.mako`` template.

.. literalinclude:: single_file_tasks_src/tasks.py
   :language: python
   :lines: 20-28
   :linenos:
   :lineno-start: 20
   :emphasize-lines: 4-

When using the ``view_config`` decorator, it's important to specify a
``route_name`` to match a defined route, and a ``renderer`` if the function is
intended to render a template. The view function should then return a
dictionary defining the variables for the renderer to use.  Our ``list_view``
above does both.


New view
++++++++

This view lets the user add new tasks to the application. If a ``name`` is
provided to the form, a task is added to the database. Then an information
message is flashed to be displayed on the next request, and the user's browser
is redirected back to the ``list_view``. If nothing is provided, a warning
message is flashed and the ``new_view`` is displayed again.  Insert the
following code immediately after the ``list_view``.

.. literalinclude:: single_file_tasks_src/tasks.py
   :language: python
   :lines: 31-43
   :linenos:
   :lineno-start: 31
   :emphasize-lines: 1-

.. warning::

    Be sure to use question marks when building SQL statements via
    ``db.execute``, otherwise your application will be vulnerable to SQL
    injection when using string formatting.


Close view
++++++++++

This view lets the user mark a task as closed, flashes a success message, and
redirects back to the ``list_view`` page. Insert the following code immediately
after the ``new_view``.

.. literalinclude:: single_file_tasks_src/tasks.py
   :language: python
   :lines: 46-53
   :linenos:
   :lineno-start: 46
   :emphasize-lines: 1-


NotFound view
+++++++++++++

This view lets us customize the default ``NotFound`` view provided by Pyramid,
by using our own template. The ``NotFound`` view is displayed by Pyramid when
a URL cannot be mapped to a Pyramid view.  We'll add the template in a
subsequent step. Insert the following code immediately after the
``close_view``.

.. literalinclude:: single_file_tasks_src/tasks.py
   :language: python
   :lines: 56-58
   :linenos:
   :lineno-start: 56
   :emphasize-lines: 1-


Adding routes
+++++++++++++

We finally need to add some routing elements to our application configuration
if we want our view functions to be matched to application URLs. Insert the
following code immediately after the configuration setup code.

.. literalinclude:: single_file_tasks_src/tasks.py
   :language: python
   :lines: 98-101
   :linenos:
   :lineno-start: 95
   :emphasize-lines: 1-

We've now added functionality to the application by defining views exposed
through the routes system.


Step 5 - View templates
-----------------------

The views perform the work, but they need to render something that the web
browser understands: HTML.  We have seen that the view configuration accepts a
renderer argument with the name of a template. We'll use one of the templating
engines, Mako, supported by the Pyramid add-on, `pyramid_mako
<http://docs.pylonsproject.org/projects/pyramid-mako/en/latest/>`_.

We'll also use Mako template inheritance. Template inheritance makes it
possible to reuse a generic layout across multiple templates, easing layout
maintenance and uniformity.

Create the following templates in the ``templates`` directory with the
respective content:


layout.mako
+++++++++++

This template contains the basic layout structure that will be shared with
other templates. Inside the body tag, we've defined a block to display flash
messages sent by the application, and another block to display the content of
the page, inheriting this master layout by using the mako directive
``${next.body()}``.

.. literalinclude:: single_file_tasks_src/templates/layout.mako
   :language: html+mako


list.mako
+++++++++

This template is used by the ``list_view`` view function.  This template
extends the master ``layout.mako`` template by providing a listing of tasks.
The loop uses the passed ``tasks`` dictionary sent from the ``list_view``
function using Mako syntax. We also use the ``request.route_url`` function to
generate a URL based on a route name and its arguments instead of statically
defining the URL path.

.. literalinclude:: single_file_tasks_src/templates/list.mako
   :language: html+mako


new.mako
++++++++

This template is used by the ``new_view`` view function. The template extends
the master ``layout.mako`` template by providing a basic form to add new tasks.

.. literalinclude:: single_file_tasks_src/templates/new.mako
   :language: html+mako


notfound.mako
+++++++++++++

This template extends the master ``layout.mako`` template.  We use it as the
template for our custom ``NotFound`` view.

.. literalinclude:: single_file_tasks_src/templates/notfound.mako
   :language: html+mako


Configuring template locations
++++++++++++++++++++++++++++++

To make it possible for views to find the templates they need by renderer
name, we now need to specify where the Mako templates can be found by modifying
the application configuration settings in ``tasks.py``. Insert the emphasized
lines as indicated in the following.

.. literalinclude:: single_file_tasks_src/tasks.py
   :language: python
   :lines: 90-98
   :linenos:
   :lineno-start: 90
   :emphasize-lines: 2,7-8


Step 6 - Styling your templates
-------------------------------

It's now time to add some styling to the application templates by adding a CSS
file named ``style.css`` to the ``static`` directory with the following
content:

.. literalinclude:: single_file_tasks_src/static/style.css
   :language: css

To cause this static file to be served by the application, we must add a
"static view" directive to the application configuration.

.. literalinclude:: single_file_tasks_src/tasks.py
   :language: python
   :lines: 101-104
   :linenos:
   :lineno-start: 101
   :emphasize-lines: 2-3


Step 7 - Running the application
--------------------------------

We have now completed all steps needed to run the application in its final
version. Before running it, here's the complete main code for ``tasks.py`` for
review.

.. literalinclude:: single_file_tasks_src/tasks.py
   :language: python
   :linenos:

And now let's run ``tasks.py``:

.. code-block:: bash

    $ python tasks.py 
    WARNING:tasks.py:Initializing database...

It will be listening on port 8080. Open a web browser to the URL
http://localhost:8080/ to view and interact with the app.

Conclusion
----------

This introduction to Pyramid was inspired by Flask and Bottle tutorials with
the same minimalistic approach in mind. Big thanks to Chris McDonough, Carlos
de la Guardia, and Casey Duncan for their support and friendship.
