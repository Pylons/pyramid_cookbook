import unittest
import BTrees

from zope.interface import alsoProvides

from pyramid import testing

def _makeSite(**kw):
    from ...interfaces import IFolder
    site = testing.DummyResource(__provides__=kw.pop('__provides__', None))
    alsoProvides(site, IFolder)
    objectmap = kw.pop('objectmap', None)
    if objectmap is not None:
        site.__objectmap__ = objectmap
    for k, v in kw.items():
        if k == 'catalog':
            catalogs = testing.DummyResource(
                __provides__=IFolder,
                __is_service__=True
                )
            site['catalogs'] = catalogs
            catalogs['system'] = v
    return site

class Test_object_added(unittest.TestCase):
    def _callFUT(self, event):
        from ..subscribers import object_added
        return object_added(event)

    def test_no_catalog(self):
        model = testing.DummyResource()
        event = testing.DummyResource(object=model)
        self._callFUT(event) # doesnt blow up

    def test_catalogable_objects(self):
        from ...interfaces import IFolder
        catalog = DummyCatalog()
        objectmap = DummyObjectMap()
        site = _makeSite(objectmap=objectmap, catalog=catalog)
        model1 = testing.DummyResource(__provides__=(IFolder,))
        model1.__oid__ = 1
        model2 = testing.DummyResource()
        model2.__oid__ = 2
        model1['model2'] = model2
        site['model1'] = model1
        event = DummyEvent(model1, None)
        self._callFUT(event)
        indexed = catalog.indexed
        self.assertEqual(len(indexed), 2)
        self.assertEqual(indexed[0][0], model2)
        self.assertEqual(indexed[0][1], 2)
        self.assertEqual(indexed[1][0], model1)
        self.assertEqual(indexed[1][1], 1)
        
    def test_catalogable_objects_disjoint(self):
        from ...interfaces import IFolder
        catalog = DummyCatalog()
        objectmap = DummyObjectMap()
        site = _makeSite(objectmap=objectmap, catalog=catalog)
        model1 = testing.DummyResource(__provides__=IFolder)
        model2 = testing.DummyResource()
        model2.__oid__ = 1
        model1['model2'] = model2
        site['model1'] = model1
        event = DummyEvent(model1, None)
        self._callFUT(event)
        indexed = catalog.indexed
        self.assertEqual(len(indexed), 1)
        self.assertEqual(indexed[0][0], model2)
        self.assertEqual(indexed[0][1], 1)

    def test_multiple_catalogs(self):
        from ...interfaces import IFolder
        catalog1 = DummyCatalog()
        catalog2 = DummyCatalog()
        objectmap = DummyObjectMap()
        inner_site = _makeSite(catalog=catalog2)
        inner_site.__oid__ = -1
        outer_site = _makeSite(objectmap=objectmap, catalog=catalog1)
        outer_site['inner'] = inner_site
        model1 = testing.DummyResource(__provides__=(IFolder,))
        model1.__oid__ = 1
        model2 = testing.DummyResource()
        model2.__oid__ = 2
        model1['model2'] = model2
        inner_site['model1'] = model1
        event = DummyEvent(model1, None)
        self._callFUT(event)
        for catalog in (catalog1, catalog2):
            indexed = catalog.indexed
            self.assertEqual(len(indexed), 2)
            self.assertEqual(indexed[0][0], model2)
            self.assertEqual(indexed[0][1], 2)
            self.assertEqual(indexed[1][0], model1)
            self.assertEqual(indexed[1][1], 1)

    def test_moving_rename(self):
        from ...interfaces import IFolder
        catalog = DummyCatalog()
        objectmap = DummyObjectMap()
        site = _makeSite(objectmap=objectmap, catalog=catalog)
        model1 = testing.DummyResource(__provides__=(IFolder,))
        model1.__oid__ = 1
        model2 = testing.DummyResource()
        model2.__oid__ = 2
        model1['model2'] = model2
        site['model1'] = model1
        event = DummyEvent(model1, site, moving=site)
        self._callFUT(event)
        reindexed = catalog.reindexed
        self.assertEqual(len(reindexed), 2)
        self.assertEqual(reindexed[0][0], model2)
        self.assertEqual(reindexed[0][1], 2)
        self.assertEqual(reindexed[1][0], model1)
        self.assertEqual(reindexed[1][1], 1)

    def test_moving_not_rename_same_catalogs(self):
        from ...interfaces import IFolder
        catalog = DummyCatalog()
        objectmap = DummyObjectMap()
        site = _makeSite(objectmap=objectmap, catalog=catalog)
        model1 = testing.DummyResource(__provides__=(IFolder,))
        model1.__oid__ = 1
        model2 = testing.DummyResource()
        model2.__oid__ = 2
        model1['model2'] = model2
        site['model1'] = model1
        foo = site['foo'] = testing.DummyResource()
        event = DummyEvent(model1, site, moving=foo)
        self._callFUT(event)
        reindexed = catalog.reindexed
        self.assertEqual(len(reindexed), 2)
        self.assertEqual(reindexed[0][0], model2)
        self.assertEqual(reindexed[0][1], 2)
        self.assertEqual(reindexed[1][0], model1)
        self.assertEqual(reindexed[1][1], 1)
        
    def test_moving_not_rename_different_catalogs(self):
        from ...interfaces import IFolder
        catalog = DummyCatalog()
        catalog2 = DummyCatalog()
        objectmap = DummyObjectMap()
        site = _makeSite(objectmap=objectmap, catalog=catalog)
        site2 = _makeSite(catalog=catalog2)
        model1 = testing.DummyResource(__provides__=(IFolder,))
        model1.__oid__ = 1
        model2 = testing.DummyResource()
        model2.__oid__ = 2
        model1['model2'] = model2
        site['model1'] = model1
        event = DummyEvent(model1, site, moving=site2)
        self._callFUT(event)
        indexed = catalog.indexed
        self.assertEqual(len(indexed), 2)
        self.assertEqual(indexed[0][0], model2)
        self.assertEqual(indexed[0][1], 2)
        self.assertEqual(indexed[1][0], model1)
        self.assertEqual(indexed[1][1], 1)

