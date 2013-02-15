Windows
+++++++

There are 3 possible deployment scenarios for windows: 

1.  Run as a windows service with a Python based web server like CherryPy or
    Twisted.
2.  Run as a windows service behind another web server (either IIS or Apache)
    using a reverse proxy.
3.  Inside IIS using a in IIS WSGI bridge, either ISAPI-WSGI or PyISAPIe. These
    methods are more complicated and won't be covered by this guide.


Step 1: Install Dependencies
============================

Both method one and two are quite similar to running the development server
except that debugging info is turned off and you want to run the process as a
windows service. Running as a windows service depends on the 
`PyWin32 <http://sourceforge.net/projects/pywin32/>`_ project. You will need to
download the pre-built binary that matches your version of Python.

You can install directly into the virtualenv if you run easy_install on the
downloaded installer. For example::

    easy_install pywin32-217.win32-py2.7.exe
    

Since the web server for `CherryPy <http://www.cherrypy.org>`_ has good Windows
support, is available for Python 2 and 3 and can be gracefully started and
stopped on demand from the service, we'll use that as the web server. You could
also substitute another web server, like the one from `Twisted
<http://www.twistedmatrix.com>`_.

To install cherrypy run::
    
    pip install cherrypy


Step 2: Create a Windows Service
================================

Create a new file called ``pyramidsvc.py`` file with the following code to
define your service::

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
        # Only exists on Windows 2000 or later, ignored on windows NT
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
Service. You can register the service with the system by running::
    
    python pyramidsvc.py install


Your service is now ready to start, you can do this through the normal Service
snap-in for the Microsoft Management Console or by running::

    python pyramidsvc.py start


If you want your service to start automatically you can run::

    python pyramidsvc.py update --start=auto


Step 3: Reverse Proxy
=====================

If you want to run many Pyramid applications on the same machine you will need
to run each of them on a different port and in a separate Service. If you want
to be able to access each one through a different host name on port 80 then you
will need to run another web server (IIS or Apache) up front and proxy back to
the appropriate service. 

There are several options available for reverse proxy with IIS. Versions
starting with IIS 7 you can install and use the `Application Request Routing
<http://learn.iis.net/page.aspx/489/using-the-application-request-routing-module/>`_
if you want to use a Microsoft provided solution. Another option is one of the
several solutions from `Helicon Tech <http://www.helicontech.com/>`_. The
Helicon Ape is available without cost for up to 3 sites.

If you aren't already using IIS Apache is available for Windows and works well.
There are many reverse proxy tutorials available for Apache and they are equally
applicable to Windows.
