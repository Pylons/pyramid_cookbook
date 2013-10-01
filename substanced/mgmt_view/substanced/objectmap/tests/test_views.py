import unittest

from pyramid import testing

class TestReferencedView(unittest.TestCase):
    def setUp(self):
        self.config = testing.setUp()

    def tearDown(self):
        testing.tearDown()

    def _makeOne(self, context, request):
        from  ..views import ReferencedView
        return ReferencedView(context, request)

    def test_show(self):
        context = testing.DummyResource()
        request = testing.DummyRequest()
        context.__oid__ = 1
        objectmap = DummyObjectMap(('foo-to-bar',), (1,), (2,))
        context.__objectmap__ = objectmap
        inst = self._makeOne(context, request)
        result = inst.show()
        sources = result['sources']
        self.assertEqual(len(sources), 1)
        self.assertEqual(sources[0][0], 'foo-to-bar')
        self.assertEqual(list(sources[0][1]), ['/a/b'])
        targets = result['targets']
        self.assertEqual(len(targets), 1)
        self.assertEqual(targets[0][0], 'foo-to-bar')
        self.assertEqual(list(targets[0][1]), ['/a/b'])

class DummyObjectMap(object):
    def __init__(self, reftypes=(), targetids=(), sourceids=()):
        self._reftypes = reftypes
        self._targetids = targetids
        self._sourceids = sourceids
        
    def sourceids(self, oid, reftype):
        return self._sourceids

    def targetids(self, oid, reftype):
        return self._targetids

    def get_reftypes(self):
        return self._reftypes

    def path_for(self, oid):
        return ('', 'a', 'b')
    
