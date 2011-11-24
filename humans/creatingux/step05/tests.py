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

    def test_hello_view(self):
        from views import index_view

        result = index_view({})
        self.assertEqual(result['page_title'], 'Home')

    def test_about_view(self):
        from views import about_view

        result = about_view({})
        self.assertEqual(result['page_title'], 'About')

    def test_company_view(self):
        from views import company_view

        result = company_view({})
        self.assertEqual(result["company"], "ACME, Inc.")
        self.assertEqual(len(result["projects"]), 2)

    def test_people_view(self):
        from views import people_view

        result = people_view({})
        self.assertEqual(result["company"], "ACME, Inc.")
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
