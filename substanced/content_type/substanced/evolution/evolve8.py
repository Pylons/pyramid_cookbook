from pyramid.compat import string_types

from substanced.util import (
    get_oid,
    is_folder,
    )
    
import logging

_marker = object()

logger = logging.getLogger('evolution')

def postorder(startnode):
    """ Cannot use utils.postorder because it uses node.values """
    def visit(node):
        if is_folder(node):
            for child in node.data.values():
                for result in visit(child):
                    yield result
        yield node
    return visit(startnode)

def evolve(root):
    logger.info(
        'Running substanced evolve step 8: add explicit oid ordering to folders'
        )
    for obj in postorder(root):
        if is_folder(obj):
            order = getattr(obj, '_order', None)
            if order is not None:
                oid_order = ()
                name_order = ()
                if order:
                    if isinstance(order[0], string_types):
                        # handle master branch
                        name_order = obj._order
                        oid_order = []
                        for name in name_order:
                            oid_order.append(get_oid(obj.data[name]))
                    else:
                        # handle ree-ordering-clientside-foo-bar-baz branch
                        name_order = [x[0] for x in order]
                        oid_order = [x[1] for x in order]
                obj._order = tuple(name_order)
                obj._order_oids = tuple(oid_order)
