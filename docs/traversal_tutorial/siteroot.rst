==================================
2: Basic Traversal With Site Roots
==================================

Model websites as a hierarchy of objects with operations.

Background
==========

Web applications have URLs which locate data and make operations on that data.
Pyramid supports two ways of mapping URLs into Python operations:

- the more traditional approach of *URL dispatch*, or *routes*

- the more object-oriented approach of :ref:`traversal
  <pyramid:traversal_chapter>` popularized by Zope

In this section we will introduce traversal bit-by-bit. Along the way, we will
try to show how easy and Pythonic it is to think in terms of traversal.

Traversal is easy, powerful, and useful.

With traversal, you think of your website as a tree of Python objects, just
like a dictionary of dictionaries. For example::

  http://example.com/company1/aFolder/subFolder/search

...is nothing more than::

  >>> root['aFolder']['subFolder'].search()

To remove some mystery about traversal, we start with the smallest possible
step: an object at the top of our URL space. This object acts as the "root" and
has a view which shows some data on that object.

Objectives
==========

- Make a factory for the root object.

- Pass it to the configurator.

- Have a view which displays an attribute on that object.

Steps
=====

#. We are going to use the previous step as our starting point:

   .. code-block:: bash

    $ cd ..; cp -r layout siteroot; cd siteroot
    $ $VENV/bin/python setup.py develop

#. In ``siteroot/tutorial/__init__.py``, make a root factory that points to a
   function in a module we are about to create:

   .. literalinclude:: siteroot/tutorial/__init__.py
      :linenos:
      :emphasize-lines: 3,7-8

#. We add a new file ``siteroot/tutorial/resources.py`` with a class for the
   root of our site, and a factory that returns it:

   .. literalinclude:: siteroot/tutorial/resources.py
      :linenos:

#. Our views in ``siteroot/tutorial/views.py`` are now very different:

   .. literalinclude:: siteroot/tutorial/views.py
      :linenos:
      :emphasize-lines: 4-6,9-16

#. Rename the template ``siteroot/tutorial/templates/site.jinja2`` to
   ``siteroot/tutorial/templates/home.jinja2`` and modify it:

   .. literalinclude:: siteroot/tutorial/templates/home.jinja2
    :language: jinja
    :linenos:
    :emphasize-lines: 4-5

#. Add a template in ``siteroot/tutorial/templates/hello.jinja2``:

   .. literalinclude:: siteroot/tutorial/templates/hello.jinja2
    :language: jinja
    :linenos:

#. Modify the simple tests in ``siteroot/tutorial/tests.py``:

   .. literalinclude:: siteroot/tutorial/tests.py
      :linenos:
      :emphasize-lines: 4,8-16,26,28

#. Now run the tests:

   .. code-block:: bash

    $ $VENV/bin/nosetests tutorial
    ..
    ----------------------------------------------------------------------
    Ran 2 tests in 0.134s

    OK

#. Run your Pyramid application with:

   .. code-block:: bash

    $ $VENV/bin/pserve development.ini --reload

#. Open http://localhost:6543/hello in your browser.

Analysis
========

Our ``__init__.py`` has a small but important change: we create the
configuration with a *root factory*. Our root factory is a simple function that
performs some work and returns the root object in the :ref:`resource tree
<pyramid:the_resource_tree>`.

In the resource tree, Pyramid can match URLs to objects and subobjects,
finishing in a view as the operation to perform. Traversing through containers
is done using Python's normal ``__getitem__`` dictionary protocol.

Pyramid provides services beyond simple Python dictionaries. These
:ref:`location <pyramid:location_aware>` services need a little bit more
protocol than just ``__getitem__``. Namely, objects need to provide an
attribute/callable for ``__name__`` and ``__parent__``.

In this step, our tree has one object: the root. It is an instance of our
``Root`` class. The next URL hop is ``hello``. Our root instance does not have
an item in its dictionary named ``hello``, so Pyramid looks for a view with a
``name=hello``, finding our view method.

Our ``home`` view is passed by Pyramid, with the instance of this folder as
``context``. The view can then grab attributes and other data from the object
that is the focus of the URL.

Now on to the most visible part: no more routes! Previously we wrote URL
"replacement patterns" which mapped to a route. The route extracted data from
the patterns and made this data available to views that were mapped to that
route.

Instead segments in URLs become object identifiers in Python.

Extra Credit
============

#. Is the root factory called once on startup, or on every request? Do
   a small change that answers this. What is the impact of the answer
   on this?

.. seealso::
   :ref:`pyramid:traversal_chapter`,
   :ref:`pyramid:location_aware`,
   :ref:`pyramid:the_resource_tree`,
   :ref:`much_ado_about_traversal_chapter`
