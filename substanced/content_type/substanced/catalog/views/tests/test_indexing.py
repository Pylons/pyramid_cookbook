import unittest

from pyramid import testing

class TestIndexingView(unittest.TestCase):
    def setUp(self):
        self.config = testing.setUp()

    def tearDown(self):
        testing.tearDown()

    def _makeOne(self, context, request):
        from  ..indexing import IndexingView
        return IndexingView(context, request)

    def _makeCatalogContainer(self):
        from substanced.interfaces import IFolder
        catalogs = testing.DummyResource(
            __provides__=IFolder, __is_service__=True
            )
        return catalogs

    def test_show(self):
        from substanced.interfaces import IFolder
        context = testing.DummyResource(__provides__=IFolder)
        request = testing.DummyRequest()
        context.__oid__ = 1
        catalog = DummyCatalog()
        catalogs = self._makeCatalogContainer()
        catalogs['catalog'] = catalog
        context['catalogs'] = catalogs
        inst = self._makeOne(context, request)
        result = inst.show()
        self.assertEqual(
            result,
            {'catalogs':[(catalog, [{'index':catalog.index, 'value':'repr'}])]}
            )

    def test_reindex(self):
        from substanced.interfaces import IFolder
        context = testing.DummyResource(__provides__=IFolder)
        request = testing.DummyRequest()
        token = request.session.new_csrf_token()
        request.POST['csrf_token'] = token
        request.sdiapi = DummySDIAPI()
        context.__oid__ = 1
        catalog = DummyCatalog()
        catalogs = self._makeCatalogContainer()
        catalogs['catalog'] = catalog
        context['catalogs'] = catalogs
        inst = self._makeOne(context, request)
        result = inst.reindex()
        self.assertEqual(result.__class__.__name__, 'HTTPFound')
        self.assertEqual(catalog.oid, 1)
        self.assertEqual(catalog.content, context)
        self.assertEqual(request.sdiapi.flashed,
                         ('Object reindexed', 'success') )

class DummyIndex(object):
    def document_repr(self, oid, default=None):
        return 'repr'

class DummyCatalog(object):
    __is_service__ = True
    def __init__(self):
        self.index = DummyIndex()

    def values(self):
        return (self.index,)

    def reindex_doc(self, oid, content):
        self.oid = oid
        self.content = content

    def reindex_resource(self, content, oid=None, action_mode=None):
        self.action_mode = action_mode
        return self.reindex_doc(oid, content)

class DummySDIAPI(object):
    def mgmt_url(self, *arg, **kw):
        return 'http://mgmt_url'

    def flash_with_undo(self, message, status):
        self.flashed = (message, status)
        