class Test_object_removed(unittest.TestCase):
    def _callFUT(self, event):
        from ..subscribers import object_removed
        return object_removed(event)

    def test_no_objectmap(self):
        model = testing.DummyResource()
        parent = testing.DummyResource()
        event = DummyEvent(object=model, parent=parent)
        event.removed_oids = None
        self._callFUT(event) # doesnt blow up

    def test_no_catalog(self):
        site = _makeSite()
        event = DummyEvent(None, site)
        self._callFUT(event) # doesnt blow up

    def test_with_removed_oids(self):
        catalog = DummyCatalog()
        catalog.objectids = catalog.family.IF.Set([1,2])
        site = _makeSite(catalog=catalog)
        event = DummyEvent(None, site)
        event.removed_oids = catalog.family.IF.Set([1,2])
        self._callFUT(event)
        self.assertEqual(catalog.unindexed, [1,2])

    def test_with_pathlookup_limited_by_objectids(self):
        catalog = DummyCatalog()
        catalog.objectids = catalog.family.IF.Set([1])
        site = _makeSite(catalog=catalog)
        event = DummyEvent(None, site)
        event.removed_oids = catalog.family.IF.Set([1,2])
        self._callFUT(event)
        self.assertEqual(catalog.unindexed, [1])

    def test_multiple_catalogs(self):
        catalog1 = DummyCatalog()
        catalog1.objectids = catalog1.family.IF.Set([1])
        catalog2 = DummyCatalog()
        catalog2.objectids = catalog2.family.IF.Set([2])
        outer = _makeSite(catalog=catalog1)
        inner = _makeSite(catalog=catalog2)
        inner.__oid__ = -1
        outer['inner'] = inner
        event = DummyEvent(None, inner)
        event.removed_oids = catalog1.family.IF.Set([1,2])
        self._callFUT(event)
        self.assertEqual(catalog1.unindexed, [1])
        self.assertEqual(catalog2.unindexed, [2])

    def test_moving_rename(self):
        catalog = DummyCatalog()
        catalog.objectids = catalog.family.IF.Set([1,2])
        site = _makeSite(catalog=catalog)
        event = DummyEvent(None, site, moving=site)
        event.removed_oids = catalog.family.IF.Set([1,2])
        self._callFUT(event)
        self.assertEqual(catalog.unindexed, [])
        
    def test_moving_not_rename_same_catalogs(self):
        catalog = DummyCatalog()
        catalog.objectids = catalog.family.IF.Set([1,2])
        site = _makeSite(catalog=catalog)
        foo = site['foo'] = testing.DummyResource()
        event = DummyEvent(None, site, moving=foo)
        event.removed_oids = catalog.family.IF.Set([1,2])
        self._callFUT(event)
        self.assertEqual(catalog.unindexed, [])

    def test_moving_not_rename_different_catalogs(self):
        catalog = DummyCatalog()
        catalog.objectids = catalog.family.IF.Set([1,2])
        catalog2 = DummyCatalog()
        site = _makeSite(catalog=catalog)
        site2 = _makeSite(catalog=catalog2)
        event = DummyEvent(None, site, moving=site2)
        event.removed_oids = catalog.family.IF.Set([1,2])
        self._callFUT(event)
        self.assertEqual(catalog.unindexed, [1,2])
        
