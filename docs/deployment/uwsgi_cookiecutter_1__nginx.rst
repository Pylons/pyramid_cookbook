.. _uwsgi_cookiecutter_part_1:

uWSGI with Cookiecutter :app:`Pyramid` App Part 1: Basic uWSGI + :app:`Nginx`
=============================================================================

``uWSGI`` is a software application for building hosting services.
It is named after the Web Server Gateway Interface (the `WSGI <https://wsgi.readthedocs.io/en/latest/>`_ specification
to which many Python web frameworks conform).

This guide will outline broad steps that can be used to get a Cookiecutter
:app:`Pyramid` application running under under ``uWSGI`` and Nginx.  This particular
tutorial was developed and tested on Ubuntu 18.04, but the instructions should be
largely the same for all systems, delta specific path information for commands
and files.

.. note::

    For those of you with your hearts set on running your pyramid
    application under uWSGI, this be your guide.

    However, if you are simply looking for a decent-performing
    production-grade server with auto-start capability, waitress + Systemd
    has a much gentler learning curve.

With that said, let's begin.


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


#.  Create a new directory at ``~/myproject/tmp`` to house a pidfile and a unix
    socket.  However, you'll need to make sure that *two* users have access to
    change into the ``~/myproject/tmp`` directory: your current user (mine is
    ``ubuntu`` and the user that Nginx will run as often named ``www-data`` or
    ``nginx``).

#.  Add a ``[uwsgi]`` section to ``production.ini``. Here are the lines
    to include:

    .. code-block:: text

        [uwsgi]
        proj = myproject
        chdir = /home/ubuntu/%(proj)
        processes = 2
        threads = 2
        offload-threads = 2
        stats =  127.0.0.1:9191
        max-requests = 5000
        master = True
        vacuum = True
        enable-threads = true
        harakiri = 60
        chmod-socket = 020
        plugin = python3
        pidfile=%(chdir)/tmp/%(proj).pid
        socket = %(chdir)/tmp/%(proj).sock
        virtualenv = %(chdir)/env
        uid = ubuntu
        gid = www-data
        #wsgi-file = wsgi.py                 # Used in part 2 of this tutorial
        #callable = app                      # Used in part 2 of this tutorial
        #logto = /var/log/uwsgi/%(proj).log  # Used in part 2 of this tutorial

    And here is an explanation of the salient options:

    .. code-block:: text

        # Explanation of Options
        #
        # proj = myproject                    # Set a variable named "proj"
        #                                       so we can use it elsewhere in this
        #                                       block of config
        #
        # chmod-socket = 020                  # Change permissions on socket to
        #                                       at least 020 so that in combination
        #                                       with "--gid www-data", Nginx will be able
        #                                       to write to it after  uWSGI creates it
        #
        # enable-threads                      # Execute threads that are in your app
        #
        # plugin = python3                    # Use the python3 plugin
        #
        # socket = %(chdir)/tmp/%(proj).sock  # Where to put the unix socket
        # pidfile=%(chdir)/tmp/%(proj).pid    # Where to put PID file
        #
        # uid = ubuntu                        # Masquerade as the ubuntu user
        #                                       This grants you permissions to use
        #                                       python packages installed in your
        #                                       home directory
        #
        # gid = www-data                      # Masquerade as the www-data group
        #                                       This makes it easy to allow Nginx
        #                                       (which runs as the www-data group)
        #                                       access to the socket file.
        #
        # virtualenv = (chdir)/env            # Use packages installed in your venv





#.  Invoke uWSGI with ``--ini-paste-logged``.

    There are multiple ways to invoke uWSGI. Using ``--ini-paste-logged``
    is the easiest, as it does not require an explicit entry point.

    .. code-block:: bash

        $ cd ~/myproject
        $ sudo uwsgi --plugin python3 --ini-paste-logged production.ini

        # Explanation of Options
        #
        # sudo uwsgi                          # Invoke as sudo so you can masquerade
        #                                       as the users specfied by `uid` and `gid`
        #
        # --plugin=python3                    # Use the python3 plugin
        #
        # --ini-paste-logged                  # Implicitly defines a wsgi entry point
        #                                       so that you don' have to.
        #                                       Also enables logging




