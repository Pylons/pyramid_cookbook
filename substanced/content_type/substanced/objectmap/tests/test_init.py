import sys
import unittest
from zope.interface import implementer

from pyramid import testing

IS_32_BIT = sys.maxsize == 2**32

from substanced._compat import u
_BLANK = u('')
_SLASH = u('/')
_A = u('a')
_B = u('b')
_C = u('c')
_Z = u('z')

class TestObjectMap(unittest.TestCase):
    def setUp(self):
        self.config = testing.setUp()

    def tearDown(self):
        testing.tearDown()

    def _makeOne(self, root=None, family=None):
        from .. import ObjectMap
        if root is None:
            root = DummyRoot()
        return ObjectMap(root, family=family)

    def test_ctor_alternate_family(self):
        import BTrees
        inst = self._makeOne(family=BTrees.family32)
        self.assertEqual(inst.family, BTrees.family32)

    def test_new_objectid_empty(self):
        inst = self._makeOne()
        times = [0]
        def randrange(frm, to):
            val = times[0]
            times[0] = times[0] + 1
            return val
        inst._randrange = randrange
        result = inst.new_objectid()
        # cant get 0 back, it's irresolveable
        self.assertEqual(result, 1)
        
    def test_new_objectid_notempty(self):
        inst = self._makeOne()
        times = [0]
        def randrange(frm, to):
            val = times[0]
            times[0] = times[0] + 1
            return val
        inst._randrange = randrange
        inst.objectid_to_path[1] = True
        result = inst.new_objectid()
        self.assertEqual(result, 2)

    def test_new_objectid_gt_maxint(self):
        inst = self._makeOne()
        oob = inst.family.maxint + 1
        times = [oob, 5]
        def randrange(frm, to):
            val = times.pop(0)
            return val
        inst._randrange = randrange
        result = inst.new_objectid()
        self.assertEqual(result, 5)

    def test_objectid_for_object(self):
        obj = testing.DummyResource()
        inst = self._makeOne()
        inst.path_to_objectid[(_BLANK,)] = 1
        self.assertEqual(inst.objectid_for(obj), 1)

    def test_objectid_for_path_tuple(self):
        inst = self._makeOne()
        inst.path_to_objectid[(_BLANK,)] = 1
        self.assertEqual(inst.objectid_for((_BLANK,)), 1)

    def test_objectid_for_nonsense(self):
        inst = self._makeOne()
        self.assertRaises(ValueError, inst.objectid_for, 'a')

    def test_path_for(self):
        inst = self._makeOne()
        inst.objectid_to_path[1] = 'abc'
        self.assertEqual(inst.path_for(1), 'abc')

    def test_object_for_int(self):
        a = testing.DummyResource()
        inst = self._makeOne()
        inst.objectid_to_path[1] = 'abc'
        inst._find_resource = lambda *arg: a
        self.assertEqual(inst.object_for(1), a)

    if IS_32_BIT: # pragma: no cover
        def test_object_for_long(self):
            a = testing.DummyResource()
            inst = self._makeOne()
            oid = sys.maxint + 1
            inst.objectid_to_path[oid] = 'abc'
            inst._find_resource = lambda *arg: a
            self.assertEqual(inst.object_for(oid), a)

    def test_object_for_path_tuple(self):
        a = testing.DummyResource()
        inst = self._makeOne()
        inst.objectid_to_path[1] = 'abc'
        inst._find_resource = lambda *arg: a
        self.assertEqual(inst.object_for((_BLANK,)), a)

    def test_object_for_unknown(self):
        inst = self._makeOne()
        self.assertRaises(ValueError, inst.object_for, None)

    def test_object_for_cantbefound(self):
        inst = self._makeOne()
        inst.objectid_to_path[1] = 'abc'
        def find_resource(*arg):
            raise KeyError('a')
        inst._find_resource = find_resource
        self.assertEqual(inst.object_for(1), None)
        
    def test_object_for_path_tuple_alternate_context(self):
        a = testing.DummyResource()
        inst = self._makeOne()
        inst.objectid_to_path[1] = 'abc'
        L= []
        def find_resource(context, path_tuple):
            L.append(context)
            return a
        inst._find_resource = find_resource
        self.assertEqual(inst.object_for((_BLANK,), 'a'), a)
        self.assertEqual(L, ['a'])

    def test_object_for_path_not_in_objectid_to_path(self):
        inst = self._makeOne()
        self.assertEqual(inst.object_for(1), None)

    def test__find_resource_no_context(self):
        self.config.testing_resources({'/a':1})
        inst = self._makeOne()
        inst.root = None
        self.assertEqual(inst._find_resource(None, ('', 'a')), 1)

    def test__find_resource_with_alternate_context(self):
        self.config.testing_resources({'/a':1})
        inst = self._makeOne()
        ctx = testing.DummyResource()
        self.assertEqual(inst._find_resource(ctx, ('', 'a')), 1)

    def test_add_moving_and_duplicating(self):
        inst = self._makeOne()
        obj = testing.DummyResource()
        self.assertRaises(ValueError, inst.add,
                          obj, (_BLANK,), True, True)
        
    def test_add_already_in_path_to_objectid(self):
        inst = self._makeOne()
        obj = testing.DummyResource()
        obj.__oid__ = 1
        inst.path_to_objectid[(_BLANK,)] = 1
        self.assertRaises(ValueError, inst.add, obj, (_BLANK,))

    def test_add_duplicating(self):
        inst = self._makeOne()
        obj = testing.DummyResource()
        obj.__oid__ = 1
        inst.path_to_objectid[(_BLANK,)] = 1
        self.assertRaises(ValueError, inst.add, obj, (_BLANK,), True)

    def test_add_already_in_objectid_to_path(self):
        inst = self._makeOne()
        obj = testing.DummyResource()
        obj.__oid__ = 1
        inst.objectid_to_path[1] = True
        self.assertRaises(ValueError, inst.add, obj, (_BLANK,))

    def test_add_not_a_path_tuple(self):
        inst = self._makeOne()
        self.assertRaises(ValueError, inst.add, None, None)

    def test_add_traversable_object(self):
        inst = self._makeOne()
        inst._v_nextid = 1
        obj = testing.DummyResource()
        inst.add(obj, (_BLANK,))
        self.assertEqual(inst.objectid_to_path[1], (_BLANK,))
        self.assertEqual(obj.__oid__, 1)
        
    def test_add_not_valid(self):
        inst = self._makeOne()
        self.assertRaises(AttributeError, inst.add, 'a', (_BLANK,))

    def test_remove_not_an_int_or_tuple(self):
        inst = self._makeOne()
        self.assertRaises(ValueError, inst.remove, 'a')

    def test_remove_int(self):
        inst = self._makeOne()
        inst.objectid_to_path[1] = (_BLANK,)
        inst.path_to_objectid[(_BLANK,)] = 1
        inst.pathindex[(_BLANK,)] = {0:[1]}
        inst.remove(1)
        self.assertEqual(dict(inst.objectid_to_path), {})

    if IS_32_BIT: # pragma: no cover
        def test_remove_long(self):
            inst = self._makeOne()
            oid = sys.maxint + 1
            inst.objectid_to_path[oid] = (_BLANK,)
            inst.path_to_objectid[(_BLANK,)] = oid
            inst.pathindex[(_BLANK,)] = {0:[oid]}
            inst.remove(oid)
            self.assertEqual(dict(inst.objectid_to_path), {})
        
    def test_remove_traversable_object(self):
        inst = self._makeOne()
        inst.objectid_to_path[1] = (_BLANK,)
        inst.path_to_objectid[(_BLANK,)] = 1
        inst.pathindex[(_BLANK,)] = {0:[1]}
        obj = testing.DummyResource()
        inst.remove(obj)
        self.assertEqual(dict(inst.objectid_to_path), {})
        
    def test_remove_no_omap(self):
        inst = self._makeOne()
        inst.objectid_to_path[1] = (_BLANK,)
        result = inst.remove((_BLANK,))
        self.assertEqual(list(result), [])

    def test_pathlookup_not_valid(self):
        inst = self._makeOne()
        self.assertRaises(ValueError, inst.pathlookup, 1)

    def test_pathlookup_traversable_object(self):
        inst = self._makeOne()
        obj = testing.DummyResource()
        gen = inst.pathlookup(obj)
        result = list(gen)
        self.assertEqual(result, [])

    def test_pathcount_not_valid(self):
        inst = self._makeOne()
        self.assertRaises(ValueError, inst.pathcount, 1)
        
    def test_pathcount_traversable_object(self):
        inst = self._makeOne()
        obj = testing.DummyResource()
        result = inst.pathcount(obj)
        self.assertEqual(result, 0)

    def test_navgen_notexist(self):
        inst = self._makeOne()
        result = inst.navgen((_BLANK,), 99)
        self.assertEqual(result, [])

    def test_navgen_bigdepth(self):
        inst = self._makeOne()
        root = resource('/')
        a = resource('/a')
        ab = resource('/a/b')
        abc = resource('/a/b/c')
        z = resource('/z')
        for thing in root, a, ab, abc, z:
            inst.add(thing, thing.path_tuple)
        result = inst.navgen(root, 99)
        self.assertEqual(
            result, 
            [{'path': ('', _A), 
              'name':_A,
              'children': [{'path': ('', _A, _B), 
                            'name':_B,
                            'children': [{'path': ('', _A, _B, _C), 
                                          'name':_C,
                                          'children': []}]}]}, 
             {'path': ('', _Z), 
              'name':_Z,
              'children': []}]
            )

    def test_navgen_bigdepth_notroot(self):
        inst = self._makeOne()
        root = resource('/')
        a = resource('/a')
        ab = resource('/a/b')
        abc = resource('/a/b/c')
        z = resource('/z')
        for thing in root, a, ab, abc, z:
            inst.add(thing, thing.path_tuple)
        result = inst.navgen(a, 99)
        self.assertEqual(
            result,
            [{'path': ('', _A, _B), 
              'name':_B,
              'children': [{'path': ('', _A, _B, _C), 
                            'name':_C,
                            'children': []}]}]
            )
        
    def test_navgen_smalldepth(self):
        inst = self._makeOne()
        root = resource('/')
        a = resource('/a')
        ab = resource('/a/b')
        abc = resource('/a/b/c')
        z = resource('/z')
        for thing in root, a, ab, abc, z:
            inst.add(thing, thing.path_tuple)
        result = inst.navgen(root, 1)
        self.assertEqual(
            result,
            [{'path': ('', _A), 
              'name':'a',
              'children': []},
             {'path': ('', _Z), 
              'name':_Z,
              'children': []}]
            )

    def test_navgen_smalldepth_notroot(self):
        inst = self._makeOne()
        root = resource('/')
        a = resource('/a')
        ab = resource('/a/b')
        abc = resource('/a/b/c')
        z = resource('/z')
        for thing in root, a, ab, abc, z:
            inst.add(thing, thing.path_tuple)
        result = inst.navgen(a, 1)
        self.assertEqual(
            result,
            [{'path': ('', _A, _B), 
              'name':_B,
              'children': []}]
            )
        
    def test_navgen_nodepth(self):
        inst = self._makeOne()
        root = resource('/')
        a = resource('/a')
        ab = resource('/a/b')
        abc = resource('/a/b/c')
        z = resource('/z')
        for thing in root, a, ab, abc, z:
            inst.add(thing, thing.path_tuple)
        result = inst.navgen(root, 0)
        self.assertEqual(result, [])

    def test_navgen_nodepth_notroot(self):
        inst = self._makeOne()
        root = resource('/')
        a = resource('/a')
        ab = resource('/a/b')
        abc = resource('/a/b/c')
        z = resource('/z')
        for thing in root, a, ab, abc, z:
            inst.add(thing, thing.path_tuple)
        result = inst.navgen(a, 0)
        self.assertEqual(result, [])

    def test_get_extent(self):
        inst = self._makeOne()
        root = resource('/')
        a = resource('/a')
        ab = resource('/a/b')
        abc = resource('/a/b/c')
        z = resource('/z')
        for thing in root, a, ab, abc, z:
            inst.add(thing, thing.path_tuple)
        result = inst.get_extent('pyramid.testing.DummyResource')
        self.assertEqual(len(sorted(list(result))), 5)

    def test_get_extent_missing_default(self):
        inst = self._makeOne()
        result = inst.get_extent('pyramid.testing.DummyResource')
        self.assertEqual(result, ())

    def test_get_extent_missing_nondefault(self):
        inst = self._makeOne()
        result = inst.get_extent('pyramid.testing.DummyResource', None)
        self.assertEqual(result, None)

    def test_functional(self):

        def l(path, depth=None, include_origin=True):
            path_tuple = split(path)
            oids = sorted(
                list(objmap.pathlookup(path_tuple, depth, include_origin))
                )
            count = objmap.pathcount(path_tuple, depth, include_origin)
            return oids, count

        objmap = self._makeOne()
        objmap._v_nextid = 1

        root = resource('/')
        a = resource('/a')
        ab = resource('/a/b')
        abc = resource('/a/b/c')
        z = resource('/z')

        oid1 = objmap.add(ab, ab.path_tuple)
        oid2 = objmap.add(abc, abc.path_tuple)
        oid3 = objmap.add(a, a.path_tuple)
        oid4 = objmap.add(root, root.path_tuple)
        oid5 = objmap.add(z, z.path_tuple)

        # /
        nodepth = l('/')
        assert nodepth == ([oid1, oid2, oid3, oid4, oid5], 5), nodepth
        depth0 = l('/', depth=0)
        assert depth0 == ([oid4], 1), depth0
        depth1 = l('/', depth=1)
        assert depth1 == ([oid3, oid4, oid5], 3), depth1
        depth2 = l('/', depth=2)
        assert depth2 == ([oid1, oid3, oid4, oid5], 4), depth2
        depth3 = l('/', depth=3)
        assert depth3 == ([oid1, oid2, oid3, oid4, oid5], 5), depth3
        depth4 = l('/', depth=4)
        assert depth4 == ([oid1, oid2, oid3, oid4, oid5], 5), depth4

        # /a
        nodepth = l('/a')
        assert nodepth == ([oid1, oid2, oid3], 3), nodepth
        depth0 = l('/a', depth=0)
        assert depth0 == ([oid3], 1), depth0
        depth1 = l('/a', depth=1)
        assert depth1 == ([oid1, oid3], 2), depth1
        depth2 = l('/a', depth=2)
        assert depth2 == ([oid1, oid2, oid3], 3), depth2
        depth3 = l('/a', depth=3)
        assert depth3 == ([oid1, oid2, oid3], 3), depth3

        # /a/b
        nodepth = l('/a/b')
        assert nodepth == ([oid1, oid2], 2), nodepth
        depth0 = l('/a/b', depth=0)
        assert depth0 == ([oid1], 1), depth0
        depth1 = l('/a/b', depth=1)
        assert depth1 == ([oid1, oid2], 2), depth1
        depth2 = l('/a/b', depth=2)
        assert depth2 == ([oid1, oid2], 2), depth2

        # /a/b/c
        nodepth = l('/a/b/c')
        assert nodepth == ([oid2], 1), nodepth
        depth0 = l('/a/b/c', depth=0)
        assert depth0 == ([oid2], 1), depth0
        depth1 = l('/a/b/c', depth=1)
        assert depth1 == ([oid2], 1), depth1

        # remove '/a/b'
        removed = objmap.remove(oid1)
        assert set(removed) == set([1,2])

        # /a/b/c
        nodepth = l('/a/b/c')
        assert nodepth == ([], 0), nodepth
        depth0 = l('/a/b/c', depth=0)
        assert depth0 == ([], 0), depth0
        depth1 = l('/a/b/c', depth=1)
        assert depth1 == ([], 0), depth1

        # /a/b
        nodepth = l('/a/b')
        assert nodepth == ([], 0), nodepth
        depth0 = l('/a/b', depth=0)
        assert depth0 == ([], 0), depth0
        depth1 = l('/a/b', depth=1)
        assert depth1 == ([], 0), depth1

        # /a
        nodepth = l('/a')
        assert nodepth == ([oid3], 1), nodepth
        depth0 = l('/a', depth=0)
        assert depth0 == ([oid3], 1), depth0
        depth1 = l('/a', depth=1)
        assert depth1 == ([oid3], 1), depth1

        # /
        nodepth = l('/')
        assert nodepth == ([oid3, oid4, oid5], 3), nodepth
        depth0 = l('/', depth=0)
        assert depth0 == ([oid4], 1), depth0
        depth1 = l('/', depth=1)
        assert depth1 == ([oid3, oid4, oid5], 3), depth1

        # test include_origin false with /, no depth
        nodepth = l('/', include_origin=False)
        assert nodepth == ([oid3, oid5], 2), nodepth

        # test include_origin false with /, depth=1
        depth1 = l('/', include_origin=False, depth=0)
        assert depth1 == ([], 0), depth1
        
        pathindex = objmap.pathindex
        keys = list(pathindex.keys())

        self.assertEqual(
            keys,
            [(_BLANK,), (_BLANK, _A), (_BLANK, _Z)]
        )

        root = pathindex[(_BLANK,)]
        self.assertEqual(len(root), 2)
        self.assertEqual(set(root[0]), set([4]))
        self.assertEqual(set(root[1]), set([3,5]))

        a = pathindex[(_BLANK, _A)]
        self.assertEqual(len(a), 1)
        self.assertEqual(set(a[0]), set([3]))

        z = pathindex[(_BLANK, _Z)]
        self.assertEqual(len(z), 1)
        self.assertEqual(set(z[0]), set([5]))
        
        self.assertEqual(
            dict(objmap.objectid_to_path),
            {3: (_BLANK, _A), 4: (_BLANK,), 5: (_BLANK, _Z)})
        self.assertEqual(
            dict(objmap.path_to_objectid),
            {(_BLANK, _Z): 5, (_BLANK, _A): 3, (_BLANK,): 4})

        # remove '/'
        removed = objmap.remove((_BLANK,))
        self.assertEqual(set(removed), set([3,4,5]))

        assert dict(objmap.pathindex) == {}
        assert dict(objmap.objectid_to_path) == {}
        assert dict(objmap.path_to_objectid) == {}

    def test__refids_for_source_missing(self):
        inst = self._makeOne()
        self.assertRaises(ValueError, inst._refids_for, 1, 2)
        
    def test__refids_for_target_missing(self):
        inst = self._makeOne()
        inst.objectid_to_path[1] = (_BLANK,)
        self.assertRaises(ValueError, inst._refids_for, 1, 2)

    def test__refids_for_success_oids(self):
        inst = self._makeOne()
        inst.objectid_to_path[1] = (_BLANK,)
        inst.objectid_to_path[2] = (_BLANK,)
        s, t = inst._refids_for(1, 2)
        self.assertEqual(s, 1)
        self.assertEqual(t, 2)

    def test__refids_for_success_objects(self):
        inst = self._makeOne()
        one = testing.DummyResource()
        one.__oid__ = 1
        two = testing.DummyResource()
        two.__oid__ = 2
        inst.objectid_to_path[1] = (_BLANK,)
        inst.objectid_to_path[2] = (_BLANK,)
        s, t = inst._refids_for(one, two)
        self.assertEqual(s, 1)
        self.assertEqual(t, 2)
        
    def test__refid_for_missing(self):
        inst = self._makeOne()
        self.assertRaises(ValueError, inst._refid_for, 1)
        
    def test__refid_for_success_oid(self):
        inst = self._makeOne()
        inst.objectid_to_path[1] = (_BLANK,)
        oid = inst._refid_for(1)
        self.assertEqual(oid, 1)

    def test__refid_for_success_object(self):
        inst = self._makeOne()
        obj = testing.DummyResource()
        obj.__oid__ = 1
        inst.objectid_to_path[1] = (_BLANK,)
        oid = inst._refid_for(obj)
        self.assertEqual(oid, 1)

    def test_connect(self):
        inst = self._makeOne()
        inst.objectid_to_path[1] = (_BLANK,)
        inst.objectid_to_path[2] = (_BLANK, _A)
        inst.referencemap = DummyReferenceMap()
        inst.connect(1, 2, 'ref')
        self.assertEqual(inst.referencemap['ref'], (1, 2))

    def test_disconnect(self):
        inst = self._makeOne()
        inst.objectid_to_path[1] = (_BLANK,)
        inst.objectid_to_path[2] = (_BLANK, _A)
        inst.referencemap = DummyReferenceMap()
        inst.referencemap['ref'] = True
        inst.disconnect(1, 2, 'ref')
        self.assertTrue('ref' not in inst.referencemap)

    def test_disconnect_with_objects(self):
        one = testing.DummyResource(__oid__=1)
        two = testing.DummyResource(__oid__=2)
        inst = self._makeOne()
        inst.objectid_to_path[1] = (_BLANK,)
        inst.objectid_to_path[2] = (_BLANK, _A)
        inst.referencemap = DummyReferenceMap()
        inst.referencemap['ref'] = True
        inst.disconnect(one, two, 'ref')
        self.assertTrue('ref' not in inst.referencemap)

    def test__oidset_not_listset(self):
        inst = self._makeOne()
        oidset = inst._oidset([1,2,3])
        self.assertEqual(oidset.__class__, inst.family.OO.Set)
        self.assertEqual(list(sorted(list(oidset))), [1,2,3])
        
    def test__oidset_is_listset(self):
        from substanced.objectmap import ListSet
        inst = self._makeOne()
        listset = ListSet([1,2,3])
        oidset = inst._oidset(listset)
        self.assertEqual(oidset.__class__, ListSet)
        self.assertTrue(oidset is not listset)
        self.assertEqual(list(sorted(list(oidset))), [1,2,3])
        
    def test_sourceids(self):
        inst = self._makeOne()
        inst.objectid_to_path[1] = (_BLANK,)
        inst.referencemap = DummyReferenceMap(sourceids=[2])
        self.assertEqual(list(inst.sourceids(1, 'ref')), [2])
        
    def test_targetids(self):
        inst = self._makeOne()
        inst.objectid_to_path[1] = (_BLANK,)
        inst.referencemap = DummyReferenceMap(targetids=[2])
        self.assertEqual(list(inst.targetids(1, 'ref')), [2])

    def test_sources(self):
        inst = self._makeOne()
        inst.objectid_to_path[1] = (_BLANK,)
        inst.objectid_to_path[2] = (_BLANK, _A)
        inst.objectid_to_path[3] = (_BLANK, _B)
        inst.referencemap = DummyReferenceMap(sourceids=[2, 3])
        obj = object()
        inst._find_resource = lambda *arg: obj
        self.assertEqual(list(inst.sources(1, 'ref')), [obj, obj])
        
    def test_targets(self):
        inst = self._makeOne()
        inst.objectid_to_path[1] = (_BLANK,)
        inst.objectid_to_path[2] = (_BLANK, _A)
        inst.objectid_to_path[3] = (_BLANK, _B)
        inst.referencemap = DummyReferenceMap(targetids=[2, 3])
        obj = object()
        inst._find_resource = lambda *arg: obj
        self.assertEqual(list(inst.targets(1, 'ref')), [obj, obj])

    def test_has_references_obj(self):
        inst = self._makeOne()
        inst.referencemap = DummyReferenceMap(has_references=True)
        inst.objectid_to_path[1] = (_BLANK,)
        obj = testing.DummyResource()
        obj.__oid__ = 1
        self.assertTrue(inst.has_references(obj))
        self.assertEqual(inst.referencemap.oid_arg, 1)
        self.assertEqual(inst.referencemap.reftype_arg, None)

    def test_has_references_oid(self):
        inst = self._makeOne()
        inst.referencemap = DummyReferenceMap(has_references=True)
        inst.objectid_to_path[1] = (_BLANK,)
        self.assertTrue(inst.has_references(1))
        self.assertEqual(inst.referencemap.oid_arg, 1)
        self.assertEqual(inst.referencemap.reftype_arg, None)

    def test_has_references_with_reftype(self):
        inst = self._makeOne()
        inst.referencemap = DummyReferenceMap(has_references=True)
        inst.objectid_to_path[1] = (_BLANK,)
        self.assertTrue(inst.has_references(1, 'abc'))
        self.assertEqual(inst.referencemap.oid_arg, 1)
        self.assertEqual(inst.referencemap.reftype_arg, 'abc')

    def test_get_reftypes(self):
        inst = self._makeOne()
        inst.referencemap = DummyReferenceMap(reftypes=(1,2))
        self.assertTrue(inst.get_reftypes(), (1,2))

    def test_order_sources_order_is_None(self):
        inst = self._makeOne()
        refmap = DummyReferenceMap()
        inst.referencemap = refmap
        result = inst.order_sources(1, 'reftype', None)
        self.assertEqual(refmap.sources_ordered, [(1, 'reftype', None)])
        self.assertEqual(result, None)

    def test_order_sources_order_is__marker(self):
        from substanced.objectmap import _marker
        inst = self._makeOne()
        refmap = DummyReferenceMap()
        inst.referencemap = refmap
        result = inst.order_sources(1, 'reftype', _marker)
        self.assertEqual(refmap.sources_ordered, [(1, 'reftype', _marker)])
        self.assertEqual(result, _marker)

    def test_order_sources_order_is_oidlist(self):
        inst = self._makeOne()
        refmap = DummyReferenceMap()
        inst.referencemap = refmap
        inst.objectid_to_path = {2:True, 3:True}
        result = inst.order_sources(1, 'reftype', [2,3])
        self.assertEqual(refmap.sources_ordered, [(1, 'reftype', [2,3])])
        self.assertEqual(result, [2,3])

    def test_order_sources_order_is_objectlist(self):
        inst = self._makeOne()
        refmap = DummyReferenceMap()
        inst.referencemap = refmap
        one = testing.DummyResource()
        one.__oid__ = 1
        two = testing.DummyResource()
        two.__oid__ = 2
        inst.objectid_to_path = {1:True, 2:True}
        result = inst.order_sources(1, 'reftype', [one, two])
        self.assertEqual(refmap.sources_ordered, [(1, 'reftype', [1,2])])
        self.assertEqual(result, [1,2])

    def test_order_targets_order_is_None(self):
        inst = self._makeOne()
        refmap = DummyReferenceMap()
        inst.referencemap = refmap
        result = inst.order_targets(1, 'reftype', None)
        self.assertEqual(refmap.targets_ordered, [(1, 'reftype', None)])
        self.assertEqual(result, None)

    def test_order_targets_order_is__marker(self):
        from substanced.objectmap import _marker
        inst = self._makeOne()
        refmap = DummyReferenceMap()
        inst.referencemap = refmap
        result = inst.order_targets(1, 'reftype', _marker)
        self.assertEqual(refmap.targets_ordered, [(1, 'reftype', _marker)])
        self.assertEqual(result, _marker)

    def test_order_targets_order_is_oidlist(self):
        inst = self._makeOne()
        refmap = DummyReferenceMap()
        inst.referencemap = refmap
        inst.objectid_to_path = {2:True, 3:True}
        result = inst.order_targets(1, 'reftype', [2,3])
        self.assertEqual(refmap.targets_ordered, [(1, 'reftype', [2,3])])
        self.assertEqual(result, [2,3])

    def test_order_targets_order_is_objectlist(self):
        inst = self._makeOne()
        refmap = DummyReferenceMap()
        inst.referencemap = refmap
        one = testing.DummyResource()
        one.__oid__ = 1
        two = testing.DummyResource()
        two.__oid__ = 2
        inst.objectid_to_path = {1:True, 2:True}
        result = inst.order_targets(1, 'reftype', [one, two])
        self.assertEqual(refmap.targets_ordered, [(1, 'reftype', [1,2])])
        self.assertEqual(result, [1,2])
        
