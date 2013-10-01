import unittest
from pyramid import testing
import mock

class TestManageDatabase(unittest.TestCase):
    def _makeOne(self, context, request):
        from ..views import ManageDatabase
        return ManageDatabase(context, request)

    def test_view_with_activity_monitor(self):
        context = testing.DummyResource()
        request = testing.DummyRequest()
        inst = self._makeOne(context, request)
        am = DummyActivityMonitor()
        conn = DummyConnection(am=am)
        inst.get_connection = lambda *arg: conn
        result = inst.view()
        self.assertEqual(result['data_connections'], '[[1000, 1], [1000, 1]]')
        self.assertEqual(result['data_object_loads'], '[[1000, 1], [1000, 1]]')
        self.assertEqual(result['data_object_stores'], '[[1000, 1], [1000, 1]]')

    def test_view_no_activity_monitor(self):
        context = testing.DummyResource()
        request = testing.DummyRequest()
        inst = self._makeOne(context, request)
        conn = DummyConnection(am=None)
        inst.get_connection = lambda *arg: conn
        result = inst.view()
        self.assertEqual(result['data_connections'], '[]')
        self.assertEqual(result['data_object_loads'], '[]')
        self.assertEqual(result['data_object_stores'], '[]')

    def test_pack(self):
        context = testing.DummyResource()
        request = testing.DummyRequest()
        inst = self._makeOne(context, request)
        conn = DummyConnection(am=None)
        inst.get_connection = lambda *arg: conn
        request.POST['days'] = '5'
        request.sdiapi = DummySDIAPI()
        resp = inst.pack()
        self.assertEqual(conn._db.packed, 5)
        self.assertEqual(resp.location, '/mgmt_path')

    def test_pack_invalid_days(self):
        from pyramid.httpexceptions import HTTPFound
        context = testing.DummyResource()
        request = testing.DummyRequest()
        inst = self._makeOne(context, request)
        conn = DummyConnection(am=None)
        inst.get_connection = lambda *arg: conn
        request.POST['days'] = 'p'
        request.sdiapi = DummySDIAPI()
        self.assertRaises(HTTPFound, inst.pack)

    def test_flush_cache(self):
        context = testing.DummyResource()
        request = testing.DummyRequest()
        inst = self._makeOne(context, request)
        conn = DummyConnection(am=None)
        inst.get_connection = lambda *arg: conn
        request.POST['days'] = '5'
        request.sdiapi = DummySDIAPI()
        resp = inst.flush_cache()
        self.assertTrue(conn._db.minimized)
        self.assertEqual(resp.location, '/mgmt_path')

    def test_show_evolve(self):
        context = testing.DummyResource()
        request = testing.DummyRequest()
        inst = self._makeOne(context, request)
        inst.EvolutionManager = DummyEvolutionManager()

        resp = inst.show_evolve()
        self.assertEqual(resp['finished_steps'], ["1", "2", "3"])
        self.assertEqual(resp['unfinished_steps'], [('4', '4'), ('5', '5'), ('6', '6')])

    def test_evolve(self):
        context = testing.DummyResource()
        request = testing.DummyRequest()
        request.sdiapi = DummySDIAPI()
        request.session.flash = DummyFlash()
        inst = self._makeOne(context, request)
        inst.EvolutionManager = DummyEvolutionManager()

        resp = inst.evolve()
        self.assertEqual(resp.location, '/mgmt_path')
        self.assertEqual(request.session.flash.messages,
                         ["3 evolution steps executed"])

    def test_evolve_empty(self):
        context = testing.DummyResource()
        request = testing.DummyRequest()
        request.sdiapi = DummySDIAPI()
        request.session.flash = DummyFlash()
        inst = self._makeOne(context, request)
        inst.EvolutionManager = DummyEvolutionManager([])

        resp = inst.evolve()
        self.assertEqual(resp.location, '/mgmt_path')
        self.assertEqual(request.session.flash.messages,
                         ["No evolution steps executed"])

    def test_dryrun(self):
        context = testing.DummyResource()
        request = testing.DummyRequest()
        request.sdiapi = DummySDIAPI()
        request.session.flash = DummyFlash()
        inst = self._makeOne(context, request)
        inst.EvolutionManager = DummyEvolutionManager()

        resp = inst.dryrun()
        self.assertEqual(resp.location, '/mgmt_path')
        self.assertEqual(request.session.flash.messages,
                         ["3 evolution steps dry-run"])

    def test_dryrun_empty(self):
        context = testing.DummyResource()
        request = testing.DummyRequest()
        request.sdiapi = DummySDIAPI()
        request.session.flash = DummyFlash()
        inst = self._makeOne(context, request)
        inst.EvolutionManager = DummyEvolutionManager([])

        resp = inst.dryrun()
        self.assertEqual(resp.location, '/mgmt_path')
        self.assertEqual(request.session.flash.messages,
                         ["No evolution steps dry-run"])

    def test_evolve_finished(self):
        context = testing.DummyResource()
        request = testing.DummyRequest()
        request.sdiapi = DummySDIAPI()
        request.session.flash = DummyFlash()
        request.POST['step'] = '4'
        inst = self._makeOne(context, request)
        inst.EvolutionManager = DummyEvolutionManager()

        resp = inst.evolve_finished()
        self.assertEqual(resp.location, '/mgmt_path')
        self.assertEqual(request.session.flash.messages,
                         ["Step 4 marked as finished"])
        self.assertEqual(inst.EvolutionManager.finished_steps, ["4"])

    def test_evolve_finished_unknown(self):
        context = testing.DummyResource()
        request = testing.DummyRequest()
        request.sdiapi = DummySDIAPI()
        request.session.flash = DummyFlash()
        request.POST['step'] = '4'
        inst = self._makeOne(context, request)
        inst.EvolutionManager = DummyEvolutionManager([])

        resp = inst.evolve_finished()
        self.assertEqual(resp.location, '/mgmt_path')
        self.assertEqual(request.session.flash.messages,
                         ["Unknown step 4, not marking as finished"])

    def test_evolve_finished_already(self):
        context = testing.DummyResource()
        request = testing.DummyRequest()
        request.sdiapi = DummySDIAPI()
        request.session.flash = DummyFlash()
        request.POST['step'] = '1'
        inst = self._makeOne(context, request)
        inst.EvolutionManager = DummyEvolutionManager()

        resp = inst.evolve_finished()
        self.assertEqual(resp.location, '/mgmt_path')
        self.assertEqual(request.session.flash.messages,
                         ["Step 1 already marked as finished"])

    def test_evolve_unfinished(self):
        context = testing.DummyResource()
        request = testing.DummyRequest()
        request.sdiapi = DummySDIAPI()
        request.session.flash = DummyFlash()
        request.POST['step'] = '1'
        inst = self._makeOne(context, request)
        inst.EvolutionManager = DummyEvolutionManager()

        resp = inst.evolve_unfinished()
        self.assertEqual(resp.location, '/mgmt_path')
        self.assertEqual(request.session.flash.messages,
                         ["Step 1 marked as unfinished"])
        self.assertEqual(inst.EvolutionManager.removed_finished_steps, ["1"])

    def test_evolve_unfinished_unknown(self):
        context = testing.DummyResource()
        request = testing.DummyRequest()
        request.sdiapi = DummySDIAPI()
        request.session.flash = DummyFlash()
        request.POST['step'] = '9'
        inst = self._makeOne(context, request)
        inst.EvolutionManager = DummyEvolutionManager()

        resp = inst.evolve_unfinished()
        self.assertEqual(resp.location, '/mgmt_path')
        self.assertEqual(request.session.flash.messages,
                         ["Unknown step 9, not marking as unfinished"])

    def test_evolve_unfinished_already(self):
        context = testing.DummyResource()
        request = testing.DummyRequest()
        request.sdiapi = DummySDIAPI()
        request.session.flash = DummyFlash()
        request.POST['step'] = '4'
        inst = self._makeOne(context, request)
        inst.EvolutionManager = DummyEvolutionManager()

        resp = inst.evolve_unfinished()
        self.assertEqual(resp.location, '/mgmt_path')
        self.assertEqual(request.session.flash.messages,
                         ["Step 4 already marked as unfinished"])


    def test_format_timestamp(self):
        from ..views import _format_timestamp
        dt = _format_timestamp(1374121920.462345, 'UTC')
        self.assertEqual(dt, '2013-07-18 04:32:00 UTC')


