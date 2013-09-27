from pyramid.view import view_config

from .resources import SiteFolder
from .resources import Folder
from .resources import Document


class TutorialViews:
    def __init__(self, context, request):
        self.context = context
        self.request = request

    @view_config(renderer="templates/site.pt",
                 context=SiteFolder)
    def site(self):
        return {"children": self.context.values()}

    @view_config(renderer="templates/folder.pt",
                 context=Folder)
    def folder(self):
        return {"children": self.context.values()}


    @view_config(renderer="templates/document.pt",
                 context=Document)
    def document(self):
        return {}
