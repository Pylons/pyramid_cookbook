from pyramid.location import lineage
from pyramid.view import view_config

from .resources import (
    Root,
    Folder,
    Document
    )


class TutorialViews:
    def __init__(self, context, request):
        self.context = context
        self.request = request
        self.parents = reversed(list(lineage(context)))

    @view_config(renderer='templates/root.jinja2',
                 context=Root)
    def root(self):
        page_title = 'Quick Tutorial: Root'
        return dict(page_title=page_title)

    @view_config(renderer='templates/folder.jinja2',
                 context=Folder)
    def folder(self):
        page_title = 'Quick Tutorial: Folder'
        return dict(page_title=page_title)


    @view_config(renderer='templates/document.jinja2',
                 context=Document)
    def document(self):
        page_title = 'Quick Tutorial: Document'
        return dict(page_title=page_title)
