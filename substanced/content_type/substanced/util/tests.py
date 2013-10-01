import unittest

from pyramid import testing

from . import _marker

class Test__postorder(unittest.TestCase):
    def setUp(self):
        testing.setUp()

    def tearDown(self):
        testing.tearDown()

    def _callFUT(self, node):
        from . import postorder
        return postorder(node)

    def test_None_node(self):
        result = list(self._callFUT(None))
        self.assertEqual(result, [None])

    def test_IFolder_node_no_children(self):
        from ..interfaces import IFolder
        model = testing.DummyResource(__provides__=IFolder)
        result = list(self._callFUT(model))
        self.assertEqual(result, [model])

    def test_IFolder_node_nonfolder_children(self):
        from ..interfaces import IFolder
        model = testing.DummyResource(__provides__=IFolder)
        one = testing.DummyResource()
        two = testing.DummyResource()
        model['one'] = one
        model['two'] = two
        result = list(self._callFUT(model))
        self.assertEqual(result, [one, two, model])

    def test_IFolder_node_folder_children(self):
        from ..interfaces import IFolder
        model = testing.DummyResource(__provides__=IFolder)
        one = testing.DummyResource()
        two = testing.DummyResource(__provides__=IFolder)
        model['one'] = one
        model['two'] = two
        three = testing.DummyResource()
        four = testing.DummyResource()
        two['three'] = three
        two['four'] = four
        result = list(self._callFUT(model))
        self.assertEqual(result, [one, four, three, two, model])

class Test_get_oid(unittest.TestCase):
    def _callFUT(self, obj, default=_marker):
        from . import get_oid
        return get_oid(obj, default)

    def test_gardenpath(self):
        obj = testing.DummyResource()
        obj.__oid__ = 1
        self.assertEqual(self._callFUT(obj), 1)

    def test_no_objectid_no_default(self):
        obj = testing.DummyResource()
        self.assertRaises(AttributeError, self._callFUT, obj)

    def test_no_objectid_with_default(self):
        obj = testing.DummyResource()
        self.assertEqual(self._callFUT(obj, 1), 1)

class Test_set_oid(unittest.TestCase):
    def _callFUT(self, obj, val):
        from . import set_oid
        return set_oid(obj, val)

    def test_gardenpath(self):
        obj = testing.DummyResource()
        self._callFUT(obj, 1)
        self.assertEqual(obj.__oid__, 1)

