from pyramid.view import view_config


class TutorialViews:
    def __init__(self, context, request):
        self.context = context
        self.request = request

    @view_config(renderer='home.pt')
    def home(self):
        parent = self.context.__parent__
        if parent:
            parent_title = parent.title
        else:
            parent_title = 'No Parent'
        return {
            'view_name': 'Home View',
            'name': self.context.__name__,
            'parent_title': parent_title,
            }