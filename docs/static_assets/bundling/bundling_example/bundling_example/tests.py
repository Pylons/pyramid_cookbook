import unittest

from pyramid import testing


class ViewTests(unittest.TestCase):
    def setUp(self):
        self.config = testing.setUp()

    def tearDown(self):
        testing.tearDown()

    def test_my_view(self):
        from .views.default import my_view
        request = testing.DummyRequest()
        info = my_view(request)
        self.assertEqual(info['project'], 'bundling_example')


class FunctionalTests(unittest.TestCase):
    def setUp(self):
        from bundling_example import main
        additional_settings = {
            'statics.dir':'statics',
            'statics.build_dir':'static_build'
        }
        app = main({}, **additional_settings)
        from webtest import TestApp
        self.testapp = TestApp(app)

    def test_root(self):
        res = self.testapp.get('/', status=200)
        self.assertTrue(b'Pyramid' in res.body)
