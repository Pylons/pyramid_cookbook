import unittest
from pyramid import testing

class TestAction(unittest.TestCase):
    def _makeOne(self):
        from ..deferred import Action
        return Action()

    def test___repr__(self):
        inst = self._makeOne()
        result = repr(inst)
        self.assertTrue(
            result.startswith(
                '<substanced.catalog.deferred.Action object oid None for '
                'index None at')
            )

    def test___hash__(self):
        inst = self._makeOne()
        self.assertEqual(hash(inst), hash((inst.oid, inst.index_oid)))

    def test___eq__True(self):
        inst = self._makeOne()
        other = self._makeOne()
        self.assertTrue(inst == other)

    def test___eq__False(self):
        inst = self._makeOne()
        other = self._makeOne()
        other.oid = 123
        self.assertFalse(inst == other)

    def test___lt__(self):
        inst = self._makeOne()
        other = self._makeOne()
        other.oid = 2
        inst.oid = 1
        self.assertTrue(inst < other)
        
    def test___gt__(self):
        # wrapped with total_ordering from functools, so this should work
        inst = self._makeOne()
        other = self._makeOne()
        other.oid = 2
        inst.oid = 1
        self.assertTrue(other.__gt__(inst))

    def test_find_resource_resource_cant_be_found(self):
        from ..deferred import ResourceNotFound
        index = testing.DummyResource()
        index.__objectmap__ = DummyObjectmap(None)
        inst = self._makeOne()
        inst.index = index
        inst.oid = 1
        self.assertRaises(ResourceNotFound, inst.find_resource)

    def test_find_resource_objectmap_cant_be_found(self):
        from ..deferred import ObjectMapNotFound
        index = testing.DummyResource()
        inst = self._makeOne()
        inst.index = index
        inst.oid = 1
        self.assertRaises(ObjectMapNotFound, inst.find_resource)

    def test_find_resource(self):
        index = testing.DummyResource()
        index.__objectmap__ = DummyObjectmap('abc')
        inst = self._makeOne()
        inst.index = index
        inst.oid = 1
        self.assertEqual(inst.find_resource(), 'abc')

class TestResourceNotFound(unittest.TestCase):
    def _makeOne(self, action):
        from ..deferred import ResourceNotFound
        return ResourceNotFound(action)

    def test___repr__(self):
        inst = self._makeOne(1)
        self.assertEqual(
            repr(inst),
            'Indexing error: cannot find resource for oid 1'
            )

class TestIndexAction(unittest.TestCase):
    def _makeOne(self, index, mode='mode', oid='oid'):
        from ..deferred import IndexAction
        return IndexAction(index, mode, oid)

    def test_index_oid_from_index(self):
        index = DummyIndex()
        inst = self._makeOne(index)
        self.assertEqual(inst.index_oid, index.__oid__)

    def test_execute(self):
        index = DummyIndex()
        inst = self._makeOne(index)
        resource = testing.DummyResource()
        inst.find_resource = lambda *arg: resource
        inst.execute()
        self.assertEqual(index.oid, 'oid')
        self.assertEqual(index.resource, resource)

    def test_execute_objectmap_not_found(self):
        from ..deferred import ObjectMapNotFound
        index = DummyIndex()
        inst = self._makeOne(index)
        logger = DummyLogger()
        inst.logger = logger
        def find_resource():
            raise ObjectMapNotFound(None)
        inst.find_resource = find_resource
        inst.execute()
        self.assertEqual(len(logger.messages), 1)
        self.assertEqual(index.oid, None)

    def test_anti(self):
        from ..deferred import UnindexAction
        index = testing.DummyResource()
        index.__oid__ = 1
        inst = self._makeOne(index)
        result = inst.anti()
        self.assertEqual(result.__class__, UnindexAction)
        self.assertEqual(result.index, index) 
        self.assertEqual(result.index_oid, 1)
        self.assertEqual(result.mode, 'mode')
        self.assertEqual(result.oid, 'oid')

class TestReindexAction(unittest.TestCase):
    def _makeOne(self, index, mode='mode', oid='oid'):
        from ..deferred import ReindexAction
        return ReindexAction(index, mode, oid)

    def test_index_oid_from_index(self):
        index = DummyIndex()
        inst = self._makeOne(index)
        self.assertEqual(inst.index_oid, index.__oid__)

    def test_execute(self):
        index = DummyIndex()
        inst = self._makeOne(index)
        resource = testing.DummyResource()
        inst.find_resource = lambda *arg: resource
        inst.execute()
        self.assertEqual(index.oid, 'oid')
        self.assertEqual(index.resource, resource)

    def test_execute_objectmap_not_found(self):
        from ..deferred import ObjectMapNotFound
        index = DummyIndex()
        inst = self._makeOne(index)
        logger = DummyLogger()
        inst.logger = logger
        def find_resource():
            raise ObjectMapNotFound(None)
        inst.find_resource = find_resource
        inst.execute()
        self.assertEqual(index.oid, None)
        self.assertEqual(len(logger.messages), 1)

    def test_anti(self):
        from ..deferred import ReindexAction
        index = testing.DummyResource()
        index.__oid__ = 1
        inst = self._makeOne(index)
        result = inst.anti()
        self.assertEqual(result.__class__, ReindexAction)
        self.assertEqual(result.index, index)
        self.assertEqual(result.index_oid, 1)
        self.assertEqual(result.mode, 'mode')
        self.assertEqual(result.oid, 'oid')

