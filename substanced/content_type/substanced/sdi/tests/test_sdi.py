import unittest
from pyramid import testing

class Test_add_mgmt_view(unittest.TestCase):
    def _callFUT(self, config, **kw):
        from .. import add_mgmt_view
        return add_mgmt_view(config, **kw)

    def _makeConfig(self):
        config = DummyConfigurator()
        return config

    def test_default_permission_is_sdi_view(self):
        config = self._makeConfig()
        self._callFUT(config)
        self.assertEqual(config._added['permission'], 'sdi.view')

    def test_with_request_method(self):
        config = self._makeConfig()
        self._callFUT(config, request_method=('HEAD', 'GET'))
        self.assertEqual(config._added['request_method'], ('HEAD', 'GET'))
        self.assertTrue(config._actions)

    def test_view_isclass_with_attr(self):
        class AView(object):
            pass
        config = self._makeConfig()
        self._callFUT(config, view=AView, attr='foo')
        self.assertTrue(config.desc.startswith('method'))

    def test_discriminator(self):
        config = self._makeConfig()
        self._callFUT(config)
        discrim = config._actions[0][0]
        self.assertEqual(discrim.resolve(),
                         ('sdi view', None, '', 'substanced_manage', 'hash')
                         )

    def test_intr_action(self):
        config = self._makeConfig()
        self._callFUT(config)
        self.assertEqual(config._actions[0][1][0], config._intr)

    def test_intr_related(self):
        config = self._makeConfig()
        self._callFUT(config)
        self.assertTrue('views' in config._intr.related)

    def test_intr_values(self):
        config = self._makeConfig()
        self._callFUT(
            config,
            tab_title='tab_title',
            tab_condition='tab_condition',
            check_csrf=True
            )
        self.assertEqual(config._intr['tab_title'], 'tab_title')
        self.assertEqual(config._intr['tab_condition'], 'tab_condition')
        self.assertEqual(config._intr.related['views'].resolve(),
                         ('view', None, '', 'substanced_manage', 'hash'))

    def test_with_tab_near_and_tab_before(self):
        from pyramid.exceptions import ConfigurationError
        from .. import MIDDLE
        config = self._makeConfig()
        self.assertRaises(
            ConfigurationError,
            self._callFUT,
            config,
            tab_near=MIDDLE,
            tab_before='tab2',
            )

    def test_with_tab_near_and_tab_after(self):
        from pyramid.exceptions import ConfigurationError
        from .. import MIDDLE
        config = self._makeConfig()
        self.assertRaises(
            ConfigurationError,
            self._callFUT,
            config,
            tab_near=MIDDLE,
            tab_after='tab2',
            )

    def test_with_tab_near_left(self):
        from .. import LEFT, FIRST, CENTER1
        config = self._makeConfig()
        self._callFUT(
            config,
            tab_near=LEFT,
            )
        self.assertEqual(config._intr['tab_before'], CENTER1)
        self.assertEqual(config._intr['tab_after'], FIRST)
        self.assertEqual(config._intr['tab_near'], LEFT)

    def test_with_tab_near_middle(self):
        from .. import MIDDLE, CENTER1, CENTER2
        config = self._makeConfig()
        self._callFUT(
            config,
            tab_near=MIDDLE,
            )
        self.assertEqual(config._intr['tab_before'], CENTER2)
        self.assertEqual(config._intr['tab_after'], CENTER1)
        self.assertEqual(config._intr['tab_near'], MIDDLE)
        
    def test_with_tab_near_right(self):
        from .. import RIGHT, CENTER2, LAST
        config = self._makeConfig()
        self._callFUT(
            config,
            tab_near=RIGHT,
            )
        self.assertEqual(config._intr['tab_before'], LAST)
        self.assertEqual(config._intr['tab_after'], CENTER2)
        self.assertEqual(config._intr['tab_near'], RIGHT)

    def test_with_tab_near_unknown(self):
        from pyramid.exceptions import ConfigurationError
        config = self._makeConfig()
        self.assertRaises(
            ConfigurationError,
            self._callFUT,
            config,
            tab_near='wontwork',
            )

class Test_mgmt_view(unittest.TestCase):
    def setUp(self):
        testing.setUp()

    def tearDown(self):
        testing.tearDown()

    def _getTargetClass(self):
        from .. import mgmt_view
        return mgmt_view

    def _makeOne(self, *arg, **kw):
        return self._getTargetClass()(*arg, **kw)

    def test_create_defaults(self):
        decorator = self._makeOne()
        self.assertEqual(decorator.__dict__, {})

    def test_create_nondefaults(self):
        decorator = self._makeOne(
            name=None,
            request_type=None,
            permission='foo',
            mapper='mapper',
            decorator='decorator',
            match_param='match_param',
            )
        self.assertEqual(decorator.name, None)
        self.assertEqual(decorator.request_type, None)
        self.assertEqual(decorator.permission, 'foo')
        self.assertEqual(decorator.mapper, 'mapper')
        self.assertEqual(decorator.decorator, 'decorator')
        self.assertEqual(decorator.match_param, 'match_param')
        
    def test_call_function(self):
        decorator = self._makeOne()
        venusian = DummyVenusian()
        decorator.venusian = venusian
        def foo(): pass
        wrapped = decorator(foo)
        self.assertTrue(wrapped is foo)
        context = testing.DummyResource()
        context.config = DummyConfigurator()
        venusian.callback(context, None, 'abc')
        self.assertEqual(context.config.view, 'abc')

    def test_call_class_no_attr(self):
        decorator = self._makeOne()
        info = DummyVenusianInfo(scope='class')
        venusian = DummyVenusian(info)
        decorator.venusian = venusian
        def foo(): pass
        wrapped = decorator(foo)
        self.assertTrue(wrapped is foo)
        context = testing.DummyResource()
        context.config = DummyConfigurator()
        venusian.callback(context, None, None)
        self.assertEqual(context.config.settings['attr'], 'foo')

    def test_call_class_with_attr(self):
        decorator = self._makeOne(attr='bar')
        info = DummyVenusianInfo(scope='class')
        venusian = DummyVenusian(info)
        decorator.venusian = venusian
        def foo(): pass
        wrapped = decorator(foo)
        self.assertTrue(wrapped is foo)
        context = testing.DummyResource()
        context.config = DummyConfigurator()
        venusian.callback(context, None, None)
        self.assertEqual(context.config.settings['attr'], 'bar')

