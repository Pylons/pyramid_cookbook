from pyramid.traversal import find_interface

from substanced.util import get_dotted_name
from substanced.objectmap import find_objectmap

from substanced.catalog.indexes import AllowedIndex
from substanced.catalog import Catalog

import logging

_marker = object()

logger = logging.getLogger('evolution')

def evolve(root):
    logger.info(
        'Running substanced evolve step 9: reindex all allowed indices '
        'due to change in discriminator principal repr'
        )

    site = root

    objectmap = find_objectmap(site)

    index_oids = objectmap.get_extent(get_dotted_name(AllowedIndex))

    for oid in index_oids:
        index = objectmap.object_for(oid)
        catalog = find_interface(index, Catalog)
        catalog.reindex(indexes=(index.__name__,))
