import json
import unittest
from pyramid import testing
import mock

class Test_acl_modified(unittest.TestCase):
    def setUp(self):
        self.request = testing.DummyRequest()
        self.config = testing.setUp(request=self.request)

    def tearDown(self):
        testing.tearDown()
        
    def _callFUT(self, event):
        from ..subscribers import acl_modified
        return acl_modified(event)

    @mock.patch('substanced.audit.subscribers.get_auditlog')
    def test_it(self, mock_get_auditlog):
        from substanced.audit import AuditLog
        self.request.user = Dummy({'__oid__':1, '__name__':'fred'})
        event = Dummy()
        context = testing.DummyResource()
        auditlog = AuditLog()
        mock_get_auditlog.side_effect = lambda c: auditlog
        context.__oid__ = 5
        event.registry = _makeRegistry()
        event.object = context
        event.old_acl = 'old_acl'
        event.new_acl = 'new_acl'
        self._callFUT(event)
        self.assertEqual(len(auditlog), 1)
        entries = list(auditlog.entries)
        entry = entries[0]
        self.assertEqual(entry[0], 0)
        self.assertEqual(entry[1], 0)
        self.assertEqual(entry[2].name, 'ACLModified')
        self.assertEqual(entry[2].oid, 5)
        self.assertEqual(
            json.loads(entry[2].payload),
            {
                'time':entry[2].timestamp,
                'old_acl': 'old_acl',
                'new_acl': 'new_acl',
                'userinfo':{'oid':1, 'name':'fred'},
                'object_path':'/',
                'content_type':'SteamingPile'
             }

            )

    @mock.patch('substanced.audit.subscribers.get_auditlog')
    def test_it_nolog(self, mock_get_auditlog):
        mock_get_auditlog.side_effect = lambda c: None
        event = Dummy()
        context = testing.DummyResource()
        context.__oid__ = 5
        event.object = context
        self.assertEqual(self._callFUT(event), None)

_marker = object()

class Test_content_added_moved_or_duplicated(unittest.TestCase):
    def setUp(self):
        self.request = testing.DummyRequest()
        self.config = testing.setUp(request=self.request)

    def tearDown(self):
        testing.tearDown()
        
    def _callFUT(self, event):
        from ..subscribers import content_added_moved_or_duplicated
        return content_added_moved_or_duplicated(event)

    @mock.patch('substanced.audit.subscribers.get_auditlog')
    def test_it_added(self, mock_get_auditlog):
        auditlog = _makeAuditLog()
        mock_get_auditlog.side_effect = lambda c: auditlog
        self.request.user = Dummy({'__oid__':1, '__name__':'fred'})
        event = _makeEvent()
        self._callFUT(event)
        self.assertEqual(len(auditlog), 1)
        entries = list(auditlog.entries)
        entry = entries[0]
        self.assertEqual(entry[0], 0)
        self.assertEqual(entry[1], 0)
        self.assertEqual(entry[2].name, 'ContentAdded')
        self.assertEqual(entry[2].oid, 10)
        self.assertEqual(
            json.loads(entry[2].payload),
            {
                'folder_path': '/',
                'folder_oid': 10,
                'object_name': 'objectname',
                'userinfo': {'oid': 1, 'name': 'fred'},
                'content_type': 'SteamingPile',
                'time': entry[2].timestamp,
                'object_oid': 5

                }
            )

    @mock.patch('substanced.audit.subscribers.get_auditlog')
    def test_it_added_noscribe(self, mock_get_auditlog):
        mock_get_auditlog.side_effect = lambda c: None
        event = _makeEvent()
        self._callFUT(event) # does not throw an exception
        
    @mock.patch('substanced.audit.subscribers.get_auditlog')
    def test_it_moved(self, mock_get_auditlog):
        auditlog = _makeAuditLog()
        mock_get_auditlog.side_effect = lambda c: auditlog
        self.request.user = Dummy({'__oid__':1, '__name__':'fred'})
        event = _makeEvent()
        event.moving = True
        event.duplicating = None
        self._callFUT(event)
        self.assertEqual(len(auditlog), 1)
        entries = list(auditlog.entries)
        entry = entries[0]
        self.assertEqual(entry[0], 0)
        self.assertEqual(entry[1], 0)
        self.assertEqual(entry[2].name, 'ContentMoved')
        self.assertEqual(entry[2].oid, 10)
        self.assertEqual(
            json.loads(entry[2].payload),
            {
                'folder_path': '/',
                'folder_oid': 10,
                'object_name': 'objectname',
                'userinfo': {'oid': 1, 'name': 'fred'},
                'content_type': 'SteamingPile',
                'time': entry[2].timestamp,
                'object_oid': 5

                }
            )

    @mock.patch('substanced.audit.subscribers.get_auditlog')
    def test_it_duplicated(self, mock_get_auditlog):
        auditlog = _makeAuditLog()
        mock_get_auditlog.side_effect = lambda c: auditlog
        self.request.user = Dummy({'__oid__':1, '__name__':'fred'})
        event = _makeEvent()
        event.moving = None
        event.duplicating = True
        self._callFUT(event)
        self.assertEqual(len(auditlog), 1)
        entries = list(auditlog.entries)
        entry = entries[0]
        self.assertEqual(entry[0], 0)
        self.assertEqual(entry[1], 0)
        self.assertEqual(entry[2].name, 'ContentDuplicated')
        self.assertEqual(entry[2].oid, 10)
        self.assertEqual(
            json.loads(entry[2].payload),
            {
                'folder_path': '/',
                'folder_oid': 10,
                'object_name': 'objectname',
                'userinfo': {'oid': 1, 'name': 'fred'},
                'content_type': 'SteamingPile',
                'time': entry[2].timestamp,
                'object_oid': 5

                }
            )
        