class Test_sdi_mgmt_views(unittest.TestCase):
    def setUp(self):
        testing.setUp()

    def tearDown(self):
        testing.tearDown()
        
    def _callFUT(self, context, request, names=None):
        from .. import sdi_mgmt_views
        return sdi_mgmt_views(context, request, names)

    def test_context_has_no_name(self):
        result = self._callFUT(None, None)
        self.assertEqual(result, [])

    def test_no_views_found(self):
        request = testing.DummyRequest()
        request.matched_route = None
        request.registry.content = DummyContent()
        request.registry.introspector = DummyIntrospector()
        context = testing.DummyResource()
        result = self._callFUT(context, request)
        self.assertEqual(result, [])

    def test_no_related_view(self):
        request = testing.DummyRequest()
        request.matched_route = None
        request.registry.content = DummyContent()
        intr = {}
        intr['tab_title'] = None
        intr['tab_condition'] = None
        intr['tab_before'] = None
        intr['tab_after'] = None
        intr = DummyIntrospectable(related=(), introspectable=intr)
        request.registry.introspector = DummyIntrospector([(intr,)])
        context = testing.DummyResource()
        result = self._callFUT(context, request)
        self.assertEqual(result, [])

    def test_one_related_view_gardenpath(self):
        request = testing.DummyRequest()
        request.matched_route = None
        request.sdiapi = DummySDIAPI()
        request.registry.content = DummyContent()
        request.view_name = 'name'
        view_intr = DummyIntrospectable()
        view_intr.category_name = 'views'
        view_intr['name'] = 'name'
        view_intr['context'] = None
        view_intr['derived_callable'] = None
        intr = {}
        intr['tab_title'] = None
        intr['tab_condition'] = None
        intr['tab_before'] = None
        intr['tab_after'] = None
        intr = DummyIntrospectable(related=(view_intr,), introspectable=intr)
        request.registry.introspector = DummyIntrospector([(intr,)])
        context = testing.DummyResource()
        result = self._callFUT(context, request)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]['view_name'], 'name')
        self.assertEqual(result[0]['title'], 'Name')
        self.assertEqual(result[0]['class'], 'active')
        self.assertEqual(result[0]['url'], '/mgmt_path')

    def test_one_related_view_somecontext_tabcondition_None(self):
        from zope.interface import Interface
        class IFoo(Interface):
            pass
        request = testing.DummyRequest()
        request.matched_route = None
        request.sdiapi = DummySDIAPI()
        request.registry.content = DummyContent()
        view_intr = DummyIntrospectable()
        view_intr.category_name = 'views'
        view_intr['name'] = 'name'
        view_intr['context'] = IFoo
        view_intr['derived_callable'] = None
        intr = {}
        intr['tab_title'] = None
        intr['tab_condition'] = None
        intr['tab_before'] = None
        intr['tab_after'] = None
        intr = DummyIntrospectable(related=(view_intr,), introspectable=intr)
        request.registry.introspector = DummyIntrospector([(intr,)])
        context = testing.DummyResource()
        result = self._callFUT(context, request)
        self.assertEqual(result, [])

    def test_one_related_view_instcontext_tabcondition_None(self):
        class Foo(object):
            pass
        request = testing.DummyRequest()
        request.matched_route = None
        request.sdiapi = DummySDIAPI()
        request.registry.content = DummyContent()
        view_intr = DummyIntrospectable()
        view_intr.category_name = 'views'
        view_intr['name'] = 'name'
        view_intr['context'] = Foo
        view_intr['derived_callable'] = None
        intr = {}
        intr['tab_title'] = None
        intr['tab_condition'] = None
        intr['tab_before'] = None
        intr['tab_after'] = None
        intr = DummyIntrospectable(related=(view_intr,), introspectable=intr)
        request.registry.introspector = DummyIntrospector([(intr,)])
        context = testing.DummyResource()
        result = self._callFUT(context, request)
        self.assertEqual(result, [])

    def test_one_related_view_anycontext_tabcondition_False(self):
        request = testing.DummyRequest()
        request.matched_route = None
        request.sdiapi = DummySDIAPI()
        request.registry.content = DummyContent()
        view_intr = DummyIntrospectable()
        view_intr.category_name = 'views'
        view_intr['name'] = 'name'
        view_intr['context'] = None
        view_intr['derived_callable'] = None
        intr = {}
        intr['tab_title'] = None
        intr['tab_condition'] = False
        intr['tab_before'] = None
        intr['tab_after'] = None
        intr = DummyIntrospectable(related=(view_intr,), introspectable=intr)
        request.registry.introspector = DummyIntrospector([(intr,)])
        context = testing.DummyResource()
        result = self._callFUT(context, request)
        self.assertEqual(result, [])

    def test_one_related_view_anycontext_tabcondition_True(self):
        request = testing.DummyRequest()
        request.matched_route = None
        request.sdiapi = DummySDIAPI()
        request.registry.content = DummyContent()
        view_intr = DummyIntrospectable()
        view_intr.category_name = 'views'
        view_intr['name'] = 'name'
        view_intr['context'] = None
        view_intr['derived_callable'] = None
        intr = {}
        intr['tab_title'] = None
        intr['tab_condition'] = True
        intr['tab_before'] = None
        intr['tab_after'] = None
        intr = DummyIntrospectable(related=(view_intr,), introspectable=intr)
        request.registry.introspector = DummyIntrospector([(intr,)])
        context = testing.DummyResource()
        result = self._callFUT(context, request)
        self.assertEqual(len(result), 1)

    def test_one_related_view_anycontext_tabcondition_callable(self):
        request = testing.DummyRequest()
        request.matched_route = None
        request.sdiapi = DummySDIAPI()
        request.registry.content = DummyContent()
        view_intr = DummyIntrospectable()
        view_intr.category_name = 'views'
        view_intr['name'] = 'name'
        view_intr['context'] = None
        view_intr['derived_callable'] = None
        intr = {}
        def tabcondition(context, request):
            return False
        intr['tab_title'] = None
        intr['tab_condition'] = tabcondition
        intr['tab_before'] = None
        intr['tab_after'] = None
        intr = DummyIntrospectable(related=(view_intr,), introspectable=intr)
        request.registry.introspector = DummyIntrospector([(intr,)])
        context = testing.DummyResource()
        result = self._callFUT(context, request)
        self.assertEqual(result, [])

    def test_one_related_view_anycontext_tabcondition_None_not_in_names(self):
        request = testing.DummyRequest()
        request.matched_route = None
        request.sdiapi = DummySDIAPI()
        request.registry.content = DummyContent()
        view_intr = DummyIntrospectable()
        view_intr.category_name = 'views'
        view_intr['name'] = 'name'
        view_intr['context'] = None
        view_intr['derived_callable'] = None
        intr = {}
        intr['tab_title'] = None
        intr['tab_condition'] = None
        intr['tab_before'] = None
        intr['tab_after'] = None
        intr = DummyIntrospectable(related=(view_intr,), introspectable=intr)
        request.registry.introspector = DummyIntrospector([(intr,)])
        context = testing.DummyResource()
        result = self._callFUT(context, request, names=('fred',))
        self.assertEqual(result, [])

    def test_one_related_view_anycontext_tabcondition_None_predicatefail(self):
        request = testing.DummyRequest()
        request.matched_route = None
        request.sdiapi = DummySDIAPI()
        request.registry.content = DummyContent()
        view_intr = DummyIntrospectable()
        view_intr.category_name = 'views'
        view_intr['name'] = 'name'
        view_intr['context'] = None
        class Thing(object):
            def __predicated__(self, context, request):
                return False
        thing = Thing()
        view_intr['derived_callable'] = thing
        intr = {}
        intr['tab_title'] = None
        intr['tab_condition'] = None
        intr['tab_before'] = None
        intr['tab_after'] = None
        intr = DummyIntrospectable(related=(view_intr,), introspectable=intr)
        request.registry.introspector = DummyIntrospector([(intr,)])
        context = testing.DummyResource()
        result = self._callFUT(context, request)
        self.assertEqual(result, [])

    def test_one_related_view_anycontext_tabcondition_None_permissionfail(self):
        request = testing.DummyRequest()
        request.matched_route = None
        request.sdiapi = DummySDIAPI()
        request.registry.content = DummyContent()
        view_intr = DummyIntrospectable()
        view_intr.category_name = 'views'
        view_intr['name'] = 'name'
        view_intr['context'] = None
        class Thing(object):
            def __permitted__(self, context, request):
                return False
        thing = Thing()
        view_intr['derived_callable'] = thing
        intr = {}
        intr['tab_title'] = None
        intr['tab_condition'] = None
        intr['tab_before'] = None
        intr['tab_after'] = None
        intr = DummyIntrospectable(related=(view_intr,), introspectable=intr)
        request.registry.introspector = DummyIntrospector([(intr,)])
        context = testing.DummyResource()
        result = self._callFUT(context, request)
        self.assertEqual(result, [])

    def test_one_related_view_two_tabs_gardenpath_tab_title_sorting(self):
        request = testing.DummyRequest()
        request.matched_route = None
        request.sdiapi = DummySDIAPI()
        request.registry.content = DummyContent()
        view_intr = DummyIntrospectable()
        view_intr.category_name = 'views'
        view_intr['name'] = 'name'
        view_intr['context'] = None
        view_intr['derived_callable'] = None
        intr = {}
        intr['tab_title'] = 'b'
        intr['tab_condition'] = None
        intr['tab_before'] = None
        intr['tab_after'] = None
        intr2 = {}
        intr2['tab_title'] = 'a'
        intr2['tab_condition'] = None
        intr2['tab_before'] = None
        intr2['tab_after'] = None
        intr = DummyIntrospectable(related=(view_intr,), introspectable=intr)
        intr2 = DummyIntrospectable(related=(view_intr,), introspectable=intr2)
        request.registry.introspector = DummyIntrospector([(intr, intr2)])
        context = testing.DummyResource()
        result = self._callFUT(context, request)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]['view_name'], 'name')
        self.assertEqual(result[0]['title'], 'b')
        self.assertEqual(result[0]['class'], None)
        self.assertEqual(result[0]['url'], '/mgmt_path')
        # "a" is gone because we choose the first view data item via sort-break

    def test_one_related_view_gardenpath_with_taborder(self):
        request = testing.DummyRequest()
        request.matched_route = None
        request.sdiapi = DummySDIAPI()
        request.registry.content = DummyContent(tab_order=('b',))
        request.view_name = 'b'
        view_intr1 = DummyIntrospectable()
        view_intr1.category_name = 'views'
        view_intr1['name'] = 'b'
        view_intr1['context'] = None
        view_intr1['derived_callable'] = None
        view_intr2 = DummyIntrospectable()
        view_intr2.category_name = 'views'
        view_intr2['name'] = 'a'
        view_intr2['context'] = None
        view_intr2['derived_callable'] = None
        intr = {}
        intr['tab_title'] = 'b'
        intr['tab_condition'] = None
        intr['tab_before'] = None
        intr['tab_after'] = None
        intr2 = {}
        intr2['tab_title'] = 'a'
        intr2['tab_condition'] = None
        intr2['tab_before'] = None
        intr2['tab_after'] = None
        intr = DummyIntrospectable(related=(view_intr1,), introspectable=intr)
        intr2 = DummyIntrospectable(related=(view_intr2,), introspectable=intr2)
        request.registry.introspector = DummyIntrospector([(intr, intr2)])
        context = testing.DummyResource()
        result = self._callFUT(context, request)
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]['view_name'], 'b')
        self.assertEqual(result[0]['title'], 'b')
        self.assertEqual(result[0]['class'], 'active')
        self.assertEqual(result[0]['url'], '/mgmt_path')
        self.assertEqual(result[1]['view_name'], 'a')
        self.assertEqual(result[1]['title'], 'a')
        self.assertEqual(result[1]['class'], None)
        self.assertEqual(result[1]['url'], '/mgmt_path')

    def test_one_related_view_gardenpath_with_tab_before(self):
        request = testing.DummyRequest()
        request.matched_route = None
        request.sdiapi = DummySDIAPI()
        request.registry.content = DummyContent()
        request.view_name = 'b'
        view_intr1 = DummyIntrospectable()
        view_intr1.category_name = 'views'
        view_intr1['name'] = 'b'
        view_intr1['context'] = None
        view_intr1['derived_callable'] = None
        view_intr2 = DummyIntrospectable()
        view_intr2.category_name = 'views'
        view_intr2['name'] = 'a'
        view_intr2['context'] = None
        view_intr2['derived_callable'] = None
        intr = {}
        intr['tab_title'] = 'b'
        intr['tab_condition'] = None
        intr['tab_before'] = 'a'
        intr['tab_after'] = None
        intr2 = {}
        intr2['tab_title'] = 'a'
        intr2['tab_condition'] = None
        intr2['tab_before'] = None
        intr2['tab_after'] = None
        intr = DummyIntrospectable(related=(view_intr1,), introspectable=intr)
        intr2 = DummyIntrospectable(related=(view_intr2,), introspectable=intr2)
        request.registry.introspector = DummyIntrospector([(intr, intr2)])
        context = testing.DummyResource()
        result = self._callFUT(context, request)
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]['view_name'], 'b')
        self.assertEqual(result[0]['title'], 'b')
        self.assertEqual(result[0]['class'], 'active')
        self.assertEqual(result[0]['url'], '/mgmt_path')
        self.assertEqual(result[1]['view_name'], 'a')
        self.assertEqual(result[1]['title'], 'a')
        self.assertEqual(result[1]['class'], None)
        self.assertEqual(result[1]['url'], '/mgmt_path')

    def test_gardenpath_with_tab_before_and_after(self):
        from substanced.sdi import CENTER1, CENTER2, FIRST, LAST
        request = testing.DummyRequest()
        request.matched_route = None
        request.sdiapi = DummySDIAPI()
        request.registry.content = DummyContent()
        request.view_name = 'b'
        view_intr1 = DummyIntrospectable()
        view_intr1.category_name = 'views'
        view_intr1['name'] = 'c'
        view_intr1['context'] = None
        view_intr1['derived_callable'] = None
        view_intr2 = DummyIntrospectable()
        view_intr2.category_name = 'views'
        view_intr2['name'] = 'a'
        view_intr2['context'] = None
        view_intr2['derived_callable'] = None
        view_intr3 = DummyIntrospectable()
        view_intr3.category_name = 'views'
        view_intr3['name'] = 'b'
        view_intr3['context'] = None
        view_intr3['derived_callable'] = None
        view_intr4 = DummyIntrospectable()
        view_intr4.category_name = 'views'
        view_intr4['name'] = 'd'
        view_intr4['context'] = None
        view_intr4['derived_callable'] = None
        intr = {}
        intr['tab_title'] = 'c'
        intr['tab_condition'] = None
        intr['tab_before'] = CENTER1
        intr['tab_after'] = FIRST
        intr2 = {}
        intr2['tab_title'] = 'a'
        intr2['tab_condition'] = None
        intr2['tab_before'] = LAST
        intr2['tab_after'] = CENTER2
        intr3 = {}
        intr3['tab_title'] = 'b'
        intr3['tab_condition'] = None
        intr3['tab_before'] = CENTER2
        intr3['tab_after'] = CENTER1
        intr4 = {}
        intr4['tab_title'] = 'd'
        intr4['tab_condition'] = None
        intr4['tab_before'] = CENTER2
        intr4['tab_after'] = CENTER1
        
        intr = DummyIntrospectable(related=(view_intr1,), introspectable=intr)
        intr2 = DummyIntrospectable(related=(view_intr2,), introspectable=intr2)
        intr3 = DummyIntrospectable(related=(view_intr3,), introspectable=intr3)
        intr4 = DummyIntrospectable(related=(view_intr4,), introspectable=intr4)
        request.registry.introspector = DummyIntrospector(
            [(intr, intr2, intr3, intr4)]
            )
        context = testing.DummyResource()
        result = self._callFUT(context, request)
        self.assertEqual(len(result), 4)
        self.assertEqual(result[0]['view_name'], 'c')
        self.assertEqual(result[0]['title'], 'c')
        self.assertEqual(result[0]['class'], None)
        self.assertEqual(result[0]['url'], '/mgmt_path')
        self.assertEqual(result[1]['view_name'], 'b')
        self.assertEqual(result[1]['title'], 'b')
        self.assertEqual(result[1]['class'], 'active')
        self.assertEqual(result[1]['url'], '/mgmt_path')
        self.assertEqual(result[2]['view_name'], 'd')
        self.assertEqual(result[2]['title'], 'd')
        self.assertEqual(result[2]['class'], None)
        self.assertEqual(result[2]['url'], '/mgmt_path')
        self.assertEqual(result[3]['view_name'], 'a')
        self.assertEqual(result[3]['title'], 'a')
        self.assertEqual(result[3]['class'], None)
        self.assertEqual(result[3]['url'], '/mgmt_path')

    def test_duplicate_view_names_ordering_context_is_iface(self):
        from zope.interface import Interface
        from zope.interface import directlyProvides
        request = testing.DummyRequest()
        request.matched_route = None
        request.sdiapi = DummySDIAPI()
        request.registry.content = DummyContent()
        request.view_name = 'name'
        class I1(Interface):
            pass
        class I2(Interface):
            pass
        view_intr1 = DummyIntrospectable()
        view_intr1.category_name = 'views'
        view_intr1['name'] = 'name'
        view_intr1['context'] = I1
        view_intr1['derived_callable'] = None
        intr1 = {}
        intr1['tab_title'] = 'One'
        intr1['tab_condition'] = None
        intr1['tab_before'] = None
        intr1['tab_after'] = None
        intr1 = DummyIntrospectable(related=(view_intr1,), introspectable=intr1)
        view_intr2 = DummyIntrospectable()
        view_intr2.category_name = 'views'
        view_intr2['name'] = 'name'
        view_intr2['context'] = I2
        view_intr2['derived_callable'] = None
        intr2 = {}
        intr2['tab_title'] = 'Two'
        intr2['tab_condition'] = None
        intr2['tab_before'] = None
        intr2['tab_after'] = None
        intr2 = DummyIntrospectable(related=(view_intr2,), introspectable=intr2)
        request.registry.introspector = DummyIntrospector([(intr1, intr2)])
        context = testing.DummyResource()
        directlyProvides(context, (I2, I1))
        result = self._callFUT(context, request)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]['view_name'], 'name')
        self.assertEqual(result[0]['title'], 'Two')

    def test_duplicate_view_names_ordering_context_is_class(self):
        request = testing.DummyRequest()
        request.matched_route = None
        request.sdiapi = DummySDIAPI()
        request.registry.content = DummyContent()
        request.view_name = 'name'
        class MoreDirectContext(testing.DummyResource):
            pass
        view_intr1 = DummyIntrospectable()
        view_intr1.category_name = 'views'
        view_intr1['name'] = 'name'
        view_intr1['context'] = MoreDirectContext
        view_intr1['derived_callable'] = None
        intr1 = {}
        intr1['tab_title'] = 'One'
        intr1['tab_condition'] = None
        intr1['tab_before'] = None
        intr1['tab_after'] = None
        intr1 = DummyIntrospectable(related=(view_intr1,), introspectable=intr1)
        view_intr2 = DummyIntrospectable()
        view_intr2.category_name = 'views'
        view_intr2['name'] = 'name'
        view_intr2['context'] = testing.DummyResource
        view_intr2['derived_callable'] = None
        intr2 = {}
        intr2['tab_title'] = 'Two'
        intr2['tab_condition'] = None
        intr2['tab_before'] = None
        intr2['tab_after'] = None
        intr2 = DummyIntrospectable(related=(view_intr2,), introspectable=intr2)
        request.registry.introspector = DummyIntrospector([(intr1, intr2)])
        context = MoreDirectContext()
        result = self._callFUT(context, request)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]['view_name'], 'name')
        self.assertEqual(result[0]['title'], 'One')

    def test_duplicate_view_names_ordering_context_iface_doesnt_match(self):
        from zope.interface import Interface
        class I1(Interface): pass
        request = testing.DummyRequest()
        request.matched_route = None
        request.sdiapi = DummySDIAPI()
        request.registry.content = DummyContent()
        request.view_name = 'name'
        class MoreDirectContext(testing.DummyResource):
            pass
        view_intr1 = DummyIntrospectable()
        view_intr1.category_name = 'views'
        view_intr1['name'] = 'name'
        view_intr1['context'] = MoreDirectContext
        view_intr1['derived_callable'] = None
        intr1 = {}
        intr1['tab_title'] = 'One'
        intr1['tab_condition'] = None
        intr1['tab_before'] = None
        intr1['tab_after'] = None
        intr1 = DummyIntrospectable(related=(view_intr1,), introspectable=intr1)
        view_intr2 = DummyIntrospectable()
        view_intr2.category_name = 'views'
        view_intr2['name'] = 'name'
        view_intr2['context'] = I1
        view_intr2['derived_callable'] = None
        intr2 = {}
        intr2['tab_title'] = 'Two'
        intr2['tab_condition'] = None
        intr2['tab_before'] = None
        intr2['tab_after'] = None
        intr2 = DummyIntrospectable(related=(view_intr2,), introspectable=intr2)
        request.registry.introspector = DummyIntrospector([(intr1, intr2)])
        context = MoreDirectContext()
        result = self._callFUT(context, request)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]['view_name'], 'name')
        self.assertEqual(result[0]['title'], 'One')

    def test_duplicate_view_names_ordering_context_neither_iface_nor_cls_match(
        self):
        from zope.interface import Interface
        class I1(Interface): pass
        request = testing.DummyRequest()
        request.matched_route = None
        request.sdiapi = DummySDIAPI()
        request.registry.content = DummyContent()
        request.view_name = 'name'
        class MoreDirectContext(object):
            pass
        view_intr1 = DummyIntrospectable()
        view_intr1.category_name = 'views'
        view_intr1['name'] = 'name'
        view_intr1['context'] = MoreDirectContext
        view_intr1['derived_callable'] = None
        intr1 = {}
        intr1['tab_title'] = 'One'
        intr1['tab_condition'] = None
        intr1['tab_before'] = None
        intr1['tab_after'] = None
        intr1 = DummyIntrospectable(related=(view_intr1,), introspectable=intr1)
        view_intr2 = DummyIntrospectable()
        view_intr2.category_name = 'views'
        view_intr2['name'] = 'name'
        view_intr2['context'] = I1
        view_intr2['derived_callable'] = None
        intr2 = {}
        intr2['tab_title'] = 'Two'
        intr2['tab_condition'] = None
        intr2['tab_before'] = None
        intr2['tab_after'] = None
        intr2 = DummyIntrospectable(related=(view_intr2,), introspectable=intr2)
        request.registry.introspector = DummyIntrospector([(intr1, intr2)])
        context = testing.DummyResource()
        result = self._callFUT(context, request)
        self.assertEqual(len(result), 0)
        