class TestBatch(unittest.TestCase):
    def _makeOne(self, seq, request, url=None, default_size=15, seqlen=None):
        from . import Batch
        return Batch(seq, request, url, default_size, seqlen=seqlen)

    def test_it_first_batch_of_3(self):
        seq = [1,2,3,4,5,6,7]
        request = testing.DummyRequest()
        request.params['batch_num'] = 0
        request.params['batch_size'] = 3
        request.url = 'http://example.com'
        inst = self._makeOne(seq, request)
        self.assertEqual(inst.items, [1,2,3])
        self.assertEqual(inst.num, 0)
        self.assertEqual(inst.size, 3)
        self.assertEqual(inst.length, 3)
        self.assertEqual(inst.last, 2)
        self.assertEqual(inst.required, True)
        self.assertEqual(inst.first_url, None)
        self.assertEqual(inst.prev_url, None)
        self.assertEqual(inst.next_url,
                         'http://example.com?batch_num=1&batch_size=3')
        self.assertEqual(inst.last_url,
                         'http://example.com?batch_num=2&batch_size=3')

    def test_it_first_batch_of_3_generator(self):
        def gen():
            for x in [1,2,3,4,5,6,7]:
                yield x
        seq = gen()
        request = testing.DummyRequest()
        request.params['batch_num'] = 0
        request.params['batch_size'] = 3
        request.url = 'http://example.com'
        inst = self._makeOne(seq, request, seqlen=7)
        self.assertEqual(inst.items, [1,2,3])
        self.assertEqual(inst.num, 0)
        self.assertEqual(inst.size, 3)
        self.assertEqual(inst.length, 3)
        self.assertEqual(inst.last, 2)
        self.assertEqual(inst.required, True)
        self.assertEqual(inst.first_url, None)
        self.assertEqual(inst.prev_url, None)
        self.assertEqual(inst.next_url,
                         'http://example.com?batch_num=1&batch_size=3')
        self.assertEqual(inst.last_url,
                         'http://example.com?batch_num=2&batch_size=3')

    def test_it_second_batch_of_3(self):
        seq = [1,2,3,4,5,6,7]
        request = testing.DummyRequest()
        request.params['batch_num'] = 1
        request.params['batch_size'] = 3
        request.url = 'http://example.com'
        inst = self._makeOne(seq, request)
        self.assertEqual(inst.items, [4,5,6])
        self.assertEqual(inst.num, 1)
        self.assertEqual(inst.size, 3)
        self.assertEqual(inst.length, 3)
        self.assertEqual(inst.last, 2)
        self.assertEqual(inst.required, True)
        self.assertEqual(inst.first_url,
                         'http://example.com?batch_num=0&batch_size=3')
        self.assertEqual(inst.prev_url,
                         'http://example.com?batch_num=0&batch_size=3')
        self.assertEqual(inst.next_url,
                         'http://example.com?batch_num=2&batch_size=3')
        self.assertEqual(inst.last_url,
                         'http://example.com?batch_num=2&batch_size=3')

    def test_it_second_batch_of_3_generator(self):
        def gen():
            for x in [1,2,3,4,5,6,7]:
                yield x
        seq = gen()
        request = testing.DummyRequest()
        request.params['batch_num'] = 1
        request.params['batch_size'] = 3
        request.url = 'http://example.com'
        inst = self._makeOne(seq, request, seqlen=7)
        self.assertEqual(inst.items, [4,5,6])
        self.assertEqual(inst.num, 1)
        self.assertEqual(inst.size, 3)
        self.assertEqual(inst.length, 3)
        self.assertEqual(inst.last, 2)
        self.assertEqual(inst.required, True)
        self.assertEqual(inst.first_url,
                         'http://example.com?batch_num=0&batch_size=3')
        self.assertEqual(inst.prev_url,
                         'http://example.com?batch_num=0&batch_size=3')
        self.assertEqual(inst.next_url,
                         'http://example.com?batch_num=2&batch_size=3')
        self.assertEqual(inst.last_url,
                         'http://example.com?batch_num=2&batch_size=3')

    def test_it_third_batch_of_3(self):
        seq = [1,2,3,4,5,6,7]
        request = testing.DummyRequest()
        request.params['batch_num'] = 2
        request.params['batch_size'] = 3
        request.url = 'http://example.com'
        inst = self._makeOne(seq, request)
        self.assertEqual(inst.items, [7])
        self.assertEqual(inst.num, 2)
        self.assertEqual(inst.size, 3)
        self.assertEqual(inst.length, 1)
        self.assertEqual(inst.last, 2)
        self.assertEqual(inst.required, True)
        self.assertEqual(inst.first_url,
                         'http://example.com?batch_num=0&batch_size=3')
        self.assertEqual(inst.prev_url,
                         'http://example.com?batch_num=1&batch_size=3')
        self.assertEqual(inst.next_url, None)
        self.assertEqual(inst.last_url, None)

    def test_it_third_batch_of_3_generator(self):
        def gen():
            for x in [1,2,3,4,5,6,7]:
                yield x
        seq = gen()
        request = testing.DummyRequest()
        request.params['batch_num'] = 2
        request.params['batch_size'] = 3
        request.url = 'http://example.com'
        inst = self._makeOne(seq, request, seqlen=7)
        self.assertEqual(inst.items, [7])
        self.assertEqual(inst.num, 2)
        self.assertEqual(inst.size, 3)
        self.assertEqual(inst.length, 1)
        self.assertEqual(inst.last, 2)
        self.assertEqual(inst.required, True)
        self.assertEqual(inst.first_url,
                         'http://example.com?batch_num=0&batch_size=3')
        self.assertEqual(inst.prev_url,
                         'http://example.com?batch_num=1&batch_size=3')
        self.assertEqual(inst.next_url, None)
        self.assertEqual(inst.last_url, None)

    def test_it_invalid_batch_num(self):
        seq = [1,2,3,4,5,6,7]
        request = testing.DummyRequest()
        request.params['batch_num'] = None
        request.params['batch_size'] = 3
        request.url = 'http://example.com'
        inst = self._makeOne(seq, request)
        self.assertEqual(inst.items, [1,2,3])
        self.assertEqual(inst.num, 0)

    def test_it_negative_batch_num(self):
        seq = [1,2,3,4,5,6,7]
        request = testing.DummyRequest()
        request.params['batch_num'] = -1
        request.params['batch_size'] = 3
        request.url = 'http://example.com'
        inst = self._makeOne(seq, request)
        self.assertEqual(inst.items, [1,2,3])
        self.assertEqual(inst.num, 0)

    def test_it_invalid_batch_size(self):
        seq = [1,2,3,4,5,6,7]
        request = testing.DummyRequest()
        request.params['batch_num'] = 0
        request.params['batch_size'] = None
        request.url = 'http://example.com'
        inst = self._makeOne(seq, request)
        self.assertEqual(inst.items, seq)
        self.assertEqual(inst.size, 15)

    def test_it_negative_batch_size(self):
        seq = [1,2,3,4,5,6,7]
        request = testing.DummyRequest()
        request.params['batch_num'] = 0
        request.params['batch_size'] = -1
        request.url = 'http://example.com'
        inst = self._makeOne(seq, request)
        self.assertEqual(inst.items, seq)
        self.assertEqual(inst.size, 15)

    def test_it_size_zero(self):
        seq = [1,2,3,4,5,6,7]
        request = testing.DummyRequest()
        request.params['batch_num'] = 0
        request.params['batch_size'] = 0
        request.url = 'http://example.com'
        inst = self._makeOne(seq, request)
        self.assertEqual(inst.items, seq)
        self.assertEqual(inst.size, 15)

    def test_it_multicolumn_toggle_text(self):
        seq = [1,2,3,4,5,6]
        request = testing.DummyRequest()
        request.params['multicolumn'] = 'True'
        inst = self._makeOne(seq, request)
        self.assertEqual(inst.toggle_text, 'Single column')

    def test_it_not_multicolumn_toggle_text(self):
        seq = [1,2,3,4,5,6]
        request = testing.DummyRequest()
        request.params['multicolumn'] = 'False'
        inst = self._makeOne(seq, request)
        self.assertEqual(inst.toggle_text, 'Multi-column')

    def test_it_make_columns(self):
        seq = [1,2,3,4,5,6]
        request = testing.DummyRequest()
        inst = self._makeOne(seq, request)
        cols = inst.make_columns(column_size=2, num_columns=3)
        expected = [ [1,2], [3,4], [5,6] ]
        self.assertEqual(cols, expected)

