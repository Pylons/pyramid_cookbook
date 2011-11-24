import unittest

class ProjectorViewsUnitTests(unittest.TestCase):
    def test_hello_world(self):
        from application import hello_world
        result = hello_world({})
        self.assertEqual(result.body, 'hello!')

class ProjectorFunctionalTests(unittest.TestCase):
    def setUp(self):
        from application import main
        app = main()
        from webtest import TestApp
        self.testapp = TestApp(app)

    def test_it(self):
        res = self.testapp.get('/', status=200)
        self.failUnless('hello' in res.body)