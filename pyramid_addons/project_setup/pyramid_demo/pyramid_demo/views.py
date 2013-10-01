from pyramid.view import (
    view_config,
    view_defaults
    )

@view_defaults(renderer='templates/home.jinja2')
class PyramidDemoViews:
    def __init__(self, request):
        self.request = request

    @view_config(name='home')
    def home(self):
        page_title = "Home View"
        return dict(page_title=page_title)
