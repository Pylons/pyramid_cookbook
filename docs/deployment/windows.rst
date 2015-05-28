Windows
+++++++

There are four possible deployment options for Windows:

#.  Run as a Windows service with a Python based web server like CherryPy or
    Twisted
#.  Run as a Windows service behind another web server (either IIS or Apache)
    using a reverse proxy
#.  Inside IIS using the WSGI bridge with ISAPI-WSGI
#.  Inside IIS using the WSGI bridge with PyISAPIe


Options 1 and 2: run as a Windows service
=========================================

Both Options 1 and 2 are quite similar to running the development server,
except that debugging info is turned off and you want to run the process as a
Windows service.

Install dependencies
--------------------

Running as a Windows service depends on the `PyWin32`_ project. You will need
to download the pre-built binary that matches your version of Python.

You can install directly into the virtualenv if you run ``easy_install`` on
the downloaded installer. For example::

    easy_install pywin32-217.win32-py2.7.exe

Since the web server for `CherryPy <http://www.cherrypy.org>`_ has good
Windows support, is available for Python 2 and 3, and can be gracefully
started and stopped on demand from the service, we'll use that as the web
server. You could also substitute another web server, like the one from
`Twisted <http://www.twistedmatrix.com>`_.

To install CherryPy run::

    pip install cherrypy


Create a Windows service
------------------------

Create a new file called ``pyramidsvc.py`` with the following code to define
your service::

    # uncomment the next import line to get print to show up or see early
    # exceptions if there are errors then run 
    #   python -m win32traceutil 
    # to see the output
    #import win32traceutil
    import win32serviceutil

    PORT_TO_BIND = 80
    CONFIG_FILE = 'production.ini'
    SERVER_NAME = 'www.pyramid.example'

    SERVICE_NAME = "PyramidWebService"
    SERVICE_DISPLAY_NAME = "Pyramid Web Service" 
    SERVICE_DESCRIPTION = """This will be displayed as a description \
    of the serivice in the Services snap-in for the Microsoft \
    Management Console."""

    class PyWebService(win32serviceutil.ServiceFramework):
        """Python Web Service."""
        
        _svc_name_ = SERVICE_NAME
        _svc_display_name_ = SERVICE_DISPLAY_NAME
        _svc_deps_ = None        # sequence of service names on which this depends
        # Only exists on Windows 2000 or later, ignored on Windows NT
        _svc_description_ = SERVICE_DESCRIPTION
        
        def SvcDoRun(self):
            from cherrypy import wsgiserver
            from pyramid.paster import get_app
            import os, sys

            path = os.path.dirname(os.path.abspath(__file__))

            os.chdir(path)

            app = get_app(CONFIG_FILE)

            self.server = wsgiserver.CherryPyWSGIServer(
                    ('0.0.0.0', PORT_TO_BIND), app,
                    server_name=SERVER_NAME)

            self.server.start()
            
        
        def SvcStop(self):
            self.server.stop()


    if __name__ == '__main__':
        win32serviceutil.HandleCommandLine(PyWebService)    

The ``if __name__ == '__main__'`` block provides an interface to register the
service. You can register the service with the system by running::
    
    python pyramidsvc.py install

Your service is now ready to start, you can do this through the normal service
snap-in for the Microsoft Management Console or by running::

    python pyramidsvc.py start

If you want your service to start automatically you can run::

    python pyramidsvc.py update --start=auto

Reverse proxy (optional)
------------------------

If you want to run many Pyramid applications on the same machine you will need
to run each of them on a different port and in a separate Service. If you want
to be able to access each one through a different host name on port 80, then
you will need to run another web server (IIS or Apache) up front and proxy
back to the appropriate service.

There are several options available for reverse proxy with IIS. In versions
starting with IIS 7, you can install and use the `Application Request Routing
<http://learn.iis.net/page.aspx/489/using-the-application-request-routing-module/>`_
if you want to use a Microsoft-provided solution. Another option is one of the
several solutions from `Helicon Tech <http://www.helicontech.com/>`_. Helicon
Ape is available without cost for up to 3 sites.

If you aren't already using IIS, Apache is available for Windows and works
well. There are many reverse proxy tutorials available for Apache, and they
are all applicable to Windows.

Options 3 and 4: Inside IIS using the WSGI bridge with ISAPI-WSGI
=================================================================

IIS configuration
-----------------

Turn on Windows feature for IIS.

Control panel -> "Turn Windows features on off" and select:

- Internet Information service (all)
- World Wide Web Services (all)

Create website
--------------

Go to Internet Information Services Manager and add website.

- Site name (your choice)
- Physical path (point to the directory of your Pyramid porject)
- select port
- select the name of your website

Python
------

- Install `PyWin32`_, according to your 32- or 64-bit installation
- Install `isapi-wsgi <https://code.google.com/p/isapi-wsgi/downloads/list>`_

Create bridging script
----------------------

Create a file ``install_website.py``, and place it in your pyramid project::
    
    # path to your site packages in your environment
    # needs to be put in here
    import site
    site.addsitedir('/path/to/your/site-packages')

    # this is used for debugging
    # after everything was installed and is ready to meka a http request
    # run this from the command line:
    # python -m python -m win32traceutil
    # It will give you debug output from this script
    # (remove the 3 lines for production use)
    import sys
    if hasattr(sys, "isapidllhandle"):
        import win32traceutil


    # this is for setting up a path to a temporary
    # directory for egg cache.
    import os
    os.environ['PYTHON_EGG_CACHE'] = '/path/to/writable/dir'
    
    # The entry point for the ISAPI extension.
    def __ExtensionFactory__():
        from paste.deploy import loadapp
        import isapi_wsgi
        from logging.config import fileConfig
    
        appdir = '/path/to/your/pyramid/project'
        configfile = 'production.ini'
        con = appdir + configfile
    
        fileConfig(con)
        application = loadapp('config:' + configfile, relative_to=appdir)
        return isapi_wsgi.ISAPIThreadPoolHandler(application)
    
    # ISAPI installation
    if __name__ == '__main__':
        from isapi.install import ISAPIParameters, ScriptMapParams, VirtualDirParameters, HandleCommandLine
    
        params = ISAPIParameters()
        sm = [
            ScriptMapParams(Extension="*", Flags=0)
        ]
    
        # if name = "/" then it will install on root 
        # if any other name then it will install on virtual host for that name
        vd = VirtualDirParameters(Name="/",
                                  Description="Description of your proj",
                                  ScriptMaps=sm,
                                  ScriptMapUpdate="replace"
        )
    
        params.VirtualDirs = [vd]
        HandleCommandLine(params)

Install your Pyramid project as Virtual Host or root feature
------------------------------------------------------------

Activate your virtual env and run the stript::

    python install_website.py install --server=<name of your website>

Restart your website from IIS.

.. _PyWin32: http://sourceforge.net/projects/pywin32/
