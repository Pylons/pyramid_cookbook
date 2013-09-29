from pyramid.view import view_config


class TutorialViews:
    def __init__(self, context, request):
        self.context = context
        self.request = request

    @view_config(renderer='templates/home.jinja2')
    def home(self):
        page_title = 'Quick Tutorial: Home'
        return dict(page_title=page_title)

    @view_config(name='hello', renderer='templates/hello.jinja2')
    def hello(self):
        page_title = 'Quick Tutorial: Hello'
        return dict(page_title=page_title)
