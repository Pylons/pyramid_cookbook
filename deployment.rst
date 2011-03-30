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

*** Important *** Be sure to create a ``production.ini`` file to use for
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

    paster serve --daemon production.ini http_port=5000
    paster serve --daemon production.ini http_port=5001

Step 3: Serving Static Files with Nginx (Optional)
==================================================

Assuming your static files are in a subdirectory of your pyramid application,
they can be easily served using nginx's highly optimized web server. This will
greatly improve performance because requests for this content will not need to
be proxied to your WSGI application and can be served directly.

*** Important *** This is only a good idea if your static content is intended
to be public. It will not respect any view permissions you've placed on this
directory.

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
    command=%(here)s/env/bin/paster serve %(here)s/production.ini http_port=50%(process_num)01d
    process_name=%(program_name)s-%(process_num)01d
    numprocs=2
    numprocs_start=0
    redirect_stderr=true
    stdout_logfile=%(here)s/env/%(program_name)s-%(process_num)01d.log

Apach + mod_wsgi
++++++++++++++++

TODO

gevent + pyramid_socketio
+++++++++++++++++++++++++

TODO - where's our long polling/websockets demo???