class Test_default_sdi_addable(unittest.TestCase):
    def _callFUT(self, context, intr):
        from .. import default_sdi_addable
        return default_sdi_addable(context, intr)

    def test_is_service_with_service_name_in_context(self):
        context = {'catalog':True}
        intr = {'meta':{'is_service':True, 'service_name':'catalog'}}
        self.assertFalse(self._callFUT(context, intr))
                         
    def test_is_service_with_service_name_not_in_context(self):
        context = {}
        intr = {'meta':{'is_service':True, 'service_name':'catalog'}}
        self.assertTrue(self._callFUT(context, intr))
    
    def test_is_service_without_service_name(self):
        context = {'catalog':True}
        intr = {'meta':{'is_service':True}}
        self.assertTrue(self._callFUT(context, intr))

    def test_is_not_service(self):
        context = {'catalog':True}
        intr = {'meta':{}}
        self.assertTrue(self._callFUT(context, intr))

class Test_sdi_add_views(unittest.TestCase):
    def _callFUT(self, context, request):
        from .. import sdi_add_views
        return sdi_add_views(context, request)

    def setUp(self):
        testing.setUp()

    def tearDown(self):
        testing.tearDown()

    def test_no_content_types(self):
        request = testing.DummyRequest()
        request.matched_route = None
        request.registry.content = DummyContent()
        request.registry.introspector = DummyIntrospector()
        result = self._callFUT(None, request)
        self.assertEqual(result, [])

    def test_one_content_type(self):
        request = testing.DummyRequest()
        request.matched_route = None
        request.registry.content = DummyContent()
        request.sdiapi = DummySDIAPI()
        ct_intr = {}
        ct_intr['meta'] = {'add_view':'abc'}
        ct_intr['content_type'] = 'Content'
        ct_intr = DummyIntrospectable(introspectable=ct_intr)
        view_intr1 = DummyIntrospectable()
        view_intr1.category_name = 'views'
        view_intr1['name'] = 'abc'
        view_intr1['context'] = None
        view_intr1['derived_callable'] = None
        intr = {}
        intr['tab_title'] = 'abc'
        intr['tab_condition'] = None
        intr['tab_before'] = None
        intr['tab_after'] = None
        intr = DummyIntrospectable(related=(view_intr1,), introspectable=intr)
        request.registry.introspector = DummyIntrospector([(ct_intr,), (intr,)])
        context = testing.DummyResource()
        result = self._callFUT(context, request)
        self.assertEqual(
            result,
            [{
                    'url': '/mgmt_path',
                    'type_name': 'Content',
                    'icon': '',
                    'content_type':'Content',
                    }])

    def test_one_content_type_not_addable(self):
        request = testing.DummyRequest()
        request.matched_route = None
        request.registry.content = DummyContent()
        request.sdiapi = DummySDIAPI()
        context = testing.DummyResource()
        context.__sdi_addable__ = ('Not Content',)
        ct_intr = {}
        ct_intr['meta'] = {'add_view':'abc'}
        ct_intr['content_type'] = 'Content'
        ct_intr = DummyIntrospectable(introspectable=ct_intr)
        view_intr1 = DummyIntrospectable()
        view_intr1.category_name = 'views'
        view_intr1['name'] = 'abc'
        view_intr1['context'] = None
        view_intr1['derived_callable'] = None
        intr = {}
        intr['tab_title'] = 'abc'
        intr['tab_condition'] = None
        intr['tab_before'] = None
        intr['tab_after'] = None
        intr = DummyIntrospectable(related=(view_intr1,), introspectable=intr)
        request.registry.introspector = DummyIntrospector([(ct_intr,), (intr,)])
        result = self._callFUT(context, request)
        self.assertEqual(result, [])

    def test_one_content_type_not_addable_callable(self):
        request = testing.DummyRequest()
        request.matched_route = None
        request.registry.content = DummyContent()
        request.sdiapi = DummySDIAPI()
        context = testing.DummyResource()
        context.__sdi_addable__ = lambda *arg: False
        ct_intr = {}
        ct_intr['meta'] = {'add_view':'abc'}
        ct_intr['content_type'] = 'Content'
        ct_intr = DummyIntrospectable(introspectable=ct_intr)
        view_intr1 = DummyIntrospectable()
        view_intr1.category_name = 'views'
        view_intr1['name'] = 'abc'
        view_intr1['context'] = None
        view_intr1['derived_callable'] = None
        intr = {}
        intr['tab_title'] = 'abc'
        intr['tab_condition'] = None
        intr['tab_before'] = None
        intr['tab_after'] = None
        intr = DummyIntrospectable(related=(view_intr1,), introspectable=intr)
        request.registry.introspector = DummyIntrospector([(ct_intr,), (intr,)])
        result = self._callFUT(context, request)
        self.assertEqual(result, [])
        
    def test_content_type_not_addable_to(self):
        request = testing.DummyRequest()
        request.matched_route = None
        request.registry.content = DummyContent()
        request.sdiapi = DummySDIAPI()
        context = testing.DummyResource()
        context.__content_type__ = 'Foo'
        ct_intr = {}
        ct_intr['meta'] = {'add_view':lambda *arg: 'abc'}
        ct_intr['content_type'] = 'Content'
        ct_intr = DummyIntrospectable(introspectable=ct_intr)
        ct2_intr = {}
        checked = []
        def check(context, request):
            checked.append(True)
        ct2_intr['meta'] = {'add_view':check}
        ct2_intr['content_type'] = 'Content'
        ct2_intr = DummyIntrospectable(introspectable=ct2_intr)
        view_intr1 = DummyIntrospectable()
        view_intr1.category_name = 'views'
        view_intr1['name'] = 'abc'
        view_intr1['context'] = None
        view_intr1['derived_callable'] = None
        intr = {}
        intr['tab_title'] = 'abc'
        intr['tab_condition'] = None
        intr['tab_before'] = None
        intr['tab_after'] = None
        intr = DummyIntrospectable(related=(view_intr1,), introspectable=intr)
        request.registry.introspector = DummyIntrospector(
            [(ct_intr, ct2_intr), (intr,)])
        result = self._callFUT(context, request)
        self.assertEqual(checked, [True])
        self.assertEqual(
            result,
            [
                {'url': '/mgmt_path',
                 'type_name': 'Content',
                 'icon': '',
                 'content_type':'Content',
                 }])

