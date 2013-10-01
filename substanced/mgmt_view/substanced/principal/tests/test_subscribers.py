import unittest
from pyramid import testing

class Test_principal_added(unittest.TestCase):
    def _callFUT(self, event):
        from ..subscribers import principal_added
        return principal_added(event)

    def test_event_wo_loading_attr(self):
        event = testing.DummyResource()
        event.object = testing.DummyResource()
        self.assertRaises(AttributeError, self._callFUT, event)

    def test_event_w_loading_True(self):
        event = testing.DummyResource(loading=True)
        result = self._callFUT(event)
        self.assertEqual(result, None)

    def test_wo_principals_service(self):
        from zope.interface import directlyProvides
        from ...interfaces import IFolder
        event = testing.DummyResource(loading=False)
        root = testing.DummyResource()
        directlyProvides(root, IFolder)
        event.object = root['testing'] = testing.DummyResource()
        self.assertRaises(ValueError, self._callFUT, event)
        
    def test_user_not_in_groups(self):
        from ...testing import make_site
        from ...interfaces import IUser
        site = make_site()
        user = testing.DummyResource(__provides__=IUser)
        site['user'] = user
        event = testing.DummyResource(object=user, loading=False)
        self._callFUT(event) # doesnt blow up

    def test_user_in_groups(self):
        from ...testing import make_site
        from ...interfaces import IUser
        site = make_site()
        groups = site['principals']['groups']
        groups['user'] = testing.DummyResource()
        user = testing.DummyResource(__provides__=IUser)
        site['user'] = user
        event = testing.DummyResource(object=user, loading=False)
        self.assertRaises(ValueError, self._callFUT, event)

    def test_group_not_in_users(self):
        from ...testing import make_site
        site = make_site()
        group = testing.DummyResource()
        site['groups'] = group
        event = testing.DummyResource(object=group, loading=False)
        self._callFUT(event) # doesnt blow up

    def test_group_in_users(self):
        from ...testing import make_site
        site = make_site()
        users = site['principals']['users']
        users['group'] = testing.DummyResource()
        group = testing.DummyResource()
        site['group'] = group
        event = testing.DummyResource(object=group, loading=False)
        self.assertRaises(ValueError, self._callFUT, event)

class Test_user_will_be_removed(unittest.TestCase):
    def _callFUT(self, event):
        from ..subscribers import user_will_be_removed
        return user_will_be_removed(event)

    def test_loading(self):
        event = testing.DummyResource(loading=True, moving=None)
        result = self._callFUT(event)
        self.assertEqual(result, None)

    def test_moving(self):
        event = testing.DummyResource(loading=False, moving=True)
        result = self._callFUT(event)
        self.assertEqual(result, None)
        
    def test_it(self):
        from ...interfaces import IFolder
        parent = testing.DummyResource(__provides__=IFolder)
        user = testing.DummyResource()
        reset = testing.DummyResource()
        def commit_suicide():
            reset.committed = True
        reset.commit_suicide = commit_suicide
        objectmap = DummyObjectMap((reset,))
        parent.__objectmap__ = objectmap
        parent['user'] = user
        event = testing.DummyResource(object=user, loading=False, moving=None)
        self._callFUT(event)
        self.assertTrue(reset.committed)

    def test_it_moving(self):
        event = testing.DummyResource(object=None, loading=False)
        event.moving = True
        self.assertEqual(self._callFUT(event), None)

class Test_user_added(unittest.TestCase):
    def _callFUT(self, event):
        from ..subscribers import user_added
        return user_added(event)

    def test_loading(self):
        event = testing.DummyResource(loading=True)
        result = self._callFUT(event)
        self.assertEqual(result, None)

    def test_it_user_has_no_oid(self):
        user = testing.DummyResource()
        event = testing.DummyResource(object=user, loading=False)
        event.registry = DummyRegistry()
        self.assertRaises(AttributeError, self._callFUT, event)
        
    def test_it(self):
        from pyramid.security import Allow
        user = testing.DummyResource()
        user.__oid__ = 1
        event = testing.DummyResource(object=user, loading=False)
        event.registry = DummyRegistry()
        self._callFUT(event)
        self.assertEqual(
            user.__acl__,
            [(Allow, 1, ('sdi.view',
                         'sdi.edit-properties',
                         'sdi.change-password',
                        ))])

class Test_acl_maybe_added(unittest.TestCase):
    def _callFUT(self, event):
        from ..subscribers import acl_maybe_added
        return acl_maybe_added(event)

    def test_moving(self):
        event = DummyEvent(moving=True, loading=False)
        self.assertEqual(self._callFUT(event), False)

    def test_loading(self):
        event = DummyEvent(moving=None, loading=True)
        self.assertEqual(self._callFUT(event), False)

    def test_objectmap_is_None(self):
        event = DummyEvent(moving=None, object=None, loading=False)
        self.assertEqual(self._callFUT(event), None)

    def test_no_acls(self):
        from substanced.interfaces import IFolder
        resource1 = testing.DummyResource(__provides__=IFolder)
        resource2 = testing.DummyResource()
        resource1['resource2'] = resource2
        objectmap = DummyObjectMap()
        resource1.__objectmap__ = objectmap
        event = DummyEvent(moving=None, object=resource1, loading=False)
        self._callFUT(event)
        self.assertEqual(objectmap.connections, [])

    def test_with_acls(self):
        from ...interfaces import PrincipalToACLBearing
        from substanced.interfaces import IFolder
        resource1 = testing.DummyResource(__provides__=IFolder)
        resource2 = testing.DummyResource()
        resource1['resource2'] = resource2
        resource1.__acl__ = [(None, 'fred', None), (None, 1, None)]
        resource2.__acl__ = [(None, 'bob', None), (None, 2, None)]
        objectmap = DummyObjectMap()
        resource1.__objectmap__ = objectmap
        event = DummyEvent(moving=None, object=resource1, loading=False)
        self._callFUT(event)
        self.assertEqual(
            objectmap.connections,
            [(2, resource2, PrincipalToACLBearing),
             (1, resource1, PrincipalToACLBearing)]
            )

class Test_acl_modified(unittest.TestCase):
    def _callFUT(self, event):
        from ..subscribers import acl_modified
        return acl_modified(event)

    def test_objectmap_is_None(self):
        event = DummyEvent(object=None)
        self.assertEqual(self._callFUT(event), None)

    def test_gardenpath(self):
        from ...interfaces import PrincipalToACLBearing
        resource = testing.DummyResource()
        objectmap = DummyObjectMap()
        resource.__objectmap__ = objectmap
        event = DummyEvent(
            object=resource,
            new_acl=[(None, 'fred', None), (None, 1, None)],
            old_acl=[(None, 'bob', None), (None, 2, None)],
            )
        self._callFUT(event) 
        self.assertEqual(
            objectmap.connections,
            [(1, resource, PrincipalToACLBearing)]
            )
        self.assertEqual(
            objectmap.disconnections,
            [(2, resource, PrincipalToACLBearing)]
            )
           

class DummyObjectMap(object):
    def __init__(self, result=()):
        self.result = result
        self.connections = []
        self.disconnections = []

    def targets(self, object, reftype):
        return self.result

    def connect(self, source, target, reftype):
        self.connections.append((source, target, reftype))

    def disconnect(self, source, target, reftype):
        self.disconnections.append((source, target, reftype))
    
class DummyEvent(object):
    def __init__(self, **kw):
        self.__dict__.update(kw)
        
class DummyRegistry(object):
    def subscribers(self, *arg):
        return
    