class TestReferenceSet(unittest.TestCase):
    def _makeOne(self):
        from .. import ReferenceSet
        return ReferenceSet()

    def test_connect_empty(self):
        refset = self._makeOne()
        refset.connect(1, 2)
        self.assertEqual(list(refset.src2target[1]), [2])
        self.assertEqual(list(refset.target2src[2]), [1])
        
    def test_connect_nonempty_overlap(self):
        refset = self._makeOne()
        refset.src2target[1] = DummyTreeSet([2])
        refset.target2src[2] = DummyTreeSet([1])
        refset.connect(1, 2)
        self.assertEqual(list(refset.src2target[1]), [2])
        self.assertEqual(list(refset.target2src[2]), [1])

    def test_connect_nonempty_nonoverlap(self):
        refset = self._makeOne()
        refset.src2target[1] = DummyTreeSet([3])
        refset.target2src[2] = DummyTreeSet([4])
        refset.connect(1, 2)
        self.assertEqual(sorted(list(refset.src2target[1])), [2, 3])
        self.assertEqual(sorted(list(refset.target2src[2])), [1, 4])

    def test_disconnect_empty(self):
        refset = self._makeOne()
        refset.disconnect(1, 2)
        self.assertEqual(list(refset.src2target.keys()), [])
        self.assertEqual(list(refset.target2src.keys()), [])
        
    def test_disconnect_nonempty(self):
        refset = self._makeOne()
        refset.src2target[1] = DummyTreeSet([2, 3])
        refset.target2src[2] = DummyTreeSet([1, 4])
        refset.disconnect(1, 2)
        self.assertEqual(list(refset.src2target[1]), [3])
        self.assertEqual(list(refset.target2src[2]), [4])

    def test_disconnect_keyerrors(self):
        refset = self._makeOne()
        refset.src2target[1] = DummyTreeSet()
        refset.target2src[2] = DummyTreeSet()
        refset.disconnect(1, 2)
        self.assertEqual(list(refset.src2target[1]), [])
        self.assertEqual(list(refset.target2src[2]), [])

    def test_targetids(self):
        refset = self._makeOne()
        dummyset = DummyTreeSet([1])
        refset.src2target[1] = dummyset
        self.assertEqual(refset.targetids(1), dummyset)
        
    def test_sourceids(self):
        refset = self._makeOne()
        dummyset = DummyTreeSet([1])
        refset.target2src[1] = dummyset
        self.assertEqual(refset.sourceids(1), dummyset)

    def test_remove_empty(self):
        refset = self._makeOne()
        self.assertEqual(list(refset.remove([1,2])), [])

    def test_remove_notempty(self):
        # emulate the result of:
        # connect(1, 2)
        # connect(3, 4)
        # connect(2, 4)
        # connect(2, 1)
        # connect(3, 5)
        src2target = {1:DummyTreeSet([2]), 3:DummyTreeSet([4, 5]), 
                      2:DummyTreeSet([4, 1])}
        target2src = {2:DummyTreeSet([1]), 4:DummyTreeSet([3, 2]),
                      1:DummyTreeSet([2]), 5:DummyTreeSet([3])}
        refset = self._makeOne()
        refset.src2target = src2target
        refset.target2src = target2src
        oids = [1,4, 10]
        result = refset.remove(oids)
        self.assertEqual(list(result), [1,4]) # 10 unmentioned
        self.assertEqual(
            src2target,
            {3:DummyTreeSet([5])}
            )
        self.assertEqual(
            target2src,
            {5:DummyTreeSet([3])}
            )

    def test_is_target_True(self):
        refset = self._makeOne()
        refset.target2src[1] = True
        self.assertTrue(refset.is_target(1))

    def test_is_target_False(self):
        refset = self._makeOne()
        self.assertFalse(refset.is_target(1))

    def test_is_source_True(self):
        refset = self._makeOne()
        refset.src2target[1] = True
        self.assertTrue(refset.is_source(1))

    def test_is_source_False(self):
        refset = self._makeOne()
        self.assertFalse(refset.is_source(1))

    def test_order_targets_oid_exists_order_is_None(self):
        refset = self._makeOne()
        refset.src2target[1] = refset.oidlist_class([2])
        oids = refset.order_targets(1, None)
        self.assertEqual(oids.__class__, refset.oidset_class)
        self.assertEqual(list(oids), [2])

    def test_order_targets_oid_missing_order_is_None(self):
        refset = self._makeOne()
        oids = refset.order_targets(1, None)
        self.assertEqual(list(oids), [])
        self.assertFalse(1 in refset.src2target)

    def test_order_targets_oid_points_at_OOSet_order_is_None(self):
        refset = self._makeOne()
        oidset = refset.oidset_class([1])
        refset.src2target[1] = oidset
        oids = refset.order_targets(1, None)
        self.assertTrue(oids is oidset)
        self.assertTrue(refset.src2target[1] is oidset)

    def test_order_targets_invalid_extra_oid_doesnt_exist(self):
        refset = self._makeOne()
        self.assertRaises(ValueError, refset.order_targets, 1, [2])

    def test_order_targets_invalid_extra_oid_exists(self):
        refset = self._makeOne()
        oidset = refset.oidset_class([1])
        refset.src2target[1] = oidset
        self.assertRaises(ValueError, refset.order_targets, 1, [2])

    def test_order_targets_invalid_missing_oid_doesnt_exist(self):
        refset = self._makeOne()
        oidset = refset.oidset_class([1, 2])
        refset.src2target[1] = oidset
        self.assertRaises(ValueError, refset.order_targets, 1, [2])

    def test_order_targets_invalid_missing_oid_exists(self):
        refset = self._makeOne()
        oidset = refset.oidset_class([1, 2])
        refset.src2target[1] = oidset
        self.assertRaises(ValueError, refset.order_targets, 1, [2])

    def test_order_targets_valid_oid_doesnt_exist_with_missing_default(self):
        refset = self._makeOne()
        oids = refset.order_targets(1)
        self.assertEqual(refset.oidlist_class(), oids)

    def test_order_targets_valid_oid_doesnt_exist_with_missing_speced(self):
        refset = self._makeOne()
        oids = refset.order_targets(1, [])
        self.assertEqual(refset.oidlist_class(), oids)
        
    def test_order_targets_valid_oid_exists(self):
        refset = self._makeOne()
        oidset = refset.oidset_class([2, 3])
        refset.src2target[1] = oidset
        oids = refset.order_targets(1, [3,2])
        self.assertEqual(oids, refset.oidlist_class([3,2]))
        self.assertEqual(oids, refset.src2target[1])

    def test_order_sources_oid_exists_order_is_None(self):
        refset = self._makeOne()
        refset.target2src[1] = refset.oidlist_class([2])
        oids = refset.order_sources(1, None)
        self.assertEqual(oids.__class__, refset.oidset_class)
        self.assertEqual(list(oids), [2])

    def test_order_sources_oid_missing_order_is_None(self):
        refset = self._makeOne()
        oids = refset.order_sources(1, None)
        self.assertEqual(list(oids), [])
        self.assertFalse(1 in refset.target2src)

    def test_order_sources_oid_points_at_OOSet_order_is_None(self):
        refset = self._makeOne()
        oidset = refset.oidset_class([1])
        refset.target2src[1] = oidset
        oids = refset.order_sources(1, None)
        self.assertTrue(oids is oidset)
        self.assertTrue(refset.target2src[1] is oidset)

    def test_order_sources_invalid_extra_oid_doesnt_exist(self):
        refset = self._makeOne()
        self.assertRaises(ValueError, refset.order_sources, 1, [2])

    def test_order_sources_invalid_extra_oid_exists(self):
        refset = self._makeOne()
        oidset = refset.oidset_class([1])
        refset.target2src[1] = oidset
        self.assertRaises(ValueError, refset.order_sources, 1, [2])

    def test_order_sources_invalid_missing_oid_doesnt_exist(self):
        refset = self._makeOne()
        oidset = refset.oidset_class([1, 2])
        refset.target2src[1] = oidset
        self.assertRaises(ValueError, refset.order_sources, 1, [2])

    def test_order_sources_invalid_missing_oid_exists(self):
        refset = self._makeOne()
        oidset = refset.oidset_class([1, 2])
        refset.target2src[1] = oidset
        self.assertRaises(ValueError, refset.order_sources, 1, [2])

    def test_order_sources_valid_oid_doesnt_exist_with_missing_default(self):
        refset = self._makeOne()
        oids = refset.order_sources(1)
        self.assertEqual(refset.oidlist_class(), oids)

    def test_order_sources_valid_oid_doesnt_exist_with_missing_speced(self):
        refset = self._makeOne()
        oids = refset.order_sources(1, [])
        self.assertEqual(refset.oidlist_class(), oids)
        
    def test_order_sources_valid_oid_exists(self):
        refset = self._makeOne()
        oidset = refset.oidset_class([2, 3])
        refset.target2src[1] = oidset
        oids = refset.order_sources(1, [3,2])
        self.assertEqual(oids, refset.oidlist_class([3,2]))
        self.assertEqual(oids, refset.target2src[1])

