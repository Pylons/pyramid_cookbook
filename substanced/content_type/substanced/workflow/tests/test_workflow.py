import unittest
import mock

from pyramid import testing

class WorkflowTests(unittest.TestCase):

    def _getTargetClass(self):
        from substanced.workflow import Workflow
        return Workflow

    def _makeOne(self, initial_state='pending', type='basic'):
        klass = self._getTargetClass()
        return klass(initial_state, type)

    def _makePopulated(self, state_callback=None, transition_callback=None):
        sm = self._makeOne()
        sm._states['pending'] = {'callback': state_callback}
        sm._states['published'] = {'callback': state_callback}
        sm._states['private'] = {'callback': state_callback}
        tdata = sm._transitions
        tdata['publish'] = dict(name='publish',
                                from_state='pending',
                                to_state='published',
                                callback=transition_callback)
        tdata['reject'] = dict(name='reject',
                               from_state='pending',
                               to_state='private',
                               callback=transition_callback)
        tdata['retract'] = dict(name='retract',
                                from_state='published',
                                to_state='pending',
                                callback=transition_callback)
        tdata['submit'] = dict(name='submit',
                               from_state='private',
                               to_state='pending',
                               callback=transition_callback)
        return sm

    def _makePopulatedOverlappingTransitions(
            self, state_callback=None, transition_callback=None):
        sm = self._makePopulated(state_callback, transition_callback)

        sm._transitions['submit2'] = dict(
            name='submit2',
            from_state='private',
            to_state='pending',
            callback=transition_callback,
            )
        return sm

    @mock.patch('substanced.workflow.has_permission')
    def test_transition_to_state_two_transitions_second_works(
            self, mock_has_permission):
        args = []
        def dummy(content, **info):
            args.append((content, info))

        sm = self._makePopulatedOverlappingTransitions(
            transition_callback=dummy,
            )

        sm._transitions['submit']['permission'] = 'forbidden'
        sm._transitions['submit2']['permission'] = 'allowed'

        mock_has_permission.side_effect = lambda p, c, r: p != 'forbidden'
        ob = DummyContent()
        ob.__workflow_state__ = {'basic': 'private'}
        sm.transition_to_state(ob, object(), 'pending')
        self.assertEqual(len(args), 1)
        self.assertEqual(args[0][1]['transition']['name'], 'submit2')

    @mock.patch('substanced.workflow.has_permission')
    def test_transition_to_state_two_transitions_none_works(
            self, mock_has_permission):
        callback_args = []
        def dummy(content, info):  # pragma NO COVER
            callback_args.append((content, info))

        sm = self._makePopulatedOverlappingTransitions(
            transition_callback=dummy,
            )

        sm._transitions['submit']['permission'] = 'forbidden1'
        sm._transitions['submit2']['permission'] = 'forbidden2'

        ob = DummyContent()
        ob.__workflow_state__ = {'basic': 'private'}
        request = object()
        from substanced.workflow import WorkflowError
        mock_has_permission.return_value = False
        self.assertRaises(WorkflowError, sm.transition_to_state,
                          ob, request, 'pending')
        self.assertEqual(len(callback_args), 0)
        pcalls = sorted(mock_has_permission.mock_calls)
        self.assertEqual(pcalls[0], mock.call('forbidden1', ob, request))
        self.assertEqual(pcalls[1], mock.call('forbidden2', ob, request))

    def test_class_conforms_to_IWorkflow(self):
        from zope.interface.verify import verifyClass
        from substanced.interfaces import IWorkflow
        verifyClass(IWorkflow, self._getTargetClass())

    def test_instance_conforms_to_IWorkflow(self):
        from zope.interface.verify import verifyObject
        from substanced.interfaces import IWorkflow
        verifyObject(IWorkflow, self._makeOne())

    def test_has_state_false(self):
        sm = self._makeOne()
        self.assertEqual(sm.has_state(None), False)

    def test_has_state_true(self):
        sm = self._makeOne()
        ob = DummyContent()
        ob.__workflow_state__ = {'basic': 'abc'}
        self.assertEqual(sm.has_state(ob), True)

    def test_state_of_uninitialized(self):
        sm = self._makeOne()
        ob = DummyContent()
        self.assertEqual(sm.state_of(ob), None)

    def test_state_of_initialized(self):
        sm = self._makeOne()
        ob = DummyContent()
        ob.__workflow_state__ = {'basic': 'pending'}
        self.assertEqual(sm.state_of(ob), 'pending')

    def test_state_of_no_workflow_is_None(self):
        sm = self._makeOne()
        sm.add_state('pending')
        ob = DummyContent()
        self.assertEqual(sm.state_of(ob), None)

    def test_state_of_nondefault(self):
        sm = self._makeOne()
        ob = DummyContent()
        ob.__workflow_state__ = {'basic': 'pending'}
        self.assertEqual(sm.state_of(ob), 'pending')

    def test_state_of_None_is_None(self):
        sm = self._makeOne()
        self.assertEqual(sm.state_of(None), None)

    def test_add_state_state_exists(self):
        from substanced.workflow import WorkflowError
        sm = self._makeOne()
        sm._states = {'foo': {'c': 5}}
        self.assertRaises(WorkflowError, sm.add_state, 'foo')

    def test_add_state_info_state_doesntexist(self):
        sm = self._makeOne()
        callback = object()
        sm.add_state('foo', callback, a=1, b=2)
        self.assertEqual(sm._states,
                         {'foo': {'callback': callback, 'a': 1, 'b': 2}})

    def test_add_state_defaults(self):
        sm = self._makeOne()
        sm.add_state('foo')
        self.assertEqual(sm._states, {'foo': {'callback': None}})

    def test_add_state_w_custom_factory(self):
        sm = self._makeOne()
        _THE_STATE = object()
        _called_with = []
        def _factory(*args, **kw):
            _called_with.append((args, kw))
            return _THE_STATE
        sm._state_factory = _factory
        sm.add_state('foo')
        self.assertEqual(sm._states, {'foo': _THE_STATE})
        self.assertEqual(_called_with, [((), {'callback': None})])

    def test_add_transition_transition_name_already_exists(self):
        from substanced.workflow import WorkflowError
        sm = self._makeOne()
        sm.add_state('public')
        sm.add_state('private')
        sm.add_transition('make_public', 'private', 'public', None, a=1)
        self.assertRaises(WorkflowError, sm.add_transition, 'make_public',
                          'private', 'public')

    def test_add_transition_from_state_doesnt_exist(self):
        from substanced.workflow import WorkflowError
        sm = self._makeOne()
        sm.add_state('public')
        self.assertRaises(WorkflowError, sm.add_transition, 'make_public',
                          'private', 'public')

    def test_add_transition_to_state_doesnt_exist(self):
        from substanced.workflow import WorkflowError
        sm = self._makeOne()
        sm.add_state('private')
        self.assertRaises(WorkflowError, sm.add_transition, 'make_public',
                          'private', 'public')

    def test_add_transition(self):
        sm = self._makeOne()
        sm.add_state('public')
        sm.add_state('private')
        sm.add_transition('make_public', 'private', 'public', None, a=1)
        sm.add_transition('make_private', 'public', 'private', None, b=2)
        self.assertEqual(len(sm._transitions), 2)
        make_public = sm._transitions['make_public']
        self.assertEqual(make_public['name'], 'make_public')
        self.assertEqual(make_public['from_state'], 'private')
        self.assertEqual(make_public['to_state'], 'public')
        self.assertEqual(make_public['callback'], None)
        self.assertEqual(make_public['a'], 1)
        make_private = sm._transitions['make_private']
        self.assertEqual(make_private['name'], 'make_private')
        self.assertEqual(make_private['from_state'], 'public')
        self.assertEqual(make_private['to_state'], 'private')
        self.assertEqual(make_private['callback'], None)
        self.assertEqual(make_private['b'], 2)
        self.assertEqual(len(sm._states), 2)

    def test_add_transition_w_custom_factory(self):
        sm = self._makeOne()
        _THE_TRANSITION = object()
        _called_with = []
        def _factory(*args, **kw):
            _called_with.append((args, kw))
            return _THE_TRANSITION
        sm._transition_factory = _factory
        sm.add_state('public')
        sm.add_state('private')
        sm.add_transition('make_public', 'private', 'public', None, a=1)
        self.assertEqual(sm._transitions, {'make_public': _THE_TRANSITION})
        self.assertEqual(_called_with,
                         [((), {'name': 'make_public',
                                'from_state': 'private',
                                'to_state': 'public',
                                'permission': None,
                                'callback': None,
                                'a': 1})])

    def test_check_fails(self):
        from substanced.workflow import WorkflowError
        sm = self._makeOne()
        self.assertRaises(WorkflowError, sm.check)

    def test_check_succeeds(self):
        sm = self._makeOne()
        sm.add_state('pending')
        self.assertEqual(sm.check(), None)

    def test__get_transitions_default_from_state(self):
        import operator
        sm = self._makePopulated()
        ob = DummyContent()
        ob.__workflow_state__ = {'basic': 'pending'}
        result = sorted(sm._get_transitions(ob),
                        key=operator.itemgetter('name'))
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]['name'], 'publish')
        self.assertEqual(result[1]['name'], 'reject')

    def test__get_transitions_overridden_from_state(self):
        sm = self._makePopulated()
        ob = DummyContent()
        result = sm._get_transitions(ob, from_state='private')
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]['name'], 'submit')

    def test__get_transitions_content_has_state(self):
        sm = self._makePopulated()
        ob = DummyContent()
        ob.__workflow_state__ = {'basic': 'published'}
        result = sm._get_transitions(ob)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]['name'], 'retract')

    def test__transition(self):
        args = []
        def dummy(content, **kw):
            args.append((content, kw))
        sm = self._makePopulated(transition_callback=dummy)
        ob = DummyContent()
        ob.__workflow_state__ = {'basic': 'pending'}
        sm._transition(ob, 'publish')
        self.assertEqual(ob.__workflow_state__['basic'], 'published')
        sm._transition(ob, 'retract')
        self.assertEqual(ob.__workflow_state__['basic'], 'pending')
        sm._transition(ob, 'reject')
        self.assertEqual(ob.__workflow_state__['basic'], 'private')
        sm._transition(ob, 'submit')
        self.assertEqual(ob.__workflow_state__['basic'], 'pending')

        self.assertEqual(len(args), 4)
        self.assertEqual(args[0][0], ob)
        info = args[0][1]
        self.assertEqual(info['transition'], {'from_state': 'pending',
                                              'callback': dummy,
                                              'to_state': 'published',
                                              'name': 'publish'})
        self.assertEqual(info['workflow'], sm)
        self.assertEqual(args[1][0], ob)
        info = args[1][1]
        self.assertEqual(info['transition'], {'from_state': 'published',
                                              'callback': dummy,
                                              'to_state': 'pending',
                                              'name': 'retract'})
        self.assertEqual(args[1][0], ob)
        self.assertEqual(args[2][0], ob)
        info = args[2][1]
        self.assertEqual(info['transition'], {'from_state': 'pending',
                                              'callback': dummy,
                                              'to_state': 'private',
                                              'name': 'reject'})
        self.assertEqual(info['workflow'], sm)
        self.assertEqual(args[3][0], ob)
        info = args[3][1]
        self.assertEqual(info['transition'], {'from_state': 'private',
                                              'callback': dummy,
                                              'to_state': 'pending',
                                              'name': 'submit'})
        self.assertEqual(info['workflow'], sm)

    def test__transition_with_state_callback(self):
        def dummy(content, **kw):
            content.info = kw
        sm = self._makePopulated(state_callback=dummy)
        ob = DummyContent()
        ob.__workflow_state__ = {'basic': 'pending'}
        sm._transition(ob, 'publish')
        self.assertEqual(ob.info['transition'],
                         {'from_state': 'pending',
                          'callback': None,
                          'to_state':
                          'published',
                          'name': 'publish'})
        self.assertEqual(ob.info['workflow'], sm)

    def test__transition_with_custom_state_callback(self):
        class _State(dict):
            _called = None
            def __call__(self, content, **kw):
                self._called = (content, kw)
        sm = self._makeOne()
        sm._state_factory = _State
        sm.add_state('pending')
        sm.add_state('published')
        sm.add_transition('publish', 'pending', 'published')
        ob = DummyContent()
        ob.__workflow_state__ = {'basic': 'pending'}
        sm._transition(ob, 'publish')
        called = sm._states['published']._called
        self.assertEqual(called[0], ob)
        self.assertEqual(called[1], {'request': None,
                                     'transition': {'from_state': 'pending',
                                                    'callback': None,
                                                    'to_state': 'published',
                                                    'permission': None,
                                                    'name': 'publish',
                                                   },
                                     'workflow': sm,
                                    })

    def test__transition_error(self):
        sm = self._makeOne(initial_state='pending')
        sm.add_state('pending')
        ob = DummyContent()
        from substanced.workflow import WorkflowError
        self.assertRaises(WorkflowError, sm._transition, ob, 'nosuch')

    def test__transition_to_state_same(self):
        sm = self._makePopulated()
        ob = DummyContent()
        ob.__workflow_state__ = {'basic': 'pending'}
        sm._transition_to_state(ob, 'pending')
        self.assertEqual(ob.__workflow_state__['basic'], 'pending')

    def test__transition_to_state(self):
        args = []
        def dummy(content, **info):
            args.append((content, info))
        sm = self._makePopulated(transition_callback=dummy)
        ob = DummyContent()
        ob.__workflow_state__ = {'basic': 'pending'}
        sm._transition_to_state(ob, 'published')
        self.assertEqual(ob.__workflow_state__['basic'], 'published')
        sm._transition_to_state(ob, 'pending')
        self.assertEqual(ob.__workflow_state__['basic'], 'pending')
        sm._transition_to_state(ob, 'private')
        self.assertEqual(ob.__workflow_state__['basic'], 'private')
        sm._transition_to_state(ob, 'pending')

        self.assertEqual(len(args), 4)
        self.assertEqual(args[0][0], ob)
        info = args[0][1]
        self.assertEqual(info['transition'], {'from_state': 'pending',
                                              'callback': dummy,
                                              'to_state': 'published',
                                              'name': 'publish'})
        self.assertEqual(info['workflow'], sm)
        self.assertEqual(args[1][0], ob)
        info = args[1][1]
        self.assertEqual(info['transition'], {'from_state': 'published',
                                              'callback': dummy,
                                              'to_state': 'pending',
                                              'name': 'retract'})
        self.assertEqual(info['workflow'], sm)
        self.assertEqual(args[2][0], ob)
        info = args[2][1]
        self.assertEqual(info['transition'], {'from_state': 'pending',
                                              'callback': dummy,
                                              'to_state': 'private',
                                              'name': 'reject'})
        self.assertEqual(info['workflow'], sm)
        self.assertEqual(args[3][0], ob)
        info = args[3][1]
        self.assertEqual(info['transition'], {'from_state': 'private',
                                              'callback': dummy,
                                              'to_state': 'pending',
                                              'name': 'submit'})
        self.assertEqual(info['workflow'], sm)

    def test__transition_to_state_error(self):
        sm = self._makeOne(initial_state='pending')
        sm.add_state('pending')
        ob = DummyContent()
        from substanced.workflow import WorkflowError
        self.assertRaises(WorkflowError, sm._transition_to_state, ob,
                          'nosuch')

    def test__transition_to_state_skip_same_false(self):
        sm = self._makeOne(initial_state='pending')
        sm.add_state('pending')
        ob = DummyContent()
        from substanced.workflow import WorkflowError
        self.assertRaises(WorkflowError, sm._transition_to_state, ob, None,
                          'pending', (), False)

    def test__transition_to_state_skip_same_true(self):
        sm = self._makeOne(initial_state='pending')
        ob = DummyContent()
        ob.__workflow_state__ = {}
        ob.__workflow_state__['basic'] = 'pending'
        self.assertEqual(sm._transition_to_state(ob, 'pending', (), True),
                         None)

    def test__state_with_title(self):
        sm = self._makeOne()
        sm.add_state('pending', title='Pending')
        ob = DummyContent()
        ob.__workflow_state__ = {'basic': 'pending'}
        result = sm._get_states(ob)

        state = result[0]
        self.assertEqual(state['initial'], True)
        self.assertEqual(state['current'], True)
        self.assertEqual(state['name'], 'pending')
        self.assertEqual(state['title'], 'Pending')
        self.assertEqual(state['data'], {'callback': None, 'title': 'Pending'})
        self.assertEqual(len(state['transitions']), 0)

    def test__get_states_pending(self):
        from operator import itemgetter
        sm = self._makePopulated()
        ob = DummyContent()
        ob.__workflow_state__ = {'basic': 'pending'}
        result = sorted(sm._get_states(ob), key=itemgetter('name'))
        self.assertEqual(len(result), 3)

        state = result[0]
        self.assertEqual(state['name'], 'pending')
        self.assertEqual(state['initial'], True)
        self.assertEqual(state['current'], True)
        self.assertEqual(state['title'], 'pending')
        self.assertEqual(state['data'], {'callback': None})
        self.assertEqual(len(state['transitions']), 0)

        state = result[1]
        self.assertEqual(state['name'], 'private')
        self.assertEqual(state['initial'], False)
        self.assertEqual(state['current'], False)
        self.assertEqual(state['title'], 'private')
        self.assertEqual(state['data'], {'callback': None})
        self.assertEqual(len(state['transitions']), 1)
        self.assertEqual(state['transitions'][0]['name'], 'reject')

        state = result[2]
        self.assertEqual(state['name'], 'published')
        self.assertEqual(state['initial'], False)
        self.assertEqual(state['current'], False)
        self.assertEqual(state['title'], 'published')
        self.assertEqual(state['data'], {'callback': None})
        self.assertEqual(len(state['transitions']), 1)
        self.assertEqual(state['transitions'][0]['name'], 'publish')

    def test__get_states_published(self):
        from operator import itemgetter
        sm = self._makePopulated()
        ob = DummyContent()
        ob.__workflow_state__ = {'basic': 'published'}
        result = sorted(sm._get_states(ob), key=itemgetter('name'))
        self.assertEqual(len(result), 3)

        state = result[0]
        self.assertEqual(state['name'], 'pending')
        self.assertEqual(state['initial'], True)
        self.assertEqual(state['current'], False)
        self.assertEqual(state['title'], 'pending')
        self.assertEqual(state['data'], {'callback': None})
        self.assertEqual(len(state['transitions']), 1)
        self.assertEqual(state['transitions'][0]['name'], 'retract')

        state = result[1]
        self.assertEqual(state['name'], 'private')
        self.assertEqual(state['initial'], False)
        self.assertEqual(state['current'], False)
        self.assertEqual(state['title'], 'private')
        self.assertEqual(state['data'], {'callback': None})
        self.assertEqual(len(state['transitions']), 0)

        state = result[2]
        self.assertEqual(state['name'], 'published')
        self.assertEqual(state['initial'], False)
        self.assertEqual(state['current'], True)
        self.assertEqual(state['title'], 'published')
        self.assertEqual(state['data'], {'callback': None})
        self.assertEqual(len(state['transitions']), 0)

    def test__get_states_private(self):
        from operator import itemgetter
        sm = self._makePopulated()
        ob = DummyContent()
        ob.__workflow_state__ = {'basic': 'private'}
        result = sorted(sm._get_states(ob), key=itemgetter('name'))
        self.assertEqual(len(result), 3)

        state = result[0]
        self.assertEqual(state['name'], 'pending')
        self.assertEqual(state['initial'], True)
        self.assertEqual(state['current'], False)
        self.assertEqual(state['title'], 'pending')
        self.assertEqual(state['data'], {'callback': None})
        self.assertEqual(len(state['transitions']), 1)
        self.assertEqual(state['transitions'][0]['name'], 'submit')

        state = result[1]
        self.assertEqual(state['name'], 'private')
        self.assertEqual(state['initial'], False)
        self.assertEqual(state['current'], True)
        self.assertEqual(state['title'], 'private')
        self.assertEqual(state['data'], {'callback': None})
        self.assertEqual(len(state['transitions']), 0)

        state = result[2]
        self.assertEqual(state['name'], 'published')
        self.assertEqual(state['initial'], False)
        self.assertEqual(state['current'], False)
        self.assertEqual(state['title'], 'published')
        self.assertEqual(state['data'], {'callback': None})
        self.assertEqual(len(state['transitions']), 0)

    def test_initialize_no_initializer(self):
        sm = self._makeOne(initial_state='pending')
        sm.add_state('pending')
        ob = DummyContent()
        state, msg = sm.initialize(ob)
        self.assertEqual(ob.__workflow_state__['basic'], 'pending')
        self.assertEqual(msg, None)
        self.assertEqual(state, 'pending')

    def test_initialize_with_initializer(self):
        def initializer(content, **kw):
            content.initialized = True
            return 'abc'
        sm = self._makeOne(initial_state='pending')
        sm.add_state('pending', initializer)
        ob = DummyContent()
        state, msg = sm.initialize(ob)
        self.assertEqual(ob.__workflow_state__['basic'], 'pending')
        self.assertEqual(ob.initialized, True)
        self.assertEqual(msg, 'abc')
        self.assertEqual(state, 'pending')

    def test_reset_content_has_no_state(self):
        from persistent.mapping import PersistentMapping
        def callback(content, **kw):
            content.called_back = True
            return '123'
        sm = self._makeOne(initial_state='pending')
        sm.add_state('pending', callback=callback)
        ob = DummyContent()
        state, msg = sm.reset(ob)
        self.assertEqual(ob.__workflow_state__.__class__, PersistentMapping)
        self.assertEqual(ob.__workflow_state__['basic'], 'pending')
        self.assertEqual(ob.called_back, True)
        self.assertEqual(state, 'pending')
        self.assertEqual(msg, '123')

    def test_reset_content_no_callback(self):
        sm = self._makeOne(initial_state='pending')
        sm.add_state('pending',)
        ob = DummyContent()
        state, msg = sm.reset(ob)
        self.assertEqual(ob.__workflow_state__['basic'], 'pending')
        self.assertEqual(state, 'pending')
        self.assertEqual(msg, None)

    def test_reset_content_has_state(self):
        def callback(content, **kw):
            content.called_back = True
            return '123'
        sm = self._makeOne(initial_state='pending')
        sm.add_state('pending')
        sm.add_state('private', callback=callback)
        ob = DummyContent()
        ob.__workflow_state__ = {'basic': 'private'}
        state, msg = sm.reset(ob)
        self.assertEqual(ob.__workflow_state__['basic'], 'private')
        self.assertEqual(ob.called_back, True)
        self.assertEqual(state, 'private')
        self.assertEqual(msg, '123')

    def test_reset_content_has_state_not_in_workflow(self):
        from substanced.workflow import WorkflowError
        sm = self._makeOne(initial_state='pending')
        sm.add_state('pending')
        ob = DummyContent()
        ob.__workflow_state__ = {'basic': 'supersecret'}
        self.assertRaises(WorkflowError, sm.reset, ob)

    def test_transition_permission_is_None(self):
        workflow = self._makeOne()
        transitioned = []
        def append(content, name, context=None, request=None):
            D = {'content': content, 'name': name, 'request': request,
                 'context': context}
            transitioned.append(D)
        workflow._transition = lambda *arg, **kw: append(*arg, **kw)
        content = DummyContent()
        content.__workflow_state__ = {'basic': 'pending'}
        request = object()
        workflow.transition(content, request, 'publish')
        self.assertEqual(len(transitioned), 1)
        transitioned = transitioned[0]
        self.assertEqual(transitioned['content'], content)
        self.assertEqual(transitioned['name'], 'publish')
        self.assertEqual(transitioned['request'], request)
        self.assertEqual(transitioned['context'], None)

    @mock.patch('substanced.workflow.has_permission')
    def test_transition_to_state_not_permissive(self, mock_has_permission):
        mock_has_permission.return_value = False
        workflow = self._makeOne()
        transitioned = []
        def append(content, name, context=None, request=None,
                   skip_same=True):
            D = {'content': content, 'name': name, 'request': request,
                 'context': context, 'skip_same': skip_same}
            transitioned.append(D)
        workflow._transition_to_state = lambda *arg, **kw: append(*arg, **kw)
        request = object()
        content = DummyContent()
        content.__workflow_state__ = {'basic': 'pending'}
        workflow.transition_to_state(content, request, 'published')
        self.assertEqual(len(transitioned), 1)
        transitioned = transitioned[0]
        self.assertEqual(transitioned['content'], content)
        self.assertEqual(transitioned['name'], 'published')
        self.assertEqual(transitioned['request'], request)
        self.assertEqual(transitioned['context'], None)
        self.assertEqual(transitioned['skip_same'], True)

    def test_transition_to_state_request_is_None(self):
        workflow = self._makeOne()
        transitioned = []
        def append(content, name, context=None, request=None,
                   skip_same=True):
            D = {'content': content, 'name': name, 'request': request,
                 'context': context, 'skip_same': skip_same}
            transitioned.append(D)
        workflow._transition_to_state = lambda *arg, **kw: append(*arg, **kw)
        content = DummyContent()
        content.__workflow_state__ = {'basic': 'pending'}
        workflow.transition_to_state(content, None, 'published')
        self.assertEqual(len(transitioned), 1)
        transitioned = transitioned[0]
        self.assertEqual(transitioned['content'], content)
        self.assertEqual(transitioned['name'], 'published')
        self.assertEqual(transitioned['request'], None)
        self.assertEqual(transitioned['context'], None)
        self.assertEqual(transitioned['skip_same'], True)

    def test_transition_to_state_permission_is_None(self):
        workflow = self._makeOne()
        transitioned = []
        def append(content, name, context=None, request=None,
                   skip_same=True):
            D = {'content': content, 'name': name, 'request': request,
                 'context': context, 'skip_same': skip_same}
            transitioned.append(D)
        workflow._transition_to_state = lambda *arg, **kw: append(*arg, **kw)
        content = DummyContent()
        content.__workflow_state__ = {'basic': 'pending'}
        request = object()
        workflow.transition_to_state(content, request, 'published')
        self.assertEqual(len(transitioned), 1)
        transitioned = transitioned[0]
        self.assertEqual(transitioned['content'], content)
        self.assertEqual(transitioned['name'], 'published')
        self.assertEqual(transitioned['request'], request)
        self.assertEqual(transitioned['context'], None)
        self.assertEqual(transitioned['skip_same'], True)

    @mock.patch('substanced.workflow.has_permission')
    def test_get_transitions_permissive(self, mock_has_permission):
        mock_has_permission.return_value = True
        workflow = self._makeOne()
        workflow._get_transitions = \
            lambda *arg, **kw: [{'permission': 'view'}, {}]
        transitions = workflow.get_transitions(None, None, 'private')
        self.assertEqual(len(transitions), 2)
        self.assertEqual(mock_has_permission.mock_calls,
                         [mock.call('view', None, None)])

    @mock.patch('substanced.workflow.has_permission')
    def test_get_transitions_nonpermissive(self, mock_has_permission):
        mock_has_permission.return_value = False
        workflow = self._makeOne()
        workflow._get_transitions = \
            lambda *arg, **kw: [{'permission': 'view'}, {}]
        transitions = workflow.get_transitions(None, 'private')
        self.assertEqual(len(transitions), 1)
        self.assertEqual(mock_has_permission.mock_calls,
                         [mock.call('view', None, 'private')])

    @mock.patch('substanced.workflow.has_permission')
    def test_get_states_permissive(self, mock_has_permission):
        mock_has_permission.return_value = True
        state_info = []
        state_info.append({'transitions': [{'permission': 'view'}, {}]})
        state_info.append({'transitions': [{'permission': 'view'}, {}]})
        workflow = self._makeOne()
        workflow._get_states = lambda *arg, **kw: state_info
        request = object()
        result = workflow.get_states(request, 'whatever')
        self.assertEqual(result, state_info)
        self.assertEqual(mock_has_permission.mock_calls,
                         [mock.call('view', request, 'whatever'),
                          mock.call('view', request, 'whatever')])

    @mock.patch('substanced.workflow.has_permission')
    def test_get_states_nonpermissive(self, mock_has_permission):
        mock_has_permission.return_value = False
        state_info = []
        state_info.append({'transitions': [{'permission': 'view'}, {}]})
        state_info.append({'transitions': [{'permission': 'view'}, {}]})
        workflow = self._makeOne()
        workflow._get_states = lambda *arg, **kw: state_info
        request = object()
        result = workflow.get_states(request, 'whatever')
        self.assertEqual(result, [{'transitions': [{}]},
                                  {'transitions': [{}]}])
        self.assertEqual(mock_has_permission.mock_calls,
                         [mock.call('view', request, 'whatever'),
                          mock.call('view', request, 'whatever')])

    def test_callbackinfo_has_request(self):
        def transition_cb(content, **info):
            self.assertEqual(info['request'], request)
        def state_cb(content, **kw):
            self.assertEqual(kw['request'], request)
        wf = self._makeOne('initial')
        wf.add_state('initial', callback=state_cb)
        wf.add_state('new')
        wf.add_transition('tonew',
                          'initial',
                          'new',
                          callback=transition_cb)
        request = object()
        content = DummyContent()
        wf.initialize(content, request=request)
        wf.transition_to_state(content, request, 'new')

