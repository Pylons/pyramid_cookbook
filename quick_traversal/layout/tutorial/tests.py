import unittest

from pyramid.testing import DummyRequest


class TutorialViewsUnitTests(unittest.TestCase):
    def _makeOne(self, request):
        from .views import TutorialViews
        inst = TutorialViews(request)
        return inst

    def test_site_view(self):
        request = DummyRequest()
        inst = self._makeOne(request)
        result = inst.site()
        self.assertIn('Site View', result['page_title'])


class TutorialFunctionalTests(unittest.TestCase):
    def setUp(self):
        from tutorial import main
        app = main({})
        from webtest import TestApp
        self.testapp = TestApp(app)

    def test_it(self):
        result = self.testapp.get('/hello', status=200)
        self.assertIn(b'Site View', result.body)
