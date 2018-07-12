Forked and Threaded Servers
+++++++++++++++++++++++++++

Forked and threaded servers share common "gotchas" and solutions when
using Pyramid and some popular packages.

Forked and threaded servers tend to use a "copy on write" implementation detail
to optimize how they work and share memory. This can create problems when
certain actions happen before the fork or thread dispatch, such as when files or
file-descriptors are opened or random number generators are initialized.

Many servers have built-in hooks or events which allow you to easily handle
these situations.


Servers
=======

The following servers are known to have built-in hooks or events to handle
problems arising from "copy on write" issues. This listing is not complete; an
omission from the below does not suggest a given server is immune from these
issues or that a server does not offer the necessary hooks/events.


Gunicorn
--------

Gunicorn offers several hooks during an application lifecycle.

The postfork routine is provided as a function in a configuration python script.

For example a script ``config.py`` might look like the following.

.. code-block:: python

    def post_fork(server, worker):
        log.debug("gunicorn - post_fork")

Invoking the script would look like the following.

.. code-block:: bash

    gunicorn --paste production.ini -c config.py

See `documentation for the post_fork hook <http://docs.gunicorn.org/en/latest/settings.html#post-fork>`_.


uWSGI
-----

uWSGI offers a decorator to handle forking.

Your application should include code like the following.

.. code-block:: python

    from uwsgidecorators import postfork
    
    @postfork
    def my_setup():
        log.debug("uwsgi - postfork")

See `documentation for the postfork decorator <https://uwsgi-docs.readthedocs.io/en/latest/PythonDecorators.html#uwsgidecorators.postfork>`_.


Waitress
--------

Waitress is not a forking server, but its threads can create issues similar to
those of forking servers.


Known Packages
==============

The following packages are known to have potential issues when deploying on 
forked or threaded servers.  This listing is not complete; an omission from the
below does not suggest a given package is immune from these types of deployment
concerns.


SQLAlchemy
----------

Many people use SQLAlchemy as part of their Pyramid application stack.

The database connections and the connection pools in SQLAlchemy are not safe to
share across process boundaries (forks or threads). The connections and 
connection pools are lazily created on their first use, so most Pyramid users 
will not encounter an issue as database interaction usually happens on a 
per-request basis.

If your Pyramid application connects to a database during the application
startup however, then you must use ``Engine.dispose`` to reset the connections.
It would look like the following.

.. code-block:: python

    @postfork
    def reset_sqlalchemy():
        models.engine.dispose()

Additional documentation on this topic is available from SQLAlchemy's documentation.

* `Using Connection Pools with Multiprocessing <https://docs.sqlalchemy.org/en/latest/core/pooling.html#using-connection-pools-with-multiprocessing>`_
* `Engine Disposal <https://docs.sqlalchemy.org/en/latest/core/connections.html#engine-disposal>`_


PyCrypto
--------

The `PyCrypto <https://www.dlitz.net/software/pycrypto/>`_ library provides for
a ``Crypto.Random.atfork`` function to reseed the pseudo-random number generator
when a process forks.