class GetWorkflowTests(unittest.TestCase):

    def setUp(self):
        from substanced.workflow import includeme
        self.config = testing.setUp()
        includeme(self.config)

    def tearDown(self):
        testing.tearDown()

    def _callFUT(self, content_type, type=''):
        from substanced.workflow import get_workflow
        return get_workflow(testing.DummyRequest(), type, content_type)

    def _registerWorkflowList(self, content_type, workflows):
        for wf in workflows:
            wf.type = ''
            self.config.registry.workflow.add(wf, content_type)

    def test_content_type_is_None_no_registered_workflows(self):
        self.assertEqual(self._callFUT(None, ''), None)

    def test_content_type_is_IDefaultWorkflow_no_registered_workflows(self):
        from substanced.interfaces import IDefaultWorkflow
        self.assertEqual(self._callFUT(IDefaultWorkflow, ''), None)

    def test_content_type_is_None_registered_workflow(self):
        from substanced.interfaces import IDefaultWorkflow
        workflow = mock.Mock()
        self._registerWorkflowList(IDefaultWorkflow, [workflow])
        result = self._callFUT(None)
        self.assertEqual(result, workflow)

    def test_content_type_is_class_registered_workflow(self):
        from substanced.interfaces import IDefaultWorkflow
        workflow = mock.Mock()
        self._registerWorkflowList(IDefaultWorkflow, [workflow])
        result = self._callFUT('Folder')
        self.assertEqual(result, workflow)

    def test_content_type_is_IDefaultWorkflow_registered_workflow(self):
        from substanced.interfaces import IDefaultWorkflow
        workflow = mock.Mock()
        self._registerWorkflowList(IDefaultWorkflow, [workflow])
        self.assertEqual(self._callFUT(IDefaultWorkflow),
                         workflow)

    def test_content_type_is_Folder_no_registered_workflows(self):
        self.assertEqual(self._callFUT('Folder', ''), None)

    def test_content_type_is_Folder_finds_default(self):
        from substanced.interfaces import IDefaultWorkflow
        workflow = mock.Mock()
        self._registerWorkflowList(IDefaultWorkflow, [workflow])
        self.assertEqual(self._callFUT('Folder'), workflow)

    def test_content_type_is_Folder_finds_specific(self):
        workflow = mock.Mock()
        self._registerWorkflowList('Folder', [workflow])
        self.assertEqual(self._callFUT('Folder'), workflow)

    def test_content_type_is_Folder_finds_more_specific_first(self):
        from substanced.interfaces import IDefaultWorkflow
        default_workflow = mock.Mock()
        specific_workflow = mock.Mock()
        self._registerWorkflowList('Folder', [specific_workflow])
        self._registerWorkflowList(IDefaultWorkflow, [default_workflow])
        self.assertEqual(
            self._callFUT('Folder'),
            specific_workflow)
        self.assertEqual(
            self._callFUT(None),
            default_workflow)