class Test_user(unittest.TestCase):
    def _callFUT(self, request):
        from .. import user
        return user(request)

    def setUp(self):
        self.config = testing.setUp()

    def tearDown(self):
        testing.tearDown()

    def test_userid_is_None(self):
        self.config.testing_securitypolicy(permissive=False)
        request = testing.DummyRequest()
        self.assertEqual(self._callFUT(request), None)

    def test_userid_is_not_None(self):
        from ...interfaces import IFolder
        self.config.testing_securitypolicy(permissive=True, userid='fred')
        request = testing.DummyRequest()
        context = testing.DummyResource(__provides__=IFolder)
        objectmap = testing.DummyResource()
        objectmap.object_for = lambda *arg: 'foo'
        context.__objectmap__ = objectmap
        request.context = context
        self.assertEqual(self._callFUT(request), 'foo')

class Test_sdiapi(unittest.TestCase):
    def setUp(self):
        self.config = testing.setUp()

    def tearDown(self):
        testing.tearDown()
        
    def _makeOne(self, request):
        from .. import sdiapi
        return sdiapi(request)

    def test_main_template(self):
        self.config.testing_securitypolicy(permissive=False)
        request = testing.DummyRequest()
        inst = self._makeOne(request)
        self.assertTrue(inst.main_template)

    def test_flash_with_undo_no_permission(self):
        self.config.testing_securitypolicy(permissive=False)
        request = testing.DummyRequest()
        inst = self._makeOne(request)
        connection = DummyConnection()
        inst.get_connection = lambda *arg: connection
        inst.transaction = DummyTransaction()
        inst.flash_with_undo('message')
        self.assertEqual(request.session['_f_'], ['message'])
        self.assertFalse(inst.transaction.notes)

    def test_flash_with_undo_db_doesnt_support_undo(self):
        self.config.testing_securitypolicy(permissive=True)
        request = testing.DummyRequest()
        inst = self._makeOne(request)
        connection = DummyConnection(supports_undo=False)
        inst.get_connection = lambda *arg: connection
        inst.transaction = DummyTransaction()
        inst.flash_with_undo('message')
        self.assertEqual(request.session['_f_'], ['message'])
        self.assertFalse(inst.transaction.notes)

    def test_flash_with_undo_gardenpath(self):
        from ..._compat import u
        self.config.testing_securitypolicy(permissive=True)
        request = testing.DummyRequest()
        inst = self._makeOne(request)
        connection = DummyConnection()
        inst.get_connection = lambda *arg: connection
        inst.transaction = DummyTransaction()
        inst.mgmt_path = lambda *arg, **kw: '/mg'
        inst.flash_with_undo('message')
        self.assertEqual(request.session['_f_'],
                         [u('<span>message <a href="/mg" class="btn btn-mini '
                            'btn-info">Undo</a></span>\n')])
        self.assertTrue(inst.transaction.notes)

    def test_mgmt_path(self):
        from .. import MANAGE_ROUTE_NAME
        request = testing.DummyRequest()
        context = testing.DummyResource()
        def resource_path(resource, *arg, **kw):
            self.assertEqual(arg, ('a',))
            self.assertEqual(kw, {'b':1, 'route_name':MANAGE_ROUTE_NAME})
            return '/path'
        request.resource_path = resource_path
        inst = self._makeOne(request)
        result = inst.mgmt_path(context, 'a', b=1)
        self.assertEqual(result, '/path')

    def test_mgmt_path_with_alt_route_name(self):
        route_name = 'foo'
        request = testing.DummyRequest()
        context = testing.DummyResource()
        def resource_path(resource, *arg, **kw):
            self.assertEqual(arg, ('a',))
            self.assertEqual(kw, {'b':1, 'route_name':route_name})
            return '/path'
        request.resource_path = resource_path
        inst = self._makeOne(request)
        result = inst.mgmt_path(context, 'a', b=1, route_name=route_name)
        self.assertEqual(result, '/path')
        
    def test_mgmt_url(self):
        from .. import MANAGE_ROUTE_NAME
        request = testing.DummyRequest()
        context = testing.DummyResource()
        def resource_url(resource, *arg, **kw):
            self.assertEqual(arg, ('a',))
            self.assertEqual(kw, {'b':1, 'route_name':MANAGE_ROUTE_NAME})
            return 'http://example.com/path'
        request.resource_url = resource_url
        inst = self._makeOne(request)
        result = inst.mgmt_url(context, 'a', b=1)
        self.assertEqual(result, 'http://example.com/path')

    def test_mgmt_url_with_alt_route_name(self):
        route_name = 'foo'
        request = testing.DummyRequest()
        context = testing.DummyResource()
        def resource_url(resource, *arg, **kw):
            self.assertEqual(arg, ('a',))
            self.assertEqual(kw, {'b':1, 'route_name':route_name})
            return 'http://example.com/path'
        request.resource_url = resource_url
        inst = self._makeOne(request)
        result = inst.mgmt_url(context, 'a', b=1, route_name=route_name)
        self.assertEqual(result, 'http://example.com/path')
        
    def test_breadcrumbs_no_permissions(self):
        self.config.testing_securitypolicy(permissive=False)
        resource = testing.DummyResource()
        request = testing.DummyRequest()
        request.context = resource
        inst = self._makeOne(request)
        result = inst.breadcrumbs()
        self.assertEqual(result, [])
        
    def test_breadcrumbs_with_permissions(self):
        self.config.testing_securitypolicy(permissive=True)
        resource = testing.DummyResource()
        request = testing.DummyRequest()
        request.sdiapi = DummySDIAPI()
        request.context = resource
        request.registry.content = DummyContent()
        inst = self._makeOne(request)
        result = inst.breadcrumbs()
        self.assertEqual(
            result,
             [{'url': '/mgmt_path',
               'active': 'active',
               'name': 'Home',
               'icon': None}]
            )

    def test_breadcrumbs_with_vroot(self):
        self.config.testing_securitypolicy(permissive=True)
        resource = testing.DummyResource()
        second = testing.DummyResource()
        second.__parent__ = resource
        second.__name__ = 'second'
        request = testing.DummyRequest()
        request.virtual_root = second
        request.sdiapi = DummySDIAPI()
        request.context = second
        request.registry.content = DummyContent()
        inst = self._makeOne(request)
        result = inst.breadcrumbs()
        self.assertEqual(
            result,
             [{'url': '/mgmt_path',
               'active': 'active',
               'name': 'second',
               'icon': None}]
            )
        
    def test_sdi_title_exists(self):
        resource = testing.DummyResource()
        resource.sdi_title = 'My Title'
        request = testing.DummyRequest()
        request.context = resource
        inst = self._makeOne(request)
        result = inst.sdi_title()
        self.assertEqual(result, 'My Title')

    def test_sdi_title_missing(self):
        resource = testing.DummyResource()
        request = testing.DummyRequest()
        request.context = resource
        inst = self._makeOne(request)
        result = inst.sdi_title()
        self.assertEqual(result, 'Substance D')

    def test_mgmt_views(self):
        resource = testing.DummyResource()
        request = testing.DummyRequest()
        request.context = resource
        inst = self._makeOne(request)
        inst.sdi_mgmt_views = lambda *arg, **kw: True
        self.assertEqual(inst.mgmt_views(resource), True)

    def test_get_macro_without_name(self):
        request = testing.DummyRequest()
        inst = self._makeOne(request)
        macro = inst.get_macro('substanced.sdi.views:templates/master.pt')
        self.assertTrue(macro.macros)
        
    def test_get_macro_with_name(self):
        request = testing.DummyRequest()
        inst = self._makeOne(request)
        macro = inst.get_macro(
            'substanced.sdi.views:templates/master.pt', 'main')
        self.assertTrue(macro.include)

