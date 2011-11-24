from pyramid.config import Configurator
from paste.httpserver import serve

from resources import bootstrap

def main():
    config = Configurator(root_factory=bootstrap)
    config.scan("views")
    config.add_static_view('static', 'static/',
                           cache_max_age=86400)
    app = config.make_wsgi_app()
    return app

if __name__ == '__main__':
    app = main()
    serve(app, host='0.0.0.0')
