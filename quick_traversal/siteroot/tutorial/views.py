from pyramid.view import view_config


class TutorialViews:
    def __init__(self, context, request):
        self.context = context
        self.request = request

    @view_config(name='hello', renderer='templates/site.jinja2')
    def home(self):
        page_title = 'Quick Tutorial: Site View'
        return dict(page_title=page_title)
