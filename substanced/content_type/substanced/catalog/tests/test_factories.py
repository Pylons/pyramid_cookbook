import unittest
from pyramid import testing

class TestIndexFactory(unittest.TestCase):
    def _makeOne(self, **kw):
        from ..factories import IndexFactory
        inst = IndexFactory(**kw)
        def index_type(discriminator, **kw):
            return inst.idx
        inst.index_type = index_type
        inst.idx = testing.DummyResource()
        return inst

    def test_ctor(self):
        inst = self._makeOne(a=1)
        self.assertEqual(inst.kw, {'a':1})

    def test_call_and_hash(self):
        inst = self._makeOne(a=1)
        index = inst('catalog', 'index')
        self.assertEqual(index, inst.idx)
        self.assertEqual(index.__factory_hash__, hash(inst))

    def test_hashvalues_family32(self):
        import BTrees
        inst = self._makeOne(a=1, family=BTrees.family32)
        values = inst.hashvalues()
        self.assertEqual(
            values,
            {'a':1,
             'family':'family32',
             'class':'substanced.catalog.factories.IndexFactory'}
            )

    def test_hashvalues_family64(self):
        import BTrees
        inst = self._makeOne(a=1, family=BTrees.family64)
        values = inst.hashvalues()
        self.assertEqual(
            values,
            {'a':1,
             'family':'family64',
             'class':'substanced.catalog.factories.IndexFactory'}
            )

    def test_hashvalues_family_unknown(self):
        inst = self._makeOne(a=1, family=True)
        self.assertRaises(ValueError, inst.hashvalues)

    def test_is_stale(self):
        inst = self._makeOne(a=1)
        index = testing.DummyResource()
        index.__factory_hash__ = None
        self.assertTrue(inst.is_stale(index))

    def test_is_not_stale(self):
        inst = self._makeOne(a=1)
        index = testing.DummyResource()
        index.__factory_hash__ = hash(inst)
        self.assertFalse(inst.is_stale(index))

class TestText(unittest.TestCase):
    def _makeOne(self, **kw):
        from ..factories import Text
        return Text(**kw)

    def test_call(self):
        inst = self._makeOne()
        result = inst('catalog', 'index')
        self.assertEqual(result.__class__.__name__, 'TextIndex')
        self.assertEqual(
            result.discriminator.__class__.__name__,
            'IndexViewDiscriminator'
            )
        self.assertTrue(hasattr(result, '__factory_hash__'))

    def test_hashvalues(self):
        inst = self._makeOne()
        result = inst.hashvalues()
        self.assertEqual(
            result,
            {'class': 'substanced.catalog.factories.Text'}
            )

    def test_hashvalues_with_lexicon_and_index(self):
        dummy = testing.DummyResource()
        inst = self._makeOne(lexicon=dummy, index=dummy)
        result = inst.hashvalues()
        self.assertEqual(
            result,
            {'index': 'DummyResource',
             'lexicon': 'DummyResource',
             'class': 'substanced.catalog.factories.Text'}
            )

        
class TestField(unittest.TestCase):
    def _makeOne(self, **kw):
        from ..factories import Field
        return Field(**kw)

    def test_call(self):
        inst = self._makeOne()
        result = inst('catalog', 'index')
        self.assertEqual(result.__class__.__name__, 'FieldIndex')
        self.assertEqual(
            result.discriminator.__class__.__name__,
            'IndexViewDiscriminator'
            )
        self.assertTrue(hasattr(result, '__factory_hash__'))

    def test_hashvalues(self):
        inst = self._makeOne()
        result = inst.hashvalues()
        self.assertEqual(
            result,
            {'class': 'substanced.catalog.factories.Field'}
            )

