from pyramid.config import Configurator

from .resources import bootstrap


def main(global_config, **settings):
    config = Configurator(settings=settings,
                          root_factory=bootstrap)
    config.scan('.views')
    return config.make_wsgi_app()
