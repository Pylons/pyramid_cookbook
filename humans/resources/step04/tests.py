import unittest

from pyramid.testing import DummyRequest
from pyramid.testing import DummyResource

class DummySite(DummyResource):
    title = "Dummy Title"
    __name__ = "dummy"
    __parent__ = None

    def values(self):
        v = DummyResource(title="Dummy Item")
        return [v, v, v, v, v]
    
class ProjectorViewsUnitTests(unittest.TestCase):

    def _makeOne(self, context, request):
        from views import ProjectorViews
        inst = ProjectorViews(context, request)
        return inst

    def test_site_view(self):
        request = DummyRequest()
        context = DummySite()
        inst = self._makeOne(context, request)
        result = inst.site_view()
        self.assertEqual(len(result['children']), 5)

    def test_folder_view(self):
        request = DummyRequest()
        context = DummySite()
        inst = self._makeOne(context, request)
        result = inst.folder_view()
        self.assertEqual(len(result['children']), 5)

    def test_document_view(self):
        request = DummyRequest()
        context = DummyResource()
        inst = self._makeOne(context, request)
        result = inst.document_view()
        self.assertEqual(result, {})

    def test_add_folder_view(self):
        from pyramid.httpexceptions import HTTPFound
        t = 'New Folder'
        request=DummyRequest(params={'folder_title': t})
        context = DummySite()
        inst = self._makeOne(context, request)
        result = inst.add_folder_view()
        # XXX Need a test that the item actually went in the folder
        self.assertEqual(HTTPFound, result.__class__)

    def test_add_document_view(self):
        from pyramid.httpexceptions import HTTPFound
        request=DummyRequest(folder_title='New Document')
        context = DummySite()
        inst = self._makeOne(context, request)
        result = inst.site_view()
        #self.assertEqual(HTTPFound, result.__class__)
        # XXX Need tests that the doc was actually added

class ProjectorFunctionalTests(unittest.TestCase):
    def setUp(self):
        from application import main
        app = main()
        from webtest import TestApp
        self.testapp = TestApp(app)

    def test_it(self):
        res = self.testapp.get('/', status=200)
        self.failUnless('SiteFolder' in res.body)
        res = self.testapp.get('/folder1', status=200)
        self.failUnless('Folder' in res.body)
        res = self.testapp.get('/doc1', status=200)
        self.failUnless('Document' in res.body)
        res = self.testapp.get('/doc2', status=200)
        self.failUnless('Document' in res.body)
        res = self.testapp.get('/folder1/doc1', status=200)
        self.failUnless('Document' in res.body)
