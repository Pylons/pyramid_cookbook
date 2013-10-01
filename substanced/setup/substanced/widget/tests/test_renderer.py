import unittest
from pyramid import testing

class TestZPTRendererFactory(unittest.TestCase):
    def setUp(self):
        testing.setUp()

    def tearDown(self):
        testing.tearDown()
        
    def _makeOne(self, dirs, **kw):
        from substanced.widget import WidgetRendererFactory
        return WidgetRendererFactory(dirs, **kw)

    def test_functional_using_searchpath(self):
        from pkg_resources import resource_filename
        from ..._compat import u
        default_dir = resource_filename('substanced.widget', 'tests/fixtures/')
        renderer = self._makeOne((default_dir,))
        result = renderer('test')
        self.assertEqual(result.strip(), u('<div>Test</div>'))

    def test_functional_using_assetspec(self):
        from ..._compat import u
        renderer = self._makeOne(())
        result = renderer('substanced.widget.tests:fixtures/test.pt')
        self.assertEqual(result.strip(), u('<div>Test</div>'))

    def test_it(self):
        import os
        path = os.path.join(os.path.dirname(__file__), 'fixtures')
        renderer = self._makeOne(
            (path,),
            auto_reload=True,
            debug=True,
            encoding='utf-16',
            translator=lambda *arg: 'translation',
            )
        template = renderer.load('test')
        self.assertEqual(template.auto_reload, True)
        self.assertEqual(template.debug, True)
        self.assertEqual(template.encoding, 'utf-16')
        self.assertEqual(template.translate('a'), 'translation')
