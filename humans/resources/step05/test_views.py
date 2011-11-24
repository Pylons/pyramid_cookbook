import unittest

from pyramid.testing import DummyRequest
from pyramid.testing import setUp
from pyramid.testing import tearDown

class DummyContext(object):
    title = "Dummy Context"


class ProjectorViewsUnitTests(unittest.TestCase):
    def setUp(self):
        request = DummyRequest()
        self.config = setUp(request=request)

    def tearDown(self):
        tearDown()

    def _makeOne(self, request):
        from views import ProjectorViews

        context = DummyContext()
        inst = ProjectorViews(context, request)
        return inst

    def test_site_view(self):
        request = DummyRequest()
        inst = self._makeOne(request)
        result = inst.site_view()
        self.assertEqual(result['page_title'], 'Home')

    def test_company_view(self):
        request = DummyRequest()
        inst = self._makeOne(request)
        result = inst.company_view()
        self.assertEqual(result["page_title"], "Dummy Context")

    def test_project_view(self):
        request = DummyRequest()
        inst = self._makeOne(request)
        result = inst.project_view()
        self.assertEqual(result["page_title"], "Dummy Context")

    def test_folder_view(self):
        request = DummyRequest()
        inst = self._makeOne(request)
        result = inst.folder_view()
        self.assertEqual(result["page_title"], "Dummy Context")

    def test_document_view(self):
        request = DummyRequest()
        inst = self._makeOne(request)
        result = inst.document_view()
        self.assertEqual(result["page_title"], "Dummy Context")

    def test_people_view(self):
        request = DummyRequest()
        inst = self._makeOne(request)
        result = inst.people_view()
        self.assertEqual(result["page_title"], "Dummy Context")

    def test_person_view(self):
        request = DummyRequest()
        inst = self._makeOne(request)
        result = inst.person_view()
        self.assertEqual(result["page_title"], "Dummy Context")


class ProjectorFunctionalTests(unittest.TestCase):
    def setUp(self):
        from application import main

        app = main()
        from webtest import TestApp

        self.testapp = TestApp(app)

    def test_it(self):
        res = self.testapp.get('/', status=200)
        self.failUnless('Home page content' in res.body)
        res = self.testapp.get('/about', status=200)
        self.failUnless('project management system' in res.body)
        res = self.testapp.get('/acme', status=200)
        self.failUnless('our company' in res.body)
        res = self.testapp.get('/acme/project01', status=200)
        self.failUnless('Project Content' in res.body)
        res = self.testapp.get('/acme/project01/folder1', status=200)
        self.failUnless('Folder Contents' in res.body)
        res = self.testapp.get('/acme/project01/folder1/doc3',
                               status=200)
        self.failUnless('deep down' in res.body)
        res = self.testapp.get('/people', status=200)
        self.failUnless('Add Person' in res.body)
        res = self.testapp.get('/people/bbarker', status=200)
        self.failUnless('goes here' in res.body)
        res = self.testapp.get('/updates.json', status=200)
        self.failUnless('888' in res.body)
