import logging

from substanced.util import postorder
from substanced.interfaces import PrincipalToACLBearing
from substanced.objectmap import find_objectmap
from substanced._compat import INT_TYPES

_marker = object()

logger = logging.getLogger('evolution')

_TO_APPEND = INT_TYPES + (tuple,)

def _referenceable_principals(acl):
    result = set()
    for ace in (acl or ()):
        principal_id = ace[1]
        if isinstance(principal_id, _TO_APPEND):
            result.add(principal_id)
    return result

def evolve(root):
    logger.info(
        'Running substanced evolve step 2: add PRINCIPAL_TO_ACL_BEARING '
        'relationships'
        )
    objectmap = find_objectmap(root)
    if objectmap is None:
        return
    for obj in postorder(root):
        logger.info(
            'Substanced evolve step 2: trying %s' % (obj,)
            )
        acl = getattr(obj, '__acl__', _marker)
        if acl is _marker:
            continue
        for princid in _referenceable_principals(acl):
            objectmap.connect(
                princid, obj, PrincipalToACLBearing,
                )
