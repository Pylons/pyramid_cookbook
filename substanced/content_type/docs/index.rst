Substance D
===========

Overview
--------

Substance D is an application server built using the :term:`Pyramid` web
framework. It can be used as a base to build a general-purpose web application
like a blog, a shopping cart application, a scheduling application, or any
other web app that requires both an administration and a retail interface.

Substance D owes much of its spirit to the :term:`Zope` application server.

It requires Python 2.6, 2.7, 3.2 or 3.3.

Installation
------------

Install using setuptools, e.g. (within a virtualenv)::

  $ easy_install substanced

.. warning:: 

   During Substance D's pre-alpha period, it may be necessary to use a checkout
   of Substance D as well as checkouts of the most recent versions of the
   libraries upon which Substance D depends.

.. _optional_dependencies:

Optional Dependencies
---------------------

Use of the :py:attr:`substanced.file.USE_MAGIC`
constant for guessing file types
from stream content requires the ``python-magic`` library, which works without
extra help on Linux systems, but requires special dependency installations on
Mac OS and Windows systems.  You'll need to follow these steps on those
platforms to use this feature:

Mac OS X

  http://www.brambraakman.com/blog/comments/installing_libmagic_in_mac_os_x_for_python-magic/

Windows

  "Installation on Win32" in https://github.com/ahupp/python-magic

Demonstration Application
--------------------------

See the application running at http://demo.substanced.net for a demonstration
of the Substance D management interface.  The package that contains the code
for that demo is available by running ``pcreate -s substanced myproj`` with
Substance D installed.

Narrative Documentation
-----------------------

.. toctree::
   :maxdepth: 1

   intro
   sdi
   content
   mgmtview
   forms
   services
   cataloging
   references
   workflows
   dump
   evolution
   folder_contents
   audit
   locking
   configuration
   statistics
   vrooting
   retail

API Documentation
-----------------

.. toctree::
   :maxdepth: 1

   api
   permissions

Support / Reporting Bugs / Development Versions
-----------------------------------------------

Visit http://github.com/Pylons/substanced to download development or tagged
versions.

Visit http://github.com/Pylons/substanced/issues to report bugs.

The mailing list exists at https://groups.google.com/group/substanced-users

The IRC channel is at irc://freenode.net/#substanced

Indices and tables
------------------

* :ref:`glossary`
* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

.. add glossary in a hidden toc to avoid warnings

.. toctree::
   :hidden:

   glossary
