from pyramid.view import view_config

from .resources import SiteFolder
from .resources import Folder
from .resources import Document


class TutorialViews:
    def __init__(self, context, request):
        self.context = context
        self.request = request

    @view_config(renderer="templates/site.jinja2",
                 context=SiteFolder)
    def site(self):
        return {}

    @view_config(renderer="templates/folder.jinja2",
                 context=Folder)
    def folder(self):
        return {}


    @view_config(renderer="templates/document.jinja2",
                 context=Document)
    def document(self):
        return {}
