from pyramid.config import Configurator
from paste.httpserver import serve

def main():
    config = Configurator()
    config.scan("views")
    config.add_static_view('deform_static', 'deform:static')
    app = config.make_wsgi_app()
    return app

if __name__ == '__main__':
    app = main()
    serve(app, host='0.0.0.0')
