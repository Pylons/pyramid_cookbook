import unittest
from pyramid import testing

class TestManageCatalog(unittest.TestCase):
    def _makeOne(self, context, request):
        from ..catalog import ManageCatalog
        return ManageCatalog(context, request)

    def test_view(self):
        context = DummyCatalog()
        request = testing.DummyRequest()
        request.sdiapi = DummySDIAPI()
        inst = self._makeOne(context, request)
        result = inst.view()
        self.assertEqual(result['cataloglen'], 0)

    def test_reindex(self):
        context = DummyCatalog()
        request = testing.DummyRequest()
        request.sdiapi = DummySDIAPI()
        inst = self._makeOne(context, request)
        result = inst.reindex()
        self.assertEqual(result.location, '/mgmt_path')
        self.assertEqual(context.reindexed, None)

    def test_update(self):
        context = DummyCatalog()
        request = testing.DummyRequest()
        request.sdiapi = DummySDIAPI()
        inst = self._makeOne(context, request)
        result = inst.update()
        self.assertEqual(result.location, '/mgmt_path')
        self.assertEqual(context.updated, True)

class TestManageIndex(unittest.TestCase):
    def _makeOne(self, context, request):
        from ..catalog import ManageIndex
        return ManageIndex(context, request)

    def test_view(self):
        context = DummyIndex()
        request = testing.DummyRequest()
        request.sdiapi = DummySDIAPI()
        inst = self._makeOne(context, request)
        result = inst.view()
        self.assertEqual(result['indexed'], 1)
        self.assertEqual(result['not_indexed'], 1)
        self.assertEqual(result['index_name'], 'name')
        self.assertEqual(result['index_type'], 'DummyIndex')

    def test_reindex_parent_not_icatalog(self):
        context = DummyIndex(False)
        request = testing.DummyRequest()
        request.sdiapi = DummySDIAPI()
        inst = self._makeOne(context, request)
        result = inst.reindex()
        self.assertEqual(result.location, '/mgmt_path')
        self.assertEqual(
            request.session['_f_error'],
            ['Cannot reindex an index unless it is contained in a catalog'])

    def test_reindex_parent_is_icatalog(self):
        from zope.interface import alsoProvides
        from substanced.interfaces import ICatalog
        catalog = DummyCatalog()
        alsoProvides(catalog, ICatalog)
        context = DummyIndex(catalog)
        request = testing.DummyRequest()
        request.sdiapi = DummySDIAPI()
        inst = self._makeOne(context, request)
        result = inst.reindex()
        self.assertEqual(result.location, '/mgmt_path')
        self.assertEqual(catalog.indexes, ['name'])
        self.assertEqual(
            request.session['_f_success'], ['Index "name" reindexed'])

class TestSearchCatalogView(unittest.TestCase):
    def _makeOne(self, context, request):
        from ..catalog import SearchCatalogView
        return SearchCatalogView(context, request)

    def test_search_success(self):
        request = testing.DummyRequest()
        context = testing.DummyResource()
        request.sdiapi = DummySDIAPI()
        inst = self._makeOne(context, request)
        resp = inst.search_success({'a':1})
        self.assertEqual(request.session['catalogsearch.appstruct'], {'a':1})
        self.assertEqual(resp.location, '/mgmt_path')

    def test_show_no_appstruct(self):
        request = testing.DummyRequest()
        context = testing.DummyResource()
        form = DummyForm()
        inst = self._makeOne(context, request)
        result = inst.show(form)
        self.assertEqual(result, {'searchresults': (),
                                  'form':'form'})

    def test_show_with_appstruct_no_results(self):
        request = testing.DummyRequest()
        context = testing.DummyResource()
        appstruct = {'cqe_expression':"name=='abc'"}
        request.session['catalogsearch.appstruct'] = appstruct
        form = DummyForm()
        inst = self._makeOne(context, request)
        q = DummyQuery([])
        objectmap = DummyObjectmap()
        def parse_query(expr, catalog):
            return q
        def find_objectmap(context):
            return objectmap 
        inst.parse_query = parse_query
        inst.find_objectmap = find_objectmap
        result = inst.show(form)
        self.assertEqual(result, {'searchresults': [('', 'No results')],
                                  'form':'form'})
        self.assertEqual(request.session['_f_success'], ['Query succeeded'])

    def test_show_with_appstruct_and_results(self):
        request = testing.DummyRequest()
        context = testing.DummyResource()
        appstruct = {'cqe_expression':"name=='abc'"}
        request.session['catalogsearch.appstruct'] = appstruct
        form = DummyForm()
        inst = self._makeOne(context, request)
        q = DummyQuery([1,2])
        objectmap = DummyObjectmap()
        def parse_query(expr, catalog):
            return q
        def find_objectmap(context):
            return objectmap 
        inst.parse_query = parse_query
        inst.find_objectmap = find_objectmap
        result = inst.show(form)
        self.assertEqual(result, {'searchresults': [(1,1), (2,2)],
                                  'form':'form'})
        self.assertEqual(request.session['_f_success'], ['Query succeeded'])

    def test_show_with_appstruct_query_exception(self):
        request = testing.DummyRequest()
        context = testing.DummyResource()
        appstruct = {'cqe_expression':"name=='abc'"}
        request.session['catalogsearch.appstruct'] = appstruct
        form = DummyForm()
        inst = self._makeOne(context, request)
        inst.logger = DummyLogger()
        result = inst.show(form)
        self.assertEqual(result, {'searchresults': (),
                                  'form':'form'})
        self.assertEqual(request.session['_f_error'],
                         ['Query failed (KeyError: name)'])