class Test_merge_url_qs(unittest.TestCase):
    def _callFUT(self, url, **kw):
        from . import merge_url_qs
        return merge_url_qs(url, **kw)

    def test_with_no_qs(self):
        url = 'http://example.com'
        result = self._callFUT(url, a=1, b=2)
        self.assertEqual(result, 'http://example.com?a=1&b=2')

    def test_with_existing_qs_overlap(self):
        url = 'http://example.com?a=3'
        result = self._callFUT(url, a=1, b=2)
        self.assertEqual(result, 'http://example.com?a=1&b=2')

    def test_with_existing_qs_no_overlap(self):
        url = 'http://example.com?c=3'
        result = self._callFUT(url, a=1, b=2)
        self.assertEqual(result, 'http://example.com?a=1&b=2&c=3')

class Test_acquire(unittest.TestCase):
    def _callFUT(self, node, name, default=None):
        from . import acquire
        if default is None:
            return acquire(node, name)
        else:
            return acquire(node, name, default)

    def test_missing_with_default(self):
        inst = DummyContent(None)
        marker = object()
        self.assertEqual(self._callFUT(inst, 'abc', marker), marker)

    def test_missing_no_default(self):
        inst = DummyContent(None)
        self.assertRaises(AttributeError, self._callFUT, inst, 'abc')

    def test_hit(self):
        inst = DummyContent(None)
        inst.abc = '123'
        self.assertEqual(self._callFUT(inst, 'abc'), '123')

class Test_coarse_datetime_repr(unittest.TestCase):
    def _callFUT(self, d):
        from . import coarse_datetime_repr
        return coarse_datetime_repr(d)

    def test_it(self):
        import calendar
        import datetime
        d = datetime.datetime.utcnow()
        result = self._callFUT(d)
        timetime = calendar.timegm(d.timetuple())
        val = int(timetime) // 100        
        self.assertEqual(result, val)

