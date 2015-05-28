Porting a Legacy Pylons Application Piecemeal
---------------------------------------------

You would like to move from Pylons 1.0 to Pyramid, but you're not going to be
able manage a wholesale port any time soon. You're wondering if it would be
practical to start using some parts of Pyramid within an existing Pylons
project.

One idea is to use a Pyramid "NotFound view" which delegates to the existing
Pylons application, and port piecemeal::

    # ... obtain pylons WSGI application object ...
    from mypylonsproject import thepylonsapp

    class LegacyView(object): 
        def __init__(self, app): 
            self.app = app
        def __call__(self, request): 
            return request.get_response(self.app) 

    if __name__ == '__main__': 
       legacy_view = LegacyView(thepylonsapp) 
       config = Configurator() 
       config.add_view(context='pyramid.exceptions.NotFound', view=legacy_view) 
       # ... rest of config ... 

At that point, whenever Pyramid cannot service a request because the URL
doesn't match anything, it will invoke the Pylons application as a fallback,
which will return things normally.  At that point you can start moving logic
incrementally into Pyramid from the Pylons application until you've ported
everything.
