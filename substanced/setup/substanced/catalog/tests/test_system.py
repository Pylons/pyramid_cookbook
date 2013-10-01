import unittest
from pyramid import testing

from zope.interface import Interface
from zope.interface import alsoProvides

class TestSystemIndexViews(unittest.TestCase):
    def setUp(self):
        self.config = testing.setUp()

    def tearDown(self):
        testing.tearDown()
        
    def _makeOne(self, resource):
        from ..system import SystemIndexViews
        return SystemIndexViews(resource)

    def test_interfaces(self):
        resource = testing.DummyResource()
        class Dummy1(Interface):
            pass
        class Dummy2(Interface):
            pass
        alsoProvides(resource, Dummy1)
        alsoProvides(resource, Dummy2)
        inst = self._makeOne(resource)
        result = inst.interfaces(None)
        self.assertEqual(len(result), 3)
        self.assertTrue(Dummy1 in result)
        self.assertTrue(Dummy2 in result)
        self.assertTrue(Interface in result)

    def test_name_has_no_name(self):
        resource = object()
        inst = self._makeOne(resource)
        result = inst.name(None)
        self.assertEqual(result, None)

    def test_name_has_name(self):
        resource = testing.DummyResource()
        resource.__name__ = 'foo'
        inst = self._makeOne(resource)
        result = inst.name(None)
        self.assertEqual(result, 'foo')

    def test_name_has_name_None(self):
        resource = testing.DummyResource()
        resource.__name__ = None
        inst = self._makeOne(resource)
        result = inst.name('abc')
        self.assertEqual(result, 'abc')

    def test_text_name_doesnt_exist(self):
        resource = testing.DummyResource()
        inst = self._makeOne(resource)
        result = inst.text(None)
        self.assertEqual(result, None)

    def test_text_name_is_not_string(self):
        resource = testing.DummyResource()
        resource.__name__ = False
        inst = self._makeOne(resource)
        result = inst.text(None)
        self.assertEqual(result, False)

    def test_text_name_has_no_separators(self):
        resource = testing.DummyResource()
        resource.__name__ = 'foobar'
        inst = self._makeOne(resource)
        result = inst.text(None)
        self.assertEqual(result, 'foobar')

    def test_text_name_has_separators(self):
        resource = testing.DummyResource()
        resource.__name__ = 'foo-bar_baz.pt,foz'
        inst = self._makeOne(resource)
        result = inst.text(None)
        self.assertEqual(result, 'foo-bar_baz.pt,foz foo bar baz pt foz')

    def test_content_type(self):
        resource = testing.DummyResource()
        content = testing.DummyResource()
        def typeof(resrc):
            self.assertEqual(resrc, resource)
            return 'foo'
        content.typeof = typeof
        self.config.registry.content = content
        inst = self._makeOne(resource)
        result = inst.content_type(None)
        self.assertEqual(result, 'foo')

    def test_content_type_None(self):
        resource = testing.DummyResource()
        content = testing.DummyResource()
        def typeof(resrc):
            self.assertEqual(resrc, resource)
            return None
        content.typeof = typeof
        self.config.registry.content = content
        inst = self._makeOne(resource)
        result = inst.content_type('default')
        self.assertEqual(result, 'default')
        
