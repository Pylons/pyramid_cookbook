import unittest

class TestFileEditable(unittest.TestCase):

    def _getTargetClass(self):
        from . import FileEditable
        return FileEditable

    def _makeOne(self, context=None, request=None):
        if context is None:
            context = object()
        if request is None:
            request = object()
        return self._getTargetClass()(context, request)

    def test_class_conforms_to_IEditable(self):
        from zope.interface.verify import verifyClass
        from . import IEditable
        verifyClass(IEditable, self._getTargetClass())

    def test_instance_conforms_to_IEditable(self):
        from zope.interface.verify import verifyObject
        from . import IEditable
        verifyObject(IEditable, self._makeOne())

    def test_get_context_has_mimetype(self):
        from pyramid.testing import DummyRequest
        from pyramid.testing import DummyResource
        context = DummyResource()
        context.mimetype = 'application/foo'
        blob = DummyResource()
        here = __file__
        def committed():
            return here
        blob.committed = committed
        context.blob = blob
        request = DummyRequest()
        inst = self._makeOne(context, request)
        iterable, mimetype = inst.get()
        self.assertEqual(mimetype, 'application/foo')
        self.assertEqual(type(next(iterable)), bytes)

    def test_get_context_has_no_mimetype(self):
        from pyramid.testing import DummyRequest
        from pyramid.testing import DummyResource
        context = DummyResource()
        context.mimetype = None
        blob = DummyResource()
        here = __file__
        def committed():
            return here
        blob.committed = committed
        context.blob = blob
        request = DummyRequest()
        inst = self._makeOne(context, request)
        iterable, mimetype = inst.get()
        self.assertEqual(mimetype, 'application/octet-stream')
        self.assertEqual(type(next(iterable)), bytes)

    def test_put(self):
        from pyramid.testing import DummyRequest
        from pyramid.testing import DummyResource
        context = DummyResource()
        fp = 'fp'
        def upload(_fp):
            self.assertEqual(_fp, fp)
        context.upload = upload
        request = DummyRequest()
        inst = self._makeOne(context, request)
        inst.put(fp)

class Test_register_editable_adapter(unittest.TestCase):

    def setUp(self):
        from pyramid.testing import setUp
        self.config = setUp()

    def tearDown(self):
        from pyramid.testing import tearDown
        tearDown()

    def _callFUT(self, config, adapter, iface):
        from . import register_editable_adapter
        return register_editable_adapter(config, adapter, iface)

    def test_it(self):
        from zope.interface import Interface
        from . import IEditable
        class ITesting(Interface):
            pass
        config = DummyConfigurator(self.config.registry)
        def _editable_factory(context, reqeust): #pragma NO COVER
            pass
        self._callFUT(config, _editable_factory, ITesting)
        self.assertEqual(len(config.actions), 1)
        action = config.actions[0]
        self.assertEqual(action['discriminator'],
                         ('sd-editable-adapter', ITesting))
        self.assertEqual(
            action['introspectables'], (config.intr,)
            )
        callable = action['callable']
        callable()
        wrapper = self.config.registry.adapters.lookup(
            (ITesting, Interface), IEditable)
        self.assertEqual(config.intr['registered'], wrapper)

class DummyIntrospectable(dict):
    pass

class DummyConfigurator(object):
    _ainfo = None
    def __init__(self, registry):
        self.actions = []
        self.intr = DummyIntrospectable()
        self.registry = registry
        self.indexes = []

    def action(self, discriminator, callable, order=None, introspectables=()):
        self.actions.append(
            {
            'discriminator':discriminator,
            'callable':callable,
            'order':order,
            'introspectables':introspectables,
            })

    def introspectable(self, category, discriminator, name, single):
        return self.intr

