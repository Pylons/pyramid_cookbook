from zope.interface import providedBy

from pyramid.security import principals_allowed_by_permission
from pyramid.compat import is_nonstr_iter
from pyramid.threadlocal import get_current_registry

from ..interfaces import IIndexView

from ..util import (
    get_all_permissions,
    get_principal_repr,
    )

_marker = object()

class AllowedIndexDiscriminator(object):
    def __init__(self, permissions=None):
        if permissions is not None and not is_nonstr_iter(permissions):
            permissions = (permissions,)
        if is_nonstr_iter(permissions):
            permissions = set(permissions)
        self.permissions = permissions

    def __call__(self, resource, default):
        permissions = self.permissions

        if permissions is None:
            registry = get_current_registry() # XXX lame
            permissions = get_all_permissions(registry)

        values = []

        for permission in permissions:
            principal_ids = principals_allowed_by_permission(
                resource,
                permission
                )
            for principal_id in principal_ids:
                principal_repr = get_principal_repr(principal_id)
                values.append((principal_repr, permission))

        if not values:
            return default
            
        return values

class IndexViewDiscriminator(object):
    get_current_registry = staticmethod(get_current_registry) # for testing
    
    def __init__(self, catalog_name, index_name):
        self.catalog_name = catalog_name
        self.index_name = index_name

    def __call__(self, resource, default):
        registry = self.get_current_registry() # XXX lame
        composite_name = '%s|%s' % (self.catalog_name, self.index_name)
        resource_iface = providedBy(resource)
        index_view = registry.adapters.lookup(
            (resource_iface,),
            IIndexView,
            name=composite_name,
            default=None,
            )
        if index_view is None:
            return default
        return index_view(resource, default)

def dummy_discriminator(object, default):
    return default
