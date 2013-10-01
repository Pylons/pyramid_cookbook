import unittest
from pyramid import testing

import BTrees

from ..._compat import u
_BLANK = u('')
_A = u('a')
_ABC = u('abc')

def _makeSite(**kw):
    from ...interfaces import IFolder
    from zope.interface import alsoProvides
    site = testing.DummyResource(__provides__=kw.pop('__provides__', None))
    alsoProvides(site, IFolder)
    for k, v in kw.items():
        site[k] = v
        v.__is_service__ = True
    return site

class TestSDIndex(unittest.TestCase):
    def _makeOne(self, oid=1):
        from ..indexes import SDIndex
        index = SDIndex()
        index.__oid__ = oid
        return index

    def test_resultset_from_query_no_resolver(self):
        inst = self._makeOne()
        inst.__objectmap__ = DummyObjectmap()
        query = DummyQuery()
        resultset = inst.resultset_from_query(query)
        self.assertEqual(resultset.ids, [1,2,3])
        self.assertEqual(resultset.resolver, inst.__objectmap__.object_for)
        self.assertTrue(query.flushed)

    def test_resultset_from_query_with_resolver(self):
        inst = self._makeOne()
        inst.__objectmap__ = DummyObjectmap()
        query = DummyQuery()
        resolver = object()
        resultset = inst.resultset_from_query(query, resolver=resolver)
        self.assertEqual(resultset.ids, [1,2,3])
        self.assertEqual(resultset.resolver, resolver)
        self.assertTrue(query.flushed)

    def test_get_action_tm_existing_action_tm(self):
        inst = self._makeOne()
        tm = DummyActionTM(None)
        inst._p_action_tm = tm
        self.assertEqual(inst.get_action_tm(), tm)
        
    def test_get_action_tm_no_existing_action_tm(self):
        inst = self._makeOne()
        inst.tm_class = DummyActionTM
        result = inst.get_action_tm()
        self.assertEqual(result.__class__, DummyActionTM)
        self.assertEqual(result.index, inst)
        self.assertTrue(result.registered)

    def test_flush(self):
        inst = self._makeOne()
        tm = DummyActionTM(None)
        inst._p_action_tm = tm
        inst.flush('abc')
        self.assertEqual(tm.flushed, 'abc')

    def test_flush_no_tm(self):
        inst = self._makeOne()
        inst._p_action_tm = None
        self.assertEqual(inst.flush(), None)

    def test_add_action(self):
        inst = self._makeOne()
        tm = DummyActionTM(None)
        inst._p_action_tm = tm
        inst.add_action(True)
        self.assertEqual(tm.actions, [True])

    def test_index_resource_default_action_mode_is_MODE_ATCOMMIT(self):
        resource = testing.DummyResource()
        inst = self._makeOne()
        tm = DummyActionTM(None)
        inst._p_action_tm = tm
        inst.index_resource(resource, 1)
        self.assertEqual(len(tm.actions), 1)

    def test_index_resource_action_MODE_IMMEDIATE(self):
        from substanced.interfaces import MODE_IMMEDIATE
        resource = testing.DummyResource()
        inst = self._makeOne()
        L = []
        inst.index_doc = lambda oid, resource: L.append((oid, resource))
        inst.index_resource(resource, 1, action_mode=MODE_IMMEDIATE)
        self.assertEqual(L, [(1, resource)])

    def test_index_resource_action_MODE_ATCOMMIT(self):
        from substanced.interfaces import MODE_ATCOMMIT
        resource = testing.DummyResource()
        inst = self._makeOne()
        tm = DummyActionTM(None)
        inst._p_action_tm = tm
        inst.index_resource(resource, 1, action_mode=MODE_ATCOMMIT)
        self.assertEqual(len(tm.actions), 1)
        action = tm.actions[0]
        self.assertEqual(action.__class__.__name__, 'IndexAction')
        self.assertEqual(action.oid, 1)
        self.assertEqual(action.mode, MODE_ATCOMMIT)
        self.assertEqual(action.index, inst)

    def test_index_resource_oid_is_None(self):
        from substanced.interfaces import MODE_IMMEDIATE
        resource = testing.DummyResource()
        resource.__oid__ = 1
        inst = self._makeOne()
        L = []
        inst.index_doc = lambda oid, resource: L.append((oid, resource))
        inst.index_resource(resource, action_mode=MODE_IMMEDIATE)
        self.assertEqual(L, [(1, resource)])

    def test_reindex_resource_default_action_mode_is_MODE_ATCOMMIT(self):
        resource = testing.DummyResource()
        inst = self._makeOne()
        inst = self._makeOne()
        tm = DummyActionTM(None)
        inst._p_action_tm = tm
        inst.reindex_resource(resource, 1)
        self.assertEqual(len(tm.actions), 1)

    def test_reindex_resource_action_MODE_IMMEDIATE(self):
        from substanced.interfaces import MODE_IMMEDIATE
        resource = testing.DummyResource()
        inst = self._makeOne()
        L = []
        inst.reindex_doc = lambda oid, resource: L.append((oid, resource))
        inst.reindex_resource(resource, 1, action_mode=MODE_IMMEDIATE)
        self.assertEqual(L, [(1, resource)])

    def test_reindex_resource_action_MODE_ATCOMMIT(self):
        from substanced.interfaces import MODE_ATCOMMIT
        resource = testing.DummyResource()
        inst = self._makeOne()
        tm = DummyActionTM(None)
        inst._p_action_tm = tm
        inst.reindex_resource(resource, 1, action_mode=MODE_ATCOMMIT)
        self.assertEqual(len(tm.actions), 1)
        action = tm.actions[0]
        self.assertEqual(action.__class__.__name__, 'ReindexAction')
        self.assertEqual(action.oid, 1)
        self.assertEqual(action.mode, MODE_ATCOMMIT)
        self.assertEqual(action.index, inst)

    def test_reindex_resource_no_oid(self):
        from substanced.interfaces import MODE_IMMEDIATE
        resource = testing.DummyResource()
        resource.__oid__ = 1
        inst = self._makeOne()
        L = []
        inst.reindex_doc = lambda oid, resource: L.append((oid, resource))
        inst.reindex_resource(resource, action_mode=MODE_IMMEDIATE)
        self.assertEqual(L, [(1, resource)])

    def test_unindex_resource_default_mode_is_MODE_ATCOMMIT(self):
        inst = self._makeOne()
        tm = DummyActionTM(None)
        inst._p_action_tm = tm
        inst.unindex_resource(1)
        self.assertEqual(len(tm.actions), 1)

    def test_unindex_resource_action_MODE_IMMEDIATE(self):
        from substanced.interfaces import MODE_IMMEDIATE
        inst = self._makeOne()
        L = []
        inst.unindex_doc = lambda oid: L.append(oid)
        inst.unindex_resource(1, action_mode=MODE_IMMEDIATE)
        self.assertEqual(L, [1])

    def test_unindex_resource_action_MODE_ATCOMMIT(self):
        from substanced.interfaces import MODE_ATCOMMIT
        inst = self._makeOne()
        tm = DummyActionTM(None)
        inst._p_action_tm = tm
        inst.unindex_resource(1, action_mode=MODE_ATCOMMIT)
        self.assertEqual(len(tm.actions), 1)
        action = tm.actions[0]
        self.assertEqual(action.__class__.__name__, 'UnindexAction')
        self.assertEqual(action.oid, 1)
        self.assertEqual(action.mode, MODE_ATCOMMIT)
        self.assertEqual(action.index, inst)

    def test_unindex_resource_resource_is_not_oid(self):
        from substanced.interfaces import MODE_IMMEDIATE
        resource = testing.DummyResource()
        resource.__oid__ = 1
        inst = self._makeOne()
        L = []
        inst.unindex_doc = lambda oid: L.append(oid)
        inst.unindex_resource(resource, action_mode=MODE_IMMEDIATE)
        self.assertEqual(L, [1])

    def test_repr(self):
        inst = self._makeOne()
        inst.__name__ = 'fred'
        r = repr(inst)
        self.assertTrue(r.startswith(
           "<substanced.catalog.indexes.SDIndex object 'fred' at"))
        
        

