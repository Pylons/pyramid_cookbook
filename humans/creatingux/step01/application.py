from paste.httpserver import serve
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
    serve(app, host='0.0.0.0')
