from substanced.objectmap import (
    find_objectmap,
    )
import logging
from substanced.catalog import Catalog
from substanced.util import get_dotted_name

_marker = object()

logger = logging.getLogger('evolution')

def evolve(root):
    logger.info(
        'Running substanced evolve step 5: remove None as default for index '
        'action mode (MODE_ATCOMMIT should be implicit default)'
        )
    objectmap = find_objectmap(root)
    if objectmap is not None:
        oids = objectmap.get_extent(get_dotted_name(Catalog))
        for oid in oids:
            catalog = objectmap.object_for(oid)
            if catalog is not None:
                for index in catalog.values():
                    # wake up index via getattr first
                    if (index.action_mode is None and
                        'action_mode' in index.__dict__):
                        del index.action_mode
