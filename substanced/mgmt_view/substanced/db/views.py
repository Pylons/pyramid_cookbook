import json
import datetime
import transaction
import pytz

from pyramid_zodbconn import get_connection

from pyramid.httpexceptions import HTTPFound
from pyramid.view import view_defaults
from pyramid.traversal import find_root

from ..sdi import mgmt_view
from ..evolution import EvolutionManager


@view_defaults(
    physical_path='/',
    name='database',
    renderer='templates/db.pt',
    permission='sdi.manage-database'
    )
class ManageDatabase(object):
    get_connection = staticmethod(get_connection)
    EvolutionManager = staticmethod(EvolutionManager)

    def __init__(self, context, request):
        self.context = context
        self.request = request

    @mgmt_view(request_method='GET', tab_title='Database')
    def view(self):
        conn = self.get_connection(self.request)
        db = conn.db()
        am = db.getActivityMonitor()

        data_connections = []
        data_object_stores = []
        data_object_loads = []

        if am:
            # we multiply datetime by 1000 to get JavaScript representatin of
            # unix timestamp
            # TODO: add timezone support
            for data in am.getActivityAnalysis():
                data_connections.append(
                    [int(data['end']*1000), data['connections']])
                data_object_stores.append(
                    [int(data['end']*1000), data['stores']])
                data_object_loads.append(
                    [int(data['end']*1000), data['loads']])
        return dict(
            am=am,
            db=db,
            conn=conn,
            data_connections=json.dumps(data_connections),
            data_object_stores=json.dumps(data_object_stores),
            data_object_loads=json.dumps(data_object_loads),
            )

    @mgmt_view(request_method='POST', request_param='pack', check_csrf=True)
    def pack(self):
        try:
            days = int(self.request.POST['days'])
        except:
            self.request.session.flash('Invalid number of days', 'error')
            raise HTTPFound(location=self.request.sdiapi.mgmt_path(
                self.context, '@@database'))
        conn = self.get_connection(self.request)
        conn.db().pack(days=days)
        self.request.session.flash('Database packed to %s days' % days)
        return HTTPFound(location=self.request.sdiapi.mgmt_path(
            self.context, '@@database'))

    @mgmt_view(request_method='POST', request_param='flush_cache',
               check_csrf=True)
    def flush_cache(self):
        conn = self.get_connection(self.request)
        conn.db().cacheMinimize()
        self.request.session.flash('Database flushed cache')
        return HTTPFound(location=self.request.sdiapi.mgmt_path(
            self.context, '@@database'))

    @mgmt_view(request_method='GET',
               request_param='show_evolve',
               renderer='templates/db_show_evolve.pt',
              )
    def show_evolve(self):
        root = find_root(self.request.context)
        manager = self.EvolutionManager(root, self.request.registry)

        return dict(
            unfinished_steps=list(manager.get_unfinished_steps()),
            finished_steps=list(manager.get_finished_steps_by_value()),
            format_timestamp=_format_timestamp,
            )

    @mgmt_view(request_method='POST',
               request_param='dryrun',
               check_csrf=True)
    def dryrun(self):
        root = find_root(self.request.context)
        manager = self.EvolutionManager(root, self.request.registry)
        complete = manager.evolve(commit=False)
        if complete:
            self.request.session.flash('%d evolution steps dry-run' % len(complete))
        else:
            self.request.session.flash('No evolution steps dry-run')
        return HTTPFound(location=self.request.sdiapi.mgmt_path(
            self.context, '@@database'))

    @mgmt_view(request_method='POST',
               request_param='evolve',
               check_csrf=True)
    def evolve(self):
        root = find_root(self.request.context)
        manager = self.EvolutionManager(root, self.request.registry)
        complete = manager.evolve(commit=True)
        if complete:
            self.request.session.flash('%d evolution steps executed' % len(complete))
        else:
            self.request.session.flash('No evolution steps executed')
        return HTTPFound(location=self.request.sdiapi.mgmt_path(
            self.context, '@@database'))

    @mgmt_view(request_method='POST',
               request_param='evolve_finished',
               check_csrf=True)
    def evolve_finished(self):
        root = find_root(self.request.context)
        manager = self.EvolutionManager(root, self.request.registry)
        step = self.request.POST['step']

        finished_steps = manager.get_finished_steps()
        unfinished_steps = dict(manager.get_unfinished_steps())

        if step in finished_steps:
            self.request.session.flash('Step %s already marked as finished' % step)
        else:
            if step in unfinished_steps:
                manager.add_finished_step(step)
                self.request.session.flash('Step %s marked as finished' % step)
                t = transaction.get()
                t.note('Marked %s evolution step as finished' % step)
            else:
                self.request.session.flash('Unknown step %s, not marking as finished' % step)
        return HTTPFound(location=self.request.sdiapi.mgmt_path(
            self.context, '@@database', query=dict(show_evolve=True)))

    @mgmt_view(request_method='POST',
               request_param='evolve_unfinished',
               check_csrf=True)
    def evolve_unfinished(self):
        root = find_root(self.request.context)
        manager = self.EvolutionManager(root, self.request.registry)
        step = self.request.POST['step']

        finished_steps = manager.get_finished_steps()
        unfinished_steps = dict(manager.get_unfinished_steps())

        if step in finished_steps:
            manager.remove_finished_step(step)
            self.request.session.flash('Step %s marked as unfinished' % step)
            t = transaction.get()
            t.note('Marked %s evolution step as unfinished' % step)
        else:
            if step in unfinished_steps:
                self.request.session.flash('Step %s already marked as unfinished' % step)
            else:
                self.request.session.flash('Unknown step %s, not marking as unfinished' % step)
        return HTTPFound(location=self.request.sdiapi.mgmt_path(
            self.context, '@@database', query=dict(show_evolve=True)))


def _format_timestamp(t, tz):
    if hasattr(tz, 'upper'): # it's a timezone name, not a timezone object
        tz = pytz.timezone(tz)
    return datetime.datetime.fromtimestamp(t, tz).strftime(
        '%Y-%m-%d %H:%M:%S %Z')
