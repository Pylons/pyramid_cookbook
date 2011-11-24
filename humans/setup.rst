==============
Tutorial Setup
==============

This tutorial presumes you have Python 2.6 or higher, a network
connection, and the editor of your choice. The following is enough to
get you started on the first step. Other steps might ask to install
extra packages.

.. note::

   Windows users will need to adapt the Unix-isms below to match
   their environment.

Our directory layout will look as follows::

  someworkingdirectory/
     tutorial_workspace/
       venv                     ### Target for our virtualenv
       creatingux/
          step01
          step02
          etc.
       resources
          step01
          step02
          etc.
       etc.

Steps
=====

#. Open a shell window and ``cd`` to a working directory.

#. ``$ mkdir tutorial_workspace; cd tutorial_workspace``

#. ``$ virtualenv --no-site-packages venv``

#. ``$ export PATH=/path/to/tutorial_workspace/venv/bin:$PATH``

#. ``$ which easy_install``

   This should report the ``easy_install`` from ``venv/bin``.

#. ``$ easy_install pyramid WebTest nose``

#. ``$ export PYRAMID_RELOAD_TEMPLATES=1`` lets you edit templates and
   not have to restart your Pyramid application.


Code Examples
=============

Each step in the tutorial asks the reader to enter code examples and
produce a working application. The directories for these steps are
*not* Python packages, but rather, a simple directory full of Python
modules. They are, however, fully-working, standalone examples that
gradually increase into a full application.

The example files are available for those that don't want to enter the
code as part of the tutorial process.
