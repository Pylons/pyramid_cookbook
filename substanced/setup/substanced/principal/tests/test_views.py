import unittest
import colander
from pyramid import testing

class Test_add_principals_service(unittest.TestCase):
    def _callFUT(self, context, request):
        from ..views import add_principals_service
        return add_principals_service(context, request)

    def test_it(self):
        context = testing.DummyResource()
        request = testing.DummyRequest()
        request.sdiapi = DummySDIAPI()
        service = testing.DummyResource()
        request.registry.content = DummyContentRegistry(service)
        result = self._callFUT(context, request)
        self.assertEqual(context['principals'], service)
        self.assertEqual(result.location, '/mgmt_path')

class TestAddUserView(unittest.TestCase):
    def _makeOne(self, context, request):
        from ..views import AddUserView
        return AddUserView(context, request)

    def _makeRequest(self, resource):
        request = testing.DummyRequest()
        request.registry = testing.DummyResource()
        request.registry.content = DummyContentRegistry(resource)
        request.sdiapi = DummySDIAPI()
        return request

    def test_add_success(self):
        resource = DummyPrincipal()
        request = self._makeRequest(resource)
        context = testing.DummyResource()
        inst = self._makeOne(context, request)
        resp = inst.add_success({'name':'name', 'groupids':(1,)})
        self.assertEqual(context['name'], resource)
        self.assertEqual(resp.location, '/mgmt_path')
        self.assertEqual(resource.groupids, (1,))

class TestAddGroupView(unittest.TestCase):
    def _makeOne(self, context, request):
        from ..views import AddGroupView
        return AddGroupView(context, request)

    def _makeRequest(self, resource):
        request = testing.DummyRequest()
        request.registry = testing.DummyResource()
        request.registry.content = DummyContentRegistry(resource)
        request.sdiapi = DummySDIAPI()
        return request

    def test_add_success(self):
        resource = DummyPrincipal()
        request = self._makeRequest(resource)
        context = testing.DummyResource()
        inst = self._makeOne(context, request)
        resp = inst.add_success({'name':'name', 'memberids':(1,)})
        self.assertEqual(context['name'], resource)
        self.assertEqual(resp.location, '/mgmt_path')
        self.assertEqual(resource.memberids, (1,))

class Test_password_validator(unittest.TestCase):
    def _makeOne(self, node, kw):
        from ..views import password_validator
        return password_validator(node, kw)

    def test_it_success(self):
        request = testing.DummyRequest()
        context = testing.DummyResource()
        def check_password(pwd):
            return True
        context.check_password = check_password
        kw = dict(request=request, context=context)
        inst = self._makeOne(None, kw)
        self.assertEqual(inst(None, 'pwd'), None)

    def test_it_failure(self):
        request = testing.DummyRequest()
        context = testing.DummyResource()
        def check_password(pwd):
            return False
        context.check_password = check_password
        kw = dict(request=request, context=context)
        inst = self._makeOne(None, kw)
        self.assertRaises(colander.Invalid, inst, None, 'pwd')

class TestChangePasswordView(unittest.TestCase):
    def _makeOne(self, context, request):
        from ..views import ChangePasswordView
        return ChangePasswordView(context, request)

    def test_add_success(self):
        context = DummyPrincipal()
        request = testing.DummyRequest()
        request.sdiapi = DummySDIAPI()
        inst = self._makeOne(context, request)
        resp = inst.change_success({'password':'password'})
        self.assertEqual(context.password, 'password')
        self.assertEqual(resp.location, '/mgmt_path')
        self.assertTrue(request.session['_f_success'])

class TestRequestResetView(unittest.TestCase):
    def _makeOne(self, context, request):
        from ..views import ResetRequestView
        return ResetRequestView(context, request)

    def _makeRequest(self):
        request = testing.DummyRequest()
        request.sdiapi = DummySDIAPI()
        return request

    def _makeSite(self):
        from substanced.testing import make_site
        return make_site()

    def test_send_success(self):
        site = self._makeSite()
        user = DummyPrincipal()
        site['principals']['users']['user'] = user
        request = self._makeRequest()
        inst = self._makeOne(site, request)
        resp = inst.send_success({'login':'user'})
        self.assertEqual(resp.location, '/mgmt_path')
        self.assertTrue(user.emailed_password_reset)

class TestResetView(unittest.TestCase):
    def _makeOne(self, context, request):
        from ..views import ResetView
        return ResetView(context, request)

    def _makeRequest(self):
        request = testing.DummyRequest()
        request.sdiapi = DummySDIAPI()
        return request

    def test_reset_success(self):
        context = testing.DummyResource()
        def reset_password(password):
            self.assertEqual(password, 'thepassword')
        context.reset_password = reset_password
        request = self._makeRequest()
        inst = self._makeOne(context, request)
        resp = inst.reset_success({'new_password':'thepassword'})
        self.assertEqual(resp.location, '/mgmt_path')
    

class Test_login_validator(unittest.TestCase):
    def _makeOne(self, node, kw):
        from ..views import login_validator
        return login_validator(node, kw)

    def _makeSite(self):
        from substanced.interfaces import IFolder
        site = testing.DummyResource(__provides__=IFolder)
        principals = testing.DummyResource(__is_service__=True)
        users = testing.DummyResource()
        site['principals'] = principals
        principals['users'] = users
        return site

    def test_no_such_user(self):
        request = testing.DummyRequest()
        site = self._makeSite()
        inst = self._makeOne(None, dict(request=request, context=site))
        self.assertRaises(colander.Invalid, inst, None, 'fred')

    def test_user_exists(self):
        request = testing.DummyRequest()
        site = self._makeSite()
        fred = testing.DummyResource()
        site['principals']['users']['fred'] = fred
        inst = self._makeOne(None, dict(request=request, context=site))
        self.assertEqual(inst(None, 'fred'), None)

class DummyPrincipal(object):
    def set_password(self, password):
        self.password = password

    def email_password_reset(self, request):
        self.emailed_password_reset = True

class DummyContentRegistry(object):
    def __init__(self, resource):
        self.resource = resource

    def create(self, iface, *arg, **kw):
        return self.resource
        
class DummySDIAPI(object):
    def mgmt_path(self, *arg, **kw):
        return '/mgmt_path'
