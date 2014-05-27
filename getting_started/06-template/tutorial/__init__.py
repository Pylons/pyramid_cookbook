from pyramid.config import Configurator


def main(global_config, **settings):
    config = Configurator(settings=settings)
    config.include('pyramid_chameleon')
    config.add_route('hello', '/')
    config.scan()
    return config.make_wsgi_app()
