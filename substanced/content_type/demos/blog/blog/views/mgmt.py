from webob.exc import HTTPFound
from substanced.sdi import mgmt_view
from substanced.form import FormView

from ..resources import (
    BlogEntrySchema,
    BinderSchema,
    )

@mgmt_view(
    name='add_binder',
    tab_title='Add Binder',
    permission='sdi.add-content',
    renderer='substanced.sdi:templates/form.pt',
    tab_condition=False,
    )
class AddBinderView(FormView):
    title = 'Add Binder'
    schema = BinderSchema()
    buttons = ('add',)

    def add_success(self, appstruct):
        request = self.request
        name = appstruct.pop('name')
        binder = request.registry.content.create('Binder', **appstruct)
        self.context[name] = binder
        loc = request.mgmt_path(self.context, name, '@@properties')
        return HTTPFound(location=loc)


class HelloView:
    def __init__(self, context, request):
        self.context = context
        self.request = request

    @mgmt_view(
        name='hello',
        tab_title='Hello',
        renderer='templates/hello.pt'
        )
    def hello(self):
        return dict(page_title='hello')

@mgmt_view(
    content_type='Root',
    name='add_blog_entry',
    permission='sdi.add-content', 
    renderer='substanced.sdi:templates/form.pt',
    tab_condition=False,
    )
class AddBlogEntryView(FormView):
    title = 'Add Blog Entry'
    schema = BlogEntrySchema()
    buttons = ('add',)

    def add_success(self, appstruct):
        name = appstruct.pop('name')
        request = self.request
        blogentry = request.registry.content.create('Blog Entry', **appstruct)
        self.context[name] = blogentry
        loc = request.mgmt_path(self.context, name, '@@properties')
        return HTTPFound(location=loc)

