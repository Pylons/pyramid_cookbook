import colander
import deform.widget

from hypatia.interfaces import IIndex
from hypatia.query import parse_query

from pyramid.httpexceptions import HTTPFound

from pyramid.view import view_defaults

from substanced.catalog import logger
from substanced.form import FormView
from substanced.interfaces import ICatalog, IFolder
from substanced.objectmap import find_objectmap
from substanced.schema import Schema
from substanced.sdi import mgmt_view

def context_is_an_index(context, request):
    return request.registry.content.metadata(context, 'is_index', False)

@view_defaults(
    name='manage_catalog',
    context=ICatalog,
    renderer='templates/catalog.pt',
    permission='sdi.manage-catalog'
    )
class ManageCatalog(object):
    def __init__(self, context, request):
        self.context = context
        self.request = request

    @property
    def redir_location(self):
        return self.request.sdiapi.mgmt_path(self.context, '@@manage_catalog')
        
    @mgmt_view(request_method='GET', tab_title='Manage')
    def view(self):
        cataloglen = len(self.context.objectids)
        return dict(cataloglen=cataloglen)

    @mgmt_view(request_method='POST', request_param='reindex', check_csrf=True)
    def reindex(self):
        self.context.reindex()
        self.request.session.flash('Catalog reindexed')
        return HTTPFound(location=self.redir_location)

    @mgmt_view(request_method='POST', request_param='update', check_csrf=True)
    def update(self):
        self.context.update_indexes()
        self.request.session.flash('Catalog index definitions updated')
        return HTTPFound(location=self.redir_location)

@view_defaults(
    name='manage_index',
    context=IIndex,
    renderer='templates/index.pt',
    permission='sdi.manage-catalog')
class ManageIndex(object):
    def __init__(self, context, request):
        self.context = context
        self.request = request

    @property
    def redir_location(self):
        return self.request.sdiapi.mgmt_path(self.context, '@@manage_index')

    @mgmt_view(request_method='GET', tab_title='Manage')
    def view(self):
        index = self.context
        indexed = index.indexed_count()
        not_indexed = index.not_indexed_count()
        index_name = index.__name__
        return dict(
            indexed=indexed,
            not_indexed=not_indexed,
            index_name=index_name,
            index_type = index.__class__.__name__,
            )

    @mgmt_view(request_method='POST', request_param='reindex', check_csrf=True)
    def reindex(self):
        index_name = self.context.__name__
        catalog  = self.context.__parent__
        if ICatalog.providedBy(catalog):
            catalog.reindex(indexes=[index_name])
            self.request.session.flash('Index "%s" reindexed' % index_name,
                                       'success')
        else:
            self.request.session.flash(
                'Cannot reindex an index unless it is contained in a catalog',
                'error'
                )
        return HTTPFound(location=self.redir_location)

class SearchSchema(Schema):
    cqe_expression = colander.SchemaNode(
        colander.String(),
        widget = deform.widget.TextAreaWidget(rows=10, cols=120),
        title='CQE Expression',
        )

@mgmt_view(context=ICatalog, name='search_catalog', 
           permission='sdi.manage-catalog', 
           renderer='templates/search.pt', tab_title='Search')
class SearchCatalogView(FormView):
    schema = SearchSchema(title='Expression')
    buttons = ('search',)
    catalog_results = None
    logger = logger
    parse_query = staticmethod(parse_query) # for testing
    find_objectmap = staticmethod(find_objectmap) # for testing

    def search_success(self, appstruct):
        """ Accept a CQE expression and a permitted value and return a 
        sequence of object renderings """
        self.request.session['catalogsearch.appstruct'] = appstruct
        context = self.context
        return HTTPFound(
            location=self.request.sdiapi.mgmt_path(context, '@@search_catalog')
            )

    def show(self, form):
        appstruct = self.request.session.pop('catalogsearch.appstruct',
                                             colander.null)
        searchresults = ()
        if appstruct:
            expr = appstruct['cqe_expression']
            try:
                q = self.parse_query(expr, self.context)
                resultset = q.execute().all(resolve=False)
            except Exception as e:
                self.logger.exception('During search')
                cls_name = e.__class__.__name__
                msg = 'Query failed (%s: %s)' % (cls_name, e.args[0])
                self.request.session.flash(msg, 'error')
            else:
                objectmap = self.find_objectmap(self.context)
                resolve = objectmap.object_for
                searchresults = list([(oid, resolve(oid)) for oid in resultset])
                if not searchresults:
                    searchresults = [('', 'No results')]
                self.request.session.flash('Query succeeded', 'success')
        return {
            'searchresults':searchresults,
            'form':form.render(appstruct=appstruct),
            }

# reindex button handler

@mgmt_view(
    context=IFolder,
    content_type='Catalog',
    name='contents',
    request_param='form.reindex',
    request_method='POST',
    renderer='substanced.folder:templates/contents.pt',
    permission='sdi.manage-contents',
    tab_condition=False,
    )
def reindex_indexes(context, request):
    toreindex_str = request.POST.get('item-modify', '')
    toreindex = [x for x in toreindex_str.split('/') if x]
    toreindex_fmt = ', '.join(toreindex)
    if toreindex:
        context.reindex(indexes=toreindex, registry=request.registry)
        request.session.flash(
            'Reindex of selected indexes %s succeeded' % (toreindex_fmt,),
            'success'
            )
    else:
        request.session.flash(
            'No indexes selected to reindex',
            'error'
            )
        
    return HTTPFound(request.sdiapi.mgmt_path(context, '@@contents'))