class Test_renamer(unittest.TestCase):
    def _makeOne(self):
        from . import renamer
        return renamer()

    def test_get_has_no_name(self):
        class Foo(object):
            name = self._makeOne()
        foo = Foo()
        self.assertEqual(foo.name, None)

    def test_get_has_a_name(self):
        class Foo(object):
            name = self._makeOne()
        foo = Foo()
        foo.__name__ = 'fred'
        self.assertEqual(foo.name, 'fred')

    def test_set_has_no_parent(self):
        class Foo(object):
            name = self._makeOne()
        foo = Foo()
        foo.__name__ = 'fred'
        foo.name = 'bar' # doesn't blow up
        self.assertEqual(foo.name, 'fred')

    def test_set_has_parent_same_value(self):
        class Foo(object):
            name = self._makeOne()
        foo = Foo()
        foo.__name__ = 'fred'
        parent = DummyContent()
        foo.__parent__ = parent
        foo.name = 'fred' # doesn't blow up
        self.assertEqual(foo.name, 'fred')
        self.assertEqual(parent.renamed_from, None)

    def test_set_has_parent_different_value(self):
        class Foo(object):
            name = self._makeOne()
        foo = Foo()
        foo.__name__ = 'fred'
        parent = DummyContent()
        foo.__parent__ = parent
        foo.name = 'bob'
        self.assertEqual(parent.renamed_from, 'fred')
        self.assertEqual(parent.renamed_to, 'bob')

class Test_get_acl(unittest.TestCase):
    def _callFUT(self, obj, default=_marker):
        from . import get_acl
        return get_acl(obj, default)

    def test_gardenpath(self):
        obj = testing.DummyResource()
        obj.__acl__ = 1
        self.assertEqual(self._callFUT(obj), 1)

    def test_no_objectid_no_default(self):
        obj = testing.DummyResource()
        self.assertRaises(AttributeError, self._callFUT, obj)

    def test_no_objectid_with_default(self):
        obj = testing.DummyResource()
        self.assertEqual(self._callFUT(obj, 1), 1)

class Test_set_acl(unittest.TestCase):
    def setUp(self):
        self.config = testing.setUp()

    def tearDown(self):
        testing.tearDown()

    def _callFUT(self, context, acl, registry=None):
        from . import set_acl
        return set_acl(context, acl, registry)

    def test_no_change_context_has_no_acl(self):
        context = testing.DummyResource()
        result = self._callFUT(context, None)
        self.assertFalse(result)

    def test_change_context_has_no_acl(self):
        context = testing.DummyResource()
        registry = DummyRegistry()
        result = self._callFUT(context, 1, registry)
        self.assertTrue(result)
        self.assertEqual(registry.event.old_acl, None)
        self.assertEqual(registry.event.new_acl, 1)
        self.assertEqual(context.__acl__, 1)

    def test_change_remove_acl(self):
        context = testing.DummyResource()
        context.__acl__ = 1
        registry = DummyRegistry()
        result = self._callFUT(context, None, registry)
        self.assertTrue(result)
        self.assertEqual(registry.event.old_acl, 1)
        self.assertEqual(registry.event.new_acl, None)
        self.assertFalse(hasattr(context, '__acl__'))
        
    def test_no_registry(self):
        context = testing.DummyResource()
        L = []
        self.config.registry.subscribers = lambda *arg: L.append(arg)
        result = self._callFUT(context, 1)
        self.assertTrue(result)
        self.assertEqual(context.__acl__, 1)
        self.assertEqual(L[0][1], None)

class Test_get_dotted_name(unittest.TestCase):
    def _callFUT(self, obj):
        from . import get_dotted_name
        return get_dotted_name(obj)

    def test_module(self):
        from substanced import util
        result = self._callFUT(util)
        self.assertEqual(result, 'substanced.util')

    def test_nonmodule(self):
        result = self._callFUT(self.__class__)
        self.assertEqual(result, 'substanced.util.tests.Test_get_dotted_name')

class Test_get_content_type(unittest.TestCase):
    def setUp(self):
        self.config = testing.setUp()

    def tearDown(self):
        testing.tearDown()

    def _callFUT(self, resource, registry=None):
        from . import get_content_type
        return get_content_type(resource, registry=registry)

    def test_without_registry(self):
        self.config.registry.content = DummyContentRegistry()
        resource = Dummy()
        resource.type = 'foo'
        self.assertEqual(self._callFUT(resource), 'foo')
        
    def test_with_registry(self):
        registry = Dummy()
        registry.content = DummyContentRegistry()
        resource = Dummy()
        resource.type = 'bar'
        self.assertEqual(self._callFUT(resource, registry), 'bar')

