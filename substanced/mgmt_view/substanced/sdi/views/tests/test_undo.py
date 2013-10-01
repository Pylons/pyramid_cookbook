import unittest
from pyramid import testing

class TestUndoViews(unittest.TestCase):
    def _makeOne(self, context, request):
        from ..undo import UndoViews
        return UndoViews(context, request)

    def test_undo_recent_no_referrer(self):
        conn = DummyConnection()
        request = testing.DummyRequest()
        request._primary_zodb_conn = conn # XXX not an API, will break
        request.sdiapi = DummySDIAPI()
        request.referrer = None
        request.params['undohash'] = 'undohash'
        context = testing.DummyResource()
        inst = self._makeOne(context, request)
        resp = inst.undo_recent()
        self.assertEqual(resp.location, '/mgmt_path')
        
    def test_undo_recent_with_referrer(self):
        conn = DummyConnection()
        request = testing.DummyRequest()
        request._primary_zodb_conn = conn # XXX not an API, will break
        request.sdiapi = DummySDIAPI()
        request.referrer = 'loc'
        request.params['undohash'] = 'undohash'
        context = testing.DummyResource()
        inst = self._makeOne(context, request)
        resp = inst.undo_recent()
        self.assertEqual(resp.location, 'loc')

    def test_undo_recent_no_undo_info(self):
        conn = DummyConnection()
        request = testing.DummyRequest()
        request._primary_zodb_conn = conn # XXX not an API, will break
        request.sdiapi = DummySDIAPI()
        request.referrer = 'loc'
        request.params['undohash'] = 'undohash'
        context = testing.DummyResource()
        inst = self._makeOne(context, request)
        inst.undo_recent()
        self.assertEqual(request.session['_f_error'], ['Could not undo, sorry'])
        
    def test_undo_recent_with_undo_info_no_match(self):
        record = {'description':'desc', 'id':'abc'}
        conn = DummyConnection(undo_info=[record])
        request = testing.DummyRequest()
        request._primary_zodb_conn = conn # XXX not an API, will break
        request.sdiapi = DummySDIAPI()
        request.referrer = 'loc'
        request.params['undohash'] = 'undohash'
        context = testing.DummyResource()
        inst = self._makeOne(context, request)
        inst.undo_recent()
        self.assertEqual(request.session['_f_error'], ['Could not undo, sorry'])

    def test_undo_recent_with_undo_info_match(self):
        record = {'undohash':'abc', 'id':'abc', 'description':'desc'}
        conn = DummyConnection(undo_info=[record])
        request = testing.DummyRequest()
        request._primary_zodb_conn = conn # XXX not an API, will break
        request.sdiapi = DummySDIAPI()
        request.referrer = 'loc'
        request.params['undohash'] = 'abc'
        context = testing.DummyResource()
        inst = self._makeOne(context, request)
        transaction = DummyTransaction()
        inst.transaction = transaction
        inst.undo_recent()
        self.assertEqual(len(request.session['_f_success']), 1)
        self.assertEqual(len(conn._db.undone), 1)
        self.assertEqual(transaction.committed, True)

    def test_undo_recent_with_undo_info_POSError(self):
        from ZODB.POSException import POSError
        record = {'undohash':'abc', 'id':'abc'}
        conn = DummyConnection(undo_info=[record], undo_exc=POSError)
        request = testing.DummyRequest()
        request._primary_zodb_conn = conn # XXX not an API, will break
        request.sdiapi = DummySDIAPI()
        request.referrer = 'loc'
        request.params['undohash'] = 'abc'
        transaction = DummyTransaction()
        context = testing.DummyResource()
        inst = self._makeOne(context, request)
        inst.transaction = transaction
        inst.undo_recent()
        self.assertEqual(len(request.session['_f_error']), 1)
        self.assertEqual(len(conn._db.undone), 0)
        self.assertEqual(transaction.aborted, True)

    def test__get_db(self):
        request = testing.DummyRequest()
        context = testing.DummyResource()
        inst = self._makeOne(context, request)
        conn = DummyConnection()
        def get_connection(req):
            self.assertEqual(req, request)
            return conn
        inst.get_connection = get_connection
        db = inst._get_db()
        self.assertEqual(db, conn._db)

    def test__undoable_transactions(self):
        import time
        request = testing.DummyRequest()
        context = testing.DummyResource()
        now = time.time()
        now_ctime = time.ctime(now)[4:][:-5]
        record1 = dict(
            time=now,
            description=b'abc',
            user_name=b'1',
            id=b'0',
            )
        record2 = dict(
            time=now,
            description=b'abc',
            user_name=b'cantintify',
            id=b'1',
            )
        record3 = dict(
            time=now,
            description=b'',
            user_name=b'cantintify',
            id=b'1',
            )
        record4 = dict(
            time=now,
            description=b'a'*81,
            user_name=b'1',
            id=b'1',
            )
        records = [record1, record2, record3, record4]
        db = DummyDB(True, records)
        def _get_db():
            return db
        inst = self._makeOne(context, request)
        inst._get_db = _get_db
        user = testing.DummyResource(__name__='fred')
        objectmap = DummyObjectmap(user)
        def find_objectmap(ctx):
            self.assertEqual(ctx, context)
            return objectmap
        inst.find_objectmap = find_objectmap
        result = inst._undoable_transactions(0, 10)
        self.assertEqual(db.first, 0)
        self.assertEqual(db.last, 10)
        self.assertEqual(
            result,
            [
                {'description': b'abc',
                 'user_name': b'fred',
                 'id': b'MA==\n abc',
                 'time': now_ctime},
                {'description': b'abc',
                 'user_name': b'cantintify',
                 'id': b'MQ==\n abc',
                 'time': now_ctime},
                {'description': b'',
                 'user_name': b'cantintify',
                 'id': b'MQ==\n ',
                 'time': now_ctime},
                {'description': (b'a'*81),
                 'user_name': b'fred',
                 'id': b'MQ==\n ' + (b'a' * 76) + b' ...',
                 'time': now_ctime}
                ]
            )

    def test_undo_multiple(self):
        import binascii
        request = testing.DummyRequest()
        context = testing.DummyResource()
        inst = self._makeOne(context, request)
        conn = DummyConnection()
        def get_connection(req):
            self.assertEqual(req, request)
            return conn
        inst.get_connection = get_connection
        def authenticated_userid(req):
            self.assertEqual(req, request)
            return 1
        post = testing.DummyResource()
        enca = binascii.b2a_base64(b'a')
        encb = binascii.b2a_base64(b'b')
        info = [enca + b' b', encb + b' f']
        def getall(n):
            self.assertEqual(n, 'transaction')
            return info
        post.getall = getall
        request.POST = post
        request.sdiapi = DummySDIAPI()
        inst.authenticated_userid = authenticated_userid
        txn = DummyTransaction()
        inst.transaction = txn
        result = inst.undo_multiple()
        self.assertEqual(result.location, '/mgmt_path')
        self.assertEqual(conn._db.tids, [b'a', b'b'])
        self.assertTrue(txn.committed)
        self.assertEqual(txn.user, 1)

    def test_undo_multiple_with_exception(self):
        import binascii
        from ZODB.POSException import POSError
        request = testing.DummyRequest()
        context = testing.DummyResource()
        inst = self._makeOne(context, request)
        conn = DummyConnection()
        def get_connection(req):
            self.assertEqual(req, request)
            return conn
        conn._db.undo_exc = POSError
        inst.get_connection = get_connection
        def authenticated_userid(req):
            self.assertEqual(req, request)
            return 1
        post = testing.DummyResource()
        enca = binascii.b2a_base64(b'a')
        encb = binascii.b2a_base64(b'b')
        info = [enca + b' b', encb + b' f']
        def getall(n):
            self.assertEqual(n, 'transaction')
            return info
        post.getall = getall
        request.POST = post
        request.sdiapi = DummySDIAPI()
        inst.authenticated_userid = authenticated_userid
        txn = DummyTransaction()
        inst.transaction = txn
        result = inst.undo_multiple()
        self.assertEqual(result.location, '/mgmt_path')
        self.assertTrue(txn.aborted)
        self.assertEqual(
            request.session,
            {'_f_error': ['Could not undo, sorry']}
            )

    def test_undo_no_transactions(self):
        request = testing.DummyRequest()
        request.sdiapi = DummySDIAPI()
        context = testing.DummyResource()
        inst = self._makeOne(context, request)
        def _undoable_transactions(first, last):
            return []
        inst._undoable_transactions = _undoable_transactions
        result = inst.undo()
        self.assertEqual(
            result,
            {'batch_num': 0, 'earlier': None, 'batch': [], 'later': None}
            )

    def test_undo_some_transactions_first(self):
        request = testing.DummyRequest()
        request.sdiapi = DummySDIAPI()
        context = testing.DummyResource()
        inst = self._makeOne(context, request)
        def _undoable_transactions(first, last):
            return [None] * 10
        inst._undoable_transactions = _undoable_transactions
        result = inst.undo()
        self.assertEqual(
            result,
            {'batch_num': 0,
             'earlier': '/mgmt_path',
             'batch': [None] * 10,
             'later': None,
             }
            )

    def test_undo_some_transactions_notfirst(self):
        request = testing.DummyRequest()
        request.GET['first'] = '10'
        request.sdiapi = DummySDIAPI()
        context = testing.DummyResource()
        inst = self._makeOne(context, request)
        def _undoable_transactions(first, last):
            return [None] * 10
        inst._undoable_transactions = _undoable_transactions
        result = inst.undo()
        self.assertEqual(
            result,
            {'batch_num': 1,
             'earlier': '/mgmt_path',
             'batch': [None] * 10,
             'later': '/mgmt_path'}
            )

