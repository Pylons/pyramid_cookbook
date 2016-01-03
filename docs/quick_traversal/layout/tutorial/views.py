from pyramid.view import view_config


class TutorialViews(object):
    def __init__(self, request):
        self.request = request

    @view_config(name='hello', renderer='templates/site.jinja2')
    def site(self):
        page_title = 'Quick Tutorial: Site View'
        return dict(page_title=page_title)
