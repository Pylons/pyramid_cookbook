from ..util import get_oid
from .._compat import INT_TYPES

def oid_from_resource(resource):
    oid = get_oid(resource, None)
    if not isinstance(oid, INT_TYPES):
        raise ValueError(
            'Resource must be an object with an integer __oid__ attribute'
            )
    return oid
