.. _appengine_buildout_tutorial:


:app:`Pyramid` on Google's App Engine (using buildout)
======================================================

This is but one way to develop applications to run on Google's `App
Engine <http://code.google.com/appengine/>`_. This one uses `buildout
<http://www.buildout.org>`_ . For a different approach, you may want
to look at :ref:`appengine_tutorial`.


Install the pyramid_appengine scaffold
--------------------------------------

Let's take it step by step.

You can get `pyramid_appengine
<http://pypi.python.org/pypi/pyramid_appengine/>`_ from pypi via `pip <http://pypi.python.org/pypi/pip>`_
just as you typically would any other python package, however to reduce the
chances of the system installed python packages intefering with tools
you use for your own development you should install it in a local
`virtual environment <http://pypi.python.org/pypi/virtualenv>`_

Creating a virtual environment
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Update distribute
+++++++++++++++++

.. code-block:: text

   $ sudo pip install --upgrade distribute


Install virtualenv
++++++++++++++++++

.. code-block:: text

   $ sudo pip install virtualenv


create a virtual environment
++++++++++++++++++++++++++++

.. code-block:: text

   $ virtualenv -p /usr/bin/python2.7 --no-site-packages --distribute myenv


install pyramid_appengine into your virtual environment
+++++++++++++++++++++++++++++++++++++++++++++++++++++++

.. code-block:: text

   $ myenv/bin/pip install pyramid_appengine



Once successfully installed a new project template is available to use
named "appengine_starter".

To get a list of all available templates.

.. code-block:: text

   $ myenv/bin/pcreate -l

Create the skeleton for your project
------------------------------------

You create your project skeleton using the "appengine_starter" project
scaffold just as you would using any other project scaffold. 

.. code-block:: text

   $ myenv/bin/pcreate -t appengine_starter newproject

Once successfully ran, you will have a new `buildout <http://www.buildout.org>`_ directory for your project. The app engine
application source is located at newproject/src/newproject.

This buildout directory can be added to version control if you like,
using any of the available version control tools available to you.

Bootstrap the buildout
----------------------

Before you do anything with a new buildout directory you need to
bootstrap it, which installs buildout locally and everything necessary
to manage the project dependencies.

As with all buildouts, it can be bootstrapped running the following
commands. 

.. code-block:: text

   ~/ $ cd newproject
   ~/newproject $ ../bin/python2.7 bootstrap.py

You typically only need to do this once to generate your
buildout command. See the `buildout documentation <http://www.buildout.org/docs/tutorial.html#buildout-steps>`_ for more information.


Run buildout
------------

As with all buildouts, after it has been bootstrapped, a "bin"
directory is created with a new buildout command. This command is run
to install things based on the newproject/buildout.cfg which you can
edit to suit your needs.

.. code-block:: text

   ~/newproject $ ./bin/buildout 

In the case of this particular buildout, when run, it will take care
of several things that you need to do....

  #. install the app engine SDK in parts/google_appengine `more info <http://pypi.python.org/pypi/rod.recipe.appengine>`_
  #. Place tools from the appengine SDK in the buildout's "bin" directory.
  #. Download/install the dependencies for your project including pyramid and all it's
     dependencies not already provided by the app engine SDK. 
     `more info <http://pypi.python.org/pypi/rod.recipe.appengine>`_
  #. A directory structure appropriate for deploying to app engine at
     newproject/parts/newproject. `more info <http://pypi.python.org/pypi/rod.recipe.appengine>`_
  #. Download/Install tools to support unit testing including `pytest <http://pytest.org>`_, and `coverage <http://nedbatchelder.com/code/coverage/>`_.


Run your tests
--------------

Your project is configured to run all tests found in files that begin with "test\_"(example: newproject/src/newproject/newproject/test_views.py).

.. code-block:: text

   ~/newproject/ $ cd src/newproject
   ~/newproject/src/newproject/ $ ../../bin/python setup.py test

Your project incorporates the `unit testing tools <http://code.google.com/appengine/docs/python/tools/localunittesting.html>`_ provided by the app engine SDK to setUp and tearDown the app engine environment for each of your tests. In addition to that, running the unit tests will keep your projects `index.yaml <http://code.google.com/appengine/docs/python/config/indexconfig.html>`_ up to date. As a result, maintaining a thorough test suite will be your best chance at insuring that your application is ready for deployment.

You can adjust how the app engine api's are initialized for your tests by editing newproject/src/newproject/newproject/conftest.py.

Run your application locally
----------------------------
You can run your application using the app engine SDK's `Development Server <http://code.google.com/appengine/docs/python/tools/devserver.html>`_

.. code-block:: text

   ~/newproject/ $ ./bin/devappserver parts/newproject

Point your browser at `http://localhost:8080 <http://localhost:8080>`_
to see it working.


Deploy to App Engine
--------------------

Note: Before you can upload any appengine application you must create an `application ID <http://code.google.com/appengine/docs/python/gettingstarted/uploading.html>`_ for it. 

To upload your application to app engine, run the following command. For more information see App Engine Documentation for `appcfg <http://code.google.com/appengine/docs/python/tools/uploadinganapp.html#Uploading_the_App>`_

.. code-block:: text

   ~/newproject/ $ ./bin/appcfg update parts/newproject -A newproject -V dev

Point your browser at `http://dev.newproject.appspot.com <http://dev.newproject.appspot.com>`_ to see it working.

The above command will most likely not work for you, it is just an
example. the "-A" switch indicates an `Application ID <http://code.google.com/appengine/docs/python/gettingstarted/uploading.html>`_ to deploy to and overrides the setting in the app.yaml, use the Application ID you created when you registered the application instead. The "-V" switch specifies the version and overrides the setting in your app.yaml. 

You can set which version of your application handles requests by
default in the `admin console <http://appengine.google.com>`_. However you can also specify a version of your application to hit in the URL like so...

.. code-block:: text

   http://<app-version>.<application-id>.appspot.com

This can come in pretty handy in a variety of scenarios that become obvious once you start managing the development of your application while supporting a current release. 
