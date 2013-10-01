from substanced.util import postorder
import logging

_marker = object()

logger = logging.getLogger('evolution')

def evolve(root):
    logger.info(
        'Running substanced evolve step 1: convert __objectid__ to __oid__'
        )
    for obj in postorder(root):
        logger.info(
            'Substanced evolve step 1: trying %s' % (obj,)
            )
        objectid = getattr(obj, '__objectid__', _marker)
        if objectid is _marker:
            continue
        if hasattr(obj, '__oid__'):
            continue
        obj.__oid__ = objectid
        del obj.__objectid__