class Test_find_content(unittest.TestCase):
    def setUp(self):
        self.config = testing.setUp()

    def tearDown(self):
        testing.tearDown()

    def _callFUT(self, resource, content_type, registry=None):
        from . import find_content
        return find_content(resource, content_type, registry)

    def test_without_registry(self):
        self.config.registry.content = DummyContentRegistry()
        resource = Dummy()
        self.assertEqual(self._callFUT(resource, 1), resource)
        
    def test_with_registry(self):
        registry = Dummy()
        registry.content = DummyContentRegistry()
        resource = Dummy()
        self.assertEqual(self._callFUT(resource, 1, registry), resource)

class Test_find_service(unittest.TestCase):
    def _callFUT(self, context, name, *subnames):
        from . import find_service
        return find_service(context, name, *subnames)
    
    def test_unfound(self):
        from ..interfaces import IFolder
        site = testing.DummyResource(__provides__=IFolder)
        self.assertEqual(self._callFUT(site, 'catalog'), None)
        
    def test_found(self):
        from ..interfaces import IFolder
        site = testing.DummyResource(__provides__=IFolder)
        catalog = testing.DummyResource(__is_service__=True)
        site['catalog'] = catalog
        self.assertEqual(self._callFUT(site, 'catalog'), catalog)

    def test_unfound_with_subnames(self):
        from ..interfaces import IFolder
        site = testing.DummyResource(__provides__=IFolder)
        catalog = testing.DummyResource(__is_service__=True)
        site['catalog'] = catalog
        result = self._callFUT(site, 'catalog', 'a', 'b')
        self.assertEqual(result, None)

    def test_unfound_with_subnames_inner_not_folder(self):
        from ..interfaces import IFolder
        site = testing.DummyResource(__provides__=IFolder)
        catalog = testing.DummyResource(__is_service__=True,
                                        __provides__=IFolder)
        site['catalog'] = catalog
        catalog['a'] = testing.DummyResource()
        result = self._callFUT(site, 'catalog', 'a', 'b')
        self.assertEqual(result, None)

    def test_found_with_subnames_missing(self):
        from ..interfaces import IFolder
        site = testing.DummyResource(__provides__=IFolder)
        catalog = testing.DummyResource(__is_service__=True,
                                        __provides__=IFolder)
        site['catalog'] = catalog
        catalog['a'] = testing.DummyResource(__provides__=IFolder)
        catalog['a']['b'] = testing.DummyResource()
        result = self._callFUT(site, 'catalog', 'a', 'c')
        self.assertEqual(result, None)

    def test_found_with_subnames(self):
        from ..interfaces import IFolder
        site = testing.DummyResource(__provides__=IFolder)
        catalog = testing.DummyResource(__is_service__=True,
                                        __provides__=IFolder)
        site['catalog'] = catalog
        catalog['a'] = testing.DummyResource(__provides__=IFolder)
        catalog['a']['b'] = testing.DummyResource()
        result = self._callFUT(site, 'catalog', 'a', 'b')
        self.assertEqual(result, catalog['a']['b'])


