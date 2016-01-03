Migrating an Existing Pylons Application
++++++++++++++++++++++++++++++++++++++++

There are two general ways to port a Pylons application to Pyramid. One is to
start from scratch, expressing the application's behavior in Pyramid. Many
aspects such as the models, templates, and static files can be used unchanged
or mostly unchanged. Other aspects like such as the controllers and globals
will have to be rewritten. The route map can be ported to the new syntax, or
you can take the opportunity to restructure your routes.

The other way is to port one URL at a time, and let Pyramid serve the ported
URLs and Pylons serve the unported URLs. There are several ways to do this:

* Run both the Pyramid and Python applications in Apache, and use mod_rewrite
  to send different URLs to different applications.
* Set up ``paste.cascade`` in the INI file, so that it will first try one
  application and then the other if the URL returns "Not Found". (This is how
  Pylons serves static files.)
* Wrap the Pylons application in a Pyramid view. See pyramid.wsgiapp.wsgiapp2_.

Also see the `Porting Applications to Pyramid`_ section in the Cookbook.

*Caution:* running a Pyramid and a Pylons application simultaneously may bring up
some tricky issues such as coordiating database connections, sessions, data
files, etc. These are beyond the scope of this Guide.

You'll also have to choose whether to write the Pyramid application in Python 2
or 3. Pyramid 1.3 runs on Python 3, along with Mako and SQLAlchemy, and the
Waitress and CherryPy HTTP servers (but not PasteHTTPServer). But not all
optional libraries have been ported yet, and your application may depend on
libraries which haven't been.


.. include:: ../links.rst


.. _pyramid.wsgiapp.wsgiapp2: http://docs.pylonsproject.org/projects/pyramid/en/latest/api/wsgi.html#pyramid.wsgi.wsgiapp2
.. _Porting Applications to Pyramid: ../porting/index.html