class Test_content_removed(unittest.TestCase):
    def setUp(self):
        self.request = testing.DummyRequest()
        self.config = testing.setUp(request=self.request)

    def tearDown(self):
        testing.tearDown()
        
    def _callFUT(self, event):
        from ..subscribers import content_removed
        return content_removed(event)
    
    def test_it_moving(self):
        event = Dummy()
        event.moving = True
        self.assertEqual(self._callFUT(event), None)

    @mock.patch('substanced.audit.subscribers.get_auditlog')
    def test_it(self, mock_get_auditlog):
        auditlog = _makeAuditLog()
        mock_get_auditlog.side_effect = lambda c: auditlog
        self.request.user = Dummy({'__oid__':1, '__name__':'fred'})
        event = _makeEvent()
        event.moving = None
        event.duplicating = None
        self._callFUT(event)
        self.assertEqual(len(auditlog), 1)
        entries = list(auditlog.entries)
        entry = entries[0]
        self.assertEqual(entry[0], 0)
        self.assertEqual(entry[1], 0)
        self.assertEqual(entry[2].name, 'ContentRemoved')
        self.assertEqual(entry[2].oid, 10)
        self.assertEqual(
            json.loads(entry[2].payload),
            {
                'folder_path': '/',
                'folder_oid': 10,
                'object_name': 'objectname',
                'userinfo': {'oid': 1, 'name': 'fred'},
                'content_type': 'SteamingPile',
                'time': entry[2].timestamp,
                'object_oid': 5

                }
            )

    
        
class Test_content_modified(unittest.TestCase):
    def setUp(self):
        self.request = testing.DummyRequest()
        self.config = testing.setUp(request=self.request)

    def tearDown(self):
        testing.tearDown()
        
    def _callFUT(self, event):
        from ..subscribers import content_modified
        return content_modified(event)

    @mock.patch('substanced.audit.subscribers.get_auditlog')
    def test_it_noscribe(self, mock_get_auditlog):
        mock_get_auditlog.side_effect = lambda c: None
        event = Dummy()
        context = testing.DummyResource()
        event.object = context
        self.assertEqual(self._callFUT(event), None)
        
    @mock.patch('substanced.audit.subscribers.get_auditlog')
    def test_it(self, mock_get_auditlog):
        auditlog = _makeAuditLog()
        mock_get_auditlog.side_effect = lambda c: auditlog
        self.request.user = Dummy({'__oid__':1, '__name__':'fred'})
        event = Dummy()
        context = testing.DummyResource()
        context.__oid__ = 5
        event.registry = _makeRegistry()
        event.object = context
        self._callFUT(event)
        self.assertEqual(len(auditlog), 1)
        entries = list(auditlog.entries)
        entry = entries[0]
        self.assertEqual(entry[0], 0)
        self.assertEqual(entry[1], 0)
        self.assertEqual(entry[2].name, 'ContentModified')
        self.assertEqual(entry[2].oid, 5)
        self.assertEqual(
            json.loads(entry[2].payload),
            {
                'object_oid': 5,
                'userinfo': {'oid': 1, 'name': 'fred'},
                'content_type': 'SteamingPile',
                'object_path': '/',
                'time': entry[2].timestamp,
                },
            )

