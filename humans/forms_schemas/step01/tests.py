import unittest

from pyramid.testing import DummyRequest

class ProjectorViewsUnitTests(unittest.TestCase):

    def _makeOne(self, request):
        from views import ProjectorViews
        inst = ProjectorViews(request)
        return inst

    def test_site_view(self):
        request = DummyRequest()
        inst = self._makeOne(request)
        result = inst.site_view()
        self.assertTrue('form' in result.keys())

class ProjectorFunctionalTests(unittest.TestCase):
    def setUp(self):
        from application import main
        app = main()
        from webtest import TestApp
        self.testapp = TestApp(app)

    def test_it(self):
        res = self.testapp.get('/', status=200)
        self.assertTrue('Hello Form' in res.body)
