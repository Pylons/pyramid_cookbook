from pyramid.view import view_config


class TutorialViews:
    def __init__(self, context, request):
        self.context = context
        self.request = request

    @view_config(renderer='home.jinja2')
    def home(self):
        return {'view_name': 'Home View'}
