import unittest
from pyramid import testing

from zope.interface import Interface
from zope.interface.verify import (
    verifyObject,
    verifyClass
    )

class TestFolder(unittest.TestCase):
    def setUp(self):
        self.config = testing.setUp()

    def tearDown(self):
        testing.tearDown()

    def _getTargetClass(self):
        from .. import Folder
        return Folder

    def _makeSite(self, objectmap=None):
        from substanced.interfaces import IFolder
        from zope.interface import alsoProvides
        site = testing.DummyResource()
        if objectmap:
            site.__objectmap__ = objectmap
        alsoProvides(site, IFolder)
        return site

    def _makeOne(self, data=None, family=None):
        klass = self._getTargetClass()
        return klass(data, family=family)

    def test_klass_provides_IFolder(self):
        klass = self._getTargetClass()
        from substanced.interfaces import IFolder
        verifyClass(IFolder, klass)

    def test_inst_provides_IFolder(self):
        from substanced.interfaces import IFolder
        inst = self._makeOne()
        verifyObject(IFolder, inst)

    def test_ctor_alternate_family(self):
        import BTrees
        inst = self._makeOne(family=BTrees.family32)
        self.assertEqual(inst.family, BTrees.family32)

    def _registerEventListener(self, listener, iface):
        self.config.registry.registerHandler(
            listener, (iface, Interface, Interface))

    def test_keys(self):
        model1 = DummyModel()
        model2 = DummyModel()
        folder = self._makeOne({'a': model1, 'b': model2})
        self.assertEqual(list(folder.keys()), ['a', 'b'])

    def test_set_order_not_all_names_mentioned(self):
        model1 = DummyModel()
        model2 = DummyModel()
        folder = self._makeOne({'a': model1, 'b': model2})
        self.assertRaises(ValueError, folder.set_order, ['a'])

    def test_set_order_name_mentioned_more_than_once(self):
        model1 = DummyModel()
        model2 = DummyModel()
        folder = self._makeOne({'a': model1, 'b': model2})
        self.assertRaises(ValueError, folder.set_order, ['a', 'a', 'b'])

    def test_set_order_influences_is_ordered(self):
        model1 = DummyModel()
        model2 = DummyModel()
        folder = self._makeOne({'a': model1, 'b': model2})
        folder.set_order(['b', 'a'])
        self.assertTrue(folder.is_ordered())

    def test_set_order_impacts_keys(self):
        model1 = DummyModel()
        model2 = DummyModel()
        folder = self._makeOne({'a': model1, 'b': model2})
        folder.set_order(['b', 'a'])
        self.assertEqual(list(folder.keys()), ['b', 'a'])

    def test_unset_order_not_reorderable(self):
        model1 = DummyModel()
        model2 = DummyModel()
        folder = self._makeOne({'a': model1, 'b': model2})
        folder.set_order(['b', 'a'])
        self.assertTrue(folder.is_ordered())
        self.assertFalse(folder.is_reorderable())
        self.assertEqual(list(folder.keys()), ['b', 'a'])
        folder.unset_order()
        self.assertEqual(list(folder.keys()), ['a', 'b'])
        self.assertEqual(folder._order, None)
        self.assertEqual(folder._order_oids, None)
        self.assertEqual(folder._reorderable, None)
        self.assertFalse(folder.is_ordered())
        self.assertFalse(folder.is_reorderable())

    def test_unset_order_reorderable(self):
        model1 = DummyModel()
        model2 = DummyModel()
        folder = self._makeOne({'a': model1, 'b': model2})
        folder.set_order(['b', 'a'], reorderable=True)
        self.assertTrue(folder.is_ordered())
        self.assertTrue(folder.is_reorderable())
        self.assertEqual(list(folder.keys()), ['b', 'a'])
        folder.unset_order()
        self.assertEqual(list(folder.keys()), ['a', 'b'])
        self.assertEqual(folder._order, None)
        self.assertEqual(folder._order_oids, None)
        self.assertEqual(folder._reorderable, None)
        self.assertFalse(folder.is_ordered())
        self.assertFalse(folder.is_reorderable())

    def test_set_order_is_non_reorderable_by_default(self):
        model1 = DummyModel()
        model2 = DummyModel()
        folder = self._makeOne({'a': model1, 'b': model2})
        folder.set_order(['a', 'b'])
        self.assertFalse(folder.is_reorderable())

    def test_set_order_reorderable_false(self):
        model1 = DummyModel()
        model2 = DummyModel()
        folder = self._makeOne({'a': model1, 'b': model2})
        folder.set_order(['a', 'b'], reorderable=False)
        self.assertFalse(folder.is_reorderable())

    def test_set_order_reorderable_true(self):
        model1 = DummyModel()
        model2 = DummyModel()
        folder = self._makeOne({'a': model1, 'b': model2})
        folder.set_order(['a', 'b'], reorderable=True)
        self.assertTrue(folder.is_reorderable())

    def test_is_ordered_false_by_default(self):
        folder = self._makeOne({'a': 1, 'b': 2})
        self.assertFalse(folder.is_ordered())

    def test_sort_with_explicit_folder_order(self):
        model1 = DummyModel()
        model1.__oid__ = 1
        model2 = DummyModel()
        model2.__oid__ = 2
        folder = self._makeOne({'a': model1, 'b': model2})
        folder.set_order(['a', 'b'])
        result = folder.sort([1,2])
        self.assertEqual(result, [1, 2])

    def test_sort_no_reverse_no_limit(self):
        model1 = DummyModel()
        model1.__oid__ = 1
        model2 = DummyModel()
        model2.__oid__ = 2
        folder = self._makeOne({'a': model1, 'b': model2})
        result = folder.sort([1,2])
        self.assertEqual(result, [1, 2])

    def test_sort_no_reverse_no_limit_catalog_has_more_results_than_fold(self):
        model1 = DummyModel()
        model1.__oid__ = 1
        model2 = DummyModel()
        model2.__oid__ = 2
        folder = self._makeOne({'a': model1, 'b': model2})
        result = folder.sort([1,2,3])
        self.assertEqual(result, [1, 2])

    def test_sort_no_reverse_no_limit_fold_has_more_results_than_catalog(self):
        model1 = DummyModel()
        model1.__oid__ = 1
        model2 = DummyModel()
        model2.__oid__ = 2
        folder = self._makeOne({'a': model1, 'b': model2})
        result = folder.sort([1])
        self.assertEqual(result, [1])

    def test_sort_reverse_no_limit(self):
        model1 = DummyModel()
        model1.__oid__ = 1
        model2 = DummyModel()
        model2.__oid__ = 2
        folder = self._makeOne({'a': model1, 'b': model2})
        result = folder.sort([1, 2], reverse=True)
        self.assertEqual(result, [2, 1])

    def test_sort_reverse_limit(self):
        model1 = DummyModel()
        model1.__oid__ = 1
        model2 = DummyModel()
        model2.__oid__ = 2
        folder = self._makeOne({'a': model1, 'b': model2})
        result = folder.sort([1, 2], reverse=True, limit=1)
        self.assertEqual(result, [2])

    def test_sort_forward_limit(self):
        model1 = DummyModel()
        model1.__oid__ = 1
        model2 = DummyModel()
        model2.__oid__ = 2
        folder = self._makeOne({'a': model1, 'b': model2})
        result = folder.sort([1, 2], limit=1)
        self.assertEqual(result, [1])

    def test__iter__(self):
        model1 = DummyModel()
        model2 = DummyModel()
        folder = self._makeOne({'a': model1, 'b': model2})
        self.assertEqual(list(folder), ['a', 'b'])

    def test__iter___with_order(self):
        model1 = DummyModel()
        model2 = DummyModel()
        folder = self._makeOne({'a': model1, 'b': model2})
        folder.set_order(['b', 'a'])
        self.assertEqual(list(folder), ['b', 'a'])

    def test_values(self):
        folder = self._makeOne({'a': 1, 'b': 2})
        self.assertEqual(list(folder.values()), [1, 2])

    def test_values_with_order(self):
        model1 = DummyModel()
        model2 = DummyModel()
        folder = self._makeOne({'a': model1, 'b': model2})
        folder.set_order(['b', 'a'])
        self.assertEqual(list(folder.values()), [model2, model1])

    def test_items(self):
        folder = self._makeOne({'a': 1, 'b': 2})
        self.assertEqual(list(folder.items()), [('a', 1), ('b', 2)])

    def test_items_with_order(self):
        model1 = DummyModel()
        model2 = DummyModel()
        folder = self._makeOne({'a': model1, 'b': model2})
        folder.set_order(['b', 'a'])
        self.assertEqual(list(folder.items()), [('b', model2), ('a', model1)])

    def test__len__(self):
        folder = self._makeOne({'a': 1, 'b': 2})
        self.assertEqual(len(folder), 2)
        del folder['a']
        self.assertEqual(len(folder), 1)

    def test__contains__(self):
        folder = self._makeOne({'a': 1, 'b': 2})
        self.assertTrue('a' in folder)
        self.assertFalse('c' in folder)

    def test___nonzero__(self):
        folder = self._makeOne()
        self.assertTrue(folder)

    def test___setitem__nonstring(self):
        folder = self._makeOne()
        self.assertRaises(ValueError, folder.__setitem__, None, None)

    def test___setitem__8bitstring(self):
        folder = self._makeOne()
        self.assertRaises(ValueError, folder.__setitem__, b'\xff', None)

    def test___setitem__empty(self):
        folder = self._makeOne()
        self.assertRaises(ValueError, folder.__setitem__, '', None)

    def test___setitem__(self):
        from substanced.interfaces import IObjectEvent
        from substanced.interfaces import IObjectWillBeAdded
        from substanced.interfaces import IObjectAdded
        events = []
        def listener(event, obj, container):
            events.append(event)
        self._registerEventListener(listener, IObjectEvent)
        dummy = DummyModel()
        folder = self._makeOne()
        self.assertEqual(folder._num_objects(), 0)
        folder['a'] = dummy
        self.assertEqual(folder._num_objects(), 1)
        self.assertEqual(len(events), 2)
        self.assertTrue(IObjectWillBeAdded.providedBy(events[0]))
        self.assertEqual(events[0].object, dummy)
        self.assertEqual(events[0].parent, folder)
        self.assertEqual(events[0].name, 'a')
        self.assertTrue(IObjectAdded.providedBy(events[1]))
        self.assertEqual(events[1].object, dummy)
        self.assertEqual(events[1].parent, folder)
        self.assertEqual(events[1].name, 'a')
        self.assertEqual(folder['a'], dummy)

    def test_validate_name_non_string(self):
        folder = self._makeOne()
        self.assertRaises(ValueError, folder.validate_name, object())

    def test_validate_name_empty_string(self):
        folder = self._makeOne()
        self.assertRaises(ValueError, folder.validate_name, '')

    def test_validate_name_non_decdable_string(self):
        folder = self._makeOne()
        self.assertRaises(ValueError, folder.validate_name, b'\x80')

    def test_validate_name_reserved(self):
        folder = self._makeOne()
        self.assertRaises(ValueError, folder.validate_name, 'foo',
                                      reserved_names=['foo', 'bar'])

    def test_validate_name_startswith_goggles(self):
        folder = self._makeOne()
        self.assertRaises(ValueError, folder.validate_name, '@@foo')

    def test_validate_name_startswith_slash(self):
        folder = self._makeOne()
        self.assertRaises(ValueError, folder.validate_name, '/foo')

    def test_validate_name_endswith_slash(self):
        folder = self._makeOne()
        self.assertRaises(ValueError, folder.validate_name, 'foo/')

    def test_validate_name_with_slash(self):
        folder = self._makeOne()
        self.assertRaises(ValueError, folder.validate_name, 'foo/bar')

    def test_validate_name_ok(self):
        folder = self._makeOne()
        self.assertEqual(folder.validate_name('foo'), 'foo')

    def test_add_name_wrongtype(self):
        folder = self._makeOne()
        self.assertRaises(ValueError, folder.add, 1, 'foo')

    def test_add_name_empty(self):
        folder = self._makeOne()
        self.assertRaises(ValueError, folder.add, '', 'foo')

    def test_add_reserved_name(self):
        folder = self._makeOne()
        self.assertRaises(ValueError, folder.add, 'foo', None,
                          reserved_names=('foo',))

    def test_add_with_slash_in_name(self):
        folder = self._makeOne()
        self.assertRaises(ValueError, folder.add, '/abc', None)

    def test_add_begins_with_atat(self):
        folder = self._makeOne()
        self.assertRaises(ValueError, folder.add, '@@abc', None)

    def test_check_name(self):
        folder = self._makeOne()
        self.assertRaises(ValueError, folder.check_name, '@@abc')

    def test_add_send_events(self):
        from substanced.interfaces import IObjectEvent
        from substanced.interfaces import IObjectWillBeAdded
        from substanced.interfaces import IObjectAdded
        events = []
        def listener(event, obj, container):
            events.append(event)
        self._registerEventListener(listener, IObjectEvent)
        dummy = DummyModel()
        folder = self._makeOne()
        self.assertEqual(folder._num_objects(), 0)
        folder.add('a', dummy, send_events=True)
        self.assertEqual(folder._num_objects(), 1)
        self.assertEqual(len(events), 2)
        self.assertTrue(IObjectWillBeAdded.providedBy(events[0]))
        self.assertEqual(events[0].object, dummy)
        self.assertEqual(events[0].parent, folder)
        self.assertEqual(events[0].name, 'a')
        self.assertTrue(IObjectAdded.providedBy(events[1]))
        self.assertEqual(events[1].object, dummy)
        self.assertEqual(events[1].parent, folder)
        self.assertEqual(events[1].name, 'a')
        self.assertEqual(folder['a'], dummy)

    def test_add_suppress_events(self):
        from substanced.interfaces import IObjectEvent
        events = []
        def listener(event, obj, container):
            events.append(event) #pragma NO COVER
        self._registerEventListener(listener, IObjectEvent)
        dummy = DummyModel()
        folder = self._makeOne()
        self.assertEqual(folder._num_objects(), 0)
        folder.add('a', dummy, send_events=False)
        self.assertEqual(folder._num_objects(), 1)
        self.assertEqual(len(events), 0)
        self.assertEqual(folder['a'], dummy)

    def test_add_with_order_appends_name_and_oid(self):
        folder = self._makeOne()
        folder.set_order([])
        folder.add('a', DummyModel())
        self.assertEqual(folder._order, ('a',))
        self.assertEqual(folder._order_oids, (1,))
        folder.add('b', DummyModel())
        self.assertEqual(folder._order, ('a', 'b'))
        self.assertEqual(folder._order_oids, (1, 1))

    def test_add_with_object_has_parent(self):
        folder = self._makeOne()
        objectmap = DummyObjectMap()
        folder.__objectmap__ = objectmap
        site = self._makeSite()
        a = site['a'] = DummyModel()
        self.assertRaises(ValueError, folder.add, 'a', a)

    def test_add_with_objectmap(self):
        folder = self._makeOne()
        objectmap = DummyObjectMap()
        folder.__objectmap__ = objectmap
        a = DummyModel()
        folder.add('a', a)
        self.assertEqual(objectmap.added, [(a, ('', 'a'))])

    def test_add_with_objectmap_object_has_children(self):
        from substanced.interfaces import IFolder
        folder = self._makeOne()
        objectmap = DummyObjectMap()
        folder.__objectmap__ = objectmap
        one = testing.DummyModel(__provides__=IFolder)
        two = testing.DummyModel()
        one['two'] = two
        folder.add('one', one)
        self.assertEqual(
            objectmap.added,
            [(two, ('', 'one', 'two')), (one, ('', 'one'))]
        )

    def test_add_with_objectmap_object_has_children_object_has_no_name(self):
        from substanced.interfaces import IFolder
        folder = self._makeOne()
        objectmap = DummyObjectMap()
        folder.__objectmap__ = objectmap
        one = testing.DummyModel(__provides__=IFolder)
        two = testing.DummyModel()
        one['two'] = two
        del one.__name__
        folder.add('one', one)
        self.assertEqual(
            objectmap.added,
            [(two, ('', 'one', 'two')), (one, ('', 'one'))]
        )

    def test_add_with_objectmap_object_has_children_not_adding_to_root(self):
        from substanced.interfaces import IFolder
        folder = self._makeOne()
        objectmap = DummyObjectMap()
        site = self._makeSite(objectmap)
        site['folder'] = folder
        one = testing.DummyModel(__provides__=IFolder)
        two = testing.DummyModel()
        one['two'] = two
        folder.add('one', one)
        self.assertEqual(
            objectmap.added,
            [(two, ('', 'folder', 'one', 'two')), (one, ('', 'folder', 'one'))]
        )

    def test___setitem__exists(self):
        from .. import FolderKeyError
        dummy = DummyModel()
        folder = self._makeOne({'a': dummy})
        self.assertEqual(folder._num_objects(), 1)
        self.assertRaises(FolderKeyError, folder.__setitem__, 'a', dummy)
        self.assertEqual(folder._num_objects(), 1)

    def test___delitem__(self):
        from substanced.interfaces import IObjectEvent
        from substanced.interfaces import IObjectRemoved
        from substanced.interfaces import IObjectWillBeRemoved
        events = []
        def listener(event, obj, container):
            events.append(event)
        self._registerEventListener(listener, IObjectEvent)
        dummy = DummyModel()
        dummy.__parent__ = None
        dummy.__name__ = None
        folder = self._makeOne({'a': dummy})
        self.assertEqual(folder._num_objects(), 1)
        del folder['a']
        self.assertEqual(folder._num_objects(), 0)
        self.assertEqual(len(events), 2)
        self.assertTrue(IObjectWillBeRemoved.providedBy(events[0]))
        self.assertTrue(IObjectRemoved.providedBy(events[1]))
        self.assertEqual(events[0].object, dummy)
        self.assertEqual(events[0].parent, folder)
        self.assertEqual(events[0].name, 'a')
        self.assertEqual(events[1].object, dummy)
        self.assertEqual(events[1].parent, folder)
        self.assertEqual(events[1].name, 'a')
        self.assertFalse(hasattr(dummy, '__parent__'))
        self.assertFalse(hasattr(dummy, '__name__'))

    def test_remove_miss(self):
        folder = self._makeOne()
        self.assertRaises(KeyError, folder.remove, "nonesuch")

    def test_remove_returns_object(self):
        dummy = DummyModel()
        dummy.__parent__ = None
        dummy.__name__ = None
        folder = self._makeOne({'a': dummy})
        self.assertTrue(folder.remove("a") is dummy)

    def test_remove_send_events(self):
        from substanced.interfaces import IObjectEvent
        from substanced.interfaces import IObjectRemoved
        from substanced.interfaces import IObjectWillBeRemoved
        events = []
        def listener(event, obj, container):
            events.append(event)
        self._registerEventListener(listener, IObjectEvent)
        dummy = DummyModel()
        dummy.__parent__ = None
        dummy.__name__ = None
        folder = self._makeOne({'a': dummy})
        self.assertEqual(folder._num_objects(), 1)
        folder.remove('a', send_events=True)
        self.assertEqual(folder._num_objects(), 0)
        self.assertEqual(len(events), 2)
        self.assertTrue(IObjectWillBeRemoved.providedBy(events[0]))
        self.assertTrue(IObjectRemoved.providedBy(events[1]))
        self.assertEqual(events[0].object, dummy)
        self.assertEqual(events[0].parent, folder)
        self.assertEqual(events[0].name, 'a')
        self.assertFalse(events[0].moving)
        self.assertEqual(events[1].object, dummy)
        self.assertEqual(events[1].parent, folder)
        self.assertEqual(events[1].name, 'a')
        self.assertFalse(events[1].moving)

        self.assertFalse(hasattr(dummy, '__parent__'))
        self.assertFalse(hasattr(dummy, '__name__'))

    def test_remove_suppress_events(self):
        from substanced.interfaces import IObjectEvent
        events = []
        def listener(event, obj, container):
            events.append(event) #pragma NO COVER
        self._registerEventListener(listener, IObjectEvent)
        dummy = DummyModel()
        dummy.__parent__ = None
        dummy.__name__ = None
        folder = self._makeOne({'a': dummy})
        self.assertEqual(folder._num_objects(), 1)
        folder.remove('a', send_events=False)
        self.assertEqual(folder._num_objects(), 0)
        self.assertEqual(len(events), 0)
        self.assertFalse(hasattr(dummy, '__parent__'))
        self.assertFalse(hasattr(dummy, '__name__'))

    def test_remove_moving(self):
        from substanced.interfaces import IObjectEvent
        from substanced.interfaces import IObjectRemoved
        from substanced.interfaces import IObjectWillBeRemoved
        events = []
        def listener(event, obj, container):
            events.append(event) #pragma NO COVER
        self._registerEventListener(listener, IObjectEvent)
        dummy = DummyModel()
        dummy.__parent__ = None
        dummy.__name__ = None
        folder = self._makeOne({'a': dummy})
        self.assertEqual(folder._num_objects(), 1)
        folder.remove('a', moving=True)
        self.assertEqual(folder._num_objects(), 0)
        self.assertFalse(hasattr(dummy, '__parent__'))
        self.assertFalse(hasattr(dummy, '__name__'))
        self.assertEqual(len(events), 2)
        self.assertTrue(IObjectWillBeRemoved.providedBy(events[0]))
        self.assertTrue(IObjectRemoved.providedBy(events[1]))
        self.assertEqual(events[0].object, dummy)
        self.assertEqual(events[0].parent, folder)
        self.assertEqual(events[0].name, 'a')
        self.assertTrue(events[0].moving)
        self.assertEqual(events[1].object, dummy)
        self.assertEqual(events[1].parent, folder)
        self.assertEqual(events[1].name, 'a')
        self.assertTrue(events[1].moving)

    def test_remove_with_objectmap(self):
        dummy = DummyModel()
        dummy.__parent__ = None
        dummy.__name__ = None
        dummy.__oid__ = 1
        folder = self._makeOne({'a': dummy})
        objectmap = DummyObjectMap()
        folder.__objectmap__ = objectmap
        folder.remove("a")
        self.assertEqual(objectmap.removed, [1])
        self.assertFalse(objectmap.moving)

    def test_remove_with_objectmap_moving(self):
        dummy = DummyModel()
        dummy.__parent__ = None
        dummy.__name__ = None
        dummy.__oid__ = 1
        folder = self._makeOne({'a': dummy})
        objectmap = DummyObjectMap()
        folder.__objectmap__ = objectmap
        folder.remove("a", moving=True)
        self.assertEqual(objectmap.removed, [1])
        self.assertTrue(objectmap.moving)

    def test_move_no_newname(self):
        folder = self._makeOne()
        other = self._makeOne()
        model = DummyModel()
        folder['a'] = model
        folder.move('a', other)
        self.assertEqual(other['a'], model)
        self.assertEqual(other['a'].__name__, 'a')
        self.assertEqual(other['a'].__parent__, other)
        self.assertFalse('a' in folder)

    def test_move_newname(self):
        folder = self._makeOne()
        other = self._makeOne()
        model = DummyModel()
        folder['a'] = model
        folder.move('a', other, 'b')
        self.assertEqual(other['b'], model)
        self.assertEqual(other['b'].__name__, 'b')
        self.assertEqual(other['b'].__parent__, other)
        self.assertFalse('a' in other)
        self.assertFalse('a' in folder)

    def test_move_is_service(self):
        folder = self._makeOne()
        other = self._makeOne()
        model = DummyModel()
        model.__is_service__ = True
        folder['a'] = model
        folder.move('a', other)
        self.assertEqual(other['a'], model)
        self.assertTrue(other['a'].__is_service__)

    def test_copy_no_newname(self):
        folder = self._makeOne()
        other = self._makeOne()
        model = testing.DummyResource()
        folder['a'] = model
        folder.copy('a', other)
        self.assertEqual(other['a'].__name__, 'a')
        self.assertEqual(other['a'].__parent__, other)
        self.assertTrue('a' in folder)

    def test_copy_newname(self):
        folder = self._makeOne()
        other = self._makeOne()
        model = testing.DummyResource()
        folder['a'] = model
        folder.copy('a', other, 'b')
        self.assertEqual(other['b'].__name__, 'b')
        self.assertEqual(other['b'].__parent__, other)
        self.assertFalse('a' in other)
        self.assertTrue('a' in folder)

    def test_rename(self):
        folder = self._makeOne()
        model = DummyModel()
        folder['a'] = model
        folder.rename('a', 'b')
        self.assertEqual(folder['b'], model)
        self.assertEqual(folder['b'].__name__, 'b')
        self.assertEqual(folder['b'].__parent__, folder)
        self.assertFalse('a' in folder)

    def test_remove_with_order_removes_name(self):
        folder = self._makeOne()
        folder['a'] = DummyModel()
        folder['b'] = DummyModel()
        folder.set_order(['a', 'b'])
        folder.remove('a')
        self.assertEqual(folder._order, ('b',))
        self.assertEqual(folder._order_oids, (1,))

    def test_replace_existing(self):
        folder = self._makeOne()
        other = self._makeOne()
        model = DummyModel()
        folder['a'] = model
        folder.replace('a', other)
        self.assertEqual(folder['a'], other)
        self.assertEqual(other.__name__, 'a')
        self.assertEqual(other.__parent__, folder)

    def test_replace_nonexisting(self):
        folder = self._makeOne()
        other = self._makeOne()
        folder.replace('a', other)
        self.assertEqual(folder['a'], other)
        self.assertEqual(other.__name__, 'a')
        self.assertEqual(other.__parent__, folder)

    def test_load_with_registry(self):
        registry = self.config.registry
        folder = self._makeOne()
        one = testing.DummyResource()
        two = testing.DummyResource()
        folder['a'] = one
        result = []
        folder.remove = lambda *arg, **kw: result.append(('removed', kw))
        folder.add = lambda *arg, **kw: result.append(('added', kw))
        folder.load('a', two, registry=registry)
        self.assertEqual(
            result,
            [
                ('removed', {'loading':True}),
                ('added', {'loading':True, 'registry':registry}),
                ])

    def test_load_no_registry(self):
        registry = self.config.registry
        folder = self._makeOne()
        one = testing.DummyResource()
        two = testing.DummyResource()
        folder['a'] = one
        result = []
        folder.remove = lambda *arg, **kw: result.append(('removed', kw))
        folder.add = lambda *arg, **kw: result.append(('added', kw))
        folder.load('a', two)
        self.assertEqual(
            result,
            [
                ('removed', {'loading':True}),
                ('added', {'loading':True, 'registry':registry}),
                ])

    def test_pop_success(self):
        from substanced.interfaces import IObjectEvent
        from substanced.interfaces import IObjectRemoved
        from substanced.interfaces import IObjectWillBeRemoved
        dummy = DummyModel()
        dummy.__parent__ = None
        dummy.__name__ = None
        events = []
        def listener(event, obj, container):
            events.append(event)
        self._registerEventListener(listener, IObjectEvent)
        folder = self._makeOne({'a': dummy})
        result = folder.pop('a')
        self.assertEqual(result, dummy)
        self.assertEqual(folder._num_objects(), 0)
        self.assertEqual(len(events), 2)
        self.assertTrue(IObjectWillBeRemoved.providedBy(events[0]))
        self.assertTrue(IObjectRemoved.providedBy(events[1]))
        self.assertEqual(events[0].object, dummy)
        self.assertEqual(events[0].parent, folder)
        self.assertEqual(events[0].name, 'a')
        self.assertEqual(events[1].object, dummy)
        self.assertEqual(events[1].parent, folder)
        self.assertEqual(events[1].name, 'a')
        self.assertFalse(hasattr(dummy, '__parent__'))
        self.assertFalse(hasattr(dummy, '__name__'))

    def test_pop_fail_nodefault(self):
        folder = self._makeOne()
        self.assertRaises(KeyError, folder.pop, 'nonesuch')

    def test_pop_fail_withdefault(self):
        folder = self._makeOne()
        result = folder.pop('a', 123)
        self.assertEqual(result, 123)

    def test_repr(self):
        folder = self._makeOne()
        folder.__name__ = 'thefolder'
        r = repr(folder)
        self.assertTrue(
            r.startswith("<substanced.folder.Folder object 'thefolder"))
        self.assertTrue(r.endswith('>'))

    def test_str(self):
        folder = self._makeOne()
        folder.__name__ = 'thefolder'
        r = str(folder)
        self.assertTrue(
            r.startswith("<substanced.folder.Folder object 'thefolder"))
        self.assertTrue(r.endswith('>'))

    def test_unresolveable_unicode_setitem(self):
        from substanced._compat import u
        name = u(b'La Pe\xc3\xb1a', 'utf-8').encode('latin-1')
        folder = self._makeOne()
        self.assertRaises(ValueError,
                          folder.__setitem__, name, DummyModel())

    def test_resolveable_unicode_setitem(self):
        name = 'La'
        folder = self._makeOne()
        folder[name] = DummyModel()
        self.assertTrue(folder.get(name))

    def test_unresolveable_unicode_getitem(self):
        from substanced._compat import u
        name = u(b'La Pe\xc3\xb1a', 'utf-8').encode('latin-1')
        folder = self._makeOne()
        self.assertRaises(UnicodeDecodeError, folder.__getitem__, name)

    def test_resolveable_unicode_getitem(self):
        name = 'La'
        folder = self._makeOne()
        folder[name] = DummyModel()
        self.assertTrue(folder[name])

    def test_find_service_missing(self):
        inst = self._makeOne()
        self.assertEqual(inst.find_service('abc'), None)

    def test_find_service_found(self):
        inst = self._makeOne()
        inst2 = self._makeOne()
        inst2.__is_service__ = True
        inst.add('inst2', inst2)
        self.assertEqual(inst.find_service('inst2'), inst2)

    def test_find_services_missing(self):
        inst = self._makeOne()
        self.assertEqual(inst.find_services('abc'), [])

    def test_find_services_found(self):
        inst = self._makeOne()
        inst2 = self._makeOne()
        inst2.__is_service__ = True
        inst.add('inst2', inst2)
        self.assertEqual(inst.find_services('inst2'), [inst2])

    def test_add_service(self):
        inst = self._makeOne()
        foo = testing.DummyResource()
        inst.add_service('foo', foo)
        self.assertEqual(inst['foo'], foo)
        self.assertTrue(foo.__is_service__)

    def test_add_service_withregistry(self):
        inst = self._makeOne()
        foo = testing.DummyResource()
        inst.add_service('foo', foo, registry=self.config.registry)
        self.assertEqual(inst['foo'], foo)
        self.assertTrue(foo.__is_service__)

    def test__notify_no_registry(self):
        def f(t, n):
            self.assertEqual(t, (event, event.object, inst))
            self.assertEqual(n, None)
        self.config.registry.subscribers = f
        inst = self._makeOne()
        event = DummyModel()
        event.object = DummyModel()
        inst._notify(event)

    def test_ordered_folder_oids(self):
        model1 = DummyModel()
        model2 = DummyModel()
        model2.__oid__ = 2
        folder = self._makeOne({'a': model1, 'b': model2})
        folder.set_order(['b', 'a'])
        self.assertEqual(folder._order_oids, (2, 1))

    def test_reorder_folder(self):
        model1 = DummyModel()
        model2 = DummyModel()
        model3 = DummyModel()
        folder = self._makeOne({'a': model1, 'b': model2, 'c': model3})
        folder.set_order(['a', 'b', 'c'], reorderable=True)
        folder.reorder(['b', 'c'], 'a')
        self.assertEqual(list(folder), ['b', 'c', 'a'])

    def test_reorder_folder_item_before_itself(self):
        model1 = DummyModel(1)
        model2 = DummyModel(2)
        model3 = DummyModel(3)
        model4 = DummyModel(4)
        folder = self._makeOne({'a': model1, 'b': model2, 'c': model3,
                                'd':model4})
        folder.set_order(['a', 'b', 'c', 'd'], reorderable=True)
        folder.reorder(['d', 'a', 'b'], 'b')
        self.assertEqual(list(folder), ['d', 'a', 'b', 'c'])

    def test_reorder_folder_item_before_itself_2(self):
        model1 = DummyModel(1)
        model2 = DummyModel(2)
        model3 = DummyModel(3)
        model4 = DummyModel(4)
        folder = self._makeOne({'a': model1, 'b': model2, 'c': model3,
                                'd':model4})
        folder.set_order(['a', 'b', 'c', 'd'], reorderable=True)
        folder.reorder(['b', 'a', 'c'], 'a')
        self.assertEqual(list(folder), ['b', 'a', 'c', 'd'])

    def test_reorder_folder_afterlast(self):
        model1 = DummyModel()
        model2 = DummyModel()
        model3 = DummyModel()
        folder = self._makeOne({'a': model1, 'b': model2, 'c': model3})
        folder.set_order(['a', 'b', 'c'], reorderable=True)
        folder.reorder(['a', 'b'], None)
        self.assertEqual(list(folder), ['c', 'a', 'b'])

    def test_reorder_folder_no_such_before(self):
        model1 = DummyModel()
        model2 = DummyModel()
        model3 = DummyModel()
        folder = self._makeOne({'a': model1, 'b': model2, 'c': model3})
        folder.set_order(['a', 'b', 'c'], reorderable=True)
        self.assertRaises(KeyError,
               folder.reorder, ['a', 'b'], 'NOSUCH')

    def test_reorder_folder_no_such_item(self):
        model1 = DummyModel()
        model2 = DummyModel()
        model3 = DummyModel()
        folder = self._makeOne({'a': model1, 'b': model2, 'c': model3})
        folder.set_order(['a', 'b', 'c'], reorderable=True)
        self.assertRaises(KeyError,
               folder.reorder, ['a', 'z'], 'c')

    def test_reorder_folder_repeated_name(self):
        model1 = DummyModel(1)
        model2 = DummyModel(2)
        model3 = DummyModel(3)
        model4 = DummyModel(4)
        folder = self._makeOne({'a': model1, 'b': model2, 'c': model3,
                                'd':model4})
        folder.set_order(['a', 'b', 'c', 'd'], reorderable=True)
        self.assertRaises(ValueError, folder.reorder, ['b', 'b'], 'a')

    def test_reorder_folder_non_reorderable(self):
        model1 = DummyModel()
        model2 = DummyModel()
        model3 = DummyModel()
        folder = self._makeOne({'a': model1, 'b': model2, 'c': model3})
        folder.set_order(['a', 'b', 'c'], reorderable=False)
        self.assertRaises(ValueError, folder.reorder, ['b', 'c'], 'a')

    def test_order_property_get_set_and_del(self):
        model1 = DummyModel()
        model2 = DummyModel()
        model3 = DummyModel()
        folder = self._makeOne({'a': model1, 'b': model2, 'c': model3})
        self.assertEqual(list(folder.order), ['a', 'b', 'c'])
        folder.order = ['c', 'b', 'a']
        self.assertEqual(list(folder.order), ['c', 'b', 'a'])
        del folder.order
        self.assertEqual(list(folder.order), ['a', 'b', 'c'])
        
        

