import datetime
from logging import getLogger

from pyramid.view import view_defaults
from pyramid.httpexceptions import HTTPPreconditionFailed
from pyramid.compat import PY3, text_type
from substanced.sdi import mgmt_view, RIGHT
from substanced.util import (
    get_oid,
    get_auditlog,
    )

@view_defaults(
    permission='sdi.view-auditlog',
    http_cache=0,
    )
class AuditLogEventStreamView(object):
    get_auditlog = staticmethod(get_auditlog) # for test replacement
    logger = getLogger('substanced')

    def __init__(self, context, request):
        self.context = context
        self.request = request

    @mgmt_view(
        name='auditing',
        tab_title='Auditing',
        renderer='templates/auditing.pt',
        tab_near=RIGHT,
        physical_path='/',
        )
    def auditing(self):
        log = self.get_auditlog(self.context)
        log_exists = False
        results = []
        if log is not None:
            log_exists = True
            for gen, idx, event in log:
                tz = self.request.user.timezone
                dt = datetime.datetime.fromtimestamp(event.timestamp, tz)
                time = dt.strftime('%Y-%m-%d %H:%M:%S %Z')
                results.insert(0, (gen, idx, time, event))
        return {'results':results, 'log_exists':log_exists}

    @mgmt_view(name='auditstream-sse', tab_condition=False)
    def auditstream_sse(self):
        """Returns an event stream suitable for driving an HTML5 EventSource.
           The event stream will contain auditing events.

           Obtain events for the context of the view only::

            var source = new EventSource(
               "${request.sdiapi.mgmt_path(context, 'auditstream-sse')}");
           
           Obtain events for a single OID unrelated to the context::

            var source = new EventSource(
               "${request.sdiapi.mgmt_path(context, 'auditstream-sse', query={'oid':'12345'})}");

           Obtain events for a set of OIDs::

            var source = new EventSource(
               "${request.sdiapi.mgmt_path(context, 'auditstream-sse', query={'oid':['12345', '56789']})}");

           Obtain all events for all oids::

            var source = new EventSource(
               "${request.sdiapi.mgmt_path(context, 'auditstream-sse', query={'all':'1'})}");
           
           The executing user will need to possess the ``sdi.view-auditstream``
           permission against the context on which the view is invoked.
        """
        request = self.request
        response = request.response
        response.content_type = 'text/event-stream'
        last_event_id = request.headers.get('Last-Event-Id')
        log = self.get_auditlog(self.context)
        if log is None:
            return HTTPPreconditionFailed('Auditing not configured')
        if not last_event_id:
            # first call, set a baseline event id
            gen, idx = log.latest_id()
            msg = compose_message('%s-%s' % (gen, idx))
            response.text = msg
            self.logger.debug(
                'New SSE connection on %s, returning %s' % (
                    request.url, msg)
                )
            return response
        else:
            if request.GET.get('all'):
                oids = ()
            elif request.GET.get('oid'):
                oids = map(int, request.GET.getall('oid'))
            else:
                oids = [get_oid(self.context)]
            _gen, _idx = map(int, last_event_id.split('-', 1))
            events = log.newer(_gen, _idx, oids=oids)
            msg = text_type('')
            for gen, idx, event in events:
                event_id = '%s-%s' % (gen, idx)
                message = compose_message(event_id, event.name, event.payload)
                msg += message
            self.logger.debug(
                'SSE connection on %s with id %s-%s, returning %s' % (
                    request.url, _gen, _idx, msg)
                )
            response.text = msg
            return response

def compose_message(eventid, name=None, payload=''):
    msg = 'id: %s\n' % eventid
    if name:
        msg += 'event: %s\n' % name
    msg += 'retry: 10000\n'
    msg += 'data: %s\n' % payload
    msg += '\n'
    if PY3: # pragma: no cover
        return msg
    else: # pragma: no cover
        return msg.decode('utf-8')

