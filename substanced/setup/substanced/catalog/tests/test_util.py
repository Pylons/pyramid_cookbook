import unittest
from pyramid import testing


class Test_oid_from_resource(unittest.TestCase):
    def _callFUT(self, resource):
        from ..util import oid_from_resource
        return oid_from_resource(resource)

    def test_it_resource_is_None(self):
        self.assertRaises(ValueError, self._callFUT, None)

    def test_it_resource_has_no_oid(self):
        resource = testing.DummyResource()
        self.assertRaises(ValueError, self._callFUT, resource)

    def test_it_resource_has_oid(self):
        resource = testing.DummyResource()
        resource.__oid__ = 1
        self.assertEqual(self._callFUT(resource), 1)

