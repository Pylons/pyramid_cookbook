import colander
import deform.widget
import deform_bootstrap.widget

from deform.i18n import _ as deform_i18n

from ..util import get_all_permissions

from pyramid.i18n import TranslationStringFactory

_ = TranslationStringFactory('substanced')

class CSRFToken(colander.SchemaNode):

    schema_type = colander.String
    widget = deform.widget.HiddenWidget()
    
    def validator(self, node, value):
        request = self.bindings['request']
        token = request.session.get_csrf_token()
        if value != token:
            raise colander.Invalid(
                node,
                _('Invalid cross-site scripting token'),
                value
                )

    def after_bind(self, node, kw):
        token = kw['request'].session.get_csrf_token()
        self.default = token
        
class RemoveCSRFMapping(colander.Mapping):
    def deserialize(self, node, cstruct):
        result = colander.Mapping.deserialize(self, node, cstruct)
        if result is colander.null:
            return result
        result.pop('_csrf_token_', None)
        return result

class Schema(colander.Schema):
    """
    A ``colander.Schema`` subclass which generates and validates a CSRF token
    automatically.  You must use it like so:

    .. code-block:: python

      from substanced.schema import Schema
      import colander

      class MySchema(Schema):
          my_value = colander.SchemaNode(colander.String())

    And in your application code, *bind* the schema, passing the request
    as a keyword argument:

    .. code-block:: python

      def aview(request):
          schema = MySchema().bind(request=request)

    In order for the CRSFSchema to work, you must configure a *session
    factory* in your Pyramid application.  This is usually done by
    Substance D itself, but may not be done for you in extremely custom
    configurations.
    """
    schema_type = RemoveCSRFMapping
    _csrf_token_ = CSRFToken()

class NameSchemaNode(colander.SchemaNode):
    """ Convenience Colander schemanode used to represent the name (aka
    ``__name__``) of an object in a propertysheet or add form which allows for
    customizing the detection of whether editing or adding is being done, and
    setting a max length for the name.

    By default it uses the context's ``check_name`` API to ensure that the name
    provided is valid, and limits filename length to a default of 100
    characters.  Some usage examples follow.
    
    This sets up the name_node to assume that it's in 'add' mode with the
    default 100 character max limit.::

      name_node = NameSchemaNode()

    This sets up the name_node to assume that it's in 'add' mode, and that the
    maximum length of the name provided is 20 characters::
    
      name_node = NameSchemaNode(max_len=20)

    This sets up the name_node to assume that it's in 'edit'
    mode (``check_name`` will be called on the **parent** of the bind
    context, not on the context itself)::
    
      name_node = NameSchemaNode(editing=True)

    This sets up the name_node to condition whether it's in edit mode on the
    result of a function::

      def i_am_editing(context, request):
          return request.registry.content.istype(context, 'Document')
    
      name_node = NameSchemaNode(editing=i_am_editing)
    """

    schema_type = colander.String
    max_len = 100
    editing = None

    def validator(self, node, value):
        context = self.bindings['context']
        request = self.bindings['request']
        editing = self.editing
        # By default, we are adding, meaning that we're checking the name
        # against the raw context which is assumed to be the parent
        # object that we're being added to.
        if editing is not None:
            if callable(editing):
                editing = editing(context, request)
            if editing:
                # However, if this is true, we are editing, not adding, which
                # means the raw context is the object itself, so we need to
                # walk up its parent chain to get the folder to call
                # ``check_name`` against.
                context = context.__parent__
        try:
            if editing:
                value = context.validate_name(value)
            else:
                value = context.check_name(value)
        except Exception as e:
            raise colander.Invalid(node, e.args[0], value)
        if len(value) > self.max_len:
            raise colander.Invalid(
                node,
                'Length of name must be %s characters or fewer' % self.max_len,
                value
                )

class PermissionsSchemaNode(colander.SchemaNode):
    """ A SchemaNode which represents a set of permissions; uses a widget which
    collects all permissions from the introspection system.  Deserializes to a
    set."""
    def schema_type(self): 
        return deform.Set(allow_empty=True)

    def _get_all_permissions(self, registry): # pragma: no cover (testing)
        return get_all_permissions(registry)

    @property
    def widget(self):
        request = self.bindings['request']
        permissions = self._get_all_permissions(request.registry)
        values = [(p, p) for p in permissions]
        return deform_bootstrap.widget.ChosenMultipleWidget(values=values)

    def validator(self, node, value):
        request = self.bindings['request']
        registry = request.registry
        permissions = self._get_all_permissions(registry)
        for perm in value:
            if not perm in permissions:
                raise colander.Invalid(
                    node, 'Unknown permission %s' % value, value
                    )

class IdSet(object):
    def _check_iterable(self, node, value):
        if not hasattr(value, '__iter__'):
            raise colander.Invalid(
                node,
                deform_i18n('${value} is not iterable',
                            mapping={'value':value})
                )
        
    def serialize(self, node, value):
        if value is colander.null:
            return value
        self._check_iterable(node, value)
        return [str(x) for x in value]

    def deserialize(self, node, value):
        if value is colander.null:
            return value
        self._check_iterable(node, value)
        return [int(x) for x in value]

    def cstruct_children(self, node, cstruct):
        return []

class MultireferenceIdSchemaNode(colander.SchemaNode):
    schema_type = IdSet

    def _get_choices(self):
        context = self.bindings['context']
        request = self.bindings['request']
        return self.choices_getter(context, request) # passed to SchemaNode ctor

    @property
    def widget(self):
        values = self._get_choices()
        return deform_bootstrap.widget.ChosenMultipleWidget(values=values)
