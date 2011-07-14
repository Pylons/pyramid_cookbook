Deploying Your Pyramid Application
----------------------------------

So you've written a sweet application and you want to deploy it outside of
your local machine. We're not going to cover caching here, but suffice it to
say that there are a lot of things to consider when optimizing your pyramid
application.

At a high level, you need to expose a server on ports 80 (HTTP) and 443
(HTTPS) to handle your various traffic. Underneath this layer, however, is
a plethora of different configurations that can be used to get a request
from a client, into your application, and return the response.

::

    Client <---> WSGI Server <---> Your Application

Due to the beauty of standards, many different configurations can be used to
generate this basic setup, injecting caching layers, load balancers, etc into
the basic workflow.

Disclaimer
++++++++++

It's important to note that the setups discussed here are meant to give some
direction to newer users. Deployment is *almost always* highly dependent on
the application's specific purposes. These setups have been used for many
different projects in production with much success, but never verbatim.

What is WSGI?
+++++++++++++

WSGI is a Python standard dictating the interface between a server and an
application. The entry point to your pyramid application is an object
implementing the WSGI interface. Thus, your application can be served by any
server supporting WSGI.

There are many different servers implementing the WSGI standard in existance.
A short list includes:

+ ``paste.httpserver``

+ ``CherryPy``

+ ``uwsgi``

+ ``gevent``

+ ``mod_wsgi``

Nginx + paster + supervisord
++++++++++++++++++++++++++++

This setup can be accomplished simply and is capable of serving a large amount
of traffic. The advantage in deployment is that by using ``paster``, it is not
unlike the basic development environment you're probably using on your local
machine.

Nginx is a highly optimized HTTP server, very capable of serving static
content as well as acting as a proxy between other applications and the
outside world. As a proxy, it also has good support for basic load balancing
between multiple instances of an application.

