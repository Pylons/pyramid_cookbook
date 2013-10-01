import unittest
from pyramid import testing

class AuditLogEntryTests(unittest.TestCase):
    def test_it(self):
        from .. import AuditLogEntry
        entry = AuditLogEntry('name', 'oid', 'payload', 'timestamp')
        self.assertEqual(entry.name, 'name')
        self.assertEqual(entry.oid, 'oid')
        self.assertEqual(entry.payload, 'payload')
        self.assertEqual(entry.timestamp, 'timestamp')

class AuditLogTests(unittest.TestCase):
    def _makeOne(self, max_layers=2, layer_size=2, entries=None):
        from .. import AuditLog
        return AuditLog(max_layers, layer_size, entries=entries)

    def test_add(self):
        import json
        entries = DummyAppendStack()
        inst = self._makeOne(entries=entries)
        inst.add('name', 1, a=1)
        self.assertEqual(len(entries.pushed), 1)
        pushed = entries.pushed[0]
        self.assertTrue(pushed.timestamp)
        self.assertEqual(pushed.oid, 1)
        self.assertEqual(pushed.name, 'name')
        payload = json.loads(pushed.payload)
        self.assertEqual(payload['a'], 1)

    def test_newer(self):
        entry = DummyAuditLogEntry()
        entries = DummyAppendStack([(0, 0, entry)])
        inst = self._makeOne(entries=entries)
        result = list(inst.newer(0, 0))
        self.assertEqual(result, [(0, 0, entry)])
        
    def test_newer_with_oid_filter(self):
        entry = DummyAuditLogEntry()
        entries = DummyAppendStack([(0, 0, entry)])
        inst = self._makeOne(entries=entries)
        result = list(inst.newer(0, 0, 2))
        self.assertEqual(result, [])

    def test_newer_with_oid_multifilter(self):
        entry = DummyAuditLogEntry()
        entries = DummyAppendStack([(0, 0, entry)])
        inst = self._makeOne(entries=entries)
        result = list(inst.newer(0, 0, [1, 2]))
        self.assertEqual(result, [(0, 0, entry)])

    def test_latest_id(self):
        entries = DummyAppendStack()
        inst = self._makeOne(entries=entries)
        self.assertEqual(inst.latest_id(), (0, 0))

    def test___len__(self):
        entry = DummyAuditLogEntry()
        entries = DummyAppendStack([(0, 0, entry)])
        inst = self._makeOne(entries=entries)
        result = len(inst)
        self.assertEqual(result, 1)

    def test___bool__(self):
        inst = self._makeOne()
        result = bool(inst)
        self.assertEqual(result, True)

    def test___iter__(self):
        entry = DummyAuditLogEntry()
        entries = DummyAppendStack([(0, 0, entry)])
        inst = self._makeOne(entries=entries)
        result = list(inst)
        self.assertEqual(result, [(0, 0, entry)])
        
