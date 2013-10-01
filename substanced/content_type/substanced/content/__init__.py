import inspect

from pyramid.compat import is_nonstr_iter
from pyramid.location import lineage
import venusian

from ..event import ContentCreated
from ..util import (
    get_dotted_name,
    set_oid,
    get_factory_type,
    )
from .._compat import STRING_TYPES

_marker = object()

class ContentRegistry(object):
    """ An object accessible as ``registry.content`` (aka
    ``request.registry.content``, aka ``config.registry.content``) that
    contains information about Substance D content types."""
    def __init__(self, registry):
        self.registry = registry
        self.factory_types = {}
        self.content_types = {}
        self.meta = {}

    def add(self, content_type, factory_type, factory, **meta):
        """ Add a content type to this registry """
        self.factory_types[factory_type] = content_type
        self.content_types[content_type] = factory
        self.meta[content_type] = meta

    def all(self):
        """ Return all content types known my this registry as a sequence."""
        return list(self.content_types.keys())

    def create(self, content_type, *arg, **kw):
        """ Create an instance of ``content_type`` by calling its factory
        with ``*arg`` and ``**kw``.  If the meta of the content type has an
        ``after_create`` value, call it (if it's a string, it's assumed to be
        a method of the created object, and if it's a sequence, each value
        should be a string or a callable, which will be called in turn); then
        send a :class:`substanced.event.ContentCreatedEvent`.  Return the
        created object.

        If the key ``__oid`` is in the ``kw`` arguments, it will be used as
        the created object's oid.
        """
        factory = self.content_types[content_type]
        oid = kw.pop('__oid', None) # FBO dump system loader
        inst = factory(*arg, **kw)
        if oid is not None:
            set_oid(inst, oid)
        meta = self.meta[content_type].copy()
        aftercreate = meta.get('after_create')
        if aftercreate is not None:
            if not is_nonstr_iter(aftercreate):
                aftercreate = [aftercreate]
            for callback in aftercreate:
                if isinstance(callback, STRING_TYPES):
                    callback = getattr(inst, callback)
                callback(inst, self.registry)
        self.registry.subscribers(
            (ContentCreated(inst, content_type, meta), inst),
            None
            )
        return inst

    def metadata(self, resource, name, default=None):
        """
        Return a metadata value for the content type of ``resource`` based on
        the ``**meta`` value passed to
        :meth:`~substanced.content.ContentRegistry.add`.  If a value in that
        content type's metadata was passed using ``name`` as its name, the
        value will be returned, otherwise ``default`` will be returned.
        """
        content_type = self.typeof(resource)
        maybe = self.meta.get(content_type, {}).get(name)
        if maybe is not None:
            return maybe
        return default

    def typeof(self, resource):
        """ Return the content type of ``resource`` """
        factory_type = get_factory_type(resource)
        content_type = self.factory_types.get(factory_type)
        return content_type

    def istype(self, resource, content_type):
        """ Return ``True`` if ``resource`` is of content type
        ``content_type``, ``False`` otherwise."""
        return content_type == self.typeof(resource)

    def exists(self, content_type):
        """ Return ``True`` if ``content_type`` has been registered within
        this content registry, ``False`` otherwise."""
        return content_type in self.content_types.keys()

    def find(self, resource, content_type):
        """ Return the first object in the :term:`lineage` of the
        ``resource`` that supplies the ``content_type`` or ``None`` if no
        such object can be found."""
        for location in lineage(resource):
            if self.typeof(location) == content_type:
                return location

    def factory_type_for_content_type(self, content_type):
        """ Return the factory_type value for the content_type requested """
        for ftype, ctype in self.factory_types.items():
            if ctype == content_type:
                return ftype

