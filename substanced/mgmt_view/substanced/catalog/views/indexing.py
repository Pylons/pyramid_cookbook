from pyramid.view import view_defaults
from pyramid.httpexceptions import HTTPFound
from pyramid.session import check_csrf_token

from substanced.interfaces import MODE_IMMEDIATE
from substanced.util import (
    get_oid,
    find_catalogs,
    )

from substanced.sdi import (
    mgmt_view,
    RIGHT,
    )

@view_defaults(
    catalogable=True,
    name='indexing',
    permission='sdi.manage-catalog',
    )
class IndexingView(object):

    def __init__(self, context, request):
        self.context = context
        self.request = request
    
    @mgmt_view(
        renderer='templates/indexing.pt',
        tab_title='Indexing',
        tab_near=RIGHT, # try not to be the default tab, we're too obscure
        )
    def show(self):
        oid = get_oid(self.context)
        catalogs = []
        for catalog in find_catalogs(self.context):
            indexes = []
            catalogs.append((catalog, indexes))
            for index in catalog.values():
                docrepr = index.document_repr(oid, '(not indexed)')
                indexes.append({'index':index, 'value':docrepr})
        return {'catalogs':catalogs}

    @mgmt_view(request_method='POST', tab_condition=False)
    def reindex(self):
        context = self.context
        request = self.request
        check_csrf_token(request)
        oid = get_oid(context)
        for catalog in find_catalogs(context):
            catalog.reindex_resource(
                context, oid=oid, action_mode=MODE_IMMEDIATE
                )
        request.sdiapi.flash_with_undo('Object reindexed', 'success')
        return HTTPFound(request.sdiapi.mgmt_url(context, '@@indexing'))