class TestPathIndex(unittest.TestCase):
    def _makeOne(self, family=None):
        from ..indexes import PathIndex
        from ...objectmap import ObjectMap
        catalog = DummyCatalog()
        index = PathIndex(family=family)
        index.__parent__ = catalog
        site = _makeSite(catalog=catalog)
        objectmap = ObjectMap(site)
        site.__objectmap__ = objectmap
        return index

    def _acquire(self, inst, name):
        from substanced.util import acquire
        return acquire(inst, name)

    def test_document_repr(self):
        from substanced.util import get_oid
        inst = self._makeOne()
        obj = testing.DummyResource()
        objectmap = self._acquire(inst, '__objectmap__')
        objectmap.add(obj, (_BLANK,))
        result = inst.document_repr(get_oid(obj))
        self.assertEqual(result, (_BLANK,))

    def test_document_repr_missing(self):
        inst = self._makeOne()
        result = inst.document_repr(1)
        self.assertEqual(result, None)

    def test_ctor_alternate_family(self):
        inst = self._makeOne(family=BTrees.family32)
        self.assertEqual(inst.family, BTrees.family32)

    def test_index_doc(self):
        inst = self._makeOne()
        result = inst.index_doc(1, None)
        self.assertEqual(result, None)

    def test_unindex_doc(self):
        inst = self._makeOne()
        result = inst.unindex_doc(1)
        self.assertEqual(result, None)

    def test_reindex_doc(self):
        inst = self._makeOne()
        result = inst.reindex_doc(1, None)
        self.assertEqual(result, None)

    def test_docids(self):
        inst = self._makeOne()
        result = inst.docids()
        self.assertEqual(list(result),  [])

    def test_not_indexed(self):
        inst = self._makeOne()
        result = inst.not_indexed()
        self.assertEqual(list(result),  [])
        
    def test_search(self):
        inst = self._makeOne()
        obj = testing.DummyResource()
        objectmap = self._acquire(inst, '__objectmap__')
        objectmap._v_nextid = 1
        objectmap.add(obj, (_BLANK,))
        result = inst.search((_BLANK,))
        self.assertEqual(list(result),  [1])

    def test_apply_obj(self):
        inst = self._makeOne()
        obj = testing.DummyResource()
        objectmap = self._acquire(inst, '__objectmap__')
        objectmap._v_nextid = 1
        objectmap.add(obj, (_BLANK,))
        result = inst.apply(obj)
        self.assertEqual(list(result),  [1])

    def test_apply_obj_noresults(self):
        inst = self._makeOne()
        obj = testing.DummyResource()
        result = inst.apply(obj)
        self.assertEqual(list(result),  [])
        
    def test_apply_path(self):
        inst = self._makeOne()
        obj = testing.DummyResource()
        objectmap = self._acquire(inst, '__objectmap__')
        objectmap._v_nextid = 1
        objectmap.add(obj, (_BLANK,))
        result = inst.apply((_BLANK,))
        self.assertEqual(list(result),  [1])

    def test_apply_dict(self):
        inst = self._makeOne()
        obj = testing.DummyResource()
        objectmap = self._acquire(inst, '__objectmap__')
        objectmap._v_nextid = 1
        objectmap.add(obj, (_BLANK,))
        obj2 = testing.DummyResource(__name__='a')
        obj2.__parent__ = obj
        objectmap.add(obj2, (_BLANK, _A))
        result = inst.apply({'path':obj})
        self.assertEqual(list(result),  [1, 2])

    def test_apply_dict_withdepth(self):
        inst = self._makeOne()
        obj = testing.DummyResource()
        objectmap = self._acquire(inst, '__objectmap__')
        objectmap._v_nextid = 1
        objectmap.add(obj, (_BLANK,))
        obj2 = testing.DummyResource(__name__='a')
        obj2.__parent__ = obj
        objectmap.add(obj2, (_BLANK, _A))
        result = inst.apply({'path':obj, 'depth':0})
        self.assertEqual(list(result),  [1])

    def test_apply_dict_with_include_origin_false(self):
        inst = self._makeOne()
        obj = testing.DummyResource()
        objectmap = self._acquire(inst, '__objectmap__')
        objectmap._v_nextid = 1
        objectmap.add(obj, (_BLANK,))
        obj2 = testing.DummyResource(__name__='a')
        obj2.__parent__ = obj
        objectmap.add(obj2, (_BLANK, _A))
        result = inst.apply({'path':obj, 'include_origin':False})
        self.assertEqual(list(result),  [2])
        
    def test__parse_path_obj(self):
        inst = self._makeOne()
        obj = testing.DummyResource()
        result = inst._parse_path(obj)
        self.assertEqual(result, ((_BLANK,), None, True))
        
    def test__parse_path_path_tuple(self):
        inst = self._makeOne()
        result = inst._parse_path((_BLANK,))
        self.assertEqual(result, ((_BLANK,), None, True))

    def test__parse_path_path_str(self):
        inst = self._makeOne()
        result = inst._parse_path('/')
        self.assertEqual(result, ((_BLANK,), None, True))

    def test__parse_path_path_str_with_depth(self):
        inst = self._makeOne()
        result = inst._parse_path('[depth=2]/abc')
        self.assertEqual(result, ((_BLANK, _ABC), 2, True))

    def test__parse_path_path_str_with_origin_false(self):
        inst = self._makeOne()
        result = inst._parse_path('[include_origin=false]/abc')
        self.assertEqual(result, ((_BLANK, _ABC), None, False))
        
    def test__parse_path_path_str_with_depth_and_origin(self):
        inst = self._makeOne()
        result = inst._parse_path('[depth=2,include_origin=false]/abc')
        self.assertEqual(result, ((_BLANK, _ABC), 2, False))

    def test__parse_path_path_str_with_depth_and_origin_no_val(self):
        inst = self._makeOne()
        result = inst._parse_path('[depth=2,include_origin]/abc')
        self.assertEqual(result, ((_BLANK, _ABC), 2, True))

    def test__parse_path_path_invalid(self):
        inst = self._makeOne()
        self.assertRaises(ValueError, inst._parse_path, None)

    def test__parse_path_path_invalid_string_no_begin_slash(self):
        inst = self._makeOne()
        self.assertRaises(ValueError, inst._parse_path, 'abc/def')

    def test_apply_intersect(self):
        # ftest to make sure we have the right kind of Sets
        inst = self._makeOne()
        obj = testing.DummyResource()
        objectmap = self._acquire(inst, '__objectmap__')
        objectmap._v_nextid = 1
        objectmap.add(obj, (_BLANK,))
        result = inst.apply_intersect(obj, objectmap.family.IF.Set([1]))
        self.assertEqual(list(result),  [1])

    def test_eq_defaults(self):
        inst = self._makeOne()
        result = inst.eq('/abc')
        self.assertEqual(
            result._value,
            {'path': '/abc'}
            )

    def test_eq_include_origin_is_False(self):
        inst = self._makeOne()
        inst.depth = 10
        result = inst.eq('/abc', include_origin=False)
        self.assertEqual(
            result._value,
            {'path': '/abc', 'include_origin': False}
            )

    def test_eq_include_depth_is_not_None(self):
        inst = self._makeOne()
        inst.depth = 10
        result = inst.eq('/abc', depth=1)
        self.assertEqual(
            result._value,
            {'path': '/abc', 'depth': 1}
            )