class Test_encode64(unittest.TestCase):
    def _callFUT(self, v):
        from ..undo import encode64
        return encode64(v)
    
    def test_it_len_lt_58(self):
        import binascii
        result = self._callFUT(b'a')
        self.assertEqual(result, binascii.b2a_base64(b'a'))
        
    def test_it_len_gt_58(self):
        import binascii
        result = self._callFUT(b'a'*80)
        self.assertEqual(result, binascii.b2a_base64(b'a'*80)[:-1])

class Test_decode64(unittest.TestCase):
    def _callFUT(self, v):
        from ..undo import decode64
        return decode64(v)
    
    def test_it_len_lt_58(self):
        import binascii
        send = binascii.b2a_base64(b'a')
        result = self._callFUT(send)
        self.assertEqual(result, b'a')
    

class DummyDB(object):
    def __init__(self, supports_undo, undo_info, undo_exc=None):
        self.supports_undo = supports_undo
        self.undo_info = undo_info
        self.undone = []
        self.undo_exc = undo_exc

    def undoLog(self, first, last):
        self.first = first
        self.last = last
        return self.undo_info

    def undo(self, id):
        if self.undo_exc:
            raise self.undo_exc
        self.undone.append(id)

    def undoMultiple(self, tids):
        if self.undo_exc:
            raise self.undo_exc
        self.tids = tids
        
class DummyConnection(object):
    def __init__(self, supports_undo=True, undo_info=(), undo_exc=None):
        self._db = DummyDB(supports_undo, undo_info, undo_exc)

    def db(self):
        return self._db

class DummySDIAPI(object):
    def mgmt_path(self, *arg, **kw):
        return '/mgmt_path'

class DummyTransaction(object):
    def commit(self):
        self.committed = True

    def abort(self):
        self.aborted = True

    def note(self, msg):
        self._note = msg

    def get(self):
        return self

    def setUser(self, user):
        self.user = user
        
class DummyObjectmap(object):
    def __init__(self, result):
        self.result = result
    def object_for(self, other):
        return self.result
