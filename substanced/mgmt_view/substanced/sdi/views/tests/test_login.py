import unittest
from pyramid import testing

class Test_logout(unittest.TestCase):
    def setUp(self):
        testing.setUp()

    def tearDown(self):
        testing.tearDown()
        
    def _callFUT(self, request):
        from ..login import logout
        return logout(request)

    def test_it(self):
        request = testing.DummyRequest()
        request.sdiapi = DummySDIAPI()
        response = self._callFUT(request)
        self.assertEqual(response.location, '/mgmt_path')

class Test_login(unittest.TestCase):
    def setUp(self):
        testing.setUp()

    def tearDown(self):
        testing.tearDown()
        
    def _callFUT(self, context, request):
        from ..login import login
        return login(context, request)

    def test_referrer_is_auditstream(self):
        from pyramid.httpexceptions import HTTPForbidden
        request = testing.DummyRequest()
        request.url = '/auditstream-sse'
        request.sdiapi = DummySDIAPI()
        context = testing.DummyResource()
        result = self._callFUT(context, request)
        self.assertEqual(result.__class__, HTTPForbidden)

    def test_referrer_is_login_view(self):
        from pyramid.testing import testConfig
        request = testing.DummyRequest()
        request.url = '/mgmt_path'
        request.sdiapi = DummySDIAPI()
        context = testing.DummyResource()
        with testConfig() as config:
            config.testing_add_renderer(
                    'substanced.sdi.views:templates/login.pt')
            result = self._callFUT(context, request)
        self.assertEqual(result['url'], '/mgmt_path')
        self.assertEqual(result['came_from'], '/mgmt_path')
        self.assertEqual(result['login'], '')
        self.assertEqual(result['password'], '')
        self.assertEqual(request.session['sdi.came_from'], '/mgmt_path')
        
    def test_form_not_submitted(self):
        from pyramid.testing import testConfig
        class DummyRenderer(object):
            def __init__(self, macros):
                self.macros = macros
            def implementation(self):
                return self
        request = testing.DummyRequest()
        request.sdiapi = DummySDIAPI()
        context = testing.DummyResource()
        form, reset = object(), object()
        renderer = DummyRenderer(
                    {'login-form': form, 'password-reset-link': reset})
        with testConfig() as config:
            config.testing_add_renderer(
                    'substanced.sdi.views:templates/login.pt', renderer)
            result = self._callFUT(context, request)
        self.assertEqual(result['url'], '/mgmt_path')
        self.assertEqual(result['came_from'], 'http://example.com')
        self.assertEqual(result['login'], '')
        self.assertEqual(result['password'], '')
        self.assertTrue(result['login_template'] is renderer)
        self.assertEqual(request.session['sdi.came_from'],
                         'http://example.com')

    def test_form_submitted_csrf_error(self):
        from pyramid.testing import testConfig
        request = testing.DummyRequest()
        request.params['form.submitted'] = True
        request.sdiapi = DummySDIAPI()
        context = testing.DummyResource()
        with testConfig() as config:
            config.testing_add_renderer(
                    'substanced.sdi.views:templates/login.pt')
            result = self._callFUT(context, request)
        self.assertEqual(result['url'], '/mgmt_path')
        self.assertEqual(result['came_from'], 'http://example.com')
        self.assertEqual(result['login'], '')
        self.assertEqual(result['password'], '')
        self.assertEqual(request.session['_f_error'], ['Failed login (CSRF)'])
        self.assertEqual(request.session['sdi.came_from'], 'http://example.com')
        
    def test_form_submitted_failed_login_no_user(self):
        from pyramid.testing import testConfig
        from ....testing import make_site
        request = testing.DummyRequest()
        request.params['form.submitted'] = True
        request.params['login'] = 'login'
        request.params['password'] = 'password'
        request.sdiapi = DummySDIAPI()
        request.params['csrf_token'] = request.session.get_csrf_token()
        context = make_site()
        with testConfig() as config:
            config.testing_add_renderer(
                    'substanced.sdi.views:templates/login.pt')
            result = self._callFUT(context, request)
        self.assertEqual(result['url'], '/mgmt_path')
        self.assertEqual(result['came_from'], 'http://example.com')
        self.assertEqual(result['login'], 'login')
        self.assertEqual(result['password'], 'password')
        self.assertEqual(request.session['_f_error'], ['Failed login'])
        self.assertEqual(request.session['sdi.came_from'], 'http://example.com')

    def test_form_submitted_failed_login_wrong_password(self):
        from pyramid.testing import testConfig
        from ....testing import make_site
        request = testing.DummyRequest()
        request.params['form.submitted'] = True
        request.params['login'] = 'login'
        request.params['password'] = 'password'
        request.sdiapi = DummySDIAPI()
        request.params['csrf_token'] = request.session.get_csrf_token()
        context = make_site()
        context['principals']['users']['login'] = DummyUser(0)
        with testConfig() as config:
            config.testing_add_renderer(
                    'substanced.sdi.views:templates/login.pt')
            result = self._callFUT(context, request)
        self.assertEqual(result['url'], '/mgmt_path')
        self.assertEqual(result['came_from'], 'http://example.com')
        self.assertEqual(result['login'], 'login')
        self.assertEqual(result['password'], 'password')
        self.assertEqual(request.session['_f_error'], ['Failed login'])
        self.assertEqual(request.session['sdi.came_from'], 'http://example.com')

    def test_form_submitted_success_w_locator_adapter(self):
        from pyramid.testing import testConfig
        from zope.interface import Interface
        from ....interfaces import IUserLocator
        from ....testing import make_site
        request = testing.DummyRequest()
        request.params['form.submitted'] = True
        request.params['login'] = 'login'
        request.params['password'] = 'password'
        request.sdiapi = DummySDIAPI()
        request.params['csrf_token'] = request.session.get_csrf_token()
        context = make_site()
        user = DummyUser(1)
        user.__oid__ = 2
        locator = DummyLocator(user)
        def _locator(context, request):
            return locator
        with testConfig() as config:
            config.testing_add_renderer(
                    'substanced.sdi.views:templates/login.pt')
            config.registry.registerAdapter(_locator, (Interface, Interface),
                                            IUserLocator)
            result = self._callFUT(context, request)
        self.assertEqual(result.location, 'http://example.com')
        self.assertTrue(result.headers)
        self.assertTrue('sdi.came_from' not in request.session)

    def test_form_submitted_success(self):
        from pyramid.testing import testConfig
        from ....testing import make_site
        request = testing.DummyRequest()
        request.params['form.submitted'] = True
        request.params['login'] = 'login'
        request.params['password'] = 'password'
        request.sdiapi = DummySDIAPI()
        request.params['csrf_token'] = request.session.get_csrf_token()
        context = make_site()
        user = DummyUser(1)
        user.__oid__ = 1
        context['principals']['users']['login'] = user
        with testConfig() as config:
            config.testing_add_renderer(
                    'substanced.sdi.views:templates/login.pt')
            result = self._callFUT(context, request)
        self.assertEqual(result.location, 'http://example.com')
        self.assertTrue(result.headers)
        self.assertTrue('sdi.came_from' not in request.session)

class DummyUser(object):
    def __init__(self, result):
        self.result = result

    def check_password(self, password):
        return self.result

class DummySDIAPI(object):
    def mgmt_path(self, *arg, **kw):
        return '/mgmt_path'

class DummyLocator(object):
    def __init__(self, user=None):
        self._user = user

    def get_user_by_login(self, login):
        self._login = login
        return self._user
