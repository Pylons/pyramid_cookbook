import unittest
from pyramid import testing

class TestPropertySheetsView(unittest.TestCase):
    def setUp(self):
        self.config = testing.setUp()

    def tearDown(self):
        testing.tearDown()
        
    def _makeOne(self, request):
        from ..views import PropertySheetsView
        return PropertySheetsView(request)

    def test_ctor_no_viewable_sheet_factories(self):
        from pyramid.httpexceptions import HTTPNotFound
        request = testing.DummyRequest()
        request.registry = testing.DummyResource()
        request.registry.content = DummyContent([])
        resource = testing.DummyResource()
        request.context = resource
        self.assertRaises(HTTPNotFound, self._makeOne, request)

    def test_ctor_no_subpath(self):
        request = testing.DummyRequest()
        request.registry = testing.DummyResource()
        request.registry.content = DummyContent([('name', DummyPropertySheet)])
        resource = testing.DummyResource()
        request.context = resource
        inst = self._makeOne(request)
        self.assertEqual(inst.active_sheet_name, 'name')
        self.assertTrue(inst.schema, 'schema')
        self.assertEqual(inst.sheet_names, ['name'])

    def test_ctor_with_subpath(self):
        request = testing.DummyRequest()
        request.subpath = ('othername',)
        request.registry = testing.DummyResource()
        request.registry.content = DummyContent(
            [('othername', DummyPropertySheet)])
        resource = testing.DummyResource()
        request.context = resource
        inst = self._makeOne(request)
        self.assertEqual(inst.active_sheet_name, 'othername')
        self.assertTrue(inst.schema, 'schema')
        self.assertEqual(inst.sheet_names, ['othername'])

    def test_save_success_no_change_permission(self):
        from pyramid.httpexceptions import HTTPForbidden
        request = testing.DummyRequest()
        request.sdiapi = DummySDIAPI()
        sheet_factory = DummySheetFactory([('change', 'sdi.change')])
        request.registry.content = DummyContent(
            [('name', sheet_factory)])
        resource = testing.DummyResource()
        request.context = resource
        inst = self._makeOne(request)
        self.config.testing_securitypolicy(permissive=False)
        self.assertRaises(HTTPForbidden, inst.save_success, {'a':1})

    def test_save_success_cannot_lock(self):
        from zope.interface import alsoProvides
        from substanced.form import FormError
        from substanced.interfaces import IFolder
        request = testing.DummyRequest()
        request.sdiapi = DummySDIAPI()
        request.registry.content = DummyContent(
            [('name', DummyPropertySheet)])
        resource = testing.DummyResource()
        alsoProvides(resource, IFolder)
        resource['locks'] = DummyLockService(False)
        request.context = resource
        inst = self._makeOne(request)
        self.assertRaises(FormError, inst.save_success, {'a':1})

    def test_save_success_ok(self):
        from zope.interface import alsoProvides
        from substanced.interfaces import IFolder
        request = testing.DummyRequest()
        request.sdiapi = DummySDIAPI()
        request.registry.content = DummyContent(
            [('name', DummyPropertySheet)])
        resource = testing.DummyResource()
        alsoProvides(resource, IFolder)
        resource['locks'] = DummyLockService(True)
        request.context = resource
        inst = self._makeOne(request)
        response = inst.save_success({'a':1})
        self.assertEqual(response.location, '/mgmt_path')
        self.assertEqual(inst.active_sheet.struct, {'a': 1})
        self.assertTrue(inst.active_sheet.after)
        self.assertEqual(request.sdiapi.flashed,
                         ('Updated properties', 'success') )

    def test_show(self):
        request = testing.DummyRequest()
        request.registry = testing.DummyResource()
        request.registry.content = DummyContent(
            [('name', DummyPropertySheet)])
        resource = testing.DummyResource()
        request.context = resource
        inst = self._makeOne(request)
        form = DummyForm()
        result = inst.show(form)
        self.assertTrue(form.rendered)
        self.assertEqual(result['form'], None)

    def test_has_permission_to_no_permissions(self):
        request = testing.DummyRequest()
        request.registry = testing.DummyResource()
        request.registry.content = DummyContent(
            [('name', DummyPropertySheet)])
        resource = testing.DummyResource()
        request.context = resource
        inst = self._makeOne(request)
        result = inst.has_permission_to('view', DummyPropertySheet)
        self.assertTrue(result)

    def test_has_permission_to_no_specific_permission(self):
        request = testing.DummyRequest()
        request.registry = testing.DummyResource()
        sheet_factory = DummySheetFactory([('edit', 'sdi.edit')])
        request.registry.content = DummyContent(
            [('name', sheet_factory)])
        resource = testing.DummyResource()
        request.context = resource
        inst = self._makeOne(request)
        result = inst.has_permission_to('view', DummyPropertySheet)
        self.assertTrue(result)
        
    def test_has_permission_to_denied(self):
        request = testing.DummyRequest()
        request.registry = self.config.registry
        sheet_factory = DummySheetFactory([('view', 'sdi.view')])
        request.registry.content = DummyContent(
            [('name', sheet_factory)])
        resource = testing.DummyResource()
        request.context = resource
        inst = self._makeOne(request)
        self.config.testing_securitypolicy(permissive=False)
        result = inst.has_permission_to('view', sheet_factory)
        self.assertFalse(result)

    def test_viewable_sheet_factories_no_permission(self):
        sheet_factory = DummySheetFactory([('view', 'sdi.view')])
        request = testing.DummyRequest()
        request.registry.content = DummyContent(
            [('name', sheet_factory)])
        resource = testing.DummyResource()
        request.context = resource
        inst = self._makeOne(request)
        self.config.testing_securitypolicy(permissive=False)
        result = inst.viewable_sheet_factories()
        self.assertEqual(result, [])
        

