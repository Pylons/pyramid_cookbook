=======================================
Step 01: Most Basic Resource: Site Root
=======================================

To remove some mystery about traversal, we start with the smallest
possible step: an object at the top of our URL space. This object acts
as the "root" and has a view which shows some data on that object.

Goals
=====

- Take a tiny step into traversal

- Show how Pyramid grabs a resource object and makes it available in a
  view

Objectives
==========

- Make a factory for the root object

- Pass it to the configurator

- Have a view which displays an attribute on that object

Steps
=====

#. ``$ cd ../../resources; mkdir step01; cd step01``

#. Copy the following into ``step01/application.py``:

   .. literalinclude:: application.py
      :linenos:

#. Copy the following into ``step01/views.py``:

   .. literalinclude:: views.py
      :linenos:

#. Copy the following into ``step01/resources.py``:

   .. literalinclude:: resources.py
      :linenos:

#. Copy the following into ``step01/tests.py``:

   .. literalinclude:: tests.py
      :linenos:

#. ``$ nosetests`` should report running 2 tests.

#. ``$ python application.py``

#. Open ``http://127.0.0.1:8080/`` in your browser.

Extra Credit
============

#. Is the root factory called once on startup, or on every request? Do
   a small change that answers this. What is the impact of the answer
   on this?

Analysis
========

Our ``application.py`` has a small but important change: we create the
configuration with a *root factory*. Our root factory is a simple
function that populates.

We put our resource objects in ``resources.py``. Here we make the
classes that model our application. We then have a ``bootstrap.py``
function which makes an instance of our class and hands back as the top
of the tree.

In this step, our tree has one object: the root. It is an instance of
``SiteFolder``. Since it is the root, it doesn't need a ``__name__``
(aka ``id``) nor a ``__parent__`` (reference to the container an object
is in.)

Our ``site_view`` is passed, by Pyramid, the instance of this folder as
``context``. The view can then grab attributes and other data from the
object that is the focus of the URL.

Discussion
==========

- The concept of factories and their genesis going back to Zope and CMF

- Pyramid and need for, and management of,  ``__name__`` and
  ``__parent__``