import re
import unittest
from pyramid import testing
import BTrees

from zope.interface import (
    implementer,
    alsoProvides,
    )

from hypatia.interfaces import IIndex

from ..._compat import u
_BLANK = u('')
_A = u('a')
_B = u('b')

def _makeSite(**kw):
    from ...interfaces import IFolder
    site = testing.DummyResource(__provides__=kw.pop('__provides__', None))
    alsoProvides(site, IFolder)
    objectmap = kw.pop('objectmap', None)
    if objectmap is not None:
        site.__objectmap__ = objectmap
    for k, v in kw.items():
        site[k] = v
        v.__is_service__ = True
    return site

class TestCatalog(unittest.TestCase):
    family = BTrees.family64
    
    def setUp(self):
        self.config = testing.setUp()
        from zope.deprecation import __show__
        __show__.off()

    def tearDown(self):
        testing.tearDown()
        from zope.deprecation import __show__
        __show__.on()

    def _getTargetClass(self):
        from .. import Catalog
        return Catalog
        
    def _makeOne(self, *arg, **kw):
        cls = self._getTargetClass()
        inst = cls(*arg, **kw)
        inst.__name__ = 'catalog'
        return inst

    def test___sdi_addable__True(self):
        inst = self._makeOne()
        intr = {'meta':{'is_index':True}}
        self.assertTrue(inst.__sdi_addable__(None, intr))

    def test___sdi_addable__False(self):
        inst = self._makeOne()
        intr = {'meta':{}}
        self.assertFalse(inst.__sdi_addable__(None, intr))

    def test_klass_provides_ICatalog(self):
        klass = self._getTargetClass()
        from zope.interface.verify import verifyClass
        from ...interfaces import ICatalog
        verifyClass(ICatalog, klass)
        
    def test_inst_provides_ICatalog(self):
        from zope.interface.verify import verifyObject
        from ...interfaces import ICatalog
        inst = self._makeOne()
        verifyObject(ICatalog, inst)

    def test_flush(self):
        inst = self._makeOne()
        idx = DummyIndex()
        inst['name'] = idx
        inst.flush()
        self.assertEqual(idx.flushed, True)

    def test_reset(self):
        catalog = self._makeOne()
        idx = DummyIndex()
        catalog['name'] = idx
        catalog.reset()
        self.assertEqual(idx.cleared, True)
        
    def test_reset_objectids(self):
        inst = self._makeOne()
        inst.objectids.insert(1)
        inst.reset()
        self.assertEqual(list(inst.objectids), [])

    def test_ctor_defaults(self):
        catalog = self._makeOne()
        self.assertTrue(catalog.family is self.family)

    def test_ctor_explicit_family(self):
        catalog = self._makeOne(family=BTrees.family32)
        self.assertTrue(catalog.family is BTrees.family32)

    def test_index_resource_indexes(self):
        catalog = self._makeOne()
        idx = DummyIndex()
        catalog['name'] = idx
        catalog.index_resource('value', 1)
        self.assertEqual(idx.oid, 1)
        self.assertEqual(idx.resource, 'value')

    def test_index_resource_objectids(self):
        inst = self._makeOne()
        inst.index_resource(object(), 1)
        self.assertEqual(list(inst.objectids), [1])

    def test_index_resource_nonint_docid(self):
        catalog = self._makeOne()
        idx = DummyIndex()
        catalog['name'] = idx
        self.assertRaises(TypeError, catalog.index_resource, 'value', 'abc')

    def test_index_resource_oid_is_None(self):
        resource = testing.DummyResource()
        resource.__oid__ = 1
        catalog = self._makeOne()
        idx = DummyIndex()
        catalog['name'] = idx
        catalog.index_resource(resource)
        self.assertEqual(idx.oid, 1)
        self.assertEqual(idx.resource, resource)

    def test_index_doc(self):
        catalog = self._makeOne()
        idx = DummyIndex()
        catalog['name'] = idx
        catalog.index_doc(1, 'value')
        self.assertEqual(idx.oid, 1)
        self.assertEqual(idx.resource, 'value')

    def test_unindex_resource_indexes(self):
        catalog = self._makeOne()
        idx = DummyIndex()
        catalog['name'] = idx
        catalog.unindex_resource(1)
        self.assertEqual(idx.unindexed, 1)
        
    def test_unindex_resource_objectids_exists(self):
        inst = self._makeOne()
        inst.objectids.insert(1)
        inst.unindex_resource(1)
        self.assertEqual(list(inst.objectids), [])

    def test_unindex_resource_objectids_notexists(self):
        inst = self._makeOne()
        inst.unindex_resource(1)
        self.assertEqual(list(inst.objectids), [])

    def test_index_resource_or_oid_is_resource_without_oid(self):
        resource = testing.DummyResource()
        catalog = self._makeOne()
        self.assertRaises(ValueError, catalog.unindex_resource, resource)

    def test_index_resource_or_oid_is_noninteger(self):
        catalog = self._makeOne()
        self.assertRaises(ValueError, catalog.unindex_resource, 'foo')

    def test_unindex_doc(self):
        inst = self._makeOne()
        inst.objectids.insert(1)
        inst.unindex_doc(1)
        self.assertEqual(list(inst.objectids), [])

    def test_reindex_resource_indexes(self):
        catalog = self._makeOne()
        idx = DummyIndex()
        catalog['name'] = idx
        catalog.reindex_resource('value', 1)
        self.assertEqual(idx.reindexed_oid, 1)
        self.assertEqual(idx.reindexed_resource, 'value')

    def test_reindex_resource_objectids_exists(self):
        inst = self._makeOne()
        inst.objectids.insert(1)
        inst.reindex_resource(object(), 1)
        self.assertEqual(list(inst.objectids), [1])
        
    def test_reindex_resource_objectids_notexists(self):
        inst = self._makeOne()
        inst.reindex_resource(object(), 1)
        self.assertEqual(list(inst.objectids), [1])
        
    def test_reindex_resource_oid_is_None(self):
        resource = testing.DummyResource()
        resource.__oid__ = 1
        catalog = self._makeOne()
        idx = DummyIndex()
        catalog['name'] = idx
        catalog.reindex_resource(resource)
        self.assertEqual(idx.reindexed_oid, 1)
        self.assertEqual(idx.reindexed_resource, resource)

    def test_reindex_doc(self):
        catalog = self._makeOne()
        idx = DummyIndex()
        catalog['name'] = idx
        catalog.reindex_doc(1, 'value')
        self.assertEqual(idx.reindexed_oid, 1)
        self.assertEqual(idx.reindexed_resource, 'value')

    def test_reindex(self):
        a = testing.DummyModel()
        L = []
        transaction = DummyTransaction()
        inst = self._makeOne()
        inst.transaction = transaction
        objectmap = DummyObjectMap({1:[a, (_BLANK, _A)]})
        site = _makeSite(catalog=inst, objectmap=objectmap)
        site['a'] = a
        inst.objectids = [1]
        def reindex_resource(resource, oid=None, action_mode=None):
            L.append((oid, resource))
        inst.reindex_resource = reindex_resource
        inst.flush = lambda *arg, **kw: True
        out = []
        inst.reindex(output=out.append)
        self.assertEqual(len(L), 1)
        self.assertEqual(L[0][0], 1)
        self.assertEqual(L[0][1], a)
        self.assertEqual(out,
                          ["catalog reindexing /a",
                          '*** committing ***'])
        self.assertEqual(transaction.committed, 1)

    def test_reindex_with_missing_path(self):
        a = testing.DummyModel()
        L = []
        transaction = DummyTransaction()
        objectmap = DummyObjectMap(
            {1: [a, (_BLANK, _A)], 2:[None, (_BLANK, _B)]}
            )
        inst = self._makeOne()
        inst.transaction = transaction
        site = _makeSite(catalog=inst, objectmap=objectmap)
        site['a'] = a
        inst.objectids = [1, 2]
        def reindex_resource(resource, oid=None, action_mode=None):
            L.append((oid, resource))
        inst.reindex_resource = reindex_resource
        inst.flush = lambda *arg, **kw: True
        out = []
        inst.reindex(output=out.append)
        self.assertEqual(L[0][0], 1)
        self.assertEqual(L[0][1], a)
        self.assertEqual(out,
                          ["catalog reindexing /a",
                          "error: object at path /b not found",
                          '*** committing ***'])
        self.assertEqual(transaction.committed, 1)

    def test_reindex_with_missing_objectid(self):
        a = testing.DummyModel()
        L = []
        transaction = DummyTransaction()
        objectmap = DummyObjectMap()
        inst = self._makeOne()
        inst.transaction = transaction
        inst.flush = lambda *arg, **kw: True
        site = _makeSite(catalog=inst, objectmap=objectmap)
        site['a'] = a
        inst.objectids = [1]
        out = []
        inst.reindex(output=out.append)
        self.assertEqual(L, [])
        self.assertEqual(out,
                          ["error: no path for objectid 1 in object map",
                          '*** committing ***'])
        self.assertEqual(transaction.committed, 1)
        
        
    def test_reindex_pathre(self):
        a = testing.DummyModel()
        b = testing.DummyModel()
        L = []
        objectmap = DummyObjectMap({1: [a, (_BLANK, _A)],
                                    2: [b, (_BLANK, _B)]})
        transaction = DummyTransaction()
        inst = self._makeOne()
        inst.transaction = transaction
        inst.flush = lambda *arg, **kw: True
        site = _makeSite(catalog=inst, objectmap=objectmap)
        site['a'] = a
        site['b'] = b
        inst.objectids = [1, 2]
        def reindex_resource(resource, oid=None, action_mode=None):
            L.append((oid, resource))
        inst.reindex_resource = reindex_resource
        out = []
        inst.reindex(
            path_re=re.compile('/a'), 
            output=out.append
            )
        self.assertEqual(L[0][0], 1)
        self.assertEqual(L[0][1], a)
        self.assertEqual(out,
                          ['catalog reindexing /a',
                          '*** committing ***'])
        self.assertEqual(transaction.committed, 1)

    def test_reindex_dryrun(self):
        a = testing.DummyModel()
        b = testing.DummyModel()
        L = []
        objectmap = DummyObjectMap({1: [a, (_BLANK, _A)], 2: [b, (_BLANK, _B)]})
        transaction = DummyTransaction()
        inst = self._makeOne()
        inst.transaction = transaction
        site = _makeSite(catalog=inst, objectmap=objectmap)
        site['a'] = a
        site['b'] = b
        inst.objectids = [1,2]
        def reindex_resource(resource, oid, action_mode=None):
            L.append((oid, resource))
        inst.reindex_resource = reindex_resource
        inst.flush = lambda *arg, **kw: True
        out = []
        inst.reindex(dry_run=True, output=out.append)
        self.assertEqual(len(L), 2)
        L.sort()
        self.assertEqual(L[0][0], 1)
        self.assertEqual(L[0][1], a)
        self.assertEqual(L[1][0], 2)
        self.assertEqual(L[1][1], b)
        self.assertEqual(out,
                         ['catalog reindexing /a',
                          'catalog reindexing /b',
                          '*** aborting ***'])
        self.assertEqual(transaction.aborted, 1)
        self.assertEqual(transaction.committed, 0)

    def test_reindex_with_indexes(self):
        a = testing.DummyModel()
        L = []
        objectmap = DummyObjectMap({1: [a, (_BLANK, _A)]})
        transaction = DummyTransaction()
        inst = self._makeOne()
        inst.transaction = transaction
        site = _makeSite(catalog=inst, objectmap=objectmap)
        site['a'] = a
        inst.objectids = [1]
        index = DummyIndex()
        inst['index'] = index
        self.config.registry._substanced_indexes = {'index':index}
        def reindex_resource(resource, oid=None, action_mode=None):
            L.append((oid, resource))
        index.reindex_resource = reindex_resource
        inst.flush = lambda *arg, **kw: True
        out = []
        inst.reindex(indexes=('index',),  output=out.append)
        self.assertEqual(out,
                          ["catalog reindexing only indexes ('index',)",
                          'catalog reindexing /a',
                          '*** committing ***'])
        self.assertEqual(transaction.committed, 1)
        self.assertEqual(len(L), 1)
        self.assertEqual(L[0][0], 1)
        self.assertEqual(L[0][1], a)

    def _setup_factory(self, factory=None):
        from substanced.interfaces import ICatalogFactory
        registry = self.config.registry
        if factory is None:
            factory = DummyFactory(True)
        registry.registerUtility(factory, ICatalogFactory, name='catalog')

    def test_update_indexes_nothing_to_do(self):
        self._setup_factory(DummyFactory(False))
        registry = self.config.registry
        out = []
        inst = self._makeOne()
        transaction = DummyTransaction()
        inst.transaction = transaction
        inst.update_indexes(registry=registry,  output=out.append)
        self.assertEqual(
            out,  
            ['catalog update_indexes: no indexes added or removed'],
            )
        self.assertEqual(transaction.committed, 0)
        self.assertEqual(transaction.aborted, 0)

    def test_update_indexes_replace(self):
        self._setup_factory()
        registry = self.config.registry
        out = []
        inst = self._makeOne()
        transaction = DummyTransaction()
        inst.transaction = transaction
        inst.update_indexes(registry=registry, output=out.append, replace=True)
        self.assertEqual(out, ['*** committing ***'])
        self.assertEqual(transaction.committed, 1)
        self.assertEqual(transaction.aborted, 0)
        self.assertTrue(inst.replaced)

    def test_update_indexes_noreplace(self):
        self._setup_factory()
        registry = self.config.registry
        out = []
        inst = self._makeOne()
        transaction = DummyTransaction()
        inst.transaction = transaction
        inst.update_indexes(registry=registry, output=out.append)
        self.assertEqual(out, ['*** committing ***'])
        self.assertEqual(transaction.committed, 1)
        self.assertEqual(transaction.aborted, 0)
        self.assertTrue(inst.synced)

    def test_update_indexes_dryrun(self):
        self._setup_factory()
        registry = self.config.registry
        out = []
        inst = self._makeOne()
        transaction = DummyTransaction()
        inst.transaction = transaction
        inst.update_indexes(registry=registry, output=out.append, dry_run=True)
        self.assertEqual(out, ['*** aborting ***'])
        self.assertEqual(transaction.committed, 0)
        self.assertEqual(transaction.aborted, 1)