class TestFieldIndex(unittest.TestCase):
    def _makeOne(self, discriminator=None, family=None, action_mode=None):
        from ..indexes import FieldIndex
        return FieldIndex(discriminator, family, action_mode=action_mode)
    
    def test_ctor_with_discriminator(self):
        inst = self._makeOne('abc')
        self.assertEqual(inst.discriminator, 'abc')

    def test_ctor_without_discriminator(self):
        inst = self._makeOne()
        self.assertEqual(inst.discriminator.__class__, type(lambda x: True))

    def test_ctor_with_action_mode(self):
        from substanced.interfaces import MODE_IMMEDIATE
        inst = self._makeOne('abc', action_mode=MODE_IMMEDIATE)
        self.assertEqual(inst.action_mode, MODE_IMMEDIATE)

    def test_ctor_without_action_mode(self):
        from substanced.interfaces import MODE_ATCOMMIT
        inst = self._makeOne('abc')
        self.assertEqual(inst.action_mode, MODE_ATCOMMIT)

class TestKeywordIndex(unittest.TestCase):
    def _makeOne(self, discriminator=None, family=None, action_mode=None):
        from ..indexes import KeywordIndex
        return KeywordIndex(discriminator, family, action_mode=action_mode)
    
    def test_ctor_with_discriminator(self):
        inst = self._makeOne('abc')
        self.assertEqual(inst.discriminator, 'abc')

    def test_ctor_without_discriminator(self):
        inst = self._makeOne()
        self.assertEqual(inst.discriminator.__class__, type(lambda x: True))

    def test_ctor_with_action_mode(self):
        from substanced.interfaces import MODE_IMMEDIATE
        inst = self._makeOne('abc', action_mode=MODE_IMMEDIATE)
        self.assertEqual(inst.action_mode, MODE_IMMEDIATE)

    def test_ctor_without_action_mode(self):
        from substanced.interfaces import MODE_ATCOMMIT
        inst = self._makeOne('abc')
        self.assertEqual(inst.action_mode, MODE_ATCOMMIT)

