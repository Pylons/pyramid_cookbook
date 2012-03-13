Creating an Application
+++++++++++++++++++++++

Scaffolds
=========

Pylons has one application scaffold ("pylons") that asks questions about what
kind of application you want. Pyramid's scaffolds do not ask questions; instead
you choose a scaffold. Here's a table of all the built-in scaffolds:

=================    ==========  ====================    ======================
Routing mechanism    Database    Pyramid 1.3 scaffold    Pyramid 1.2.4 scaffold
=================    ==========  ====================    ======================
URL dispatch         SQLAlchemy  **alchemy**             routesalchemy
URL dispatch         \-          **starter**             \-
Traversal            ZODB        **zodb**                zodb
Traversal            SQLAlchemy  \-                      alchemy
Traversal            \-          \-                      starter
=================    ==========  ====================    ======================

The first two rows are the most similar to Pylons, because they use URL
dispatch which is similar to Routes. So to create a Routes-like application
with SQLAlchemy on Pyramid 1.3, use the "alchemy" scaffold. If you're not using
SQLAlchemy, use the "starter" scaffold.

For additional scaffolds and APIs, see the Akhet distribution and Akhet Demo,
and the Ptah and Kotti distributions.


The p\* Commands
================

Pyramid 1.3 replaces the multipurpose "paster" commands with a series of
Pyramid-specific "p\*" commands. So "pcreate" replaces "paster create", and
"pserve" replaces "paster serve". Note that some of the command-line arguments
have changed. Here's the basic mantra to create and run a Pyramid application
using the 'alchemy' scaffold on Ubuntu 11.10:

.. code-block:: sh
   :linenos:

   $ virtualenv --no-site-packages ~/directory/myvenv
   $ source ~/directory/myvenv/bin/activate
   (myvenv)$ pip install 'Pyramid>=1.3'
   (myvenv)$ pcreate -s alchemy PyramidApp
   (myenv)$ cd PyramidApp
   (myenv)$ pip install -e .
   (myenv)$ populate_PyramidApp development.ini
   (myenv)$ pserve development.ini

Go to http://localhost:6543/ in your web browser to see the default content.
Press ctrl-c to quit the server.

Line 7 ("populate") is specific to the 'alchemy' scaffold; it
creates the initial database. (It thus fulfills the role of "paster setup-app",
which Pyramid does not support.)

For more information on these commands, see "Installing Pyramid" and "Creating
a Pyramid Project" in the Pyramid manual. The latter also explains
the debug toolbar (which Pylons doesn't have) and interactive traceback. 


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