class Test_is_catalogable(unittest.TestCase):
    def setUp(self):
        self.config = testing.setUp()

    def tearDown(self):
        testing.tearDown()

    def _callFUT(self, resource, registry=None):
        from .. import is_catalogable
        return is_catalogable(resource, registry)

    def _registerIndexView(self):
        from zope.interface import Interface
        from substanced.interfaces import IIndexView
        self.config.registry.registerAdapter(True, (Interface,), IIndexView)

    def test_no_registry_passed(self):
        resource = Dummy()
        self._registerIndexView()
        self.assertTrue(self._callFUT(resource))

    def test_true(self):
        resource = Dummy()
        self._registerIndexView()
        registry = self.config.registry
        self.assertTrue(self._callFUT(resource, registry))

    def test_false(self):
        resource = Dummy()
        registry = self.config.registry
        self.assertFalse(self._callFUT(resource, registry))

class Test_add_catalog_factory(unittest.TestCase):
    def setUp(self):
        self.config = testing.setUp()

    def tearDown(self):
        testing.tearDown()
        
    def _callFUT(self, config, name, factory):
        from .. import add_catalog_factory
        return add_catalog_factory(config, name, factory)

    def test_it(self):
        from substanced.interfaces import ICatalogFactory
        from substanced.catalog import Field
        config = DummyConfigurator(registry=self.config.registry)
        class Factory(object):
            index = Field()
        self._callFUT(config, 'name', Factory)
        self.assertEqual(len(config.actions), 1)
        action = config.actions[0]
        self.assertEqual(
            action['discriminator'],
            ('sd-catalog-factory', 'name')
            )
        self.assertEqual(
            action['introspectables'], (config.intr,)
            )
        self.assertEqual(config.intr['name'], 'name')
        self.assertEqual(config.intr['factory'].__class__.__name__,
                         'CatalogFactory')
        callable = action['callable']
        callable()
        self.assertEqual(
            self.config.registry.getUtility(ICatalogFactory, 'name'),
            config.intr['factory']
            )

