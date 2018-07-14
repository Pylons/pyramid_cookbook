.. _uwsgi_tutorial:

Running a Cookiecutter :app:`Pyramid` Application under :app:`uWSGI` and :app:`Nginx`
=====================================================================================

``uWSGI`` is a software application for building hosting services.
It is named after the Web Server Gateway Interface (the WSGI specification
to which many Python web frameworks conform).

This guide will outline broad steps that can be used to get a Cookiecutter
:app:`Pyramid` application running under Nginx via ``uWSGI``.  This particular
tutorial was developed under Ubuntu 18.04, but the instructions should be
largely the same for all systems, delta specific path information for commands
and files.


#.  Install prerequisites

    .. code-block:: bash

        $ sudo apt install -y uwsgi-core uwsgi-plugin-python3 python3-cookiecutter \
                              python3-pip python3-venv nginx

#.  Create a :app:`Pyramid` application. For this tutorial we'll use the
    ``starter`` :term:`cookiecutter`. See :ref:`pyramid:project_narr` for more
    in-depth information about creating a new project.

    .. code-block:: bash

        $ cd
        $ python3 -m cookiecutter gh:Pylons/pyramid-cookiecutter-starter

    If prompted for the first item, accept the default ``yes`` by hitting return.

    .. code-block:: text

        You've cloned ~/.cookiecutters/pyramid-cookiecutter-starter before.
        Is it okay to delete and re-clone it? [yes]: yes
        project_name [Pyramid Scaffold]: myproject
        repo_name [myproject]: myproject
        Select template_language:
        1 - jinja2
        2 - chameleon
        3 - mako
        Choose from 1, 2, 3 [1]: 1

#.  Create a :term:`virtual environment` which we'll use to install our
    application.

    .. code-block:: bash

        $ cd myproject
        $ python3 -m venv env

#.  Install your :app:`Pyramid` application and its dependencies.

    .. code-block:: bash

        $ env/bin/pip install -e ".[testing]"

#.  Within the project directory (``~/myproject``), create a script
    named ``wsgi.py``.  Give it these contents:

    .. code-block:: python

        # Adapted from PServeCommand.run in site-packages/pyramid/scripts/pserve.py
        from pyramid.scripts.common import get_config_loader
        app_name    = 'main'
        config_vars = {}
        config_uri  = 'production.ini'

        loader = get_config_loader(config_uri)
        loader.setup_logging(config_vars)
        app = loader.get_wsgi_app(app_name, config_vars)

    ``config_uri`` is the project configuration file name.  It's best to use
    the ``production.ini`` file provided by your cookiecutter, as it contains
    settings appropriate for production.  ``app_name`` is the name of the section
    within the ``.ini`` file that should be loaded by ``uWSGI``.  The
    assignment to the name ``app`` is important: we will reference ``app`` and
    the name of the file, ``wsgi`` when we invoke uWSGI.

    The call to ``loader.setup_logging`` initializes the standard library's
    :mod:`python3:logging` module through :func:`pyramid.paster.setup_logging`
    to allow logging within your application. See
    :ref:`pyramid:logging_config`.

#.  Create a new directory at ``~/myproject/tmp`` to house a pidfile and a unix
    socket.  However, you'll need to make sure that *two* users have access to
    change into the ``~/myproject/tmp`` directory: your current user (mine is
    ``ubuntu`` and the user that Nginx will run as often named ``www-data`` or
    ``nginx``).

#.  Invoke uWSGI.

    .. code-block:: bash

        cd ~/myproject
        sudo uwsgi \
          --chmod-socket=020 \
          --enable-threads \
          --plugin=python3 \
          --socket ~/myproject/tmp/myproject.sock \
          --manage-script-name \
          --mount /=wsgi:app \
          --uid ubuntu \
          --gid www-data \
          --virtualenv env

        # Explanation of Options
        # sudo uwsgi                          # Invoke as sudo so you can masquerade
        #                                       as the users specfied in --uid and --gid
        #
        # --chmod-socket=020                  # Change permissions on socket to
        #                                       at least 020 so that in combination
        #                                       with "--gid www-data", Nginx will be able
        #                                       to write to it after  uWSGI creates it
        #
        # --enable-threads                    # Execute threads that are in your app
        #
        # --plugin=python3                    # Use the python3 plugin
        #
        # --socket ~/myproject/tmp/myproject.sock   # Where to put the unix socket
        #
        # --manage-script-name
        #
        # --mount /=wsgi:app                  # Mount the path "/" on the symbol
        #                                       "app" found in the file wsgi.py
        #
        # --uid ubuntu                        # masquerade as the ubuntu user
        #
        # --gid www-data                      # masquerade as the www-data group
        #
        # --virtualenv env                    # Use packages installed in your venv

