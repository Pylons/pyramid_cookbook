.. _appengine_tutorial:

Google App Engine Standard and :app:`Pyramid`
=============================================

It is possible to run a :app:`Pyramid` application on `Google App Engine <https://cloud.google.com/appengine/>`_.  This tutorial is written in terms of using the command line on a UNIX system. It should be possible to perform similar actions on a Windows system. This tutorial also assumes you've already installed and created a :app:`Pyramid` application, and that you have a Google App Engine account.

Setup
-----

First we'll need to create a few files so that App Engine can communicate with our project properly.

Create the files with content as follows.

#.  ``requirements.txt``

    .. code-block:: text

        Pyramid
        waitress
        pyramid_debugtoolbar
        pyramid_chameleon

#.  ``main.py``

    .. code-block:: python

        from pyramid.paster import get_app, setup_logging
        ini_path = 'production.ini'
        setup_logging(ini_path)
        application = get_app(ini_path, 'main')

#.  ``appengine_config.py``

    .. code-block:: python

        from google.appengine.ext import vendor
        vendor.add('lib')

#.  ``app.yaml``

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

    Configure this file with the following values:

    * Replace "application-id" with your App Engine application's ID.
    * Replace "version" with the version you want to deploy.
    * Replace "pyramid_project" in the definition for ``static_dir`` with the parent directory name of your static assets. If your static assets are in the root directory, you can just put "static".

    For more details about ``app.yaml``, see `app.yaml Reference <https://cloud.google.com/appengine/docs/standard/python/config/appref>`_.

#.  Install dependencies.

    .. code-block:: bash

        $ pip install -t lib -r requirements.txt


Running locally
---------------

At this point you should have everything you need to run your Pyramid application locally using ``dev_appserver``. Assuming you have appengine in your ``$PATH``:

.. code-block:: bash

  $ dev_appserver.py app.yaml

And voilà! You should have a perfectly-running Pyramid application via Google App Engine on your local machine.


Deploying
---------

If you've successfully launched your application locally, deploy with a single command.

.. code-block:: bash

    $ appcfg.py update app.yaml

Your Pyramid application is now live to the world! You can access it by navigating to your domain name, by "<applicationid>.appspot.com", or if you've specified a version outside of your default then it would be "<version-dot-applicationid>.appspot.com".
