from substanced.objectmap import (
    find_objectmap,
    )
import logging
from substanced.file import File
from substanced.util import get_dotted_name
from pyramid.compat import string_types

_marker = object()

logger = logging.getLogger('evolution')

def evolve(root):
    logger.info(
        'Running substanced evolve step 6: files should not have USE_MAGIC '
        'as a mimetype or any other non-string value'
        )
    objectmap = find_objectmap(root)
    if objectmap is not None:
        oids = objectmap.get_extent(get_dotted_name(File))
        if oids is not None:
            for oid in oids:
                f = objectmap.object_for(oid)
                if not type(f.mimetype) in string_types:
                    f.mimetype = 'application/octet-stream'