class Test_logged_in(unittest.TestCase):
    def setUp(self):
        self.request = testing.DummyRequest()
        self.config = testing.setUp(request=self.request)

    def tearDown(self):
        testing.tearDown()
        
    def _callFUT(self, event):
        from ..subscribers import logged_in
        return logged_in(event)

    @mock.patch('substanced.audit.subscribers.get_auditlog')
    def test_it_noscribe(self, mock_get_auditlog):
        mock_get_auditlog.side_effect = lambda c: None
        event = Dummy()
        event.request = Dummy()
        context = testing.DummyResource()
        event.request.context = context
        self.assertEqual(self._callFUT(event), None)

    @mock.patch('substanced.audit.subscribers.get_auditlog')
    def test_it_user_has_oid(self, mock_get_auditlog):
        auditlog = _makeAuditLog()
        mock_get_auditlog.side_effect = lambda c: auditlog
        event = Dummy()
        event.request = Dummy()
        context = testing.DummyResource()
        event.request.context = context
        user = Dummy()
        user.__oid__ = 5
        event.user = user
        event.login = 'login'
        self._callFUT(event)
        self.assertEqual(len(auditlog), 1)
        entries = list(auditlog.entries)
        entry = entries[0]
        self.assertEqual(entry[0], 0)
        self.assertEqual(entry[1], 0)
        self.assertEqual(entry[2].name, 'LoggedIn')
        self.assertEqual(entry[2].oid, None)
        self.assertEqual(
            json.loads(entry[2].payload),
            {
                'user_oid': 5,
                'login': 'login',
                'time': entry[2].timestamp,
                },
            )

    @mock.patch('substanced.audit.subscribers.get_auditlog')
    def test_it_user_has_no_oid(self, mock_get_auditlog):
        auditlog = _makeAuditLog()
        mock_get_auditlog.side_effect = lambda c: auditlog
        event = Dummy()
        event.request = Dummy()
        context = testing.DummyResource()
        event.request.context = context
        user = Dummy()
        event.user = user
        event.login = 'login'
        self._callFUT(event)
        self.assertEqual(len(auditlog), 1)
        entries = list(auditlog.entries)
        entry = entries[0]
        self.assertEqual(entry[0], 0)
        self.assertEqual(entry[1], 0)
        self.assertEqual(entry[2].name, 'LoggedIn')
        self.assertEqual(entry[2].oid, None)
        self.assertEqual(
            json.loads(entry[2].payload),
            {
                'user_oid': None,
                'login': 'login',
                'time': entry[2].timestamp,
                },
            )

class Test_root_added(unittest.TestCase):
    def _callFUT(self, event):
        from ..subscribers import root_added
        return root_added(event)

    @mock.patch('substanced.audit.subscribers.set_auditlog')
    def test_it(self, mock_set_auditlog):
        event = Dummy()
        root = Dummy()
        def is_set(_root):
            self.assertEqual(_root,  root)
        mock_set_auditlog.side_effect = is_set
        event.object = root
        self._callFUT(event)
        
class Dummy(object):
    def __init__(self, kw=None):
        if kw:
            self.__dict__.update(kw)

class DummyContentRegistry(object):
    def typeof(self, content):
        return 'SteamingPile'
    
def _makeAuditLog():
    from substanced.audit import AuditLog
    auditlog = AuditLog()
    return auditlog

def _makeRegistry():
    registry = Dummy()
    registry.content = DummyContentRegistry()
    return registry

def _makeEvent():
    event = Dummy()
    event.moving = None
    event.duplicating = None
    event.parent = testing.DummyResource()
    event.parent.__oid__ = 10
    event.name = 'objectname'
    context = testing.DummyResource()
    context.__oid__ = 5
    context.__parent__ = event.parent
    event.registry = _makeRegistry()
    event.object = context
    event.old_acl = 'old_acl'
    event.new_acl = 'new_acl'
    return event

