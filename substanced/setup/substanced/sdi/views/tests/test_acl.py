import unittest

from pyramid import testing

from ...._compat import u
_JOHN = u('john')
_MARY = u('mary')

class TestACLView(unittest.TestCase):
    def setUp(self):
        self.config = testing.setUp()

    def tearDown(self):
        testing.tearDown()

    def _makeOne(self, context, request):
        from ..acl import ACLEditViews
        return ACLEditViews(context, request).acl_view

    def test_view(self):
        from ....testing import make_site
        request = testing.DummyRequest()
        site = make_site()
        site['page'] = context = testing.DummyResource()
        context.__oid__ = 5
        site.__acl__ = context.__acl__ = [(None, 1, (None,))]
        user = DummyUser(1, _JOHN)
        site['principals']['users']['john'] = user
        site.__objectmap__ = DummyObjectMap({1:user})
        inst = self._makeOne(context, request)
        resp = inst()
        self.assertEqual(resp['parent_acl'], [(None, _JOHN, (None,))])
        self.assertEqual(resp['users'], [(1, _JOHN)])
        self.assertEqual(resp['groups'], [('system.Everyone',
                                          'system.Everyone'),
                                          ('system.Authenticated',
                                          'system.Authenticated')])
        self.assertEqual(resp['local_acl'], [(None, _JOHN, (None,))])
        self.assertEqual(resp['permissions'], ['-- ALL --'])
        self.assertEqual(resp['inheriting'], 'enabled')

class TestInheritedACL(TestACLView):

    def _makeOne(self, context, request):
        from ..acl import ACLEditViews
        return ACLEditViews(context, request).inherited_acl

class TestLocaldACL(TestACLView):

    def _makeOne(self, context, request):
        from ..acl import ACLEditViews
        return ACLEditViews(context, request).local_acl

class TestMoveUp(unittest.TestCase):
    def setUp(self):
        self.config = testing.setUp()

    def tearDown(self):
        testing.tearDown()

    def _makeOne(self, context, request):
        from ..acl import ACLEditViews
        return ACLEditViews(context, request).move_up

    def test_view(self):
        from ....testing import make_site
        request = testing.DummyRequest()
        request.sdiapi = DummySDIAPI()
        token = request.session.new_csrf_token()
        request.POST['csrf_token'] = token
        request.POST['index'] = 1
        site = make_site()
        site['page'] = context = testing.DummyResource()
        site.__acl__ = [(None, 1, (None,))]
        context.__acl__ = [(None, 1, (None,)),
                           (None, 2, (None,))]
        context.__oid__ = 5
        user = DummyUser(1, _JOHN)
        user2 = DummyUser(2, _MARY)
        site['principals']['users']['john'] = user
        site.__objectmap__ = DummyObjectMap({1:user, 2:user2})
        inst = self._makeOne(context, request)
        resp = inst()
        self.assertEqual(resp['parent_acl'], [(None, _JOHN, (None,))])
        self.assertEqual(resp['users'], [(1, _JOHN)])
        self.assertEqual(resp['groups'], [('system.Everyone',
                                          'system.Everyone'),
                                          ('system.Authenticated',
                                          'system.Authenticated')])
        self.assertEqual(resp['local_acl'], [(None, _MARY, (None,)),
                                             (None, _JOHN, (None,))])
        self.assertEqual(resp['permissions'], ['-- ALL --'])
        self.assertEqual(resp['inheriting'], 'enabled')
        self.assertEqual(request.sdiapi.flashed, 'ACE moved up')