#.  Verify that the output of the previous step includes a line that looks
    approximately like this:


    .. code-block:: bash

        WSGI app 0 (mountpoint='/') ready in 1 seconds on interpreter 0x5615894a69a0 pid: 8827 (default app)



    If any errors occurred, you will need to correct them. If you get a
    ``uwsgi: unrecognized option '--ini-paste-logged'``, may sure you are
    specifying the python3 plugin.

    If you get an error like this:

    .. code-block:: text

        Fatal Python error: Py_Initialize: Unable to get the locale encoding
        ModuleNotFoundError: No module named 'encodings'

    check that the ``virtualenv`` option in the [uwsgi] section of your
    .ini file points to the correct directory. Specifically, it should
    end in ``env``, not ``bin``.

    Any import errors probably means that the package it's failing to
    import either is not installed or is not accessible by the user. That's why
    we chose to masquerade as the normal user that you log in as, so you would
    for sure have access to installed packages.

    If you get almost no output at all, yet the process still appears to
    be running, make sure that ``logto`` is commented out in ``production.ini``.

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


#.  If there is a file at /var/nginx/sites-enabled/default,
    remove it so your new nginx config file will catch all traffic.
    (If ``default`` is in use and important, simply add a real
    ``server_name`` to ``/etc/nginx/sites-enabled/myproject.conf``
    to disambiguate them.)

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
    referenced there actually exists. If it does not, check what location is
    specified for ``socket`` in your .ini file, and verify that the
    specified file actually exists.  Once both uWSGI and Nginx both point to the
    same file and both have access to its containing directory, you will be
    past this error.  If all else fails, put your sockets somewhere writable by
    all, such as ``/tmp``.

    If you see an ``upstream prematurely closed connection while reading
    response header from upstream`` error in the Nginx error log, something is wrong
    with your app or the way uWSGI is calling it. Check the output from the
    window where uWSGI is still running to see what error messages it gives
    when you ``curl localhost``.

    If you see a ``Connection refused`` error in the Nginx error log, check the
    permissions on the socket file that Nginx says it is attempting to connect
    to. The socket file is expected to be owned by the user ``ubuntu`` and the
    group ``www-data`` because those are the ``uid`` and ``gid`` options we
    specified in the .ini file. If the socket file is owned by a different
    user or group than these, correct the uWSGI parameters in your .ini file
    until these are correct.

    If you are still getting a ``Connection refused`` error in the Nginx error log,
    check permissions on the socket file. Permissions are expected to be
    ``020`` as set by your .ini file. The ``2`` in the middle of ``020``
    means group-writable, which is required because uWSGI first creates the
    socket file, then Nginx (running as the group ``www-data``) must have write
    permissions to it or it will not be able to connect. You can use
    permissions more open than ``020``, but in testing this tutorial ``020``
    was all that was required.


#.  Once your app is accessible via Nginx, you have cause to celebrate.

    If you wish to also add the
    `uWSGI Emperor <https://uwsgi-docs.readthedocs.io/en/latest/Emperor.html>`_
    and `Systemd <https://en.wikipedia.org/wiki/Systemd>`_ to the mix, proceed
    to part 2 of this tutorial: :ref:`uwsgi_cookiecutter_part_2`.


`uWSGI` has many knobs and a great variety of deployment modes. This
is just one representation of how you might use it to serve up a CookieCutter :app:`Pyramid`
application.  See the `uWSGI documentation
<https://uwsgi-docs.readthedocs.io/en/latest/>`_
for more in-depth configuration information.

This tutorial is modified from the `original tutorial for mod_wsgi <https://docs.pylonsproject.org/projects/pyramid/en/latest/tutorials/modwsgi/index.html>`_.