class Test_add_indexview(unittest.TestCase):
    def setUp(self):
        self.config = testing.setUp()

    def tearDown(self):
        testing.tearDown()
        
    def _callFUT(
        self,
        config,
        view,
        catalog_name,
        index_name,
        context=None,
        attr=None,
        ):
        from .. import add_indexview
        return add_indexview(
            config, view, catalog_name, index_name, context=context, attr=attr
            )

    def test_it_func(self):
        from zope.interface import Interface
        from substanced.interfaces import IIndexView
        config = DummyConfigurator(registry=self.config.registry)
        def view(resource, default): return True
        self._callFUT(config, view, 'catalog', 'index')
        self.assertEqual(len(config.actions), 1)
        action = config.actions[0]
        self.assertEqual(
            action['discriminator'],
            ('sd-index-view', 'catalog', 'index', Interface)
            )
        self.assertEqual(
            action['introspectables'], (config.intr,)
            )
        self.assertEqual(config.intr['catalog_name'], 'catalog')
        self.assertEqual(config.intr['index_name'], 'index')
        self.assertEqual(config.intr['name'], 'catalog|index')
        self.assertEqual(config.intr['callable'], view)
        self.assertEqual(config.intr['attr'], None)
        callable = action['callable']
        callable()
        wrapper = self.config.registry.adapters.lookup(
            (Interface,), IIndexView, name='catalog|index')
        self.assertEqual(config.intr['derived_callable'], wrapper)

    def test_it_cls_with_attr(self):
        from zope.interface import Interface
        from substanced.interfaces import IIndexView
        config = DummyConfigurator(registry=self.config.registry)
        class View(object):
            def amethod(self, default): pass
        self._callFUT(config, View, 'catalog', 'index', attr='amethod')
        self.assertEqual(len(config.actions), 1)
        action = config.actions[0]
        self.assertEqual(
            action['discriminator'],
            ('sd-index-view', 'catalog', 'index', Interface)
            )
        self.assertEqual(
            action['introspectables'], (config.intr,)
            )
        self.assertEqual(config.intr['catalog_name'], 'catalog')
        self.assertEqual(config.intr['index_name'], 'index')
        self.assertEqual(config.intr['name'], 'catalog|index')
        self.assertEqual(config.intr['callable'], View)
        self.assertEqual(config.intr['attr'], 'amethod')
        callable = action['callable']
        callable()
        wrapper = self.config.registry.adapters.lookup(
            (Interface,), IIndexView, name='catalog|index')
        self.assertEqual(config.intr['derived_callable'], wrapper)

