from pyramid.traversal import resource_path

from pyramid.httpexceptions import HTTPFound

from substanced.interfaces import (
    ILockService,
    IFolder,
    )
from substanced.form import FormView
from substanced.sdi import mgmt_view
from substanced.folder.views import (
    FolderContents,
    folder_contents_views,
    )

from . import LockSchema

@mgmt_view(
    context=IFolder,
    name='add_lock_service',
    tab_condition=False,
    permission='sdi.add-services',
    )
def add_lock_service(context, request):
    service = request.registry.content.create('Lock Service')
    context.add_service('locks', service)
    return HTTPFound(location=request.sdiapi.mgmt_path(context))

@mgmt_view(
    context=ILockService,
    name='add_lock',
    permission='sdi.add-content', 
    renderer='substanced.sdi.views:templates/form.pt',
    tab_condition=False
    )
class AddLockView(FormView):
    title = 'Add Lock'
    schema = LockSchema()
    buttons = ('add',)

    def add_success(self, appstruct):
        registry = self.request.registry
        lock = registry.content.create(
            'Lock',
            timeout=appstruct['timeout'],
            last_refresh=appstruct['last_refresh'],
            )
        self.context.add_next(lock)
        lock.ownerid = appstruct['ownerid']
        lock.resource = appstruct['resource']
        return HTTPFound(
            self.request.sdiapi.mgmt_path(self.context, '@@contents')
            )

@folder_contents_views(
    context=ILockService,
    )
class LockServiceFolderContents(FolderContents):
    def get_buttons(self):
        button_groups = self.get_default_buttons()[-1:]
        new_buttons = [
            {'id':'delete_expired',
             'name':'form.delete_expired',
             'class':'btn-sdi-act',
             'value':'delete_expired',
             'text':'Delete Expired'
             },
            ]
        button_groups.append(
            {'type':'group', 'buttons':new_buttons}
            )
        return button_groups

    def get_columns(self, subobject):
        columns = self.get_default_columns(subobject)
        owner = getattr(subobject, 'owner', None)
        if owner is not None:
            owner = owner.__name__
        resource = getattr(subobject, 'resource', None)
        if resource is not None:
            resource = resource_path(resource)
        expires = getattr(subobject, 'expires', None)
        if expires is not None:
            expires = expires()
        if expires is not None:
            tz = self.request.user.timezone
            expires = expires.replace(tzinfo=None) # in case it's not naive
            expires = tz.localize(expires).strftime('%Y-%m-%d %H:%M:%S %Z')
        
        columns.extend((
            {'name':'Owner',
             'value':owner,
             },
            {'name':'Resource',
             'value':resource,
             },
            {'name':'Expires',
             'value':expires,
             },
            ))

        return columns

    def delete_expired(self):
        todelete = []
        # build a secondary list so we don't mutate the BTree while iterating
        for lock in self.context.values():
            if not lock.is_valid():
                todelete.append(lock)
        for item in todelete:
            item.commit_suicide()
        return self.get_redirect_response()
    
def includeme(config): # pragma: no cover
    config.add_mgmt_view(
        LockServiceFolderContents,
        context=ILockService,
        name='contents',
        permission='sdi.manage-content',
        request_method='POST',
        request_param='form.delete_expired',
        tab_condition=False,
        attr='delete_expired',
        )
