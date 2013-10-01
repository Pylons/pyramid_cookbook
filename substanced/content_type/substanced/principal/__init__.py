import random
import string

from persistent import Persistent
from cryptacular.bcrypt import BCRYPTPasswordManager

from zope.interface import implementer
from deform_bootstrap.widget import ChosenSingleWidget

import colander
import pytz

from pyramid.renderers import render
from pyramid.security import (
    Allow,
    Everyone,
    )
from pyramid.threadlocal import get_current_registry

from pyramid_mailer import get_mailer
from pyramid_mailer.message import Message

from ..interfaces import (
    IUser,
    IGroup,
    IUsers,
    IGroups,
    IPrincipals,
    IPasswordResets,
    IPasswordReset,
    IUserLocator,
    UserToGroup,
    UserToPasswordReset,
    )

from ..content import (
    content,
    service,
    )
from ..folder import Folder
from ..objectmap import (
    find_objectmap,
    multireference_targetid_property,
    multireference_target_property,
    multireference_sourceid_property,
    multireference_source_property,
    )
from ..property import PropertySheet
from ..schema import (
    MultireferenceIdSchemaNode,
    Schema
    )
from ..util import (
    get_oid,
    renamer,
    set_acl,
    find_service,
    acquire,
    )
from ..stats import statsd_gauge
from .._compat import _LETTERS

def _gen_random_token():
    length = random.choice(range(10, 16))
    chars = _LETTERS + string.digits
    return ''.join(random.choice(chars) for _ in range(length))

@service(
    'Principals',
    service_name='principals',
    icon='icon-lock',
    after_create='after_create',
    add_view='add_principals_service',
    )
@implementer(IPrincipals)
class Principals(Folder):
    """ Service object representing a collection of principals.  Inherits
    from :class:`substanced.folder.Folder`.

    If this object is created via
    :meth:`substanced.content.ContentRegistry.create`, the instance will
    contain three subobjects:

      ``users``

         an instance of the content type `Users``

      ``groups``

         an instance of the content type ``Groups``
         
      ``resets``

         an instance of the content type ``Password Resets``

    If however, an instance of this class is created directly (as opposed to
    being created via the ``registry.content.create`` API), you'll need to
    call its ``after_create`` method manually after you've created it
    to cause the content subobjects described above to be added to it.
    """
    def __sdi_addable__(self, context, introspectable):
        ct = introspectable.get('content_type')
        return ct in ('Users', 'Groups', 'Password Resets')
        
    def after_create(self, inst, registry):
        users = registry.content.create('Users')
        groups = registry.content.create('Groups')
        resets = registry.content.create('Password Resets')
        users.__sdi_deletable__ = False
        groups.__sdi_deletable__ = False
        resets.__sdi_deletable__ = False
        self.add('users', users, registry=registry)
        self.add('groups', groups, registry=registry)
        self.add('resets', resets, registry=registry)

    def add_user(self, login, *arg, **kw):
        """ Add a user to this principal service using the login ``login``.
        ``*arg`` and ``**kw`` are passed along to
        ``registry.content.create('User')``"""
        registry = kw.pop('registry', None)
        if registry is None:
            registry = get_current_registry()
        user = registry.content.create('User', *arg, **kw)
        self['users'][login] = user
        return user

    def add_group(self, name, *arg, **kw):
        """ Add a group to this principal service using the name ``name``.
        ``*arg`` and ``**kw`` are passed along to
        ``registry.content.create('Group')``"""
        registry = kw.pop('registry', None)
        if registry is None:
            registry = get_current_registry()
        group = registry.content.create('Group', *arg, **kw)
        self['groups'][name] = group
        return group

    def add_reset(self, user, *arg, **kw):
        """ Add a password reset to this principal service for the user
        ``user`` (either a user object or a user id).  ``name``.  ``*arg``
        and ``**kw`` are passed along to ``registry.content.create('Password
        Reset')``"""
        registry = kw.pop('registry', None)
        if registry is None:
            registry = get_current_registry()
        while 1:
            token = _gen_random_token()
            if not token in self:
                break
        reset = registry.content.create('Password Reset', *arg, **kw)
        self['resets'][token] = reset
        set_acl(reset, [(Allow, Everyone, ('sdi.view',))], registry=registry)
        objectmap = find_objectmap(self)
        objectmap.connect(user, reset, UserToPasswordReset)
        return reset