class Test_find_services(unittest.TestCase):
    def _callFUT(self, context, name, *subnames):
        from . import find_services
        return find_services(context, name, *subnames)
    
    def test_one_found(self):
        from ..interfaces import IFolder
        site = testing.DummyResource(__provides__=IFolder)
        catalog = testing.DummyResource(__is_service__=True)
        site['catalog'] = catalog
        self.assertEqual(self._callFUT(site, 'catalog'), [catalog])
        
    def test_two_found(self):
        from ..interfaces import IFolder
        folder = testing.DummyResource(__provides__=IFolder)
        catalog1 = testing.DummyResource(__is_service__=True)
        folder['catalog'] = catalog1
        site = testing.DummyResource(__provides__=IFolder)
        catalog2 = testing.DummyResource(__is_service__=True)
        site['catalog'] = catalog2
        site['folder'] = folder
        self.assertEqual(self._callFUT(folder, 'catalog'), [catalog1, catalog2])
    
    def test_unfound(self):
        from ..interfaces import IFolder
        site = testing.DummyResource(__provides__=IFolder)
        self.assertEqual(self._callFUT(site, 'catalog'), [])

    def test_unfound2(self):
        from ..interfaces import IFolder
        site = testing.DummyResource(__provides__=IFolder)
        self.assertEqual(self._callFUT(site, 'catalog'), [])

    def test_unfound_with_subnames(self):
        from ..interfaces import IFolder
        site = testing.DummyResource(__provides__=IFolder)
        catalog = testing.DummyResource(__is_service__=True)
        site['catalog'] = catalog
        result = self._callFUT(site, 'catalog', 'a', 'b')
        self.assertEqual(result, [])

    def test_unfound_with_subnames_inner_not_folder(self):
        from ..interfaces import IFolder
        site = testing.DummyResource(__provides__=IFolder)
        catalog = testing.DummyResource(__is_service__=True,
                                        __provides__=IFolder)
        site['catalog'] = catalog
        catalog['a'] = testing.DummyResource()
        result = self._callFUT(site, 'catalog', 'a', 'b')
        self.assertEqual(result, [])

    def test_found_with_subnames_missing(self):
        from ..interfaces import IFolder
        site = testing.DummyResource(__provides__=IFolder)
        catalog = testing.DummyResource(__is_service__=True,
                                        __provides__=IFolder)
        site['catalog'] = catalog
        catalog['a'] = testing.DummyResource(__provides__=IFolder)
        catalog['a']['b'] = testing.DummyResource()
        result = self._callFUT(site, 'catalog', 'a', 'c')
        self.assertEqual(result, [])

    def test_found_with_subnames(self):
        from ..interfaces import IFolder
        site = testing.DummyResource(__provides__=IFolder)
        catalog = testing.DummyResource(__is_service__=True,
                                        __provides__=IFolder)
        site['catalog'] = catalog
        catalog['a'] = testing.DummyResource(__provides__=IFolder)
        catalog['a']['b'] = testing.DummyResource()
        result = self._callFUT(site, 'catalog', 'a', 'b')
        self.assertEqual(result, [catalog['a']['b']])


class Test_get_factory_type(unittest.TestCase):
    def _callFUT(self, resource):
        from . import get_factory_type
        return get_factory_type(resource)

    def test_has_ft_attr(self):
        resource = Dummy()
        resource.__factory_type__ = 'abc'
        self.assertEqual(self._callFUT(resource), 'abc')

    def test_without_ft_attr(self):
        resource = Dummy()
        self.assertEqual(self._callFUT(resource),
                         'substanced.util.tests.Dummy')

class Test_get_interfaces(unittest.TestCase):
    def _callFUT(self, resource, classes=True):
        from . import get_interfaces
        return get_interfaces(resource, classes=classes)

    def test_with_classes(self):
        from zope.interface import Interface, implementer
        class IFoo(Interface):
            pass
        @implementer(IFoo)
        class Foo(object):
            pass
        foo = Foo()
        result = self._callFUT(foo)
        self.assertEqual(result, set([IFoo, Interface, Foo]))
        
    def test_without_classes(self):
        from zope.interface import Interface, implementer
        class IFoo(Interface):
            pass
        @implementer(IFoo)
        class Foo(object):
            pass
        foo = Foo()
        result = self._callFUT(foo, classes=False)
        self.assertEqual(result, set([IFoo, Interface]))
        
class Test_find_catalogs(unittest.TestCase):
    def _callFUT(self, resource, name=None):
        from . import find_catalogs
        return find_catalogs(resource, name=name)

    def _makeTree(self):
        from substanced.interfaces import IFolder
        root = testing.DummyResource(__provides__=IFolder)
        catalogs1 = root['catalogs'] = testing.DummyResource(
            __is_service__=True)
        catalog1 = testing.DummyResource()
        catalogs1['catalog1'] = catalog1
        sub = testing.DummyResource(__provides__=IFolder)
        root['sub'] = sub
        catalogs2 = sub['catalogs'] = testing.DummyResource(__is_service__=True)
        catalog2 = testing.DummyResource()
        catalog1_2 = testing.DummyResource()
        sub['catalogs'] = catalogs2
        catalogs2['catalog2'] = catalog2
        catalogs2['catalog1'] = catalog1_2
        return root

    def test_no_catalogs(self):
        resource = testing.DummyResource()
        self.assertEqual(self._callFUT(resource), [])

    def test_with_multiple_catalogs_no_name(self):
        root = self._makeTree()
        sub = root['sub']
        catalog2 = sub['catalogs']['catalog2']
        catalog1_2 = sub['catalogs']['catalog1']
        catalog1 = root['catalogs']['catalog1']
        result = set(self._callFUT(sub))
        self.assertEqual(len(result), 3)
        self.assertTrue(catalog1 in result)
        self.assertTrue(catalog2 in result)
        self.assertTrue(catalog1_2 in result)

    def test_with_multiple_catalogs_and_name(self):
        root = self._makeTree()
        sub = root['sub']
        catalog1_2 = sub['catalogs']['catalog1']
        catalog1 = root['catalogs']['catalog1']
        result = list(enumerate(self._callFUT(sub, 'catalog1')))
        self.assertEqual(
            result,
            [ (0, catalog1_2), (1, catalog1) ],
            )

    def test_nosuch_catalog(self):
        root = self._makeTree()
        sub = root['sub']
        result = list(enumerate(self._callFUT(sub, 'catalog3')))
        self.assertEqual(
            result,
            [],
            )

