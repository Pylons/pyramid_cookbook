from wsgiref.simple_server import make_server

from pyramid.config import Configurator
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
    config.include('pyramid_chameleon')
    config.scan("views")
    app = config.make_wsgi_app()
    return app


if __name__ == '__main__':
    app = main()
    server = make_server(host='0.0.0.0', port=8080, app=app)
    server.serve_forever()
