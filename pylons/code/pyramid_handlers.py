    # In the top-level __init__.py
    from .handlers import Hello
    def main(global_config, **settings):
        ...
        config.include("pyramid_handlers")
        config.add_handler("hello", "/hello/{action}", handler=Hello) 

    # In zzz/handlers.py
    from pyramid_handlers import action
    class Hello(object):
        __autoexpose__ = None

        def __init__(self, request):
            self.request = request

        @action
        def index(self):
            return Response('Hello world!')

        @action(renderer="mytemplate.mak")
        def bye(self):
            return {}