#.  Verify that the output of the previous step includes a line that looks approximately like this:

    .. code-block:: bash

        WSGI app 0 (mountpoint='/') ready in 1 seconds on interpreter 0x5615894a69a0 pid: 8827 (default app)

    If any errors occurred, you will need to correct them. If you get a
    ``callable not found or import error``, make sure your 
    ``--mount /=wsgi:app`` matches the ``app`` symbol in the ``wsgi.py`` file.
    An import error that looks like ``ImportError: No module named 'wsgi'``
    probably indicates a mismatch in your --mount arguments. Any other import
    errors probably means that the package it's failing to import either is not
    installed or is not accessible by the user. That's why we chose to
    masquerade as the normal user that you log in as, so you would for sure
    have access to installed packages.

#.  Add a new file at ``/etc/nginx/sites-enabled/myproject.conf`` with
    the following contents. Also change any occurrences of the word ``ubuntu``
    to your actual username.

    .. code-block:: nginx

      server{
        server_name _;

        root /home/ubuntu/myproject/;

        location /  {
          include uwsgi_params;
          # The socket location must match that used by uWSGI
          uwsgi_pass unix:/home/ubuntu/myproject/tmp/myproject.sock;
        }

      }


#.  If there is a file that is at /var/nginx/sites-enabled/default,
    remove it so your new nginx config file will catch all traffic.
    (If ``default`` is in use and important, simply add a real
    ``server_name`` to ``/etc/nginx/sites-enabled/myproject.conf``
    to disambiguate them.

#.  Reload Nginx

    .. code-block:: bash

       $ sudo nginx -s reload

#.  Visit http://localhost in a browser. Alternatively, call ``curl localhost``
    from a terminal.  You should see the sample application rendered.

#.  If the app does not render, tail the nginx logs, then
    refresh the browser window (or call ``curl localhost``) again to determine
    the cause. (uWSGI should still be running in a separate terminal window.)

    .. code-block:: bash

      $ cd /var/log/nginx
      $ tail -f error.log access.log

    If you see a ``No such file or directory`` error in the Nginx error log,
    verify the name of the socket file specified in
    ``/etc/nginx/sites-enabled/myproject.conf``.  Verify that the file
    reference there actually exists. If it does not, check where uWSGI is set
    to put the socket and that it actually exists there.  Once both uWSGI and
    Nginx both point to the same file and both have access to its containing
    directory, you will be past this error.  If all else fails, put your
    sockets somewhere writable by all, such as ``/tmp``.

    If you see an ``upstream prematurely closed connection while reading
    response header from upstream`` error in the Nginx error log, something is wrong
    with your app or the way uWSGI is calling it. Check the output from the
    window where uWSGI is still running to see what error messages it gives.

    If you see a ``Connection refused`` error in the Nginx error log, check the
    permissions on the socket file that Nginx says it is attempting to connect
    to. The socket file is expected to be owned by the user ``ubuntu`` and the
    group ``www-data`` because those are the ``--uid`` and ``--gid`` options we
    specified when invoking uWSGI. If it is owned by a different user or group
    than these, correct your uWSGI invocation until these are correct. Next
    check permissions on the socket file. Permissions are expected to be
    ``020`` as set by your uWSGI invocation. The ``2`` in the middle of ``020``
    means group-writable, which is required because uWSGI first creates the
    socket file, then Nginx (running as the group ``www-data``) must have write
    permissions to it or it will not be able to connect. You can use
    permissions more open than ``020``, but in testing this tutorial ``020``
    was all that was required.




`uWSGI` has many knobs and a great variety of deployment modes. This
is just one representation of how you might use it to serve up a CookieCutter :app:`Pyramid`
application.  See the `uWSGI documentation
<https://uwsgi-docs.readthedocs.io/en/latest/>`_
for more in-depth configuration information.

This tutorial is modified from the `original tutorial for mod_wsgi <https://docs.pylonsproject.org/projects/pyramid/en/latest/tutorials/modwsgi/index.html>`_.