class LayerTests(unittest.TestCase):

    def _getTargetClass(self):
        from .. import Layer
        return Layer

    def _makeOne(self, *args, **kw):
        return self._getTargetClass()(*args, **kw)

    def test_ctor_defaults(self):
        layer = self._makeOne()
        self.assertEqual(layer._max_length, 100)
        self.assertTrue(type(layer._stack) is list)
        self.assertEqual(layer._generation, 0)

    def test_ctor_w_positional(self):
        layer = self._makeOne(4, 14)
        self.assertEqual(layer._max_length, 4)
        self.assertTrue(type(layer._stack) is list)
        self.assertEqual(layer._generation, 14)

    def test_ctor_w_max_length(self):
        layer = self._makeOne(max_length=14)
        self.assertEqual(layer._max_length, 14)

    def test_ctor_w_generation(self):
        layer = self._makeOne(generation=12)
        self.assertEqual(layer._generation, 12)

    def test___iter___empty(self):
        layer = self._makeOne()
        self.assertEqual(list(layer), [])

    def test_newer_empty(self):
        layer = self._makeOne()
        self.assertEqual(list(layer.newer(0)), [])


    def test___iter___filled(self):
        layer = self._makeOne()
        OBJ1 = object()
        OBJ2 = object()
        OBJ3 = object()
        layer.push(OBJ1)
        layer.push(OBJ2)
        layer.push(OBJ3)
        self.assertEqual(list(layer), [(0, OBJ1), (1, OBJ2), (2, OBJ3)])

    def test_newer_miss(self):
        layer = self._makeOne()
        layer.push(object())
        self.assertEqual(list(layer.newer(0)), [])

    def test_newer_hit(self):
        layer = self._makeOne()
        OBJ1 = object()
        OBJ2 = object()
        OBJ3 = object()
        layer.push(OBJ1)
        layer.push(OBJ2)
        layer.push(OBJ3)
        self.assertEqual(list(layer.newer(0)),
                         [(1, OBJ2), (2, OBJ3)])

    def test_push_one(self):
        layer = self._makeOne()
        OBJ = object()
        layer.push(OBJ)
        self.assertEqual(list(layer), [(0, OBJ)])

    def test_push_many(self):
        layer = self._makeOne()
        OBJ1, OBJ2, OBJ3 = object(), object(), object()
        layer.push(OBJ1)
        layer.push(OBJ2)
        layer.push(OBJ3)
        self.assertEqual(list(layer), [(0, OBJ1),
                                       (1, OBJ2),
                                       (2, OBJ3),
                                      ])

    def test_push_overflow(self):
        from .. import LayerFull
        layer = self._makeOne(2)
        OBJ1, OBJ2, OBJ3 = object(), object(), object()
        layer.push(OBJ1)
        layer.push(OBJ2)
        self.assertRaises(LayerFull, layer.push, OBJ3)
        self.assertEqual(list(layer), [(0, OBJ1),
                                       (1, OBJ2),
                                      ])


