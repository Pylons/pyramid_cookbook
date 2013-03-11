from pyramid.httpexceptions import HTTPFound
from pyramid.renderers import get_renderer
from pyramid.view import view_config

pages = [
    dict(uid='100', title='Page 100', body='<em>100</em>'),
    dict(uid='101', title='Page 101', body='<em>101</em>'),
    dict(uid='102', title='Page 102', body='<em>102</em>'),
]


class WikiViews(object):
    def __init__(self, request):
        self.request = request
        renderer = get_renderer("templates/layout.pt")
        self.layout = renderer.implementation().macros['layout']

    def get_pages(self):
        return pages

    @view_config(route_name='wiki_view',
                 renderer='templates/wiki_view.pt')
    def wiki_view(self):
        return dict(title='Welcome to the Wiki', pages=pages)

    @view_config(route_name='wikipage_add',
                 renderer='templates/wikipage_addedit.pt')
    def wikipage_add(self):
        return dict(title='Add Wiki Page')

    @view_config(route_name='wikipage_view',
                 renderer='templates/wikipage_view.pt')
    def wikipage_view(self):
        uid = self.request.matchdict['uid']
        page = [page for page in pages if page['uid'] == uid][0]
        title = page['title']
        return dict(page=page, title=title, uid=uid)

    @view_config(route_name='wikipage_edit',
                 renderer='templates/wikipage_addedit.pt')
    def wikipage_edit(self):
        uid = self.request.matchdict['uid']
        page = [page for page in pages if page['uid'] == uid][0]
        title = 'Edit ' + page['title']
        return dict(title=title)

    @view_config(route_name='wikipage_delete')
    def wikipage_delete(self):
        url = self.request.route_url('wiki_view')
        return HTTPFound(url)