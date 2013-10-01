import unittest
from pyramid import testing

import colander

class TestPropertySheet(unittest.TestCase):
    def _makeOne(self, context, request):
        from .. import PropertySheet
        return PropertySheet(context, request)

    def test_get(self):
        context = testing.DummyResource()
        request = testing.DummyRequest()
        inst = self._makeOne(context, request)
        inst.schema = [DummySchemaNode('title'),
                       DummySchemaNode('description'),
                       DummySchemaNode('another')]
        context.title = 'title'
        context.description = 'description'
        vals = inst.get()
        self.assertEqual(vals['title'], 'title')
        self.assertEqual(vals['description'], 'description')
        self.assertEqual(vals['another'], colander.null)

    def test_set(self):
        context = testing.DummyResource()
        request = testing.DummyRequest()
        inst = self._makeOne(context, request)
        context.title = 'title'
        context.description = 'description'
        inst.schema = [DummySchemaNode('title'),
                       DummySchemaNode('description')]
        inst.set(dict(title='t', description='d'))
        self.assertEqual(context.title, 't')
        self.assertEqual(context.description, 'd')

    def test_set_schema_missing_value(self):
        context = testing.DummyResource()
        request = testing.DummyRequest()
        inst = self._makeOne(context, request)
        context.title = 'title'
        context.description = 'description'
        inst.schema = [DummySchemaNode('title')]
        inst.set(dict(title='t', description='d'))
        self.assertEqual(context.title, 't')
        self.assertEqual(context.description, 'description')

    def test_set_nochange(self):
        context = testing.DummyResource()
        request = testing.DummyRequest()
        inst = self._makeOne(context, request)
        inst.schema = [DummySchemaNode('title'),
                       DummySchemaNode('description')]
        context.title = 't'
        context.description = 'd'
        inst.set(dict(title='t', description='d'))
        self.assertEqual(context.title, 't')
        self.assertEqual(context.description, 'd')

    def test_set_with_omit_iter(self):
        context = testing.DummyResource()
        request = testing.DummyRequest()
        inst = self._makeOne(context, request)
        context.title = 'title'
        context.description = 'description'
        inst.schema = [DummySchemaNode('title'),
                       DummySchemaNode('description')]
        inst.set(dict(title='t', description='d'), omit=('title',))
        self.assertEqual(context.title, 'title')
        self.assertEqual(context.description, 'd')

    def test_set_with_omit_noniter(self):
        context = testing.DummyResource()
        request = testing.DummyRequest()
        inst = self._makeOne(context, request)
        context.title = 'title'
        context.description = 'description'
        inst.schema = [DummySchemaNode('title'),
                       DummySchemaNode('description')]
        inst.set(dict(title='t', description='d'), omit='title')
        self.assertEqual(context.title, 'title')
        self.assertEqual(context.description, 'd')

    def test_after_set_changed_True(self):
        from substanced.event import ObjectModified
        request = testing.DummyRequest()
        request.registry = DummyRegistry()
        context = testing.DummyResource()
        inst = self._makeOne(context, request)
        inst.after_set(True)
        subscribed = request.registry.subscribed[0]
        self.assertEqual(subscribed[1], None)
        self.assertEqual(subscribed[0][0].__class__, ObjectModified)
        self.assertEqual(subscribed[0][1], context)

    def test_after_set_changed_False(self):
        request = testing.DummyRequest()
        request.registry = DummyRegistry()
        context = testing.DummyResource()
        inst = self._makeOne(context, request)
        inst.after_set(False)
        subscribed = request.registry.subscribed
        self.assertEqual(len(subscribed), 0)
        
class Test_is_propertied(unittest.TestCase):
    def setUp(self):
        self.config = testing.setUp()

    def tearDown(self):
        testing.tearDown()

    def _callFUT(self, resource, registry=None):
        from .. import is_propertied
        return is_propertied(resource, registry)

    def test_no_registry_passed(self):
        resource = Dummy()
        self.config.registry.content = DummyContent(True)
        self.assertTrue(self._callFUT(resource))

    def test_true(self):
        resource = Dummy()
        registry = Dummy()
        registry.content = DummyContent(())
        self.assertTrue(self._callFUT(resource, registry))

    def test_false(self):
        resource = Dummy()
        registry = Dummy()
        registry.content = DummyContent(None)
        self.assertFalse(self._callFUT(resource, registry))

class Test_PropertiedPredicate(unittest.TestCase):
    def _makeOne(self, val, config):
        from .. import _PropertiedPredicate
        return _PropertiedPredicate(val, config)

    def test_text(self):
        config = Dummy()
        config.registry = Dummy()
        inst = self._makeOne(True, config)
        self.assertEqual(inst.text(), 'propertied = True')

    def test_phash(self):
        config = Dummy()
        config.registry = Dummy()
        inst = self._makeOne(True, config)
        self.assertEqual(inst.phash(), 'propertied = True')

    def test__call__(self):
        config = Dummy()
        config.registry = Dummy()
        inst = self._makeOne(True, config)
        def is_propertied(context, registry):
            self.assertEqual(context, None)
            self.assertEqual(registry, config.registry)
            return True
        inst.is_propertied = is_propertied
        self.assertEqual(inst(None, None), True)

class Dummy(object):
    pass

class DummyRegistry(object):
    def __init__(self):
        self.subscribed = []
    
    def subscribers(self, *args):
        self.subscribed.append(args)
        
class DummyContent(object):
    def __init__(self, result=None):
        self.result = result
        
    def metadata(self, *arg, **kw):
        return self.result

class DummySchemaNode(object):
    def __init__(self, name):
        self.name = name