class TestMoveDown(unittest.TestCase):
    def setUp(self):
        self.config = testing.setUp()

    def tearDown(self):
        testing.tearDown()

    def _makeOne(self, context, request):
        from ..acl import ACLEditViews
        return ACLEditViews(context, request).move_down

    def test_view(self):
        from ....testing import make_site
        request = testing.DummyRequest()
        request.sdiapi = DummySDIAPI()
        token = request.session.new_csrf_token()
        request.POST['csrf_token'] = token
        request.POST['index'] = 0
        site = make_site()
        site['page'] = context = testing.DummyResource()
        site.__acl__ = [(None, 1, (None,))]
        context.__acl__ = [(None, 1, (None,)),
                           (None, 2, (None,))]
        context.__oid__ = 5
        user = DummyUser(1, _JOHN)
        user2 = DummyUser(2, _MARY)
        site['principals']['users']['john'] = user
        site.__objectmap__ = DummyObjectMap({1:user, 2:user2})
        inst = self._makeOne(context, request)
        resp = inst()
        self.assertEqual(resp['parent_acl'], [(None, _JOHN, (None,))])
        self.assertEqual(resp['users'], [(1, _JOHN)])
        self.assertEqual(resp['groups'], [('system.Everyone',
                                          'system.Everyone'),
                                          ('system.Authenticated',
                                          'system.Authenticated')])
        self.assertEqual(resp['local_acl'], [(None, _MARY, (None,)),
                                             (None, _JOHN, (None,))])
        self.assertEqual(resp['permissions'], ['-- ALL --'])
        self.assertEqual(resp['inheriting'], 'enabled')
        self.assertEqual(request.sdiapi.flashed, 'ACE moved down')

class TestRemove(unittest.TestCase):
    def setUp(self):
        self.config = testing.setUp()

    def tearDown(self):
        testing.tearDown()

    def _makeOne(self, context, request):
        from ..acl import ACLEditViews
        return ACLEditViews(context, request).remove

    def test_view(self):
        from ....testing import make_site
        request = testing.DummyRequest()
        request.sdiapi = DummySDIAPI()
        token = request.session.new_csrf_token()
        request.POST['csrf_token'] = token
        request.POST['index'] = 0
        site = make_site()
        site['page'] = context = testing.DummyResource()
        site.__acl__ = [(None, 1, (None,))]
        context.__acl__ = [(None, 1, (None,)),
                           (None, 2, (None,))]
        context.__oid__ = 5
        user = DummyUser(1, _JOHN)
        user2 = DummyUser(2, _MARY)
        site['principals']['users']['john'] = user
        site.__objectmap__ = DummyObjectMap({1:user, 2:user2})
        inst = self._makeOne(context, request)
        resp = inst()
        self.assertEqual(resp['parent_acl'], [(None, _JOHN, (None,))])
        self.assertEqual(resp['users'], [(1, _JOHN)])
        self.assertEqual(resp['groups'], [('system.Everyone',
                                          'system.Everyone'),
                                          ('system.Authenticated',
                                          'system.Authenticated')])
        self.assertEqual(resp['local_acl'], [(None, _MARY, (None,))])
        self.assertEqual(resp['permissions'], ['-- ALL --'])
        self.assertEqual(resp['inheriting'], 'enabled')
        self.assertEqual(request.sdiapi.flashed, 'ACE removed')