class add_workflowTests(unittest.TestCase):

    def setUp(self):
        self.config = testing.setUp()
        from substanced.workflow import includeme
        includeme(self.config)

    def tearDown(self):
        testing.tearDown()

    def _callFUT(self, workflow, config, content_types=(None,)):
        from substanced.workflow import add_workflow
        add_workflow(config, workflow, content_types)

    def _makeWorkflow(self):
        from zope.interface import implementer
        from substanced.interfaces import IWorkflow
        @implementer(IWorkflow)
        class _Workflow(object):
            type = 'testing'
            def check(self):
                pass
        return _Workflow()

    def test_add_workflow_doesnt_implement_iworkflow(self):
        config = mock.Mock()
        self.assertRaises(ValueError, self._callFUT, object(), config)

    def test_add_workflow_global(self):
        from substanced.interfaces import IWorkflow
        from substanced.workflow import register_workflow
        config = mock.MagicMock()
        wf = self._makeWorkflow()
        self._callFUT(wf, config)

        self.assertEqual(config.action.mock_calls, [
            mock.call((IWorkflow, None, wf.type),
                      callable=register_workflow,
                      introspectables=(mock.ANY,),
                      order=9999,
                      args=(config, wf, wf.type, None))
        ])

    def test_add_workflow_multi_content_types(self):
        from substanced.interfaces import IWorkflow
        from substanced.workflow import register_workflow
        config = mock.MagicMock()
        wf = self._makeWorkflow()
        self._callFUT(wf, config, content_types=('Folder', 'File'))

        self.assertEqual(config.action.mock_calls, [
            mock.call((IWorkflow, 'Folder', wf.type),
                      callable=register_workflow,
                      introspectables=(mock.ANY,),
                      order=9999,
                      args=(config, wf, wf.type, 'Folder')),
            mock.call((IWorkflow, 'File', wf.type),
                      callable=register_workflow,
                      introspectables=(mock.ANY,),
                      order=9999,
                      args=(config, wf, wf.type, 'File')),
        ])

    def test_add_workflow_check_error(self):
        from pyramid.config import ConfigurationError
        from substanced.workflow import WorkflowError
        config = mock.Mock()
        wf = self._makeWorkflow()
        def _check():
            raise WorkflowError('bogus')
        wf.check = _check
        self.assertRaises(ConfigurationError, self._callFUT, wf, config)