class Test_content_is_an_index(unittest.TestCase):
    def setUp(self):
        testing.setUp()
    def tearDown(self):
        testing.tearDown()

    def _callFUT(self, context, request):
        from ..catalog import context_is_an_index
        return context_is_an_index(context, request)
    
    def test_it_true(self):
        request = testing.DummyRequest()
        request.registry.content = DummyContent(True)
        context = testing.DummyResource()
        self.assertEqual(self._callFUT(context, request), True)
        
    def test_it_false(self):
        request = testing.DummyRequest()
        request.registry.content = DummyContent(False)
        context = testing.DummyResource()
        self.assertEqual(self._callFUT(context, request), False)

class Test_reindex_indexes(unittest.TestCase):
    def setUp(self):
        testing.setUp()

    def tearDown(self):
        testing.tearDown()

    def _callFUT(self, context, request):
        from ..catalog import reindex_indexes
        return reindex_indexes(context, request)

    def test_with_indexes(self):
        context = DummyCatalog()
        request = testing.DummyRequest()
        request.sdiapi = DummySDIAPI()
        request.POST = {'item-modify':'a'}
        result = self._callFUT(context, request)
        self.assertEqual(result.location, '/mgmt_path')
        self.assertEqual(
            request.session['_f_success'],
            ['Reindex of selected indexes a succeeded'])
        self.assertEqual(context.reindexed, ['a'])

    def test_without_indexes(self):
        context = DummyCatalog()
        request = testing.DummyRequest()
        request.sdiapi = DummySDIAPI()
        request.POST = testing.DummyResource()
        request.POST.getall = {}.get
        result = self._callFUT(context, request)
        self.assertEqual(result.location, '/mgmt_path')
        self.assertEqual(
            request.session['_f_error'],
            ['No indexes selected to reindex'])

class DummyContent(object):
    def __init__(self, result):
        self.result = result

    def metadata(self, context, name, default=None):
        return self.result
    

class DummyForm(object):
    def render(self, appstruct):
        return 'form'

class DummyLogger(object):
    def exception(self, msg):
        pass
        
class DummyCatalog(object):
    def __init__(self):
        self.objectids = ()

    def reindex(self, indexes=None, registry=None):
        self.indexes = indexes
        self.reindexed = indexes

    def update_indexes(self):
        self.updated = True

class DummyIndex(object):
    def __init__(self, parent=None):
        if parent is None:
            parent = DummyCatalog()
        self.__parent__ = parent
        self.__name__ = 'name'

    def indexed_count(self):
        return 1

    def not_indexed_count(self):
        return 1
    
class DummyResultSet(object):
    def __init__(self, results):
        self.results = results
    def all(self, resolve=False):
        return self.results

class DummyQuery(object):
    def __init__(self, results):
        self.results = results
    def execute(self):
        return DummyResultSet(self.results)

class DummyObjectmap(object):
    def object_for(self, oid):
        return oid
    
class DummySDIAPI(object):
    def mgmt_path(self, *arg, **kw):
        return '/mgmt_path'

