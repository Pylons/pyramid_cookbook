=====================================
4: Quick Project Start With Scaffolds
=====================================

Getting started quickly on a Python application requires,
as we just saw, several steps. Like other popular web frameworks,
Pyramid provides a facility called "scaffolds" that let you quickly
generate the basics of a Pyramid application.

Objectives
==========

- Use ``pcreate`` to see what scaffolds are available

- Create and install a sample project using one of the available
  scaffolds

Steps
=====

#. ``(env33)$ cd ..; mkdir step03; cd step03``

#. See the usage for ``pcreate``:

   .. code-block:: bash

    (env33)$ pcreate --help

#. List the available scaffolds:

   .. code-block:: bash

    (env33)$ pcreate --list

#. Make a new Python project called ``tutorial`` using ``starter``
   as a starting point:

   .. code-block:: bash

    (env33)$ pcreate -s starter tutorial


#. Visit that project and see the project contents:

   .. code-block:: bash

    (env33)$ cd tutorial; ls

#. Install your new project:

   .. code-block:: bash

    (env33)$ python3.3 setup.py develop

#. Run the WSGI application with:

   .. code-block:: bash

    (env33)$ pserve development.ini

#. Open ``http://127.0.0.1:6543/`` in your browser. *Different port
   number!*

Analysis
========

Pyramid has a number of scaffold *templates* that provide different
starting points. ``starter`` is the most basic. ``alchemy`` is useful
for developers wanting SQLAlchemy as a starting point. These scaffolds
provide a way for Pyramid to remain unopinionated,
but still provide starting points with a set of opinions.

When you visited this project in your browser, you might have seen the
``pyramid_debugtoolbar`` in action. This is a handy helper during
development.

.. note::

  The remaining steps in this tutorial do not use scaffolds,
  as we want to teach the various decisions being made.

Extra Credit
============

#. If you make a project with one of the scaffolds, can you still
   share your project with others?

#. Can you make scaffolds for your own Pyramid projects?
