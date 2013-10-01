import sys

from pyramid.renderers import get_renderer
from pyramid.events import (
    BeforeRender,
    subscriber,
    )

def main_template():
    return get_renderer('templates/main.pt').implementation()

@subscriber(BeforeRender)
def add_helpers(event):
    event['h'] = sys.modules[__name__]

