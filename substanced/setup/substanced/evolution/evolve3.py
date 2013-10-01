from substanced.util import postorder
import logging

_marker = object()

logger = logging.getLogger('evolution')

def evolve(root):
    logger.info(
        'Running substanced evolve step 3: evolve __services__ into '
        '__is_service__'
        )
    for obj in postorder(root):
        logger.info(
            'Substanced evolve step 3: trying %s' % (obj,)
            )
        services = getattr(obj, '__services__', None)
        if services:
            for name in services:
                obj[name].__is_service__ = True
            del obj.__services__
