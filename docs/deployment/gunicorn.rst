********
gunicorn
********

The short story
===============
Running your pyramid based application with gunicorn can be as easy as:

.. code-block:: bash

    $ gunicorn --paste production.ini


The long story
==============
Similar to the ``pserve`` command that comes with Pyramid, gunicorn can also
directly use your project's INI files, such as ``production.ini``, to launch
your application. Just supply the ``--paste`` command line option together with
the path of your configuration file to the ``gunicorn`` command, and it will
try to load the app.

As documented in the section `Paster Applications
<http://docs.gunicorn.org/en/stable/configure.html#paster-applications>`_, you
may also add gunicorn specific settings to the ``[server:main]`` section of
your INI file.

The following configuration will cause gunicorn to listen on a unix socket, use
four workers, preload the application, reload it on file changes, output
accesslog lines to stderr and use the debug loglevel.

.. code-block:: ini

    [server:main]
    use = egg:gunicorn#main
    bind = unix:/var/run/app.sock
    workers = 4
    preload = true
    reload = true
    accesslog = -
    loglevel = debug

For all configuration options that may be used, have a look at the `available
settings <http://docs.gunicorn.org/en/stable/settings.html>`_.

Keep in mind that settings defined within a gunicorn configuration file or
command line arguments given to gunicorn take precedence over the settings
established within the INI file.

For all of this to work, the Python interpreter used by quicken also needs to
be able to load your application. In other words, gunicorn and your application
need to be installed and used inside the same ``virtualenv``.

Naturally, the ``paste`` option can also be combined with other gunicorn
options that might be applicable for your deployment situation. Also you might
want to put something like `nginx <https://www.nginx.com/resources/wiki/>`_ in
front of gunicorn and have gunicorn supervised by some process manager. Please
have a look at the `gunicorn website <http://gunicorn.org/>`_ and the `gunicorn
documentation on deployment <http://docs.gunicorn.org/en/latest/deploy.html>`_
for more information on those topics.
