Nginx + pserve + supervisord
++++++++++++++++++++++++++++

This setup can be accomplished simply and is capable of serving a large amount
of traffic. The advantage in deployment is that by using ``pserve``, it is not
unlike the basic development environment you're probably using on your local
machine.

`Nginx <http://wiki.nginx.org/Main>`_ is a highly optimized HTTP server, very
capable of serving
static content as well as acting as a proxy between other applications and the
outside world. As a proxy, it also has good support for basic load balancing
between multiple instances of an application.

::

    Client <---> Nginx [0.0.0.0:80] <---> (static files)
                  /|\
                   |-------> WSGI App [localhost:5000]
                   `-------> WSGI App [localhost:5001]

Our target setup is going to be an Nginx server listening on port 80 and
load-balancing between 2 pserve processes. It will also serve the static files
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
        listen 80;
    
        # optional ssl configuration
        
        listen 443 ssl;
        ssl_certificate /path/to/ssl/pem_file;
        ssl_certificate_key /path/to/ssl/certificate_key;
        
        # end of optional ssl configuration
    
        server_name  example.com;

        access_log  /home/example/env/access.log;

        location / {
            proxy_set_header        Host $http_host;
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

.. note::

   myapp.conf is actually included into the ``http {}`` section of the
   main nginx.conf file.


The optional ``listen`` directive, as well as the 2 following lines,
are the only configuration changes required to enable SSL from the Client
to Nginx. You will need to have already created your SSL certificate and
key for this to work.  More details on this process can be found in
the `OpenSSL <http://www.openssl.org/docs/HOWTO/certificates.txt>`_ howto.
You will also need to update the paths that are shown to match the actual
path to your SSL certificates.


The ``upstream`` directive sets up a round-robin load-balancer between two
processes. The proxy is then configured to pass requests through the balancer
with the ``proxy_pass`` directive. It's important to investigate the
implications of many of the other settings as they are likely
application-specific.

The ``header`` directives inform our application of the exact deployment
setup. They will help the WSGI server configure our environment's
``SCRIPT_NAME``, ``HTTP_HOST``, and the actual IP address of the client.

Step 2: Starting pserve
=======================

.. warning::

   Be sure to create a ``production.ini`` file to use for
   deployment that has debugging turned off and removing the
   pyramid_debugtoolbar.

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
    pyramid.reload_templates = false
    pyramid.debug_authorization = false
    pyramid.debug_notfound = false
    pyramid.default_locale_name = en

    #---------- Pipeline Configuration ----------
    [filter:paste_prefix]
    use = egg:PasteDeploy#prefix

    [pipeline:main]
    pipeline =
        paste_prefix
        # a good spot for some logging middleware!
        myapp

    #---------- Server Configuration ----------
    [server:main]
    use = egg:waitress#main
    host = 127.0.0.1
    port = %(http_port)s

    #---------- Logging Configuration ----------
    # ...

Running the pserve processes::

    pserve --daemon --pid-file=pserve_5000.pid production.ini http_port=5000
    pserve --daemon --pid-file=pserve_5001.pid production.ini http_port=5001

Step 3: Serving Static Files with Nginx (Optional)
==================================================

Assuming your static files are in a subdirectory of your pyramid application,
they can be easily served using nginx's highly optimized web server. This will
greatly improve performance because requests for this content will not need to
be proxied to your WSGI application and can be served directly.

.. warning::

   This is only a good idea if your static content is intended
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

Step 4: Managing Your pserve Processes with Supervisord (Optional)
==================================================================

Turning on all of your ``pserve`` processes manually and daemonizing them
works for the simplest setups, but for a really robust server, you're going
to want to automate the startup and shutdown of those processes, as well as
have some way of managing failures.

Enter ``supervisord``::

    pip install supervisor

This is a great program that will manage arbitrary processes, restarting them
when they fail, providing hooks for sending emails, etc when things change,
and even exposing an XML-RPC interface for determining the status of your
system.

Below is an example configuration that starts up two instances of the pserve
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
    autorestart=true
    command=%(here)s/env/bin/pserve %(here)s/production.ini http_port=50%(process_num)02d
    process_name=%(program_name)s-%(process_num)01d
    numprocs=2
    numprocs_start=0
    redirect_stderr=true
    stdout_logfile=%(here)s/env/%(program_name)s-%(process_num)01d.log
