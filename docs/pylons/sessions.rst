Sessions
++++++++

Pyramid uses Beaker sessions just like Pylons, but they're not enabled by
default. To use them you'll have to add the "pyramid_beaker" package as a
dependency, and put the following line in your ``main()`` function::

    config.include("pyramid_beaker")

(To add a dependency, put it in the ``requires`` list in setup.py, and
reinstall the application.)

The default configuration is in-memory sessions and (I think) no caching. You
can customize this by putting configuration settings in your INI file or in the
``settings`` dict at the beginning of the ``main()`` function (before the
Configurator is instantiated).  The Akhet Demo configures Beaker with the
following settings, borrowed from the Pylons configuration:

.. code-block:: ini

    # Beaker cache
    cache.regions = default_term, second, short_term, long_term
    cache.type = memory
    cache.second.expire = 1
    cache.short_term.expire = 60
    cache.default_term.expire = 300
    cache.long_term.expire = 3600

    # Beaker sessions
    #session.type = file
    #session.data_dir = %(here)s/data/sessions/data
    #session.lock_dir = %(here)s/data/sessions/lock
    session.type = memory
    session.key = akhet_demo
    session.secret = 0cb243f53ad865a0f70099c0414ffe9cfcfe03ac

To use file-based sessions like in Pylons, uncomment the first three session
settings and comment out the "session.type = memory" line.

You should set the "session.secret=" setting to a random string. It's used to
digitally sign the session cookie to prevent session hijacking.

Beaker has several persistence backends available, including memory, files,
SQLAlchemy, memcached, and cookies (which stores each session variable in a
client-side cookie, and has size limitationss). The most popular
deployment backend nowadays is memcached, which can act as a shared storage
between several processes and servers, thus providing the speed of memory with
the ability to scale to a multi-server cluster. Pylons defaults to disk-based
sessions.

Beaker plugs into Pyramid's built-in session interface, which is accessed via
``request.session``.  Use it like a dict. Unlike raw Beaker sessions, you don't
have to call ``session.save()`` every time you change something, but you should
call ``session.changed()`` if you've modified a *mutable* item in the session;
e.g., ``session["mylist"].append(1)``.

The Pyramid session interface also has some extra features. It can store a set
of "flash messages" to display on the next page view, which is useful when you
want to push a success/failure message and redirect, and the message will be
displayed on the target page. It's based on ``webhelpers.flash``, which is
incompatible with Pyramid because it depends on Pylons' magic globals. There
are also methods to set a secure form token, which prevent form submissions
that didn't come from a form requested earlier in the session (and thus may be
a cross-site forgery attack).  (Note: flash messages are not related to the Adobe
Flash movie player.)

See the :ref:`sessions_chapter` chapter in the Pyramid manual for the API of
all these features and other features.  The Beaker_ manual will help you
configure a backend. The Akhet_ Demo is an example of using Pyramid with
Beaker, and has flash messages.

*Note:* I sometimes get an exception in the debug toolbar when sessions are
enabled.  They may be a code discrepency between the distributions. If this
happens to you, you can disable the toolbar until the problem is fixed.


.. include:: ../links.rst
