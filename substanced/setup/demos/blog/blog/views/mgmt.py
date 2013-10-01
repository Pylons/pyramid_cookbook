from webob.exc import HTTPFound
from substanced.sdi import mgmt_view
from substanced.form import FormView

from ..resources import BlogEntrySchema

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

