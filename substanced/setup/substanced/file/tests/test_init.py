import io
import os
import unittest
from pyramid import testing

class Test_file_upload_widget(unittest.TestCase):
    def setUp(self):
        testing.setUp()

    def tearDown(self):
        testing.tearDown()

    def _callFUT(self, node, kw):
        from .. import file_upload_widget
        return file_upload_widget(node, kw)

    def test_loading(self):
        kw = {'loading':True}
        self.assertEqual(self._callFUT(None, kw), None)

    def test_it(self):
        here = os.path.dirname(__file__)
        request = testing.DummyRequest()
        request.registry.settings['substanced.uploads_tempdir'] = here
        kw = {}
        kw['request'] = request
        widget = self._callFUT(None, kw)
        self.assertEqual(widget.__class__.__name__, 'FileUploadWidget')

class TestFileUploadPropertySheet(unittest.TestCase):
    def setUp(self):
        testing.setUp()

    def tearDown(self):
        testing.tearDown()

    def _makeOne(self, context, request):
        from .. import FileUploadPropertySheet
        return FileUploadPropertySheet(context, request)

    def test_get_not_an_image(self):
        context = testing.DummyResource()
        context.__oid__ = 'oid'
        context.get_size = lambda *arg: 80
        context.mimetype = 'application/octet-stream'
        request = testing.DummyRequest()
        request.sdiapi = DummySDIAPI()
        inst = self._makeOne(context, request)
        file = {'fp':None, 'uid':'oid', 'filename':'', 'size':80}
        self.assertEqual(
            inst.get(),
            {'file':file}
            )

    def test_get_is_an_image(self):
        context = testing.DummyResource()
        context.__oid__ = 'oid'
        context.get_size = lambda *arg: 80
        context.mimetype = 'image/foo'
        request = testing.DummyRequest()
        request.sdiapi = DummySDIAPI()
        inst = self._makeOne(context, request)
        file = {'fp':None,
                'uid':'oid',
                'filename':'',
                'preview_url':'/mgmt_path',
                'size':80}
        self.assertEqual(
            inst.get(),
            {'file':file}
            )

    def test_set_no_fp(self):
        context = testing.DummyResource()
        request = testing.DummyRequest()
        inst = self._makeOne(context, request)
        inst.set({'file':{}})

    def test_set_with_fp_and_filename(self):
        fp = io.BytesIO(b'abc')
        fp.seek(2)
        def upload(_fp, mimetype_hint=None):
            self.assertEqual(_fp, fp)
            self.assertEqual(mimetype_hint, 'foo.pt')
            context.uploaded = True
        context = testing.DummyResource()
        context.upload = upload
        request = testing.DummyRequest()
        inst = self._makeOne(context, request)
        inst.set({'file':{'fp':fp, 'filename':'foo.pt'}})
        self.assertTrue(context.uploaded)
        self.assertEqual(fp.tell(), 0)

    def test_set_with_fp_no_filename(self):
        from .. import USE_MAGIC
        fp = io.BytesIO(b'abc')
        fp.seek(2)
        def upload(_fp, mimetype_hint=None):
            self.assertEqual(_fp, fp)
            self.assertEqual(mimetype_hint, USE_MAGIC)
            context.uploaded = True
        context = testing.DummyResource()
        context.upload = upload
        request = testing.DummyRequest()
        inst = self._makeOne(context, request)
        inst.set({'file':{'fp':fp}})
        self.assertTrue(context.uploaded)
        self.assertEqual(fp.tell(), 0)

    def test_after_set(self):
        context = testing.DummyResource()
        here = os.path.dirname(__file__)
        request = testing.DummyRequest()
        request.sdiapi = DummySDIAPI()
        request.registry.settings = {}
        request.registry.settings['substanced.uploads_tempdir'] = here
        request.session['substanced.tempstore'] = {'1':{}}
        inst = self._makeOne(context, request)
        inst.after_set(True)
        self.assertEqual(request.session.get('substanced.tempstore'), None)

