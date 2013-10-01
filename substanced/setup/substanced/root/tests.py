import unittest
from pyramid import testing

class TestRoot(unittest.TestCase):
    def setUp(self):
        testing.setUp()

    def tearDown(self):
        testing.tearDown()
        
    def _makeOne(self):
        from . import Root
        inst = Root()
        return inst

    def test_ctor(self):
        inst = self._makeOne()
        self.assertEqual(list(inst.items()), [])

    def _makeRegistry(self, settings):
        created = testing.DummyResource()
        group = testing.DummyResource()
        def connect(other):
            group.connected = other
        memberids = testing.DummyResource()
        memberids.connect = connect
        group.memberids = memberids
        group.__oid__ = 1
        user = testing.DummyResource()
        catalog = testing.DummyResource()
        catalog.update_indexes = lambda *arg, **kw: True
        catalog.index_doc = lambda *arg, **kw: True
        def add_user(*arg, **kw):
            return user
        def add_group(*arg, **kw):
            return group
        def add_catalog(name):
            return catalog
        created_stack = []
        created.add_user = add_user
        created.add_group = add_group
        created2 = testing.DummyResource()
        created2.add_catalog = add_catalog
        locks = testing.DummyResource()
        created_stack = [created2, created, locks]
        registry = testing.DummyResource()
        registry.settings = settings
        registry.content = testing.DummyResource()
        def create(type, *arg, **kw):
            return created_stack.pop(0)
        registry.content.create = create
        registry.group = group
        registry.user = user
        registry.created = created
        registry.subscribers = lambda *arg: True
        return registry

    def test_after_create_with_password(self):
        settings = {
            'substanced.initial_password':'pass',
            'substanced.initial_login':'login',
            'substanced.initial_email':'email@example.com',
            }
        registry = self._makeRegistry(settings)
        inst = self._makeOne()
        inst.__oid__ = 1
        inst.after_create(inst, registry)
        self.assertTrue('__objectmap__' in inst.__dict__)
        principals = inst['principals']
        locks = inst['locks']
        self.assertTrue(principals.__is_service__)
        self.assertTrue(registry.group.connected)
        self.assertTrue(inst.__acl__)
        self.assertFalse(registry.created.__sdi_deletable__)
        self.assertTrue(locks.__is_service__)

    def test_after_create_without_password(self):
        from pyramid.exceptions import ConfigurationError
        settings = {}
        registry = self._makeRegistry(settings)
        inst = self._makeOne()
        self.assertRaises(ConfigurationError, inst.after_create, inst, registry)
