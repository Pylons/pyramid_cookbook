import unittest

from pyramid.testing import DummyRequest
from pyramid.testing import DummyResource

class DummySite(object):
    title = "Dummy Title"
    __name__ = "dummy"
    __parent__ = None

    def values(self):
        return [1,2,3,4,5]
    
class TutorialViewsUnitTests(unittest.TestCase):

    def _makeOne(self, context, request):
        from .views import TutorialViews
        inst = TutorialViews(context, request)
        return inst

    def test_site_view(self):
        request = DummyRequest()
        context = DummySite()
        inst = self._makeOne(context, request)
        result = inst.site()
        self.assertEqual(len(result['children']), 5)

    def test_folder_view(self):
        request = DummyRequest()
        context = DummySite()
        inst = self._makeOne(context, request)
        result = inst.folder()
        self.assertEqual(len(result['children']), 5)

    def test_document_view(self):
        request = DummyRequest()
        context = DummyResource()
        inst = self._makeOne(context, request)
        result = inst.document()
        self.assertEqual(result, {})

class TutorialFunctionalTests(unittest.TestCase):
    def setUp(self):
        from tutorial import main
        app = main({})
        from webtest import TestApp
        self.testapp = TestApp(app)

    def test_it(self):
        res = self.testapp.get('/', status=200)
        self.assertTrue('SiteFolder' in res.body)
        res = self.testapp.get('/folder1', status=200)
        self.assertTrue('Folder' in res.body)
        res = self.testapp.get('/doc1', status=200)
        self.assertTrue('Document' in res.body)
        res = self.testapp.get('/doc2', status=200)
        self.assertTrue('Document' in res.body)
        res = self.testapp.get('/folder1/doc1', status=200)
        self.assertTrue('Document' in res.body)