class TestUnindexAction(unittest.TestCase):
    def _makeOne(self, index, mode='mode', oid='oid'):
        from ..deferred import UnindexAction
        return UnindexAction(index, mode, oid)

    def test_index_oid_from_index(self):
        index = DummyIndex()
        inst = self._makeOne(index)
        self.assertEqual(inst.index_oid, index.__oid__)

    def test_execute(self):
        index = DummyIndex()
        inst = self._makeOne(index)
        inst.execute()
        self.assertEqual(index.oid, 'oid')

    def test_anti(self):
        from ..deferred import IndexAction
        index = testing.DummyResource()
        index.__oid__ = 1
        inst = self._makeOne(index)
        result = inst.anti()
        self.assertEqual(result.__class__, IndexAction)
        self.assertEqual(result.index, index)
        self.assertEqual(result.index_oid, 1)
        self.assertEqual(result.mode, 'mode')
        self.assertEqual(result.oid, 'oid')

class TestActionsQueue(unittest.TestCase):
    def _makeOne(self):
        from ..deferred import ActionsQueue
        return ActionsQueue()

    def test_extend(self):
        inst = self._makeOne()
        inst.extend([1])
        self.assertEqual(inst.actions, [1])
        # cant check for _p_changed getting set, some magic goes on that causes
        # it to be false, bleh
        self.assertEqual(inst.gen, 1)

    def test_len(self):
        inst = self._makeOne()
        inst.extend([1])
        self.assertEqual(len(inst), 1)

    def test_popall_no_actions(self):
        inst = self._makeOne()
        self.assertEqual(inst.popall(), None)
        self.assertEqual(inst.gen, 0)

    def test_popall_with_actions(self):
        inst = self._makeOne()
        inst.actions = [1, 2]
        self.assertEqual(inst.popall(), [1,2])
        self.assertEqual(inst.actions, [])
        self.assertEqual(inst.gen, 1)

    def test__p_resolveConflict_states_have_different_keys(self):
        from ZODB.POSException import ConflictError
        inst = self._makeOne()
        self.assertRaises(
            ConflictError,
            inst._p_resolveConflict, None, {'a':1}, {'b':2}
            )
        
    def test__p_resolveConflict_unknown_state_value_change(self):
        from ZODB.POSException import ConflictError
        inst = self._makeOne()
        self.assertRaises(
            ConflictError,
            inst._p_resolveConflict, None, {'a':1}, {'a':2}
            )

    def test__p_resolveConflict_states_get_optimized(self):
        inst = self._makeOne()
        logger = DummyLogger()
        inst.logger = logger
        a1 = DummyAction(1)
        old = state([])
        committed = state([a1, a1])
        new = state([])
        result = inst._p_resolveConflict(old, committed, new)
        self.assertEqual(len(logger.messages), 2)
        self.assertEqual(result['actions'], [a1])

    def test__p_resolveConflict_action_intersection_states_conflict(self):
        from ZODB.POSException import ConflictError
        from ..deferred import IndexAction, UnindexAction
        inst = self._makeOne()
        logger = DummyLogger()
        inst.logger = logger
        index = DummyIndex()
        a1 = IndexAction(index, 'mode', 'oid')
        a2 = UnindexAction(index, 'mode', 'oid')
        old = state([a1])
        committed = state([a2])
        new = state([])
        self.assertRaises(
            ConflictError, inst._p_resolveConflict, old, committed, new)

    def test__p_resolveConflict_action_intersection_states_resolveable(self):
        from ..deferred import IndexAction, ReindexAction
        inst = self._makeOne()
        logger = DummyLogger()
        inst.logger = logger
        index = DummyIndex()
        a1 = IndexAction(index, 'mode', 'oid')
        a2 = ReindexAction(index, 'mode', 'oid')
        old = state([a1])
        committed = state([a2])
        new = state([])
        result = inst._p_resolveConflict(old, committed, new)
        self.assertEqual(len(logger.messages), 2)
        self.assertEqual(result['actions'], [])

    def test__p_resolveConflict_both_new_and_commited_remove_same(self):
        from ZODB.POSException import ConflictError
        inst = self._makeOne()
        logger = DummyLogger()
        inst.logger = logger
        a1 = DummyAction(1)
        old = state([a1])
        committed = state([])
        new = state([])
        self.assertRaises(
            ConflictError,
            inst._p_resolveConflict,
            old,
            committed,
            new)
        self.assertEqual(len(logger.messages), 2)

    def test__p_resolveConflict_new_and_commited_remove_different(self):
        inst = self._makeOne()
        logger = DummyLogger()
        inst.logger = logger
        a1 = DummyAction(1)
        a2 = DummyAction(2)
        old = state([a1, a2])
        committed = state([a1])
        new = state([a2])
        result = inst._p_resolveConflict(old, committed, new)
        self.assertEqual(len(logger.messages), 2)
        self.assertEqual(result['actions'], [])

    def test__p_resolveConflict_both_new_and_commited_add_same(self):
        from ZODB.POSException import ConflictError
        inst = self._makeOne()
        logger = DummyLogger()
        inst.logger = logger
        a1 = DummyAction(1)
        old = state([])
        committed = state([a1])
        new = state([a1])
        self.assertRaises(
            ConflictError,
            inst._p_resolveConflict,
            old,
            committed,
            new
            )
        self.assertEqual(len(logger.messages), 2)

    def test__p_resolveConflict_new_and_commited_add_different(self):
        inst = self._makeOne()
        logger = DummyLogger()
        inst.logger = logger
        a1 = DummyAction(1)
        a2 = DummyAction(2)
        old = state([])
        committed = state([a1])
        new = state([a2])
        result = inst._p_resolveConflict(old, committed, new)
        self.assertEqual(len(logger.messages), 2)
        self.assertEqual(result['actions'], [a1, a2])
        
    def test__p_resolveConflict_with_committed_added_new_not_added(self):
        inst = self._makeOne()
        a1 = DummyAction(1)
        old = state([])
        committed = state([a1])
        new = state([])
        logger = DummyLogger()
        inst.logger = logger
        result = inst._p_resolveConflict(old, committed, new)
        self.assertEqual(len(logger.messages), 2)
        self.assertEqual(result['actions'], [a1])

    def test__p_resolveConflict_with_new_removed(self):
        inst = self._makeOne()
        a1 = DummyAction(1)
        a2 = DummyAction(2)
        old = state([a1])
        committed = state([a1, a2])
        new = state([])
        logger = DummyLogger()
        inst.logger = logger
        result = inst._p_resolveConflict(old, committed, new)
        self.assertEqual(len(logger.messages), 2)
        self.assertEqual(result['actions'], [a2])

    def test__p_resolveConflict_undo_generates_antiactions_for_removed(self):
        inst = self._makeOne()
        a1 = DummyAction(1)
        a2 = DummyAction(2)
        a3 = DummyAction(3)
        old = state([a1, a2], gen=1)
        committed = state([a3], gen=0)
        new = state([], gen=0)
        logger = DummyLogger()
        inst.logger = logger
        result = inst._p_resolveConflict(old, committed, new)
        self.assertEqual(len(logger.messages), 3)
        actions = result['actions']
        self.assertEqual(result['gen'], 1)
        self.assertEqual(actions[0].oid, 1)
        self.assertEqual(actions[1].oid, 2)
        self.assertEqual(actions[2].oid, 3)
        self.assertTrue(actions[0]._anti)
        self.assertTrue(actions[1]._anti)
        self.assertFalse(actions[2]._anti)

    def test__p_resolveConflict_undo_no_antiactions_to_generate(self):
        inst = self._makeOne()
        a1 = DummyAction(1)
        a2 = DummyAction(2)
        old = state([a1, a2], gen=1)
        committed = state([a1, a2], gen=0)
        new = state([a1, a2], gen=0)
        logger = DummyLogger()
        inst.logger = logger
        result = inst._p_resolveConflict(old, committed, new)
        self.assertEqual(len(logger.messages), 2)
        actions = result['actions']
        self.assertEqual(actions, [a1, a2])
        self.assertEqual(result['gen'], 1)

    def test__p_resolveConflict_undo_anti_already_in_new_added(self):
        from ZODB.POSException import ConflictError
        inst = self._makeOne()
        a1 = DummyAction(1)
        a2 = DummyAction(2, antiresult=a1)
        old = state([a2], gen=1)
        committed = state([], gen=0)
        new = state([a1], gen=0)
        logger = DummyLogger()
        inst.logger = logger
        self.assertRaises(
            ConflictError,
            inst._p_resolveConflict, old, committed, new
            )

    def test__p_resolveConflict_undo_anti_already_in_committed(self):
        from ZODB.POSException import ConflictError
        inst = self._makeOne()
        a1 = DummyAction(1)
        a2 = DummyAction(2, antiresult=a1)
        old = state([a2], gen=1)
        committed = state([a1], gen=0)
        new = state([], gen=0)
        logger = DummyLogger()
        inst.logger = logger
        self.assertRaises(
            ConflictError,
            inst._p_resolveConflict, old, committed, new
            )

    def test__p_resolveConflict_resolved_returns_higher_generation_number(self):
        inst = self._makeOne()
        old = state([], gen=0)
        committed = state([], gen=2)
        new = state([], gen=1)
        logger = DummyLogger()
        inst.logger = logger
        result = inst._p_resolveConflict(old, committed, new)
        self.assertEqual(len(logger.messages), 2)
        self.assertEqual(result['actions'], [])
        self.assertEqual(result['gen'], 2)

    def test__p_resolveConflict_resolved_returns_agreed_upon_pactive(self):
        inst = self._makeOne()
        old = state([], gen=0)
        committed = state([], gen=2)
        new = state([], gen=1)
        logger = DummyLogger()
        inst.logger = logger
        result = inst._p_resolveConflict(old, committed, new)
        self.assertEqual(len(logger.messages), 2)
        self.assertEqual(result['actions'], [])
        self.assertEqual(result['pactive'], True)