class Test_find_catalog(unittest.TestCase):
    def _callFUT(self, resource, name):
        from . import find_catalog
        return find_catalog(resource, name)

    def _makeTree(self):
        from substanced.interfaces import IFolder
        root = testing.DummyResource(__provides__=IFolder)
        catalogs1 = root['catalogs'] = testing.DummyResource(
            __is_service__=True)
        catalog1 = testing.DummyResource()
        catalogs1['catalog1'] = catalog1
        sub = testing.DummyResource(__provides__=IFolder)
        root['sub'] = sub
        catalogs2 = sub['catalogs'] = testing.DummyResource(__is_service__=True)
        catalog2 = testing.DummyResource()
        catalog1_2 = testing.DummyResource()
        sub['catalogs'] = catalogs2
        catalogs2['catalog2'] = catalog2
        catalogs2['catalog1'] = catalog1_2
        return root

    def test_no_catalogs(self):
        resource = testing.DummyResource()
        self.assertEqual(self._callFUT(resource, 'catalog1'), None)

    def test_with_multiple_catalogs(self):
        root = self._makeTree()
        sub = root['sub']
        catalog2 = sub['catalogs']['catalog2']
        catalog1_2 = sub['catalogs']['catalog1']
        catalog1 = root['catalogs']['catalog1']
        result = self._callFUT(sub, 'catalog2')
        self.assertEqual(result, catalog2)
        result = self._callFUT(sub, 'catalog1')
        self.assertEqual(result, catalog1_2)
        result = self._callFUT(root, 'catalog1')
        self.assertEqual(result, catalog1)

    def test_nosuch_catalog(self):
        root = self._makeTree()
        sub = root['sub']
        result = self._callFUT(sub, 'catalog3')
        self.assertEqual(
            result,
            None,
            )

class Test_find_index(unittest.TestCase):
    def _callFUT(self, resource, catalog_name, index_name):
        from . import find_index
        return find_index(resource, catalog_name, index_name)

    def _makeTree(self):
        from substanced.interfaces import IFolder
        root = testing.DummyResource(__provides__=IFolder)
        catalogs1 = root['catalogs'] = testing.DummyResource(
            __is_service__=True)
        catalog1 = testing.DummyResource()
        catalogs1['catalog1'] = catalog1
        sub = testing.DummyResource(__provides__=IFolder)
        root['sub'] = sub
        catalogs2 = sub['catalogs'] = testing.DummyResource(__is_service__=True)
        catalog2 = testing.DummyResource()
        catalog1_2 = testing.DummyResource()
        sub['catalogs'] = catalogs2
        catalogs2['catalog2'] = catalog2
        catalogs2['catalog1'] = catalog1_2
        return root

    def test_no_such_catalog(self):
        resource = testing.DummyResource()
        self.assertEqual(self._callFUT(resource, 'catalog1', 'index'), None)

    def test_no_such_index(self):
        resource = self._makeTree()
        self.assertEqual(self._callFUT(resource, 'catalog1', 'index'), None)

    def test_index_found(self):
        resource = self._makeTree()
        index = testing.DummyResource()
        resource['catalogs']['catalog1']['index'] = index
        self.assertEqual(self._callFUT(resource, 'catalog1', 'index'), index)
        
