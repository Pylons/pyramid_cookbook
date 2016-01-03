Porting an Existing WSGI Application to Pyramid
-----------------------------------------------

Pyramid is cool, but already-working code is cooler.  You may not have the
time, money or energy to port an existing Pylons, Django, Zope, or other
WSGI-based application to Pyramid wholesale.  In such cases, it can be useful
to *incrementally* port an existing application to Pyramid.

The broad-brush way to do this is:

- Set up an *exception view* that will be called whenever a NotFound
  exception is raised by Pyramid.

- In this exception view, delegate to your already-written WSGI application.

Here's an example::

   from pyramid.wsgi import wsgiapp2
   from pyramid.exceptions import NotFound

   if __name__ == '__main__':
       # during Pyramid configuration (usually in your Pyramid project's
       # __init__.py), get a hold of an instance of your existing WSGI
       # application.
       original_app = MyWSGIApplication()

       # using the pyramid.wsgi.wsgiapp2 wrapper function, wrap the
       # application into something that can be used as a Pyramid view.
       notfound_view = wsgiapp2(original_app)

       # in your configuration, use the wsgiapp2-wrapped application as
       # a NotFound exception view
       config = Configurator()

       # ... your other Pyramid configuration ...
       config.add_view(notfound_view, context=NotFound)
       # .. the remainder of your configuration ...


When Pyramid cannot resolve a URL to a view, it will raise a NotFound
exception.  The ``add_view`` statement in the example above configures
Pyramid to use your original WSGI application as the NotFound view.  This
means that whenever Pyramid cannot resolve a URL, your original application
will be called.

Incrementally, you can begin moving features from your existing WSGI
application to Pyramid; if Pyramid can resolve a request to a view, the
Pyramid "version" of the application logic will be used.  If it cannot, the
original WSGI application version of the logic will be used.  Over time, you
can move *all* of the logic into Pyramid without needing to do it all at
once.
