********
gunicorn
********

The short story
===============
Running your pyramid based application with gunicorn can be as easy as::

    gunicorn --paste production.ini


The long story
==============
Similar to the ``pserve`` command that comes with pyramid, gunicorn can also
use your projects' INI files (such as ``production.ini``) directly to launch
your application.
Just supply the ``--paste`` command line option together with the path of your
configuration file to the ``gunicorn`` command and it will try to load the app
in question.

For this to work, the Python interpreter used by gunicorn also needs to be able
to load your application (e.g. gunicorn and your application need to be
installed and used inside the same ``virtualenv``).

Naturally, the paste option can also be combined with other gunicorn options
that might be applicable for your deployment situation. Also, you might want to
put something like `nginx <https://www.nginx.com/resources/wiki/>`_ in front of
gunicorn and have gunicorn supervised by some process manager.
Please have a look at the `gunicorn website <http://gunicorn.org/>`_ and the
`gunicorn documentation on deployment
<http://docs.gunicorn.org/en/latest/deploy.html>`_ for more information on
those topics.
