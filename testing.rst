Testing a POST Request Using cURL
---------------------------------

Using the following Pyramid application:

.. code-block:: python

    from pyramid.view import view_config

    @view_config(route_name='theroute', renderer='string', 
                 request_method='POST')
    def myview(request):
        print request.GET.items()
        print request.POST.items()
        print request.params.items()
        return 'OK'
        
    if __name__ == '__main__':
        from pyramid.config import Configurator
        from paste.httpserver import serve
        config = Configurator()
        config.add_route('theroute', '/')
        config.scan('__main__')
        serve(config.make_wsgi_app())

Once your run the above application, you can test a POST request to the
application via ``curl`` (available on most UNIX systems):

.. code-block: text

   $ curl -d "param1=value1&param2=value2" http://localhost:8080/?param3=value3

You'll see the following output on the application terminal:

.. code-block:: text

    [('param3', u'value3')]
    [('param1', u'value1'), ('param2', u'value2')]
    [('param3', u'value3'), ('param1', u'value1'), ('param2', u'value2')]

Note the relationship between the query string and ``request.GET``.  Note the
relationship between the POST body values (provided as the argument to the
``-d`` flag of ``curl``) and ``request.POST``.  Note that ``request.params``
is an amalgamation of ``request.GET`` and ``request.POST`` values.
