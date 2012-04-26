Introduction
%%%%%%%%%%%%

History
=======

Pyramid is the unification of two different web programming styles in Python,
which I'll call the "Rails tradition" and the "content management
tradition". Pylons fits into the Rails tradition because it, like TurboGears
and Django, consciously emulates Ruby on Rails. That means they have more
built-in features than the previous generation of (non-Zope, non-Twisted)
Python web frameworks.  Pylons in particular ported Rails' map-based routing
mechanism (Routes) and HTML utilities (WebHelpers), and its default application
scaffold configures a template engine (Mako) and database ORM (SQLAlchemy) for
you.

The content management tradition started earlier, in 1998 with Zope. Zope has
an object-oriented routing mechanism which allows users to define arbitrarily
deep URL structures, uses XML-based template languages, and has a component
architecture (interfaces). These all helped build Python's premier
content-management system, Plone. In the mid 2000s some developers brought these
features out of Zope into a framework called BFG.

In 2010 the developers of Pylons and BFG decided they needed access to each
other's technologies. They merged their developer communities under the name
"The Pylons Project", renamed BFG to Pyramid, and added Pylons-like features to
Pyramid.  However, Pyramid is not completely like Pylons because the Pylons
developers decided to switch to some BFG APIs, TurboGears-like APIs, and some
innovations. 

Porting an application
======================

There are two general ways to port a Pylons application to Pyramid. One is to
start from scratch, expressing the application's behavior in Pyramid. Many
aspects such as the models, templates, and static files can be used unchanged
or mostly unchanged. Others such as the controllers and globals will have to be
rewritten. The route map can be ported to the new syntax, or you can take the
opportunity to restructure your routes.

The other way is to port one URL at a time, and let Pyramid serve the ported
URLs and Pylons serve the unported URLs. You can do this by running both the
Pyramid application and the Pylons application under Apache, and having it send
certain URLs to one app and other URLs to the other. You can also have Pyramid
delegate certain URLs to Pylons as a WSGI sub-application. (That may bring up
some tricky issues such as coordinating database connections, sessions, data
files, etc.)

You'll also have to choose whether to write the Pyramid application in Python 2
or 3. Pyramid 1.3 runs on Python 3, along with Mako and SQLAlchemy, and the
Waitress and CherryPy HTTP servers (but not PasteHTTPServer). But not all
optional libraries have been ported yet, and your application may depend on
libraries which haven't been. The author has not used Python 3 yet, so this
guide focuses on Python 2.7.

There are several higher-level frameworks built on top of Pyramid, such as
Kotti and Ptah. You may prefer to use one of these as a basis for your
application, but be forewarned that they stray even further from the Pylons API.

Following along with the examples
=================================

The examples in this guide are based on Pyramid 1.3's "alchemy" skeleton and
the Akhet_ demo. You may want to generate a Pyramid application and check out
the Akhet demo repository now, and have them open in separate console windows
while reading. If you haven't generated a Pyramid application yet, see
`Installing Pyramid`_ and `Creating Your First Pyramid Application`_ in the
`Pyramid manual`_.  Here are the basic steps on Linux Ubuntu 11.10:

.. code-block:: sh

   # Prepare virtual Python environment.

   $ cd ~/workspace
   $ virtualenv myvenv
   $ source venv/bin/activate
   (myvenv)$ pip install 'Pyramid>=1.3'

   # Create a Pyramid "alchemy" application and run it.

   (myvenv)$ pcreate -s alchemy PyramidApp
   (myvenv)$ cd PyramidApp
   (myvenv)$ pip install -e .
   (myvenv)$ populate_PyramidApp development.ini
   (myvenv)$ pserve development.ini
   Starting server in PID 3871.
   serving on http://0.0.0.0:6543

   # Press ctrl-C to quit server

   # Check out the Akhet demo and run it.

   (myvenv)$ git clone git://github.com/mikeorr/akhet_demo
   (myvenv)$ cd akhet_demo
   (myvenv)$ pip install -e .
   (myvenv)$ pserve development.ini
   Starting server in PID 3871.
   serving on http://0.0.0.0:6543

   # Check out the Pyramid source and Akhet source to study.

   (myvenv)$ git clone git://github.com/pylons/pyramid
   (myvenv)$ git clone git://github.com/pylons/akhet

   (myvenv)$ ls -F
   akhet/
   akhet_demo/
   PyramidApp/
   pyramid/
   venv/


.. include:: ../links.rst