class Test_which_action(unittest.TestCase):
    def _callFUT(self, a1, a2):
        from ..deferred import which_action
        return which_action(a1, a2)

    def test_conflict_I_U(self):
        from ZODB.POSException import ConflictError
        from ..deferred import IndexAction, UnindexAction
        index = DummyIndex()
        a1 = IndexAction(index, 'mode', 'oid')
        a2 = UnindexAction(index, 'mode', 'oid')
        self.assertRaises(ConflictError, self._callFUT, a1, a2)
    
    def test_conflict_U_I(self):
        from ZODB.POSException import ConflictError
        from ..deferred import IndexAction, UnindexAction
        index = DummyIndex()
        a1 = UnindexAction(index, 'mode', 'oid')
        a2 = IndexAction(index, 'mode', 'oid')
        self.assertRaises(ConflictError, self._callFUT, a1, a2)

    def test_conflict_R_U(self):
        from ZODB.POSException import ConflictError
        from ..deferred import ReindexAction, UnindexAction
        index = DummyIndex()
        a1 = ReindexAction(index, 'mode', 'oid')
        a2 = UnindexAction(index, 'mode', 'oid')
        self.assertRaises(ConflictError, self._callFUT, a1, a2)

    def test_conflict_U_R(self):
        from ZODB.POSException import ConflictError
        from ..deferred import ReindexAction, UnindexAction
        index = DummyIndex()
        a1 = UnindexAction(index, 'mode', 'oid')
        a2 = ReindexAction(index, 'mode', 'oid')
        self.assertRaises(ConflictError, self._callFUT, a1, a2)

    def test_second_R_I(self):
        from ..deferred import ReindexAction, IndexAction
        index = DummyIndex()
        a1 = ReindexAction(index, 'mode', 'oid')
        a2 = IndexAction(index, 'mode', 'oid')
        self.assertEqual(self._callFUT(a1, a2), a2)

    def test_first_I_R(self):
        from ..deferred import ReindexAction, IndexAction
        index = DummyIndex()
        a1 = IndexAction(index, 'mode', 'oid')
        a2 = ReindexAction(index, 'mode', 'oid')
        self.assertEqual(self._callFUT(a1, a2), a1)

    def test_first_I_I(self):
        from ..deferred import IndexAction
        index = DummyIndex()
        a1 = IndexAction(index, 'mode', 'oid')
        a2 = IndexAction(index, 'mode', 'oid')
        self.assertEqual(self._callFUT(a1, a2), a1)

