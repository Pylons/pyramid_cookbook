from wsgiref.simple_server import make_server

from pyramid.config import Configurator
from pyramid.response import Response

def hello_world(request):
    return Response('hello!')

def main():
    config = Configurator()
    config.add_view(hello_world)
    app = config.make_wsgi_app()
    return app

if __name__ == '__main__':
    app = main()
    server = make_server('0.0.0.0', 8080, app)
    server.serve_forever()