class TestFacetIndex(unittest.TestCase):
    def _makeOne(self, discriminator=None, facets=None, family=None,
                 action_mode=None):
        from ..indexes import FacetIndex
        return FacetIndex(discriminator, facets, family,
                          action_mode=action_mode)
    
    def test_ctor_with_discriminator(self):
        inst = self._makeOne('abc')
        self.assertEqual(inst.discriminator, 'abc')
        self.assertEqual(list(inst.facets), [])

    def test_ctor_without_discriminator(self):
        inst = self._makeOne()
        self.assertEqual(inst.discriminator.__class__, type(lambda x: True))

    def test_ctor_with_action_mode(self):
        from substanced.interfaces import MODE_IMMEDIATE
        inst = self._makeOne('abc', action_mode=MODE_IMMEDIATE)
        self.assertEqual(inst.action_mode, MODE_IMMEDIATE)

    def test_ctor_without_action_mode(self):
        from substanced.interfaces import MODE_ATCOMMIT
        inst = self._makeOne('abc')
        self.assertEqual(inst.action_mode, MODE_ATCOMMIT)

class TestTextIndex(unittest.TestCase):
    def _makeOne(
        self,
        discriminator=None,
        lexicon=None,
        index=None,
        family=None,
        action_mode=None,
        ):
        from ..indexes import TextIndex
        return TextIndex(discriminator, family, action_mode=action_mode)
    
    def test_ctor_with_discriminator(self):
        inst = self._makeOne('abc')
        self.assertEqual(inst.discriminator, 'abc')

    def test_ctor_without_discriminator(self):
        inst = self._makeOne()
        self.assertEqual(inst.discriminator.__class__, type(lambda x: True))

    def test_ctor_with_action_mode(self):
        from substanced.interfaces import MODE_IMMEDIATE
        inst = self._makeOne(action_mode=MODE_IMMEDIATE)
        self.assertEqual(inst.action_mode, MODE_IMMEDIATE)

    def test_ctor_without_action_mode(self):
        from substanced.interfaces import MODE_ATCOMMIT
        inst = self._makeOne()
        self.assertEqual(inst.action_mode, MODE_ATCOMMIT)