@content(
    'Users',
    icon='icon-list-alt'
    )
@implementer(IUsers)
class Users(Folder):
    """ Object representing a collection of users.  Inherits from
    :class:`substanced.folder.Folder`.  Contains objects of content type
    'User'."""
    def __sdi_addable__(self, context, introspectable):
        return introspectable.get('content_type') == 'User'

@content(
    'Groups',
    icon='icon-list-alt'
    )
@implementer(IGroups)
class Groups(Folder):
    """ Object representing a collection of groups.  Inherits from
    :class:`substanced.folder.Folder`.  Contains objects of content type 'Group'
    """
    def __sdi_addable__(self, context, introspectable):
        return introspectable.get('content_type') == 'Group'

@colander.deferred
def groupname_validator(node, kw):
    request = kw['request']
    context = request.context
    adding = not request.registry.content.istype(context, 'Group')
    def exists(node, value):
        principals = find_service(context, 'principals')
        if adding:
            try:
                context.check_name(value)
            except Exception as e:
                raise colander.Invalid(node, e.args[0], value)
        else:
            groups = principals['groups']
            if value != context.__name__:
                try:
                    groups.check_name(value)
                except Exception as e:
                    raise colander.Invalid(node, e.args[0], value)

        users = principals['users']
        if value in users:
            raise colander.Invalid(node, 'User named "%s" already exists' % 
                                   value)
        
    return colander.All(
        colander.Length(min=1, max=100),
        exists,
        )

def members_choices(context, request):
    principals = find_service(context, 'principals')
    if principals is None:
        return () # fbo dump/load
    values = [(get_oid(group), name) for name, group in 
              principals['users'].items()]
    return values

class GroupSchema(Schema):
    """ The property schema for :class:`substanced.principal.Group`
    objects."""
    name = colander.SchemaNode(
        colander.String(),
        validator=groupname_validator,
        )
    description = colander.SchemaNode(
        colander.String(),
        validator=colander.Length(max=100),
        missing='',
        )
    memberids = MultireferenceIdSchemaNode(
        choices_getter=members_choices,
        title='Members',
        )

class GroupPropertySheet(PropertySheet):
    schema = GroupSchema()

@content(
    'Group',
    icon='icon-th-list',
    add_view='add_group',
    tab_order=('properties',),
    propertysheets = (
        ('', GroupPropertySheet),
        )
    )
@implementer(IGroup)
class Group(Folder):
    """ Represents a group.  """
    def __init__(self, description=''):
        Folder.__init__(self)
        self.description = description

    memberids = multireference_targetid_property(UserToGroup)
    members = multireference_target_property(UserToGroup)
    name = renamer()

@colander.deferred
def login_validator(node, kw):
    request = kw['request']
    context = request.context
    adding = not request.registry.content.istype(context, 'User')
    def exists(node, value):
        principals = find_service(context, 'principals')
        if adding:
            try:
                context.check_name(value)
            except Exception as e:
                raise colander.Invalid(node, e.args[0], value)
        else:
            users = principals['users']
            if value != context.__name__:
                try:
                    users.check_name(value)
                except Exception as e:
                    raise colander.Invalid(node, e.args[0], value)

        groups = principals['groups']
        if value in groups:
            raise colander.Invalid(node, 'Group named "%s" already exists' % 
                                   value)
        
    return colander.All(
        colander.Length(min=1, max=100),
        exists,
        )

def groups_choices(context, request):
    principals = find_service(context, 'principals')
    if principals is None:
        return () # fbo dump/load
    values = [(get_oid(group), name) for name, group in 
              principals['groups'].items()]
    return values

_ZONES = pytz.all_timezones

@colander.deferred
def tzname_widget(node, kw): #pragma NO COVER
    return ChosenSingleWidget(values=zip(_ZONES, _ZONES))

class UserSchema(Schema):
    """ Property schema for :class:`substanced.principal.User` objects.
    """
    name = colander.SchemaNode(
        colander.String(),
        validator=login_validator,
        title='Login',
        )
    email = colander.SchemaNode(
        colander.String(),
        validator=colander.All(
            colander.Email(),
            colander.Length(max=100)
            ),
        )
    tzname = colander.SchemaNode(
        colander.String(),
        title='Timezone',
        widget=tzname_widget,
        validator=colander.OneOf(_ZONES)
        )

