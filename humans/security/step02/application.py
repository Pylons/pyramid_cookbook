from pyramid.config import Configurator
from paste.httpserver import serve
from pyramid.authentication import AuthTktAuthenticationPolicy

from resources import bootstrap

from usersdb import groupfinder

def main():
    config = Configurator(
        root_factory=bootstrap,
        authentication_policy=AuthTktAuthenticationPolicy(
            'seekr1t',
            callback=groupfinder)
    )
    config.scan("views")
    app = config.make_wsgi_app()
    return app

if __name__ == '__main__':
    app = main()
    serve(app, host='0.0.0.0')
