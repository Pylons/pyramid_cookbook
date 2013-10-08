from pyramid.config import Configurator


def main(global_config, **settings):
    config = Configurator(settings=settings)
    config.include('pyramid_demo')

    print (settings)

    # Now do config.scan() in mydemo
    return config.make_wsgi_app()