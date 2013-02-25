============
Python Setup
============

As the world of Python starts to get more traction with Python 3,
important technologies such as Pyramid need to work harder to not just
tolerate Python 3 but to embrace it. As a step towards this,
our *Getting Started* tutorial features Python 3.3+ (though it will
also work as-is in Python 2.)

This, of course, introduces some complexity.

Python 3.3 From Source
======================

Compiling and installing your own Python 3 or 2 is always the preferred
solution. As this document later shows, issues arise from using
pre-packaged installations.

First:

  #. Download and compile Python from source
  #. Install it to a directory of your choosing

Below, ``path/to/python/bin`` refers to this directory.

Making a Virtual Environment
============================

Developing in isolation helps us ensure what we are learning doesn't
conflict with any packages installed from other work on the machine.
*Virtual environments* let us do just this.

Python 3.3 has support for virtual environments using the ``pyvenv``
command. Since we are embracing Python 3.3, let's use its virtualenv
approach.

.. code-block:: bash

  $ path/to/python/bin/pyvenv-3.3 env33
  $ source env33/bin/activate
  (env33)$ which python3.3

Once you do this, your path will be setup to point at the ``bin`` of
your virtual environment. Your prompt will also change, as noted above.

.. note::

  If you are an OS X user that got your Python 3.3 from Homebrew,
  its pyvenv is broken (as of Feb 2013.) If you still want to use
  Homebrew, do ``pip install virtualenv`` and make your virtual
  environments with ``virtualenv``.

Installing Packaging Tools
==========================

Almost there. ``pyvenv`` doesn't copy any of the Python packaging tools
into your virtualenv. Fortunately this is easy and supported: just
download and install ``distribute``.

.. code-block:: bash

  (env33)$ curl -O http://python-distribute.org/distribute_setup.py
  (env33)$ python3.3 distribute_setup.py

.. note::

  Make sure the ``python3.3`` above is from your virtualenv!