class register_workflowTests(unittest.TestCase):

    def setUp(self):
        self.config = testing.setUp()
        self.config.registry.content = mock.Mock()
        from substanced.workflow import includeme
        includeme(self.config)

    def tearDown(self):
        testing.tearDown()

    def _callFUT(self, config, workflow, type_,
                 content_type=None):
        from substanced.workflow import register_workflow
        workflow.type = type_
        register_workflow(config, workflow, type_, content_type)

    def test_register_workflow_global(self):
        from substanced.interfaces import IDefaultWorkflow
        from substanced._compat import u
        wf = mock.Mock()
        self._callFUT(self.config, wf, 'basic')

        self.assertEqual({'basic': {IDefaultWorkflow: wf}},
                         self.config.registry.workflow.types)
        self.assertEqual({IDefaultWorkflow: {u('basic'): wf}},
                         self.config.registry.workflow.content_types)

    def test_register_workflow_global_skip_if_exists(self):
        from substanced.interfaces import IDefaultWorkflow
        from substanced._compat import u
        wf = mock.Mock()
        self._callFUT(self.config, wf, 'basic')
        self.assertEqual({'basic': {IDefaultWorkflow: wf}},
                         self.config.registry.workflow.types)
        self.assertEqual({IDefaultWorkflow: {u('basic'): wf}},
                         self.config.registry.workflow.content_types)

        self._callFUT(self.config, wf, 'basic')
        self.assertEqual({'basic': {IDefaultWorkflow: wf}},
                         self.config.registry.workflow.types)
        self.assertEqual({IDefaultWorkflow: {u('basic'): wf}},
                         self.config.registry.workflow.content_types)

    def test_register_workflow_two_types(self):
        from substanced._compat import u
        wf = mock.Mock()
        self._callFUT(self.config, wf, 'basic', 'File')
        self._callFUT(self.config, wf, 'basic', 'Folder')

        self.assertEqual({'basic': {'File': wf, 'Folder': wf}},
                         self.config.registry.workflow.types)
        self.assertEqual({'File': {u('basic'): wf}, 'Folder': {u('basic'): wf}},
                         self.config.registry.workflow.content_types)
        self.config.registry.content.exists.assert_any_call('File')
        self.config.registry.content.exists.assert_any_call('Folder')

    def test_register_workflow_no_such_content_type(self):
        from pyramid.config import ConfigurationError
        self.config.registry.content.exists.return_value = False
        wf = mock.Mock()
        self.assertRaises(ConfigurationError,
                          self._callFUT,
                          self.config,
                          wf,
                          'basic',
                          'Foobar')
        self.config.registry.content.exists.assert_call('Foobar')

