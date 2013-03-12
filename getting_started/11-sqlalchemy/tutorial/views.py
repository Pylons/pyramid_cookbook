import colander
import deform.widget

from pyramid.decorator import reify
from pyramid.httpexceptions import HTTPFound
from pyramid.renderers import get_renderer
from pyramid.security import remember, forget, authenticated_userid
from pyramid.view import view_config, forbidden_view_config

from .models import DBSession, Page
from .security import USERS


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
        pages = DBSession.query(Page).order_by(Page.title)
        return dict(title='Welcome to the Wiki', pages=pages)

    @view_config(route_name='wikipage_add',
                 renderer='templates/wikipage_addedit.pt')
    def wikipage_add(self):
        schema = WikiPage()
        wiki_form = deform.Form(schema, buttons=('submit',))
        form = wiki_form.render()

        if 'submit' in self.request.params:
            controls = self.request.POST.items()
            try:
                appstruct = wiki_form.validate(controls)
            except deform.ValidationFailure as e:
                # Form is NOT valid
                return dict(title='Add Wiki Page', form=e.render())

            # Add a new page to the database
            new_title = appstruct['title']
            new_body = appstruct['body']
            DBSession.add(Page(new_title, new_body))

            # Get the new ID and redirect
            page = DBSession.query(Page).filter_by(title=new_title).one()
            new_uid = page.id

            url = self.request.route_url('wikipage_view', uid=new_uid)
            return HTTPFound(url)

        return dict(title='Add Wiki Page', form=form)

    @view_config(route_name='wikipage_view',
                 renderer='templates/wikipage_view.pt')
    def wikipage_view(self):
        uid = int(self.request.matchdict['uid'])
        page = DBSession.query(Page).filter_by(id=uid).one()

        return dict(page=page, title=page.title)

    @view_config(route_name='wikipage_edit',
                 renderer='templates/wikipage_addedit.pt')
    def wikipage_edit(self):
        uid = int(self.request.matchdict['uid'])
        page = DBSession.query(Page).filter_by(id=uid).one()
        title = 'Edit ' + page.title

        schema = WikiPage()
        wiki_form = deform.Form(schema, buttons=('submit',))

        if 'submit' in self.request.params:
            controls = self.request.POST.items()
            try:
                appstruct = wiki_form.validate(controls)
            except deform.ValidationFailure as e:
                return dict(title=title, page=page, form=e.render())

            # Change the content and redirect to the view
            page.title = appstruct['title']
            page.body = appstruct['body']

            url = self.request.route_url('wikipage_view', uid=uid)
            return HTTPFound(url)

        form = wiki_form.render(dict(
            uid=page.id, title=page.title, body=page.body)
        )

        return dict(page=page, title=title, form=form)

    @view_config(route_name='wikipage_delete')
    def wikipage_delete(self):
        uid = int(self.request.matchdict['uid'])
        page = DBSession.query(Page).filter_by(id=uid).one()
        DBSession.delete(page)

        url = self.request.route_url('wiki_view')
        return HTTPFound(url)