# venusian decorator that marks a content factory
class content(object):
    """ Use as a decorator for a content factory (usually a class).  Accepts
    a content type, a factory type (optionally), and a set of meta keywords.
    These values mean the same thing as they mean for
    :func:`substanced.content.add_content_type`.  This decorator attaches
    information to the object it decorates which is used to call
    :func:`~substanced.content.add_content_type` during a :term:`scan`.
    """
    venusian = venusian
    def __init__(self, content_type, factory_type=None, **meta):
        self.content_type = content_type
        self.factory_type = factory_type
        self.meta = meta

    def __call__(self, wrapped):
        def callback(context, name, ob):
            config = context.config.with_package(info.module)
            add_content_type = getattr(config, 'add_content_type', None)
            # might not have been included
            if add_content_type is not None:
                add_content_type(
                    self.content_type,
                    wrapped,
                    factory_type=self.factory_type,
                    **self.meta
                    )
        info = self.venusian.attach(wrapped, callback, category='substanced')
        self.meta['_info'] = info.codeinfo # fbo "action_method"
        return wrapped

# venusian decorator that marks a service factory
class service(content):
    """
    This class is meant to be used as a decorator for a content factory that
    creates a service object (aka a service factory).  A service object is an
    instance of a content type that can be looked up by name and which
    provides a service to application code.  Services have well-known names
    within a folder.  For example, the ``principals`` service within a folder
    is 'the principals service', the ``catalog`` object within a folder is
    'the catalog service' and so on.

    This decorator accepts a content type, a factory type (optionally), and a
    set of meta keywords.  These values mean the same thing as they mean for
    the :class:`substanced.content.content` decorator and
    :func:`substanced.content.add_content_type`.  The decorator attaches
    information to the object it decorates which is used to call
    :func:`~substanced.content.add_content_type` during a :term:`scan`.

    There is only one difference between using the
    :class:`substanced.content.content` decorator and the
    :class:`substanced.service.service` decorator.  The ``service`` decorator
    honors a ``service_name`` keyword argument.  If this argument is passed,
    and a service already exists in the folder by this name, the service will
    not be shown as addable in the add-content dropdown in the SDI UI.
    """

    venusian = venusian
    
    def __init__(self, content_type, factory_type=None, **meta):
        meta['is_service'] = True
        content.__init__(self, content_type, factory_type=factory_type, **meta)

def add_content_type(config, content_type, factory, factory_type=None, **meta):
    """
    Configurator directive method which register a content type factory with
    the Substance D type system.  Call via ``config.add_content_type`` during
    Pyramid configuration phase.
    
    ``content_type`` is a hashable object (usually a string) representing the
    content type.

    ``factory`` is a class or function which produces a content instance.  It
    must be a :term:`global object` (e.g. it cannot be a callable which is a
    method of a class or a callable instance).  If ``factory`` is a function
    rather than a class, a :term:`factory wrapper` is used (see below).

    ``**meta`` is an arbitrary set of keywords associated with the content
    type in the content registry.

    Some of the keywords in ``**meta`` have special meaning:

    - If ``meta`` contains the keyword ``propertysheets``, the content type
      will obtain a tab in the SDI that allows users to manage its
      properties.

    - If ``meta`` contains the keyword ``catalog`` and its value is true, the
      object will be tracked in the Substance D catalog.

    Other keywords in ``meta`` will just be stored, and have no special
    meaning.

    ``factory_type`` is an optional argument that can be used if the same
    factory must be used for two different content types; it is used during
    content type lookup (e.g. :func:`substanced.util.get_content_type`) to
    figure out which content type a constructed object is an instance of; it
    only needs to be used when the same factory is used for two different
    content types.  Note that two content types cannot have the same factory
    type, unless it is ``None``.

    If ``factory_type`` is passed, the supplied factory will be wrapped in a
    factory wrapper which adds a ``__factory_type__`` attribute to the
    constructed instance.  The value of this attribute will be used to
    determine the content type of objects created by the factory.

    If the factory is a function rather than a class, a factory wrapper is
    used unconditionally.

    The upshot wrt to ``factory_type``: if your factory is a class and you
    pass a ``factory_type`` *or* if your factory is a function, you won't be
    able to successfully use the 'bare' factory callable to construct an
    instance of this content in your code, because the resulting instance
    will not have a ``__factory_type__`` attribute.  Instead, you'll be
    required to use :meth:`substanced.content.Content.create` to create an
    instance of the object with a proper ``__factory_type__`` attribute.
    But if your factory is a class, and you don't pass ``factory_type``
    (the 'garden path'), you'll be able to use the class' constructor directly
    in your code to create instances of your content objects, which is more
    convenient and easier to unit test.
    
    """

    # NB: we don't want to make a content registration mutate the factory
    # it's using because folks may need to override content construction.
    # For example, they might use the same factory but an alternate set of
    # metainformation and we don't want the metainformation claimed by the
    # unused content registration to be jammed onto the factory (which will
    # be a global).  Therefore we derive a factory as possible using a
    # wrapper, but only if absolutely necessary (if the factory is a class
    # and a factory type is supplied, or if the factory is a function).  We
    # avoid wrapping the factory in the garden path case, because it's so
    # convenient to be able to use the factory directly (via an import) in
    # user code.
    
    factory_type, derived_factory = _wrap_factory(factory, factory_type)

    def register_factory():
        config.registry.content.add(
            content_type, factory_type, derived_factory, **meta
            )

    discrim = ('sd-content-type', content_type)
    
    intr = config.introspectable(
        'substance d content types',
        discrim,
        content_type,
        'substance d content type',
        )
    intr['meta'] = meta
    intr['content_type'] = content_type
    intr['factory_type'] = factory_type
    intr['original_factory'] = factory
    intr['factory'] = derived_factory

    # conflict if two content type registrations have the same factory type
    config.action(('sd-factory-type', factory_type))
    
    config.action(discrim, callable=register_factory, introspectables=(intr,))