class Test_mgmt_path(unittest.TestCase):
    def _callFUT(self, *arg, **kw):
        from .. import mgmt_path
        return mgmt_path(*arg, **kw)

    def test_it(self):
        request = testing.DummyRequest()
        request.sdiapi = DummySDIAPI()
        result = self._callFUT(request, None)
        self.assertEqual(result, '/mgmt_path')

class Test_mgmt_url(unittest.TestCase):
    def _callFUT(self, *arg, **kw):
        from .. import mgmt_url
        return mgmt_url(*arg, **kw)

    def test_it(self):
        request = testing.DummyRequest()
        request.sdiapi = DummySDIAPI()
        result = self._callFUT(request, None)
        self.assertEqual(result, 'http://mgmt_url')

class Test_flash_with_undo(unittest.TestCase):
    def _callFUT(self, *arg, **kw):
        from .. import flash_with_undo
        return flash_with_undo(*arg, **kw)

    def test_it(self):
        request = testing.DummyRequest()
        request.sdiapi = DummySDIAPI()
        self._callFUT(request, 'a')
        self.assertEqual(request.sdiapi.flashed, 'a')

class Test__bwcompat_kw(unittest.TestCase):
    def _callFUT(self, kw):
        from .. import _bwcompat_kw
        return _bwcompat_kw(kw)

    def test_call_with_all(self):
        kw = {
            '_query':'query',
            '_anchor':'anchor',
            '_app_url':'app_url',
            '_host':'host',
            '_scheme':'scheme',
            '_port':'port'
            }
        result = self._callFUT(kw)
        self.assertEqual(
            result,
            {
                'query':'query',
                'anchor':'anchor',
                'app_url':'app_url',
                'host':'host',
                'scheme':'scheme',
                'port':'port'
                }
            )
        