class TestListSet(unittest.TestCase):
    def _makeOne(self, *arg, **kw):
        from substanced.objectmap import ListSet
        return ListSet(*arg, **kw)

    def test_insert(self):
        inst = self._makeOne()
        inst.insert('foo')
        self.assertEqual(inst, self._makeOne(['foo']))

    def test___repr__(self):
        inst = self._makeOne(['foo'])
        self.assertEqual(repr(inst), "<ListSet: ['foo']>")
        
class TestReferenceMap(unittest.TestCase):
    def _makeOne(self, map=None):
        from .. import ReferenceMap
        return ReferenceMap(map)

    def test_ctor(self):
        refs = self._makeOne()
        self.assertEqual(refs.refmap.__class__.__name__, 'OOBTree')

    def test_connect(self):
        refset = DummyReferenceSet()
        map = {'reftype':refset}
        refs = self._makeOne(map)
        refs.connect('a', 'b', 'reftype')
        self.assertEqual(refset.connected, [('a', 'b')])
        
    def test_disconnect(self):
        refset = DummyReferenceSet()
        map = {'reftype':refset}
        refs = self._makeOne(map)
        refs.disconnect('a', 'b', 'reftype')
        self.assertEqual(refset.disconnected, [('a', 'b')])

    def test_targetids_no_refset(self):
        refs = self._makeOne()
        self.assertEqual(list(refs.targetids('a', 'reftype')), [])
        
    def test_targetids_with_refset(self):
        refset = DummyReferenceSet(['123'])
        map = {'reftype':refset}
        refs = self._makeOne(map)
        self.assertEqual(list(refs.targetids('a', 'reftype')), ['123'])

    def test_sourceids_no_refset(self):
        refs = self._makeOne()
        self.assertEqual(list(refs.sourceids('a', 'reftype')), [])
        
    def test_sourceids_with_refset(self):
        refset = DummyReferenceSet(['123'])
        map = {'reftype':refset}
        refs = self._makeOne(map)
        self.assertEqual(list(refs.sourceids('a', 'reftype')), ['123'])

    def test_remove(self):
        L = []
        refset1 = DummyReferenceSet()
        refset2 = DummyReferenceSet()
        refset1.remove = lambda oids: L.append(oids)
        refset2.remove = lambda oids: L.append(oids)
        map = {'reftype':refset1, 'reftype2':refset2}
        refs = self._makeOne(map)
        refs.remove([1,2])
        self.assertEqual(L, [[1,2], [1,2]])

    def test_has_references_True(self):
        refset = DummyReferenceSet(True)
        map = {'reftype':refset}
        refs = self._makeOne(map)
        self.assertTrue(refs.has_references(1))

    def test_has_references_False(self):
        refset = DummyReferenceSet(False)
        map = {'reftype':refset}
        refs = self._makeOne(map)
        self.assertFalse(refs.has_references(1))

    def test_has_references_with_reftype(self):
        refset = DummyReferenceSet(True)
        map = {'reftype':refset}
        refs = self._makeOne(map)
        self.assertTrue(refs.has_references(1, 'reftype'))

    def test_get_reftypes(self):
        map = {'reftype':None}
        refs = self._makeOne(map)
        self.assertEqual(list(refs.get_reftypes()), ['reftype'])

    def test_order_sources_with_refset(self):
        refset = DummyReferenceSet()
        map = {'reftype':refset}
        refs = self._makeOne(map)
        result = refs.order_sources('a', 'reftype', [1, 2, 3])
        self.assertEqual(result, [1,2,3])
        self.assertEqual(refset.sources_ordered, [('a', [1,2,3])])

    def test_order_sources_without_refset(self):
        refs = self._makeOne()
        result = refs.order_sources('a', 'reftype', [])
        self.assertEqual(result, [])
        refset = refs.refmap['reftype']
        self.assertEqual(
            refset.target2src['a'], refset.oidlist_class()
            )

    def test_order_sources_without_refset_order_missing(self):
        refs = self._makeOne()
        result = refs.order_sources('a', 'reftype')
        self.assertEqual(result, [])
        refset = refs.refmap['reftype']
        self.assertEqual(
            refset.target2src['a'], refset.oidlist_class()
            )
        
    def test_order_targets_with_refset(self):
        refset = DummyReferenceSet()
        map = {'reftype':refset}
        refs = self._makeOne(map)
        result = refs.order_targets('a', 'reftype', [1, 2, 3])
        self.assertEqual(result, [1,2,3])
        self.assertEqual(refset.targets_ordered, [('a', [1,2,3])])

    def test_order_targets_without_refset(self):
        refs = self._makeOne()
        result = refs.order_targets('a', 'reftype', [])
        self.assertEqual(result, [])
        refset = refs.refmap['reftype']
        self.assertEqual(
            refset.src2target['a'], refset.oidlist_class()
            )
        
    def test_order_targets_without_refset_order_missing(self):
        refs = self._makeOne()
        result = refs.order_targets('a', 'reftype')
        self.assertEqual(result, [])
        refset = refs.refmap['reftype']
        self.assertEqual(
            refset.src2target['a'], refset.oidlist_class()
            )
        
        