def add_service_type(config, content_type, factory, factory_type=None, **meta):
    """
    Configurator directive method which registers a service factory.  Call
    via ``config.add_service_type`` during Pyramid configuration phase.  All
    arguments mean the same thing as they mean for the
    :class:`substanced.content.add_content_type`.
    
    A service factory is a special kind of content factory.  A service
    factory creates a service object.  A service object is an instance of a
    content type that can be looked up by name and which provides a service
    to application code.  Services often have well-known names within the
    services folder.  For example, the ``principals`` object within a
    services folder is 'the principals service', the ``catalog`` object
    within a services folder is 'the catalog service' and so on.

    There is only one difference between using the
    :class:`substanced.content.add_content_type` function and the
    :class:`substanced.service.add_service_type` decorator. The
    ``add_service_type`` function honors a ``service_name`` keyword argument
    in its ``**meta``.  If this argument is passed, and a service already
    exists in a folder by this name, the service will not
    be shown as addable in the add-content dropdown in the SDI UI of the
    folder.
    """
    meta['is_service'] = True
    return add_content_type(
        config,
        content_type,
        factory,
        factory_type=factory_type,
        **meta
        )

def _wrap_factory(factory, factory_type):
    """ Wrap a factory in something that applies a factory type marker
    attribute to an instance created by the factory if necessary.  It's
    necessary if any of the following are true:

    - The factory is a class and factory_type is not None.

    - The factory is a function.

    If neither of these things is true, we return the factory unwrapped and
    return the dotted name of the factory as the factory name.
    """
 
    if inspect.isclass(factory) and factory_type is None:
        return get_dotted_name(factory), factory

    if factory_type is None:
        factory_type = get_dotted_name(factory)

    def factory_wrapper(*arg, **kw):
        inst = factory(*arg, **kw)
        inst.__factory_type__ = factory_type
        return inst
    
    factory_wrapper.__factory__ = factory
    return factory_type, factory_wrapper

class _ContentTypePredicate(object):
    def __init__(self, val, config):
        self.val = val
        self.registry = config.registry

    def text(self):
        return 'content_type = %s' % (self.val,)

    phash = text

    def __call__(self, context, request):
        cregistry =  getattr(self.registry, 'content', None)
        # include() might not have been called
        if cregistry is not None:
            return cregistry.istype(context, self.val)
        return False

def includeme(config): # pragma: no cover
    config.registry.content = ContentRegistry(config.registry)
    config.add_directive('add_content_type', add_content_type)
    config.add_directive('add_service_type', add_service_type)
    config.add_view_predicate('content_type', _ContentTypePredicate)