class Test_object_modified(unittest.TestCase):
    def _callFUT(self, event):
        from ..subscribers import object_modified
        return object_modified(event)

    def test_no_catalog(self):
        objectmap = DummyObjectMap()
        site = _makeSite(objectmap=objectmap)
        model = testing.DummyResource()
        model.__oid__ = 1
        site['model'] = model
        event = DummyEvent(model, site)
        content = DummyContent()
        registry = DummyRegistry(content=content)
        event.registry = registry
        self._callFUT(event) # doesnt blow up
        
    def test_catalogable_object(self):
        objectmap = DummyObjectMap()
        catalog = DummyCatalog()
        site = _makeSite(objectmap=objectmap, catalog=catalog)
        model = testing.DummyResource()
        model.__oid__ = 1
        site['model'] = model
        event = DummyEvent(model, site)
        content = DummyContent()
        registry = DummyRegistry(content=content)
        event.registry = registry
        self._callFUT(event)
        reindexed = catalog.reindexed
        self.assertEqual(len(reindexed), 1)
        self.assertEqual(reindexed[0][0], model)
        self.assertEqual(reindexed[0][1], 1)

    def test_multiple_catalogs(self):
        objectmap = DummyObjectMap()
        catalog1 = DummyCatalog()
        catalog2 = DummyCatalog()
        outer = _makeSite(objectmap=objectmap, catalog=catalog1)
        inner = _makeSite(catalog=catalog2)
        inner.__oid__ = -1
        outer['inner'] = inner
        model = testing.DummyResource()
        model.__oid__ = 1
        inner['model'] = model
        outer['inner'] = inner
        event = DummyEvent(model, None)
        content = DummyContent()
        registry = DummyRegistry(content=content)
        event.registry = registry
        self._callFUT(event)
        for catalog in (catalog1, catalog2):
            reindexed = catalog.reindexed
            self.assertEqual(len(reindexed), 1)
            self.assertEqual(reindexed[0][0], model)
            self.assertEqual(reindexed[0][1], 1)

class Test_acl_modified(unittest.TestCase):
    def _callFUT(self, event):
        from ..subscribers import acl_modified
        return acl_modified(event)

    def test_no_catalogs(self):
        resource = testing.DummyResource()
        event = DummyEvent(resource, None)
        self._callFUT(event) # doesnt blow up

    def test_gardenpath(self):
        from substanced.interfaces import IFolder
        resource = testing.DummyResource(__provides__=IFolder)
        resource.__oid__ = 1
        catalog = DummyCatalog()
        catalog.__name__ = 'catalog'
        catalogs = resource['catalogs'] = testing.DummyResource(
            __provides__=IFolder, __is_service__=True, __name__='catalogs')
        catalogs['catalog'] = catalog
        index = DummyIndex()
        index.__name__ = 'index'
        catalog['index'] = index
        event = DummyEvent(resource, None)
        content = DummyContent()
        registry = DummyRegistry(content=content)
        event.registry = registry
        self._callFUT(event)
        self.assertEqual(index.oid, 1)
        self.assertEqual(index.resource, resource)

