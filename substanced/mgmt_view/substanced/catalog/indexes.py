import colander
import deform.widget
import re

import BTrees
import hypatia.query
import hypatia.interfaces
import hypatia.field
import hypatia.facet
import hypatia.keyword
import hypatia.text
import hypatia.util
from persistent import Persistent
from pyramid.compat import (
    url_unquote_text,
    is_nonstr_iter,
    )
from pyramid.settings import asbool
from pyramid.security import effective_principals
from pyramid.traversal import resource_path_tuple
from pyramid.interfaces import IRequest
from zope.interface import implementer

from ..content import content
from .. import interfaces as sd_interfaces
from ..interfaces import (
    MODE_IMMEDIATE,
    MODE_ATCOMMIT,
    )
from ..objectmap import find_objectmap
from ..property import PropertySheet
from ..schema import Schema
from ..stats import statsd_timer
from .._compat import STRING_TYPES
from .._compat import INT_TYPES
from .._compat import u
from ..util import get_principal_repr

from .discriminators import dummy_discriminator
from .util import oid_from_resource

from . import deferred

PATH_WITH_OPTIONS = re.compile(r'\[(.+?)\](.+?)$')
_BLANK = u('')
_SLASH = u('/')

_marker = object()

class SDIndex(object):

    _p_action_tm = None
    action_mode = MODE_ATCOMMIT
    tm_class = deferred.IndexActionTM # for testing

    def resultset_from_query(self, query, names=None, resolver=None):
        # XXX we should probably flush pending atcommit actions before
        # executing the query; we can't just flush *this* index's actions,
        # we have to flush actions for all indexes in all catalogs related
        # to this query.
        if resolver is None:
            objectmap = find_objectmap(self)
            resolver = objectmap.object_for
        with statsd_timer('catalog.query'):
            query.flush()
            docids = query._apply(names)
            numdocs = len(docids)
            return hypatia.util.ResultSet(docids, numdocs, resolver)

    def get_action_tm(self):
        action_tm = self._p_action_tm
        if action_tm is None:
            action_tm = self._p_action_tm = self.tm_class(self)
            action_tm.register()
        return action_tm

    def flush(self, all=True):
        # This method will be called before query execution for every index
        # involved in a query.  It must be callable more than once without
        # having any issues.
        if self._p_action_tm is not None:
            self._p_action_tm.flush(all=all)

    def add_action(self, action):
        action_tm = self.get_action_tm()
        action_tm.add(action)

    def index_resource(self, resource, oid=None, action_mode=None):
        if oid is None:
            oid = oid_from_resource(resource)
        if action_mode is None:
            action_mode = self.action_mode
        if action_mode is MODE_IMMEDIATE:
            self.index_doc(oid, resource)
        else:
            action = deferred.IndexAction(self, action_mode, oid)
            self.add_action(action)

    def reindex_resource(self, resource, oid=None, action_mode=None):
        if oid is None:
            oid = oid_from_resource(resource)
        if action_mode is None:
            action_mode = self.action_mode
        if action_mode is MODE_IMMEDIATE:
            self.reindex_doc(oid, resource)
        else:
            action = deferred.ReindexAction(self, action_mode, oid)
            self.add_action(action)

    def unindex_resource(self, resource_or_oid, action_mode=None):
        if isinstance(resource_or_oid, INT_TYPES):
            oid = resource_or_oid
        else:
            oid = oid_from_resource(resource_or_oid)
        if action_mode is None:
            action_mode = self.action_mode
        if action_mode is MODE_IMMEDIATE:
            self.unindex_doc(oid)
        else:
            action = deferred.UnindexAction(self, action_mode, oid)
            self.add_action(action)

    def __repr__(self):
        klass = self.__class__
        classname = '%s.%s' % (klass.__module__, klass.__name__)
        return '<%s object %r at %#x>' % (classname,
                                          getattr(self, '__name__', None),
                                          id(self))

@content(
    'Path Index',
    icon='icon-search',
    is_index=True,
    )
