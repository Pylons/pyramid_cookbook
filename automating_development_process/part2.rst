Prerequisites
%%%%%%%%%%%%%

If you want to play with *pyramid_starter_seed* you'll need to install 
`NodeJS <http://nodejs.org/>`_ and, obviously, Python.
Once installed Python and Pyramid, you'll have to clone the 
pyramid_starter_seed repository from github and initialize the Yeoman stuff.

Python and Pyramid
==================

pyramid_starter_seed was tested with Python 2.7.
Create an isolated Python environment as explained in the official Pyramid 
documentation and install Pyramid.

Official Pyramid installation documentation

- http://docs.pylonsproject.org/projects/pyramid/en/latest/narr/install.html#installing-chapter

NodeJS
======

You won't use NodeJS at all in your code, you just need to install 
development dependencies required by the Yeoman tools.

Once installed NodeJS (if you want to easily install different versions 
on your system and manage them you can use the NodeJS Version Manager 
utility: `NVM <https://github.com/creationix/nvm>`_), you need to 
enable the following tools:

.. code-block:: bash

    $ npm install -g bower
    $ npm install -g grunt-cli
    $ npm install -g karma

Tested with NodeJS version 0.10.31.

How to install pyramid_starter_seed
===================================

Clone *pyramid_starter_seed* from github:

.. code-block:: bash

    $ git clone git@github.com:davidemoro/pyramid_starter_seed.git
    $ cd pyramid_starter_seed
    $ YOUR_VIRTUALENV_PYTHON_PATH/bin/python setup.py develop

Yeoman initialization
---------------------

Go to the folder where it lives our Yeoman project and initialize it.

These are the standard commands (but, wait a moment, see the "Notes and 
known issues" subsection):

.. code-block:: bash

    $ cd pyramid_starter_seed/webapp
    $ bower install
    $ npm install

Known issues
------------

You'll need to perform these additional steps in order to get a working 
environment (the generator-webapp's version used by pyramid_starter_seed 
has a couple of known issues).

Avoid imagemin errors on build:

.. code-block:: bash

    $ npm cache clean
    $ npm install grunt-contrib-imagemin

Avoid Mocha/PhantomJS issue (see 
`issues #446 <https://github.com/yeoman/generator-webapp/issues/446>`_):

.. code-block:: bash

    $ cd test
    $ bower install

Build
-----

Run:

.. code-block:: bash

    $ grunt build

Run pyramid_starter_seed
========================

Now can choose to run Pyramid in development or production mode.

Go to the root of your project directory, where the files `development.ini` 
and `production.ini` are located.

.. code-block:: bash

    cd ../../..

Just type:

.. code-block:: bash

    $ YOUR_VIRTUALENV_PYTHON_PATH/bin/pserve development.ini

or:

.. code-block:: bash

    $ YOUR_VIRTUALENV_PYTHON_PATH/bin/pserve production.ini

