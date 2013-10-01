import logging
import os

from pyramid.events import (
    ApplicationCreated,
    subscriber,
    )
from pyramid.request import Request
from pyramid.settings import asbool

from . import EvolutionManager

logger = logging.getLogger(__name__)

@subscriber(ApplicationCreated)
def on_startup(event):
    app = event.object
    registry = app.registry
    settings = getattr(registry, 'settings', {})
    autoevolve = asbool(
        os.environ.get('SUBSTANCED_AUTOEVOLVE',
                       settings.get('substanced.autoevolve', False))
        )
    if autoevolve:
        request = Request.blank('/') # path is meaningless
        request.registry = registry
        root = app.root_factory(request)
        em = EvolutionManager(root, registry)
        complete = em.evolve(commit=True)
        if complete:
            for step in complete:
                logger.info('Ran evolution step: %s', step)
        else:
            logger.info('No evolution steps to run.')
