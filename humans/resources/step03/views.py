from pyramid.view import view_config

from resources import SiteFolder
from resources import Folder
from resources import Document

class ProjectorViews(object):
    def __init__(self, context, request):
        self.context = context
        self.request = request

    @view_config(renderer="templates/site_view.pt",
                 context=SiteFolder)
    def site_view(self):
        return {"children": self.context.values()}

    @view_config(renderer="templates/folder_view.pt",
                 context=Folder)
    def folder_view(self):
        return {"children": self.context.values()}


    @view_config(renderer="templates/document_view.pt",
                 context=Document)
    def document_view(self):
        return {}
