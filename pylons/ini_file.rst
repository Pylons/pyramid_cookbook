INI File
++++++++

The "[app:main]" section in Pyramid apps has different options than its Pylons
counterpart. Here's what it looks like in Pyramid's "alchemy" scaffold:

.. code-block:: ini

    [app:main]
    use = egg:{{project}}

    pyramid.reload_templates = true
    pyramid.debug_authorization = false
    pyramid.debug_notfound = false
    pyramid.debug_routematch = false
    pyramid.debug_templates = true
    pyramid.default_locale_name = en
    pyramid.includes =
        pyramid_debugtoolbar
        pyramid_tm

    sqlalchemy.url = sqlite:///%(here)s/{{project}}.db

The "pyramid.includes=" variable lists a number of "tweens" to activate. A
tween is like a WSGI middleware but specific to Pyramid.  "pyramid_debugtoolbar"
is the debug toolbar; it provides information on the request variables and
runtime state on every page.

"pyramid_tm" is a transaction manager. This has no equivalent in Pylons but is
used in TurboGears and BFG. It provides a request-wide transaction that manages
your SQLAlchemy session(s) and potentially other kinds of transactions like
email sending. This means you don't have to call ``DBSession.commit()`` in your
view. At the end of the request, it will automatically commit the database
session(s) and send any pending emails, unless an uncaught exception was raised
during the session, in which case it will roll them back. It has functions to
allow you to commit or roll back the request-wide transaction at any time, or
to "doom" it to prevent any other code from committing anything.

The other "pyramid.\*" options are for debugging. Set any of these
to true to tell that subsystem to log what it's
doing. The messages will be logged at the DEBUG level. (The reason these aren't
in the logging configuration in the bottom part of the INI file is that they
were established early in Pyramid's history before it had adopted INI-style
logging configuration.)

If "pyramid.reload_templates=true", the template engine will check the
timestamp of the template source file every time it renders a template, and
recompile the template if its source has changed. This works only for template
engines and Pyramid-template adapaters that support this feature.  Mako and
Chameleon do.

The "sqlalchemy.url=" line is for SQLAlchemy.  "%(here)s" expands to the path
of the directory containing the INI file. You can add settings for any library
that understands them, including SQLAlchemy, Mako, and Beaker. You can also
define custom settings that your application code understands, so that you can
deploy it with different configurations without changing the code. This is all
the same as in Pylons.

*production.ini* has the same app settings as *development.ini*, except that
the "pyramid_debugtoolbar" tween is *not* present, and all the debug settings
are false. The debug toolbar *must* be disabled in production because it's a
potential security hole: anybody who can force an exception and get an
interactive traceback can run arbitrary Python commmands in the application
process, and thus read or modify files or execute programs.  So never enable
the debug toolbar when the site is accessible on the Internet, except perhaps
in a wide-area development scenario where higher-level access restrictions
(Apache) allow only trusted developers and beta testers to get to the site.

Pyramid no longer uses WSGI middleware by default. In most cases you can find a
tween or Pyramid add-on package that does the equivalent. If you need to
activate your own middleware, do it the same way as in Pylons; the syntax is in
the `PasteDeploy manual`_. But first consider whether making a Pyramid tween
would be just as convenient. Tweens have a much simpler API than middleware,
and have access to the view's request and response objects. The WSGI protocol is
extraordinarily difficult to implement correctly due to edge cases, and many
existing middlewares are incorrect. Let server developers and framework
developers worry about those issues; you can just write a tween and be out on the
golf course by 3pm.


.. _PasteDeploy manual: http://pythonpaste.org/deploy/
