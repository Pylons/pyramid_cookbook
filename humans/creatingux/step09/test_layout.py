import unittest

from pyramid.testing import DummyRequest
from pyramid.testing import setUp
from pyramid.testing import tearDown

class LayoutUnitTests(unittest.TestCase):
    def setUp(self):
        request = DummyRequest()
        self.config = setUp(request=request)

    def tearDown(self):
        tearDown()

    def _makeOne(self):
        from layouts import Layouts

        inst = Layouts()
        return inst

    def test_global_template(self):
        from chameleon.zpt.template import Macro

        inst = self._makeOne()
        self.assertEqual(inst.global_template.__class__, Macro)

    def test_company_name(self):
        from dummy_data import COMPANY

        inst = self._makeOne()
        self.assertEqual(inst.company_name, COMPANY)

    def test_site_menu(self):
        from dummy_data import SITE_MENU

        inst = self._makeOne()
        inst.request = DummyRequest()
        self.assertEqual(len(inst.site_menu), len(SITE_MENU))