class Test_action_intersection(unittest.TestCase):
    def _callFUT(self, a1, a2):
        from ..deferred import action_intersection
        return action_intersection(a1, a2)

    def test_conflict_I_U(self):
        from ZODB.POSException import ConflictError
        from ..deferred import IndexAction, UnindexAction
        index = DummyIndex()
        a1 = IndexAction(index, 'mode', 'oid')
        a2 = UnindexAction(index, 'mode', 'oid')
        s1 = set([a1])
        s2 = set([a2])
        self.assertRaises(ConflictError, self._callFUT, s1, s2)

    def test_index_replaces_reindex(self):
        from ..deferred import IndexAction, ReindexAction
        index = DummyIndex()
        a1 = IndexAction(index, 'mode', 'oid')
        a2 = ReindexAction(index, 'mode', 'oid')
        s1 = set([a1])
        s2 = set([a2])
        result = self._callFUT(s1, s2)
        self.assertEqual(list(result), [a1])

    def test_no_matches(self):
        from ..deferred import IndexAction, ReindexAction
        index = DummyIndex()
        a1 = IndexAction(index, 'mode', 'oid1')
        a2 = ReindexAction(index, 'mode', 'oid2')
        a3 = IndexAction(index, 'mode', 'oid3')
        s1 = set([a1, a3])
        s2 = set([a2])
        result = self._callFUT(s1, s2)
        self.assertEqual(sorted(list(result)), [])

    def test_only_some_matches(self):
        from ..deferred import IndexAction, ReindexAction
        index = DummyIndex()
        a1_a = IndexAction(index, 'mode', 'oid1')
        a1_b = ReindexAction(index, 'mode', 'oid1')
        a2 = IndexAction(index, 'mode', 'oid2')
        s1 = set([a1_a, a2])
        s2 = set([a1_b])
        result = self._callFUT(s1, s2)
        self.assertEqual(sorted(list(result)), [a1_a])

class Test_commit(unittest.TestCase):
    def _makeOne(self, tries, meth):
        from ..deferred import commit
        return commit(tries)(meth)

    def test_gardenpath(self):
        ap = DummyActionProcessor(None)
        def fakemethod(ap):
            ap.called += 1
        inst = self._makeOne(3, fakemethod)
        inst(ap)
        self.assertEqual(ap.synced, 1)
        self.assertEqual(ap.called, 1)
        self.assertEqual(ap.transaction.begun, 1)
        self.assertEqual(ap.transaction.committed, 1)

    def test_conflict_overflow(self):
        from ZODB.POSException import ConflictError
        ap = DummyActionProcessor(
            None, [ConflictError, ConflictError, ConflictError]
            )
        def fakemethod(ap):
            ap.called += 1
        inst = self._makeOne(3, fakemethod)
        self.assertRaises(ConflictError, inst, ap)
        self.assertEqual(ap.synced, 3)
        self.assertEqual(ap.called, 3)
        self.assertEqual(ap.transaction.begun, 3)
        self.assertEqual(ap.transaction.committed, 0)
        self.assertEqual(ap.transaction.aborted, 3)

    def test_conflicts_but_success(self):
        from ZODB.POSException import ConflictError
        ap = DummyActionProcessor(
            None,
            [ConflictError, ConflictError]
            )
        def fakemethod(ap):
            ap.called += 1
        inst = self._makeOne(3, fakemethod)
        inst(ap)
        self.assertEqual(ap.synced, 3)
        self.assertEqual(ap.called, 3)
        self.assertEqual(ap.transaction.begun, 3)
        self.assertEqual(ap.transaction.committed, 1)
        self.assertEqual(ap.transaction.aborted, 2)

