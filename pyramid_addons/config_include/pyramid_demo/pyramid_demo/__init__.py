
def includeme(config):
    config.include('pyramid_jinja2')
    config.scan('.views')