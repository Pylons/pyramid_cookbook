import unittest

from pyramid import testing


class WikiViewTests(unittest.TestCase):
    def setUp(self):
        self.config = testing.setUp()

    def tearDown(self):
        testing.tearDown()

    def test_wiki_view(self):
        from tutorial.views import WikiViews

        request = testing.DummyRequest()
        inst = WikiViews(request)
        response = inst.wiki_view()
        self.assertEqual(response['title'], 'Welcome to the Wiki')


class WikiFunctionalTests(unittest.TestCase):
    def setUp(self):
        from tutorial import main

        settings = {}
        app = main(settings)
        from webtest import TestApp

        self.testapp = TestApp(app)

    def test_it(self):
        res = self.testapp.get('/', status=200)
        self.assertIn(b'Welcome', res.body)
        res = self.testapp.get('/add', status=200)
        self.assertIn(b'Add Wiki Page', res.body)
        res = self.testapp.get('/100', status=200)
        self.assertIn(b'100', res.body)
        res = self.testapp.get('/100/edit', status=200)
        self.assertIn(b'Edit', res.body)
        res = self.testapp.get('/100/delete', status=302)
        self.assertIn(b'Found', res.body)