class TestBasicActionProcessor(unittest.TestCase):
    def _makeOne(self, context):
        from ..deferred import BasicActionProcessor
        return BasicActionProcessor(context)

    def test_get_root_no_jar(self):
        context = testing.DummyResource()
        context._p_jar = None
        inst = self._makeOne(context)
        self.assertTrue(inst.get_root() is None)

    def test_get_root_with_jar(self):
        context = testing.DummyResource()
        context._p_jar = DummyJar('root')
        inst = self._makeOne(context)
        self.assertEqual(inst.get_root(), 'root')

    def test_get_queue_no_root(self):
        context = testing.DummyResource()
        context._p_jar = None
        inst = self._makeOne(context)
        self.assertTrue(inst.get_queue() is None)
        
    def test_get_queue_with_root(self):
        context = testing.DummyResource()
        inst = self._makeOne(context)
        context._p_jar = DummyJar({inst.queue_name:'queue'})
        self.assertEqual(inst.get_queue(), 'queue')

    def test_active_True(self):
        context = testing.DummyResource()
        inst = self._makeOne(context)
        queue = DummyQueue()
        queue.pactive = True
        context._p_jar = DummyJar({inst.queue_name:queue})
        self.assertTrue(inst.active())
        
    def test_active_False_no_queue(self):
        context = testing.DummyResource()
        context._p_jar = None
        inst = self._makeOne(context)
        self.assertFalse(inst.active())

    def test_active_False_processor_not_active(self):
        context = testing.DummyResource()
        queue = DummyQueue()
        queue.pactive = False
        inst = self._makeOne(context)
        context._p_jar = DummyJar({inst.queue_name:queue})
        self.assertFalse(inst.active())

    def test_engage_queue_already_present(self):
        context = testing.DummyResource()
        queue = DummyQueue()
        inst = self._makeOne(context)
        inst.transaction = DummyTransaction()
        context._p_jar = DummyJar({inst.queue_name:queue})
        self.assertEqual(inst.engage(), None)
        self.assertTrue(queue.pactive)

    def test_engage_queue_missing_context_has_no_jar(self):
        context = testing.DummyResource()
        inst = self._makeOne(context)
        inst.transaction = DummyTransaction()
        context._p_jar = DummyJar(None)
        self.assertRaises(RuntimeError, inst.engage)

    def test_engage_queue_added(self):
        context = testing.DummyResource()
        inst = self._makeOne(context)
        transaction = DummyTransaction()
        inst.transaction = transaction
        root = {}
        context._p_jar = DummyJar(root)
        self.assertEqual(inst.engage(), None)
        queue = root[inst.queue_name]
        self.assertTrue(transaction.committed)
        self.assertTrue(queue.pactive)

    def test_disengage_no_queue(self):
        context = testing.DummyResource()
        inst = self._makeOne(context)
        context._p_jar = None
        self.assertRaises(RuntimeError, inst.disengage)

    def test_disengage(self):
        context = testing.DummyResource()
        inst = self._makeOne(context)
        queue = DummyQueue()
        root = {inst.queue_name:queue}
        transaction = DummyTransaction()
        inst.transaction = transaction
        context._p_jar = DummyJar(root)
        inst.disengage()
        self.assertEqual(queue.pactive, False)
        self.assertTrue(transaction.committed)

    def test_add_not_engaged(self):
        context = testing.DummyResource()
        context._p_jar = None
        inst = self._makeOne(context)
        self.assertRaises(RuntimeError, inst.add, [1])

    def test_add_extends(self):
        context = testing.DummyResource()
        inst = self._makeOne(context)
        root = {inst.queue_name:[1]}
        context._p_jar = DummyJar(root)
        inst.add([2,3])
        self.assertEqual(root[inst.queue_name], [1,2,3])

    def test_process_gardenpath(self):
        context = testing.DummyResource()
        inst = self._makeOne(context)
        transaction = DummyTransaction()
        inst.transaction = transaction
        logger = DummyLogger()
        inst.logger = logger
        a1 = DummyAction(1)
        queue = DummyQueue([a1])
        root = {inst.queue_name:queue}
        jar = DummyJar(root)
        context._p_jar = jar
        inst.process(once=True)
        self.assertTrue(jar.synced)
        self.assertEqual(queue.result, [])
        self.assertTrue(a1.executed)
        self.assertTrue(transaction.begun)
        self.assertEqual(transaction.committed, 3) # engage, process, disengage
        self.assertEqual(
            logger.messages,
            ['starting basic action processor',
             'executing action 1',
             'committing',
             'committed',
             'stopping basic action processor']
            )

    def test_process_gardenpath_no_actions(self):
        context = testing.DummyResource()
        inst = self._makeOne(context)
        transaction = DummyTransaction()
        inst.transaction = transaction
        logger = DummyLogger()
        inst.logger = logger
        queue = DummyQueue([])
        root = {inst.queue_name:queue}
        jar = DummyJar(root)
        context._p_jar = jar
        inst.process(once=True)
        self.assertTrue(jar.synced)
        self.assertEqual(queue.result, [])
        self.assertTrue(transaction.begun)
        self.assertEqual(transaction.committed, 2) # engage, disengage
        self.assertEqual(
            logger.messages,
            ['starting basic action processor',
             'no actions to execute',
             'stopping basic action processor']
            )

    def test_process_conflicterror_at_initial_commit(self):
        from ZODB.POSException import ConflictError
        context = testing.DummyResource()
        inst = self._makeOne(context)
        transaction = DummyTransaction([ConflictError])
        inst.transaction = transaction
        logger = DummyLogger()
        inst.logger = logger
        inst.engage = lambda *arg, **kw: False
        inst.disengage = lambda *arg, **kw: False
        a1 = DummyAction(1)
        queue = DummyQueue([a1])
        root = {inst.queue_name:queue}
        jar = DummyJar(root)
        context._p_jar = jar
        inst.process(once=True)
        self.assertTrue(jar.synced)
        self.assertEqual(queue.result, [])
        self.assertTrue(a1.executed)
        self.assertTrue(transaction.begun)
        self.assertTrue(transaction.aborted)
        self.assertEqual(
            logger.messages,
            ['starting basic action processor',
             'executing action 1',
             'committing',
             'aborted due to conflict error',
             'stopping basic action processor']
            )

    def test_process_conflicterror_at_disengage(self):
        from ZODB.POSException import ConflictError
        context = testing.DummyResource()
        inst = self._makeOne(context)
        transaction = DummyTransaction([None, ConflictError])
        inst.transaction = transaction
        logger = DummyLogger()
        inst.logger = logger
        inst.engage = lambda *arg, **kw: False
        L = [ConflictError]
        def disengage(*arg, **kw):
            if L:
                raise L.pop(0)
        inst.disengage = disengage
        a1 = DummyAction(1)
        queue = DummyQueue([a1])
        root = {inst.queue_name:queue}
        jar = DummyJar(root)
        context._p_jar = jar
        inst.process(once=True)
        self.assertTrue(jar.synced)
        self.assertEqual(queue.result, [])
        self.assertTrue(a1.executed)
        self.assertEqual(
            logger.messages,
            ['starting basic action processor',
             'executing action 1',
             'committing',
             'committed',
             'stopping basic action processor',
             'couldnt disengage due to conflict, processing queue once more',
             'stopping basic action processor']            
            )

    def test_process_resource_not_found_at_execute(self):
        from ..deferred import ResourceNotFound
        context = testing.DummyResource()
        inst = self._makeOne(context)
        transaction = DummyTransaction()
        inst.transaction = transaction
        logger = DummyLogger()
        inst.logger = logger
        inst.engage = lambda *arg, **kw: False
        inst.disengage = lambda *arg, **kw: False
        a1 = DummyAction(1)
        a1.raises = ResourceNotFound(1)
        queue = DummyQueue([a1])
        root = {inst.queue_name:queue}
        jar = DummyJar(root)
        context._p_jar = jar
        inst.process(once=True)
        self.assertTrue(jar.synced)
        self.assertEqual(queue.result, [])
        self.assertFalse(a1.executed)
        self.assertTrue(transaction.begun)
        self.assertFalse(transaction.committed)
        self.assertEqual(
            logger.messages,
            ['starting basic action processor',
             'executing action 1',
             'Indexing error: cannot find resource for oid 1',
             'stopping basic action processor']
            )