class Test_catalog_factory(unittest.TestCase):
    def setUp(self):
        self.config = testing.setUp()

    def tearDown(self):
        testing.tearDown()
        
    def _makeOne(self, name):
        from .. import catalog_factory
        return catalog_factory(name)

    def test_it(self):
        class Foo(object):
            pass
        inst = self._makeOne('catalog')
        venusian = DummyVenusian()
        inst.venusian = venusian
        context = testing.DummyResource()
        context.config = DummyConfigurator(None)
        result = inst(Foo)
        self.assertEqual(result, Foo)
        venusian.callback(context, None, 'abc')
        self.assertEqual(context.config.catalog_factory, ('catalog', Foo))

class Test_CatalogablePredicate(unittest.TestCase):
    def _makeOne(self, val, config):
        from .. import _CatalogablePredicate
        return _CatalogablePredicate(val, config)

    def test_text(self):
        config = Dummy()
        config.registry = Dummy()
        inst = self._makeOne(True, config)
        self.assertEqual(inst.text(), 'catalogable = True')

    def test_phash(self):
        config = Dummy()
        config.registry = Dummy()
        inst = self._makeOne(True, config)
        self.assertEqual(inst.phash(), 'catalogable = True')

    def test__call__(self):
        config = Dummy()
        config.registry = Dummy()
        inst = self._makeOne(True, config)
        def is_catalogable(context, registry):
            self.assertEqual(context, None)
            self.assertEqual(registry, config.registry)
            return True
        inst.is_catalogable = is_catalogable
        self.assertEqual(inst(None, None), True)

