import colander
from zope.interface import implementer

from pyramid.exceptions import ConfigurationError
from pyramid.security import (
    Allow,
    ALL_PERMISSIONS,
    )

from ..interfaces import IRoot

from ..content import content
from ..folder import Folder
from ..objectmap import ObjectMap
from ..property import PropertySheet
from ..schema import Schema
from ..util import (
    get_oid,
    set_acl,
    )

class RootSchema(Schema):
    """ The schema representing site properties. """
    sdi_title = colander.SchemaNode(
        colander.String(),
        missing='',
        )

class RootPropertySheet(PropertySheet):
    schema = RootSchema()

@content(
    'Root',
    icon='icon-home',
    propertysheets = (
        ('', RootPropertySheet),
        ),
    after_create='after_create',
    )
@implementer(IRoot)
class Root(Folder):
    """ An object representing the root of a Substance D application (the
    object represented in the root of the SDI).  It is a subclass of
    :class:`substanced.folder.Folder`.

    When created as the result of ``registry.content.create``, an instance of
    a Root will contain a ``principals`` service.  The principals service
    will contain a user whose name is specified via the
    ``substanced.initial_login`` deployment setting with a password taken
    from the ``substanced.initial_password`` setting.  This user will also be
    a member of an ``admins`` group.  The ``admins`` group will be granted
    the ``ALL_PERMISSIONS`` special permission in the root.

    If this class is created by hand, its ``after_create`` method must be
    called manually to create its objectmap, the services, the user, and the
    group.
    """
    sdi_title = ''

    def after_create(self, inst, registry):
        # NB: creation of objectmap deferred until after creation to allow for
        # dump system loader to successfully load a root object; if this were
        # done in __init__, the oid of the root object would not be resettable,
        # and loaded references to the root object could not be resolved.
        self.__objectmap__ = ObjectMap(self)
        self.__objectmap__.add(self, ('',))

        catalogs = registry.content.create('Catalogs')
        catalogs.__sdi_deletable__ = False
        self.add_service('catalogs', catalogs)
        catalog = catalogs.add_catalog('system')
        # self-index so catalogs service shows up in folder contents
        oid = get_oid(catalogs)
        catalog.index_doc(oid, catalogs)
        settings = registry.settings
        password = settings.get('substanced.initial_password')
        if password is None:
            raise ConfigurationError(
                'You must set a substanced.initial_password '
                'in your configuration file'
                )
        login = settings.get('substanced.initial_login', 'admin')
        email = settings.get('substanced.initial_email', 'admin@example.com')

        principals = registry.content.create('Principals')
        # prevent SDI deletion/renaming of root principals service
        principals.__sdi_deletable__ = False
        self.add_service('principals', principals, registry=registry)
        user = principals.add_user(login, password, email, registry=registry)
        admins = principals.add_group('admins', registry=registry)
        admins.memberids.connect([user])

        locks = registry.content.create('Lock Service')
        # prevent SDI deletion/renaming of locks service
        locks.__sdi_deletable__ = False
        self.add_service('locks', locks, registry=registry)

        self.sdi_title = 'Substance D'

        set_acl(
            self,
            [(Allow, get_oid(admins), ALL_PERMISSIONS)],
            registry=registry,
            )
        
