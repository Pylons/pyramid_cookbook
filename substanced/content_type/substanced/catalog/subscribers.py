import logging
import os

from zope.interface.interfaces import ComponentLookupError

from pyramid.traversal import resource_path
from pyramid.settings import asbool
from pyramid.events import (
    ApplicationCreated,
    subscriber,
    )
from pyramid.request import Request

from ..event import (
    subscribe_added,
    subscribe_removed,
    subscribe_modified,
    subscribe_acl_modified,
    )

from ..objectmap import find_objectmap

from ..util import (
    postorder,
    get_oid,
    find_catalogs,
    )

logger = logging.getLogger(__name__)

@subscribe_added()
def object_added(event):
    """ An IObjectAdded event subscriber which indexes an object and and its
    children in every catalog service in the lineage of the object. Depends
    upon the fact that ``substanced.objectmap.object_will_be_added`` to
    assign an ``__oid__`` to the object and its children will have been
    fired before this gets fired.
    """
    obj = event.object
    catalogs = find_catalogs(obj)
    if not catalogs:
        return

    reindex_only = False

    if event.moving is not None:
        # If we're being moved into a place with the same catalogs
        # as the old place, just reindex; don't add.  The object_removed
        # subscriber depends on this behavior.
        if event.parent is event.moving:
            # optimization to avoid calling find_catalogs during simple rename
            reindex_only = True 
        else:
            old_catalogs = find_catalogs(event.moving)
            if catalogs == old_catalogs:
                reindex_only = True

    # XXX note that adding objects to an unseated folder that itself contains a
    # catalog will cause rework to be done, as the below logic will fire once
    # for the children of the object that was added before the seating, then
    # once for the same children when the parent object is seated.

    for node in postorder(obj):
        oid = get_oid(node, None)
        if oid is not None:
            for catalog in catalogs:
                if reindex_only:
                    catalog.reindex_resource(node, oid=oid)
                else:
                    catalog.index_resource(node, oid=oid)

@subscribe_removed()
def object_removed(event):
    """ Unindex an object and its children from every catalog service object's
    lineage; an :class:`substanced.event.ObjectRemoved` event
    subscriber"""
    parent = event.parent
    catalogs = find_catalogs(parent)

    if event.moving is not None:
        # Don't actually unindex anything if we're moving to a place that has a
        # lineage with the same set of catalogs; the object_added event
        # subscriber will reindex everything, so there's no sense in actually
        # doing an unindex.
        rename_in_progress = parent is event.moving
        if rename_in_progress:
            # Common-case optimization to avoid calling find_catalogs below
            return 
        else:
            new_catalogs = find_catalogs(event.moving)
            if catalogs == new_catalogs:
                return

    # If this event is not a moving event, or if it is a moving event and the
    # set of catalogs differs between the object's old home and its new home,
    # unindex every object related to this removal.

    removed = event.removed_oids

    for catalog in catalogs:
        for oid in catalog.family.IF.intersection(removed, catalog.objectids):
            catalog.unindex_resource(oid)

@subscribe_modified()
def object_modified(event):
    """ Reindex a single object (non-recursive) in every catalog service in
    the object's lineage; an :class:`substanced.event.ObjectModifed` event
    subscriber"""
    obj = event.object
    oid = get_oid(obj, None)
    if oid is not None:
        catalogs = find_catalogs(obj)
        for catalog in catalogs:
            catalog.reindex_resource(obj, oid=oid)

@subscribe_acl_modified()
def acl_modified(event):
    resource = event.object
    registry = event.registry
    catalogs = find_catalogs(resource)

    for catalog in catalogs:
        # hellishly expensive
        indexes = catalog.values()
        for index in indexes:
            index_path = resource_path(index)
            if registry.content.istype(index, 'Allowed Index'):
                for node in postorder(resource):
                    logger.info(
                        '%s: reindexing %s due to ACL modified' % (
                            index_path, node)
                        )
                    oid = get_oid(node, None)
                    if oid is not None:
                        index.reindex_resource(node, oid=oid)

@subscriber(ApplicationCreated)
def on_startup(event):
    app = event.object
    registry = app.registry
    settings = getattr(registry, 'settings', {})
    autosync = asbool(
        os.environ.get(
            'SUBSTANCED_CATALOGS_AUTOSYNC',
            settings.get(
                'substanced.catalogs.autosync',
                settings.get('substanced.autosync_catalogs', False) # bc
                )))
    autoreindex = asbool(
        os.environ.get(
            'SUBSTANCED_CATALOGS_AUTOREINDEX',
            settings.get(
                'substanced.catalogs.autoreindex',
                settings.get('substanced.autoreindex_catalogs', False) # bc
                )))
    if autosync:
        request = Request.blank('/autosync_catalogs') # path is meaningless
        request.registry = registry
        root = app.root_factory(request)
        objectmap = find_objectmap(root)
        if objectmap is not None:
            content = registry.content
            factory_type = content.factory_type_for_content_type('Catalog')
            oids = objectmap.get_extent(factory_type)
            for oid in oids:
                catalog = objectmap.object_for(oid)
                if catalog is not None:
                    try:
                        catalog.update_indexes(
                            registry=registry,
                            reindex=autoreindex
                            )
                    except ComponentLookupError:
                        # could not find a catalog factory
                        pass
                    