class Test_has_permission_to_view_any_propertysheet(unittest.TestCase):
    def setUp(self):
        self.config = testing.setUp()

    def tearDown(self):
        testing.tearDown()

    def _callFUT(self, context, request):
        from ..views import has_permission_to_view_any_propertysheet
        return has_permission_to_view_any_propertysheet(context, request)
        
    def test_no_candidates(self):
        request = testing.DummyRequest()
        request.registry.content = DummyContent([])
        context = testing.DummyResource()
        self.assertFalse(self._callFUT(context, request))
        
    def test_no_permission_required(self):
        request = testing.DummyRequest()
        request.registry.content = DummyContent([(True, True)])
        context = testing.DummyResource()
        self.assertTrue(self._callFUT(context, request))

    def test_permission_required_denied(self):
        self.config.testing_securitypolicy(permissive=False)
        request = testing.DummyRequest()
        sheet_factory = DummySheetFactory([('view', 'sdi.view')])
        request.registry.content = DummyContent([('sheet', sheet_factory)])
        context = testing.DummyResource()
        self.assertFalse(self._callFUT(context, request))

    def test_permission_required_allowed(self):
        self.config.testing_securitypolicy(permissive=True)
        request = testing.DummyRequest()
        sheet_factory = DummySheetFactory([('view', 'sdi.view')])
        request.registry.content = DummyContent([('sheet', sheet_factory)])
        context = testing.DummyResource()
        self.assertTrue(self._callFUT(context, request))

    def test_no_view_permission_required_allowed(self):
        request = testing.DummyRequest()
        sheet_factory = DummySheetFactory([('edit', 'sdi.edit')])
        request.registry.content = DummyContent([('sheet', sheet_factory)])
        context = testing.DummyResource()
        self.assertTrue(self._callFUT(context, request))


class DummySheetFactory(object):

    def __init__(self, permissions, schema=None):
        self.permissions = permissions
        self.schema = schema

    def __call__(self, *args):
        return self

class DummyForm(object):
    def __init__(self):
        self.rendered = []
        
    def render(self, appstruct=None, readonly=False):
        self.rendered.append((appstruct, readonly))

class DummyPropertySheet(object):
    schema = 'schema'
    def __init__(self, context, request):
        self.context = context
        self.request = request

    def get(self):
        return {}

    def set(self, struct):
        self.struct = struct

    def after_set(self, changed):
        self.changed = changed
        self.after = True

class DummyContent(object):
    def __init__(self, result):
        self.result = result

    def metadata(self, context, name, default=None):
        return self.result
    
class Dummy(object):
    pass

class DummySDIAPI(object):
    def mgmt_path(self, *arg, **kw):
        return '/mgmt_path'

    def flash_with_undo(self, msg, category):
        self.flashed = (msg, category)

class DummyUser(object):
    def __init__(self, owner):
        self.__name__ = owner

class DummyLock(object):
    def __init__(self, owner, comment):
        self.owner = DummyUser(owner)
        self.comment = comment

class DummyLockService(object):
    __is_service__ = True
    def __init__(self, can_lock):
        self._can_lock = can_lock

    def borrow_lock(self, resource, owner, locktype=None):
        from substanced.locking import LockError
        if not self._can_lock:
            raise LockError(DummyLock('otheruser', 'existing'))
        return True