class TestExtentMap(unittest.TestCase):
    def _makeOne(self):
        from .. import ExtentMap
        return ExtentMap()

    def test_ctor(self):
        inst = self._makeOne()
        self.assertEqual(list(inst.extent_to_oids.items()), [])
        self.assertEqual(list(inst.oid_to_extents.items()), [])

    def test_add_and_remove(self):
        inst = self._makeOne()
        obj = Dummy()
        inst.add(obj, 1)
        inst.add(obj, 2)
        dummy_dotted = 'substanced.objectmap.tests.test_init.Dummy'
        self.assertEqual(
            list(inst.extent_to_oids.keys()),
            [dummy_dotted]
            )
        self.assertEqual(
            sorted(list(inst.extent_to_oids[dummy_dotted])),
            [1, 2]
            )
        self.assertEqual(
            sorted(list(inst.oid_to_extents.keys())),
            [1, 2]
            )
        self.assertEqual(
            list(inst.oid_to_extents[1]),
            [dummy_dotted]
            )
        inst.remove([2])
        self.assertEqual(
            list(inst.extent_to_oids.keys()),
            [dummy_dotted]
            )
        self.assertEqual(
            sorted(list(inst.extent_to_oids[dummy_dotted])),
            [1]
            )
        self.assertEqual(
            sorted(list(inst.oid_to_extents.keys())),
            [1]
            )
        self.assertEqual(
            list(inst.oid_to_extents[1]),
            [dummy_dotted]
            )
        inst.remove([1])
        self.assertEqual(
            list(inst.extent_to_oids.keys()),
            []
            )
        self.assertFalse(dummy_dotted in inst.extent_to_oids)

    def test_get(self):
        inst = self._makeOne()
        dummy_dotted = 'substanced.objectmap.tests.test_init.Dummy'
        obj = Dummy()
        inst.add(obj, 1)
        self.assertEqual(
            sorted(list(inst.get(dummy_dotted))),
            [1]
            )
        self.assertEqual(inst.get('foo', 'bar'), 'bar')
        self.assertEqual(inst.get('foo'), None)

class Test_reference_sourceid_property(unittest.TestCase):
    def setUp(self):
        from substanced.interfaces import IFolder
        @implementer(IFolder)
        class DummyFolder(dict):
            pass
        self.DummyFolder = DummyFolder

    def _makeInst(self, reftype=None):
        if reftype is None:
            reftype = Dummy
        from .. import reference_sourceid_property
        class Inner(self.DummyFolder):
            prop = reference_sourceid_property(reftype)
        inst = Inner()
        return inst

    def test_get_no_targetids(self):
        inst = self._makeInst()
        objectmap = DummyObjectMap(targetids=())
        inst.__objectmap__ = objectmap
        self.assertEqual(inst.prop, None)

    def test_get_one_targetid(self):
        inst = self._makeInst()
        objectmap = DummyObjectMap(targetids=(1,))
        inst.__objectmap__ = objectmap
        self.assertEqual(inst.prop, 1)

    def test_get_get_one_targetid(self):
        inst = self._makeInst()
        objectmap = DummyObjectMap(targetids=(1,2))
        inst.__objectmap__ = objectmap
        self.assertRaises(AssertionError, getattr, inst, 'prop')

    def test_del_no_target_id(self):
        inst = self._makeInst()
        objectmap = DummyObjectMap(targetids=())
        inst.__objectmap__ = objectmap
        del inst.prop
        self.assertEqual(inst.prop, None)

    def test_del_one_targetid(self):
        inst = self._makeInst()
        objectmap = DummyObjectMap(targetids=(1,))
        inst.__objectmap__ = objectmap
        del inst.prop
        self.assertEqual(objectmap.disconnected, [(inst, 1, Dummy)])

    def test_set_None(self):
        inst = self._makeInst()
        objectmap = DummyObjectMap(targetids=())
        inst.__objectmap__ = objectmap
        inst.prop = None
        self.assertEqual(objectmap.connected, [])

    def test_set_colander_null(self):
        from colander import null
        inst = self._makeInst()
        objectmap = DummyObjectMap(targetids=(1,))
        inst.__objectmap__ = objectmap
        inst.prop = null
        self.assertEqual(inst.prop, 1)
        self.assertEqual(objectmap.disconnected, [])

    def test_set_not_None(self):
        inst = self._makeInst()
        objectmap = DummyObjectMap(targetids=())
        inst.__objectmap__ = objectmap 
        inst.prop = 2
        self.assertEqual(objectmap.connected, [(inst, 2, Dummy)])

class Test_reference_targetid_property(unittest.TestCase):
    def setUp(self):
        from substanced.interfaces import IFolder
        @implementer(IFolder)
        class DummyFolder(dict):
            pass
        self.DummyFolder = DummyFolder

    def _makeInst(self, reftype=None):
        if reftype is None:
            reftype = Dummy
        from .. import reference_targetid_property
        class Inner(self.DummyFolder):
            prop = reference_targetid_property(reftype)
        inst = Inner()
        return inst

    def test_get_no_sourceids(self):
        inst = self._makeInst()
        inst.__objectmap__ = DummyObjectMap(sourceids=())
        self.assertEqual(inst.prop, None)

    def test_get_one_sourceid(self):
        inst = self._makeInst()
        inst.__objectmap__ = DummyObjectMap(sourceids=(1,))
        self.assertEqual(inst.prop, 1)

    def test_get_gt_one_sourceid(self):
        inst = self._makeInst()
        inst.__objectmap__ = DummyObjectMap(sourceids=(1,2))
        self.assertRaises(AssertionError, getattr, inst, 'prop')

    def test_del_no_source_id(self):
        inst = self._makeInst()
        inst.__objectmap__ = DummyObjectMap(sourceids=())
        del inst.prop
        self.assertEqual(inst.prop, None)

    def test_del_one_sourceid(self):
        inst = self._makeInst()
        objectmap = DummyObjectMap(sourceids=(1,))
        inst.__objectmap__ = objectmap
        del inst.prop
        self.assertEqual(objectmap.disconnected, [(1, inst, Dummy)])

    def test_set_None(self):
        inst = self._makeInst()
        objectmap = DummyObjectMap(sourceids=())
        inst.__objectmap__ = objectmap
        inst.prop = None
        self.assertEqual(objectmap.connected, [])

    def test_set_colander_null(self):
        from colander import null
        inst = self._makeInst()
        objectmap = DummyObjectMap(sourceids=(1,))
        inst.__objectmap__ = objectmap
        inst.prop = null
        self.assertEqual(inst.prop, 1)
        self.assertEqual(objectmap.disconnected, [])

    def test_set_not_None(self):
        inst = self._makeInst()
        objectmap = DummyObjectMap(sourceids=())
        inst.__objectmap__ = objectmap
        inst.prop = 2
        self.assertEqual(objectmap.connected, [(2, inst, Dummy)])

class Test_reference_source_property(unittest.TestCase):
    def setUp(self):
        from substanced.interfaces import IFolder
        @implementer(IFolder)
        class DummyFolder(dict):
            pass
        self.DummyFolder = DummyFolder

    def _makeInst(self, reftype=None):
        if reftype is None:
            reftype = Dummy
        from .. import reference_source_property
        class Inner(self.DummyFolder):
            prop = reference_source_property(reftype)
        inst = Inner()
        inst.__oid__ = 1
        return inst

    def test_get_no_targetids(self):
        inst = self._makeInst()
        objectmap = DummyObjectMap(targetids=(), result=1)
        inst.__objectmap__ = objectmap
        self.assertEqual(inst.prop, None)

    def test_get_one_targetid(self):
        inst = self._makeInst()
        ob = object()
        objectmap = DummyObjectMap(targetids=(1,), result=ob)
        inst.__objectmap__ = objectmap
        self.assertEqual(inst.prop, ob)

    def test_get_gt_one_targetid(self):
        inst = self._makeInst()
        objectmap = DummyObjectMap(targetids=(1,2))
        inst.__objectmap__ = objectmap
        self.assertRaises(AssertionError, getattr, inst, 'prop')

    def test_del_no_target_id(self):
        inst = self._makeInst()
        objectmap = DummyObjectMap(targetids=())
        inst.__objectmap__ = objectmap
        del inst.prop
        self.assertEqual(inst.prop, None)

    def test_del_one_targetid(self):
        inst = self._makeInst()
        objectmap = DummyObjectMap(targetids=(1,))
        inst.__objectmap__ = objectmap
        del inst.prop
        self.assertEqual(objectmap.disconnected, [(inst, 1, Dummy)])

    def test_set_None(self):
        inst = self._makeInst()
        objectmap = DummyObjectMap(targetids=())
        inst.__objectmap__ = objectmap
        inst.prop = None
        self.assertEqual(objectmap.connected, [])

    def test_set_colander_null(self):
        from colander import null
        inst = self._makeInst()
        ob = object()
        objectmap = DummyObjectMap(targetids=(1,), result=ob)
        inst.__objectmap__ = objectmap
        inst.prop = null
        self.assertEqual(inst.prop, ob)
        self.assertEqual(objectmap.disconnected, [])

    def test_set_not_None(self):
        inst = self._makeInst()
        objectmap = DummyObjectMap(targetids=())
        inst.__objectmap__ = objectmap
        inst.prop = 2
        self.assertEqual(objectmap.connected, [(inst, 2, Dummy)])