class TestAdd(unittest.TestCase):
    def setUp(self):
        self.config = testing.setUp()

    def tearDown(self):
        testing.tearDown()

    def _makeOne(self, context, request):
        from ..acl import ACLEditViews
        return ACLEditViews(context, request).add

    def test_add(self):
        from ....testing import make_site
        request = testing.DummyRequest()
        request.sdiapi = DummySDIAPI()
        request.POST = DummyPost(getall_result=('test',))
        token = request.session.get_csrf_token()
        request.params['csrf_token'] = token
        request.POST['verb'] = 'allow'
        request.POST['principal'] = '1'
        request.POST['permissions'] = 'test'
        site = make_site()
        site['page'] = context = testing.DummyResource()
        site.__acl__ = [(None, 1, (None,))]
        context.__acl__ = [(None, 1, (None,)),
                           (None, 2, (None,))]
        context.__oid__ = 5
        user = DummyUser(1, _JOHN)
        user2 = DummyUser(2, _MARY)
        site['principals']['users']['john'] = user
        site.__objectmap__ = DummyObjectMap({1:user, 2:user2})
        inst = self._makeOne(context, request)
        resp = inst()
        self.assertEqual(resp['parent_acl'], [(None, _JOHN, (None,))])
        self.assertEqual(resp['users'], [(1, _JOHN)])
        self.assertEqual(resp['groups'], [('system.Everyone',
                                          'system.Everyone'),
                                          ('system.Authenticated',
                                          'system.Authenticated')])
        self.assertEqual(resp['local_acl'], [(None, _JOHN, (None,)),
                                             (None, _MARY, (None,)),
                                             ('allow', _JOHN, ('test',))])
        self.assertEqual(resp['permissions'], ['-- ALL --'])
        self.assertEqual(resp['inheriting'], 'enabled')
        self.assertEqual(request.sdiapi.flashed, 'New ACE added')

    def test_add_no_principal_selected(self):
        from ....testing import make_site
        request = testing.DummyRequest()
        request.sdiapi = DummySDIAPI()
        request.POST = DummyPost(getall_result=('test',))
        token = request.session.get_csrf_token()
        request.params['csrf_token'] = token
        request.POST['verb'] = 'allow'
        request.POST['principal'] = ''
        request.POST['permissions'] = 'test'
        site = make_site()
        site['page'] = context = testing.DummyResource()
        site.__acl__ = [(None, 1, (None,))]
        context.__acl__ = [(None, 1, (None,)),
                           (None, 2, (None,))]
        context.__oid__ = 5
        user = DummyUser(1, _JOHN)
        user2 = DummyUser(2, _MARY)
        site['principals']['users']['john'] = user
        site.__objectmap__ = DummyObjectMap({1:user, 2:user2})
        inst = self._makeOne(context, request)
        resp = inst()
        self.assertEqual(resp['parent_acl'], [(None, _JOHN, (None,))])
        self.assertEqual(resp['users'], [(1, _JOHN)])
        self.assertEqual(resp['groups'], [('system.Everyone',
                                          'system.Everyone'),
                                          ('system.Authenticated',
                                          'system.Authenticated')])
        self.assertEqual(resp['local_acl'], [(None, _JOHN, (None,)),
                                             (None, _MARY, (None,))])
        self.assertEqual(resp['permissions'], ['-- ALL --'])
        self.assertEqual(resp['inheriting'], 'enabled')
        self.assertEqual(request.session['_f_error'],
                         ['No principal selected'])

    def test_add_unknown_user(self):
        from ....testing import make_site
        request = testing.DummyRequest()
        request.sdiapi = DummySDIAPI()
        request.POST = DummyPost(getall_result=('test',))
        token = request.session.get_csrf_token()
        request.params['csrf_token'] = token
        request.POST['verb'] = 'allow'
        request.POST['principal'] = '3'
        request.POST['permissions'] = 'test'
        site = make_site()
        site['page'] = context = testing.DummyResource()
        site.__acl__ = [(None, 1, (None,))]
        context.__acl__ = [(None, 1, (None,)),
                           (None, 2, (None,))]
        context.__oid__ = 5
        user = DummyUser(1, _JOHN)
        user2 = DummyUser(2, _MARY)
        site['principals']['users']['john'] = user
        site.__objectmap__ = DummyObjectMap({1:user, 2:user2})
        inst = self._makeOne(context, request)
        resp = inst()
        self.assertEqual(resp['parent_acl'], [(None, _JOHN, (None,))])
        self.assertEqual(resp['users'], [(1, _JOHN)])
        self.assertEqual(resp['groups'], [('system.Everyone',
                                          'system.Everyone'),
                                          ('system.Authenticated',
                                          'system.Authenticated')])
        self.assertEqual(resp['local_acl'], [(None, _JOHN, (None,)),
                                             (None, _MARY, (None,))])
        self.assertEqual(resp['permissions'], ['-- ALL --'])
        self.assertEqual(resp['inheriting'], 'enabled')
        self.assertEqual(request.session['_f_error'],
                         ['Unknown user or group when adding ACE'])

    def test_add_no_permission(self):
        from ....testing import make_site
        request = testing.DummyRequest()
        request.sdiapi = DummySDIAPI()
        request.POST = DummyPost(getall_result=None)
        token = request.session.get_csrf_token()
        request.params['csrf_token'] = token
        request.POST['verb'] = 'allow'
        request.POST['principal'] = '1'
        request.POST['permissions'] = 'test'
        site = make_site()
        context = site['page'] = testing.DummyResource()
        site.__acl__ = [(None, 1, (None,))]
        context.__acl__ = [(None, 1, (None,)),
                           (None, 2, (None,))]
        context.__oid__ = 5
        user = DummyUser(1, _JOHN)
        site['principals']['users']['john'] = user
        site.__objectmap__ = DummyObjectMap({1:user})
        inst = self._makeOne(context, request)
        resp = inst()
        self.assertEqual(context.__acl__[-1], ('allow', 1, ()))
        self.assertEqual(resp['inheriting'], 'enabled')
        self.assertEqual(request.sdiapi.flashed, 'New ACE added')

    def test_add_all_permissions(self):
        from pyramid.security import ALL_PERMISSIONS
        from ....testing import make_site
        request = testing.DummyRequest()
        request.sdiapi = DummySDIAPI()
        request.POST = DummyPost(getall_result=('-- ALL --,'))
        token = request.session.get_csrf_token()
        request.params['csrf_token'] = token
        request.POST['verb'] = 'allow'
        request.POST['principal'] = '1'
        request.POST['permissions'] = 'test'
        site = make_site()
        context = site['page'] = testing.DummyResource()
        site.__acl__ = [(None, 1, (None,))]
        context.__acl__ = [(None, 1, (None,)),
                           (None, 2, (None,))]
        context.__oid__ = 5
        user = DummyUser(1, _JOHN)
        site['principals']['users']['john'] = user
        site.__objectmap__ = DummyObjectMap({1:user})
        inst = self._makeOne(context, request)
        resp = inst()
        self.assertEqual(context.__acl__[-1], ('allow', 1, ALL_PERMISSIONS))
        self.assertEqual(resp['inheriting'], 'enabled')
        self.assertEqual(request.sdiapi.flashed, 'New ACE added')

    def test_add_Everyone(self):
        from pyramid.security import Everyone
        from ....testing import make_site
        request = testing.DummyRequest()
        request.sdiapi = DummySDIAPI()
        request.POST = DummyPost(getall_result=('view'))
        token = request.session.get_csrf_token()
        request.params['csrf_token'] = token
        request.POST['verb'] = 'allow'
        request.POST['principal'] = Everyone
        request.POST['permissions'] = 'test'
        site = make_site()
        context = site['pagge'] = testing.DummyResource()
        context.__oid__ = 5
        context.__acl__ = []
        context.__objectmap__ = DummyObjectMap({})
        inst = self._makeOne(context, request)
        resp = inst()
        self.assertEqual(context.__acl__[-1], ('allow', Everyone, 'view'))
        self.assertEqual(resp['inheriting'], 'enabled')
        self.assertEqual(request.sdiapi.flashed, 'New ACE added')

