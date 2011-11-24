import unittest

from pyramid.testing import DummyRequest
from pyramid.testing import DummyResource

class ProjectorViewsUnitTests(unittest.TestCase):
    def test_default_view(self):
        from views import ProjectorViews

        request = DummyRequest()
        title = "Dummy Context"
        context = DummyResource(title=title, __name__='dummy')
        inst = ProjectorViews(context, request)
        result = inst.default_view()
        self.assertEqual(result['page_title'], 'Dummy Context')
        self.assertEqual(result['parent_title'], 'None')
        self.assertEqual(result['name'], 'dummy')

class ProjectorFunctionalTests(unittest.TestCase):
    def setUp(self):
        from application import main

        app = main()
        from webtest import TestApp

        self.testapp = TestApp(app)

    def test_it(self):
        res = self.testapp.get('/', status=200)
        self.failUnless('Site Folder' in res.body)
        self.failUnless('Projector Site' in res.body)