class Test_catalog_buttons(unittest.TestCase):
    def setUp(self):
        testing.setUp()

    def tearDown(self):
        testing.tearDown()

    def test_it(self):
        from .. import catalog_buttons
        context = testing.DummyResource()
        request = testing.DummyRequest()
        default_buttons = [1]
        buttons = catalog_buttons(context, request, default_buttons)
        self.assertEqual(buttons,
                         [
                             {'buttons':
                              [{'text': 'Reindex',
                                'class': 'btn-primary btn-sdi-sel',
                                'id': 'reindex',
                                'value': 'reindex',
                                'name': 'form.reindex'}],
                              'type': 'single'},
                             1])

class Test_IndexViewMapper(unittest.TestCase):
    def _makeOne(self, attr=None):
        from .. import _IndexViewMapper
        return _IndexViewMapper(attr=attr)

    def test_call_class(self):
        class Foo(object):
            def __init__(self, resource):
                self.resource = resource

            def __call__(self, default):
                return self.resource
        inst = self._makeOne()
        view = inst(Foo)
        result = view('123', None)
        self.assertEqual(result, '123')

    def test_call_class_with_attr(self):
        class Foo(object):
            def __init__(self, resource):
                self.resource = resource

            def meth(self, default):
                return self.resource
        inst = self._makeOne(attr='meth')
        view = inst(Foo)
        result = view('123', None)
        self.assertEqual(result, '123')

    def test_call_function(self):
        def foo(resource, default):
            return resource
        inst = self._makeOne()
        view = inst(foo)
        result = view('123', None)
        self.assertEqual(result, '123')

    def test_call_function_with_attr(self):
        def foo(): pass
        def bar(resource, default):
            return resource
        foo.bar = bar
        inst = self._makeOne(attr='bar')
        view = inst(foo)
        result = view('123', None)
        self.assertEqual(result, '123')