class Test_reference_target_property(unittest.TestCase):
    def setUp(self):
        from substanced.interfaces import IFolder
        @implementer(IFolder)
        class DummyFolder(dict):
            pass
        self.DummyFolder = DummyFolder

    def _makeInst(self, reftype=None):
        if reftype is None:
            reftype = Dummy
        from .. import reference_target_property
        class Inner(self.DummyFolder):
            prop = reference_target_property(reftype)
        inst = Inner()
        inst.__oid__ = 1
        return inst

    def test_get_no_sourceids(self):
        inst = self._makeInst()
        objectmap = DummyObjectMap(sourceids=())
        inst.__objectmap__ = objectmap
        self.assertEqual(inst.prop, None)

    def test_get_one_sourceid(self):
        inst = self._makeInst()
        ob = object()
        objectmap = DummyObjectMap(sourceids=(1,), result=ob)
        inst.__objectmap__ = objectmap
        self.assertEqual(inst.prop, ob)

    def test_get_gt_one_sourceid(self):
        inst = self._makeInst()
        objectmap = DummyObjectMap(sourceids=(1,2))
        inst.__objectmap__ = objectmap
        self.assertRaises(AssertionError, getattr, inst, 'prop')

    def test_del_no_source_id(self):
        inst = self._makeInst()
        objectmap = DummyObjectMap(sourceids=())
        inst.__objectmap__ = objectmap
        del inst.prop
        self.assertEqual(inst.prop, None)

    def test_del_one_sourceid(self):
        inst = self._makeInst()
        objectmap = DummyObjectMap(sourceids=(1,))
        inst.__objectmap__ = objectmap
        del inst.prop
        self.assertEqual(objectmap.disconnected, [(1, inst, Dummy)])

    def test_set_None(self):
        inst = self._makeInst()
        objectmap = DummyObjectMap(sourceids=())
        inst.__objectmap__ = objectmap
        inst.prop = None
        self.assertEqual(objectmap.connected, [])

    def test_set_colander_null(self):
        from colander import null
        inst = self._makeInst()
        ob = object()
        objectmap = DummyObjectMap(sourceids=(1,), result=ob)
        inst.__objectmap__ = objectmap
        inst.prop = null
        self.assertEqual(inst.prop, ob)
        self.assertEqual(objectmap.disconnected, [])

    def test_set_not_None(self):
        inst = self._makeInst()
        objectmap = DummyObjectMap(sourceids=())
        inst.__objectmap__ = objectmap
        inst.prop = 2
        self.assertEqual(objectmap.connected, [(2, inst, Dummy)])

class Test_multireference_sourceid_property(unittest.TestCase):
    def setUp(self):
        from substanced.interfaces import IFolder
        @implementer(IFolder)
        class DummyFolder(dict):
            pass
        self.DummyFolder = DummyFolder

    def _makeInst(self, reftype=None, ignore_missing=False, ordered=False):
        if reftype is None:
            reftype = Dummy
        from .. import multireference_sourceid_property
        class Inner(self.DummyFolder):
            prop = multireference_sourceid_property(
                reftype,
                ignore_missing=ignore_missing,
                ordered=ordered,
                )
        inst = Inner()
        inst.__oid__ = -1
        return inst

    def test_get_zero(self):
        inst = self._makeInst()
        objectmap = DummyObjectMap(targetids=())
        inst.__objectmap__ = objectmap
        self.assertEqual(list(inst.prop), [])

    def test_get_one(self):
        inst = self._makeInst()
        objectmap = DummyObjectMap(targetids=(1,))
        inst.__objectmap__ = objectmap
        self.assertEqual(list(inst.prop), [1])

    def test_get_two(self):
        inst = self._makeInst()
        objectmap = DummyObjectMap(targetids=(1,2))
        inst.__objectmap__ = objectmap
        self.assertEqual(list(inst.prop), [1,2])

    def test_del_zero(self):
        inst = self._makeInst()
        objectmap = DummyObjectMap(targetids=())
        inst.__objectmap__ = objectmap
        del inst.prop
        self.assertEqual(list(inst.prop), [])
        self.assertEqual(objectmap.targets_ordered, [(-1, Dummy, None)])

    def test_del_one(self):
        inst = self._makeInst()
        objectmap = DummyObjectMap(targetids=(1,))
        inst.__objectmap__ = objectmap
        del inst.prop
        self.assertEqual(objectmap.disconnected, [(-1, 1, Dummy)])
        self.assertEqual(objectmap.targets_ordered, [(-1, Dummy, None)])

    def test_del_two(self):
        inst = self._makeInst()
        objectmap = DummyObjectMap(targetids=(1,2))
        inst.__objectmap__ = objectmap
        del inst.prop
        self.assertEqual(objectmap.disconnected,
                         [(-1, 1, Dummy), (-1, 2, Dummy)])
        self.assertEqual(objectmap.targets_ordered, [(-1, Dummy, None)])

    def test_set_None(self):
        inst = self._makeInst()
        objectmap = DummyObjectMap(targetids=())
        inst.__objectmap__ = objectmap
        self.assertRaises(ValueError, inst.__setattr__, 'prop', None)
        self.assertEqual(objectmap.targets_ordered, [])

    def test_set_colander_null(self):
        from colander import null
        inst = self._makeInst()
        objectmap = DummyObjectMap(sourceids=(1,))
        inst.__objectmap__ = objectmap
        inst.prop = null
        self.assertEqual(objectmap.disconnected, [])
        self.assertEqual(objectmap.targets_ordered, [])

    def test_set_zero(self):
        inst = self._makeInst()
        objectmap = DummyObjectMap(targetids=(1,))
        inst.__objectmap__ = objectmap
        inst.prop = []
        self.assertEqual(objectmap.disconnected, [(-1, 1, Dummy)])
        self.assertEqual(objectmap.connected, [])
        self.assertEqual(objectmap.targets_ordered, [(-1, Dummy, None)]*2)

    def test_set_one(self):
        inst = self._makeInst()
        objectmap = DummyObjectMap(targetids=(1,))
        inst.__objectmap__ = objectmap
        inst.prop = [2]
        self.assertEqual(objectmap.disconnected, [(-1, 1, Dummy)])
        self.assertEqual(objectmap.connected, [(-1, 2, Dummy)])
        self.assertEqual(objectmap.targets_ordered, [(-1, Dummy, None)]*2)

    def test_set_two(self):
        inst = self._makeInst()
        objectmap = DummyObjectMap(targetids=(1,))
        inst.__objectmap__ = objectmap
        inst.prop = [2, 3]
        self.assertEqual(objectmap.disconnected, [(-1, 1, Dummy)])
        self.assertEqual(objectmap.connected,
                         [(-1, 2, Dummy), (-1, 3, Dummy)])
        self.assertEqual(objectmap.targets_ordered, [(-1, Dummy, None)]*2)

    def test_clear(self):
        inst = self._makeInst()
        objectmap = DummyObjectMap(targetids=(1,))
        inst.__objectmap__ = objectmap
        inst.prop.clear()
        self.assertEqual(objectmap.disconnected, [(-1, 1, Dummy)])
        self.assertEqual(objectmap.targets_ordered, [(-1, Dummy, None)])

    def test_connect(self):
        inst = self._makeInst()
        objectmap = DummyObjectMap(targetids=())
        inst.__objectmap__ = objectmap
        inst.prop.connect([2,3])
        self.assertEqual(objectmap.connected,
                         [(-1, 2, Dummy), (-1, 3, Dummy)])
        self.assertEqual(objectmap.targets_ordered, [(-1, Dummy, None)])

    def test_connect_with_ordering(self):
        inst = self._makeInst(ordered=True)
        objectmap = DummyObjectMap(targetids=())
        inst.__objectmap__ = objectmap
        inst.prop.connect([2,3])
        self.assertEqual(objectmap.connected,
                         [(-1, 2, Dummy), (-1, 3, Dummy)])
        self.assertEqual(objectmap.targets_ordered, [(-1, Dummy, ())])
        
    def test_connect_missing(self):
        inst = self._makeInst()
        objectmap = DummyObjectMap(targetids=(),
                                   toraise=ValueError('a'))
        inst.__objectmap__ = objectmap
        self.assertRaises(ValueError, inst.prop.connect, [2,3])
        self.assertEqual(objectmap.targets_ordered, [(-1, Dummy, None)])

    def test_connect_with_ignore_missing(self):
        inst = self._makeInst()
        objectmap = DummyObjectMap(targetids=(),
                                   toraise=ValueError('a'))
        inst.__objectmap__ = objectmap
        inst.prop.connect([2,3], ignore_missing=True)
        self.assertEqual(objectmap.connected, [])
        self.assertEqual(objectmap.targets_ordered, [(-1, Dummy, None)])

    def test_disconnect(self):
        inst = self._makeInst()
        objectmap = DummyObjectMap(targetids=())
        inst.__objectmap__ = objectmap
        inst.prop.disconnect([2,3])
        self.assertEqual(objectmap.disconnected,
                         [(-1, 2, Dummy), (-1, 3, Dummy)])
        self.assertEqual(objectmap.targets_ordered, [(-1, Dummy, None)])
        
    def test_disconnect_with_ordering(self):
        inst = self._makeInst(ordered=True)
        objectmap = DummyObjectMap(targetids=())
        inst.__objectmap__ = objectmap
        inst.prop.disconnect([2,3])
        self.assertEqual(objectmap.disconnected,
                         [(-1, 2, Dummy), (-1, 3, Dummy)])
        self.assertEqual(objectmap.targets_ordered, [(-1, Dummy, ())])
        
    def test_disconnect_missing(self):
        inst = self._makeInst()
        objectmap = DummyObjectMap(targetids=(),
                                   toraise=ValueError('a'))
        inst.__objectmap__ = objectmap
        self.assertRaises(ValueError, inst.prop.disconnect, [2,3])
        self.assertEqual(objectmap.targets_ordered, [(-1, Dummy, None)])

    def test_disconnect_with_ignore_missing(self):
        inst = self._makeInst()
        objectmap = DummyObjectMap(targetids=(),
                                   toraise=ValueError('a'))
        inst.__objectmap__ = objectmap
        inst.prop.disconnect([2,3], ignore_missing=True)
        self.assertEqual(objectmap.disconnected, [])
        self.assertEqual(objectmap.targets_ordered, [(-1, Dummy, None)])

    def test_ignore_missing_implicit(self):
        inst = self._makeInst(ignore_missing=True)
        objectmap = DummyObjectMap(targetids=(),
                                   toraise=ValueError('a'))
        inst.__objectmap__ = objectmap
        inst.prop.disconnect([2,3])
        self.assertEqual(objectmap.disconnected, [])
        self.assertEqual(objectmap.targets_ordered, [(-1, Dummy, None)])

