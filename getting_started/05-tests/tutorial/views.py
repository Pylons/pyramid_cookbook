from pyramid.response import Response
from pyramid.view import view_config

@view_config(route_name='hello')
def hello_world(request):
    return Response('Hello')
