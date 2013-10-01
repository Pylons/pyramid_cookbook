import unittest
from pyramid import testing

class TestAllowedIndexDiscriminator(unittest.TestCase):
    def setUp(self):
        self.config = testing.setUp()

    def tearDown(self):
        testing.tearDown()
        
    def _makeOne(self, permissions=None):
        from ..discriminators import AllowedIndexDiscriminator
        return AllowedIndexDiscriminator(permissions)

    def test_it_namedpermission(self):
        inst = self._makeOne('view')
        resource = testing.DummyResource()
        result = inst(resource, None)
        self.assertEqual(result, [('system.Everyone', 'view')])

    def test_it_namedpermission_notpermitted(self):
        from pyramid.interfaces import IAuthenticationPolicy
        self.config.testing_securitypolicy(permissive=False)
        pol = self.config.registry.getUtility(IAuthenticationPolicy)
        def noprincipals(context, permission):
            return []
        pol.principals_allowed_by_permission = noprincipals
        resource = testing.DummyResource()
        inst = self._makeOne('view')
        result = inst(resource, None)
        self.assertEqual(result, None)

    def test_it_unnamedpermission_no_permissions_registered(self):
        inst = self._makeOne()
        resource = testing.DummyResource()
        result = inst(resource, None)
        self.assertEqual(result, None)

    def test_it_unnamedpermission_two_permissions_registered(self):
        self.config.add_permission('view')
        self.config.add_permission('edit')
        inst = self._makeOne()
        resource = testing.DummyResource()
        result = inst(resource, None)
        self.assertEqual(
            sorted(result),
            [('system.Everyone', 'edit'), ('system.Everyone', 'view')]
            )

class TestIndexViewDiscriminator(unittest.TestCase):
    def setUp(self):
        self.config = testing.setUp()

    def tearDown(self):
        testing.tearDown()
        
    def _makeOne(self, catalog_name, index_name):
        from ..discriminators import IndexViewDiscriminator
        return IndexViewDiscriminator(catalog_name, index_name)

    def test_ctor(self):
        inst = self._makeOne('system', 'attr')
        self.assertEqual(inst.catalog_name, 'system')
        self.assertEqual(inst.index_name, 'attr')

    def test_call_no_index_view(self):
        inst = self._makeOne('system', 'attr')
        result = inst(None, True)
        self.assertEqual(result, True)

    def test_call_with_index_view(self):
        from zope.interface import Interface
        from substanced.interfaces import IIndexView
        registry = self.config.registry
        resource = testing.DummyResource()
        def view(_resource, default):
            self.assertEqual(default, True)
            self.assertEqual(_resource, resource)
            return True
        registry.registerAdapter(view, (Interface,), IIndexView, 'system|attr')
        inst = self._makeOne('system', 'attr')
        result = inst(resource, True)
        self.assertEqual(result, True)
        
            

class Test_dummy_discriminator(unittest.TestCase):
    def _callFUT(self, object, default):
        from ..discriminators import dummy_discriminator
        return dummy_discriminator(object, default)

    def test_it(self):
        result = self._callFUT(None, '123')
        self.assertEqual(result, '123')