class TestAllowedIndex(unittest.TestCase):
    def setUp(self):
        self.config = testing.setUp()

    def tearDown(self):
        testing.tearDown()
        
    def _makeOne(self, discriminator=None, family=None):
        from ..indexes import AllowedIndex
        index = AllowedIndex(discriminator, family=family)
        return index

    def test_allows_request_default_permission(self):
        discriminator = DummyAllowsDiscriminator(('view',))
        index = self._makeOne(discriminator)
        request = testing.DummyRequest()
        q = index.allows(request)
        self.assertEqual(q._value, [('system.Everyone', 'view')])

    def test_allows_request_nondefault_permission(self):
        discriminator = DummyAllowsDiscriminator(('view', 'edit'))
        index = self._makeOne(discriminator)
        request = testing.DummyRequest()
        q = index.allows(request, 'edit')
        self.assertEqual(q._value, [('system.Everyone', 'edit')])

    def test_allows_no_default_permission(self):
        discriminator = DummyAllowsDiscriminator(('view', 'edit'))
        index = self._makeOne(discriminator)
        request = testing.DummyRequest()
        self.assertRaises(ValueError, index.allows, request)

    def test_allows_bad__permission(self):
        discriminator = DummyAllowsDiscriminator(('view', 'edit'))
        index = self._makeOne(discriminator)
        request = testing.DummyRequest()
        self.assertRaises(ValueError, index.allows, request, 'whatever')

    def test_allows_iterable(self):
        discriminator = DummyAllowsDiscriminator(('edit',))
        index = self._makeOne(discriminator)
        q = index.allows(['bob', 'joe'], 'edit')
        self.assertEqual(q._value, [('bob', 'edit'), ('joe', 'edit')])

    def test_allows_single(self):
        discriminator = DummyAllowsDiscriminator(('edit',))
        index = self._makeOne(discriminator)
        q = index.allows('bob', 'edit')
        self.assertEqual(q._value, [('bob', 'edit')])

