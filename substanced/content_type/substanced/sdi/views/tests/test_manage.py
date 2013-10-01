import unittest
from pyramid import testing

class TestManagementViews(unittest.TestCase):
    def _makeOne(self, context, request):
        from ..manage import ManagementViews
        return ManagementViews(context, request)

    def test_manage_main_no_view_data(self):
        from pyramid.httpexceptions import HTTPForbidden
        context = testing.DummyResource()
        request = testing.DummyRequest()
        def mgmt_path(ctx, value):
            self.assertEqual(value, '@@login')
            return '/path'
        request.sdiapi = Dummy()
        request.sdiapi.mgmt_path = mgmt_path
        inst = self._makeOne(context, request)
        inst.sdi_mgmt_views = lambda *arg: []
        self.assertRaises(HTTPForbidden, inst.manage_main)
        self.assertEqual(request.session['came_from'], 'http://example.com')

    def test_manage_main_with_view_data(self):
        context = testing.DummyResource()
        request = testing.DummyRequest()
        def mgmt_path(ctx, value):
            self.assertEqual(value, '@@fred')
            return '/path'
        request.sdiapi = Dummy()
        request.sdiapi.mgmt_path = mgmt_path
        inst = self._makeOne(context, request)
        inst.sdi_mgmt_views = lambda *arg: [{'view_name':'fred'}]
        result = inst.manage_main()
        self.assertEqual(result.location, '/path')

    def test_add_content_no_views(self):
        context = testing.DummyResource()
        request = testing.DummyRequest()
        inst = self._makeOne(context, request)
        inst.sdi_add_views = lambda *arg: []
        result = inst.add_content()
        self.assertEqual(result, {'views':[]})
        
    def test_add_content_with_one_view(self):
        context = testing.DummyResource()
        request = testing.DummyRequest()
        inst = self._makeOne(context, request)
        inst.sdi_add_views = lambda *arg: [{'url':'http://foo'}]
        result = inst.add_content()
        self.assertEqual(result.location, 'http://foo')

class Dummy(object):
    pass
