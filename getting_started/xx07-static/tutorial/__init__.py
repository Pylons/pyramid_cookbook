from pyramid.config import Configurator


def main(global_config, **settings):
    config = Configurator(settings=settings)
    config.add_route('hello', '/')
    config.add_static_view(name='static', path='tutorial:static')
    config.scan()
    return config.make_wsgi_app()
