Deploying Your Pyramid Application
----------------------------------

So you've written a sweet application and you want to deploy it outside of
your local machine. We're not going to cover caching here, but suffice it to
say that there are a lot of things to consider when optimizing your pyramid
application.

At a high level, you need to expose a server on ports 80 (HTTP) and 443
(HTTPS). Underneath this layer, however, is
a plethora of different configurations that can be used to get a request
from a client, into your application, and return the response.

::

    Client <---> WSGI Server <---> Your Application

Due to the beauty of standards, many different configurations can be used to
generate this basic setup, injecting caching layers, load balancers, etc into
the basic workflow.

Disclaimer
++++++++++

It's important to note that the setups discussed here are meant to give some
direction to newer users. Deployment is *almost always* highly dependent on
the application's specific purposes. These setups have been used for many
different projects in production with much success, but never verbatim.

What is WSGI?
+++++++++++++

WSGI is a `Python standard <http://www.python.org/dev/peps/pep-0333/>`_
dictating the interface between a server and an
application. The entry point to your pyramid application is an object
implementing the WSGI interface. Thus, your application can be served by any
server supporting WSGI.

There are many different servers implementing the WSGI standard in existance.
A short list includes:

+ ``waitress``

+ ``paste.httpserver``

+ ``CherryPy``

+ ``uwsgi``

+ ``gevent``

+ ``mod_wsgi``

For more information on WSGI, see the `WSGI home <http://wsgi.org>`_
