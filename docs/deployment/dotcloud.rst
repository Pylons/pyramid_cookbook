DotCloud
++++++++

`DotCloud <http://www.dotcloud.com/>`_ offers support for all WSGI frameworks.
Below is a quickstart guide for Pyramid apps. You can also read the `DotCloud
Python documentation <http://docs.dotcloud.com/services/python/>`_ for
a complete overview.

Step 0: Install DotCloud
========================

`Install DotCloud's CLI
<http://docs.dotcloud.com/firststeps/install/>`_ by running::

    $ pip install dotcloud

Step 1: Add files needed for DotCloud
=====================================

DotCloud expects Python applications to have a few files in the root of the
project. First, you need a pip ``requirements.txt`` file to instruct DotCloud
which Python library dependencies to install for your app. Secondly you need a
``dotcloud.yaml`` file which informs DotCloud that your application has (at a minimum)
a Python service. You may also want additional services such as a MongoDB
database or PostgreSQL database and so on - these things are all specified in
YAML.

Finally, you will need a file named ``wsgi.py`` which is what the DotCloud
uWSGI server is configured to look for. This wsgi.py script needs to create a
WSGI callable for your Pyramid app which must be present in a global named
"application".

You'll need to add a requirements.txt, dotcloud.yml, and wsgi.py file to the
root directory of your app. Here are some samples for a basic Pyramid app:

``requirements.txt``:

.. code-block:: text

    cherrypy
    Pyramid==1.3
    # Add any other dependencies that should be installed as well

``dotcloud.yml``:

.. code-block:: yaml

    www:
        type: python
    db:
        type: postgresql

Learn more about the `DotCloud buildfile <http://docs.dotcloud.com/guides/build-file/>`_.

``wsgi.py``::

    # Your WSGI callable should be named “application”, be located in a
    # "wsgi.py" file, itself located at the top directory of the service.
    #
    # For example, to load the app from your "production.ini" file in the same
    # directory:
    import os.path
    from pyramid.scripts.pserve import cherrypy_server_runner
    from pyramid.paster import get_app

    application = get_app(os.path.join(os.path.dirname(__file__), 'production.ini'))

    if __name__ == "__main__":
        cherrypy_server_runner(application, host="0.0.0.0")


Step 2: Configure your database
===============================

If you specified a database service in your dotcloud.yml, the connection info
will be made available to your service in a JSON file at
/home/dotcloud/environment.json. For example, the following code would read
the environment.json file and add the PostgreSQL URL to the settings of
your pyramid app::

    import json

    # if dotcloud, read PostgreSQL URL from environment.json
    db_uri = settings['postgresql.url']
    DOTCLOUD_ENV_FILE = "/home/dotcloud/environment.json"
    if os.path.exists(DOTCLOUD_ENV_FILE):
        with open(DOTCLOUD_ENV_FILE) as f:
            env = json.load(f)
            db_uri = env["DOTCLOUD_DATA_POSTGRESQL_URL"]


Learn more about the `DotCloud environment.json
<http://docs.dotcloud.com/guides/environment/>`_.

Step 3: Deploy your app
=======================

Now you can deploy your app. Remember to commit your changes if you're
using Mercurial or Git, then run these commands in the top directory
of your app::

    $ dotcloud create your_app_name
    $ dotcloud push your_app_name

At the end of the push, you'll see the URL(s) for your new app. Have fun!
