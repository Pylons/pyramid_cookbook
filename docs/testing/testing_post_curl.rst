Testing a POST request using cURL
---------------------------------

Using the following Pyramid application::

    from wsgiref.simple_server import make_server
    from pyramid.view import view_config
    from pyramid.config import Configurator
    
    @view_config(route_name='theroute', renderer='json', 
                 request_method='POST')
    def myview(request):
        return {'POST': request.POST.items()}
        
    if __name__ == '__main__':
        config = Configurator()
        config.add_route('theroute', '/')
        config.scan()
        app = config.make_wsgi_app()
        server = make_server('0.0.0.0', 6543, app)
        print server.base_environ
        server.serve_forever()

Once you run the above application, you can test a POST request to the
application via ``curl`` (available on most UNIX systems).

.. code-block:: text

    $ python application.py 
    {'CONTENT_LENGTH': '', 'SERVER_NAME': 'Latitude-XT2', 'GATEWAY_INTERFACE': 'CGI/1.1',
     'SCRIPT_NAME': '', 'SERVER_PORT': '6543', 'REMOTE_HOST': ''}
    

To access POST request body values (provided as the argument to the
``-d`` flag of ``curl``) use ``request.POST``.

.. code-block:: text

    $ curl -i -d "param1=value1&param2=value2" http://localhost:6543/
    HTTP/1.0 200 OK
    Date: Tue, 09 Sep 2014 09:34:27 GMT
    Server: WSGIServer/0.1 Python/2.7.5+
    Content-Type: application/json; charset=UTF-8
    Content-Length: 54
    
    {"POST": [["param1", "value1"], ["param2", "value2"]]}


To access QUERY_STRING parameters as well, use ``request.GET``.

.. code-block:: python

    @view_config(route_name='theroute', renderer='json', 
                 request_method='POST')
    def myview(request):
        return {'GET':request.GET.items(),
                'POST':request.POST.items()}


Append QUERY_STRING parameters to previously used URL and query with curl.

.. code-block:: text

    $ curl -i -d "param1=value1&param2=value2" http://localhost:6543/?param3=value3
    HTTP/1.0 200 OK
    Date: Tue, 09 Sep 2014 09:39:53 GMT
    Server: WSGIServer/0.1 Python/2.7.5+
    Content-Type: application/json; charset=UTF-8
    Content-Length: 85
    
    {"POST": [["param1", "value1"], ["param2", "value2"]], "GET": [["param3", "value3"]]}



Use ``request.params`` to have access to dictionary-like object
containing both the parameters from the query string and request body.

.. code-block:: python

    @view_config(route_name='theroute', renderer='json', 
                 request_method='POST')
    def myview(request):
        return {'GET':request.GET.items(),
                'POST':request.POST.items(),
                'PARAMS':request.params.items()}


Another request with curl.

.. code-block:: text

    $ curl -i -d "param1=value1&param2=value2" http://localhost:6543/?param3=value3
    HTTP/1.0 200 OK
    Date: Tue, 09 Sep 2014 09:53:16 GMT
    Server: WSGIServer/0.1 Python/2.7.5+
    Content-Type: application/json; charset=UTF-8
    Content-Length: 163
    
    {"POST": [["param1", "value1"], ["param2", "value2"]],
     "PARAMS": [["param3", "value3"], ["param1", "value1"], ["param2", "value2"]], 
     "GET": [["param3", "value3"]]}
    

Here's a simple Python program that will do the same as the ``curl`` command above does.

.. code-block:: python

    import httplib
    import urllib
    from contextlib import closing
    
    with closing(httplib.HTTPConnection("localhost", 6543)) as conn:
    	headers = {"Content-type": "application/x-www-form-urlencoded"}
    	params = urllib.urlencode({'param1': 'value1', 'param2': 'value2'})
    	conn.request("POST", "?param3=value3", params, headers)
    	response = conn.getresponse()
    	print response.getheaders()
    	print response.read()


Running this program on a console.

.. code-block:: text

    $ python request.py 
    [('date', 'Tue, 09 Sep 2014 10:18:46 GMT'), ('content-length', '163'), ('content-type', 'application/json; charset=UTF-8'), ('server', 'WSGIServer/0.1 Python/2.7.5+')]
    {"POST": [["param2", "value2"], ["param1", "value1"]], "PARAMS": [["param3", "value3"], ["param2", "value2"], ["param1", "value1"]], "GET": [["param3", "value3"]]}