class TestIndexActionSavepoint(unittest.TestCase):
    def _makeOne(self, tm):
        from ..deferred import IndexActionSavepoint
        return IndexActionSavepoint(tm)

    def test_rollback(self):
        tm = DummyIndexActionTM([1])
        inst = self._makeOne(tm)
        tm.actions = None
        inst.rollback()
        self.assertEqual(tm.actions, [1])

class TestIndexActionTM(unittest.TestCase):
    def setUp(self):
        self.config = testing.setUp()

    def tearDown(self):
        testing.tearDown()
        
    def _makeOne(self, index):
        from ..deferred import IndexActionTM
        return IndexActionTM(index)

    def test_register(self):
        index = DummyIndex()
        inst = self._makeOne(index)
        transaction = DummyTransaction()
        inst.transaction = transaction
        inst.register()
        self.assertTrue(transaction.joined)
        self.assertEqual(transaction.beforecommit_fn, inst.flush)
        self.assertEqual(transaction.beforecommit_args, (False,))
        self.assertTrue(inst.registered)

    def test_register_already_registered(self):
        index = DummyIndex()
        inst = self._makeOne(index)
        transaction = DummyTransaction()
        inst.transaction = transaction
        inst.registered = True
        inst.register()
        self.assertFalse(transaction.joined)

    def test_savepoint(self):
        index = DummyIndex()
        inst = self._makeOne(index)
        sp = inst.savepoint()
        self.assertEqual(sp.tm, inst)

    def test_tpc_begin(self):
        index = DummyIndex()
        inst = self._makeOne(index)
        self.assertEqual(inst.tpc_begin(None), None)

    def test_tpc_finish(self):
        index = DummyIndex()
        inst = self._makeOne(index)
        self.assertEqual(inst.tpc_finish(None), None)
        self.assertEqual(index._p_action_tm, None)
        self.assertEqual(inst.index, None)
        self.assertFalse(inst.registered)
        self.assertEqual(inst.actions, [])

    def test_sortKey(self):
        index = DummyIndex()
        inst = self._makeOne(index)
        self.assertEqual(inst.sortKey(), 'IndexActionTM: 1')

    def test_add(self):
        index = DummyIndex()
        inst = self._makeOne(index)
        inst.add(1)
        self.assertEqual(inst.actions, [1])

    def test_flush(self):
        index = DummyIndex()
        inst = self._makeOne(index)
        a1 = DummyAction(1)
        inst.actions = [a1]
        L = []
        inst._process = lambda actions, all=None: L.append((actions, all))
        inst.flush(all=False)
        self.assertEqual(L, [([a1], False)])

    def test_flush_no_actions(self):
        index = DummyIndex()
        inst = self._makeOne(index)
        L = []
        inst._process = lambda actions, all=None: L.append((actions, all))
        inst.flush(all=False)
        self.assertEqual(L, [])

    def test__process_all_True(self):
        index = DummyIndex()
        inst = self._makeOne(index)
        logger = DummyLogger()
        inst.logger = logger
        a1 = DummyAction(1)
        inst._process([a1])
        self.assertTrue(a1.executed)
        self.assertEqual(
            logger.messages,
            ['begin index actions processing',
             'executing all actions immediately: "all" flag',
             'executing action action 1',
             'done processing index actions']
            )

    def test__process_all_False_no_action_processor(self):
        index = DummyIndex()
        inst = self._makeOne(index)
        logger = DummyLogger()
        inst.logger = logger
        a1 = DummyAction(1)
        inst._process([a1], all=False)
        self.assertTrue(a1.executed)
        self.assertEqual(
            logger.messages,
            ['begin index actions processing',
             'executing actions all immediately: no action processor',
             'executing action action 1',
             'done processing index actions']
            )

    def test__process_all_False_no_action_processor_force_deferred(self):
        self.config.registry.settings[
            'substanced.catalogs.force_deferred'] = True
        index = DummyIndex()
        inst = self._makeOne(index)
        logger = DummyLogger()
        inst.logger = logger
        a1 = DummyAction(1)
        inst._process([a1], all=False)
        self.assertTrue(a1.executed)
        self.assertEqual(
            logger.messages,
            ['begin index actions processing',
             'executing actions all immediately: no action processor',
             'executing action action 1',
             'done processing index actions']
            )
        
    def test__process_all_False_inactive_action_processor(self):
        from substanced.interfaces import IIndexingActionProcessor
        from zope.interface import Interface
        self.config.registry.registerAdapter(
            DummyActionProcessor, (Interface,), IIndexingActionProcessor
            )
        index = DummyIndex()
        index.active = False
        index.queue = True
        inst = self._makeOne(index)
        logger = DummyLogger()
        inst.logger = logger
        a1 = DummyAction(1)
        inst._process([a1], all=False)
        self.assertTrue(a1.executed)
        self.assertEqual(
            logger.messages,
            ['begin index actions processing',
             'executing actions all immediately: inactive action processor',
             'executing action action 1',
             'done processing index actions']
            )

    def test__process_all_False_inactive_action_processor_force_deferred(self):
        self.config.registry.settings[
            'substanced.catalogs.force_deferred'] = True
        from substanced.interfaces import IIndexingActionProcessor
        from zope.interface import Interface
        self.config.registry.registerAdapter(
            DummyActionProcessor, (Interface,), IIndexingActionProcessor
            )
        index = DummyIndex()
        index._p_jar = DummyJar(None)
        index.active = False
        index.queue = True
        inst = self._makeOne(index)
        logger = DummyLogger()
        inst.logger = logger
        a1 = DummyAction(1)
        inst._process([a1], all=False)
        self.assertFalse(a1.executed)
        self.assertEqual(
            logger.messages,
            ['begin index actions processing',
             'executing deferred actions: deferred mode forced via "substanced.catalogs.force_deferred" flag in configuration or envvar',
             'adding deferred action action 1',
             'done processing index actions']
            )

    def test__process_all_False_force_deferred_no_jar(self):
        self.config.registry.settings[
            'substanced.catalogs.force_deferred'] = True
        from substanced.interfaces import IIndexingActionProcessor
        from zope.interface import Interface
        self.config.registry.registerAdapter(
            DummyActionProcessor, (Interface,), IIndexingActionProcessor
            )
        index = DummyIndex()
        index._p_jar = DummyJar(None)
        index.active = False
        index.queue = None
        inst = self._makeOne(index)
        logger = DummyLogger()
        inst.logger = logger
        a1 = DummyAction(1)
        inst._process([a1], all=False)
        self.assertTrue(a1.executed)
        self.assertEqual(
            logger.messages,
            ['begin index actions processing',
             'executing actions all immediately: no jar available to find queue',
             'executing action action 1',
             'done processing index actions']
            )
        
    def test__process_all_False_active_action_processor(self):
        from substanced.interfaces import (
            IIndexingActionProcessor,
            MODE_DEFERRED,
            MODE_ATCOMMIT,
            )
        from zope.interface import Interface
        self.config.registry.registerAdapter(
            DummyActionProcessor, (Interface,), IIndexingActionProcessor
            )
        index = DummyIndex()
        index.active = True
        index.queue = True
        inst = self._makeOne(index)
        logger = DummyLogger()
        inst.logger = logger
        a1 = DummyAction(1)
        a1.mode = MODE_DEFERRED
        a2 = DummyAction(2)
        a2.mode = MODE_ATCOMMIT
        inst._process([a1, a2], all=False)
        self.assertFalse(a1.executed)
        self.assertTrue(a2.executed)
        self.assertEqual(index.added, [a1])
        self.assertEqual(
            logger.messages,
            ['begin index actions processing',
             'executing deferred actions: action processor active',
             'adding deferred action action 1',
             'executing action action 2',
             'done processing index actions']
            )

