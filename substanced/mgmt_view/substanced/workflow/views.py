import operator

from pyramid.httpexceptions import HTTPFound
from pyramid.view import view_defaults

from ..sdi import (
    mgmt_view,
    RIGHT,
    )
from ..util import get_content_type

@view_defaults(
    permission='sdi.manage-workflow',
    name='workflows',
    workflowed=True,
    )
class WorkflowViews(object):
    def __init__(self, context, request):
        self.context = context
        self.request = request

    def _get_workflows(self):
        content_type = get_content_type(self.context)
        workflow_reg = self.request.registry.workflow
        workflows = sorted(
            workflow_reg.get_all_types(content_type),
            key = operator.attrgetter('name')
            )
        return workflows

    @mgmt_view(
        renderer='templates/workflow.pt',
        tab_title='Workflows',
        tab_near=RIGHT, # try not to be the default tab, we're too obscure
        )
    def show(self):
        results = []
        workflows = self._get_workflows()
        for workflow in workflows:
            transitions = workflow.get_transitions(self.context, self.request)
            states = workflow.get_states(self.context, self.request)
            wfid = str(workflow.type)
            current_state = workflow.state_of(self.context)
            result = {
                'id':wfid,
                'workflow':workflow,
                'transitions':transitions,
                'states':states,
                'current_state':current_state,
                }
            results.append(result)
        return {'workflows':results}

    @mgmt_view(
        request_method='POST',
        check_csrf=True,
        )
    def transition(self):
        workflows = self._get_workflows()
        wfid = self.request.POST['wfid']
        transition = self.request.POST['transition']
        for workflow in workflows:
            if str(workflow.type) == wfid:
                workflow.transition(self.context, self.request, transition)
                self.request.session.flash(
                    'Transitioned %s using %s' % (
                        workflow.name or workflow.type, transition),
                    'info',
                    )
                break
        return HTTPFound(
            self.request.sdiapi.mgmt_url(self.context, '@@workflows')
            )
