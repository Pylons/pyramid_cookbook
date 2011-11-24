=====================================
Resources, Hierarchies, and Traversal
=====================================

Web applications have URLs which locate data and make operations on that
data. Pyramid supports two ways of mapping URLs into Python operations:

- The more-traditional approach of *URL dispatch* aka *routes*

- The more object-oriented approach of *traversal* popularized by Zope

As this is a tutorial at the Plone Conference, we will show building an
application using traversal. Along the way, we will try to show how
easy and Pythonic it is to think in terms of traversal.

Remember...traversal is easy, powerful, and useful.

With traversal, you think of your website as a tree of Python objects,
just like a dictionary of dictionaries. For example::

  http://example.com/company1/aFolder/subFolder/doc1/add?x=1

...is nothing more than::

  >>> root['aFolder']['subFolder']['doc1'].add(x=1)

Goals
=====

- Easiest possible introduction to traversal

- A tree of resources of different "types"

- Show how views can be specific to a certain "type"

- Integrate back into our ongoing application

Contents
========

.. toctree::
   :maxdepth: 1

   step01/index
   step02/index
   step03/index
   step04/index
   step05/index
