heroku
++++++

`heroku <http://www.heroku.com/>`_ recently added `support for a process model
<http://blog.heroku.com/archives/2011/5/31/celadon_cedar/>`_ which allows
deployment of Pyramid applications. While there is currently **no official
support** for Python/Pyramid web applications, the current stack does support
it.

This recipe assumes that you have a pyramid app setup using a Paste INI file,
inside a package called 'myapp'. This type of structure is found in the
pyramid_starter scaffold, and other Paste scaffolds (previously called project
templates). It can be easily modified to work with other Python web
applications as well by changing the command to run the app as appropriate.

Step 0: Install heroku
======================

Install the heroku gem `per their instructions
<http://devcenter.heroku.com/articles/quickstart>`_.

Step 1: Add files needed for heroku
===================================

You will need to add the following files with the contents as shown to the
root of your project directory (the directory containing the setup.py).

``requirements.txt``:

.. code-block:: text
    
    Pyramid==1.0
    # Add any other dependencies that should be installed as well

``Procfile``:

.. code-block:: text
    
    web: ./run

``run``:

.. code-block:: text
    
    #!/bin/bash
    bin/python setup.py develop
    bin/python runapp.py

.. note::
    
    Make sure to ``chmod +x run`` before continuing.
    The 'develop' step is necessary because the current package must be
    installed before paste can load it from the INI file.

``runapp.py``::
    
    import os

    from paste.deploy import loadapp
    from paste.script.cherrypy_server import cpwsgi_server

    if __name__ == "__main__":
        port = int(os.environ.get("PORT", 5000))
        wsgi_app = loadapp('config:production.ini', relative_to='.')
        cpwsgi_server(wsgi_app, host='0.0.0.0', port=port,
                      numthreads=10, request_queue_size=200)

.. note::
    
    This assumes the INI file to use is ``production.ini``, change as
    necessary. The server section of the INI will be ignored as the server
    needs to listen on the port supplied in the OS environ.

Step 2: Setup git repo and heroku app
=====================================

Inside your projects directory, if this project is not tracked under git, run:

.. code-block:: bash
    
    $ git init
    $ git add .
    $ git commit -m init

Next, initialize the heroku stack:

.. code-block:: bash
    
    $ heroku create --stack cedar

Step 3: Deploy
==============

To deploy a new version, push it to heroku:

.. code-block:: bash
    
    $ git push heroku master

If your app is not up and running, take a look at the logs:

.. code-block:: bash
    
    $ heroku logs

Tips & Tricks
=============

The CherryPy WSGI server is fast, efficient, and multi-threaded to easily
handle many requests at once. If you're deploying small and/or low-traffic
websites you can use the `PasteDeploy composite capabilities
<http://pythonpaste.org/deploy/#composite-applications>`_ to serve multiple
web applications with a single Heroku web dyno.

Heroku add-on's generally communicate their settings via OS environ variables.
These can be easily incorporated into your applications settings, for
example::
    
    # In your pyramid apps main init
    import os
    
    from pyramid.config import Configurator
    from myproject.resources import Root

    def main(global_config, **settings):
        """ This function returns a Pyramid WSGI application.
        """
        memcache_server = os.environ.get('MEMCACHE_SERVERS')
        settings['beaker.cache.url'] = memcache_server
        config = Configurator(root_factory=Root, settings=settings)
        config.add_view('myproject.views.my_view',
                        context='myproject.resources.Root',
                        renderer='myproject:templates/mytemplate.pt')
        config.add_static_view('static', 'myproject:static')
        return config.make_wsgi_app()
