import os
import tempfile
import shutil
import unittest
from pyramid import testing
from pyramid.exceptions import ConfigurationError

class TestFormView(unittest.TestCase):
    def _getTargetClass(self):
        from . import FormView
        return FormView
        
    def _makeOne(self, context, request):
        klass = self._getTargetClass()
        inst = klass(context, request)
        return inst

    def test___call__show(self):
        schema = DummySchema()
        request = testing.DummyRequest()
        context = testing.DummyResource()
        inst = self._makeOne(context, request)
        inst.schema = schema
        inst.form_class = DummyForm
        result = inst()
        self.assertEqual(result,
                         {'css_links': (), 'js_links': (), 'form': 'rendered'})

    def test___call__show_result_response(self):
        from webob import Response
        schema = DummySchema()
        request = testing.DummyRequest()
        context = testing.DummyResource()
        inst = self._makeOne(context, request)
        inst.schema = schema
        inst.form_class = DummyForm
        response = Response()
        inst.show = lambda *arg: response
        result = inst()
        self.assertEqual(result, response)

    def test___call__button_in_request(self):
        schema = DummySchema()
        request = testing.DummyRequest()
        context = testing.DummyResource()
        request.POST['submit'] = True
        inst = self._makeOne(context, request)
        inst.schema = schema
        inst.buttons = (DummyButton('submit'), )
        inst.submit_success = lambda *x: 'success'
        inst.form_class = DummyForm
        result = inst()
        self.assertEqual(result, 'success')

    def test___call__button_in_request_validation_fails_w_handler(self):
        import deform.exception
        schema = DummySchema()
        request = testing.DummyRequest()
        context = testing.DummyResource()
        request.POST['submit'] = True
        def _validate(*args):
            exc = deform.exception.ValidationFailure(None, None, None)
            exc.render = lambda *arg: 'failure'
            raise exc
        inst = self._makeOne(context, request)
        inst.schema = schema
        inst.buttons = (DummyButton('submit'), )
        form, reqts = inst._build_form()
        form.validate = _validate
        inst._build_form = lambda *arg: (form, {'js': (), 'css': ()})
        def raiseit(*arg): #pragma NO COVER
            self.fail()
        inst.submit_success = raiseit # shouldn't get there
        inst.form_class = DummyForm
        result = inst()
        self.assertEqual(result,
                         {'css_links': (), 'js_links': (), 'form': 'failure'})

    def test___call__button_in_request_validateion_fails_wo_handler(self):
        import deform.exception
        schema = DummySchema()
        request = testing.DummyRequest()
        context = testing.DummyResource()
        request.POST['submit'] = True
        def _validate(*args):
            exc = deform.exception.ValidationFailure(None, None, None)
            exc.render = lambda *arg: 'failure'
            raise exc
        inst = self._makeOne(context, request)
        inst.schema = schema
        inst.buttons = (DummyButton('submit'), )
        form, reqts = inst._build_form()
        form.validate = _validate
        inst._build_form = lambda *arg: (form, {'js': (), 'css': ()})
        def raiseit(*arg): #pragma NO COVER
            self.fail()
        inst.submit_success = raiseit # shouldn't get there
        inst.form_class = DummyForm
        result = inst()
        self.assertEqual(result,
                         {'css_links': (), 'js_links': (), 'form': 'failure'})

    def test___call__button_in_request_fail(self):
        from . import FormError
        schema = DummySchema()
        request = testing.DummyRequest()
        context = testing.DummyResource()
        request.POST['submit'] = True
        inst = self._makeOne(context, request)
        inst.schema = schema
        inst.buttons = (DummyButton('submit'), )
        def raiseit(*arg):
            raise FormError()
        inst.submit_success = raiseit
        inst.form_class = DummyForm
        inst.submit_failure = lambda *arg: 'failure'
        result = inst()
        self.assertEqual(result,
                         {'css_links': (), 'js_links': (), 'form': 'rendered'})
        self.assertEqual(request.session.peek_flash('error'),
                         ['<div class="error">Failed: </div>'])


