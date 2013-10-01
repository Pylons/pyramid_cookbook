import unittest

from pyramid import testing

class Test_add_lock_service(unittest.TestCase):
    def setUp(self):
        self.config = testing.setUp()

    def tearDown(self):
        testing.tearDown()
        
    def _callFUT(self, context, request):
        from ..views import add_lock_service
        return add_lock_service(context, request)

    def test_it(self):
        context = testing.DummyResource()
        context.add_service = context.__setitem__
        request = testing.DummyRequest()
        request.sdiapi = DummySDIAPI('/foo')
        request.registry = self.config.registry
        service = testing.DummyResource()
        content = DummyContentRegistry(service)
        request.registry.content = content
        response = self._callFUT(context, request)
        self.assertEqual(response.location, '/foo')
        self.assertEqual(context['locks'], service)

class TestAddLockView(unittest.TestCase):
    def setUp(self):
        self.config = testing.setUp()

    def tearDown(self):
        testing.tearDown()
        
    def _makeOne(self, context, request):
        from ..views import AddLockView
        return AddLockView(context, request)

    def test_add_success(self):
        context = testing.DummyResource()
        def add_next(obj):
            context.next = obj
        context.add_next = add_next
        request = testing.DummyRequest()
        request.sdiapi = DummySDIAPI('/foo')
        request.registry = self.config.registry
        lock = testing.DummyResource()
        content = DummyContentRegistry(lock)
        request.registry.content = content
        appstruct = {
            'timeout':None,
            'last_refresh':None,
            'ownerid':1,
            'resource':context}
        inst = self._makeOne(context, request)
        response = inst.add_success(appstruct)
        self.assertEqual(lock.ownerid, 1)
        self.assertEqual(lock.resource, context)
        self.assertEqual(response.location, '/foo')

class TestLockServiceFolderContents(unittest.TestCase):
    def _makeOne(self, context, request):
        from ..views import LockServiceFolderContents
        return LockServiceFolderContents(context, request)

    def test_get_buttons(self):
        context = testing.DummyResource()
        request = testing.DummyRequest()
        inst = self._makeOne(context, request)
        inst.get_default_buttons = lambda: [{}]
        groups = inst.get_buttons()
        self.assertEqual(len(groups), 2)

    def test_get_columns_subobject_is_None(self):
        context = testing.DummyResource()
        request = testing.DummyRequest()
        inst = self._makeOne(context, request)
        inst.get_default_columns = lambda *arg: [{}]
        columns = inst.get_columns(None)
        self.assertEqual(len(columns), 4)
        self.assertEqual(columns[1]['value'], None)
        self.assertEqual(columns[2]['value'], None)
        self.assertEqual(columns[3]['value'], None)

    def test_get_columns_subobject_is_lock(self):
        import datetime
        import pytz
        context = testing.DummyResource()
        owner = testing.DummyResource()
        owner.__name__ = 'owner'
        context.owner = owner
        resource = testing.DummyResource()
        context.resource = resource
        now = datetime.datetime(2012, 10, 12)
        context.expires = lambda: now
        request = testing.DummyRequest()
        request.user = testing.DummyResource()
        request.user.timezone = pytz.timezone('UTC')
        inst = self._makeOne(context, request)
        inst.get_default_columns = lambda *arg: [{}]
        columns = inst.get_columns(context)
        self.assertEqual(len(columns), 4)
        self.assertEqual(columns[1]['value'], 'owner')
        self.assertEqual(columns[2]['value'], '/')
        self.assertEqual(columns[3]['value'], '2012-10-12 00:00:00 UTC')

    def test_get_columns_subobject_is_lock_w_expires_returning_None(self):
        context = testing.DummyResource()
        owner = testing.DummyResource()
        owner.__name__ = 'owner'
        context.owner = owner
        resource = testing.DummyResource()
        context.resource = resource
        context.expires = lambda: None
        request = testing.DummyRequest()
        inst = self._makeOne(context, request)
        inst.get_default_columns = lambda *arg: [{}]
        columns = inst.get_columns(context)
        self.assertEqual(len(columns), 4)
        self.assertEqual(columns[1]['value'], 'owner')
        self.assertEqual(columns[2]['value'], '/')
        self.assertEqual(columns[3]['value'], None)

    def test_delete_expires(self):
        context = testing.DummyResource()
        request = testing.DummyRequest()
        request.sdiapi = DummySDIAPI('/foo')
        lock = testing.DummyResource()
        def commit_suicide():
            lock.suicided = True
        lock.commit_suicide = commit_suicide
        lock.is_valid = lambda: False
        context['lock1'] = lock
        inst = self._makeOne(context, request)
        response = inst.delete_expired()
        self.assertEqual(response.location, '/foo')
        self.assertTrue(lock.suicided)
        
        
class DummyContentRegistry(object):
    def __init__(self, result):
        self.result = result

    def create(self, *arg, **kw):
        return self.result

class DummySDIAPI(object):
    def __init__(self, result):
        self.result = result

    def mgmt_path(self, *arg, **kw):
        return self.result
    