class TestCatalogsService(unittest.TestCase):
    def _makeOne(self, *arg, **kw):
        from .. import CatalogsService
        inst = CatalogsService(*arg, **kw)
        return inst

    def test_add_catalog_update_indexes_defaults_True(self):
        inst = self._makeOne()
        inst.Catalog = DummyCatalog
        catalog = inst.add_catalog('foo')
        self.assertTrue('foo' in inst)
        self.assertTrue(catalog.updated)
        self.assertEqual(catalog.indexed, [1])

    def test_add_catalog_update_indexes_false(self):
        inst = self._makeOne()
        inst.Catalog = DummyCatalog
        inst.add_catalog('foo', update_indexes=False)
        catalog = inst['foo']
        self.assertFalse(catalog.__sdi_deletable__)
        self.assertEqual(catalog.indexed, [1])

    def test_add_catalog_with_update_indexes(self):
        inst = self._makeOne()
        inst.Catalog = DummyCatalog
        catalog = inst.add_catalog('foo', update_indexes=True)
        self.assertTrue('foo' in inst)
        self.assertTrue(catalog.updated)

    def test___sdi_addable__(self):
        inst = self._makeOne()
        self.assertFalse(inst.__sdi_addable__(None, None))

class Test_indexview(unittest.TestCase):
    def setUp(self):
        testing.setUp()

    def tearDown(self):
        testing.tearDown()

    def _getTargetClass(self):
        from substanced.catalog import indexview
        return indexview

    def _makeOne(self, *arg, **kw):
        return self._getTargetClass()(*arg, **kw)

    def test_create_defaults(self):
        decorator = self._makeOne()
        self.assertEqual(decorator.settings, {})

    def test_create_nondefaults(self):
        decorator = self._makeOne(
            catalog_name=None, index_name='fred'
            )
        self.assertEqual(decorator.settings['catalog_name'], None)
        self.assertEqual(decorator.settings['index_name'], 'fred')

    def test_call_as_method(self):
        decorator = self._makeOne(catalog_name='fred', context='context')
        venusian = DummyVenusian()
        decorator.venusian = venusian
        decorator.venusian.info.scope = 'class'
        def foo(self): pass
        def bar(self): pass
        class foo(object):
            foomethod = decorator(foo)
            barmethod = decorator(bar)
        config = call_venusian(venusian)
        settings = config.settings
        self.assertEqual(len(settings), 2)
        self.assertEqual(settings[0]['attr'], 'foo')
        self.assertEqual(settings[0]['index_name'], 'foo')
        self.assertEqual(settings[0]['catalog_name'], 'fred')
        self.assertEqual(settings[0]['context'], 'context')
        self.assertEqual(settings[1]['attr'], 'bar')
        self.assertEqual(settings[1]['catalog_name'], 'fred')
        self.assertEqual(settings[1]['index_name'], 'bar')
        self.assertEqual(settings[1]['context'], 'context')

    def test_call_as_method_with_indexname(self):
        decorator1 = self._makeOne(catalog_name='fred', context='context',
                                   index_name='abc')
        decorator2 = self._makeOne(catalog_name='fred', context='context',
                                   index_name='def')
        venusian = DummyVenusian()
        decorator1.venusian = venusian
        decorator1.venusian.info.scope = 'class'
        decorator2.venusian = venusian
        decorator2.venusian.info.scope = 'class'
        def foo(self): pass
        def bar(self): pass
        class foo(object):
            foomethod = decorator1(foo)
            barmethod = decorator2(bar)
        config = call_venusian(venusian)
        settings = config.settings
        self.assertEqual(len(settings), 2)
        self.assertEqual(settings[0]['attr'], 'foo')
        self.assertEqual(settings[0]['index_name'], 'abc')
        self.assertEqual(settings[0]['catalog_name'], 'fred')
        self.assertEqual(settings[0]['context'], 'context')
        self.assertEqual(settings[1]['attr'], 'bar')
        self.assertEqual(settings[1]['catalog_name'], 'fred')
        self.assertEqual(settings[1]['index_name'], 'def')
        self.assertEqual(settings[1]['context'], 'context')
        
    def test_call_withdepth(self):
        decorator = self._makeOne(_depth=1)
        venusian = DummyVenusian()
        decorator.venusian = venusian
        def bar(self): pass
        class foo(object):
            foomethod = decorator(bar)
        self.assertEqual(venusian.depth, 2)

        