class Test_multireference_source_property(unittest.TestCase):
    def setUp(self):
        from substanced.interfaces import IFolder
        @implementer(IFolder)
        class DummyFolder(dict):
            pass
        self.DummyFolder = DummyFolder

    def _makeInst(self, reftype=None, ignore_missing=False, ordered=False):
        if reftype is None:
            reftype = Dummy
        from .. import multireference_source_property
        class Inner(self.DummyFolder):
            prop = multireference_source_property(
                reftype,
                ignore_missing=ignore_missing,
                ordered=ordered,
                )
        inst = Inner()
        inst.__oid__ = -1
        return inst

    def test_get_zero(self):
        inst = self._makeInst()
        objectmap = DummyObjectMap(targetids=())
        inst.__objectmap__ = objectmap
        self.assertEqual(list(inst.prop), [])

    def test_get_one(self):
        inst = self._makeInst()
        objectmap = DummyObjectMap(targetids=(1,), result=object)
        inst.__objectmap__ = objectmap
        self.assertEqual(list(inst.prop), [object])

    def test_get_two(self):
        inst = self._makeInst()
        objectmap = DummyObjectMap(targetids=(1,2), result=object)
        inst.__objectmap__ = objectmap
        self.assertEqual(list(inst.prop), [object, object])

    def test_del_zero(self):
        inst = self._makeInst()
        objectmap = DummyObjectMap(targetids=())
        inst.__objectmap__ = objectmap
        del inst.prop
        self.assertEqual(list(inst.prop), [])
        self.assertEqual(objectmap.targets_ordered, [(-1, Dummy, None)])

    def test_del_one(self):
        inst = self._makeInst()
        objectmap = DummyObjectMap(targetids=(1,))
        inst.__objectmap__ = objectmap
        del inst.prop
        self.assertEqual(objectmap.disconnected, [(-1, 1, Dummy)])
        self.assertEqual(objectmap.targets_ordered, [(-1, Dummy, None)])

    def test_del_two(self):
        inst = self._makeInst()
        objectmap = DummyObjectMap(targetids=(1,2))
        inst.__objectmap__ = objectmap
        del inst.prop
        self.assertEqual(objectmap.disconnected,
                         [(-1, 1, Dummy), (-1, 2, Dummy)])
        self.assertEqual(objectmap.targets_ordered, [(-1, Dummy, None)])

    def test_set_None(self):
        inst = self._makeInst()
        objectmap = DummyObjectMap(targetids=())
        inst.__objectmap__ = objectmap
        self.assertRaises(ValueError, inst.__setattr__, 'prop', None)
        self.assertEqual(objectmap.targets_ordered, [])

    def test_set_colander_null(self):
        from colander import null
        inst = self._makeInst()
        objectmap = DummyObjectMap(targetids=(1,))
        inst.__objectmap__ = objectmap
        inst.prop = null
        self.assertEqual(objectmap.disconnected, [])
        self.assertEqual(objectmap.targets_ordered, [])

    def test_set_zero(self):
        inst = self._makeInst()
        objectmap = DummyObjectMap(targetids=(1,))
        inst.__objectmap__ = objectmap
        inst.prop = []
        self.assertEqual(objectmap.disconnected, [(-1, 1, Dummy)])
        self.assertEqual(objectmap.connected, [])
        self.assertEqual(objectmap.targets_ordered, [(-1, Dummy, None)]*2)

    def test_set_one(self):
        inst = self._makeInst()
        objectmap = DummyObjectMap(targetids=(1,))
        inst.__objectmap__ = objectmap
        inst.prop = [2]
        self.assertEqual(objectmap.disconnected, [(-1, 1, Dummy)])
        self.assertEqual(objectmap.connected, [(-1, 2, Dummy)])
        self.assertEqual(objectmap.targets_ordered, [(-1, Dummy, None)]*2)

    def test_set_two(self):
        inst = self._makeInst()
        objectmap = DummyObjectMap(targetids=(1,))
        inst.__objectmap__ = objectmap
        inst.prop = [2, 3]
        self.assertEqual(objectmap.disconnected, [(-1, 1, Dummy)])
        self.assertEqual(objectmap.connected,
                         [(-1, 2, Dummy), (-1, 3, Dummy)])
        self.assertEqual(objectmap.targets_ordered, [(-1, Dummy, None)]*2)

    def test_clear(self):
        inst = self._makeInst()
        objectmap = DummyObjectMap(targetids=(1,))
        inst.__objectmap__ = objectmap
        inst.prop.clear()
        self.assertEqual(objectmap.disconnected, [(-1, 1, Dummy)])
        self.assertEqual(objectmap.targets_ordered, [(-1, Dummy, None)])

    def test_connect(self):
        inst = self._makeInst()
        objectmap = DummyObjectMap(targetids=())
        inst.__objectmap__ = objectmap
        inst.prop.connect([2,3])
        self.assertEqual(objectmap.connected,
                         [(-1, 2, Dummy), (-1, 3, Dummy)])
        self.assertEqual(objectmap.targets_ordered, [(-1, Dummy, None)])
        
    def test_connect_with_ordering(self):
        inst = self._makeInst(ordered=True)
        objectmap = DummyObjectMap(targetids=())
        inst.__objectmap__ = objectmap
        inst.prop.connect([2,3])
        self.assertEqual(objectmap.connected,
                         [(-1, 2, Dummy), (-1, 3, Dummy)])
        self.assertEqual(objectmap.targets_ordered, [(-1, Dummy, ())])
        
    def test_connect_missing(self):
        inst = self._makeInst()
        objectmap = DummyObjectMap(targetids=(),
                                   toraise=ValueError('a'))
        inst.__objectmap__ = objectmap
        self.assertRaises(ValueError, inst.prop.connect, [2,3])
        self.assertEqual(objectmap.targets_ordered, [(-1, Dummy, None)])

    def test_connect_with_ignore_missing(self):
        inst = self._makeInst()
        objectmap = DummyObjectMap(targetids=(),
                                   toraise=ValueError('a'))
        inst.__objectmap__ = objectmap
        inst.prop.connect([2,3], ignore_missing=True)
        self.assertEqual(objectmap.connected, [])
        self.assertEqual(objectmap.targets_ordered, [(-1, Dummy, None)])

    def test_disconnect(self):
        inst = self._makeInst()
        objectmap = DummyObjectMap(targetids=())
        inst.__objectmap__ = objectmap
        inst.prop.disconnect([2,3])
        self.assertEqual(objectmap.disconnected,
                         [(-1, 2, Dummy), (-1, 3, Dummy)])
        self.assertEqual(objectmap.targets_ordered, [(-1, Dummy, None)])
        
    def test_disconnect_with_ordering(self):
        inst = self._makeInst(ordered=True)
        objectmap = DummyObjectMap(targetids=())
        inst.__objectmap__ = objectmap
        inst.prop.disconnect([2,3])
        self.assertEqual(objectmap.disconnected,
                         [(-1, 2, Dummy), (-1, 3, Dummy)])
        self.assertEqual(objectmap.targets_ordered, [(-1, Dummy, ())])
        
    def test_disconnect_missing(self):
        inst = self._makeInst()
        objectmap = DummyObjectMap(targetids=(),
                                   toraise=ValueError('a'))
        inst.__objectmap__ = objectmap
        self.assertRaises(ValueError, inst.prop.disconnect, [2,3])
        self.assertEqual(objectmap.targets_ordered, [(-1, Dummy, None)])

    def test_disconnect_with_ignore_missing(self):
        inst = self._makeInst()
        objectmap = DummyObjectMap(targetids=(),
                                   toraise=ValueError('a'))
        inst.__objectmap__ = objectmap
        inst.prop.disconnect([2,3], ignore_missing=True)
        self.assertEqual(objectmap.disconnected, [])
        self.assertEqual(objectmap.targets_ordered, [(-1, Dummy, None)])

    def test_disconnect_ignore_missing_implicit(self):
        inst = self._makeInst(ignore_missing=True)
        objectmap = DummyObjectMap(targetids=(),
                                   toraise=ValueError('a'))
        inst.__objectmap__ = objectmap
        inst.prop.disconnect([2,3])
        self.assertEqual(objectmap.disconnected, [])
        self.assertEqual(objectmap.targets_ordered, [(-1, Dummy, None)])

class Test_multireference_targetid_property(unittest.TestCase):
    def setUp(self):
        from substanced.interfaces import IFolder
        @implementer(IFolder)
        class DummyFolder(dict):
            pass
        self.DummyFolder = DummyFolder

    def _makeInst(self, reftype=None, ignore_missing=False, ordered=False):
        if reftype is None:
            reftype = Dummy
        from .. import multireference_targetid_property
        class Inner(self.DummyFolder):
            prop = multireference_targetid_property(
                reftype,
                ignore_missing=ignore_missing,
                ordered=ordered,
                )
        inst = Inner()
        inst.__oid__ = -1
        return inst

    def test_get_zero(self):
        inst = self._makeInst()
        objectmap = DummyObjectMap(sourceids=())
        inst.__objectmap__ = objectmap
        self.assertEqual(list(inst.prop), [])

    def test_get_one(self):
        inst = self._makeInst()
        objectmap = DummyObjectMap(sourceids=(1,))
        inst.__objectmap__ = objectmap
        self.assertEqual(list(inst.prop), [1])

    def test_get_two(self):
        inst = self._makeInst()
        objectmap = DummyObjectMap(sourceids=(1,2))
        inst.__objectmap__ = objectmap
        self.assertEqual(list(inst.prop), [1,2])

    def test_del_zero(self):
        inst = self._makeInst()
        objectmap = DummyObjectMap(sourceids=())
        inst.__objectmap__ = objectmap
        del inst.prop
        self.assertEqual(list(inst.prop), [])
        self.assertEqual(objectmap.sources_ordered, [(-1, Dummy, None)])

    def test_del_one(self):
        inst = self._makeInst()
        objectmap = DummyObjectMap(sourceids=(1,))
        inst.__objectmap__ = objectmap
        del inst.prop
        self.assertEqual(objectmap.disconnected, [(1, -1, Dummy)])
        self.assertEqual(objectmap.sources_ordered, [(-1, Dummy, None)])

    def test_del_two(self):
        inst = self._makeInst()
        objectmap = DummyObjectMap(sourceids=(1,2))
        inst.__objectmap__ = objectmap
        del inst.prop
        self.assertEqual(objectmap.disconnected,
                         [(1, -1, Dummy), (2, -1, Dummy)])
        self.assertEqual(objectmap.sources_ordered, [(-1, Dummy, None)])

    def test_set_None(self):
        inst = self._makeInst()
        objectmap = DummyObjectMap(sourceids=())
        inst.__objectmap__ = objectmap
        self.assertRaises(ValueError, inst.__setattr__, 'prop', None)
        self.assertEqual(objectmap.sources_ordered, [])

    def test_set_colander_null(self):
        from colander import null
        inst = self._makeInst()
        objectmap = DummyObjectMap(sourceids=(1,))
        inst.__objectmap__ = objectmap
        inst.prop = null
        self.assertEqual(objectmap.disconnected, [])
        self.assertEqual(objectmap.sources_ordered, [])

    def test_set_zero(self):
        inst = self._makeInst()
        objectmap = DummyObjectMap(sourceids=(1,))
        inst.__objectmap__ = objectmap
        inst.prop = []
        self.assertEqual(objectmap.disconnected, [(1, -1, Dummy)])
        self.assertEqual(objectmap.connected, [])
        self.assertEqual(objectmap.sources_ordered, [(-1, Dummy, None)]*2)

    def test_set_one(self):
        inst = self._makeInst()
        objectmap = DummyObjectMap(sourceids=(1,))
        inst.__objectmap__ = objectmap
        inst.prop = [2]
        self.assertEqual(objectmap.disconnected, [(1, -1, Dummy)])
        self.assertEqual(objectmap.connected, [(2, -1, Dummy)])
        self.assertEqual(objectmap.sources_ordered, [(-1, Dummy, None)]*2)

    def test_set_two(self):
        inst = self._makeInst()
        objectmap = DummyObjectMap(sourceids=(1,))
        inst.__objectmap__ = objectmap
        inst.prop = [2, 3]
        self.assertEqual(objectmap.disconnected, [(1, -1, Dummy)])
        self.assertEqual(objectmap.connected,
                         [(2, -1, Dummy), (3, -1, Dummy)])
        self.assertEqual(objectmap.sources_ordered, [(-1, Dummy, None)]*2)

    def test_clear(self):
        inst = self._makeInst()
        objectmap = DummyObjectMap(sourceids=(1,))
        inst.__objectmap__ = objectmap
        inst.prop.clear()
        self.assertEqual(objectmap.disconnected, [(1, -1, Dummy)])
        self.assertEqual(objectmap.sources_ordered, [(-1, Dummy, None)])

    def test_connect(self):
        inst = self._makeInst()
        objectmap = DummyObjectMap(sourceids=())
        inst.__objectmap__ = objectmap
        inst.prop.connect([2,3])
        self.assertEqual(objectmap.connected,
                         [(2, -1, Dummy), (3, -1, Dummy)])
        self.assertEqual(objectmap.sources_ordered, [(-1, Dummy, None)])
        
    def test_connect_with_ordering(self):
        inst = self._makeInst(ordered=True)
        objectmap = DummyObjectMap(sourceids=())
        inst.__objectmap__ = objectmap
        inst.prop.connect([2,3])
        self.assertEqual(objectmap.connected,
                         [(2, -1, Dummy), (3, -1, Dummy)])
        self.assertEqual(objectmap.sources_ordered, [(-1, Dummy, ())])
        
    def test_connect_missing(self):
        inst = self._makeInst()
        objectmap = DummyObjectMap(sourceids=(),
                                   toraise=ValueError('a'))
        inst.__objectmap__ = objectmap
        self.assertRaises(ValueError, inst.prop.connect, [2,3])
        self.assertEqual(objectmap.sources_ordered, [(-1, Dummy, None)])

    def test_connect_with_ignore_missing(self):
        inst = self._makeInst()
        objectmap = DummyObjectMap(sourceids=(),
                                   toraise=ValueError('a'))
        inst.__objectmap__ = objectmap
        inst.prop.connect([2,3], ignore_missing=True)
        self.assertEqual(objectmap.connected, [])
        self.assertEqual(objectmap.sources_ordered, [(-1, Dummy, None)])

    def test_disconnect(self):
        inst = self._makeInst()
        objectmap = DummyObjectMap(sourceids=())
        inst.__objectmap__ = objectmap
        inst.prop.disconnect([2,3])
        self.assertEqual(objectmap.disconnected,
                         [(2, -1, Dummy), (3, -1, Dummy)])
        self.assertEqual(objectmap.sources_ordered, [(-1, Dummy, None)])
        
    def test_disconnect_with_ordering(self):
        inst = self._makeInst(ordered=True)
        objectmap = DummyObjectMap(sourceids=())
        inst.__objectmap__ = objectmap
        inst.prop.disconnect([2,3])
        self.assertEqual(objectmap.disconnected,
                         [(2, -1, Dummy), (3, -1, Dummy)])
        self.assertEqual(objectmap.sources_ordered, [(-1, Dummy, ())])
        
    def test_disconnect_missing(self):
        inst = self._makeInst()
        objectmap = DummyObjectMap(sourceids=(),
                                   toraise=ValueError('a'))
        inst.__objectmap__ = objectmap
        self.assertRaises(ValueError, inst.prop.disconnect, [2,3])
        self.assertEqual(objectmap.sources_ordered, [(-1, Dummy, None)])

    def test_disconnect_with_ignore_missing(self):
        inst = self._makeInst()
        objectmap = DummyObjectMap(sourceids=(),
                                   toraise=ValueError('a'))
        inst.__objectmap__ = objectmap
        inst.prop.disconnect([2,3], ignore_missing=True)
        self.assertEqual(objectmap.disconnected, [])
        self.assertEqual(objectmap.sources_ordered, [(-1, Dummy, None)])

    def test_disconnect_ignore_missing_implicit(self):
        inst = self._makeInst(ignore_missing=True)
        objectmap = DummyObjectMap(sourceids=(),
                                   toraise=ValueError('a'))
        inst.__objectmap__ = objectmap
        inst.prop.disconnect([2,3])
        self.assertEqual(objectmap.disconnected, [])
        self.assertEqual(objectmap.sources_ordered, [(-1, Dummy, None)])

