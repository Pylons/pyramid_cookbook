import colander
import deform.widget

from pyramid.decorator import reify
from pyramid.httpexceptions import HTTPFound
from pyramid.renderers import get_renderer
from pyramid.view import view_config

pages = {
    '100': dict(uid='100', title='Page 100', body='<em>100</em>'),
    '101': dict(uid='101', title='Page 101', body='<em>101</em>'),
    '102': dict(uid='102', title='Page 102', body='<em>102</em>')
}


class WikiPage(colander.MappingSchema):
    title = colander.SchemaNode(colander.String())
    body = colander.SchemaNode(
        colander.String(),
        widget=deform.widget.RichTextWidget()
    )


class WikiViews(object):
    def __init__(self, request):
        self.request = request
        renderer = get_renderer("templates/layout.pt")
        self.layout = renderer.implementation().macros['layout']
        self.uid = self.request.matchdict.get('uid', None)

    @reify
    def form(self):
        schema = WikiPage()
        form = deform.Form(schema, buttons=('submit',))
        return form

    @reify
    def reqts(self):
        return self.form.get_widget_resources()

    @view_config(route_name='wiki_view',
                 renderer='templates/wiki_view.pt')
    def wiki_view(self):
        return dict(title='Welcome to the Wiki',
                    pages=pages.values())

    @view_config(route_name='wikipage_add',
                 renderer='templates/wikipage_add.pt')
    def wikipage_add(self):
        schema = WikiPage()
        wiki_form = deform.Form(schema, buttons=('submit',))
        form = wiki_form.render()

        return dict(title='Add Wiki Page', form=form)

    @view_config(route_name='wikipage_add',
                 request_param='submit',
                 renderer='templates/wikipage_add.pt')
    def add_handler(self):
        schema = WikiPage()
        wiki_form = deform.Form(schema, buttons=('submit',))
        controls = self.request.POST.items()

        try:
            appstruct = wiki_form.validate(controls)
        except deform.ValidationFailure as e:
            return dict(title='Add Wiki Page', form=e.render())

        # Make a new identifier
        last_uid = int(sorted(pages.keys())[-1])
        new_uid = str(last_uid + 1)
        pages[new_uid] = dict(
            uid=new_uid, title=appstruct['title'], body=appstruct['body']
        )

        url = self.request.route_url('wikipage_view', uid=new_uid)
        return HTTPFound(url)

    @view_config(route_name='wikipage_view',
                 renderer='templates/wikipage_view.pt')
    def wikipage_view(self):
        page = pages[self.uid]
        return dict(page=page, title=page['title'])

    @view_config(route_name='wikipage_edit',
                 renderer='templates/wikipage_edit.pt')
    def wikipage_edit(self):
        page = pages[self.uid]

        schema = WikiPage()
        wiki_form = deform.Form(schema, buttons=('submit',))
        form = wiki_form.render(page)

        return dict(page=page, title=page['title'], form=form)

    @view_config(route_name='wikipage_edit',
                 request_param='submit',
                 renderer='templates/wikipage_edit.pt')
    def edit_handler(self):
        page = pages[self.uid]

        schema = WikiPage()
        wiki_form = deform.Form(schema, buttons=('submit',))
        controls = self.request.POST.items()

        try:
            appstruct = wiki_form.validate(controls)
        except deform.ValidationFailure as e:
            return dict(title=page['title'], page=page, form=e.render())

        # Change the content and redirect to the view
        page['title'] = appstruct['title']
        page['body'] = appstruct['body']

        url = self.request.route_url('wikipage_view', uid=page['uid'])
        return HTTPFound(url)

    @view_config(route_name='wikipage_delete')
    def wikipage_delete(self):
        del pages[self.uid]

        url = self.request.route_url('wiki_view')
        return HTTPFound(url)
