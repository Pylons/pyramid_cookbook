.. _appengine_tutorial:

:app:`Pyramid` on Google's App Engine
==============================================================

It is possible to run a :app:`Pyramid` application on Google's `App
Engine <https://cloud.google.com/appengine/>`_.  This
tutorial is written in terms of using the command line on a UNIX
system; it should be possible to perform similar actions on a Windows
system. This tutorial also assumes you've already installed and created a :app:`Pyramid` application,
and that you have an App Engine account to deploy to.

Setup
-----

First we'll need to create a few files so that App Engine can communicate with our project properly.

Create a ``requirements.txt`` file, a ``main.py`` file, an ``app.yaml`` file, and an ``appengine_config.py`` file.

#. Edit ``requirements.txt``

Add the following lines:

.. code-block:: text
    :linenos:

    Pyramid
    waitress
    pyramid_debugtoolbar
    pyramid_chameleon

#. Edit ``main.py``

Add the following lines::

.. code-block:: python
    from pyramid.paster import get_app, setup_logging
    ini_path = 'production.ini'
    setup_logging(ini_path)
    application = get_app(ini_path, 'main')

#. Edit ``appengine_config.py``

Add the following lines::

.. code-block:: python

    from google.appengine.ext import vendor
    vendor.add('lib')

#. Edit ``app.yaml``

Add the following lines:

.. code-block:: yaml

    application: application-id
    version: version
    runtime: python27
    api_version: 1
    threadsafe: false

    handlers:
    - url: /static
      static_dir: pyramid_project/static
    - url: /.*
      script: main.application

Replace `application` with your App Engine app ID, `version` with the version you want to deploy to, and `pyramid_project`
in the `static_dir` definition with the directory name above your static assets. If your static assets are in the root
directory, you can just put `static`

For more details about app.yaml, see `app.yaml Reference <https://cloud.google.com/appengine/docs/standard/python/config/appref>`_.


#. Install dependencies

.. code-block:: bash

    $ pip install -t lib -r requirements.txt


Running Locally
---------------

At this point you should have everything you need to run your Pyramid application locally using dev_appserver.
Assuming you have appengine in your $PATH,

.. code-block:: text

  $ dev_appserver.py app.yaml

And voilà! You should have a perfectly-running Pyramid application running under Google App Engine, on your local machine.

Deploying
---------

Deploying to App Engine is pretty straight forward. If you've successfully launched your application locally,
deploying is just as easy.

.. code-block:: text

  $ appcfg.py update app.yaml

Your Pyramid application is now live to the world! You can access it by navigation to your domain name, or by
`applicationid.appspot.com`, or if you've specified a version outside of your default, it would
be `version-dot-applicationid.appspot.com`
