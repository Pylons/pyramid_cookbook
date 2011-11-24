from pyramid.view import view_config

class ProjectorViews(object):
    def __init__(self, context, request):
        self.context = context
        self.request = request

    @view_config(renderer="templates/default_view.pt",
                 permission='view')
    def default_view(self):
        return dict(page_title="View Site")

    @view_config(renderer="templates/default_view.pt",
                 permission='edit',
                 name="edit")
    def edit_view(self):
        return dict(page_title="Edit Site")
