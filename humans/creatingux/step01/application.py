from wsgiref.simple_server import make_server

from pyramid.config import Configurator
from pyramid.response import Response

# This acts as the view function
def hello_world(request):
    return Response('hello!')

def main():
    # Grab the config, add a view, and make a WSGI app
    config = Configurator()
    config.add_view(hello_world)
    app = config.make_wsgi_app()
    return app

if __name__ == '__main__':
    # When run from command line, launch a WSGI server and app
    app = main()
    server = make_server('0.0.0.0', 8080, app)
    server.serve_forever()
