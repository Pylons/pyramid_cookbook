Introduction and Creating an Application
++++++++++++++++++++++++++++++++++++++++

Following along with the examples
=================================

The examples in this guide are based on (A) Pyramid 1.3's default SQLAlchemy
application and (B) the Akhet_ demo. (Akhet_ is an add-on package containing
some Pylons-like support features for Pyramid.) Here are the basic steps to
install and run these applications on Linux Ubuntu 11.10, but you should 
read `Creating a Pyramid Project`_ in the `Pyramid manual`_ before doing so:

.. code-block:: sh
   :linenos:

   # Prepare virtual Python environment.

   $ cd ~/workspace
   $ virtualenv myvenv
   $ source myvenv/bin/activate
   (myvenv)$ pip install 'Pyramid>=1.3'

   # Create a Pyramid "alchemy" application and run it.

   (myvenv)$ pcreate -s alchemy PyramidApp
   (myvenv)$ cd PyramidApp
   (myvenv)$ pip install -e .
   (myvenv)$ initialize_PyramidApp_db development.ini
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
   myvenv/

*Things to look for:* the "DT" icon at the top-right of the page is the debug
toolbar, which Pylons doesn't have. The "populate_PyramidApp" script (line 13) 
creates the database. If you skip this step you'll get an exception on the home
page; you can "accidentally" do this to see Pyramid's interactive traceback.

The p\* Commands
================

Pylons uses a third-party utility *paster* to create and run applications.
Pyramid replaces these subcommands with a series of top-level commands
beginning with "p":

================ ============  ========================= ========================
Pylons           Pyramid       Description               Caveats
================ ============  ========================= ========================
paster create    pcreate       Create an app             Option -s instead of -t
paster serve     pserve        Run app based on INI file \-
paster shell     pshell        Load app in Python shell  Fewer vars initialized
paster setup-app populate_App  Initialize database       "App" is application name
paster routes    proutes       List routes               \-
\-               ptweens       List tweens               \-
\-               pviews        List views                \-
================ ============  ========================= ========================

In many cases the code is the same, just copied into Pyramid and made Python 3
compatible. Paste has not been ported to Python 3, and the Pyramid developers
decided it contained too much legacy code to make porting worth it. So they
just ported the parts they needed. Note, however, that PasteDeploy *is* ported
to Python 3 and Pyramid uses it, as we'll see in the next chapter. Likewise,
several other packages that were earlier spun out of Paste -- like WebOb --
have been ported to Python 3 and Pyramid still uses them. (They were ported
parly by Pyramid developers.) 


Scaffolds
=========

Pylons has one paster template that asks questions
about what kind of application you want to create. Pyramid does not ask
questions, but instead offers several scaffolds to choose from. Pyramid 1.3
includes the following scaffolds:

=================    ==========  ================ 
Routing mechanism    Database    Pyramid scaffold
=================    ==========  ================
URL dispatch         SQLAlchemy  alchemy         
URL dispatch         \-          starter         
Traversal            ZODB        zodb            
=================    ==========  ================

..
    =================    ==========  ====================    ======================
    Routing mechanism    Database    Pyramid 1.3 scaffold    Pyramid 1.2.4 scaffold
    =================    ==========  ====================    ======================
    URL dispatch         SQLAlchemy  **alchemy**             routesalchemy
    URL dispatch         \-          **starter**             \-
    Traversal            ZODB        **zodb**                zodb
    Traversal            SQLAlchemy  \-                      alchemy
    Traversal            \-          \-                      starter
    =================    ==========  ====================    ======================

The first two scaffolds are the closest to Pylons because they use URL
dispatch, which is similar to Routes. The only difference between them is
whether a SQLAlchemy database is configured for you. The third scaffold uses Pyramid's other
routing mechanism, Traversal. We won't cover traversal in this guide, but it's
useful in applications that allow users to create URLs at arbitrary depths.
URL dispatch is more suited to applications with fixed-depth URL hierarchies.

To see what other kinds of Pyramid applications are possible, take a look at
the Kotti and Ptah distributions. Kotti is a content management system, and
serves as an example of traversal using SQLAlchemy.


Directory Layout
================

The default 'alchemy' application contains the following files after you create and install it:

.. code-block::  text

    PyramidApp
    ├── CHANGES.txt
    ├── MANIFEST.in
    ├── README.txt
    ├── development.ini
    ├── production.ini
    ├── setup.cfg
    ├── setup.py
    ├── pyramidapp
    │   ├── __init__.py
    │   ├── models.py
    │   ├── scripts
    │   │   ├── __init__.py
    │   │   └── populate.py
    │   ├── static
    │   │   ├── favicon.ico
    │   │   ├── pylons.css
    │   │   ├── pyramid.png
    │   ├── templates
    │   │   └── mytemplate.pt
    │   ├── tests.py
    │   └── views.py
    └── PyramidApp.egg-info
        ├── PKG-INFO
        ├── SOURCES.txt
        ├── dependency_links.txt
        ├── entry_points.txt
        ├── not-zip-safe
        ├── requires.txt
        └── top_level.txt

..
   Generated via this command and manually resorted and some entries removed.
   tree --noreport -n -I '*.pyc' Zzz  >/tmp/files

(We have omitted some static files.) As you see, the directory structure is
similar to Pylons but not identical.

.. include:: ../links.rst
