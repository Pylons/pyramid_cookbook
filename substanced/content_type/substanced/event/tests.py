import unittest

from pyramid import testing

from zope.interface import Interface

class IDummy(Interface):
    pass

class Test_ContentEventSubscriber(unittest.TestCase):
    
    event = IDummy

    def setUp(self):
        self.config = testing.setUp()

    def tearDown(self):
        testing.tearDown()

    def _makeOne(self, obj=None, **predicates):
        from . import _ContentEventSubscriber
        class Subscriber(_ContentEventSubscriber):
            event = self.event
        return Subscriber(obj=obj, **predicates)

    def test_register_defaults(self):
        dec = self._makeOne()
        def foo(event): pass
        config = DummyConfigurator()
        scanner = Dummy()
        scanner.config = config
        dec.register(scanner, None, foo)
        self.assertEqual(len(config.subscribed), 1)
        subscriber = config.subscribed[0]
        self.assertEqual(subscriber['wrapped'], foo)
        self.assertEqual(subscriber['ifaces'],
                         [self.event, Interface])
        
    def test_register_object_only(self):
        class IFoo(Interface): pass
        dec = self._makeOne(IFoo)
        def foo(event): pass
        config = DummyConfigurator()
        scanner = Dummy()
        scanner.config = config
        dec.register(scanner, None, foo)
        self.assertEqual(len(config.subscribed), 1)
        subscriber = config.subscribed[0]
        self.assertEqual(subscriber['wrapped'], foo)
        self.assertEqual(subscriber['ifaces'],
                         [self.event, IFoo])

    def test_with_predicates(self):
        class IFoo(Interface): pass
        dec = self._makeOne(IFoo, a=1)
        def foo(event): pass
        config = DummyConfigurator()
        scanner = Dummy()
        scanner.config = config
        dec.register(scanner, None, foo)
        self.assertEqual(len(config.subscribed), 1)
        subscriber = config.subscribed[0]
        self.assertEqual(subscriber['wrapped'], foo)
        self.assertEqual(subscriber['ifaces'],
                         [self.event, IFoo])
        self.assertEqual(subscriber['predicates'], {'a':1})

    def test___call__(self):
        dec = self._makeOne()
        dummy_venusian = DummyVenusian()
        dec.venusian = dummy_venusian
        def foo(): pass
        dec(foo)
        self.assertEqual(dummy_venusian.attached,
                         [(foo, dec.register, 'substanced')])

class Test_FolderEventSubscriber(unittest.TestCase):
    event = IDummy

    def setUp(self):
        self.config = testing.setUp()

    def tearDown(self):
        testing.tearDown()

    def _makeOne(self, obj=None, container=None, **predicates):
        from . import _FolderEventSubscriber
        class Subscriber(_FolderEventSubscriber):
            event = self.event
        return Subscriber(obj=obj, container=container, **predicates)

    def test_register_object_only(self):
        class IFoo(Interface): pass
        dec = self._makeOne(IFoo)
        def foo(event): pass
        config = DummyConfigurator()
        scanner = Dummy()
        scanner.config = config
        dec.register(scanner, None, foo)
        self.assertEqual(len(config.subscribed), 1)
        subscriber = config.subscribed[0]
        self.assertEqual(subscriber['wrapped'], foo)
        self.assertEqual(subscriber['ifaces'],
                         [self.event, IFoo, Interface])

    def test_register_neither_object_nor_container(self):
        class IFoo(Interface): pass
        class IBar(Interface): pass
        dec = self._makeOne()
        def foo(event): pass
        config = DummyConfigurator()
        scanner = Dummy()
        scanner.config = config
        dec.register(scanner, None, foo)
        self.assertEqual(len(config.subscribed), 1)
        subscriber = config.subscribed[0]
        self.assertEqual(subscriber['wrapped'], foo)
        self.assertEqual(subscriber['ifaces'],
                         [self.event, Interface, Interface])

    def test_register_container_only(self):
        class IFoo(Interface): pass
        dec = self._makeOne(container=IFoo)
        def foo(event): pass
        config = DummyConfigurator()
        scanner = Dummy()
        scanner.config = config
        dec.register(scanner, None, foo)
        self.assertEqual(len(config.subscribed), 1)
        subscriber = config.subscribed[0]
        self.assertEqual(subscriber['wrapped'], foo)
        self.assertEqual(subscriber['ifaces'],
                         [self.event, Interface, IFoo])

    def test_register_object_and_container(self):
        class IFoo(Interface): pass
        class IBar(Interface): pass
        dec = self._makeOne(obj=IFoo, container=IBar)
        def foo(event): pass
        config = DummyConfigurator()
        scanner = Dummy()
        scanner.config = config
        dec.register(scanner, None, foo)
        self.assertEqual(len(config.subscribed), 1)
        subscriber = config.subscribed[0]
        self.assertEqual(subscriber['wrapped'], foo)
        self.assertEqual(subscriber['ifaces'],
                         [self.event, IFoo, IBar])

    
