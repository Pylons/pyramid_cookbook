from pyramid.config import Configurator


def main(global_config, **settings):
    config = Configurator(settings=settings)
    config.include('pyramid_jinja2')
    config.scan('pyramid_demo.views')
    return config.make_wsgi_app()