class TestIndexPropertySheet(unittest.TestCase):
    def _makeOne(self, context, request):
        from ..indexes import IndexPropertySheet
        return IndexPropertySheet(context, request)

    def test_set_action_mode_different(self):
        from substanced.interfaces import (
            MODE_IMMEDIATE,
            MODE_ATCOMMIT,
            )
        context = testing.DummyResource()
        context.action_mode = MODE_ATCOMMIT
        inst = self._makeOne(context, None)
        inst.set({'action_mode':'MODE_IMMEDIATE'})
        self.assertEqual(context.action_mode, MODE_IMMEDIATE)

    def test_set_action_mode_same(self):
        from substanced.interfaces import MODE_ATCOMMIT
        context = testing.DummyResource()
        context.action_mode = MODE_ATCOMMIT
        inst = self._makeOne(context, None)
        inst.set({'action_mode':'MODE_ATCOMMIT'})
        self.assertEqual(context.action_mode, MODE_ATCOMMIT)

    def test_get_action_mode(self):
        from substanced.interfaces import MODE_IMMEDIATE
        context = testing.DummyResource()
        context.action_mode = MODE_IMMEDIATE
        inst = self._makeOne(context, None)
        result = inst.get()
        self.assertEqual(result['action_mode'], 'MODE_IMMEDIATE')

class Dummy(object):
    pass

class DummyCatalog(object):
    family = BTrees.family64
    def __init__(self, objectids=None):
        if objectids is None:
            objectids = self.family.II.TreeSet()
        self.objectids = objectids

class DummyObjectmap(object):
    def object_for(self, docid): return 'a'

class DummyQuery(object):
    def flush(self, *arg, **kw):
        self.flushed = True
        
    def _apply(self, names):
        return [1,2,3]
    
class DummyDiscriminator(object):
    permissions = (1, 2)
    def __call__(self): pass

class DummyActionTM(object):
    def __init__(self, index):
        self.index = index
        self.actions = []
    def register(self):
        self.registered = True
    def flush(self, all):
        self.flushed = all
    def add(self, action):
        self.actions.append(action)
        
class DummyAllowsDiscriminator(object):
    def __init__(self, permissions):
        self.permissions = permissions

    def __call__(self): pass
    