class Test_SimpleSubscriber(unittest.TestCase):
    
    event = IDummy

    def setUp(self):
        self.config = testing.setUp()

    def tearDown(self):
        testing.tearDown()

    def _makeOne(self, **predicates):
        from . import _SimpleSubscriber
        class Subscriber(_SimpleSubscriber):
            event = self.event
        return Subscriber(**predicates)

    def test_register_defaults(self):
        dec = self._makeOne()
        def foo(event): pass
        config = DummyConfigurator()
        scanner = Dummy()
        scanner.config = config
        dec.register(scanner, None, foo)
        self.assertEqual(len(config.subscribed), 1)
        subscriber = config.subscribed[0]
        wrapper = subscriber['wrapped']
        event = Dummy()
        self.assertEqual(wrapper(event), None)
        self.assertEqual(event.registry, scanner.config.registry)
        self.assertEqual(wrapper.wrapped, foo)
        self.assertEqual(subscriber['ifaces'], self.event)
        
    def test_with_predicates(self):
        class IFoo(Interface): pass
        dec = self._makeOne(a=1)
        def foo(event): pass
        config = DummyConfigurator()
        scanner = Dummy()
        scanner.config = config
        dec.register(scanner, None, foo)
        self.assertEqual(len(config.subscribed), 1)
        subscriber = config.subscribed[0]
        self.assertEqual(subscriber['wrapped'].wrapped, foo)
        self.assertEqual(subscriber['ifaces'], self.event)
        self.assertEqual(subscriber['predicates'], {'a':1})

    def test___call__(self):
        dec = self._makeOne()
        dummy_venusian = DummyVenusian()
        dec.venusian = dummy_venusian
        def foo(): pass
        dec(foo)
        self.assertEqual(dummy_venusian.attached,
                         [(foo, dec.register, 'substanced')])

class TestObjectWillBeRemoved(unittest.TestCase):
    def _makeOne(self, *arg, **kw):
        from . import ObjectWillBeRemoved
        return ObjectWillBeRemoved(*arg, **kw)

    def test_removed_oids_objectmap_is_None(self):
        obj = testing.DummyResource()
        parent = testing.DummyResource()
        name = 'name'
        inst = self._makeOne(obj, parent, name)
        self.assertEqual(inst.removed_oids, [])
        
    def test_removed_oids_objectmap_is_not_None(self):
        obj = testing.DummyResource()
        parent = testing.DummyResource()
        objectmap = testing.DummyResource()
        objectmap.pathlookup = lambda *arg: [1]
        parent.__objectmap__ = objectmap
        name = 'name'
        inst = self._makeOne(obj, parent, name)
        self.assertEqual(inst.removed_oids, [1])

class Test_add_content_subscriber(unittest.TestCase):
    def _callFUT(self, config, subscriber, iface=None, **predicates):
        from . import add_content_subscriber
        return add_content_subscriber(config, subscriber, iface=iface,
                                      **predicates)

    def test_register_wrapper(self):
        class IFoo(Interface): pass
        class IBar(Interface): pass
        def foo(event):
            return 'abc'
        config = DummyConfigurator()
        self._callFUT(config, foo, [IFoo, IBar])
        subscriber = config.subscribed[0]
        wrapper = subscriber['wrapped']
        self.assertEqual(wrapper.wrapped, foo)
        event = Dummy()
        self.assertEqual(wrapper(event, None, None), 'abc')
        self.assertEqual(event.registry, config.registry)

class Test_ContentTypePredicate(unittest.TestCase):
    def _makeOne(self, val, config):
        from . import _ContentTypePredicate
        return _ContentTypePredicate(val, config)

    def _makeConfig(self, result):
        config = Dummy()
        config.registry = Dummy()
        config.registry.content = Dummy()
        config.registry.content.istype = lambda *x: result
        return config
    
    def test___call___true(self):
        config = self._makeConfig(True)
        inst = self._makeOne('abc', config)
        event = Dummy()
        event.object = Dummy()
        result = inst(event)
        self.assertTrue(result)

    def test___call___false(self):
        config = self._makeConfig(False)
        inst = self._makeOne('abc', config)
        event = Dummy()
        event.object = Dummy()
        result = inst(event)
        self.assertFalse(result)
        
    def test_text(self):
        config = self._makeConfig(True)
        inst = self._makeOne('abc', config)
        self.assertEqual(inst.text(), 'content_type = abc')

    def test_phash(self):
        config = self._makeConfig(True)
        inst = self._makeOne('abc', config)
        self.assertEqual(inst.phash(), 'content_type = abc')

class Dummy:
    pass
        
registry = Dummy()
class DummyConfigurator(object):
    def __init__(self):
        self.subscribed = []
        self.registry = registry

    def add_content_subscriber(self, wrapped, ifaces, **predicates):
        self.subscribed.append(
            {'wrapped':wrapped, 'ifaces':ifaces, 'predicates':predicates}
            )

    add_subscriber = add_content_subscriber

class DummyRegistry(object):
    pass
        
class DummyVenusian(object):
    def __init__(self):
        self.attached = []

    def attach(self, wrapped, fn, category=None):
        self.attached.append((wrapped, fn, category))

