Deployment
++++++++++

Deployment is the same for Pyramid as for Pylons. Specify the desired WSGI
server in the "[server:main]" and run "pserve" with it. The default server in
Pyramid is Waitress, compared to PasteHTTPServer in Pylons. 

Waitress' advantage is that it runs on Python 3. Its disadvantage is that it
doesn't seek and destroy stuck threads like PasteHTTPServer does. If you're
like me, that's enough reason not to use Waitress in production. You can switch
to PasteHTTPServer or CherryPy server if you wish, or use a method like
mod_wsgi that doesn't require a Python HTTP server. 
