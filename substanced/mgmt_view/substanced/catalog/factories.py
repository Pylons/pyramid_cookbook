import pickle
import zlib

import BTrees
from zope.interface import implementer

from pyramid.compat import is_nonstr_iter
from pyramid.traversal import resource_path

from ..interfaces import (
    ICatalogFactory,
    IIndexFactory,
    )
from ..util import get_dotted_name

from .indexes import (
    TextIndex,
    FieldIndex,
    KeywordIndex,
    FacetIndex,
    AllowedIndex,
    PathIndex,
    )

from .discriminators import (
    IndexViewDiscriminator,
    AllowedIndexDiscriminator,
    )

@implementer(IIndexFactory)
class IndexFactory(object):

    def __init__(self, **kw):
        self.kw = kw

    def __call__(self, catalog_name, index_name):
        discriminator = IndexViewDiscriminator(catalog_name, index_name)
        index = self.index_type(discriminator=discriminator, **self.kw)
        index.__factory_hash__ = hash(self)
        return index

    def hashvalues(self):
        values = {}
        values.update(self.kw)
        values['class'] = get_dotted_name(self.__class__)
        family = values.get('family', None)
        if family is not None:
            if family == BTrees.family64:
                family = 'family64'
            elif family == BTrees.family32:
                family = 'family32'
            else:
                raise ValueError(family)
            values['family'] = family
        return values

    def __hash__(self):
        data = pickle.dumps(tuple(sorted(self.hashvalues().items())))
        return zlib.crc32(data) & 0xffffffff

    def is_stale(self, index):
        index_hash = getattr(index, '__factory_hash__', None)
        return index_hash != hash(self)

class Text(IndexFactory):
    index_type = TextIndex

    def hashvalues(self):
        values = IndexFactory.hashvalues(self)
        for name in ('lexicon', 'index'):
            attr = values.get(name, None)
            if attr is not None:
                clsname = attr.__class__.__name__
                values[name] = clsname
        return values

class Field(IndexFactory):
    index_type = FieldIndex
    
class Keyword(IndexFactory):
    index_type = KeywordIndex

class Facet(IndexFactory):
    index_type = FacetIndex

    def hashvalues(self):
        values = IndexFactory.hashvalues(self)
        facets = values.get('facets', ())
        values['facets'] = tuple(sorted([(x,y) for x, y in facets]))
        return values

class Allowed(IndexFactory):
    index_type = AllowedIndex

    def __call__(self, catalog_name, index_name):
        kw = self.kw.copy() # hashvalues below needs permissions
        permissions = kw.pop('permissions', None)
        discriminator = AllowedIndexDiscriminator(permissions)
        index = self.index_type(discriminator=discriminator, **kw)
        index.__factory_hash__ = hash(self)
        return index

    def hashvalues(self):
        values = IndexFactory.hashvalues(self)
        permissions = values.get('permissions', None)
        if not is_nonstr_iter(permissions):
            permissions = (permissions,)
        values['permissions'] = tuple(sorted(permissions))
        return values

class Path(IndexFactory):
    index_type = PathIndex

@implementer(ICatalogFactory)
class CatalogFactory(object):
    def __init__(self, name, index_factories):
        self.name = name
        self.index_factories = index_factories

    def _remove_stale(self, catalog, output=None):
        catalog_path = resource_path(catalog)
        result = False
        for index_name, index in list(catalog.items()):
            if not index_name in self.index_factories:
                output and output(
                    '%s: removing stale index named %r' % (
                        catalog_path,
                        index_name,
                        )
                    )
                catalog.remove(index_name)
                result = True
        return result

    def replace(self, catalog, reindex=False, output=None, **reindex_kw):
        catalog_path = resource_path(catalog)

        to_reindex = set()

        changed = False

        for index_name, index_factory in self.index_factories.items():
            if index_name in catalog:
                verb = 'replacing'
            else:
                verb = 'adding'

            output and output(
                '%s: %s index named %r' % (catalog_path, verb, index_name),
                )

            index = index_factory(self.name, index_name)
            index.__sdi_deletable__ = False
            catalog.replace(index_name, index)
            to_reindex.add(index_name)
            changed = True

        removed_stale = self._remove_stale(catalog, output=output)

        if changed and reindex:
            catalog.reindex(indexes=to_reindex, output=output, **reindex_kw)

        return removed_stale or changed

    def sync(self, catalog, reindex=False, output=None, **reindex_kw):

        catalog_path = resource_path(catalog)

        to_reindex = set()
        changed = False

        for index_name, index_factory in self.index_factories.items():
            if not index_name in catalog:
                output and output(
                    '%s: adding index named %r' % (catalog_path, index_name),
                    )
                index = index_factory(self.name, index_name)
                catalog.add(index_name, index)
                changed = True
                to_reindex.add(index_name)

            index = catalog[index_name]

            if index_factory.is_stale(index):
                output and output(
                    '%s: replacing stale index named %r' % (
                        catalog_path,
                        index_name,
                        )
                    )
                index = index_factory(self.name, index_name)
                index.__sdi_deletable__ = False
                catalog.replace(index_name, index)
                to_reindex.add(index_name)
                changed = True

        removed_stale = self._remove_stale(catalog, output=output)

        if changed and reindex:
            catalog.reindex(indexes=to_reindex, output=output, **reindex_kw)

        return changed or removed_stale