class UserPropertySheet(PropertySheet):
    schema = UserSchema()

class UserGroupsSchema(Schema):
    """ Restricted schema for :class:`substanced.principal.User` objects.
    """
    groupids = MultireferenceIdSchemaNode(
        choices_getter=groups_choices,
        title='Groups',
        )

class UserGroupsPropertySheet(PropertySheet):
    schema = UserGroupsSchema()
    permissions = (
        ('view', 'sdi.manage-user-groups'),
        ('change', 'sdi.manage-user-groups'),
        )

@content(
    'User',
    icon='icon-user',
    add_view='add_user',
    tab_order=('properties',),
    propertysheets = (
        ('Preferences', UserPropertySheet),
        ('Groups', UserGroupsPropertySheet),
        )
    )
@implementer(IUser)
class User(Folder):
    """ Represents a user.  """
    tzname = 'UTC' # backwards compatibility default

    pwd_manager = BCRYPTPasswordManager()

    groupids = multireference_sourceid_property(UserToGroup)
    groups = multireference_source_property(UserToGroup)
    name = renamer()

    def __init__(self, password=None, email=None, tzname=None):
        Folder.__init__(self)
        if password is not None:
            password = self.pwd_manager.encode(password)
        self.password = password
        self.email = email
        if tzname is None:
            tzname = 'UTC'
        self.tzname = tzname

    def __dump__(self):
        return dict(password=self.password)

    @property
    def timezone(self):
        return pytz.timezone(self.tzname)

    def check_password(self, password):
        """ Checks if the plaintext password passed as ``password`` matches
        this user's stored, encrypted password.  Returns ``True`` or
        ``False``."""
        statsd_gauge('check_password', 1)
        return self.pwd_manager.check(self.password, password)

    def set_password(self, password):
        self.password = self.pwd_manager.encode(password)

    def email_password_reset(self, request):
        """ Sends a password reset email."""
        root = request.virtual_root
        sitename = acquire(root, 'title', None) or 'Substance D'
        principals = find_service(self, 'principals')
        reset = principals.add_reset(self)
        # XXX should this really point at an SDI URL?
        reseturl = request.application_url + request.sdiapi.mgmt_path(reset)
        if not self.email:
            raise ValueError('User does not possess a valid email address.')
        message = Message(
            subject = 'Account information for %s' % sitename,
            recipients = [self.email],
            body = render('templates/resetpassword_email.pt',
                          dict(reseturl=reseturl))
            )
        mailer = get_mailer(request)
        mailer.send(message)

@content(
    'Password Resets',
    icon='icon-tags'
    )
@implementer(IPasswordResets)
class PasswordResets(Folder):
    """ Object representing the current set of password reset requests """
    def __sdi_addable__(self, context, introspectable):
        return introspectable.get('content_type') == 'Password Reset'

@content(
    'Password Reset',
    icon='icon-tag'
    )
@implementer(IPasswordReset)
class PasswordReset(Persistent):
    """ Object representing the a single password reset request """
    def reset_password(self, password):
        objectmap = find_objectmap(self)
        sources = list(objectmap.sources(self, UserToPasswordReset))
        user = sources[0]
        user.set_password(password)
        self.commit_suicide()

    def commit_suicide(self):
        del self.__parent__[self.__name__]

@implementer(IUserLocator)
class DefaultUserLocator(object):
    def __init__(self, context, request):
        self.context = context
        self.request = request

    def get_user_by_login(self, login):
        context = self.context
        users = find_service(context, 'principals', 'users')
        return users.get(login)

    def get_user_by_userid(self, userid):
        objectmap = find_objectmap(self.context)
        if objectmap is None:
            return None
        user = objectmap.object_for(userid)
        return user

    def get_user_by_email(self, email):
        context = self.context
        users = find_service(context, 'principals', 'users')
        for user in users.values():
            if user.email == email:
                return user

    def get_groupids(self, userid):
        user = self.get_user_by_userid(userid)
        if user is None:
            return None
        return user.groupids

def groupfinder(userid, request):
    """ A Pyramid authentication policy groupfinder callback that uses the
    Substance D user locator system to find group identifiers."""
    context = request.context
    adapter = request.registry.queryMultiAdapter((context, request),
                                                 IUserLocator)
    if adapter is None:
        adapter = DefaultUserLocator(context, request)
    return adapter.get_groupids(userid)