class TestInherit(unittest.TestCase):
    def setUp(self):
        self.config = testing.setUp()

    def tearDown(self):
        testing.tearDown()

    def _makeOne(self, context, request):
        from ..acl import ACLEditViews
        return ACLEditViews(context, request).inherit

    def test_inherit_enabled(self):
        from ....testing import make_site
        request = testing.DummyRequest()
        request.sdiapi = DummySDIAPI()
        token = request.session.new_csrf_token()
        request.POST['csrf_token'] = token
        request.POST['inherit'] = 'enabled'
        site = make_site()
        site['page'] = context = testing.DummyResource()
        site.__acl__ = [(None, 1, (None,))]
        context.__acl__ = [(None, 1, (None,)),
                           (None, 2, (None,))]
        context.__oid__ = 5
        user = DummyUser(1, _JOHN)
        user2 = DummyUser(2, _MARY)
        site['principals']['users']['john'] = user
        site.__objectmap__ = DummyObjectMap({1:user, 2:user2})
        inst = self._makeOne(context, request)
        resp = inst()
        self.assertEqual(resp['parent_acl'], [(None, _JOHN, (None,))])
        self.assertEqual(resp['users'], [(1, _JOHN)])
        self.assertEqual(resp['groups'], [('system.Everyone',
                                          'system.Everyone'),
                                          ('system.Authenticated',
                                          'system.Authenticated')])
        self.assertEqual(resp['local_acl'], [(None, _JOHN, (None,)),
                                             (None, _MARY, (None,))])
        self.assertEqual(resp['permissions'], ['-- ALL --'])
        self.assertEqual(resp['inheriting'], 'enabled')
        self.assertEqual(request.sdiapi.flashed,
                         'ACL will inherit from parent')

    def test_inherit_disabled(self):
        from ....testing import make_site
        request = testing.DummyRequest()
        request.sdiapi = DummySDIAPI()
        token = request.session.new_csrf_token()
        request.POST['csrf_token'] = token
        request.POST['inherit'] = 'disabled'
        site = make_site()
        site['page'] = context = testing.DummyResource()
        site.__acl__ = [(None, 1, (None,))]
        context.__acl__ = [(None, 1, (None,)),
                           (None, 2, (None,))]
        context.__oid__ = 5
        user = DummyUser(1, _JOHN)
        user2 = DummyUser(2, _MARY)
        site['principals']['users']['john'] = user
        site.__objectmap__ = DummyObjectMap({1:user, 2:user2})
        inst = self._makeOne(context, request)
        resp = inst()
        self.assertEqual(resp['parent_acl'], [(None, _JOHN, (None,))])
        self.assertEqual(resp['users'], [(1, _JOHN)])
        self.assertEqual(resp['groups'], [('system.Everyone',
                                          'system.Everyone'),
                                          ('system.Authenticated',
                                          'system.Authenticated')])
        self.assertEqual(resp['local_acl'], [(None, _JOHN, (None,)),
                                             (None, _MARY, (None,))])
        self.assertEqual(resp['permissions'], ['-- ALL --'])
        self.assertEqual(resp['inheriting'], 'disabled')
        self.assertEqual(request.sdiapi.flashed,
                         'ACL will *not* inherit from parent')