@implementer(hypatia.interfaces.IIndex)
class PathIndex(SDIndex, hypatia.util.BaseIndexMixin, Persistent):
    """ Uses the objectmap to apply a query to retrieve object identifiers at
    or under a path"""
    family = BTrees.family64
    include_origin = True
    depth = None

    def __init__(self, discriminator=None, family=None):
        if family is not None:
            self.family = family
        self.reset()

    def document_repr(self, docid, default=None):
        objectmap = find_objectmap(self.__parent__)
        path = objectmap.path_for(docid)
        if path is None:
            return default
        return path

    def reset(self):
        self._not_indexed = self.family.IF.Set()

    def index_doc(self, docid, obj):
        pass

    def unindex_doc(self, docid):
        pass

    def reindex_doc(self, docid, obj):
        pass

    def docids(self):
        return self.__parent__.objectids

    indexed = docids

    def not_indexed(self):
        return self._not_indexed

    def search(self, path_tuple, depth=None, include_origin=True):
        objectmap = find_objectmap(self.__parent__)
        return objectmap.pathlookup(path_tuple, depth, include_origin)

    def _parse_optionstr(self, optionstr):
        D = {}
        options = [ x.strip() for x in optionstr.split(',') ]
        for option in options:
            if '=' in option:
                name, val = [ x.strip() for x in option.split('=') ]
            else:
                name = option
                val = True
            D[name] = val
        return D
            
    def _parse_path_str(self, path_str):
        # /foo -> stuff under /foo with default depth and include_origin
        # [depth=2]/foo -> stuff under /foo with depth 2 and default i_o
        # [include_origin=false]/foo -> stuff under /foo without include_origin
        # [depth=2,include_origin=false]/foo -> combination of all options
        if path_str.startswith('[') and ']' in path_str:
            optionstr, path = PATH_WITH_OPTIONS.match(
                path_str).groups()
            optiondict = self._parse_optionstr(optionstr)
            depth = optiondict.get('depth', None)
            include_origin =  optiondict.get('include_origin', None)
            if depth is None:
                depth = self.depth
            else:
                depth = int(depth)
            if include_origin is None:
                include_origin = self.include_origin
            else:
                include_origin = asbool(include_origin)
        else:
            path = path_str
            depth = self.depth
            include_origin = self.include_origin
            
        if not path.startswith('/'):
            raise ValueError('Path must start with a slash')
        
        tmp = [x for x in url_unquote_text(path).split(_SLASH) if x]
        path_tuple = (_BLANK,) + tuple(tmp)
        return path_tuple, depth, include_origin

    def _parse_path(self, obj_or_path):
        depth = self.depth
        include_origin = self.include_origin
        path_tuple = obj_or_path
        if hasattr(obj_or_path, '__parent__'):
            path_tuple = resource_path_tuple(obj_or_path)
        elif isinstance(obj_or_path, STRING_TYPES):
            path_tuple, depth, include_origin = self._parse_path_str(
                obj_or_path)
        elif not isinstance(obj_or_path, tuple):
            raise ValueError(
                'Must be object, path string, or tuple, not %s' % (
                    obj_or_path,))
        return path_tuple, depth, include_origin

    def apply(self, obj_path_or_dict):
        if isinstance(obj_path_or_dict, dict):
            path_tuple, depth, include_origin = self._parse_path(
                obj_path_or_dict['path'])
            depth = obj_path_or_dict.get('depth', depth)
            include_origin = obj_path_or_dict.get('include_origin',
                                                  include_origin)
        else:
            path_tuple, depth, include_origin = self._parse_path(
                obj_path_or_dict)

        rs = self.search(path_tuple, depth, include_origin)

        if rs:
            return rs
        else:
            return self.family.IF.Set()

    applyEq = apply

    def eq(self, path, depth=None, include_origin=None):
        val = {'path':path}
        if depth is not None:
            val['depth'] = depth
        if include_origin is not None:
            val['include_origin'] = include_origin
        return hypatia.query.Eq(self, val)

