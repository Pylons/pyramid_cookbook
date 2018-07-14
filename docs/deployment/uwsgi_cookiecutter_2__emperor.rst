.. _uwsgi_cookiecutter_part_2:

uWSGI with Cookiecutter :app:`Pyramid` App Part 2: Adding Emperor and systemd
=============================================================================

This guide will outline broad steps that can be used to add the
`uWSGI Emperor <https://uwsgi-docs.readthedocs.io/en/latest/Emperor.html>`_
and `systemd <https://en.wikipedia.org/wiki/Systemd>`_
to our Cookiecutter app that is being served by ``uWSGI``.

This is Part 2 of a 2-part tutorial, and assumes that you have already
completed part 1: :ref:`uwsgi_cookiecutter_part_1`.

This tutorial was developed under Ubuntu 18.04, but the instructions should be
largely the same for all systems, delta specific path information for commands
and files.

Conventional Invocation of uWSGI
--------------------------------

In Part 1 we used ``--init-paste-logged`` which got us two things almost
for free: logging and an implicit WSGI entry point.

In order to run our :term:`cookiecutter` app with the
`uWSGI Emperor <https://uwsgi-docs.readthedocs.io/en/latest/Emperor.html>`_,
we will need to follow the conventional route of providing an (explicit)
WSGI entry point.




#.  Within the project directory (``~/myproject``), create a script
    named ``wsgi.py``.  This script is our WSGI entry point. Give it these
    contents:

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
    assignment to the variable ``app`` is important: we will reference ``app`` and
    the name of the file, ``wsgi.py`` when we invoke uWSGI.

    The call to ``loader.setup_logging`` initializes the standard library's
    :mod:`python3:logging` module through :func:`pyramid.paster.setup_logging`
    to allow logging within your application. See
    :ref:`pyramid:logging_config`.



#.  Uncomment these three lines of your ``production.ini`` file

    .. code-block:: text

        [uwsgi]
        ...
        wsgi-file = wsgi.py                 # Used in part 2 of this tutorial
        callable = app                      # Used in part 2 of this tutorial
        logto = /var/log/uwsgi/%(proj).log  # Used in part 2 of this tutorial


    ``wsgi-file`` points to the explicit entry point that we created in the
    previous step. ``callable`` is the name of the callable symbol
    (the variable ``app``) exposed in wsgi.py. ``logto`` specifies
    where your apps logs will be written, which means logs will no longer be
    written to STDOUT.



#.  Invoke uWSGI with ``--ini``

    Invoking uWSGI with ``--ini`` and passing it an .ini file is the
    conventional way of invoking uWSGI. (uWSGI can also be invoked
    will all configuration options specified as command-line arguments,
    but that method does not lend itself to easy configuration with Emperor,
    so we will not present that method here.)


    .. code-block:: bash

        $ cd ~/myproject
        $ sudo uwsgi --ini production.ini

    Make sure you call it with ``sudo``, or it your app will not be
    able to masquerade as the users we specified for ``uid`` and ``gid``.

    Also note that since we specified the ``logto`` parameter to be in
    ``/var/log/uwsgi``, we will see only limited output in this terminal
    window. If it starts up correctly, all you will see is this:

    .. code-block:: bash

        $ sudo uwsgi --ini production.ini
        [uWSGI] getting INI configuration from production.ini



#.  Tail the log file at ``var/log/uwsgi/myproject.log``

    .. code-block:: bash

        $ tail -f /var/log/uwsgi/myproject.log

    and verify that the output of the previous step includes a line that looks
    approximately like this:

    .. code-block:: text

        WSGI app 0 (mountpoint='/') ready in 1 seconds on interpreter 0x5615894a69a0 pid: 8827 (default app)

    If any errors occurred, you will need to correct them. If you get a
    ``callable not found or import error``, make sure that your ``production.ini``
    properly sets ``wsgi-file`` to ``wsgi.py`` and that ``~/myproject/wsgi.py`` exists
    and contains the contents provided in a previous step. Also make sure that your
    ``production.ini`` properly sets ``callable`` to ``app`` and that ``app`` is
    the name of the callable symbol in wsgi.py.

    An import error that looks like ``ImportError: No module named 'wsgi'``
    probably indicates that your ``wsgi-file`` specified in ``production.ini``
    does not match the ``wsgi.py`` file that you actually created.

    Any other `import` errors probably mean that the package it's failing to
    import either is not installed or is not accessible by the user. That's why
    we chose to masquerade as the normal user that you log in as, so you would
    for sure have access to installed packages.


#.  Visit http://localhost in a browser. Alternatively, call ``curl localhost``
    from a terminal.  You should see the sample application rendered.

#.  If the app does not render, follow the same steps you followed in
    :ref:`uwsgi_cookiecutter_part_1` to get the Nginx connection flowing.


#.  Stop your application. Now that we've demonstrated that your app can run
    with an explicit WSGI entry point, your app is ready to be
    managed by the uWSGI Emperor.



