import unittest

from pyramid import testing

class Test_delete_locks_for_resource(unittest.TestCase):
    def _callFUT(self, event):
        from ..subscribers import delete_locks_for_resource
        return delete_locks_for_resource(event)

    def test_event_moving(self):
        event = testing.DummyResource()
        event.loading = False
        event.moving = True
        result = self._callFUT(event)
        self.assertEqual(result, None)

    def test_event_loading(self):
        event = testing.DummyResource()
        event.loading = True
        event.moving = None
        result = self._callFUT(event)
        self.assertEqual(result, None)
        
    def test_objectmap_is_None(self):
        event = testing.DummyResource()
        event.moving = None
        event.loading = False
        event.object = None
        event.parent = testing.DummyResource()
        result = self._callFUT(event)
        self.assertEqual(result, None)

    def test_it(self):
        event = testing.DummyResource()
        event.moving = None
        event.loading = False
        resource = testing.DummyResource()
        parent = testing.DummyResource()
        event.object = resource
        event.removed_oids = [1, 2]
        event.parent = parent
        lock = testing.DummyResource()
        lock.suicided = 0
        def commit_suicide():
            lock.suicided+=1
        lock.commit_suicide = commit_suicide
        parent.__objectmap__ = DummyObjectMap([lock])
        result = self._callFUT(event)
        self.assertEqual(result, None)
        self.assertEqual(lock.suicided, 2)

class Test_delete_locks_for_user(unittest.TestCase):
    def _callFUT(self, event):
        from ..subscribers import delete_locks_for_user
        return delete_locks_for_user(event)
    
    def test_event_moving(self):
        event = testing.DummyResource()
        event.loading = False
        event.moving = True
        result = self._callFUT(event)
        self.assertEqual(result, None)

    def test_event_loading(self):
        event = testing.DummyResource()
        event.loading = True
        event.moving = None
        result = self._callFUT(event)
        self.assertEqual(result, None)
        
    def test_objectmap_is_None(self):
        event = testing.DummyResource()
        event.moving = None
        event.loading = False
        event.object = None
        event.parent = testing.DummyResource()
        result = self._callFUT(event)
        self.assertEqual(result, None)

    def test_it(self):
        from zope.interface import alsoProvides
        from substanced.interfaces import IUser
        event = testing.DummyResource()
        event.moving = None
        event.loading = False
        resource = testing.DummyResource()
        parent = testing.DummyResource()
        alsoProvides(resource, IUser)
        event.object = resource
        event.parent = parent
        lock = testing.DummyResource()
        lock.suicided = 0
        def commit_suicide():
            lock.suicided+=1
        lock.commit_suicide = commit_suicide
        parent.__objectmap__ = DummyObjectMap([lock])
        result = self._callFUT(event)
        self.assertEqual(result, None)
        self.assertEqual(lock.suicided, 1)
    
        
class DummyObjectMap(object):
    def __init__(self, result):
        self.result = result
    def targets(self, resource, type):
        return self.result