class Test_indexview_defaults(unittest.TestCase):
    def test_it(self):
        from substanced.catalog import indexview_defaults
        @indexview_defaults(route_name='abc', renderer='def')
        class Foo(object): pass
        self.assertEqual(Foo.__view_defaults__['route_name'],'abc')
        self.assertEqual(Foo.__view_defaults__['renderer'],'def')

    def test_it_inheritance_not_overridden(self):
        from substanced.catalog import indexview_defaults
        @indexview_defaults(route_name='abc', renderer='def')
        class Foo(object): pass
        class Bar(Foo): pass
        self.assertEqual(Bar.__view_defaults__['route_name'],'abc')
        self.assertEqual(Bar.__view_defaults__['renderer'],'def')

    def test_it_inheritance_overriden(self):
        from substanced.catalog import indexview_defaults
        @indexview_defaults(route_name='abc', renderer='def')
        class Foo(object): pass
        @indexview_defaults(route_name='ghi')
        class Bar(Foo): pass
        self.assertEqual(Bar.__view_defaults__['route_name'],'ghi')
        self.assertFalse('renderer' in Bar.__view_defaults__)

    def test_it_inheritance_overriden_empty(self):
        from substanced.catalog import indexview_defaults
        @indexview_defaults(route_name='abc', renderer='def')
        class Foo(object): pass
        @indexview_defaults()
        class Bar(Foo): pass
        self.assertEqual(Bar.__view_defaults__, {})
        
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

    def with_package(self, package):
        return self

    def introspectable(self, category, discriminator, name, single):
        return self.intr

    def add_catalog_factory(self, name, cls, **extra):
        self.catalog_factory = (name, cls)

    def maybe_dotted(self, view):
        return view