class DummyDB(object):
    def __init__(self, am=None):
        self.am = am

    def getActivityMonitor(self):
        return self.am

    def pack(self, days=None):
        self.packed = days

    def cacheMinimize(self):
        self.minimized = True

class DummyActivityMonitor(object):
    def getActivityAnalysis(self):
        return [{'end':1, 'connections':1, 'stores':1, 'loads':1}]*2

class DummyConnection(object):
    def __init__(self, am=None):
        self._db = DummyDB(am=am)

    def db(self):
        return self._db

class DummySDIAPI(object):
    def mgmt_path(self, *arg, **kw):
        return '/mgmt_path'

class DummyEvolutionManager(object):

    def __init__(self, unfinished_steps=None):
        if unfinished_steps is None:
            self.unfinished_steps = ["4", "5", "6"]
        else:
            self.unfinished_steps = unfinished_steps
        self.finished_steps = []
        self.removed_finished_steps = []

    def __call__(self, root, registry):
        self.root = root
        self.registry = registry
        return self

    def get_unfinished_steps(self):
        return zip(self.unfinished_steps, self.unfinished_steps)

    def get_finished_steps_by_value(self):
        return ["1", "2", "3"]

    def get_finished_steps(self):
        return ["1", "2", "3"]

    def evolve(self, commit):
        return self.unfinished_steps

    def add_finished_step(self, step):
        self.finished_steps.append(step)

    def remove_finished_step(self, step):
        self.removed_finished_steps.append(step)

class DummyFlash(object):

    def __init__(self):
        self.messages = []

    def __call__(self, msg):
        self.messages.append(msg)
