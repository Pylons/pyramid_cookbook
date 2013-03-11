import unittest
import transaction

from pyramid import testing


def _initTestingDB():
    from sqlalchemy import create_engine
    from tutorial.models import (
        DBSession,
        Page,
        Base
        )
    engine = create_engine('sqlite://')
    Base.metadata.create_all(engine)
    DBSession.configure(bind=engine)
    with transaction.manager:
        model = Page('FrontPage', 'This is the front page')
        DBSession.add(model)
    return DBSession


class WikiViewTests(unittest.TestCase):
    def setUp(self):
        self.session = _initTestingDB()
        self.config = testing.setUp()

    def tearDown(self):
        self.session.remove()
        testing.tearDown()

    def test_wiki_view(self):
        from tutorial.views import WikiViews

        request = testing.DummyRequest()
        inst = WikiViews(request)
        response = inst.wiki_view()
        self.assertEqual(response['title'], 'Welcome to the Wiki')


class WikiFunctionalTests(unittest.TestCase):
    def setUp(self):
        self.session = _initTestingDB()
        self.config = testing.setUp()
        from tutorial import main

        settings = {}
        app = main(settings)
        from webtest import TestApp

        self.testapp = TestApp(app)

    def tearDown(self):
        self.session.remove()
        testing.tearDown()

    def test_it(self):
        res = self.testapp.get('/', status=200)
        self.assertIn(b'Welcome', res.body)
        res = self.testapp.get('/add', status=200)
        self.assertIn(b'Add Wiki Page', res.body)
        res = self.testapp.get('/100', status=200)
        self.assertIn(b'100', res.body)
        res = self.testapp.get('/100/edit', status=200)
        self.assertIn(b'100', res.body)
        res = self.testapp.get('/100/delete', status=302)
        self.assertIn(b'Found', res.body)