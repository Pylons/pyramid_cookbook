Installing Pyramid
=========================

This is a quick guide to getting Pyramid set up, it should be good enough
for most use cases. If you run into some problem and need more detailed help
or if you are using a different platform, please consult our
`detailed installation guide
<http://docs.pylonsproject.org/projects/pyramid/1.0/narr/install.html>`_.

Before You Install
------------------

You will need Python version 2.4 or better to
run Pyramid. Pyramid doesn't run on Python 3 yet, but we're working
on it. `Get Python now <http://www.python.org/download/>`_.

Pyramid is known to run on all popular Unix-like systems such as
Linux, MacOS X, and FreeBSD as well as on Windows platforms.  It is also
known to run on Google's App Engine and :term:`Jython`.

It is best practice to install Pyramid into a "virtual"
Python environment in order to obtain isolation from any "system"
packages you've got installed in your Python version.  This can be
done by using the :term:`virtualenv` package.  Using a virtualenv will
also prevent Pyramid from globally installing versions of
packages that are not compatible with your system Python.

To install virtualenv you will need setuptools.  Once you've got
setuptools installed, you should install the :term:`virtualenv` package
using the ``easy_install`` command.

.. code-block:: text

   $ easy_install virtualenv


Installing Pyramid Into the Virtual Python Environment
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

After you've got your ``env`` virtualenv installed, you may install
Pyramid itself using the following commands from within the
virtualenv (``env``) directory:

.. code-block:: text

   $ bin/easy_install pyramid

This command will take longer than the previous ones to complete, as it
downloads and installs a number of dependencies.

What Gets Installed
-------------------

When you ``easy_install`` Pyramid, various Zope libraries,
various Chameleon libraries, WebOb, Paste, PasteScript, and
PasteDeploy libraries are installed.

Additionally, as chronicled in :ref:`project_narr`, PasteScript (aka
*paster*) templates will be registered that make it easy to start a
new Pyramid project.