class Test_multireference_target_property(unittest.TestCase):
    def setUp(self):
        from substanced.interfaces import IFolder
        @implementer(IFolder)
        class DummyFolder(dict):
            pass
        self.DummyFolder = DummyFolder

    def _makeInst(self, reftype=None, ignore_missing=False, ordered=False):
        if reftype is None:
            reftype = Dummy
        from .. import multireference_target_property
        class Inner(self.DummyFolder):
            prop = multireference_target_property(
                reftype,
                ignore_missing=ignore_missing,
                ordered=ordered,
                )
        inst = Inner()
        inst.__oid__ = -1
        return inst

    def test_get_zero(self):
        inst = self._makeInst()
        objectmap = DummyObjectMap(sourceids=())
        inst.__objectmap__ = objectmap
        self.assertEqual(list(inst.prop), [])

    def test_get_one(self):
        inst = self._makeInst()
        objectmap = DummyObjectMap(sourceids=(1,), result=object)
        inst.__objectmap__ = objectmap
        self.assertEqual(list(inst.prop), [object])

    def test_get_two(self):
        inst = self._makeInst()
        objectmap = DummyObjectMap(sourceids=(1,2), result=object)
        inst.__objectmap__ = objectmap
        self.assertEqual(list(inst.prop), [object, object])

    def test_del_zero(self):
        inst = self._makeInst()
        objectmap = DummyObjectMap(sourceids=())
        inst.__objectmap__ = objectmap
        del inst.prop
        self.assertEqual(list(inst.prop), [])
        self.assertEqual(objectmap.sources_ordered, [(-1, Dummy, None)])

    def test_del_one(self):
        inst = self._makeInst()
        objectmap = DummyObjectMap(sourceids=(1,))
        inst.__objectmap__ = objectmap
        del inst.prop
        self.assertEqual(objectmap.disconnected, [(1, -1, Dummy)])
        self.assertEqual(objectmap.sources_ordered, [(-1, Dummy, None)])

    def test_del_two(self):
        inst = self._makeInst()
        objectmap = DummyObjectMap(sourceids=(1,2))
        inst.__objectmap__ = objectmap
        del inst.prop
        self.assertEqual(objectmap.disconnected,
                         [(1, -1, Dummy), (2, -1, Dummy)])
        self.assertEqual(objectmap.sources_ordered, [(-1, Dummy, None)])

    def test_set_None(self):
        inst = self._makeInst()
        objectmap = DummyObjectMap(sourceids=())
        inst.__objectmap__ = objectmap
        self.assertRaises(ValueError, inst.__setattr__, 'prop', None)

    def test_set_colander_null(self):
        from colander import null
        inst = self._makeInst()
        objectmap = DummyObjectMap(sourceids=(1,))
        inst.__objectmap__ = objectmap
        inst.prop = null
        self.assertEqual(objectmap.disconnected, [])
        self.assertEqual(objectmap.sources_ordered, [])

    def test_set_zero(self):
        inst = self._makeInst()
        objectmap = DummyObjectMap(sourceids=(1,))
        inst.__objectmap__ = objectmap
        inst.prop = []
        self.assertEqual(objectmap.disconnected, [(1, -1, Dummy)])
        self.assertEqual(objectmap.connected, [])
        self.assertEqual(objectmap.sources_ordered, [(-1, Dummy, None)]*2)

    def test_set_one(self):
        inst = self._makeInst()
        objectmap = DummyObjectMap(sourceids=(1,))
        inst.__objectmap__ = objectmap
        inst.prop = [2]
        self.assertEqual(objectmap.disconnected, [(1, -1, Dummy)])
        self.assertEqual(objectmap.connected, [(2, -1, Dummy)])
        self.assertEqual(objectmap.sources_ordered, [(-1, Dummy, None)]*2)

    def test_set_two(self):
        inst = self._makeInst()
        objectmap = DummyObjectMap(sourceids=(1,))
        inst.__objectmap__ = objectmap
        inst.prop = [2, 3]
        self.assertEqual(objectmap.disconnected, [(1, -1, Dummy)])
        self.assertEqual(objectmap.connected,
                         [(2, -1, Dummy), (3, -1, Dummy)])
        self.assertEqual(objectmap.sources_ordered, [(-1, Dummy, None)]*2)

    def test_clear(self):
        inst = self._makeInst()
        objectmap = DummyObjectMap(sourceids=(1,))
        inst.__objectmap__ = objectmap
        inst.prop.clear()
        self.assertEqual(objectmap.disconnected, [(1, -1, Dummy)])
        self.assertEqual(objectmap.sources_ordered, [(-1, Dummy, None)])

    def test_connect(self):
        inst = self._makeInst()
        objectmap = DummyObjectMap(sourceids=())
        inst.__objectmap__ = objectmap
        inst.prop.connect([2,3])
        self.assertEqual(objectmap.connected,
                         [(2, -1, Dummy), (3, -1, Dummy)])
        self.assertEqual(objectmap.sources_ordered, [(-1, Dummy, None)])
        
    def test_connect_with_ordering(self):
        inst = self._makeInst(ordered=True)
        objectmap = DummyObjectMap(sourceids=())
        inst.__objectmap__ = objectmap
        inst.prop.connect([2,3])
        self.assertEqual(objectmap.connected,
                         [(2, -1, Dummy), (3, -1, Dummy)])
        self.assertEqual(objectmap.sources_ordered, [(-1, Dummy, ())])
        
    def test_connect_missing(self):
        inst = self._makeInst()
        objectmap = DummyObjectMap(sourceids=(),
                                   toraise=ValueError('a'))
        inst.__objectmap__ = objectmap
        self.assertRaises(ValueError, inst.prop.connect, [2,3])
        self.assertEqual(objectmap.sources_ordered, [(-1, Dummy, None)])

    def test_connect_with_ignore_missing(self):
        inst = self._makeInst()
        objectmap = DummyObjectMap(sourceids=(),
                                   toraise=ValueError('a'))
        inst.__objectmap__ = objectmap
        inst.prop.connect([2,3], ignore_missing=True)
        self.assertEqual(objectmap.connected, [])
        self.assertEqual(objectmap.sources_ordered, [(-1, Dummy, None)])

    def test_disconnect(self):
        inst = self._makeInst()
        objectmap = DummyObjectMap(sourceids=())
        inst.__objectmap__ = objectmap
        inst.prop.disconnect([2,3])
        self.assertEqual(objectmap.disconnected,
                         [(2, -1, Dummy), (3, -1, Dummy)])
        self.assertEqual(objectmap.sources_ordered, [(-1, Dummy, None)])
        
    def test_disconnect_with_ordering(self):
        inst = self._makeInst(ordered=True)
        objectmap = DummyObjectMap(sourceids=())
        inst.__objectmap__ = objectmap
        inst.prop.disconnect([2,3])
        self.assertEqual(objectmap.disconnected,
                         [(2, -1, Dummy), (3, -1, Dummy)])
        self.assertEqual(objectmap.sources_ordered, [(-1, Dummy, ())])
        
    def test_disconnect_missing(self):
        inst = self._makeInst()
        objectmap = DummyObjectMap(sourceids=(),
                                   toraise=ValueError('a'))
        inst.__objectmap__ = objectmap
        self.assertRaises(ValueError, inst.prop.disconnect, [2,3])
        self.assertEqual(objectmap.sources_ordered, [(-1, Dummy, None)])

    def test_disconnect_with_ignore_missing(self):
        inst = self._makeInst()
        objectmap = DummyObjectMap(sourceids=(),
                                   toraise=ValueError('a'))
        inst.__objectmap__ = objectmap
        inst.prop.disconnect([2,3], ignore_missing=True)
        self.assertEqual(objectmap.disconnected, [])
        self.assertEqual(objectmap.sources_ordered, [(-1, Dummy, None)])

    def test_disconnect_ignore_missing_implicit(self):
        inst = self._makeInst(ignore_missing=True)
        objectmap = DummyObjectMap(sourceids=(),
                                           toraise=ValueError('a'))
        inst.__objectmap__ = objectmap
        inst.prop.disconnect([2,3])
        self.assertEqual(objectmap.disconnected, [])
        self.assertEqual(objectmap.sources_ordered, [(-1, Dummy, None)])

class TestMultireference(unittest.TestCase):
    def _makeOne(
        self,
        context,
        oids,
        objectmap,
        ignore_missing=False,
        resolve=False,
        orientation='source'
        ):
        from .. import Multireference
        m = Multireference(
            context,
            objectmap,
            'reftype',
            ignore_missing=ignore_missing,
            resolve=resolve,
            orientation=orientation
            )
        m.get_oids = lambda: oids
        return m

    def _makeContext(self):
        resource = testing.DummyResource()
        resource.__oid__ = -1
        return resource

    def test___nonzero__True(self):
        inst = self._makeOne(None, [1], None)
        self.assertTrue(inst.__nonzero__())
        
    def test___nonzero__False(self):
        inst = self._makeOne(None, [], None)
        self.assertFalse(inst.__nonzero__())

    def test___getitem__(self):
        inst = self._makeOne(None, [1], None)
        self.assertEqual(inst[0], 1)

    def test___getitem___with_resolve(self):
        objectmap = DummyObjectMap(result=object)
        inst = self._makeOne(None, [1], objectmap, resolve=True)
        self.assertEqual(inst[0], object)
        
    def test___contains__True(self):
        inst = self._makeOne(None, [1], None)
        self.assertTrue(inst.__contains__(1))
        
    def test___contains__False(self):
        inst = self._makeOne(None, [], None)
        self.assertFalse(inst.__contains__(1))
            
    def test___contains___withresolve_True(self):
        objectmap = DummyObjectMap(result=object)
        inst = self._makeOne(None, [1], objectmap, resolve=True)
        self.assertTrue(inst.__contains__(object))
        
    def test___contains___withresolve_False_empty(self):
        objectmap = DummyObjectMap(result=object)
        inst = self._makeOne(None, [], objectmap, resolve=True)
        self.assertFalse(inst.__contains__(object))

    def test___contains___withresolve_False_nonempty(self):
        objectmap = DummyObjectMap(result=object)
        inst = self._makeOne(None, [1], objectmap, resolve=True)
        self.assertFalse(inst.__contains__(None))

    def test___iter__(self):
        inst = self._makeOne(None, [1], None)
        self.assertEqual(list(inst.__iter__()), [1])

    def test___iter__withresolve(self):
        objectmap = DummyObjectMap(result=object)
        inst = self._makeOne(None, [1], objectmap, resolve=True)
        self.assertEqual(list(inst.__iter__()), [object])

    def test___len__(self):
        inst = self._makeOne(None, [1], None)
        self.assertEqual(len(inst), 1)

    def test_connect_zero(self):
        objectmap = DummyObjectMap()
        context = self._makeContext()
        inst = self._makeOne(context, [1], objectmap)
        inst.connect([])
        self.assertEqual(objectmap.connected, [])
        
    def test_connect_one(self):
        objectmap = DummyObjectMap()
        context = self._makeContext()
        inst = self._makeOne(context, [1], objectmap)
        inst.connect([1])
        self.assertEqual(objectmap.connected, [(-1, 1, 'reftype')])
        self.assertEqual(objectmap.targets_ordered, [(-1, 'reftype', None)])
        
    def test_connect_two(self):
        objectmap = DummyObjectMap()
        context = self._makeContext()
        inst = self._makeOne(context, [1, 2], objectmap)
        inst.connect([1, 2])
        self.assertEqual(
            objectmap.connected,
            [(-1, 1, 'reftype'), (-1, 2, 'reftype')]
            )
        self.assertEqual(objectmap.targets_ordered, [(-1, 'reftype', None)])

    def test_connect_ignore_missing_explicit(self):
        objectmap = DummyObjectMap(toraise=ValueError('a'))
        context = self._makeContext()
        inst = self._makeOne(context, [1, 2], objectmap)
        inst.connect([1, 2], ignore_missing=True)
        self.assertEqual(objectmap.connected, [])
        self.assertEqual(objectmap.targets_ordered, [(-1, 'reftype', None)])

    def test_connect_ignore_missing_implicit(self):
        objectmap = DummyObjectMap(toraise=ValueError('a'))
        context = self._makeContext()
        inst = self._makeOne(context, [1, 2], objectmap, ignore_missing=True)
        inst.connect([1, 2])
        self.assertEqual(objectmap.connected, [])
        self.assertEqual(objectmap.targets_ordered, [(-1, 'reftype', None)])

    def test_connect_nonsource(self):
        objectmap = DummyObjectMap()
        context = self._makeContext()
        inst = self._makeOne(context, [1, 2], objectmap, orientation='target')
        inst.connect([1, 2])
        self.assertEqual(
            objectmap.connected,
            [(1, -1, 'reftype'), (2, -1, 'reftype')]
            )
        self.assertEqual(objectmap.sources_ordered, [(-1, 'reftype', None)])

    def test_disconnect_zero(self):
        objectmap = DummyObjectMap()
        context = self._makeContext()
        inst = self._makeOne(context, [1], objectmap)
        inst.disconnect([])
        self.assertEqual(objectmap.disconnected, [])
        self.assertEqual(objectmap.targets_ordered, [(-1, 'reftype', None)])
        
    def test_disconnect_one(self):
        objectmap = DummyObjectMap()
        context = self._makeContext()
        inst = self._makeOne(context, [1], objectmap)
        inst.disconnect([1])
        self.assertEqual(objectmap.disconnected, [(-1, 1, 'reftype')])
        self.assertEqual(objectmap.targets_ordered, [(-1, 'reftype', None)])

    def test_disconnect_two(self):
        objectmap = DummyObjectMap()
        context = self._makeContext()
        inst = self._makeOne(context, [1, 2], objectmap)
        inst.disconnect([1, 2])
        self.assertEqual(
            objectmap.disconnected,
            [(-1, 1, 'reftype'), (-1, 2, 'reftype')]
            )
        self.assertEqual(objectmap.targets_ordered, [(-1, 'reftype', None)])

    def test_disconnect_ignore_missing_explicit(self):
        objectmap = DummyObjectMap(toraise=ValueError('a'))
        context = self._makeContext()
        inst = self._makeOne(context, [1, 2], objectmap)
        inst.disconnect([1, 2], ignore_missing=True)
        self.assertEqual(objectmap.disconnected, [])
        self.assertEqual(objectmap.targets_ordered, [(-1, 'reftype', None)])
        
    def test_disconnect_ignore_missing_implicit(self):
        objectmap = DummyObjectMap(toraise=ValueError('a'))
        context = self._makeContext()
        inst = self._makeOne(context, [1, 2], objectmap, ignore_missing=True)
        inst.disconnect([1, 2])
        self.assertEqual(objectmap.disconnected, [])
        self.assertEqual(objectmap.targets_ordered, [(-1, 'reftype', None)])

    def test_disconnect_nonsource(self):
        objectmap = DummyObjectMap()
        context = self._makeContext()
        inst = self._makeOne(context, [1, 2], objectmap, orientation='target')
        inst.disconnect([1, 2])
        self.assertEqual(
            objectmap.disconnected,
            [(1, -1, 'reftype'), (2, -1, 'reftype')]
            )
        self.assertEqual(objectmap.sources_ordered, [(-1, 'reftype', None)])

    def test_clear(self):
        objectmap = DummyObjectMap()
        context = self._makeContext()
        inst = self._makeOne(context, [1, 2], objectmap)
        inst.clear()
        self.assertEqual(
            objectmap.disconnected,
            [(-1, 1, 'reftype'), (-1, 2, 'reftype')]
            )
        self.assertEqual(objectmap.targets_ordered, [(-1, 'reftype', None)])

    def test_set_ordered_as_source(self):
        objectmap = DummyObjectMap()
        context = self._makeContext()
        inst = self._makeOne(context, [1, 2], objectmap, orientation='source')
        inst.set_ordered(context.__oid__)
        self.assertEqual(objectmap.targets_ordered,  [(-1, 'reftype', [1, 2])])

    def test_set_ordered_as_target(self):
        objectmap = DummyObjectMap()
        context = self._makeContext()
        inst = self._makeOne(context, [1, 2], objectmap, orientation='target')
        inst.set_ordered(context.__oid__)
        self.assertEqual(objectmap.sources_ordered,  [(-1, 'reftype', [1, 2])])

    def test_set_unordered_as_source(self):
        objectmap = DummyObjectMap()
        context = self._makeContext()
        inst = self._makeOne(context, [1, 2], objectmap, orientation='source')
        inst.set_unordered(context.__oid__)
        self.assertEqual(objectmap.targets_ordered,  [(-1, 'reftype', None)])

    def test_set_unordered_as_target(self):
        objectmap = DummyObjectMap()
        context = self._makeContext()
        inst = self._makeOne(context, [1, 2], objectmap, orientation='target')
        inst.set_unordered(context.__oid__)
        self.assertEqual(objectmap.sources_ordered,  [(-1, 'reftype', None)])
        
