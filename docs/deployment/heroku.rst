Heroku
++++++

`Heroku <http://www.heroku.com/>`_ recently added `support for a process model
<http://blog.heroku.com/archives/2011/5/31/celadon_cedar/>`_ which allows
deployment of Pyramid applications.

This recipe assumes that you have a Pyramid application setup using a Paste
INI file, inside a package called ``myapp``. This type of structure is found in
the ``pyramid_starter`` scaffold, and other Paste scaffolds (previously called
project templates). It can be easily modified to work with other Python web
applications as well by changing the command to run the application as
appropriate.

Step 0: Install Heroku
======================

Install the heroku gem `per their instructions
<http://devcenter.heroku.com/articles/quickstart>`_.

Step 1: Add files needed for Heroku
===================================

You will need to add the following files with the contents as shown to the
root of your project directory (the directory containing the ``setup.py``).

``requirements.txt``
--------------------

You can autogenerate this file with the following command.

.. code-block:: bash

    $ pip freeze > requirements.txt

In your ``requirements.txt`` file, you will probably have a line with your
project's name in it. It might look like either of the following two lines
depending on how you setup your project. If either of these lines exist,
delete them.

.. code-block:: text

    project-name=0.0

    # or

    -e git+git@xxxx:<git username>/xxxxx.git....#egg=project-name

.. note::

    You can only use packages that can be installed with pip (e.g., those on
    PyPI, those in a git repo, using a git+git:// url, etc.). If you have any
    that you need to install in some special way, you will have to do that in
    your ``run`` file (see below). Also note that this will be done for every
    instance startup, so it needs to complete quickly to avoid being killed by
    Heroku (there's a 60-second instance startup timeout). Never include
    editable references when deploying to Heroku.

``Procfile``
------------

Generate ``Procfile`` with the following command.

.. code-block:: bash
    
    $ echo "web: ./run" > Procfile

``run``
-------

Create ``run`` with the following command.

.. code-block:: bash
    
    #!/bin/bash
    set -e
    python setup.py develop
    python runapp.py

.. note::
    
    Make sure to ``chmod +x run`` before continuing. The ``develop`` step is
    necessary because the current package must be installed before Paste can
    load it from the INI file.

``runapp.py``
-------------

If using a version greater than or equal to 1.3 (e.g. >= 1.3), use the
following for ``runapp.py``.

.. code-block:: python

    import os

    from paste.deploy import loadapp
    from waitress import serve

    if __name__ == "__main__":
        port = int(os.environ.get("PORT", 5000))
        app = loadapp('config:production.ini', relative_to='.')

        serve(app, host='0.0.0.0', port=port)

For versions of Pyramid prior to 1.3 (e.g. < 1.3), use the following for
``runapp.py``.
    
.. code-block:: python
    
    import os

    from paste.deploy import loadapp
    from paste import httpserver

    if __name__ == "__main__":
        port = int(os.environ.get("PORT", 5000))
        app = loadapp('config:production.ini', relative_to='.')

        httpserver.serve(app, host='0.0.0.0', port=port)

.. note::
    
    We assume the INI file to use is named ``production.ini``, so change the
    content of ``runapp.py`` as necessary. The server section of the INI will
    be ignored as the server needs to listen on the port supplied in the OS
    environment.

Step 2: Setup git repo and Heroku app
=====================================

Navigate to your project directory (directory with ``setup.py``) if not
already there. If your project is already under git version control, skip to
the "Initialize the Heroku stack" section.

Inside your project's directory, if this project is not tracked under git, it
is recommended yet optional to create a good ``.gitignore`` file. You can get
the recommended python one by running the following command.

.. code-block:: bash

    $ wget -O .gitignore https://raw.github.com/github/gitignore/master/Python.gitignore

Once that is done, run the following command.

.. code-block:: bash
    
    $ git init
    $ git add .
    $ git commit -m "initial commit"

Step 3: Initialize the Heroku stack
===================================

.. code-block:: bash
    
    $ heroku create --stack cedar

Step 4: Deploy
==============

To deploy a new version, push it to Heroku.

.. code-block:: bash
    
    $ git push heroku master

Make sure to start one worker.

.. code-block:: bash

    $ heroku scale web=1

Check to see if your app is running.

.. code-block:: bash
    
    $ heroku ps

Take a look at the logs to debug any errors if necessary.

.. code-block:: bash
    
    $ heroku logs -t

Tips and Tricks
===============

The CherryPy WSGI server is fast, efficient, and multi-threaded to easily
handle many requests at once. If you want to use it you can add ``cherrpy``
and ``pastescript`` to your ``setup.py:requires`` section (be sure to re-run
``pip freeze`` to update the requirements.txt file as explained above) and
setup your ``runapp.py`` to look like the following.

.. code-block:: python

    import os

    from paste.deploy import loadapp
    from paste.script.cherrypy_server import cpwsgi_server

    if __name__ == "__main__":
        port = int(os.environ.get("PORT", 5000))
        wsgi_app = loadapp('config:production.ini', relative_to='.')
        cpwsgi_server(wsgi_app, host='0.0.0.0', port=port,
                      numthreads=10, request_queue_size=200)

Heroku add-ons generally communicate their settings via OS environment
variables. These can be easily incorporated into your applications settings as
show in the following example.

.. code-block:: python

    # In your pyramid apps main init
    import os
    
    from pyramid.config import Configurator
    from myproject.resources import Root

    def main(global_config, **settings):
        """ This function returns a Pyramid WSGI application.
        """

        # Look at the environment to get the memcache server settings
        memcache_server = os.environ.get('MEMCACHE_SERVERS')

        settings['beaker.cache.url'] = memcache_server
        config = Configurator(root_factory=Root, settings=settings)
        config.add_view('myproject.views.my_view',
                        context='myproject.resources.Root',
                        renderer='myproject:templates/mytemplate.pt')
        config.add_static_view('static', 'myproject:static')
        return config.make_wsgi_app()
