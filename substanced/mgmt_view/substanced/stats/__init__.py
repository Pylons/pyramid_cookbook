import contextlib
import statsd

from pyramid.threadlocal import get_current_registry
from pyramid.settings import asbool

@contextlib.contextmanager
def donothing():
    yield

class StatsdHelper(object):
    # this is only a class for testing purposes

    def get_client(self, registry=None):
        if registry is None:
            registry = get_current_registry()
        client = registry.get('statsd_client')
        return client

    def timer(self, name, rate=1, registry=None):
        """ Return a context manager that can be used for statsd timing, e.g.::

             with statsd_timer('addlotsofstuff'):
                 # add lots of stuff

           ``name`` is the statsd stat name, ``rate`` is the sample rate (a
           float between 0 and 1), and ``registry`` can be passed to speed up
           lookups (it should be the Pyramid registry).
        """
        client = self.get_client(registry)
        if client is None:
            return donothing()
        return client.timer(name, rate=rate)

    def gauge(self, name, value, rate=1, registry=None):
        """ Register a statsd gauge value.  For example::

                statsd_gauge('connections', numconnections)

           ``name`` is the statsd stat name, ``rate`` is the sample rate (a
           float between 0 and 1), and ``registry`` can be passed to speed up
           lookups (it should be the Pyramid registry).
        """
        client = self.get_client(registry)
        if client is not None:
            return client.gauge(name, value, rate=rate)

    def incr(self, name, value=1, rate=1, registry=None):
        """ Incremement or decrement a statsd counter value.  For example::

                statsd_incr('hits', 1)

            To decrement::

                statsd_incr('numusers', -1)

           ``name`` is the statsd stat name, ``rate`` is the sample rate (a
           float between 0 and 1), and ``registry`` can be passed to speed up
           lookups (it should be the Pyramid registry).
        """
        client = self.get_client(registry)
        if client is not None:
            return client.incr(name, value, rate=rate)

helper = StatsdHelper()

statsd_incr = helper.incr
statsd_gauge = helper.gauge
statsd_timer = helper.timer

def includeme(config): # pragma: no cover
    settings = config.registry.settings
    statsd_enabled = asbool(settings.get('substanced.statsd.enabled', False))
    if statsd_enabled:
        host = settings.get('substanced.statsd.host', 'localhost')
        port = int(settings.get('substanced.statsd.port', 8125))
        prefix = settings.get('substanced.statsd.prefix', 'substanced')
        client = statsd.StatsClient(host=host, port=port, prefix=prefix)
        # use a dict lookup rather than a full-on utility lookup for speed
        config.registry['statsd_client'] = client
