import unittest

from pyramid import testing

class TestIndexingView(unittest.TestCase):
    def setUp(self):
        self.config = testing.setUp()

    def tearDown(self):
        testing.tearDown()

    def _makeOne(self, context, request):
        from  ..views import WorkflowViews
        return WorkflowViews(context, request)

    def test__get_workflows(self):
        context = testing.DummyResource()
        request = testing.DummyRequest()
        request.registry.content = DummyContent()
        workflow = DummyWorkflow('result')
        request.registry.workflow = DummyWorkflowRegistry([workflow])
        inst = self._makeOne(context, request)
        results = inst._get_workflows()
        self.assertEqual(results, [workflow])
        

    def test_show(self):
        context = testing.DummyResource()
        request = testing.DummyRequest()
        inst = self._makeOne(context, request)
        workflow = DummyWorkflow('result')
        inst._get_workflows = lambda: [workflow]
        result = inst.show()
        self.assertEqual(
            result,
            {'workflows': [
                {'states': 'result',
                 'transitions': 'result',
                 'id': 'workflow',
                 'current_state':'result',
                 'workflow': workflow}]
             }
            )

    def test_reindex(self):
        context = testing.DummyResource()
        request = testing.DummyRequest()
        request.sdiapi = DummySDIAPI()
        request.POST['wfid'] = 'workflow'
        request.POST['transition'] = 'doit'
        workflow = DummyWorkflow('result')
        inst = self._makeOne(context, request)
        inst._get_workflows = lambda: [workflow]
        result = inst.transition()
        self.assertEqual(result.__class__.__name__, 'HTTPFound')
        self.assertTrue(workflow.transitioned, True)

class DummyWorkflow(object):
    type = 'workflow'
    name = 'workflow'
    def __init__(self, result):
        self.result = result

    def get_transitions(self, *arg):
        return self.result

    def get_states(self, *arg):
        return self.result

    def transition(self, context, request, name):
        self.transitioned = True

    def state_of(self, context):
        return self.result
        
class DummyWorkflowRegistry(object):
    def __init__(self, result):
        self.result = result

    def get_all_types(self, content_type):
        return self.result
    
class DummyContent(object):
    def typeof(self, context):
        return 'abc'

class DummySDIAPI(object):
    def mgmt_url(self, *arg, **kw):
        return 'http://mgmt_url'
