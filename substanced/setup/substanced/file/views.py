import pkg_resources
import mimetypes
import colander
import deform.schema

from pyramid.httpexceptions import HTTPFound
from pyramid.response import Response
from pyramid.security import NO_PERMISSION_REQUIRED

from ..form import FormView

from ..file import (
    FilePropertiesSchema,
    FileUploadTempStore,
    file_upload_widget,
    file_name_node,
    USE_MAGIC,
    )

from ..interfaces import (
    IFile,
    IFolder,
    )

from ..sdi import mgmt_view

@mgmt_view(
    context=IFile,
    name='', 
    permission='sdi.view',
    tab_condition=False,
    http_cache=0,
    )
def view_file(context, request):
    return context.get_response(request=request)

@mgmt_view(
    context=IFile,
    name='view',
    tab_title='View',
    permission='sdi.view'
    )
def view_tab(context, request):
    return HTTPFound(location=request.sdiapi.mgmt_path(context))

class AddFileSchema(FilePropertiesSchema):
    file = colander.SchemaNode(
        deform.schema.FileData(),
        widget = file_upload_widget,
        missing = colander.null,
        )

@colander.deferred
def name_or_file(node, kw):
    def _name_or_file(node, struct):
        if not struct['file'] and not struct['name']:
            raise colander.Invalid(node, 'One of name or file is required')
        if not struct['name']:
            filename = struct['file'].get('filename')
            if filename:
                name_node = file_name_node.bind(
                    context=kw['context'], request=kw['request']
                    )
                name_node.validator(node['file'], filename)
            else:
                raise colander.Invalid(
                    node,
                    'If no name is supplied, a file must be supplied.'
                    )
    return _name_or_file

@mgmt_view(
    context=IFolder,
    name='add_file',
    tab_title='Add File', 
    permission='sdi.add-content', 
    renderer='substanced.sdi:templates/form.pt',
    tab_condition=False
    )
class AddFileView(FormView):
    title = 'Add File'
    schema = AddFileSchema(validator=name_or_file).clone()
    schema['name'].missing = colander.null
    schema['mimetype'].missing = colander.null
    buttons = ('add',)

    def _makeob(self, stream, title, mimetype):
        return self.request.registry.content.create(
            'File',
            stream=stream,
            mimetype=mimetype,
            title=title,
            )

    def add_success(self, appstruct):
        name = appstruct['name']
        title = appstruct['title'] or None
        filedata = appstruct['file']
        mimetype = appstruct['mimetype'] or USE_MAGIC
        stream = None
        filename = None
        if filedata:
            filename = filedata['filename']
            stream = filedata['fp']
            if stream:
                stream.seek(0)
            else:
                stream = None
        name = name or filename
        fileob = self._makeob(stream, title, mimetype)
        self.context[name] = fileob
        return HTTPFound(self.request.sdiapi.mgmt_path(self.context))

onepixel = pkg_resources.resource_filename(
    'substanced.sdi', 'static/img/onepixel.gif')

# this doesn't require a permission, because it's based on session data
# which the user would have to put there anyway
@mgmt_view(
    name='preview_image_upload',
    tab_condition=False,
    permission=NO_PERMISSION_REQUIRED
    )
def preview_image_upload(request):
    uid = request.subpath[0]
    tempstore = FileUploadTempStore(request)
    filedata = tempstore.get(uid, {})
    fp = filedata.get('fp')
    filename = ''
    if fp is not None:
        fp.seek(0)
        filename = filedata['filename']
    mimetype = mimetypes.guess_type(filename, strict=False)[0]
    if not mimetype or not mimetype.startswith('image/'):
        mimetype = 'image/gif'
        fp = open(onepixel, 'rb')
    response = Response(content_type=mimetype, app_iter=fp)
    return response
