ASGI (Asynchronous Server Gateway Interface)
++++++++++++++++++++++++++++++++++++++++++++

This chapter contains information about using ASGI with
Pyramid. You can read more about the specification here: https://asgi.readthedocs.io/en/latest/index.html. 

The example app below uses the WSGI to ASGI wrapper from the `asgiref <https://pypi.org/project/asgiref/>`_ library to transform normal WSGI requests into ASGI responses - this allows the application to be run with an ASGI server, such as `uvicorn <http://www.uvicorn.org/>`_ or `daphne <https://github.com/django/daphne/>`_. 


WSGI -> ASGI application
------------------------

This example uses the wrapper provided by ``asgiref`` to convert a WSGI application to ASGI, this allows it to be run by an ASGI server.

Please note that not all extended features of WSGI may be supported (such as file handles for incoming POST bodies).

.. code-block:: python
    
    # app.py

    from asgiref.wsgi import WsgiToAsgi
    from pyramid.config import Configurator
    from pyramid.response import Response

      def hello_world(request):
        return Response("Hello")

    # Configure a normal WSGI app then wrap it with WSGI -> ASGI class

    with Configurator() as config:
        config.add_route("hello", "/")
        config.add_view(hello_world, route_name="hello")
        wsgi_app = config.make_wsgi_app()


    app = WsgiToAsgi(wsgi_app)


Extended WSGI -> ASGI WebSocket application
-------------------------------------------

The example extends the ``asgiref`` wrapper to enable routing ASGI consumers alongside the converted WSGI application. This is just one potential solution for routing ASGI consumers. 

.. code-block:: python
    
    # app.py

    from asgiref.wsgi import WsgiToAsgi

    from pyramid.config import Configurator
    from pyramid.response import Response


    class ExtendedWsgiToAsgi(WsgiToAsgi):

        """Extends the WsgiToAsgi wrapper to include an ASGI consumer protocol router"""

        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.protocol_router = {"http": {}, "websocket": {}}

        def __call__(self, scope, **kwargs):
            protocol = scope["type"]
            path = scope["path"]
            try:
                consumer = self.protocol_router[protocol][path]
            except KeyError:
                consumer = None
            if consumer is not None:
                return consumer(scope)
            return super().__call__(scope, **kwargs)

        def route(self, rule, *args, **kwargs):
            try:
                protocol = kwargs["protocol"]
            except KeyError:
                raise Exception("You must define a protocol type for an ASGI handler")

            def _route(func):
                self.protocol_router[protocol][rule] = func

            return _route


    HTML_BODY = """<!DOCTYPE html>
    <html>
        <head>
            <title>ASGI WebSocket</title>
        </head>
        <body>
            <h1>ASGI WebSocket Demo</h1>
            <form action="" onsubmit="sendMessage(event)">
                <input type="text" id="messageText" autocomplete="off"/>
                <button>Send</button>
            </form>
            <ul id='messages'>
            </ul>
            <script>
                var ws = new WebSocket("ws://127.0.0.1:8000/ws");
                ws.onmessage = function(event) {
                    var messages = document.getElementById('messages')
                    var message = document.createElement('li')
                    var content = document.createTextNode(event.data)
                    message.appendChild(content)
                    messages.appendChild(message)
                };
                function sendMessage(event) {
                    var input = document.getElementById("messageText")
                    ws.send(input.value)
                    input.value = ''
                    event.preventDefault()
                }
            </script>
        </body>
    </html>
    """

    # Define normal WSGI views


    def hello_world(request):
        return Response(HTML_BODY)


    # Configure a normal WSGI app then wrap it with WSGI -> ASGI class


    with Configurator() as config:
        config.add_route("hello", "/")
        config.add_view(hello_world, route_name="hello")
        wsgi_app = config.make_wsgi_app()


    app = ExtendedWsgiToAsgi(wsgi_app)


    # Define ASGI consumers


    @app.route("/ws", protocol="websocket")
    def hello_websocket(scope):

        async def asgi_instance(receive, send):
            while True:
                message = await receive()
                if message["type"] == "websocket.connect":
                    await send({"type": "websocket.accept"})
                if message["type"] == "websocket.receive":
                    text = message.get("text")
                    if text:
                        await send({"type": "websocket.send", "text": text})
                    else:
                        await send({"type": "websocket.send", "bytes": message.get("bytes")})

        return asgi_instance


Running & Deploying
-------------------

The application can be run using an ASGI server: 

.. code-block:: bash

    $ uvicorn app:app

or 

.. code-block:: bash

    $ daphne app:app


There are several potential deployment options, one example would be to use `nginx <https://nginx.org/>`_ and `supervisor <http://supervisord.org/>`_. Below are example configuration files that run the application using ``uvicorn``, however ``daphne`` may be used as well.

Example Nginx configuration
===========================

.. code-block:: bash

    upstream app {
        server unix:/tmp/uvicorn.sock;
    }

    server {

        listen 80;
        server_name <server-name>;

        location / {
            proxy_pass http://app;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
            proxy_buffering off;
            proxy_http_version 1.1;
            proxy_set_header Upgrade $http_upgrade;
            proxy_set_header Connection "Upgrade";
            proxy_redirect off;
        }

        location /static {
          root </path-to-static>;
        }
    }

Example Supervisor configuration
================================

.. code-block:: bash

    [program:asgiapp]
    directory=/path/to/app/
    command=</path-to-virtualenv>bin/uvicorn app:app --bind unix:/tmp/uvicorn.sock --workers 2 --access-logfile /tmp/uvicorn-access.log --error-logfile /tmp/uvicorn-error.log
    user=<app-user>
    autostart=true
    autorestart=true
    redirect_stderr=True
