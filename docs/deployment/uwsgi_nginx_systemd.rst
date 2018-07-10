uWSGI + Nginx + systemd
+++++++++++++++++++++++

Below you can find (almost) production ready configuration. Almost, because some `uwsgi` params might need tweaking to fit your needs/resources.

An example systemd configuration file is shown here:

.. code-block:: text
    :linenos:

    # /etc/systemd/system/pyramid.service

    [Unit]
    Description=pyramid app

    # Requirements
    Requires=network.target

    # Dependency ordering
    After=network.target

    [Service]
    TimeoutStartSec=0
    RestartSec=10
    Restart=always

    # path to app
    WorkingDirectory=/opt/env/wiki
    # the user that you want to run app by
    User=app

    KillSignal=SIGQUIT
    Type=notify
    NotifyAccess=all

    # Main process
    ExecStartPre=/bin/mkdir -p /tmp/pyramid
    ExecStartPre=/bin/chown app:app /tmp/pyramid
    ExecStart=/opt/env/bin/uwsgi \
      --ini-paste-logged /opt/env/wiki/development.ini \
      -s /tmp/pyramid/uwsgi.sock \
      --chmod-socket=666 \
      --protocol=http

    [Install]
    WantedBy=multi-user.target

Save the file, run 

.. code-block:: bash
    
    systemctl enable pyramid.service
    systemctl start pyramid.service

Validate, if `/tmp/pyramid` directory was created and contains `uwsgi.sock`.

Few handy commands:

.. code-block:: bash

    systemctl restart pyramid.service # restarts app
    journalctl -fu pyramid.service # tail logs

Next we need to configure vhost in nginx. Below you can find example config:

.. code-block:: nginx
    :linenos:

    # myapp.conf

    upstream pyramid {
        server unix:///tmp/pyramid/uwsgi.sock;
    }

    server {
        listen 80;
    
        # optional ssl configuration
        
        listen 443 ssl;
        ssl_certificate /path/to/ssl/pem_file;
        ssl_certificate_key /path/to/ssl/certificate_key;
        
        # end of optional ssl configuration
    
        server_name  example.com;

        access_log  /opt/env/access.log;

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
            proxy_pass http://pyramid;
            proxy_redirect          off;
        }
    }

Better explanation for some of those nginx directives can be found on page :doc:`Nginx + pserve + supervisord <nginx>`.