class TestKeyword(unittest.TestCase):
    def _makeOne(self, **kw):
        from ..factories import Keyword
        return Keyword(**kw)

    def test_call(self):
        inst = self._makeOne()
        result = inst('catalog', 'index')
        self.assertEqual(result.__class__.__name__, 'KeywordIndex')
        self.assertEqual(
            result.discriminator.__class__.__name__,
            'IndexViewDiscriminator'
            )
        self.assertTrue(hasattr(result, '__factory_hash__'))

    def test_hashvalues(self):
        inst = self._makeOne()
        result = inst.hashvalues()
        self.assertEqual(
            result,
            {'class': 'substanced.catalog.factories.Keyword'}
            )

class TestFacet(unittest.TestCase):
    def _makeOne(self, **kw):
        from ..factories import Facet
        return Facet(**kw)

    def test_call(self):
        inst = self._makeOne(facets=[(1,2)])
        result = inst('catalog', 'index')
        self.assertEqual(result.__class__.__name__, 'FacetIndex')
        self.assertEqual(
            result.discriminator.__class__.__name__,
            'IndexViewDiscriminator'
            )
        self.assertTrue(hasattr(result, '__factory_hash__'))

    def test_hashvalues(self):
        inst = self._makeOne(facets=[(1,2)])
        result = inst.hashvalues()
        self.assertEqual(
            result,
            {'class': 'substanced.catalog.factories.Facet',
             'facets':((1,2),)}
            )

class TestPath(unittest.TestCase):
    def _makeOne(self, **kw):
        from ..factories import Path
        return Path(**kw)

    def test_call(self):
        inst = self._makeOne()
        result = inst('catalog', 'index')
        self.assertEqual(result.__class__.__name__, 'PathIndex')
        self.assertTrue(hasattr(result, '__factory_hash__'))

    def test_hashvalues(self):
        inst = self._makeOne()
        result = inst.hashvalues()
        self.assertEqual(
            result,
            {'class': 'substanced.catalog.factories.Path'}
            )

class TestAllowed(unittest.TestCase):
    def _makeOne(self, **kw):
        from ..factories import Allowed
        return Allowed(**kw)

    def test_call(self):
        inst = self._makeOne(permissions=['a',])
        result = inst('catalog', 'index')
        self.assertEqual(result.__class__.__name__, 'AllowedIndex')
        self.assertTrue(hasattr(result, '__factory_hash__'))
        self.assertEqual(result.discriminator.permissions, set(['a']))

    def test_hashvalues_noniter_permissions(self):
        inst = self._makeOne(permissions='a')
        result = inst.hashvalues()
        self.assertEqual(
            result,
            {'class': 'substanced.catalog.factories.Allowed',
             'permissions': ('a',)}
            )
        
    def test_hashvalues_iter_permissions(self):
        inst = self._makeOne(permissions=['b', 'a'])
        result = inst.hashvalues()
        self.assertEqual(
            result,
            {'class': 'substanced.catalog.factories.Allowed',
             'permissions': ('a','b')}
            )
        