class Test_optimize_actions(unittest.TestCase):
    def _callFUT(self, actions):
        from ..deferred import optimize_actions
        return optimize_actions(actions)

    def test_donothing(self):
        from ..deferred import IndexAction, UnindexAction
        index = DummyIndex()
        actions = [ IndexAction(index, 'mode', 'oid'),
                    UnindexAction(index, 'mode', 'oid') ]
        result = self._callFUT(actions)
        self.assertEqual(result, [])

    def test_doadd(self):
        from ..deferred import IndexAction, ReindexAction
        index = DummyIndex()
        actions = [ IndexAction(index, 'mode', 'oid'),
                    ReindexAction(index, 'mode', 'oid') ]
        result = self._callFUT(actions)
        self.assertEqual(result, [actions[0]])

    def test_dochange(self):
        from ..deferred import IndexAction, UnindexAction, ReindexAction
        index = DummyIndex()
        actions = [ UnindexAction(index, 'mode', 'oid'),
                    IndexAction(index, 'mode', 'oid') ]
        result = self._callFUT(actions)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].__class__, ReindexAction)
        self.assertEqual(result[0].index, index)
        self.assertEqual(result[0].oid, 'oid')

    def test_dodefault(self):
        from ..deferred import IndexAction
        index = DummyIndex()
        actions = [ IndexAction(index, 'mode', 'oid'),
                    IndexAction(index, 'mode', 'oid') ]
        result = self._callFUT(actions)
        self.assertEqual(result, [actions[-1]])

    def test_sorting(self):
        from ..deferred import IndexAction, ReindexAction, UnindexAction
        index1 = DummyIndex()
        index1.__name__ = 'index1'
        index2 = DummyIndex()
        index2.__oid__ = 2
        index2.__name__ = 'index2'
        a1 = IndexAction(index2, 'mode', 'oid1')
        a2 = ReindexAction(index1, 'mode', 'oid3')
        a3 = IndexAction(index2, 'mode', 'oid2')
        a4 = IndexAction(index2, 'mode', 'oid3')
        a5 = UnindexAction(index1, 'mode', 'oid1')
        actions = [a1, a2, a3, a4, a5]
        result = self._callFUT(actions)
        self.assertEqual(result, [a5, a1, a3, a2, a4])

