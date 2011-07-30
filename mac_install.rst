How to Install Pyramid on Mac OS X
==================================

This guide will walk you through the steps of installing Pyramid on Mac OS X
from the very beginning.  This guide is targeted toward the complete newbie
to Pyramid and Python, and aims to simplify an often confusing process
fraught with frustrating pitfalls.

Pre-Requisites
--------------

- A Macintosh computer running Mac OS X (10.5.x or greater recommended).

- Xcode (recommended).
  
  At some point, you may need Xcode tools to "make" or compile applications
  from source code.  Experienced developers on the Mac know this, and by
  installing Xcode once, they "set it and forget it".
  
  - For 10.5.x, use Xcode 3.1.4.
  
  - For 10.6.x, use Xcode 3.2.x or later.
  
    Visit the `Apple Developer Connection`_ website to download a massive
    installer, or use the Mac OS X installation DVD that came with your
    computer.
    
    Optionally, 10.6.x and later can run Xcode 4.x.  However Apple charges a
    nominal fee to download Xcode 4 which is $4.99 at the time of this
    writing.  Visit the `Apple Developer Tools`_ website for more
    information.

- Python 2.7.x or greater, but less than Python 3.x.
  
  Python comes pre-installed on Mac OS X, but due to Apple's release cycle,
  it's often one or even two years old. The overwhelming recommendation of
  the "MacPython" community is to upgrade your Python by downloading and
  installing a newer version from the Python standard release page. [#]_.
  Note that using the pre-installed (aka "system" Python) is almost never a
  good idea on Mac OS X, even if the Python version happens to be fairly
  recent, due to heavy customizations made to the Python environment by Apple
  themselves.  Do yourself a favor and download and install a custom Python
  instead.
  
  `Python Releases`_

  At the time of this writing, Pyramid does not yet run under Python 3.x.

Configure Your Python Development Environment for Pyramid
---------------------------------------------------------

Next we need to configure a Python environment for developing Pyramid
applications by installing a few tools.

Install ez_setup.py for setuptools
++++++++++++++++++++++++++++++++++

Python projects often rely on third party modules to obtain added
functionality.  These modules are packaged using ``distutils``, and they
contain a Python script named ``setup.py``.  By executing this script, the
developer can quickly and easily install the modules from source.  Often it
is as easy as navigating to the directory containing the script, and
executing the following command::

  python setup.py install

and the module will install itself.

However, not all setup.py scripts are well-written and they may blindly
attempt to import the ``setuptools`` bootstrap module ``ez_setup.py`` even
though ``ez_setup.py`` is usually not installed on the user's machine.  `This
causes much trouble
<http://www.google.ca/search?q=%22ImportError:+No+module+named+ez_setup%22>`_. [#]_

To remedy the situation, we need to install the missing module
``ez_setup.py`` on our system.  Execute the following commands in Terminal::

  cd ~
  curl -O http://peak.telecommunity.com/dist/ez_setup.py
  sudo python ez_setup.py

Install virtualenv Using virtualenv-burrito
+++++++++++++++++++++++++++++++++++++++++++

virtualenv_ is a tool that creates clean sandboxes for development.  This
removes the potential for conflicts from existing system libraries and allows
you to isolate dependencies. [#]_

virtualenvwrapper_ is a tool that makes working with virtualenv_ easier [#]_,
and virtualenv-burrito_ is a single-command tool that installs and sets up
virtualenvwrapper_ for you. [#]_

Execute the following commands in Terminal::

  cd ~
  curl -s https://raw.github.com/brainsik/virtualenv-burrito/master/virtualenv-burrito.sh | bash

If successful, you will see this::

  
  Fin.
  
  Done with setup!
  
  The virtualenvwrapper environment will be available when you login.
  
  To start it now, run this:
  source /Users/<username>/.venvburrito/startup.sh

Next run this command, substituting your username for ``<username>``::

  source /Users/<username>/.venvburrito/startup.sh

And you will see this::

  To create a virtualenv, run:
  mkvirtualenv <cool-name>

That statement is a little incomplete.  Read on for an explanation.

Create a New virtualenv for Pyramid
+++++++++++++++++++++++++++++++++++

When making a new virtualenv, we do not want to include any dependencies from
outside the virtualenv, so we want to use the --no-site-packages flag.  Run
the command::

  mkvirtualenv --no-site-packages pyramid

Now activate the new virtualenv::

  workon pyramid

Now cd to the virtualenv directory::

  cd ~/.virtualenvs/pyramid

And now the moment you've been waiting for…

Install Pyramid
---------------

Run the command::

  bin/easy_install pyramid

Pyramid should now be installed.

What Next?
----------

Try the `Pyramid Quick Tutorial
<http://docs.pylonsproject.org/docs/pyramid_quick_tutorial.html>`_.

Read `Pyramid Documentation <http://docs.pylonsproject.org/docs/pyramid.html>`_.

Contribute to the Pylons Project Documentation
++++++++++++++++++++++++++++++++++++++++++++++

The Pylons Project documentation uses Sphinx_. [#]_ It is recommended to
install Sphinx_ into the current virtualenv using easy_install::

  easy_install -U Sphinx

Visit the `Sphinx website`_.

The Pylons Project documentation has several components.

- `Pylons Project documentation <http://docs.pylonsproject.org/>`_

- `Pylons Project repository including documentation <https://github.com/Pylons/pylonshq>`_

- `Pyramid Cookbook <http://docs.pylonsproject.org/projects/pyramid_cookbook/dev/>`_

- `Pyramid Cookbook repository <https://github.com/Pylons/pyramid_cookbook>`_

-----------

Footnotes
'''''''''
.. [#] `Python on the Mac`_
.. [#] `ez_setup <http://pypi.python.org/pypi/ez_setup>`_ (Sridhar Ratnakumar)
.. [#] `virtualenv`_ (Ian Bicking)
.. [#] `virtualenvwrapper`_ (Doug Hellmann)
.. [#] `virtualenv-burrito <https://github.com/brainsik/virtualenv-burrito>`_ (Jeremy Avnet)
.. [#] Sphinx_



.. _Python on the Mac: http://www.python.org/download/mac/
.. _Python Releases: http://www.python.org/download/releases/
.. _Apple Developer Connection: http://connect.apple.com/
.. _Apple Developer Tools: http://developer.apple.com/technologies/tools/
.. _virtualenv: http://www.virtualenv.org/en/latest/
.. _virtualenvwrapper: http://www.doughellmann.com/articles/pythonmagazine/completely-different/2008-05-virtualenvwrapper/index.html
.. _`Sphinx website`: Sphinx_
.. _Sphinx: http://sphinx.pocoo.org/