class Test_ReferencedPredicate(unittest.TestCase):
    def _makeOne(self, val, config):
        from .. import _ReferencedPredicate
        return _ReferencedPredicate(val, config)

    def test_text(self):
        config = Dummy()
        config.registry = Dummy()
        inst = self._makeOne(True, config)
        self.assertEqual(inst.text(), 'referenced = True')

    def test_phash(self):
        config = Dummy()
        config.registry = Dummy()
        inst = self._makeOne(True, config)
        self.assertEqual(inst.phash(), 'referenced = True')

    def test__call__(self):
        config = Dummy()
        config.registry = Dummy()
        inst = self._makeOne(True, config)
        def has_references(context):
            self.assertEqual(context, None)
            return True
        inst.has_references = has_references
        self.assertEqual(inst(None, None), True)

class Test_has_references(unittest.TestCase):
    def _callFUT(self, context):
        from .. import has_references
        return has_references(context)
    
    def test_objectmap_is_None(self):
        result = self._callFUT(None)
        self.assertEqual(result, False)

    def test_oid_is_None(self):
        context = testing.DummyResource()
        context.__objectmap__ = True
        result = self._callFUT(context)
        self.assertEqual(result, False)

    def test_gardenpath(self):
        context = testing.DummyResource()
        context.__objectmap__ = DummyObjectMap(result=True)
        context.__oid__ = 1
        result = self._callFUT(context)
        self.assertEqual(result, True)

class Test_referential_integrity(unittest.TestCase):
    def _callFUT(self, event):
        from .. import referential_integrity
        return referential_integrity(event)

    def test_moving(self):
        event = DummyEvent(None, moving=True)
        self.assertFalse(self._callFUT(event))

    def test_no_objectmap(self):
        event = DummyEvent(None)
        self.assertFalse(self._callFUT(event))

    def test_no_reftypes(self):
        obj = testing.DummyResource()
        obj.__objectmap__ = DummyObjectMap()
        event = DummyEvent(obj)
        self.assertFalse(self._callFUT(event))

    def test_reftype_without_integrity(self):
        obj = testing.DummyResource()
        obj.__objectmap__ = DummyObjectMap(reftypes=('abc',))
        event = DummyEvent(obj)
        self.assertFalse(self._callFUT(event))

    def test_reftype_with_source_integrity_no_targetids(self):
        from substanced.interfaces import ReferenceType
        obj = testing.DummyResource()
        class Reference(ReferenceType):
            source_integrity = True
        obj.__objectmap__ = DummyObjectMap(reftypes=(Reference,))
        event = DummyEvent(obj)
        self.assertFalse(self._callFUT(event))

    def test_reftype_with_source_integrity_with_targetids(self):
        from substanced.interfaces import ReferenceType
        from .. import SourceIntegrityError
        obj = testing.DummyResource()
        class Reference(ReferenceType):
            source_integrity = True
        obj.__objectmap__ = DummyObjectMap(
            reftypes=(Reference,), targetids=(1,)
            )
        event = DummyEvent(obj)
        self.assertRaises(SourceIntegrityError, self._callFUT, event)

    def test_reftype_with_source_integrity_with_only_self_targetid(self):
        from substanced.interfaces import ReferenceType
        obj = testing.DummyResource()
        class Reference(ReferenceType):
            source_integrity = True
        obj.__objectmap__ = DummyObjectMap(
            reftypes=(Reference,), targetids=set([100])
            )
        event = DummyEvent(obj)
        self.assertEqual(None, self._callFUT(event)) # self-reference ignored

    def test_reftype_with_target_integrity_no_sourceids(self):
        from substanced.interfaces import ReferenceType
        obj = testing.DummyResource()
        class Reference(ReferenceType):
            target_integrity = True
        obj.__objectmap__ = DummyObjectMap(reftypes=(Reference,))
        event = DummyEvent(obj)
        self.assertFalse(self._callFUT(event))

    def test_reftype_with_target_integrity_with_sourceids(self):
        from substanced.interfaces import ReferenceType
        from .. import TargetIntegrityError
        obj = testing.DummyResource()
        class Reference(ReferenceType):
            target_integrity = True
        obj.__objectmap__ = DummyObjectMap(
            reftypes=(Reference,), sourceids=(1,)
            )
        event = DummyEvent(obj)
        self.assertRaises(TargetIntegrityError, self._callFUT, event)

    def test_reftype_with_target_integrity_with_only_self_sourceid(self):
        from substanced.interfaces import ReferenceType
        obj = testing.DummyResource()
        class Reference(ReferenceType):
            target_integrity = True
        obj.__objectmap__ = DummyObjectMap(
            reftypes=(Reference,), sourceids=set([100])
            )
        event = DummyEvent(obj)
        self.assertEqual(None, self._callFUT(event)) # self-reference ignored

class TestReferentialIntegrityError(unittest.TestCase):
    def _makeOne(self, obj, reftype, oids):
        from .. import ReferentialIntegrityError
        return ReferentialIntegrityError(obj, reftype, oids)

    def test_get_objects(self):
        objectmap = DummyObjectMap(result='one')
        obj = testing.DummyResource()
        obj.__objectmap__ = objectmap
        inst = self._makeOne(obj, 'reftype', (1,))
        self.assertEqual(list(inst.get_objects()), ['one'])

    def test_get_paths(self):
        objectmap = DummyObjectMap(result='one')
        obj = testing.DummyResource()
        obj.__objectmap__ = objectmap
        inst = self._makeOne(obj, 'reftype', (1,))
        self.assertEqual(list(inst.get_paths()), ['o/n/e'])


class DummyEvent(object):
    def __init__(self, object, moving=None):
        self.object = object
        self.moving = moving

    removed_oids = (100,)

class Dummy(object):
    pass

def resource(path):
    path_tuple = split(path)
    parent = None
    for element in path_tuple:
        obj = testing.DummyResource()
        obj.__parent__ = parent
        obj.__name__ = element
        parent = obj
    obj.path_tuple = path_tuple
    return obj
                
        
def split(s):
    return (_BLANK,) + tuple(filter(None, s.split(_SLASH)))

_marker = object()

class DummyObjectMap(object):
    def __init__(self, targetids=(), sourceids=(), result=None, toraise=None,
                 reftypes=()):
        self.added = []
        self.removed = []
        self.connected = []
        self.disconnected = []
        self._targetids = targetids
        self._sourceids = sourceids
        self._reftypes = reftypes
        self.result = result
        self.toraise = toraise
        self.sources_ordered = []
        self.targets_ordered = []

    def object_for(self, objectid):
        return self.result

    def path_for(self, objectid):
        return self.result

    def targetids(self, context, reftype):
        return self._targetids

    def sourceids(self, context, reftype):
        return self._sourceids

    def disconnect(self, source, target, reftype):
        if self.toraise:
            raise self.toraise
        self.disconnected.append((source, target, reftype))

    def connect(self, source, target, reftype):
        if self.toraise:
            raise self.toraise
        self.connected.append((source, target, reftype))

    def has_references(self, oid):
        return self.result

    def get_reftypes(self):
        return self._reftypes

    def order_sources(self, oid, reftype, order=_marker):
        self.sources_ordered.append((oid, reftype, order))

    def order_targets(self, oid, reftype, order=_marker):
        self.targets_ordered.append((oid, reftype, order))
        
class DummyTreeSet(set):
    def insert(self, val):
        self.add(val)

class DummyReferenceSet(object):
    def __init__(self, result=True):
        self.result = result
        self.connected = []
        self.disconnected = []
        self.sources_ordered = []
        self.targets_ordered = []

    def order_sources(self, oid, order):
        self.sources_ordered.append((oid, order))
        return order

    def order_targets(self, oid, order):
        self.targets_ordered.append((oid, order))
        return order
        
    def connect(self, src, target):
        self.connected.append((src, target))

    def disconnect(self, src, target):
        self.disconnected.append((src, target))

    def targetids(self, src):
        return self.result

    def sourceids(self, src):
        return self.result

    def is_target(self, oid):
        return self.result

    is_source = is_target

class DummyReferenceMap(dict):
    oid_args = None

    def __init__(self, sourceids=(), targetids=(), has_references=False,
                 reftypes=()):
        self._sourceids = sourceids
        self._targetids = targetids
        self._has_references = has_references
        self._reftypes = reftypes
        self.sources_ordered = []
        self.targets_ordered = []
        
    def connect(self, src, target, reftype):
        self[reftype] = (src, target)

    def disconnect(self, src, target, reftype):
        del self[reftype]

    def sourceids(self, oid, reftype):
        return self._sourceids

    def targetids(self, oid, reftype):
        return self._targetids

    def has_references(self, oid, reftype):
        self.oid_arg = oid
        self.reftype_arg = reftype
        return self._has_references

    def get_reftypes(self):
        return self._reftypes

    def order_sources(self, oid, reftype, order):
        self.sources_ordered.append((oid, reftype, order))
        return order

    def order_targets(self, oid, reftype, order):
        self.targets_ordered.append((oid, reftype, order))
        return order
    
class DummyRoot(object):
    pass
