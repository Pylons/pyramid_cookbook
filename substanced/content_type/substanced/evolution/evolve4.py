from substanced.objectmap import (
    ExtentMap,
    find_objectmap,
    )
import logging

_marker = object()

logger = logging.getLogger('evolution')

def evolve(root):
    logger.info(
        'Running substanced evolve step 4: add an extentmap to the objectmap'
        )
    objectmap = find_objectmap(root)
    if objectmap is not None:
        objectmap.extentmap = ExtentMap()
    for oid in objectmap.objectid_to_path:
        obj = objectmap.object_for(oid, root)
        logger.info('Adding oid %s to extentmap' % oid)
        if obj is not None:
            objectmap.extentmap.add(obj, oid)