class DummyContent(object):
    def __init__(self, **kw):
        self.__dict__.update(kw)
        
    def metadata(self, context, name, default=None):
        return getattr(self, name, default)

class DummyIntrospector(object):
    def __init__(self, results=()):
        self.results = list(results)
        
    def get_category(self, *arg):
        if self.results:
            return self.results.pop(0)
        return ()

class DummyVenusianInfo(object):
    scope = None
    codeinfo = None
    module = None
    def __init__(self, **kw):
        self.__dict__.update(kw)
    
class DummyVenusian(object):
    def __init__(self, info=None):
        if info is None:
            info = DummyVenusianInfo()
        self.info = info
        
    def attach(self, wrapped, callback, category):
        self.wrapped = wrapped
        self.callback = callback
        self.category = category
        return self.info

class DummyPredicateList(object):
    def make(self, config, **pvals):
        return 1, (), 'hash'

class DummyConfigurator(object):
    _ainfo = None
    def __init__(self):
        self._intr = DummyIntrospectable()
        self._actions = []
        self._added = None
        self.get_predlist = lambda *arg: DummyPredicateList()

    def object_description(self, ob):
        return ob
        
    def maybe_dotted(self, thing):
        return thing

    def add_view(self, **kw):
        self._added = kw

    def add_mgmt_view(self, view=None, **settings):
        self.view = view
        self.settings = settings

    def with_package(self, other):
        return self

    def introspectable(self, category, discrim, desc, name):
        self.desc = desc
        return self._intr

    def action(self, discriminator, introspectables):
        self._actions.append((discriminator, introspectables))
    
