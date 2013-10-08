.. _pyramid-tutorials:

=================
Pyramid Tutorials
=================

This is the home of tutorial and patterns content for the Pyramid web
framework.

---------------------------
Available Pyramid tutorials
---------------------------

Several Pyramid tutorials exist. Some are part of the main
`Pyramid Documentation`_, some are in this `Pyramid Tutorials`_
community project, and others are published elsewhere.

.. _Pyramid Documentation: http://docs.pylonsproject.org/en/latest/docs/pyramid.html
.. _Pyramid Tutorials: http://docs.pylonsproject.org/projects/pyramid/en/1.4-branch/#tutorials


These are the Pyramid tutorials we could locate during the PyCon USA sprints in March, 2013.

**ET** is the estimated time to complete each tutorial.

================== === ======================= =============================== ==================== ========================================
name/link          ET* title                   description                     code repo            features
================== === ======================= =============================== ==================== ========================================
`firstapp`_        1h  Creating Your First     chapter 4 in the
                       Pyramid Application     `Narrative Documentation`_ part `pyramid`_           * URL dispatch
                                               of the main Pyramid docs

`wiki`_            4h  ZODB + Traversal Wiki   chapter 37 in the `Tutorials`_  `pyramid`_           * traversal
                       Tutorial                part of the main Pyramid docs                        * ZODB

`wiki2`_           4h  SQLAlchemy + URL        chapter 38 in the `Tutorials`_  `pyramid`_           * URL dispatch
                       Dispatch Wiki Tutorial  part of the main Pyramid docs                        * SQLAlchemy

`single_file`_     ?   Todo List Application   very short; a.k.a. The Single   `pyramid_tutorials`_
                       in One File             ``tasks`` Tutorial              (this site)

`humans`_          12h Pyramid for Plone       Pyramid for Plone Developers    `pyramid_tutorials`_
                       Developers                                              (this site)

`getting_started`_ 5h  Getting Started with    Presented by Paul Everitt at    `pyramid_tutorials`_ * URL dispatch
                       Pyramid                 PyCon USA 2013                  (this site)          * SQLAlchemy
                                                                                                    * Chameleon
                                                                                                    * security

`blogr`_           4h  ``pyramid_blogr``       inspired by Flaskr app from the `pyramid_blogr`_     * URL dispatch
                       Tutorial                Flask Web Framework Tutorial                         * SQLAlchemy
                                                                                                    * Mako
                                                                                                    * security
                                                                                                    * WTForms
                                                                                                    * pagination
`birdie`_          4h  Birdie Tutorial: a      presented by Carlos de la
                       simple Twitter clone    Guardia at OSCON 2011 and PyCon `cguardia_tut`_
                                               USA 2012

`todopyramid`_     4h  ``ToDo Pyramid App``    ToDo App from Python Web        `todopyramid`_       * URL dispatch
                       Tutorial                Shotout by SixFeet, Inc                              * SQLAlchemy
                                               Demo here:                                           * Deform (with bootstrap)
                                               http://demo.todo.sixfeetup.com                       * Chameleon
                                                                                                    * Mozilla Person (using pyramid_persona)
                                                                                                    * WebHelps
                                                                                                    * Custom NotFound view
`pycharm`_         1h  Using Pycharm with      A getting started guide
                       Pyramid                 for Pyramid using Pycharm
`traversal`_       2d  Quick Tour for          Overview of traversal:          `pyramid_tutorials`_ * Site root
                       Traversal               Hierarchies, views, etc.        (this site)          * Hierarchy
		       			       		    	   	       	     		                                * Type-specific views
												                                                    * Adding content
												                                                    * ZODB persistence
												                                                    * SQL persistence
================== === ======================= =============================== ==================== ========================================


.. _firstapp: http://docs.pylonsproject.org/projects/pyramid/en/1.4-branch/narr/firstapp.html
.. _wiki: http://docs.pylonsproject.org/projects/pyramid/en/1.4-branch/tutorials/wiki/index.html
.. _wiki2: http://docs.pylonsproject.org/projects/pyramid/en/1.4-branch/tutorials/wiki2/index.html
.. _single_file: http://docs.pylonsproject.org/projects/pyramid_tutorials/en/latest/single_file_tasks/single_file_tasks.html
.. _humans: http://docs.pylonsproject.org/projects/pyramid_tutorials/en/latest/humans/index.html
.. _getting_started: http://docs.pylonsproject.org/projects/pyramid_tutorials/en/latest/getting_started/index.html
.. _blogr: http://pyramid-blogr.readthedocs.org/en/latest/
.. _birdie: https://github.com/cguardia/Pyramid-Tutorial/blob/master/presentation/pyramid_tutorial.pdf
.. _todopyramid: https://github.com/indypy/todopyramid
.. _pycharm: http://docs.pylonsproject.org/projects/pyramid_tutorials/en/latest/pycharm/index.html

.. _Narrative Documentation: http://docs.pylonsproject.org/projects/pyramid/en/1.4-branch/#narrative-documentation
.. _Tutorials: http://docs.pylonsproject.org/projects/pyramid/en/1.4-branch/#tutorials

.. _pyramid: https://github.com/Pylons/pyramid
.. _pyramid_tutorials: https://github.com/Pylons/pyramid_tutorials
.. _pyramid_blogr: https://github.com/Pylons/pyramid_blogr
.. _cguardia_tut: https://github.com/cguardia/Pyramid-Tutorial
.. _traversal: http://docs.pylonsproject.org/projects/pyramid_tutorials/en/latest/quick_traversal/index.html

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
   quick_traversal/index
   _themes/README
   pycharm/index