Running Your App via the Emperor
--------------------------------


#.  Create two new directories in ``/etc``.

    .. code-block:: bash

        $ sudo mkdir /etc/uwsgi/
        $ sudo mkdir /etc/uwsgi/vassals

#.  Create an .ini file for the uWSGI emperor and place it in ``/etc/uwsgi/emperor.ini``

    .. code-block:: text

        # /etc/uwsgi/emperor.ini
        [uwsgi]
        emperor = /etc/uwsgi/vassals
        limit-as = 1024
        logto = /var/log/uwsgi/emperor.log

    Your app is going to run as a vassal.  The ``emperor`` line in
    ``emperor.ini`` specifies a directory where the Emperor will look for
    vassal config files. That is, any vassal config file (an .ini file) that
    appears in ``/etc/uwsgi/vassals``, the Emperor will attempt to start and manage
    that vassal.



#.  Invoke the uWSGI Emperor.

    .. code-block:: bash

        $ cd /etc/uwsgi
        $ sudo uwsgi --ini emperor.ini

    Since we specified ``logto`` in ``emperor.ini``, a successful start will only
    show you this output:

    .. code-block:: bash

        $ sudo uwsgi --ini emperor.ini
        [uWSGI] getting INI configuration from emperor.ini


#.  In a new terminal window, start tailing the emperor's log.

    .. code-block:: bash

        $ sudo tail -f /var/log/uwsgi/emperor.log

    Verify that you see this line in the emperor's output:

    .. code-block:: bash

        *** starting uWSGI Emperor ***

    Keep this window open so you can see new entries in the emperor's log
    during the next steps.

#.  From the vassals directory, create a symbolic link that points to your
    app's ``production.ini``.

    .. code-block:: bash

        $ cd /etc/uwsgi/vassals
        $ sudo ln -s ~/myproject/production.ini

    As soon as you create that symbolic link, you should see traffic in the
    emperor log that looks like this:

    .. code-block:: text

        [uWSGI] getting INI configuration from production.ini
        Sun Jul 15 13:34:15 2018 - [emperor] vassal production.ini has been spawned
        Sun Jul 15 13:34:15 2018 - [emperor] vassal production.ini is ready to accept requests




#.  Tail your vassal's log to be sure that it started correctly.

    .. code-block:: bash

        $ tail -f /var/log/uwsgi/myproject.log

    A line similar to this one indicates success:

    .. code-block:: text

        WSGI app 0 (mountpoint='') ready in 0 seconds on interpreter 0x563aa0193bf0 pid: 14984 (default app)

#.  Verify that your vassal is available via Nginx. As in Part 1, you can do this
    by opening http://localhost in a browser, or by curling localhost in a terminal
    window.

    .. code-block:: bash

        $ curl localhost

#.  Stop the uWSGI Emperor, as now we will start it via systemd.



Running the Emperor via systemd
-------------------------------

#.  Create a systemd unit file for the emperor with these contents,
    and place it in ``/lib/systemd/system/emperor.uwsgi.service``:

    .. code-block:: text

        # /lib/systemd/system/emperor.uwsgi.service
        [Unit]
        Description=uWSGI Emperor
        After=syslog.target

        [Service]
        ExecStart=/usr/bin/uwsgi --ini /etc/uwsgi/emperor.ini
        # Requires systemd version 211 or newer
        RuntimeDirectory=uwsgi
        Restart=always
        KillSignal=SIGQUIT
        Type=notify
        StandardError=syslog
        NotifyAccess=all

        [Install]
        WantedBy=multi-user.target


#.  Start and enable the systemd unit.

    .. code-block:: bash

        $ sudo systemctl start emperor.uwsgi.service
        $ sudo systemctl enable emperor.uwsgi.service

#.  Verify that the uWSGI Emperor is running, and that your app is running and
    available on localhost. Here are some commands that you can use to verify:

    .. code-block:: bash

        $ sudo journalctl -u emperor.uwsgi.service # System logs for emperor

        $ tail -f /var/log/nginx/access.log /var/log/nginx/error.log

        $ tail -f /var/log/uwsgi/myproject.log

        $ sudo tail -f /var/log/uwsgi/emperor.log

#.  Verify that the Emperor starts up when you reboot your machine.

    .. code-block:: bash

        $ sudo reboot

    After it reboots:

    .. code-block:: bash

        $ curl localhost

#.  Congratulations! You've just deployed your app in robust fashion.






`uWSGI` has many knobs and a great variety of deployment modes. This
is just one representation of how you might use it to serve up a CookieCutter :app:`Pyramid`
application.  See the `uWSGI documentation
<https://uwsgi-docs.readthedocs.io/en/latest/>`_
for more in-depth configuration information.

This tutorial is modified from the `original tutorial for mod_wsgi <https://docs.pylonsproject.org/projects/pyramid/en/latest/tutorials/modwsgi/index.html>`_.
