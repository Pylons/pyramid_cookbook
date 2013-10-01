import unittest

class TestEvolutionManager(unittest.TestCase):
    def _makeOne(self, context, registry, txn):
        from .. import EvolutionManager
        return EvolutionManager(context, registry, txn)

    def test_ctor_real_txn_module(self):
        import transaction
        inst = self._makeOne(None, None, None)
        self.assertEqual(inst.transaction, transaction)

    def test_ctor_provided_txn_module(self):
        txn = DummyTransaction()
        inst = self._makeOne(None, None, txn)
        self.assertEqual(inst.transaction, txn)

    def test_get_zodb_root(self):
        root = DummyRoot()
        inst = self._makeOne(root, None, None)
        zodb_root = inst.get_zodb_root()
        self.assertEqual(zodb_root, root._p_jar._root)

    def test_get_finished_steps(self):
        from .. import FINISHED_KEY
        root = DummyRoot()
        inst = self._makeOne(root, None, None)
        steps = inst.get_finished_steps()
        self.assertEqual(steps, root._p_jar._root[FINISHED_KEY])

    def test_get_finished_steps_by_value(self):
        root = DummyRoot()
        inst = self._makeOne(root, None, None)
        inst.add_finished_step('abc')
        inst.add_finished_step('def')
        steps = inst.get_finished_steps_by_value()
        self.assertEqual(list(x[1] for x in steps), ['abc', 'def'])

    def test_add_finished_step(self):
        from .. import FINISHED_KEY
        root = DummyRoot()
        inst = self._makeOne(root, None, None)
        inst.add_finished_step('foo')
        steps = root._p_jar._root[FINISHED_KEY]
        self.assertTrue('foo' in steps)

    def test_remove_finished_step(self):
        root = DummyRoot()
        inst = self._makeOne(root, None, None)
        steps = inst.get_finished_steps()
        steps['foo'] = 1
        inst.remove_finished_step('foo')
        self.assertFalse('foo' in steps)

    def test_get_unifinished_steps_no_utility(self):
        registry = DummyRegistry(None)
        inst = self._makeOne(None, registry, None)
        result = inst.get_unfinished_steps()
        self.assertEqual(list(result), [])
        
    def test_get_unifinished_steps(self):
        steps = DummySteps(
            [(None, ('foo', None)),
             (None, ('bar', None))]
            )
        root = DummyRoot()
        registry = DummyRegistry(steps)
        inst = self._makeOne(root, registry, None)
        finished = inst.get_finished_steps()
        finished['foo'] = 1
        result = inst.get_unfinished_steps()
        self.assertEqual(list(result), [('bar', None)])

    def test_mark_unfinished_as_finished(self):
        steps = DummySteps(
            [(None, ('foo', None)),
             (None, ('bar', None))]
            )
        root = DummyRoot()
        registry = DummyRegistry(steps)
        inst = self._makeOne(root, registry, None)
        finished = inst.get_finished_steps()
        finished['foo'] = 1
        inst.mark_unfinished_as_finished()
        self.assertEqual(list(sorted(finished)), ['bar', 'foo'])

    def test_evolve_commit_false(self):
        root = DummyRoot()
        txn = DummyTransaction()
        inst = self._makeOne(root, None, txn)
        def func(context):
            self.assertEqual(context, root)
        inst.get_unfinished_steps = lambda *arg: [('name', func)]
        log = []
        inst.out = log.append
        result = inst.evolve(False)
        self.assertEqual(log, ['Executing evolution step name'])
        self.assertEqual(result, ['name'])
        self.assertEqual(txn.committed, 1)
        self.assertEqual(txn.begun, 1)
        self.assertEqual(txn.notes, [])
        self.assertEqual(txn.was_aborted, True)

    def test_evolve_commit_true(self):
        root = DummyRoot()
        txn = DummyTransaction()
        inst = self._makeOne(root, None, txn)
        def func(context):
            self.assertEqual(context, root)
        inst.get_unfinished_steps = lambda *arg: [('name', func)]
        log = []
        inst.out = log.append
        result = inst.evolve(True)
        self.assertEqual(log, ['Executing evolution step name'])
        self.assertEqual(result, ['name'])
        self.assertEqual(txn.committed, 2)
        self.assertEqual(txn.begun, 1)
        self.assertEqual(txn.notes, ['Executed evolution step name'])
        self.assertEqual(txn.was_aborted, False)

class Test_mark_unfinished_as_finished(unittest.TestCase):
    def _callFUT(self, app_root, registry, t):
        from .. import mark_unfinished_as_finished
        return mark_unfinished_as_finished(app_root, registry, t)

    def test_it(self):
        from .. import FINISHED_KEY
        steps = DummySteps(
            [(None, ('foo', None)),
             (None, ('bar', None))]
            )
        root = DummyRoot()
        registry = DummyRegistry(steps)
        txn = DummyTransaction()
        self._callFUT(root, registry, txn)
        self.assertEqual(list(sorted(root._p_jar._root[FINISHED_KEY])),
                         ['bar', 'foo'])