class Test_on_startup(unittest.TestCase):
    def setUp(self):
        self.config = testing.setUp()

    def tearDown(self):
        testing.tearDown()

    def _callFUT(self, event):
        from ..subscribers import on_startup
        return on_startup(event)

    def test_autosync_false_from_ini(self):
        registry = self.config.registry
        registry.content = DummyContentRegistry()
        registry.settings['substanced.catalogs.autosync'] = 'false'
        app = testing.DummyResource()
        app.registry = registry
        event = DummyEvent(app, None)
        result = self._callFUT(event)
        self.assertEqual(result, None)

    def test_autosync_false_from_ini_bc(self):
        registry = self.config.registry
        registry.content = DummyContentRegistry()
        registry.settings['substanced.autosync_catalogs'] = 'false'
        app = testing.DummyResource()
        app.registry = registry
        event = DummyEvent(app, None)
        result = self._callFUT(event)
        self.assertEqual(result, None)
        
    def test_autosync_missing_from_ini(self):
        registry = self.config.registry
        registry.content = DummyContentRegistry()
        app = testing.DummyResource()
        app.registry = registry
        event = DummyEvent(app, None)
        result = self._callFUT(event)
        self.assertEqual(result, None)

    def test_autosync_true_from_ini_no_objectmap(self):
        registry = self.config.registry
        registry.content = DummyContentRegistry()
        registry.settings['substanced.catalogs.autosync'] = 'true'
        app = testing.DummyResource()
        app.registry = registry
        root = testing.DummyResource()
        app.root_factory = lambda *arg: root
        event = DummyEvent(app, None)
        result = self._callFUT(event)
        self.assertEqual(result, None)

    def test_autosync_false_from_environ(self):
        import os
        from mock import patch
        with patch.dict(os.environ, {'SUBSTANCED_CATALOGS_AUTOSYNC':'false'}):
            registry = self.config.registry
            registry.content = DummyContentRegistry()
            registry.settings['substanced.catalogs.autosync'] = 'true'
            app = testing.DummyResource()
            app.registry = registry
            event = DummyEvent(app, None)
            result = self._callFUT(event)
            self.assertEqual(result, None)

    def test_autosync_true_from_environ_no_objectmap(self):
        from mock import patch
        import os
        with patch.dict(os.environ, {'SUBSTANCED_CATALOGS_AUTOSYNC':'true'}):
            registry = self.config.registry
            registry.content = DummyContentRegistry()
            registry.settings['substanced.catalogs.autosync'] = 'false'
            app = testing.DummyResource()
            app.registry = registry
            root = testing.DummyResource()
            app.root_factory = lambda *arg: root
            event = DummyEvent(app, None)
            result = self._callFUT(event)
            self.assertEqual(result, None)
        
    def test_autosync_true_no_oids(self):
        registry = self.config.registry
        registry.content = DummyContentRegistry()
        registry.settings['substanced.catalogs.autosync'] = 'true'
        app = testing.DummyResource()
        app.registry = registry
        root = testing.DummyResource()
        root.__objectmap__ = DummyObjectMap([])
        app.root_factory = lambda *arg: root
        event = DummyEvent(app, None)
        result = self._callFUT(event)
        self.assertEqual(result, None)

    def test_autosync_true_with_oids(self):
        registry = self.config.registry
        registry.content = DummyContentRegistry()
        registry.settings['substanced.catalogs.autosync'] = 'true'
        app = testing.DummyResource()
        app.registry = registry
        root = testing.DummyResource()
        catalog = DummyCatalog()
        root.__objectmap__ = DummyObjectMap([1], catalog)
        app.root_factory = lambda *arg: root
        event = DummyEvent(app, None)
        result = self._callFUT(event)
        self.assertEqual(result, None)
        self.assertTrue(catalog.updated)

    def test_autosync_true_with_oids_raises(self):
        from zope.interface.interfaces import ComponentLookupError
        registry = self.config.registry
        registry.content = DummyContentRegistry()
        registry.settings['substanced.catalogs.autosync'] = 'true'
        app = testing.DummyResource()
        app.registry = registry
        root = testing.DummyResource()
        catalog = DummyCatalog(raises=ComponentLookupError)
        root.__objectmap__ = DummyObjectMap([1], catalog)
        app.root_factory = lambda *arg: root
        event = DummyEvent(app, None)
        result = self._callFUT(event)
        self.assertEqual(result, None)
        self.assertFalse(catalog.updated)

class DummyCatalog(dict):
    
    family = BTrees.family64
    updated = False
    
    def __init__(self, result=None, raises=None):
        self.queries = []
        self.indexed = []
        self.unindexed = []
        self.reindexed = []
        self.objectids = self.family.II.TreeSet()
        self.result = result
        self.raises = raises

    def __eq__(self, other):
        return other is self

    def index_resource(self, resource, oid=None):
        self.indexed.append((resource, oid))

    def unindex_resource(self, resource_or_oid):
        self.unindexed.append(resource_or_oid)

    def reindex_resource(self, resource, oid=None):
        self.reindexed.append((resource, oid))

    def update_indexes(self, *arg, **kw):
        if self.raises:
            raise self.raises
        self.updated = True
        return self.result

class DummyObjectMap:
    family = BTrees.family64

    def __init__(self, result=None, object_result=None):
        self.result = result
        self.object_result = object_result

    def get_extent(self, name):
        return self.result

    def object_for(self, oid):
        return self.object_result
    
class DummyEvent(object):
    removed_oids = None
    def __init__(self, object, parent, registry=None, moving=None):
        self.object = object
        self.parent = parent
        self.registry = registry
        self.moving = moving
        
class DummyContent(object):
    def istype(self, obj, whatever):
        return True

class DummyRegistry(object):
    def __init__(self, content):
        self.content = content
        
class DummyIndex(object):
    def __init__(self):
        self.reindexed = []

    def reindex_resource(self, resource, oid=None, action_mode=None):
        self.oid = oid
        self.resource = resource

class DummyContentRegistry(object):
    def __init__(self, result=None):
        self.result = result

    def factory_type_for_content_type(self, content_type):
        return self.result
    
