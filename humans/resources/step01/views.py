from pyramid.response import Response
from pyramid.view import view_config

class ProjectorViews(object):
    def __init__(self, context, request):
        self.context = context
        self.request = request

    @view_config()
    def default_view(self):
        body = "This SiteFolder is named: " + self.context.title
        return Response(body)