class AppendStackTests(unittest.TestCase):

    def _getTargetClass(self):
        from .. import AppendStack
        return AppendStack

    def _makeOne(self, *args, **kw):
        return self._getTargetClass()(*args, **kw)

    def test_ctor_defaults(self):
        stack = self._makeOne()
        self.assertEqual(stack._max_layers, 10)
        self.assertEqual(stack._max_length, 100)

    def test_ctor_w_max_layers(self):
        stack = self._makeOne(max_layers=37)
        self.assertEqual(stack._max_layers, 37)

    def test_ctor_w_max_length(self):
        stack = self._makeOne(max_length=14)
        self.assertEqual(stack._max_length, 14)

    def test___iter___empty(self):
        stack = self._makeOne()
        self.assertEqual(list(stack), [])

    def test___len__(self):
        inst = self._makeOne()
        result = len(inst)
        self.assertEqual(result, 0)

    def test___bool__(self):
        inst = self._makeOne()
        result = bool(inst)
        self.assertEqual(result, True)
        
    def test_newer_empty(self):
        stack = self._makeOne()
        self.assertEqual(list(stack.newer(0, 0)), [])

    def test_newer_miss(self):
        stack = self._makeOne()
        stack.push(object())
        self.assertEqual(list(stack.newer(0, 0)), [])

    def test_newer_hit(self):
        stack = self._makeOne()
        OBJ1 = object()
        OBJ2 = object()
        OBJ3 = object()
        stack.push(OBJ1)
        stack.push(OBJ2)
        stack.push(OBJ3)
        result = list(stack.newer(0, 0))
        self.assertEqual(result, [(0, 1, OBJ2), (0, 2, OBJ3)])

    def test_newer_hit_across_layers(self):
        stack = self._makeOne(max_length=2)
        OBJ1 = object()
        OBJ2 = object()
        OBJ3 = object()
        stack.push(OBJ1)
        stack.push(OBJ2)
        stack.push(OBJ3)
        result = list(stack.newer(0, 0))
        self.assertEqual(result, [(0, 1, OBJ2), (1, 0, OBJ3)])

    def test_push_one(self):
        stack = self._makeOne()
        OBJ = object()
        stack.push(OBJ)
        self.assertEqual(list(stack), [(0, 0, OBJ)])
        self.assertEqual(len(stack._layers), 1)

    def test_push_many(self):
        stack = self._makeOne(max_length=2)
        OBJ1, OBJ2, OBJ3 = object(), object(), object()
        stack.push(OBJ1)
        stack.push(OBJ2)
        stack.push(OBJ3)
        self.assertEqual(
            list(stack), [(0, 0, OBJ1), (0, 1, OBJ2), (1, 0, OBJ3)]
            )
        self.assertEqual(len(stack._layers), 2)
        self.assertEqual(stack._layers[0]._generation, 0)
        self.assertEqual(stack._layers[1]._generation, 1)

    def test_push_trimming_layers(self):
        stack = self._makeOne(max_layers=4)
        for obj in range(1001):
            stack.push(obj)
        found = list(stack)
        self.assertEqual(len(found), 301)
        self.assertEqual(found[0], (7, 0, 700))
        self.assertEqual(found[-1], (10, 0, 1000))
        self.assertEqual(len(stack._layers), 4)
        self.assertEqual(stack._layers[0]._generation, 7)
        self.assertEqual(stack._layers[1]._generation, 8)
        self.assertEqual(stack._layers[2]._generation, 9)
        self.assertEqual(stack._layers[3]._generation, 10)

    def test_push_trimming_layers_with_archive_utility(self):
        _pruned = {}
        def _prune(generation, items):
            _pruned[generation] = items
        stack = self._makeOne(max_layers=4)
        for obj in range(1001):
            stack.push(obj, pruner=_prune)
        found = list(stack)
        self.assertEqual(len(found), 301)
        self.assertEqual(found[0], (7, 0, 700))
        self.assertEqual(found[-1], (10, 0, 1000))
        self.assertEqual(len(stack._layers), 4)
        self.assertEqual(stack._layers[0]._generation, 7)
        self.assertEqual(stack._layers[1]._generation, 8)
        self.assertEqual(stack._layers[2]._generation, 9)
        self.assertEqual(stack._layers[3]._generation, 10)
        self.assertEqual(len(_pruned), 7)
        self.assertEqual(_pruned[0], list(range(0, 100)))
        self.assertEqual(_pruned[1], list(range(100, 200)))
        self.assertEqual(_pruned[2], list(range(200, 300)))
        self.assertEqual(_pruned[3], list(range(300, 400)))
        self.assertEqual(_pruned[4], list(range(400, 500)))
        self.assertEqual(_pruned[5], list(range(500, 600)))
        self.assertEqual(_pruned[6], list(range(600, 700)))

    def test___getstate___empty(self):
        stack = self._makeOne()
        self.assertEqual(stack.__getstate__(), (10, 100, [(0, [])]))

    def test___getstate___filled(self):
        stack = self._makeOne(2, 3)
        for i in range(10):
            stack.push(i)
        self.assertEqual(stack.__getstate__(),
                        (2, 3, [(2, [6, 7, 8]), (3, [9])])
                         )

    def test___setstate___(self):
        stack = self._makeOne()
        STATE = (2,                 # _max_layers
                 3,                 # _max_length
                 [(2, [9]),        # _layers[0] as (generation, list)
                  (3, [6, 7, 8]),  # _layers[1] as (generation, list)
                 ],
                )
        stack.__setstate__(STATE)
        self.assertEqual(stack._max_layers, 2)
        self.assertEqual(stack._max_length, 3)
        self.assertEqual(list(stack), [(2, 0, 9),
                                       (3, 0, 6),
                                       (3, 1, 7),
                                       (3, 2, 8),
                                      ])

    def test__p_resolveConflict_mismatched_max_layers(self):
        from ZODB.POSException import ConflictError
        O_STATE = (2,                 # _max_layers
                   3,                 # _max_length
                   [
                    (2, [6, 7, 8]),  # _layers[0] as (generation, list)
                    (3, [9]),        # _layers[1] as (generation, list)
                   ],
                )
        C_STATE = (2,                 # _max_layers
                   3,                 # _max_length
                   [
                    (2, [6, 7, 8]),  # _layers[0] as (generation, list)
                    (3, [9]),        # _layers[1] as (generation, list)
                   ],
                )
        N_STATE = (3,                 # _max_layers
                   3,                 # _max_length
                   [
                    (2, [6, 7, 8]),  # _layers[0] as (generation, list)
                    (3, [9]),        # _layers[1] as (generation, list)
                   ],
                )
        stack = self._makeOne()
        self.assertRaises(ConflictError, stack._p_resolveConflict,
                          O_STATE, C_STATE, N_STATE)

    def test__p_resolveConflict_mismatched_max_length(self):
        from ZODB.POSException import ConflictError
        O_STATE = (2,                 # _max_layers
                   3,                 # _max_length
                   [
                    (2, [6, 7, 8]),  # _layers[0] as (generation, list)
                    (3, [9]),        # _layers[1] as (generation, list)
                   ],
                )
        C_STATE = (2,                 # _max_layers
                   3,                 # _max_length
                   [
                    (2, [6, 7, 8]),  # _layers[0] as (generation, list)
                    (3, [9]),        # _layers[1] as (generation, list)
                   ],
                )
        N_STATE = (2,                 # _max_layers
                   2,                 # _max_length
                   [
                    (2, [6, 7, 8]),  # _layers[0] as (generation, list)
                    (3, [9]),        # _layers[1] as (generation, list)
                   ],
                )
        stack = self._makeOne()
        self.assertRaises(ConflictError, stack._p_resolveConflict,
                          O_STATE, C_STATE, N_STATE)

    def test__p_resolveConflict_old_latest_commited_earliest(self):
        from ZODB.POSException import ConflictError
        O_STATE = (2,                 # _max_layers
                   3,                 # _max_length
                   [
                    (2, [6, 7, 8]),  # _layers[0] as (generation, list)
                    (3, [9]),        # _layers[1] as (generation, list)
                   ],
                )
        C_STATE = (2,                 # _max_layers
                   3,                 # _max_length
                   [
                    (4, [26, 27, 28]),  # _layers[0] as (generation, list)
                    (5, [29]),        # _layers[1] as (generation, list)
                   ],
                )
        N_STATE = (2,                 # _max_layers
                   3,                 # _max_length
                   [
                    (2, [6, 7, 8]),  # _layers[0] as (generation, list)
                    (3, [9, 10]),    # _layers[1] as (generation, list)
                   ],
                )
        stack = self._makeOne()
        self.assertRaises(ConflictError, stack._p_resolveConflict,
                          O_STATE, C_STATE, N_STATE)

    def test__p_resolveConflict_old_latest_new_earliest(self):
        from ZODB.POSException import ConflictError
        O_STATE = (2,                 # _max_layers
                   3,                 # _max_length
                   [
                    (2, [6, 7, 8]),  # _layers[0] as (generation, list)
                    (3, [9]),        # _layers[1] as (generation, list)
                   ],
                )
        C_STATE = (2,                 # _max_layers
                   3,                 # _max_length
                   [
                    (2, [6, 7, 8]),  # _layers[0] as (generation, list)
                    (3, [9, 10]),    # _layers[1] as (generation, list)
                   ],
                )
        N_STATE = (2,                 # _max_layers
                   3,                 # _max_length
                   [
                    (4, [26, 27, 28]),  # _layers[0] as (generation, list)
                    (5, [29]),        # _layers[1] as (generation, list)
                   ],
                )
        stack = self._makeOne()
        self.assertRaises(ConflictError, stack._p_resolveConflict,
                          O_STATE, C_STATE, N_STATE)

    def test__p_resolveConflict_no_added_layers(self):
        O_STATE = (2,                 # _max_layers
                   3,                 # _max_length
                   [
                    (2, [6, 7, 8]),  # _layers[0] as (generation, list)
                    (3, [9]),        # _layers[1] as (generation, list)
                   ],
                )
        C_STATE = (2,                 # _max_layers
                   3,                 # _max_length
                   [
                    (2, [6, 7, 8]),  # _layers[0] as (generation, list)
                    (3, [9, 10]),    # _layers[1] as (generation, list)
                   ],
                )
        N_STATE = (2,                 # _max_layers
                   3,                 # _max_length
                   [
                    (2, [6, 7, 8]),  # _layers[0] as (generation, list)
                    (3, [9, 11]),    # _layers[1] as (generation, list)
                   ],
                )
        M_STATE = (2,                 # _max_layers
                   3,                 # _max_length
                   [
                    (2, [6, 7, 8]),  # _layers[0] as (generation, list)
                    (3, [9, 10, 11]),# _layers[1] as (generation, list)
                   ],
                )
        stack = self._makeOne()
        merged = stack._p_resolveConflict(O_STATE, C_STATE, N_STATE)
        self.assertEqual(merged, M_STATE)

    def test__p_resolveConflict_added_committed_layer(self):
        O_STATE = (2,                 # _max_layers
                   3,                 # _max_length
                   [
                    (2, [6, 7, 8]),  # _layers[0] as (generation, list)
                    (3, [9]),        # _layers[1] as (generation, list)
                   ],
                )
        C_STATE = (2,                 # _max_layers
                   3,                 # _max_length
                   [
                    (3, [9, 10, 11]),# _layers[0] as (generation, list)
                    (4, [12]),       # _layers[1] as (generation, list)
                   ],
                )
        N_STATE = (2,                 # _max_layers
                   3,                 # _max_length
                   [
                    (2, [6, 7, 8]),  # _layers[0] as (generation, list)
                    (3, [9, 13]),    # _layers[1] as (generation, list)
                   ],
                )
        M_STATE = (2,                 # _max_layers
                   3,                 # _max_length
                   [
                    (3, [9, 10, 11]),# _layers[0] as (generation, list)
                    (4, [12, 13]),   # _layers[1] as (generation, list)
                   ],
                )
        stack = self._makeOne()
        merged = stack._p_resolveConflict(O_STATE, C_STATE, N_STATE)
        self.assertEqual(merged, M_STATE)

    def test__p_resolveConflict_added_new_layer(self):
        O_STATE = (2,                 # _max_layers
                   3,                 # _max_length
                   [
                    (2, [6, 7, 8]),  # _layers[0] as (generation, list)
                    (3, [9]),        # _layers[1] as (generation, list)
                   ],
                )
        C_STATE = (2,                 # _max_layers
                   3,                 # _max_length
                   [
                    (2, [6, 7, 8]),  # _layers[0] as (generation, list)
                    (3, [9, 10]),    # _layers[1] as (generation, list)
                   ],
                )
        N_STATE = (2,                 # _max_layers
                   3,                 # _max_length
                   [
                    (3, [9, 11, 12]),# _layers[0] as (generation, list)
                    (4, [13, 14]),   # _layers[1] as (generation, list)
                   ],
                )
        M_STATE = (2,                 # _max_layers
                   3,                 # _max_length
                   [
                    (3, [9, 10, 11]),# _layers[0] as (generation, list)
                    (4, [12, 13, 14]),# _layers[1] as (generation, list)
                   ],
                )
        stack = self._makeOne()
        merged = stack._p_resolveConflict(O_STATE, C_STATE, N_STATE)
        self.assertEqual(merged, M_STATE)

