import unittest

from pyramid.testing import DummyRequest
from pyramid.testing import DummyResource


class TutorialViewsUnitTests(unittest.TestCase):
    def test_home_view(self):
        from .views import TutorialViews

        request = DummyRequest()
        title = 'Dummy Context'
        context = DummyResource(title=title, __name__='dummy')
        inst = TutorialViews(context, request)
        result = inst.home()
        self.assertIn('Home', result['page_title'])


class TutorialFunctionalTests(unittest.TestCase):
    def setUp(self):
        from tutorial import main
        app = main({})
        from webtest import TestApp
        self.testapp = TestApp(app)

    def test_home(self):
        result = self.testapp.get('/', status=200)
        self.assertIn(b'Site Folder', result.body)