class TestSequentialAutoNamingFolder(unittest.TestCase):
    def _makeOne(self, d=None, autoname_length=None, autoname_start=None):
        from .. import SequentialAutoNamingFolder
        return SequentialAutoNamingFolder(
            d,
            autoname_length=autoname_length,
            autoname_start=autoname_start
            )

    def test_next_name_empty(self):
        inst = self._makeOne()
        self.assertEqual(inst.next_name(None), '0'.zfill(7))

    def test_next_name_nonempty(self):
        ob = DummyModel()
        inst = self._makeOne({'000000000':ob})
        self.assertEqual(inst.next_name(None), '1'.zfill(7))

    def test_next_name_alternate_autoname_length(self):
        inst = self._makeOne(autoname_length=5)
        self.assertEqual(inst.next_name(None), '0'.zfill(5))

    def test_next_name_alternate_autoname_start(self):
        inst = self._makeOne(autoname_start=0)
        self.assertEqual(inst.next_name(None), '1'.zfill(7))

    def test_next_name_empty_autoname_reset(self):
        inst = self._makeOne()
        inst._autoname_reset = True
        self.assertEqual(inst.next_name(None), '0'.zfill(7))
        self.assertFalse(inst._autoname_reset)

    def test_next_name_nonempty_autoname_reset(self):
        ob = DummyModel()
        inst = self._makeOne({'0000005':ob})
        inst._autoname_reset = True
        self.assertEqual(inst.next_name(None), '0'.zfill(7))
        self.assertFalse(inst._autoname_reset)

    def test_add_not_intifiable(self):
        ob = DummyModel()
        inst = self._makeOne()
        self.assertRaises(ValueError, inst.add, 'abcdef', ob)

    def test_add_intifiable(self):
        ob = DummyModel()
        inst = self._makeOne()
        inst.add('1', ob)
        self.assertTrue('1'.zfill(7) in inst)

    def test_add_next(self):
        ob = DummyModel()
        inst = self._makeOne()
        result = inst.add_next(ob)
        name = '0'.zfill(7)
        self.assertEqual(ob.__name__, name)
        self.assertTrue(name in inst)
        self.assertEqual(name, result)

