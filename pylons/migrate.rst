Migrating an Existing Pylons Application
++++++++++++++++++++++++++++++++++++++++

If you're upgrading a large Pylons application to Pyramid, you can do it one
route at a time and have it fall back to the Pylons application for URLs which
don't exist. There are a few ways to set this up. One is to use Paste Cascade
-- the same way Pylons serves static files. In the INI file, make the main
application ``paste.cascade.Cascade``, delegating to the Pyramid application
first and falling back to the Pylons app.

Another way is to wrap the Pylons application in a Pyramid view. See
`pyramid.wsgiapp.wsgiapp2`_ and `Porting an Existing WSGI Application to
Pyramid`_.


.. _pyramid.wsgiapp.wsgiapp2: http://docs.pylonsproject.org/projects/pyramid/en/latest/api/wsgi.html#pyramid.wsgi.wsgiapp2
.. _Porting an Existing WSGI Application to Pyramid: http://docs.pylonsproject.org/projects/pyramid_cookbook/en/latest/porting/wsgi.html
