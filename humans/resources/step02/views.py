from pyramid.view import view_config

class ProjectorViews(object):
    def __init__(self, context, request):
        self.context = context
        self.request = request

    @view_config(renderer="templates/default_view.pt")
    def default_view(self):
        # XXX Might be done more cleanly
        parent = self.context.__parent__
        if parent:
            parent_title = parent.title
        else:
            parent_title = "None"
        return {
            "page_title": self.context.title,
            "name": self.context.__name__,
            "parent_title": parent_title,
            }

