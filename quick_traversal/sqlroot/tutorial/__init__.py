from pyramid.config import Configurator

from sqlalchemy import engine_from_config

from .models import (
    DBSession,
    Base,
    root_factory
    )


def main(global_config, **settings):
    engine = engine_from_config(settings, 'sqlalchemy.')
    DBSession.configure(bind=engine)
    Base.metadata.bind = engine

    config = Configurator(settings=settings,
                          root_factory=root_factory)
    config.include('pyramid_jinja2')
    config.scan('.views')
    return config.make_wsgi_app()
