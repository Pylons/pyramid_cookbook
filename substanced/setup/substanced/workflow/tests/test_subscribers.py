import unittest
import mock
from pyramid import testing

class init_workflows_for_objectTests(unittest.TestCase):
    def setUp(self):
        testing.setUp()

    def tearDown(self):
        testing.tearDown()

    def _callFUT(self, event):
        from substanced.workflow.subscribers import init_workflows_for_object
        return init_workflows_for_object(event)

    def test_event_moving(self):
        event = mock.Mock()
        event.moving = True
        self.assertEqual(self._callFUT(event), None)
        
    @mock.patch('substanced.workflow.subscribers.get_content_type')
    def test_no_workflows(self, mock_get_content_type):
        from substanced.workflow import WorkflowRegistry
        mock_get_content_type.return_value = "Folder"
        obj = mock.Mock()
        event = mock.Mock()
        event.registry = mock.Mock()
        event.registry.workflow = WorkflowRegistry()
        event.object = obj
        event.moving = None
        self._callFUT(event)
        self.assertEqual(obj.mock_calls, [])

    @mock.patch('substanced.workflow.subscribers.get_content_type')
    def test_no_content_type(self, mock_get_content_type):
        from substanced.interfaces import IDefaultWorkflow
        from substanced.workflow import WorkflowRegistry
        mock_get_content_type.return_value = None
        workflow = WorkflowRegistry()
        wf = mock.Mock()
        workflow.add(wf, IDefaultWorkflow)
        obj = mock.Mock()
        event = mock.Mock()
        event.registry = mock.Mock()
        event.registry.workflow = workflow
        event.object = obj
        event.moving = None
        self._callFUT(event)
        self.assertEqual(obj.mock_calls, [])

    @mock.patch('substanced.workflow.subscribers.get_content_type')
    def test_content_type_overrides_default(self, mock_get_content_type):
        from substanced.interfaces import IDefaultWorkflow
        from substanced.workflow import WorkflowRegistry
        mock_get_content_type.return_value = "Folder"
        workflow = WorkflowRegistry()
        wf = mock.Mock()
        wf.type = "basic"
        wf_specific = mock.Mock()
        wf_specific.type = "basic"
        wf_specific.has_state.return_value = False
        workflow.add(wf, IDefaultWorkflow)
        workflow.add(wf_specific, 'Folder')
        obj = mock.Mock()
        event = mock.Mock()
        event.registry = mock.Mock()
        event.registry.workflow = workflow
        event.object = obj
        event.moving = None
        self._callFUT(event)
        self.assertEqual(obj.mock_calls, [])
        self.assertEqual(wf.mock_calls, [])
        self.assertEqual(wf_specific.mock_calls,
                         [mock.call.has_state(obj),
                          mock.call.initialize(obj)])

    @mock.patch('substanced.workflow.subscribers.get_content_type')
    def test_apply_defaults_and_specific(self, mock_get_content_type):
        from substanced.interfaces import IDefaultWorkflow
        from substanced.workflow import WorkflowRegistry
        mock_get_content_type.return_value = "Folder"
        workflow = WorkflowRegistry()
        wf = mock.Mock()
        wf.type = "basic"
        wf.has_state.return_value = False
        wf_specific = mock.Mock()
        wf_specific.type = "basic_2"
        wf_specific.has_state.return_value = False
        workflow.add(wf, IDefaultWorkflow)
        workflow.add(wf_specific, 'Folder')
        obj = mock.Mock()
        event = mock.Mock()
        event.object = obj
        event.registry = mock.Mock()
        event.registry.workflow = workflow
        event.object = obj
        event.moving = None
        self._callFUT(event)
        self.assertEqual(obj.mock_calls, [])
        self.assertEqual(
            wf.mock_calls,
            [mock.call.has_state(obj), mock.call.initialize(obj)]
            )
        self.assertEqual(
            wf_specific.mock_calls,
            [mock.call.has_state(obj), mock.call.initialize(obj)])

    @mock.patch('substanced.workflow.subscribers.get_content_type')
    def test_apply_only_specific(self, mock_get_content_type):
        from substanced.workflow import WorkflowRegistry
        mock_get_content_type.return_value = "Folder"
        workflow = WorkflowRegistry()
        wf = mock.Mock()
        wf.type = "basic"
        wf.has_state.return_value = False
        workflow.add(wf, 'Folder')
        obj = mock.Mock()
        event = mock.Mock()
        event.registry = mock.Mock()
        event.registry.workflow = workflow
        event.object = obj
        event.moving = None
        self._callFUT(event)
        self.assertEqual(obj.mock_calls, [])
        self.assertEqual(
            wf.mock_calls,
            [mock.call.has_state(obj),
             mock.call.initialize(obj),]
            )

    @mock.patch('substanced.workflow.subscribers.get_content_type')
    def test_apply_hierarchy(self, mock_get_content_type):
        from zope.interface import directlyProvides
        from substanced.interfaces import IFolder
        from substanced.workflow import WorkflowRegistry
        mock_get_content_type.return_value = "Folder"
        workflow = WorkflowRegistry()
        wf = mock.Mock()
        wf.type = "basic"
        wf.has_state.return_value = False
        workflow.add(wf, 'Folder')
        obj = DummyContent()
        obj2 = mock.Mock()
        obj.items = lambda *arg: [('obj2', obj2)]
        directlyProvides(obj, IFolder)
        event = mock.Mock()
        event.registry = mock.Mock()
        event.registry.workflow = workflow
        event.object = obj
        event.moving = None
        self._callFUT(event)
        self.assertEqual(obj2.mock_calls, [])
        self.assertEqual(
            wf.mock_calls,
            [
                mock.call.has_state(obj2),
                mock.call.initialize(obj2),
                mock.call.has_state(obj),
                mock.call.initialize(obj)
                ]
            )

class DummyContent:
    pass

