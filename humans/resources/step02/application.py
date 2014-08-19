from wsgiref.simple_server import make_server

from pyramid.config import Configurator
from resources import bootstrap


def main():
    config = Configurator(root_factory=bootstrap)
    config.include('pyramid_chameleon')
    config.scan("views")
    app = config.make_wsgi_app()
    return app


if __name__ == '__main__':
    app = main()
    server = make_server(host='0.0.0.0', port=8080, app=app)
    server.serve_forever()