class TestFile(unittest.TestCase):
    def setUp(self):
        testing.setUp()

    def tearDown(self):
        testing.tearDown()

    def _makeOne(self, stream, mimetype, title=None):
        from .. import File
        return File(stream, mimetype, title)

    def test_ctor_no_stream(self):
        inst = self._makeOne(None, None)
        self.assertEqual(inst.mimetype, 'application/octet-stream')

    def test_ctor_no_title(self):
        from substanced._compat import u
        inst = self._makeOne(None, None)
        self.assertEqual(inst.title, u(''))

    def test_ctor_with_None_title(self):
        from substanced._compat import u
        inst = self._makeOne(None, None, None)
        self.assertEqual(inst.title, u(''))

    def test_ctor_with_with_title(self):
        inst = self._makeOne(None, None, 'abc')
        self.assertEqual(inst.title, 'abc')

    def test_ctor_with_stream_mimetype_None(self):
        stream = io.BytesIO(b'abc')
        inst = self._makeOne(stream, None)
        self.assertEqual(inst.mimetype, 'application/octet-stream')
        with inst.blob.open('r') as fp:
            fp.seek(0)
            self.assertEqual(fp.read(), b'abc')

    def test_ctor_with_stream_mimetype_USE_MAGIC(self):
        from .. import USE_MAGIC
        stream = io.BytesIO(b'abc')
        inst = self._makeOne(stream, USE_MAGIC)
        self.assertEqual(inst.mimetype, 'text/plain')
        with inst.blob.open('r') as fp:
            fp.seek(0)
            self.assertEqual(fp.read(), b'abc')

    def test_ctor_with_mimetype_no_stream(self):
        inst = self._makeOne(None, 'text/plain')
        self.assertEqual(inst.mimetype, 'text/plain')

    def test_ctor_with_mimetype_and_stream(self):
        stream = io.BytesIO(b'abc')
        inst = self._makeOne(stream, 'text/foo')
        self.assertEqual(inst.mimetype, 'text/foo')
        with inst.blob.open('r') as fp:
            fp.seek(0)
            self.assertEqual(fp.read(), b'abc')

    def test_ctor_mimetype_is_USE_MAGIC_no_stream(self):
        from .. import USE_MAGIC
        inst = self._makeOne(None, USE_MAGIC)
        self.assertEqual(inst.mimetype, 'application/octet-stream')

    def test_upload_stream_is_None(self):
        inst = self._makeOne(None, None)
        inst.upload(None)
        with inst.blob.open('r') as f:
            self.assertEqual(f.read(), b'')

    def test_upload_stream_is_not_None(self):
        stream = io.BytesIO(b'abc')
        inst = self._makeOne(None, None)
        inst.upload(stream)
        with inst.blob.open('r') as f:
            self.assertEqual(f.read(), b'abc')

    def test_upload_stream_mimetype_hint_USE_MAGIC(self):
        from .. import USE_MAGIC
        stream = io.BytesIO(b'abc')
        inst = self._makeOne(None, None)
        self.assertEqual(inst.mimetype, 'application/octet-stream')
        inst.upload(stream, mimetype_hint=USE_MAGIC)
        self.assertEqual(inst.mimetype, 'text/plain')

    def test_upload_stream_mimetype_hint_filename(self):
        stream = io.BytesIO(b'abc')
        inst = self._makeOne(None, None)
        self.assertEqual(inst.mimetype, 'application/octet-stream')
        inst.upload(stream, mimetype_hint='foo.gif')
        self.assertEqual(inst.mimetype, 'image/gif')

    def test_upload_stream_mimetype_hint_filename_unknown_extension(self):
        stream = io.BytesIO(b'abc')
        inst = self._makeOne(None, None)
        self.assertEqual(inst.mimetype, 'application/octet-stream')
        inst.upload(stream, mimetype_hint='foo')
        self.assertEqual(inst.mimetype, 'application/octet-stream')

    def test_upload_stream_mimetype_hint_None(self):
        stream = io.BytesIO(b'abc')
        inst = self._makeOne(None, None)
        self.assertEqual(inst.mimetype, 'application/octet-stream')
        inst.upload(stream, mimetype_hint=None)
        self.assertEqual(inst.mimetype, 'application/octet-stream')

    def test_get_response_no_ct(self):
        inst = self._makeOne(None, 'text/plain')
        inst.blob = DummyBlob()
        response = inst.get_response()
        self.assertTrue(response.body)
        self.assertEqual(response.content_type, 'text/plain')

    def test_get_response_with_ct(self):
        inst = self._makeOne(None, 'text/plain')
        inst.blob = DummyBlob()
        response = inst.get_response(content_type='text/other')
        self.assertTrue(response.body)
        self.assertEqual(response.content_type, 'text/other')

    def test_get_size(self):
        inst = self._makeOne(None, None)
        inst.blob = DummyBlob()
        size = inst.get_size()
        self.assertEqual(size, os.stat(__file__).st_size)

    def test_get_etag_blob_newer(self):
        # E.g. if upload after setting title
        from ZODB.utils import oid_repr
        inst = self._makeOne(None, None)
        inst._p_serial = b'DEADBEEF'
        blob = inst.blob = DummyBlob()
        blob._p_serial = b'EDABEDAC'
        etag = inst.get_etag()
        self.assertEqual(etag, oid_repr(b'EDABEDAC'))

    def test_get_etag_file_newer(self):
        # E.g. if title is updated after upload
        from ZODB.utils import oid_repr
        inst = self._makeOne(None, None)
        inst._p_serial = b'EDABEDAC'
        blob = inst.blob = DummyBlob()
        blob._p_serial = b'DEADBEEF'
        etag = inst.get_etag()
        self.assertEqual(etag, oid_repr(b'EDABEDAC'))

    def test_get_etag_file_newer_w_ghost_blob(self):
        # E.g. if title is updated after upload
        from ZODB.utils import oid_repr
        from ZODB.utils import z64
        inst = self._makeOne(None, None)
        inst._p_serial = b'EDABEDAC'
        blob = inst.blob = DummyBlob()
        blob._p_serial = z64
        etag = inst.get_etag()
        self.assertEqual(etag, oid_repr(b'EDABEDAC'))

class Test_context_is_a_file(unittest.TestCase):
    def _callFUT(self, context, request):
        from .. import context_is_a_file
        return context_is_a_file(context, request)

    def test_it_true(self):
        registry = DummyRegistry(True)
        request = testing.DummyRequest()
        request.registry = registry
        self.assertTrue(self._callFUT(None, request))

    def test_it_false(self):
        registry = DummyRegistry(False)
        request = testing.DummyRequest()
        request.registry = registry
        self.assertFalse(self._callFUT(None, request))

class DummyContent(object):
    def __init__(self, result):
        self.result = result
    def istype(self, context, t):
        return self.result

class DummyRegistry(object):
    def __init__(self, result):
        self.content = DummyContent(result)

class DummyBlob(object):
    def committed(self):
        return os.path.abspath(__file__)
    def _p_activate(self):
        self._p_serial = b'CACAFADA'

class DummySDIAPI(object):
    def mgmt_path(self, *arg, **kw):
        return '/mgmt_path'

