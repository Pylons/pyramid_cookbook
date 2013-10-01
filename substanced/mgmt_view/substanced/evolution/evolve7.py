import logging

from pyramid.traversal import resource_path
from ZODB.POSException import POSKeyError
from ZODB.blob import Blob

from substanced.objectmap import find_objectmap
from substanced.file import File
from substanced.util import (
    get_dotted_name,
    chunks,
    )
from substanced.file import magic


_marker = object()

logger = logging.getLogger('evolution')

def evolve(root):
    logger.info(
        'Running substanced evolve step 7: reset all blob mimetypes '
        'to nominal USE_MAGIC value'
        )
    if magic:
        objectmap = find_objectmap(root)
        if objectmap is not None:
            oids = objectmap.get_extent(get_dotted_name(File))
            if oids is not None:
                for oid in oids:
                    f = objectmap.object_for(oid)
                    try:
                        if f.get_size():
                            blob = f.blob
                            fp = blob.open('r')
                            for chunk in chunks(fp):
                                m = magic.Magic(mime=True)
                                mimetype = m.from_buffer(chunk)
                                f.mimetype = mimetype
                                break
                    except POSKeyError:
                        logger.error(
                            'Missing blob for file %s, overwriting with '
                            'empty blob' % resource_path(f)
                            )
                        f.blob = Blob()
                        f.mimetype = 'application/octet-stream'
