import unittest

from pyramid.testing import DummyRequest
from pyramid.testing import DummyResource


class TutorialViewsUnitTests(unittest.TestCase):
    def _makeOne(self, context, request):
        from .views import TutorialViews

        inst = TutorialViews(context, request)
        return inst

    def test_site(self):
        request = DummyRequest()
        context = DummyResource()
        inst = self._makeOne(context, request)
        result = inst.root()
        self.assertIn('Root', result['page_title'])

    def test_folder_view(self):
        request = DummyRequest()
        context = DummyResource()
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
        self.assertIn(b'Root', res.body)
        res = self.testapp.get('/folder1', status=200)
        self.assertIn(b'Folder', res.body)
        res = self.testapp.get('/doc1', status=200)
        self.assertIn(b'Document', res.body)
        res = self.testapp.get('/doc2', status=200)
        self.assertIn(b'Document', res.body)
        res = self.testapp.get('/folder1/doc1', status=200)
        self.assertIn(b'Document', res.body)