class DummyObjectMap(object):
    def __init__(self, objectid_to=None): 
        if objectid_to is None: objectid_to = {}
        self.objectid_to = objectid_to

    def path_for(self, objectid):
        data = self.objectid_to.get(objectid)
        if data is None: return
        return data[1]

    def object_for(self, objectid):
        data = self.objectid_to.get(objectid)
        if data is None:
            return
        return data[0]

    def add(self, node, path_tuple, duplicating=False, moving=False):
        pass

class DummyCatalog(dict):
    __oid__ = 1
    def __init__(self):
        self.indexed = []
        
    def update_indexes(self, *arg, **kw):
        self.updated = True

    def index_resource(self, resource, oid=None, action_mode=None):
        self.indexed.append(oid)

class DummyTransaction(object):
    def __init__(self):
        self.committed = 0
        self.aborted = 0
        
    def commit(self):
        self.committed += 1

    def abort(self):
        self.aborted += 1
        

@implementer(IIndex)
class DummyIndex(object):

    resource = None
    oid = None
    action_mode = None
    limit = None
    sort_type = None

    def __init__(self, *arg, **kw):
        self.arg = arg
        self.kw = kw

    def flush(self, all):
        self.flushed = all

    def index_resource(self, resource, oid=None, action_mode=None):
        self.resource = resource
        self.oid = oid
        self.action_mode = action_mode

    def unindex_resource(self, oid, action_mode=None):
        self.unindexed = oid

    def reindex_resource(self, resource, oid=None, action_mode=None):
        self.reindexed_oid = oid
        self.reindexed_resource = resource

    def reset(self):
        self.cleared = True

    def apply_intersect(self, query, docids): # pragma: no cover
        if docids is None:
            return self.arg[0]
        L = []
        for docid in self.arg[0]:
            if docid in docids:
                L.append(docid)
        return L

class Dummy(object):
    pass

class DummyFactory(object):
    def __init__(self, result):
        self.result = result
        
    def replace(self, catalog, **kw):
        catalog.replaced = True
        return self.result

    def sync(self, catalog, **kw):
        catalog.synced = True
        return self.result

class DummyVenusianInfo(object):
    scope = None
    codeinfo = None
    module = None
    def __init__(self, **kw):
        self.__dict__.update(kw)
    
class DummyVenusian(object):
    def __init__(self, info=None):
        if info is None:
            info = DummyVenusianInfo()
        self.info = info
        self.attachments = []
        
    def attach(self, wrapped, callback, category, depth=1):
        self.attachments.append((wrapped, callback, category))
        self.wrapped = wrapped
        self.callback = callback
        self.category = category
        self.depth = depth
        return self.info

class DummyRegistry(object):
    pass

class DummyConfig(object):
    def __init__(self):
        self.settings = []
        self.registry = DummyRegistry()

    def add_indexview(self, ob, **kw):
        self.settings.append(kw)

    def with_package(self, pkg):
        self.pkg = pkg
        return self
    
class DummyVenusianContext(object):
    def __init__(self):
        self.config = DummyConfig()
    
def call_venusian(venusian, context=None):
    if context is None:
        context = DummyVenusianContext()
    for wrapped, callback, category in venusian.attachments:
        callback(context, None, None)
    return context.config
    
