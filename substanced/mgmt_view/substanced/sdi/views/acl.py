import logging

from pyramid.security import (
    NO_PERMISSION_REQUIRED,
    ALL_PERMISSIONS,
    Deny,
    Everyone,
    Authenticated,
    )
from pyramid.compat import is_nonstr_iter
from pyramid.session import check_csrf_token
from pyramid.view import view_defaults
from pyramid.location import lineage

from ...objectmap import find_objectmap
from ...util import (
    get_oid,
    get_all_permissions,
    set_acl,
    find_service,
    )
from ..._compat import STRING_TYPES

from .. import mgmt_view

logger = logging.getLogger(__name__)

NO_INHERIT = (Deny, Everyone, ALL_PERMISSIONS)

@view_defaults(name='acl_edit', permission='sdi.change-acls',
               renderer='templates/acl.pt')
class ACLEditViews(object):

    get_all_permissions = staticmethod(get_all_permissions) # for testing

    def __init__(self, context, request):
        self.context = context
        self.request = request
        self.acl = self.original_acl = getattr(context, '__acl__', [])
        if self.acl and self.acl[-1] == NO_INHERIT:
            self.acl = self.acl[:-1]
            self.epilog = [NO_INHERIT]
        else:
            self.epilog = []

    @mgmt_view(tab_title='Security')
    def acl_view(self):
        return self.finish_acl_edit()

    @mgmt_view(tab_condition=False, name='inherited_acl',
               renderer='templates/acl#inherited_acl.pt')
    def inherited_acl(self):
        return self.finish_acl_edit()

    @mgmt_view(tab_condition=False, name='local_acl',
               renderer='templates/acl#local_acl.pt')
    def local_acl(self):
        return self.finish_acl_edit()
    
    @mgmt_view(request_param='form.move_up', tab_title='Security')
    def move_up(self):
        check_csrf_token(self.request)
        index = int(self.request.POST['index'])
        if index > 0:
            new = self.acl[:]
            new[index-1], new[index] = new[index], new[index-1]
            self.acl = new
        self.request.sdiapi.flash_with_undo('ACE moved up')
        return self.finish_acl_edit()

    @mgmt_view(request_param='form.move_down', tab_title='Security')
    def move_down(self):
        check_csrf_token(self.request)
        index = int(self.request.POST['index'])
        if index < len(self.acl) - 1:
            new = self.acl[:]
            new[index+1], new[index] = new[index], new[index+1]
            self.acl = new
        self.request.sdiapi.flash_with_undo('ACE moved down')
        return self.finish_acl_edit()

    @mgmt_view(request_param='form.remove', tab_title='Security')
    def remove(self):
        check_csrf_token(self.request)
        index = int(self.request.POST['index'])
        new = self.acl[:]
        del new[index]
        self.acl = new
        self.request.sdiapi.flash_with_undo('ACE removed')
        return self.finish_acl_edit()

    @mgmt_view(request_param='form.add', tab_title='Security')
    def add(self):
        check_csrf_token(self.request)
        objectmap = find_objectmap(self.context)
        verb = self.request.POST['verb']
        principal_id_str = self.request.POST['principal']
        if principal_id_str in (Everyone, Authenticated):
            principal_id = principal_id_str
        else:
            try:
                principal_id = int(principal_id_str)
            except ValueError:
                principal_id = None
                
        if principal_id is None:
            self.request.session.flash('No principal selected', 'error')
            
        else:
            if principal_id not in (Everyone, Authenticated):
                if objectmap.object_for(principal_id) is None:
                    self.request.session.flash(
                        'Unknown user or group when adding ACE',
                        'error')
                    principal_id = None
                    
            if principal_id is not None:
                permissions = self.request.POST.getall('permissions')
                if not permissions:
                    permissions = ()
                if '-- ALL --' in permissions:
                    permissions = ALL_PERMISSIONS
                new = self.acl[:]
                new.append((verb, principal_id, permissions))
                self.acl = new
                self.request.sdiapi.flash_with_undo('New ACE added')
        return self.finish_acl_edit()
                
    @mgmt_view(request_param='form.inherit', tab_title='Security')
    def inherit(self):
        check_csrf_token(self.request)
        no_inherit = self.request.POST['inherit'] == 'disabled'
        if no_inherit:
            self.epilog = [NO_INHERIT]
            self.request.sdiapi.flash_with_undo(
                'ACL will *not* inherit from parent')
        else:
            self.epilog = []
            self.request.sdiapi.flash_with_undo(
                'ACL will inherit from parent')
        return self.finish_acl_edit()

    def get_principal_name(self, principal_id):
        objectmap = find_objectmap(self.context)
        if principal_id  in (Everyone, Authenticated):
            pname = principal_id
        else:
            principal = objectmap.object_for(principal_id)
            if principal is None:
                pname = '<deleted principal>'
            else:
                pname = principal.__name__
        return pname

    def get_parent_acl(self, parent):
        parent_acl = []

        while parent is not None:
            p_acl = getattr(parent, '__acl__', ())
            stop = False
            for ace in p_acl:
                if ace == NO_INHERIT:
                    stop = True
                else:
                    principal_id = ace[1]
                    pname = self.get_principal_name(principal_id)
                    if ace[2] == ALL_PERMISSIONS:
                        perms =  ('-- ALL --',)
                    else:
                        perms = ace[2]
                    if not is_nonstr_iter(perms):
                        perms = (perms,)
                    new_ace = (ace[0], pname, perms)
                    parent_acl.append(new_ace)
            if stop:
                break
            parent = parent.__parent__
        return parent_acl

    def get_local_acl(self):
        local_acl = []
        inheriting = 'enabled'
        l_acl = getattr(self.context, '__acl__', ())
        for l_ace in l_acl:
            principal_id = l_ace[1]
            permissions = l_ace[2]
            if l_ace == NO_INHERIT:
                inheriting = 'disabled'
                break
            if permissions == ALL_PERMISSIONS:
                permissions = ('-- ALL --',)
            if (isinstance(permissions, STRING_TYPES) or
                not hasattr(permissions, '__iter__')):
                permissions = (permissions,)
            pname = self.get_principal_name(principal_id)
            new_ace = (l_ace[0], pname, permissions)
            local_acl.append(new_ace)
        return inheriting, local_acl


    def finish_acl_edit(self):
        principal_service = find_service(self.context, 'principals')
        objectmap = find_objectmap(self.context)
        registry = self.request.registry
        self.acl = self.acl + self.epilog

        if self.acl != self.original_acl:
            set_acl(self.context, self.acl, registry=registry)

        parent = self.context.__parent__
        parent_acl = self.get_parent_acl(parent)

        inheriting, local_acl = self.get_local_acl()

        permissions = set(['-- ALL --'])
        registered_permissions = self.get_all_permissions(registry)
        for name in registered_permissions:
            if name != NO_PERMISSION_REQUIRED:
                permissions.add(name)
        permissions = list(permissions)
        permissions.sort()

        users = principal_service['users'].values()
        users = [ (get_oid(user), user.__name__) for user in users ]
        groups = principal_service['groups'].values()
        groups = [ (get_oid(group), group.__name__) for group in groups ]
        groups += [ (Everyone, Everyone), (Authenticated, Authenticated) ]

        oids = [ get_oid(x) for x in lineage(self.context) ]

        pathcount = objectmap.pathcount(self.context)

        return dict(
            parent_acl=parent_acl or (),
            local_acl=local_acl,
            permissions=permissions,
            inheriting=inheriting,
            users=users,
            groups=groups,
            oids=oids,
            pathcount=pathcount,
            )