class Test_add_evolution_step(unittest.TestCase):
    def _callFUT(self, config, *arg, **kw):
        from .. import add_evolution_step
        return add_evolution_step(config, *arg, **kw)

    def test_simple(self):
        from substanced.interfaces import IEvolutionSteps
        registry = DummyRegistry(None)
        config = DummyConfig(registry)
        self._callFUT(config, dummystep)
        self.assertEqual(len(config.actions), 1)
        action = config.actions[0]
        self.assertEqual(
            action['discriminator'],
            ('evolution step',
             'substanced.evolution.tests.test_evolution.dummystep')
            )
        self.assertEqual(
            action['introspectables'],
            ({'after': None,
              'name': 'substanced.evolution.tests.test_evolution.dummystep',
              'func': dummystep,
              'before': None},)
            )
        action['register']()
        utility, iface = config.registry.registered
        self.assertEqual(utility.__class__.__name__,
                         'TopologicalSorter')
        self.assertEqual(
            utility.names,
            ['substanced.evolution.tests.test_evolution.dummystep'])
        self.assertEqual(iface, IEvolutionSteps)

    def test_with_before_and_after_strings(self):
        from substanced.interfaces import IEvolutionSteps
        registry = DummyRegistry(None)
        config = DummyConfig(registry)
        self._callFUT(config, dummystep, before='foo', after='bar')
        self.assertEqual(len(config.actions), 1)
        action = config.actions[0]
        self.assertEqual(
            action['discriminator'],
            ('evolution step',
             'substanced.evolution.tests.test_evolution.dummystep')
            )
        self.assertEqual(
            action['introspectables'],
            ({'after': 'bar',
              'name': 'substanced.evolution.tests.test_evolution.dummystep',
              'func': dummystep,
              'before': 'foo'},)
            )
        action['register']()
        utility, iface = config.registry.registered
        self.assertEqual(utility.__class__.__name__,
                         'TopologicalSorter')
        self.assertEqual(
            utility.names,
            ['substanced.evolution.tests.test_evolution.dummystep'])
        self.assertEqual(iface, IEvolutionSteps)

    def test_with_before_and_after_funcs(self):
        from substanced.interfaces import IEvolutionSteps
        registry = DummyRegistry(None)
        config = DummyConfig(registry)
        self._callFUT(config, dummystep, before=dummybefore, after=dummyafter)
        self.assertEqual(len(config.actions), 1)
        action = config.actions[0]
        self.assertEqual(
            action['discriminator'],
            ('evolution step',
             'substanced.evolution.tests.test_evolution.dummystep')
            )
        self.assertEqual(
            action['introspectables'],
            ({'after': 'substanced.evolution.tests.test_evolution.dummyafter',
              'name': 'substanced.evolution.tests.test_evolution.dummystep',
              'func': dummystep,
              'before': 'substanced.evolution.tests.test_evolution.dummybefore'},
             )
            )
        action['register']()
        utility, iface = config.registry.registered
        self.assertEqual(utility.__class__.__name__,
                         'TopologicalSorter')
        self.assertEqual(
            utility.names,
            ['substanced.evolution.tests.test_evolution.dummystep'])
        self.assertEqual(iface, IEvolutionSteps)

    def test_with_custom_name(self):
        from substanced.interfaces import IEvolutionSteps
        registry = DummyRegistry(None)
        config = DummyConfig(registry)
        self._callFUT(config, dummystep, name='fred')
        self.assertEqual(len(config.actions), 1)
        action = config.actions[0]
        self.assertEqual(
            action['discriminator'],
            ('evolution step',
             'fred')
            )
        self.assertEqual(
            action['introspectables'],
            ({'after': None,
              'name': 'fred',
              'func': dummystep,
              'before': None},
             )
            )
        action['register']()
        utility, iface = config.registry.registered
        self.assertEqual(utility.__class__.__name__,
                         'TopologicalSorter')
        self.assertEqual(
            utility.names,
            ['fred'])
        self.assertEqual(iface, IEvolutionSteps)

def dummystep(root): pass

def dummybefore(root): pass

def dummyafter(root): pass
   

class DummyTransaction(object):
    def __init__(self):
        self.begun = 0
        self.committed = 0
        self.notes = []
        self.was_aborted = False

    def begin(self):
        self.begun += 1

    def commit(self):
        self.committed += 1

    def note(self, msg):
        self.notes.append(msg)

    def get(self):
        return self

    def abort(self):
        self.was_aborted = True


class DummyJar(object):
    def __init__(self):
        self._root = {}
    def root(self):
        return self._root

class DummyRoot(object):
    def __init__(self):
        self._p_jar = DummyJar()
        
class DummyRegistry(object):
    def __init__(self, utility):
        self.utility = utility

    def queryUtility(self, iface):
        return self.utility

    def registerUtility(self, utility, iface):
        self.registered = utility, iface

class DummySteps(object):
    def __init__(self, result):
        self.result = result

    def sorted(self):
        return self.result

class DummyConfig(object):
    def __init__(self, registry):
        self.registry = registry
        self.actions = []
        
    def object_description(self, func):
        return func.__name__

    def introspectable(self, title, discriminator, desc, titles):
        self.intr = {}
        return self.intr

    def action(self, discriminator, register, introspectables):
        self.actions.append(
            {'discriminator':discriminator,
             'register':register,
             'introspectables':introspectables}
            )