class TestOther(unittest.TestCase):
    def setUp(self):
        self.config = testing.setUp()

    def tearDown(self):
        testing.tearDown()

    def _makeOne(self, context, request):
        from ..acl import ACLEditViews
        return ACLEditViews(context, request)

    def _makeSite(self):
        from ....testing import make_site
        site = make_site()
        context = testing.DummyResource()
        context.__oid__ = 5
        site['context'] = context
        return site

    def test_finish_acl_edit_with_registered_permissions(self):
        from pyramid.security import NO_PERMISSION_REQUIRED
        request = testing.DummyRequest()
        site = self._makeSite()
        context = site['context']
        context.__acl__ = []
        context.__objectmap__ = DummyObjectMap({})
        inst = self._makeOne(context, request)
        inst.get_all_permissions = lambda *arg: [NO_PERMISSION_REQUIRED,'view']
        result = inst.finish_acl_edit()
        self.assertEqual(result['permissions'], ['-- ALL --', 'view'])

    def test_get_local_acl_with_no_inherit(self):
        request = testing.DummyRequest()
        site = self._makeSite()
        context = site['context']
        from ..acl import NO_INHERIT
        context.__acl__ = [NO_INHERIT]
        inst = self._makeOne(context, request)
        result = inst.get_local_acl()
        self.assertEqual(result, ('disabled', []))

    def test_get_local_acl_with_all_permissions(self):
        from pyramid.security import ALL_PERMISSIONS, Allow
        request = testing.DummyRequest()
        site = self._makeSite()
        user = testing.DummyResource()
        user.__name__ = 'fred'
        site.__objectmap__ = DummyObjectMap({1:user})
        context = site['context']
        context.__acl__ = [ (Allow, 1, ALL_PERMISSIONS),
                            (Allow, 1, 'view') ]
        inst = self._makeOne(context, request)
        result = inst.get_local_acl()
        self.assertEqual(
            result,
            ('enabled',
             [('Allow', 'fred', ('-- ALL --',)),
              ('Allow', 'fred', ('view',)),
             ])
            )

    def test_get_parent_acl_with_no_inherit(self):
        from ..acl import NO_INHERIT
        request = testing.DummyRequest()
        context = testing.DummyResource()
        context.__acl__ = [ NO_INHERIT ]
        context.__parent__ = None
        inst = self._makeOne(context, request)
        result = inst.get_parent_acl(context)
        self.assertEqual(result, [])

    def test_get_parent_acl_with_noniter_permission(self):
        from pyramid.security import Allow
        request = testing.DummyRequest()
        context = testing.DummyResource()
        context.__acl__ = [(Allow, 1, 'edit')]
        context.__parent__ = None
        inst = self._makeOne(context, request)
        user = testing.DummyResource()
        user.__name__ = 'fred'
        context.__objectmap__ = DummyObjectMap({1:user})
        result = inst.get_parent_acl(context)
        self.assertEqual(result, [(Allow, 'fred', ('edit',))])

    def test_get_parent_acl_with_all_permissions(self):
        from pyramid.security import Allow, ALL_PERMISSIONS
        request = testing.DummyRequest()
        context = testing.DummyResource()
        context.__acl__ = [ (Allow, 1, ALL_PERMISSIONS) ]
        context.__parent__ = None
        inst = self._makeOne(context, request)
        user = testing.DummyResource()
        user.__name__ = 'fred'
        context.__objectmap__ = DummyObjectMap({1:user})
        result = inst.get_parent_acl(context)
        self.assertEqual(result, [(Allow, 'fred', ('-- ALL --',))])

    def test_get_principal_name_deleted_principal(self):
        request = testing.DummyRequest()
        context = testing.DummyResource()
        context.__parent__ = None
        inst = self._makeOne(context, request)
        context.__objectmap__ = DummyObjectMap({1:None})
        result = inst.get_principal_name(1)
        self.assertEqual(result, '<deleted principal>')

    def test_get_principal_name_Everyone(self):
        from pyramid.security import Everyone
        request = testing.DummyRequest()
        context = testing.DummyResource()
        context.__parent__ = None
        inst = self._makeOne(context, request)
        context.__objectmap__ = DummyObjectMap({1:Everyone})
        result = inst.get_principal_name(Everyone)
        self.assertEqual(result, Everyone)

class DummyUser(object):
    def __init__(self, oid, name):
        self.__oid__ = oid
        self.__name__ = name

class DummyPost(dict):
    def __init__(self, getall_result=(), get_result=None):
        self.getall_result = getall_result
        self.get_result = get_result

    def getall(self, name): # pragma: no cover
        return self.getall_result

    def get(self, name, default=None): # pragma: no cover
        if self.get_result is None: 
            return default
        return self.get_result

class DummyObjectMap(object):
    def __init__(self, objectmap):
        self.objectmap = objectmap
    def object_for(self, oid):
        return self.objectmap.get(oid, None)
    def pathcount(self, context):
        return 0

class DummySDIAPI(object):
    def flash_with_undo(self, message):
        self.flashed = (message)