class DummyIntrospectable(dict):
    def __init__(self, **kw):
        dict.__init__(self, **kw)
        self.related = {}
        
    def relate(self, category, discrim):
        self.related[category] = discrim

class Dummy(object):
    pass

class DummyDB(object):
    def __init__(self, supports_undo, undo_info, undo_exc=None):
        self.supports_undo = supports_undo
        self.undo_info = undo_info
        self.undone = []
        self.undo_exc = undo_exc

    def supportsUndo(self):
        return self.supports_undo

class DummyConnection(object):
    def __init__(self, supports_undo=True, undo_info=(), undo_exc=None):
        self._db = DummyDB(supports_undo, undo_info, undo_exc)

    def db(self):
        return self._db

class DummyTransaction(object):
    def __init__(self):
        self.notes = []
        
    def get(self):
        return self

    def note(self, note):
        self.notes.append(note)

    def setExtendedInfo(self, name, value):
        self.extinfo = (name, value)

class DummySDIAPI(object):
    def __init__(self, result=None):
        self.result = result
        
    def mgmt_path(self, obj, *arg, **kw):
        return self.result or '/mgmt_path'

    def mgmt_url(self, obj, *arg, **kw):
        return self.result or 'http://mgmt_url'

    def flash_with_undo(self, val):
        self.flashed = val
    
