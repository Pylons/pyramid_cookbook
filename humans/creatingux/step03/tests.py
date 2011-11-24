import unittest

class ProjectorViewsUnitTests(unittest.TestCase):
    def test_hello_view(self):
        from views import hello_view
        result = hello_view({})
        self.assertEqual(result['tutorial'], 'Little Dummy')

class ProjectorFunctionalTests(unittest.TestCase):
    def setUp(self):
        from application import main
        app = main()
        from webtest import TestApp
        self.testapp = TestApp(app)

    def test_it(self):
        res = self.testapp.get('/', status=200)
        self.failUnless('Hello' in res.body)