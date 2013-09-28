import unittest

from pyramid.testing import DummyRequest
from pyramid.testing import DummyResource

class TutorialViewsUnitTests(unittest.TestCase):
    def test_home(self):
        from .views import TutorialViews

        request = DummyRequest()
        title = 'Dummy Context'
        context = DummyResource(title=title)
        inst = TutorialViews(context, request)
        result = inst.home()
        self.assertEqual(result['view_name'], 'Home View')


class TutorialFunctionalTests(unittest.TestCase):
    def setUp(self):
        from tutorial import main
        app = main({})
        from webtest import TestApp
        self.testapp = TestApp(app)

    def test_home(self):
        res = self.testapp.get('/hello', status=200)
        self.assertTrue(b'Hi My Site' in res.body)

