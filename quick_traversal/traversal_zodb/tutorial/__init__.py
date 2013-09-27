from pyramid.config import Configurator
from pyramid_zodbconn import get_connection

from .resources import bootstrap


def root_factory(request):
    conn = get_connection(request)
    return bootstrap(conn.root())

def main(global_config, **settings):
    config = Configurator(settings=settings,
                          root_factory=root_factory)
    config.scan('.views')
    return config.make_wsgi_app()
