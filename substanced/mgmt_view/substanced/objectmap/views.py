from pyramid.view import view_defaults
from pyramid.security import NO_PERMISSION_REQUIRED

from . import (
    find_objectmap,
    ReferentialIntegrityError,
    )
from ..util import get_oid

from ..sdi import (
    mgmt_view,
    RIGHT,
    )

@view_defaults(
    referenced=True,
    name='references',
    permission='sdi.manage-references',
    )
class ReferencedView(object):

    def __init__(self, context, request):
        self.context = context
        self.request = request
    
    @mgmt_view(
        renderer='templates/referenced.pt',
        tab_title='References',
        tab_near=RIGHT, # try not to be the default tab, we're too obscure
        )
    def show(self):
        oid = get_oid(self.context)
        objectmap = find_objectmap(self.context)
        targets = []
        sources = []
        for reftype in objectmap.get_reftypes():
            targetids = objectmap.targetids(oid, reftype)
            if targetids:
                targets.append((reftype, self._paths(targetids, objectmap)))
            sourceids = objectmap.sourceids(oid, reftype)
            if sourceids:
                sources.append((reftype, self._paths(sourceids, objectmap)))
        return {'targets':targets, 'sources':sources}

    def _paths(self, ids, objectmap):
        for id in ids:
            path_tuple = objectmap.path_for(id)
            path = '/'.join(path_tuple)
            yield path

@mgmt_view(
    context=ReferentialIntegrityError,
    renderer='templates/integrityerror.pt',
    permission=NO_PERMISSION_REQUIRED,
    )
def integrityerror(context, request): # pragma: no cover
    return {}
    
