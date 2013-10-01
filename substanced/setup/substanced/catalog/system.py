from ..util import get_interfaces

from .factories import (
    Field,
    Keyword,
    Path,
    Allowed,
    Text,
    )

from . import (
    catalog_factory,
    indexview,
    indexview_defaults,
    )

from ..interfaces import (
    MODE_DEFERRED,
    )
from ..util import get_content_type

@indexview_defaults(catalog_name='system')
class SystemIndexViews(object):
    def __init__(self, resource):
        self.resource = resource

    @indexview()
    def interfaces(self, default):
        """ Return a set of all interfaces implemented by the object, including
        inherited interfaces (but no classes).
        """
        return get_interfaces(self.resource, classes=False)

    @indexview()
    def name(self, default):
        """ Returns the ``__name__`` of the object or ``default`` if the object
        has no ``__name__``."""
        name = getattr(self.resource, '__name__', default)
        if name is None: # deal with name = None at root
            return default
        return name

    @indexview()
    def content_type(self, default):
        """ Returns the Substance D content type of the resource """
        result = get_content_type(self.resource)
        if result is None:
            return default
        return result
 
    @indexview()
    def text(self, default):
        """ Returns a derivation of the name for text indexing.  If name has no
        separator characters in it, the function will return the name
        unchanged.  Otherwise it will return the name plus the derivation of
        splitting the name on the separator characters.  The separator
        characters are: ``, . - _``.  For example, if the name is
        ``foo-bar_baz.pt,foz``, the return value will be ``foo-bar_baz.pt,foz
        foo bar baz pt foz``.  This allows for the most common lookups of
        partial index values in the filter box."""
        name = self.name(default)
        if name is default:
            return default
        if not hasattr(name, 'split'):
            return name
        val = name
        for char in (',', '-', '_', '.'):
            val = ' '.join([x.strip() for x in val.split(char)])
        if val != name:
            return name + ' ' + val
        return name

@catalog_factory('system')
class SystemCatalogFactory(object):
    """ The default set of Substance D system indexes.

    - path (a PathIndex)

      Represents the path of the content object.

    - name (a FieldIndex)

      Represents the local name of the content object.

    - interfaces (a KeywordIndex)

      Represents the set of interfaces possessed by the content object.

    - content_type (a FieldIndex)

      Represents the Substance D content type of an added object.

    - allowed (an AllowedIndex)

      Represents the set of principals with the ``sdi.view`` or ``view``
      permission against a content object.

    - text (a TextIndex)

      Indexes text used for the Substance D folder contents filter box.

    """
    path = Path()

    # name is MODE_ATCOMMIT for next-request folder contents consistency
    name = Field()

    # interfaces is MODE_ATCOMMIT because code which creates one may
    # need to access it immediately.
    interfaces = Keyword()

    # allowed is MODE_ATCOMMIT for next-request folder contents consistency
    allowed = Allowed(
        permissions=('sdi.view', 'view'),
        )

    text = Text(action_mode=MODE_DEFERRED)

    # content_type is MODE_ATCOMMIT because code which creates one may
    # need to access it immediately.
    content_type = Field()
