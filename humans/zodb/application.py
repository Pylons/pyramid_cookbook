from wsgiref.simple_server import make_server

from pyramid.config import Configurator
from pyramid_zodbconn import get_connection

from resources import bootstrap


def root_factory(request):
    conn = get_connection(request)
    return bootstrap(conn.root())


def main():
    settings = {"zodbconn.uri": "file://Data.fs"}
    config = Configurator(root_factory=root_factory, settings=settings)
    config.include('pyramid_chameleon')
    config.include("pyramid_zodbconn")
    config.include("pyramid_tm")
    config.add_static_view('static', 'deform:static')
    config.scan("views")
    app = config.make_wsgi_app()
    return app


if __name__ == '__main__':
    app = main()
    server = make_server(host='0.0.0.0', port=8080, app=app)
    server.serve_forever()
