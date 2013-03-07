from pyramid.view import view_config

class HelloWorld(object):
    def __init__(self, request):
        self.request = request

    @view_config(route_name='hello',
                 renderer='templates/helloworld.pt')
    def hello_world(self):
        return dict(title='Hello World')
