import unittest

from pyramid.testing import DummyRequest
from pyramid.testing import setUp
from pyramid.testing import tearDown

class ProjectorViewsUnitTests(unittest.TestCase):
    def setUp(self):
        request = DummyRequest()
        self.config = setUp(request=request)

    def tearDown(self):
        tearDown()

    def _makeOne(self, request):
        from views import ProjectorViews

        inst = ProjectorViews(request)
        return inst

    def test_index_view(self):
        request = DummyRequest()
        inst = self._makeOne(request)
        result = inst.index_view()
        self.assertEqual(result['page_title'], 'Home')

    def test_about_view(self):
        request = DummyRequest()
        inst = self._makeOne(request)
        result = inst.about_view()
        self.assertEqual(result['page_title'], 'About')

    def test_company_view(self):
        request = DummyRequest()
        inst = self._makeOne(request)
        result = inst.company_view()
        self.assertEqual(result["page_title"], "ACME, Inc. Projects")
        self.assertEqual(len(result["projects"]), 2)

    def test_people_view(self):
        request = DummyRequest()
        inst = self._makeOne(request)
        result = inst.people_view()
        self.assertEqual(result["page_title"], "People")
        self.assertEqual(len(result["people"]), 2)

class ProjectorFunctionalTests(unittest.TestCase):
    def setUp(self):
        from application import main
        app = main()
        from webtest import TestApp
        self.testapp = TestApp(app)

    def test_it(self):
        res = self.testapp.get('/', status=200)
        self.failUnless('Home' in res.body)
        res = self.testapp.get('/about.html', status=200)
        self.failUnless('autonomous' in res.body)
        res = self.testapp.get('/people', status=200)
        self.failUnless('Susan' in res.body)
        res = self.testapp.get('/acme', status=200)
        self.failUnless('Silly Slogans' in res.body)
