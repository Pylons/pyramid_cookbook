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

    def test_site(self):
        request = DummyRequest()
        context = DummySite()
        inst = self._makeOne(context, request)
        result = inst.site()
        self.assertIn('Root', result['page_title'])

    def test_folder_view(self):
        request = DummyRequest()
        context = DummySite()
        inst = self._makeOne(context, request)
        result = inst.folder()
        self.assertIn('Folder', result['page_title'])

    def test_document_view(self):
        request = DummyRequest()
        context = DummyResource()
        inst = self._makeOne(context, request)
        result = inst.document()
        self.assertIn('Document', result['page_title'])

class TutorialFunctionalTests(unittest.TestCase):
    def setUp(self):
        from tutorial import main
        app = main({})
        from webtest import TestApp
        self.testapp = TestApp(app)

    def test_it(self):
        res = self.testapp.get('/', status=200)
        self.assertTrue('Root' in res.body)
        res = self.testapp.get('/folder1', status=200)
        self.assertTrue('Folder' in res.body)
        res = self.testapp.get('/doc1', status=200)
        self.assertTrue('Document' in res.body)
        res = self.testapp.get('/doc2', status=200)
        self.assertTrue('Document' in res.body)
        res = self.testapp.get('/folder1/doc1', status=200)
        self.assertTrue('Document' in res.body)