class TestCatalogFactory(unittest.TestCase):
    def _makeOne(self, name, index_factories):
        from ..factories import CatalogFactory
        return CatalogFactory(name, index_factories)

    def test_ctor(self):
        inst = self._makeOne('name', 'factories')
        self.assertEqual(inst.name, 'name')
        self.assertEqual(inst.index_factories, 'factories')

    def test_replace(self):
        L = []
        output = L.append
        factory = DummyIndexFactory()
        index_factories = {'a':factory}
        inst = self._makeOne('name', index_factories)
        catalog = DummyCatalog()
        index = testing.DummyResource()
        catalog['a'] = index
        result = inst.replace(catalog, output=output)
        self.assertTrue(result)
        self.assertEqual(factory.catalog_name, 'name')
        self.assertFalse(catalog.reindexed)
        self.assertEqual(catalog['a'], factory)
        self.assertTrue(L)

    def test_replace_add(self):
        L = []
        output = L.append
        factory = DummyIndexFactory()
        index_factories = {'a':factory}
        inst = self._makeOne('name', index_factories)
        catalog = DummyCatalog()
        result = inst.replace(catalog, output=output)
        self.assertTrue(result)
        self.assertEqual(factory.catalog_name, 'name')
        self.assertFalse(catalog.reindexed)
        self.assertEqual(catalog['a'], factory)
        self.assertTrue(L)

    def test_replace_reindex_true(self):
        L = []
        output = L.append
        factory = DummyIndexFactory()
        index_factories = {'a':factory}
        inst = self._makeOne('name', index_factories)
        catalog = DummyCatalog()
        result = inst.replace(catalog, output=output, reindex=True)
        self.assertTrue(result)
        self.assertEqual(factory.catalog_name, 'name')
        self.assertEqual(catalog.reindexed['indexes'], set(['a']))
        self.assertEqual(catalog['a'], factory)
        self.assertTrue(L)

    def test_replace_remove_stale(self):
        L = []
        output = L.append
        index_factories = {}
        inst = self._makeOne('name', index_factories)
        index = testing.DummyResource()
        catalog = DummyCatalog()
        catalog['index'] = index
        result = inst.replace(catalog, output=output)
        self.assertTrue(result)
        self.assertFalse('index' in catalog)
        self.assertTrue(L)

    def test_sync_replace_stale(self):
        L = []
        output = L.append
        factory = DummyIndexFactory(True)
        index_factories = {'a':factory}
        inst = self._makeOne('name', index_factories)
        catalog = DummyCatalog()
        index = testing.DummyResource()
        catalog['a'] = index
        result = inst.sync(catalog, output=output)
        self.assertTrue(result)
        self.assertEqual(factory.catalog_name, 'name')
        self.assertFalse(catalog.reindexed)
        self.assertEqual(catalog['a'], factory)
        self.assertTrue(L)

    def test_sync_keep_notstale(self):
        L = []
        output = L.append
        factory = DummyIndexFactory(False)
        index_factories = {'a':factory}
        inst = self._makeOne('name', index_factories)
        catalog = DummyCatalog()
        index = testing.DummyResource()
        catalog['a'] = index
        result = inst.sync(catalog, output=output)
        self.assertFalse(result)
        self.assertFalse(catalog.reindexed)
        self.assertEqual(catalog['a'], index)
        self.assertFalse(L)

    def test_sync_add_and_remove_stale(self):
        L = []
        output = L.append
        factory = DummyIndexFactory(False)
        index_factories = {'b':factory}
        inst = self._makeOne('name', index_factories)
        catalog = DummyCatalog()
        index = testing.DummyResource()
        catalog['a'] = index
        result = inst.sync(catalog, output=output)
        self.assertTrue(result)
        self.assertEqual(factory.catalog_name, 'name')
        self.assertFalse(catalog.reindexed)
        self.assertEqual(catalog['b'], factory)
        self.assertFalse('a' in catalog)
        self.assertTrue(L)

    def test_sync_reindex_true(self):
        L = []
        output = L.append
        factory = DummyIndexFactory()
        index_factories = {'a':factory}
        inst = self._makeOne('name', index_factories)
        catalog = DummyCatalog()
        result = inst.sync(catalog, output=output, reindex=True)
        self.assertTrue(result)
        self.assertEqual(factory.catalog_name, 'name')
        self.assertEqual(catalog.reindexed['indexes'], set(['a']))
        self.assertEqual(catalog['a'], factory)
        self.assertTrue(L)

class DummyIndexFactory(object):
    def __init__(self, result=None):
        self.result = result

    def __call__(self, catalog_name, index_name):
        self.catalog_name = catalog_name
        self.index_name = index_name
        return self

    def is_stale(self, index):
        return self.result
        

class DummyCatalog(testing.DummyResource):
    reindexed = False
    __name__ = 'catalog'
    __parent__ = None
    def add(self, name, value, send_events=True):
        self[name] = value

    def replace(self, name, value, send_events=True):
        self[name] = value

    def reindex(self, **kw):
        self.reindexed = kw

    def remove(self, name, send_events=True):
        del self[name]
        