class DummyIndexActionTM(object):
    def __init__(self, actions):
        self.actions = actions

class DummyIndex(object):
    __oid__ = 1
    oid = None
    def index_doc(self, oid, resource):
        self.oid = oid
        self.resource = resource

    reindex_doc = index_doc

    def unindex_doc(self, oid):
        self.oid = oid

class DummyLogger(object):
    def __init__(self):
        self.messages = []
    def info(self, msg):
        self.messages.append(msg)
    debug = info
        

class DummyJar(object):
    def __init__(self, result):
        self.result = result

    def root(self):
        return self.result

    def sync(self):
        self.synced = True


class DummyTransaction(object):
    joined = False
    def __init__(self, raises=None):
        if raises is None:
            raises = []
        self.raises = raises
        self.committed = 0
        self.aborted = 0
        self.begun = 0

    def begin(self):
        self.begun += 1

    def commit(self):
        if self.raises:
            result = self.raises.pop(0)
            if result is not None:
                raise result
        self.committed += 1

    def abort(self):
        self.aborted += 1

    def note(self, msg):
        self._note = msg

    def get(self):
        return self

    def join(self, tm):
        self.joined = tm

    def addBeforeCommitHook(self, fn, args):
        self.beforecommit_fn = fn
        self.beforecommit_args = args

from substanced._compat import total_ordering

@total_ordering
class DummyAction(object):
    index = testing.DummyResource()
    index.__oid__ = 1
    executed = False
    mode = None

    def __init__(self, oid, index_oid=1, position=1, raises=None, anti=False,
                 antiresult=None):
        self.oid = oid
        self.index_oid = index_oid
        self.position = position
        self.raises = raises
        self._anti = anti
        self.antiresult = antiresult

    def execute(self):
        if self.raises:
            raise self.raises
        self.executed = True

    def __repr__(self):
        return 'action %s' % self.oid

    def __lt__(self, other):
        return self.oid < other.oid

    def anti(self):
        if self.antiresult:
            return self.antiresult
        return DummyAction(self.oid, anti=True)

class DummyQueue(object):
    def __init__(self, result=()):
        self.result = result
    def popall(self):
        result = self.result[:]
        self.result = []
        return result
    def __len__(self):
        return len(self.result)

class DummyActionProcessor(object):
    def __init__(self, context, commit_raises=None):
        self.context = context
        if commit_raises is None:
            commit_raises = []
        self.transaction = DummyTransaction(commit_raises)
        self.synced = 0
        self.called = 0

    def active(self):
        return self.context.active

    def sync(self):
        self.synced+=1

    def add(self, actions):
        self.context.added = actions

    def get_queue(self):
        return self.context.queue
    
class DummyObjectmap(object):
    def __init__(self, result):
        self.result = result

    def object_for(self, oid):
        return self.result
    
def state(actions, gen=0, pactive=True, undo=False):
    return dict(locals())
