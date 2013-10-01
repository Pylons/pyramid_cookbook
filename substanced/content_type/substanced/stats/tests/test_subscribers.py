import unittest

class Test_on_startup(unittest.TestCase):
    def test_it(self):
        from .. import subscribers
        def dummy_incr(value):
            self.assertEqual(value, 'started')
        try:
            old_statsd_incr = subscribers.statsd_incr
            subscribers.statsd_incr = dummy_incr
            subscribers.on_startup(None)
        finally:
            subscribers.statsd_incr = old_statsd_incr
            
