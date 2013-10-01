import os
import colander
import io
import mimetypes
import warnings

from persistent import Persistent
from pyramid.response import FileResponse
from ZODB.blob import Blob
from ZODB.utils import oid_repr
from ZODB.utils import z64
from zope.interface import implementer

from ..util import get_oid
from .._compat import u

_BLANK = u('')

try:
    import magic
except ImportError: # pragma: no cover
    magic = None

USE_MAGIC = object()

import deform.widget
import deform.schema

from ..interfaces import IFile

from ..content import content
from ..form import FileUploadTempStore
from ..property import PropertySheet
from ..schema import (
    Schema,
    NameSchemaNode,
    )
from ..util import (
    chunks,
    renamer,
    )

def context_is_a_file(context, request):
    return request.registry.content.istype(context, 'File')

file_name_node = NameSchemaNode(editing=context_is_a_file)

class FilePropertiesSchema(Schema):
    name = file_name_node.clone()
    title = colander.SchemaNode(
        colander.String(),
        missing='',
        )
    mimetype = colander.SchemaNode(
        colander.String(),
        )

class FilePropertySheet(PropertySheet):
    schema = FilePropertiesSchema()

@colander.deferred
def file_upload_widget(node, kw):
    if kw.get('loading'):
        return None
    request = kw['request']
    tmpstore = FileUploadTempStore(request)
    widget = deform.widget.FileUploadWidget(tmpstore)
    widget.template = 'substanced.file:templates/fileupload.pt'
    return widget

class FileNode(colander.SchemaNode):
    schema_type = deform.schema.FileData
    widget = file_upload_widget

class FileUploadSchema(Schema):
    file = FileNode()

class FileUploadPropertySheet(PropertySheet):
    schema = FileUploadSchema()
    
    def get(self):
        context = self.context
        request = self.request
        uid = str(get_oid(context))
        filedata = dict(
            fp=None, # this cant be the real fp or will be written to tmpstore
            uid=uid,
            filename='',
            size = context.get_size(),
            )
        if context.mimetype.startswith('image/'):
            # XXX should this really point at an SDI URL?
            filedata['preview_url'] = request.sdiapi.mgmt_path(context)
        return dict(file=filedata)
    
    def set(self, struct):
        context = self.context
        file = struct['file']
        filename = file.get('filename', USE_MAGIC)
        fp = file.get('fp')
        if fp:
            fp.seek(0)
            context.upload(fp, mimetype_hint=filename)
        return False

    def after_set(self, changed):
        if changed is not False:
            PropertySheet.after_set(self, changed)
            tmpstore = FileUploadTempStore(self.request)
            tmpstore.clear()

@content(
    'File',
    icon='icon-file',
    add_view='add_file',
    # prevent view tab from sorting first (it would display the image when
    # manage_main clicked)
    tab_order = ('properties', 'acl_edit', 'view'),
    propertysheets = (
        ('Basic', FilePropertySheet),
        ('Upload', FileUploadPropertySheet),
        ),
    catalog = True,
    )
@implementer(IFile)
class File(Persistent):

    title = _BLANK

    name = renamer()

    def __init__(self, stream=None, mimetype=None, title=_BLANK):
        """ The constructor of a File object.

        ``stream`` should be a filelike object (an object with a ``read``
        method that takes a size argument) or ``None``.  If stream is
        ``None``, the blob attached to this file object is created empty.

        ``title`` must be a string or Unicode object.

        ``mimetype`` may be any of the following:

        - ``None``, meaning set this file object's mimetype to
          ``application/octet-stream`` (the default).

        - A mimetype string (e.g. ``image/gif``)

        - The constant :attr:`substanced.file.USE_MAGIC`, which will
          derive the mimetype from the stream content (if ``stream`` is also
          supplied) using the ``python-magic`` library.

          .. warning::

             On non-Linux systems, successful use of
             :attr:`substanced.file.USE_MAGIC` requires the installation
             of additional dependencies.  See :ref:`optional_dependencies`.
        """
        self.blob = Blob()
        self.title = title or _BLANK

        # mimetype will be overridden by upload if there's a stream
        if mimetype is USE_MAGIC:
            self.mimetype = 'application/octet-stream'
        else:
            self.mimetype = mimetype or 'application/octet-stream'

        if stream is not None:
            if mimetype is USE_MAGIC:
                hint = USE_MAGIC
            else:
                hint = None
            self.upload(stream, mimetype_hint=hint)

    def upload(self, stream, mimetype_hint=None):
        """ Replace the current contents of this file's blob with the
        contents of ``stream``.  ``stream`` must be a filelike object (it
        must have a ``read`` method that takes a size argument).

        ``mimetype_hint`` can be any of the following:

        - ``None``, meaning don't reset the current mimetype.  This is the
          default.  If you already know the file's mimetype, and you don't
          want it divined from a filename or stream content, use ``None`` as
          the ``mimetype_hint`` value, and set the ``mimetype`` attribute of
          the file object directly before or after calling this method.

        - A string containing a filename that has an extension; the mimetype
          will be derived from the extension in the filename using the Python
          ``mimetypes`` module, and the result will be set as the mimetype
          attribute of this object.

        - The constant :attr:`pyramid.file.USE_MAGIC`, which will derive
          the mimetype using the ``python-magic`` library based on the
          stream's actual content.  The result will be set as the mimetype
          attribute of this object.

          .. warning::

             On non-Linux systems, successful use of
             :attr:`substanced.file.USE_MAGIC` requires the installation
             of additional dependencies.  See :ref:`optional_dependencies`.
          
        """
        if not stream:
            stream = io.StringIO()
        fp = self.blob.open('w')
        first = True
        use_magic = False
        if mimetype_hint is USE_MAGIC:
            use_magic = True
            if magic is None: # pragma: no cover
                warnings.warn(
                    'The python-magic library does not have its requisite '
                    'dependencies installed properly, therefore the '
                    '"USE_MAGIC" flag passed to this method has been ignored '
                    '(it has been converted to "None").  The mimetype of '
                    'substanced.file.File objects created may be incorrect as '
                    'a result.'
                    )
                use_magic = False
                mimetype_hint = None

        if not use_magic:
            if mimetype_hint is not None:
                mimetype, _ = mimetypes.guess_type(mimetype_hint, strict=False)
                if mimetype is None:
                    mimetype = 'application/octet-stream'
                self.mimetype = mimetype
        for chunk in chunks(stream):
            if use_magic and first:
                first = False
                m = magic.Magic(mime=True)
                mimetype = m.from_buffer(chunk)
                self.mimetype = u(mimetype)
            fp.write(chunk)
        fp.close()

    def get_response(self, **kw):
        """ Return a WebOb-compatible response object which uses the blob
        content as the stream data and the mimetype of the file as the
        content type.  The ``**kw`` arguments will be passed to the
        ``pyramid.response.FileResponse`` constructor as its keyword
        arguments."""
        if not 'content_type' in kw:
            kw['content_type'] = str(self.mimetype)
        path = self.blob.committed()
        response = FileResponse(path, **kw)
        return response

    def get_size(self):
        """ Return the size in bytes of the data in the blob associated with
        the file"""
        return os.stat(self.blob.committed()).st_size

    def get_etag(self):
        """ Return a token identifying the "version" of the file.
        """
        self._p_activate()
        mine = self._p_serial
        blob = self.blob._p_serial
        if blob == z64:
            self.blob._p_activate()
            blob = self.blob._p_serial
        return oid_repr(max(mine, blob))