class TestRandomAutoNamingFolder(unittest.TestCase):
    def _makeOne(self, d=None, autoname_length=None):
        from .. import RandomAutoNamingFolder
        return RandomAutoNamingFolder(d, autoname_length=autoname_length)

    def test_next_name_doesntexist(self):
        inst = self._makeOne()
        inst._randomchoice = lambda *arg: 'x'
        self.assertEqual(inst.next_name(None), 'x' * 7)

    def test_next_name_exists(self):
        inst = self._makeOne()
        L = ['x'] * 7
        L.extend(['y'] * 7)
        def choice(vals):
            v = L.pop()
            return v
        inst._randomchoice = choice
        self.assertEqual(inst.next_name(None), 'y' * 7)

    def test_next_name_alternate_length(self):
        inst = self._makeOne(autoname_length=5)
        self.assertEqual(len(inst.next_name(None)), 5)
        
    def test_add_next(self):
        ob = DummyModel()
        inst = self._makeOne()
        result = inst.add_next(ob)
        self.assertEqual(ob.__name__, result)
        self.assertTrue(result in inst)
        self.assertEqual(len(result), 7)

class TestCopyHook(unittest.TestCase):
    def _makeOne(self, context):
        from .. import CopyHook
        return CopyHook(context)

    def test_nonpersistent(self):
        from zope.copy.interfaces import ResumeCopy
        inst = self._makeOne({})
        self.assertRaises(ResumeCopy, inst, None, None)

    def test_persistent_not_child(self):
        from persistent import Persistent
        class Resource(Persistent):
            pass
        child = Resource()
        child.__parent__ = None
        parent = Resource()
        parent.__parent__ = None
        inst = self._makeOne(child)
        self.assertEqual(inst(parent, None), child)

    def test_persistent_is_child(self):
        from zope.copy.interfaces import ResumeCopy
        from persistent import Persistent
        class Resource(Persistent):
            pass
        parent = Resource()
        parent.__parent__ = None
        child = Resource()
        child.__parent__ = parent
        inst = self._makeOne(child)
        self.assertRaises(ResumeCopy, inst, parent, None)

class DummyModel(object):
    def __init__(self, oid=1):
        self.__oid__ = oid

class DummyObjectMap(object):
    def __init__(self):
        self.added = []
        self.removed = []
        self.moving = False

    def add(self, obj, path, duplicating=False, moving=False):
        self.added.append((obj, path))
        objectid = getattr(obj, '__oid__', None)
        if objectid is None:
            objectid = 1
            obj.__oid__ = objectid
        return objectid

    def remove(self, objectid, moving=False):
        self.moving = moving
        self.removed.append(objectid)
        return [objectid]