class Test_set_auditlog(unittest.TestCase):
    def _callFUT(self, context):
        from .. import set_auditlog
        return set_auditlog(context)
    
    def test_it_keyerror(self):
        conn = DummyConnection(KeyError)
        context = testing.DummyResource()
        context._p_jar = conn
        self.assertEqual(self._callFUT(context), None)

    def test_it_auditlog_exists(self):
        root = {'auditlog':True}
        conn = DummyConnection(root=root)
        context = testing.DummyResource()
        context._p_jar = conn
        self.assertEqual(self._callFUT(context), None)
        self.assertEqual(root['auditlog'], True)

    def test_it_auditlog_notexists(self):
        root = {}
        conn = DummyConnection(root=root)
        context = testing.DummyResource()
        context._p_jar = conn
        self.assertEqual(self._callFUT(context), None)
        self.assertTrue('auditlog' in root)
        
class DummyConnection(object):
    def __init__(self, conn=None, root=None):
        if root is None:
            root = {}
        self._conn = conn
        self._root = root

    def get_connection(self, name):
        if self._conn is KeyError:
            raise KeyError
        return self

    def root(self):
        return self._root


class DummyLayer(object):
    _generation = 0
    _stack = (1,)

class DummyAppendStack(object):
    def __init__(self, result=None):
        self.pushed = []
        self.result = result
        self._layers = [DummyLayer()]

    def __len__(self):
        return len(self.result)

    def __iter__(self):
        return iter(self.result)
        
    def push(self, entry):
        self.pushed.append(entry)

    def newer(self, generation, index_id):
        return self.result

class DummyAuditLogEntry(object):
    oid = 1
    