class TestJsonDict(unittest.TestCase):
    def test_it(self):
        from . import JsonDict
        import json
        val = {'a':1}
        d = JsonDict(val)
        self.assertEqual(str(d), json.dumps(val))

class Test_get_principal_repr(unittest.TestCase):
    def _callFUT(self, princ):
        from . import get_principal_repr
        return get_principal_repr(princ)

    def test_int(self):
        result = self._callFUT(1)
        self.assertEqual(result, '1')

    def test_largeint(self):
        result = self._callFUT(2 << 64)
        self.assertEqual(result, '36893488147419103232')

    def test_str(self):
        result = self._callFUT('foo')
        self.assertEqual(result, 'foo')

    def test_inst_with_principal_repr(self):
        class Principal(object):
            __oid__ = 1
            def __principal_repr__(self):
                return 'me'

        inst = Principal()
        result = self._callFUT(inst)
        self.assertEqual(result, 'me')

    def test_inst_with_oid(self):
        class Principal(object):
            __oid__ = 1

        inst = Principal()
        result = self._callFUT(inst)
        self.assertEqual(result, '1')

    def test_inst_without_principal_repr_or_oid(self):
        class Principal(object):
            pass

        inst = Principal()
        self.assertRaises(ValueError, self._callFUT, inst)

class Test_find_objectmap(unittest.TestCase):
    def _callFUT(self, context):
        from . import find_objectmap
        return find_objectmap(context)

    def test_found(self):
        inst = Dummy()
        inst.__objectmap__ = '123'
        self.assertEqual(self._callFUT(inst), '123')

    def test_unfound(self):
        inst = Dummy()
        self.assertEqual(self._callFUT(inst), None)

class Test_get_icon_name(unittest.TestCase):
    def _callFUT(self, resource, request):
        from . import get_icon_name
        return get_icon_name(resource, request)
    
    def test_callable(self):
        registry = Dummy()
        request = testing.DummyRequest()
        def icon(_resource, _request):
            self.assertEqual(_resource, resource)
            self.assertEqual(_request, request)
            return 'icon'
        registry.content = DummyContentRegistry(icon)
        request.registry = registry
        resource = Dummy()
        self.assertEqual(self._callFUT(resource, request), 'icon')

    def test_noncallable(self):
        registry = Dummy()
        request = testing.DummyRequest()
        registry.content = DummyContentRegistry('icon')
        request.registry = registry
        resource = Dummy()
        self.assertEqual(self._callFUT(resource, request), 'icon')


class Test_get_auditlog(unittest.TestCase):
    def _callFUT(self, context):
        from . import get_auditlog
        return get_auditlog(context)

    def test_get_auditlog__p_jar_is_None(self):
        context = testing.DummyResource()
        context._p_jar = None
        inst = self._callFUT(context)
        self.assertEqual(inst, None)

    def test_get_auditlog_exists(self):
        context = testing.DummyResource()
        auditlog = testing.DummyResource()
        root = {'auditlog':auditlog}
        context._p_jar = DummyConnection(root=root)
        inst = self._callFUT(context)
        self.assertEqual(inst, auditlog)

    def test_get_auditlog_notexists(self):
        context = testing.DummyResource()
        root = {}
        context._p_jar = DummyConnection(root=root)
        inst = self._callFUT(context)
        self.assertEqual(inst, None)

    def test_get_auditlog_get_connection_keyerror(self):
        context = testing.DummyResource()
        context._p_jar = DummyConnection(KeyError())
        inst = self._callFUT(context)
        self.assertEqual(inst, None)
        
class DummyContent(object):
    renamed_from = None
    renamed_to = None
    def __init__(self, result=None):
        self.result = result

    def rename(self, old, new):
        self.renamed_from = old
        self.renamed_to = new

class DummyRegistry(object):
    def subscribers(self, event_context, whatever):
        self.event, self.context = event_context
        self.whatever = whatever

class DummyContentRegistry(object):
    def __init__(self, result=None):
        self.result = result
    
    def metadata(self, resource, name, default=None):
        return self.result
    
    def typeof(self, resource):
        return resource.type

    def find(self, resource, content_type):
        return resource

class Dummy(object):
    pass

class DummyConnection(object):
    def __init__(self, conn=None, root=None):
        self._conn = conn
        self._root = root

    def root(self):
        return self._root

    def get_connection(self, name):
        conn = self._conn
        if isinstance(conn, KeyError):
            raise KeyError
        return self

