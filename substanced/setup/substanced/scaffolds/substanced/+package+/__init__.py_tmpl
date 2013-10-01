from pyramid.config import Configurator

from substanced.db import root_factory

def main(global_config, **settings):
    """ This function returns a Pyramid WSGI application.
    """
    config = Configurator(settings=settings, root_factory=root_factory)
    config.include('substanced')
    config.scan()
    return config.make_wsgi_app()
