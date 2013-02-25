=================
Tutorial Approach
=================

- Tutorial broken into topics with quick working examples

- Each step is a Python *package* with working code in the repo

- Setup each step with ``python3.3 setup.py develop``

This "Getting Started" tutorial is broken into independent steps,
starting with the smallest possible "single file WSGI app" example.
Each of these steps introduce a topic and a very small set of concepts
via working code. The steps each correspond to a directory in this
repo, where each step/topic/directory is a Python package.

To successfully run each step::

  $ cd 02-hellopackage
  $ python3.3 setup.py develop

...and repeat for each step you would like to work on.

.. note::

  The first step in the tutorial, as it explains on its page,
  does *not* require package installation.

Scenario and Technologies
=========================

This tutorial will demonstrate creation of a simple Wiki application
for Pyramid and Python 3.3. As shown in the table of contents,
we will show various Pyramid facilities, such as views and security. We
will also use some important add-on packages (SQLAlchemy for storage,
Deform for forms.)

Directory Tree
==============

As we develop our tutorial our directory tree will resemble the
structure below::

  getting_started/
    01/
        helloworld.py
    02/
        setup.py
        tutorial/
            __init__.py
            helloworld.py
            views.py
    03/
        setup.py
        development.ini
        tutorial/
            __init__.py
            views.py

Each of the 02-XX directories are a *Python package*. (01 is a
single-file application.) At the end of each step,
we copy the old directory into a new directory to use as a starting
point.
