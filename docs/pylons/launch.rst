Launching the Application
+++++++++++++++++++++++++

Pyramid and Pylons start up identically because they both use PasteDeploy and
its INI-format configuration file.  This is true even though Pyramid 1.3
replaced "paster serve" with its own "pserve" command. Both "pserve" and
"paster serve" do the following:

1. Read the INI file.
2. Instantiate an application based on the "[app:main]" section.
3. Instantiate a server based on the "[server:main]" section.
4. Configure Python logging based on the logging sections.
5. Call the server with the application.

Steps 1-3 and 5 are essentially wrappers around PasteDeploy. Only step 2 is
really "using Pyramid", because only the application depends on other parts of
Pyramid. The rest of the routine is copied directly from "paster serve" and
does not depend on other parts of Pyramid.

The way the launcher instantiates an application is often misunderstood so
let's stop for a moment and detail it. Here's part of the app section in the
Akhet Demo:

.. code-block:: ini

    [app:main]
    use = egg:akhet_demo#main
    pyramid.reload_templates = true
    pyramid.debug_authorization = false

The "use=" line indirectly names a Python callable to load. "egg:" says to look up a
Python object by entry point. (Entry points are a feature provided by
Setuptools, which is why Pyramid/Pylons require it or Distribute to be
installed.) "akhet_demo" is the name of the Python
distribution to look in (the Pyramid application), and "main" is the entry 
point. The launcher calls
``pkg_resources.require("akhet_demo#main")`` in Setuptools, and Setuptools
returns the Python object.  Entry points are defined in the distribution's
setup.py, and the installer writes them to an entry points file. Here's the
*akhet_demo.egg-info/entry_points.txt* file:

.. code-block:: ini

    [paste.app_factory]
    main = akhet_demo:main

"paste.app_factory" is the entry point group, a name publicized in the
PasteDeploy docs for all applications that want to be compatible with it.
"main" (on the left side of the equal sign) is the entry point.
"akhet_demo:main" says to import the ``akhet_demo`` package and load a "main"
attribute. This is our ``main()`` function defined in
*akhet_demo/\_\_init\_\_.py*. The other options in the "[app:main]" section
become keyword arguments to this callable. These options are called "settings"
in Pyramid and "config variables" in Pylons. (The options in the "[DEFAULT]"
section are also passed as default values.) Both frameworks provide a way to
access these variables in application code. In Pyramid they're in the
``request.registry.settings`` dict. In Pylons they're in the ``pylons.config``
magic global. 

The launcher loads the server in the same way, using the "[server:main]"
section.

*More details:* The heavy lifting is done by ``loadapp()`` and ``loadserver()``
in ``paste.deploy.loadwsgi``.  Loadwsgi is obtuse and undocumented, but
``pyramid.paster`` has some convenience functions that either call or mimic some of
its routines.

Alternative launchers such as mod_wsgi read only the "[app:main]" section and
ignore the server section, but they're still using PasteDeploy or the
equivalent. It's also possible to instantiate the application manually without an
INI file or PasteDeploy, as we'll see in the chapter called "The Main Function".

Now that we know more about how the launcher loads the application, let's look
closer at a Pyramid application itself.