class Test_WorkflowedPredicate(unittest.TestCase):
    def _makeOne(self, val, config):
        from substanced.workflow import _WorkflowedPredicate
        return _WorkflowedPredicate(val, config)

    def test_text(self):
        config = DummyContent()
        config.registry = DummyContent()
        inst = self._makeOne(True, config)
        self.assertEqual(inst.text(), 'workflowed = True')

    def test_phash(self):
        config = DummyContent()
        config.registry = DummyContent()
        inst = self._makeOne(True, config)
        self.assertEqual(inst.phash(), 'workflowed = True')

    def test__call__(self):
        config = DummyContent()
        config.registry = DummyContent()
        inst = self._makeOne(True, config)
        def is_workflowed(context, registry):
            self.assertEqual(context, None)
            self.assertEqual(registry, config.registry)
            return True
        inst.is_workflowed = is_workflowed
        self.assertEqual(inst(None, None), True)

class Test_is_workflowed(unittest.TestCase):
    def setUp(self):
        self.config = testing.setUp()

    def tearDown(self):
        testing.tearDown()

    def _callFUT(self, context, registry):
        from substanced.workflow import is_workflowed
        return is_workflowed(context, registry)

    def test_no_workflow_registry(self):
        content = DummyContent()
        registry = DummyContent()
        self.assertEqual(self._callFUT(content, registry), False)

    def test_no_content_type(self):
        content = DummyContent()
        registry = DummyContent()
        registry.workflow = True
        registry.content = DummyContentRegistry(None)
        self.assertEqual(self._callFUT(content, registry), False)

    def test_gardenpath(self):
        content = DummyContent()
        registry = DummyContent()
        workflow = DummyContent()
        registry.workflow = DummyWorkflowRegistry(workflow)
        registry.content = DummyContentRegistry('abc')
        self.assertEqual(self._callFUT(content, registry), True)


class ACLStateTests(unittest.TestCase):

    def _getTargetClass(self):
        from substanced.workflow import ACLState
        return ACLState

    def _makeOne(self, acl=None):
        klass = self._getTargetClass()
        return klass(acl)

    def test___call___wo_acl(self):
        state = self._makeOne()
        # no raise, no mutation
        state(object(), request={}, transition='dummy', workflow=object())

    def test___call___w_acl(self):
        from pyramid.security import Allow
        from pyramid.security import Everyone
        from pyramid.security import ALL_PERMISSIONS
        class _Content(object):
            pass
        content = _Content()
        AFTER = [(Allow, Everyone, ALL_PERMISSIONS)]
        state = self._makeOne(AFTER)
        state(content, request={}, transition='dummy', workflow=object())
        self.assertEqual(content.__acl__, AFTER)

class DummyContent:
    pass

class DummyContentRegistry(object):
    def __init__(self, result):
        self.result = result
    def typeof(self, context):
        return self.result

class DummyWorkflowRegistry(object):
    def __init__(self, result):
        self.result = result
    def get_all_types(self, content_type):
        return self.result