class IndexSchema(Schema):
    """ The property schema for :class:`substanced.principal.Group`
    objects."""
    action_mode = colander.SchemaNode(
        colander.String(),
        missing=colander.null,
        widget=deform.widget.RadioChoiceWidget(
            values=(
                ('MODE_IMMEDIATE', 'Immediate'),
                ('MODE_ATCOMMIT', 'Defer Until Commit'),
                ('MODE_DEFERRED', 'Defer Until Action Processing'),
                )
            )
        )

class IndexPropertySheet(PropertySheet):
    schema = IndexSchema()

    def set(self, values):
        action_mode = values['action_mode']
        action_mode = getattr(sd_interfaces, action_mode)
        if action_mode != self.context.action_mode:
            self.context.action_mode = action_mode

    def get(self):
        action_mode = self.context.action_mode
        action_mode = action_mode.__name__
        return {'action_mode':action_mode}

@content(
    'Field Index',
    icon='icon-search',
    is_index=True,
    propertysheets = ( ('', IndexPropertySheet), ),
    )
class FieldIndex(SDIndex, hypatia.field.FieldIndex):
    def __init__(self, discriminator=None, family=None, action_mode=None):
        if discriminator is None:
            discriminator = dummy_discriminator
        hypatia.field.FieldIndex.__init__(self, discriminator, family=family)
        if action_mode is not None:
            self.action_mode = action_mode

@content(
    'Keyword Index',
    icon='icon-search',
    is_index=True,
    propertysheets = ( ('', IndexPropertySheet), ),
    )
class KeywordIndex(SDIndex, hypatia.keyword.KeywordIndex):
    def __init__(self, discriminator=None, family=None, action_mode=None):
        if discriminator is None:
            discriminator = dummy_discriminator
        hypatia.keyword.KeywordIndex.__init__(
            self, discriminator, family=family
            )
        if action_mode is not None:
            self.action_mode = action_mode

@content(
    'Text Index',
    icon='icon-search',
    is_index=True,
    propertysheets = ( ('', IndexPropertySheet), ),
    )
class TextIndex(SDIndex, hypatia.text.TextIndex):
    def __init__(
        self,
        discriminator=None,
        lexicon=None,
        index=None,
        family=None,
        action_mode=None,
        ):
        if discriminator is None:
            discriminator = dummy_discriminator
        hypatia.text.TextIndex.__init__(
            self, discriminator, lexicon=lexicon, index=index, family=family,
            )
        if action_mode is not None:
            self.action_mode = action_mode

@content(
    'Facet Index',
    icon='icon-search',
    is_index=True,
    propertysheets = ( ('', IndexPropertySheet), ),
    )
class FacetIndex(SDIndex, hypatia.facet.FacetIndex):
    def __init__(self, discriminator=None, facets=None, family=None,
                 action_mode=None):
        if discriminator is None:
            discriminator = dummy_discriminator
        if facets is None:
            facets = []
        hypatia.facet.FacetIndex.__init__(
            self, discriminator, facets=facets, family=family
            )
        if action_mode is not None:
            self.action_mode = action_mode

@content(
    'Allowed Index',
    icon='icon-search',
    is_index=True,
    propertysheets = ( ('', IndexPropertySheet), ),
    )
class AllowedIndex(KeywordIndex):
    def allows(self, principals, permission=None):
        """ ``principals`` may either be 1) a sequence of principal
        indentifiers, 2) a single principal identifier, or 3) a Pyramid
        request, which indicates that all the effective principals implied by
        the request are used.

        ``permission`` may be ``None`` if this index is configured with
        only a single permission.  Otherwise a permission name must be passed
        or an error will be raised.
        """
        permissions = self.discriminator.permissions
        if permission is None:
            if len(permissions) > 1:
                raise ValueError('Must pass a permission')
            else:
                permission = list(permissions)[0]
        else:
            if permissions is not None and not permission in permissions:
                raise ValueError(
                    'This index does not support the %s '
                    'permission' % (permission,)
                    )
        if IRequest.providedBy(principals):
            principals = effective_principals(principals)
        elif not is_nonstr_iter(principals):
            principals = (principals,)
        principals = [ get_principal_repr(p) for p in principals ]
        values = [(principal, permission) for principal in principals]
        return hypatia.query.Any(self, values)

