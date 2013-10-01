import unittest

import mock
from pyramid import testing

class Test_on_startup(unittest.TestCase):
    def setUp(self):
        self.config = testing.setUp()

    def tearDown(self):
        testing.tearDown()

    def _callFUT(self, event):
        from ..subscribers import on_startup
        return on_startup(event)

    @mock.patch('substanced.evolution.subscribers.EvolutionManager')
    def test_autoevolve_false(self, mock_EvolutionManager):
        registry = self.config.registry
        registry.settings['substanced.autoevolve'] = 'false'
        app = testing.DummyResource()
        app.registry = registry
        event = DummyEvent(app, None)
        self._callFUT(event)
        self.assertEqual(mock_EvolutionManager.mock_calls, [])

    @mock.patch('substanced.evolution.subscribers.EvolutionManager')
    def test_autoevolve_missing(self, mock_EvolutionManager):
        registry = self.config.registry
        app = testing.DummyResource()
        app.registry = registry
        event = DummyEvent(app, None)
        self._callFUT(event)
        self.assertEqual(mock_EvolutionManager.mock_calls, [])

    @mock.patch('substanced.evolution.subscribers.EvolutionManager')
    def test_autosync_no_steps(self, mock_EvolutionManager):
        returnFalse = lambda *x: False
        # Python3 / Py3k
        mock_EvolutionManager().evolve().__nonzero__ = returnFalse
        mock_EvolutionManager().evolve().__bool__ = returnFalse
        registry = self.config.registry
        registry.settings['substanced.autoevolve'] = 'true'
        app = testing.DummyResource()
        app.registry = registry
        root = testing.DummyResource()
        app.root_factory = lambda *arg: root
        event = DummyEvent(app, None)
        self._callFUT(event)
        mock_EvolutionManager().evolve.assert_called_with(commit=True)

    @mock.patch('substanced.evolution.subscribers.EvolutionManager')
    def test_autoevolve_run_steps(self, mock_EvolutionManager):
        mock_EvolutionManager().evolve().__iter__ = mock.Mock(
            return_value=iter(["a", "b"]))
        registry = self.config.registry
        registry.settings['substanced.autoevolve'] = 'true'
        app = testing.DummyResource()
        app.registry = registry
        root = testing.DummyResource()
        app.root_factory = lambda *arg: root
        event = DummyEvent(app, None)
        self._callFUT(event)
        mock_EvolutionManager().evolve.assert_called_with(commit=True)

class DummyEvent(object):
    removed_oids = None

    def __init__(self, object, parent, registry=None, moving=None):
        self.object = object
        self.parent = parent
        self.registry = registry
        self.moving = moving