::

    Client <---> Nginx [0.0.0.0:80] <---> (static files)
                  /|\
                   |-------> Paster [localhost:5000]
                   `-------> Paster [localhost:5001]

Our target setup is going to be an Nginx server listening on port 80 and
load-balancing between 2 Paster processes. It will also serve the static files
from our project's directory.

Let's assume a basic project setup::

    /home/example/myapp
    |
    |-- env (your virtualenv)
    |
    |-- myapp
    |   |
    |   |-- __init__.py (defining your main entry point)
    |   |
    |   `-- static (your static files)
    |
    |-- production.ini
    |
    `-- supervisord.conf (optional)


Step 1: Configuring Nginx
=========================

Nginx needs to be configured as a proxy for your application. An example
configuration is shown here:

.. code-block:: ini
    :linenos:

    # nginx.conf

    user www-data;
    worker_processes 4;
    pid /var/run/nginx.pid;

    events {
        worker_connections 1024;
        # multi_accept on;
    }

    http {

        ##
        # Basic Settings
        ##

        sendfile on;
        tcp_nopush on;
        tcp_nodelay on;
        keepalive_timeout 65;
        types_hash_max_size 2048;
        # server_tokens off;

        # server_names_hash_bucket_size 64;
        # server_name_in_redirect off;

        include /etc/nginx/mime.types;
        default_type application/octet-stream;

        ##
        # Logging Settings
        ##

        access_log /var/log/nginx/access.log;
        error_log /var/log/nginx/error.log;

        ##
        # Gzip Settings
        ##

        gzip on;
        gzip_disable "msie6";

        ##
        # Virtual Host Configs
        ##

        server {
            server_name _;
            return 444;
        }

        include /etc/nginx/conf.d/*.conf;
        include /etc/nginx/sites-enabled/*;
    }

.. code-block:: ini
    :linenos:

    # myapp.conf

    upstream myapp-site {
        server 127.0.0.1:5000;
        server 127.0.0.1:5001;
    }

    server {
        server_name  example.com;

        access_log  /home/example/env/access.log;

        location / {
            proxy_set_header        Host $host;
            proxy_set_header        X-Real-IP $remote_addr;
            proxy_set_header        X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header        X-Forwarded-Proto $scheme;

            client_max_body_size    10m;
            client_body_buffer_size 128k;
            proxy_connect_timeout   60s;
            proxy_send_timeout      90s;
            proxy_read_timeout      90s;
            proxy_buffering         off;
            proxy_temp_file_write_size 64k;
            proxy_pass http://myapp-site;
            proxy_redirect          off;
        }
    }

.. note:: myapp.conf is actually included into the ``http {}`` section of the
    main nginx.conf file.

The ``upstream`` directive sets up a round-robin load-balancer between two
processes. The proxy is then configured to pass requests through the balancer
with the ``proxy_pass`` directive. It's important to investigate the
implications of many of the other settings as they are likely
application-specific.

The ``header`` directives inform our application of the exact deployment
setup. They will help the WSGI server configure our environment's
``SCRIPT_NAME``, ``HTTP_HOST``, and the actual IP address of the client.

Step 2: Starting Paster
=======================

.. warning:: Be sure to create a ``production.ini`` file to use for
    deployment that has debugging turned off, including removing the
    ``WebError#evalerror`` middleware.

WebError provides a production version of the debugging middleware that can be
used instead of ``WebError#evalerror``. This is important because with
``evalerror`` users would be able to execute arbitrary python code on your
system whenever an exception occurred.

This configuration uses PasteDeploy's ``PrefixMiddleware`` to automatically
convert the ``X-Forwarded-Proto`` into the correct HTTP scheme in the WSGI
environment. This is important so that the URLs generated by the application
can distinguish between different domains, HTTP vs. HTTPS, and with some
extra configuration to the ``paste_prefix`` filter it can even handle
hosting the application under a different URL than ``/``.

.. code-block:: ini
    :linenos:

    #---------- App Configuration ----------
    [app:myapp]
    use = egg:myapp#main
    reload_templates = false
    debug_authorization = false
    debug_notfound = false
    debug_templates = false
    default_locale_name = en

    #---------- Pipeline Configuration ----------
    [filter:paste_prefix]
    use = egg:PasteDeploy#prefix

    [filter:weberror]
    use = egg:WebError#error_catcher
    debug = false
    error_email = support@example.com
    from_address = paster@example.com

    [pipeline:main]
    pipeline =
        paste_prefix
        weberror
        myapp

    #---------- Server Configuration ----------
    [server:main]
    host = 127.0.0.1
    port = %(http_port)s

    use = egg:PasteScript#cherrypy
    numthreads = 10
    timeout = 180
    request_queue_size = 200

    #---------- Logging Configuration ----------
    # ...

Running the paster processes::

    paster serve --daemon --pid-file=paster_5000.pid production.ini http_port=5000
    paster serve --daemon --pid-file=paster_5001.pid production.ini http_port=5001

Step 3: Serving Static Files with Nginx (Optional)
==================================================

Assuming your static files are in a subdirectory of your pyramid application,
they can be easily served using nginx's highly optimized web server. This will
greatly improve performance because requests for this content will not need to
be proxied to your WSGI application and can be served directly.

.. warning:: This is only a good idea if your static content is intended
    to be public. It will not respect any view permissions you've placed on
    this directory.

.. code-block:: ini
    :linenos:

    ...

    location / {
        # all of your proxy configuration
    }

    location /static {
        root                    /home/example/myapp/myapp;
        expires                 30d;
        add_header              Cache-Control public;
        access_log              off;
    }

It's somewhat odd that the ``root`` doesn't point to the ``static`` directory,
but it works because Nginx will append the actual URL to the specified path.

Step 4: Managing Your Paster Processes with Supervisord (Optional)
==================================================================

Turning on all of your ``paster`` processes manually and daemonizing them
works for the simplest setups, but for a really robust server, you're going
to want to automate the startup and shutdown of those processes, as well as
have some way of managing failures.

Enter ``supervisord``::

    pip install supervisord

This is a great program that will manage arbitrary processes, restarting them
when they fail, providing hooks for sending emails, etc when things change,
and even exposing and XML-RPC interface for determining the status of your
system.

Below is an example configuration that starts up two instances of the paster
process, automatically filling in the ``http_port`` based on the
``process_num``, thus 5000 and 5001.

This is just a stripped down version of ``supervisord.conf``, read the docs
for a full breakdown of all of the great options provided.

.. code-block:: ini
    :linenos:

    [unix_http_server]
    file=%(here)s/env/supervisor.sock

    [supervisord]
    pidfile=%(here)s/env/supervisord.pid
    logfile=%(here)s/env/supervisord.log
    logfile_maxbytes=50MB
    logfile_backups=10
    loglevel=info
    nodaemon=false
    minfds=1024
    minprocs=200

    [rpcinterface:supervisor]
    supervisor.rpcinterface_factory = supervisor.rpcinterface:make_main_rpcinterface

    [supervisorctl]
    serverurl=unix://%(here)s/env/supervisor.sock

    [program:myapp]
    command=%(here)s/env/bin/paster serve %(here)s/production.ini http_port=50%(process_num)02d
    process_name=%(program_name)s-%(process_num)01d
    numprocs=2
    numprocs_start=0
    redirect_stderr=true
    stdout_logfile=%(here)s/env/%(program_name)s-%(process_num)01d.log

Apach + mod_wsgi
++++++++++++++++

`Pyramid mod_wsgi tutorial <http://docs.pylonsproject.org/projects/pyramid/1.0/tutorials/modwsgi/index.html>`_

