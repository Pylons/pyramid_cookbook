.. _pyramid-tutorials:

=================
Pyramid Tutorials
=================

This is the home of tutorial and patterns content for the Pyramid web
framework.

Available Pyramid tutorials
===========================

Pyramid tutorials exist in the official `Pyramid Documentation
<http://docs.pylonsproject.org/projects/pyramid/en/latest/#tutorials>`_,
appear in this community project `Pyramid Tutorials
<http://docs.pylonsproject.org/projects/pyramid_tutorials/en/latest/>`_, and
others are published elsewhere.

These are the Pyramid tutorials we could locate during the PyCon USA sprints in
March, 2013.

**ET** is the estimated time to complete each tutorial.

================== === ======================= =============================== ==================== ========================================
name/link          ET* title                   description                     code repo            features
================== === ======================= =============================== ==================== ========================================
`quick_tutorial`_  8h  Quick Tutorial for      Introduction to and high-level  `pyramid`_           * Most, if not all
                       Pyramid                 tour of Pyramid's major
                                               features.

`firstapp`_        1h  Creating Your First     "Hello World"                   `pyramid`_           * URL dispatch
                       Pyramid Application

`wiki`_            4h  ZODB + Traversal Wiki   Create a wiki using ZODB and    `pyramid`_           * traversal
                       Tutorial                traversal                                            * ZODB
                                                                                                    * security

`wiki2`_           4h  SQLAlchemy + URL        Create a wiki using SQLAlchemy  `pyramid`_           * URL dispatch
                       Dispatch Wiki Tutorial  and URL dispatch                                     * SQLAlchemy
                                                                                                    * security

`birdie`_          4h  Birdie Tutorial: a      presented by Carlos de la
                       simple Twitter clone    Guardia at OSCON 2011 and PyCon `cguardia_tut`_
                                               USA 2012

`blogr`_           4h  ``pyramid_blogr``       inspired by Flaskr app from the `pyramid_blogr`_     * URL dispatch
                       Tutorial                Flask Web Framework Tutorial                         * SQLAlchemy
                                                                                                    * Jinja2
                                                                                                    * security
                                                                                                    * WTForms
                                                                                                    * pagination

`pycharm`_         1h  Using PyCharm with      A getting started guide
                       Pyramid                 for Pyramid using PyCharm

`single_file`_     ?   Todo List Application   very short; a.k.a. The Single   `pyramid_tutorials`_
                       in One File             ``tasks`` Tutorial              (this site)

`todopyramid`_     4h  ``ToDo Pyramid App``    ToDo App from Python Web        `todopyramid`_       * URL dispatch
                       Tutorial                Shootout by SixFeet, Inc                             * SQLAlchemy
                                               Demo here:                                           * Deform (with bootstrap)
                                               http://demo.todo.sixfeetup.com                       * Chameleon
                                                                                                    * Mozilla Persona (using pyramid_persona)
                                                                                                    * WebHelpers
                                                                                                    * Custom NotFound view

`traversal`_       2d  Quick Tour for          Overview of traversal:          `pyramid_tutorials`_ * Site root
                       Traversal               Hierarchies, views, etc.        (this site)          * Hierarchy
                                                                                                    * Type-specific views
                                                                                                    * Adding content
                                                                                                    * ZODB persistence
                                                                                                    * SQL persistence
================== === ======================= =============================== ==================== ========================================

.. _quick_tutorial: http://docs.pylonsproject.org/projects/pyramid/en/latest/quick_tutorial/index.html
.. _firstapp: http://docs.pylonsproject.org/projects/pyramid/en/latest/narr/firstapp.html
.. _wiki: http://docs.pylonsproject.org/projects/pyramid/en/latest/tutorials/wiki/index.html
.. _wiki2: http://docs.pylonsproject.org/projects/pyramid/en/latest/tutorials/wiki2/index.html
.. _birdie: https://github.com/cguardia/Pyramid-Tutorial/blob/master/presentation/pyramid_tutorial.pdf
.. _blogr: http://pyramid-blogr.readthedocs.org/en/latest/
.. _pycharm: http://docs.pylonsproject.org/projects/pyramid_tutorials/en/latest/pycharm/index.html
.. _single_file: http://docs.pylonsproject.org/projects/pyramid_tutorials/en/latest/single_file_tasks/single_file_tasks.html
.. _todopyramid: https://github.com/indypy/todopyramid
.. _traversal: http://docs.pylonsproject.org/projects/pyramid_tutorials/en/latest/quick_traversal/index.html

.. _pyramid: https://github.com/Pylons/pyramid
.. _pyramid_tutorials: https://github.com/Pylons/pyramid_tutorials
.. _pyramid_blogr: https://github.com/Pylons/pyramid_blogr
.. _cguardia_tut: https://github.com/cguardia/Pyramid-Tutorial

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

.. toctree::
   :hidden:

   README
   getting_started/index
   single_file_tasks/single_file_tasks
   humans/index
   pycharm/index
   quick_traversal/index