class TestFileUploadTempStore(unittest.TestCase):
    def setUp(self):
        self.tempdir = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.tempdir)
        
    def _getTargetClass(self):
        from . import FileUploadTempStore
        return FileUploadTempStore

    def _makeOne(self, request):
        return self._getTargetClass()(request)

    def _makeRequest(self):
        request = testing.DummyRequest()
        request.registry.settings = {}
        request.registry.settings['substanced.uploads_tempdir'] = self.tempdir
        request.session = DummySession()
        return request

    def test_no_tempdir_in_settings(self):
        request = testing.DummyRequest()
        request.registry.settings = {}
        self.assertRaises(ConfigurationError, self._makeOne, request)

    def test_preview_url(self):
        request = self._makeRequest()
        request.sdiapi = DummySDIAPI()
        inst = self._makeOne(request)
        self.assertEqual(inst.preview_url(None), '/mgmt_path')

    def test_contains_true(self):
        request = self._makeRequest()
        inst = self._makeOne(request)
        inst.session['substanced.tempstore'] = {}
        inst.session['substanced.tempstore']['a'] = 1
        self.assertTrue('a' in inst)
        
    def test_contains_false(self):
        request = self._makeRequest()
        inst = self._makeOne(request)
        self.assertFalse('a' in inst)

    def test_setitem_stream_None(self):
        request = self._makeRequest()
        inst = self._makeOne(request)
        inst['a'] = {}
        self.assertEqual(inst.session['substanced.tempstore']['a'], {})

    def test_setitem_stream_file(self):
        request = self._makeRequest()
        inst = self._makeOne(request)
        here = os.path.dirname(__file__)
        thisfile = os.path.join(here, 'tests.py')
        with open(thisfile, 'rb') as f:
            inst['a'] = {'fp': f}
            randid = inst.session['substanced.tempstore']['a']['randid']
            self.assertTrue(randid)
        with open(thisfile, 'rb') as g:
            fn = os.path.join(self.tempdir, randid)
            with open(fn, 'rb') as h:
                self.assertEqual(h.read(), g.read())

    def test_get_data_None(self):
        request = self._makeRequest()
        inst = self._makeOne(request)
        self.assertEqual(inst.get('a', True), True)

    def test_get_no_randid(self):
        request = self._makeRequest()
        inst = self._makeOne(request)
        inst.session['substanced.tempstore'] = {}
        inst.session['substanced.tempstore']['a'] = {'fp':True}
        self.assertEqual(inst.get('a'), {'fp':True})

    def test_get_with_randid(self):
        request = self._makeRequest()
        inst = self._makeOne(request)
        fn = os.path.join(self.tempdir, '1234')
        with open(fn, 'wb') as f:
            f.write(b'abc')
        inst.session['substanced.tempstore'] = {}
        inst.session['substanced.tempstore']['a'] = {'randid':'1234'}
        with open(fn, 'rb') as f:
            with inst.get('a')['fp'] as g:
                self.assertEqual(g.read(), f.read())

    def test_get_with_randid_file_doesntexist(self):
        request = self._makeRequest()
        inst = self._makeOne(request)
        inst.session['substanced.tempstore'] = {}
        inst.session['substanced.tempstore']['a'] = {'randid':'1234'}
        self.assertFalse('fp' in inst.get('a'))

    def test___getitem___notfound(self):
        request = self._makeRequest()
        inst = self._makeOne(request)
        self.assertRaises(KeyError, inst.__getitem__, 'a')
        
    def test___getitem___found(self):
        request = self._makeRequest()
        inst = self._makeOne(request)
        inst.session['substanced.tempstore'] = {}
        inst.session['substanced.tempstore']['a'] = {}
        self.assertEqual(inst['a'], {})

    def test_clear_exists(self):
        request = self._makeRequest()
        inst = self._makeOne(request)
        tmpfile = os.path.join(self.tempdir, 'abc')
        with open(tmpfile, 'wb') as f:
            f.write(b'foo')
        inst['a'] = {'randid':'abc'}
        inst.clear()
        self.assertFalse(os.path.exists(tmpfile))

    def test_clear_doesntexist(self):
        request = self._makeRequest()
        inst = self._makeOne(request)
        inst['a'] = {'randid':'abc'}
        inst.clear() # doesn't choke

class DummyWidget(object):
    pass

class DummyForm(object):
    def __init__(self, schema, action=None, method=None, buttons=None,
                 formid=None, use_ajax=False, ajax_options='',
                 autocomplete=None):
        self.schema = schema
        self.action = action
        self.method = method
        self.buttons = buttons
        self.formid = formid
        self.use_ajax = use_ajax
        self.ajax_options = ajax_options
        self.autocomplete = autocomplete
        self.widget = DummyWidget()

    def get_widget_resources(self):
        return {'js':(), 'css':()}

    def render(self, appstruct=None):
        self.appstruct = appstruct
        return 'rendered'

    def validate(self, controls):
        return {'_csrf_token_':'abc', 'validated':'validated'}

class DummySchema(object):
    name = 'schema'
    title = 'Schema'
    description = 'Dummy schema for testing'
    required = True
    children = ()
    typ = None
    def bind(self, **kw):
        self.kw = kw
        return self
    def serialize(self, appstruct):
        return appstruct
    def cstruct_children(self, cstruct):
        return ()
    
class DummyButton(object):
    def __init__(self, name):
        self.name = name
        
class DummySession(dict):
    pass

class DummySDIAPI(object):
    def mgmt_path(self, *arg, **kw):
        return '/mgmt_path'
