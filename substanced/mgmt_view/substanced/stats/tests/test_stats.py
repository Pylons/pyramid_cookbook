import unittest
from pyramid import testing

class TestStatsdHelper(unittest.TestCase):
    def setUp(self):
        self.config = testing.setUp()

    def tearDown(self):
        testing.tearDown()
        
    def _makeOne(self):
        from .. import StatsdHelper
        return StatsdHelper()

    def test_get_client_with_registry(self):
        registry = {'statsd_client':True}
        inst = self._makeOne()
        self.assertEqual(inst.get_client(registry), True)
        
    def test_get_client_with_no_registry(self):
        self.config.registry['statsd_client'] = True
        inst = self._makeOne()
        self.assertEqual(inst.get_client(), True)

    def test_timer_no_client(self):
        self.config.registry['statsd_client'] = None
        inst = self._makeOne()
        timer = inst.timer('timer')
        with timer as t:
            self.assertEqual(t, None)
        
    def test_timer_with_client(self):
        client = DummyClient(True)
        self.config.registry['statsd_client'] = client
        inst = self._makeOne()
        timer = inst.timer('timer', .5)
        self.assertEqual(timer, True)
        self.assertEqual(client.timer_name, 'timer')
        self.assertEqual(client.timer_rate, .5)

    def test_gauge(self):
        client = DummyClient(True)
        self.config.registry['statsd_client'] = client
        inst = self._makeOne()
        result = inst.gauge('name', 'value')
        self.assertEqual(result, True)
        self.assertEqual(client.gauge_name, 'name')
        self.assertEqual(client.gauge_value, 'value')
        self.assertEqual(client.gauge_rate, 1)
        
    def test_incr(self):
        client = DummyClient(True)
        self.config.registry['statsd_client'] = client
        inst = self._makeOne()
        result = inst.incr('name', 5)
        self.assertEqual(result, True)
        self.assertEqual(client.incr_name, 'name')
        self.assertEqual(client.incr_value, 5)
        self.assertEqual(client.incr_rate, 1)
        
        
class DummyClient(object):
    def __init__(self, result):
        self.result = result

    def timer(self, timer_name, rate=1):
        self.timer_name = timer_name
        self.timer_rate = rate
        return self.result

    def gauge(self, name, value, rate=1):
        self.gauge_name = name
        self.gauge_value = value
        self.gauge_rate = rate
        return self.result
    
    def incr(self, name, value=1, rate=1):
        self.incr_name = name
        self.incr_value = value
        self.incr_rate = rate
        return self.result
    
        
    
