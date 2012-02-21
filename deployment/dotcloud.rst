DotCloud
++++++++

`DotCloud <http://www.dotcloud.com/>`_ offers support for all WSGI frameworks.
Below is a quickstart guide for Pyramid apps. You can also read the `DotCloud
Python documentation <http://newdocs.dotcloud.com/services/python/>` for
a complete overview.

Step 0: Install DotCloud
========================

`Install DotCloud's CLI
<http://docs.dotcloud.com/#installation.html>`_ by running::

    $ pip install dotcloud

Step 1: Add files needed for DotCloud
=====================================

You'll need to add a requirements.txt, dotcloud.yml, and wsgi.py file to the
root directory of your app.

``requirements.txt``:

.. code-block:: text

    Pyramid==1.0
    # Add any other dependencies that should be installed as well

``dotcloud.yml``:

.. code-block:: yaml

    www:
        type: python
    db:
        type: postgresql

Learn more about the `dotcloud.yml
<http://docs.dotcloud.com/#buildfile.html> here`.

``wsgi.py``

.. code-block:: python

    # Your WSGI callable should be named “application”, be located in a
    # "wsgi.py" file, itself located at the top directory of the service.
    #
    # For example, this file might contain:
    from your_main_app_file import app as application
    #
    # or it might include something like:
    # application = config.make_wsgi_app()


Step 2: Configure your database
===============================

If you specified a database service in your dotcloud.yml, the connection info
will be made available to your service in a JSON file at
/home/dotcloud/environment.json. For example, the following code would read
the environment.json file and add the PostgreSQL URL to the settings of
your pyramid app:

.. code-block:: python

    import json

    from pyramid.Config import Configurator

    with open('/home/dotcloud/environment.json') as f:
        env = json.loads(f.read())

    if __name__ == '__main__':
        settings = {}
        settings['db'] = env['DOTCLOUD_DB_POSTGRESQL_URL']
        config = Configurator(settings=settings)
        application = config.make_wsgi_app()

Learn more about the `DotCloud environment.json
<http://docs.dotcloud.com/#environmentfile.html>`.

Step 3: Deploy your app
=======================

Now you can deploy your app. Remember to commit your changes if you're
using Mercurial or Git, then run these commands in the top directory
of your app::

    $ dotcloud create your_app_name
    $ dotcloud push your_app_name

At the end of the push, you'll see the URL(s) for your new app. Have fun!

Tips & Tricks
=============

The CherryPy WSGI server is fast, efficient, and multi-threaded to easily
handle many requests at once. If you're deploying small and/or low-traffic
websites you can use the `PasteDeploy composite capabilities
<http://pythonpaste.org/deploy/#composite-applications>`_ to serve multiple
web applications with a single Heroku web dyno.

Heroku add-on's generally communicate their settings via OS environ variables.
These can be easily incorporated into your applications settings, for
example::
    
    # In your pyramid apps main init
    import os
    
    from pyramid.config import Configurator
    from myproject.resources import Root

    def main(global_config, **settings):
        """ This function returns a Pyramid WSGI application.
        """
        memcache_server = os.environ.get('MEMCACHE_SERVERS')
        settings['beaker.cache.url'] = memcache_server
        config = Configurator(root_factory=Root, settings=settings)
        config.add_view('myproject.views.my_view',
                        context='myproject.resources.Root',
                        renderer='myproject:templates/mytemplate.pt')
        config.add_static_view('static', 'myproject:static')
        return config.make_wsgi_app()
