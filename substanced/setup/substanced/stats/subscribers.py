from pyramid.events import (
    ApplicationCreated,
    subscriber
    )

from . import statsd_incr

@subscriber(ApplicationCreated)
def on_startup(event):
    statsd_incr('started')
    