gevent + pyramid_socketio
+++++++++++++++++++++++++

TODO - where's our long polling/websockets demo???

heroku
++++++

`heroku <http://www.heroku.com/>`_ recently added `support for a process model
<http://blog.heroku.com/archives/2011/5/31/celadon_cedar/>`_ which allows
deployment of Pyramid applications. While there is currently **no official
support** for Python/Pyramid web applications, the current stack does support
it.

This recipe assumes that you have a pyramid app setup using a Paste INI file,
inside a package called 'myapp'. This type of structure is found in the
pyramid_starter scaffold, and other Paste scaffolds (previously called project
templates). It can be easily modified to work with other Python web
applications as well by changing the command to run the app as appropriate.

Step 0: Install heroku
======================

Install the heroku gem `per their instructions
<http://devcenter.heroku.com/articles/quickstart>`_.

Step 1: Add files needed for heroku
===================================

You will need to add the following files with the contents as shown to the
root of your project directory (the directory containing the setup.py).

``requirements.txt``:

.. code-block:: text
    
    Pyramid==1.0
    # Add any other dependencies that should be installed as well

``Procfile``:

.. code-block:: text
    
    web: ./run

``run``:

.. code-block:: text
    
    #!/bin/bash
    bin/python setup.py develop
    bin/python runapp.py

.. note::
    
    Make sure to ``chmod +x run`` before continuing.
    The 'develop' step is necessary because the current package must be
    installed before paste can load it from the INI file.

``runapp.py``::
    
    import os

    from paste.deploy import loadapp
    from paste.script.cherrypy_server import cpwsgi_server

    if __name__ == "__main__":
        port = int(os.environ.get("PORT", 5000))
        wsgi_app = loadapp('config:production.ini', relative_to='.')
        cpwsgi_server(wsgi_app, host='0.0.0.0', port=port,
                      numthreads=10, request_queue_size=200)

.. note::
    
    This assumes the INI file to use is ``production.ini``, change as
    necessary. The server section of the INI will be ignored as the server
    needs to listen on the port supplied in the OS environ.

Step 2: Setup git repo and heroku app
=====================================

Inside your projects directory, if this project is not tracked under git, run:

.. code-block:: bash
    
    $ git init
    $ git add .
    $ git commit -m init

Next, initialize the heroku stack:

.. code-block:: bash
    
    $ heroku create --stack cedar

Step 3: Deploy
==============

To deploy a new version, push it to heroku:

.. code-block:: bash
    
    $ git push heroku master

If your app is not up and running, take a look at the logs:

.. code-block:: bash
    
    $ heroku logs

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
