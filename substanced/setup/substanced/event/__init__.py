from functools import update_wrapper

import venusian

from pyramid.decorator import reify

from zope.interface import (
    implementer,
    Interface,
    )

from ..interfaces import (
    IObjectAdded,
    IObjectWillBeAdded,
    IObjectRemoved,
    IObjectWillBeRemoved,
    IObjectModified,
    IACLModified,
    IContentCreated,
    ILoggedIn,
    IRootAdded,
    )

from ..util import find_objectmap
    
class _ObjectEvent(object):
    pass
        

@implementer(IObjectAdded)
class ObjectAdded(_ObjectEvent):
    """ An event sent just after an object has been added to a folder.  """
    def __init__(
        self,
        object,
        parent,
        name,
        duplicating=False,
        moving=False,
        loading=False,
        ):
        self.object = object
        self.parent = parent
        self.name = name
        self.duplicating = duplicating
        self.moving = moving
        self.loading = loading

@implementer(IObjectWillBeAdded)
class ObjectWillBeAdded(_ObjectEvent):
    """ An event sent just before an object has been added to a folder.  """
    def __init__(
        self,
        object,
        parent,
        name,
        duplicating=False,
        moving=False,
        loading=False,
        ):
        self.object = object
        self.parent = parent
        self.name = name
        self.duplicating = duplicating
        self.moving = moving
        self.loading = loading

@implementer(IObjectRemoved)
class ObjectRemoved(object):
    """ An event sent just after an object has been removed from a folder."""
    def __init__(
        self,
        object,
        parent,
        name,
        removed_oids,
        moving=False,
        loading=False,
        ):
        self.object = object
        self.parent = parent
        self.name = name
        self.removed_oids = removed_oids
        self.moving = moving
        self.loading = loading

@implementer(IObjectWillBeRemoved)
class ObjectWillBeRemoved(object):
    """ An event sent just before an object has been removed from a folder."""
    def __init__(
        self,
        object,
        parent,
        name,
        moving=False,
        loading=False,
        ):
        self.object = object
        self.parent = parent
        self.name = name
        self.moving = moving
        self.loading = loading

    @reify
    def removed_oids(self):
        """ Helper property that caches oids that will be removed as the result
        of this event.  Will return an empty sequence if objectmap cannot be
        found on self.parent."""
        objectmap = find_objectmap(self.parent)
        if objectmap is None:
            return []
        return objectmap.pathlookup(self.object)

@implementer(IObjectModified)
class ObjectModified(object): # pragma: no cover
    """ An event sent when an object has been modified."""
    def __init__(self, object):
        self.object = object

@implementer(IACLModified)
class ACLModified(object): # pragma: no cover
    def __init__(self, object, old_acl, new_acl):
        self.object = object
        self.old_acl = old_acl
        self.new_acl = new_acl

@implementer(IContentCreated)
class ContentCreated(object):
    def __init__(self, object, content_type, meta):
        self.object = object
        self.content_type = content_type
        self.meta = meta

@implementer(ILoggedIn)
class LoggedIn(object):
    def __init__(self, login, user, context, request):
        self.login = login
        self.user = user
        self.context = context
        self.request = request

@implementer(IRootAdded)
class RootAdded(object):
    def __init__(self, object):
        self.object = object
        
# subscriber decorators, e.g.
# @subscribe_added(MyContent)
# def foo(event):
#     ....

class _Subscriber(object):
    venusian = venusian # for testing
    def __call__(self, wrapped):
        self.venusian.attach(wrapped, self.register, category='substanced')
        return wrapped

class _SimpleSubscriber(_Subscriber):
    def __init__(self, **predicates):
        self.predicates = predicates

    def register(self, scanner, name, wrapped):
        registry = scanner.config.registry
        def wrapper(event, *arg): # *arg ignored, XXX it can go away pyr1.4b1+
            event.registry = registry
            return wrapped(event)
        if hasattr(wrapped, '__name__'):
            update_wrapper(wrapper, wrapped)
        wrapper.wrapped = wrapped
        scanner.config.add_subscriber(wrapper, self.event, **self.predicates)

class _FolderEventSubscriber(_Subscriber):
    def __init__(self, obj=None, container=None, **predicates):
        if obj is None:
            obj = Interface
        if container is None:
            container = Interface
        self.obj = obj
        self.container = container
        self.predicates = predicates

    def register(self, scanner, name, wrapped):
        add_content_subscriber = getattr(
            scanner.config, 'add_content_subscriber', None)
        if add_content_subscriber is not None:
            add_content_subscriber(
                wrapped,
                [self.event, self.obj, self.container],
                **self.predicates
                )

# content events have no container associated

class _ContentEventSubscriber(_Subscriber):
    def __init__(self, obj=None, **predicates):
        if obj is None:
            obj = Interface
        self.obj = obj
        self.predicates = predicates

    def register(self, scanner, name, wrapped):
        add_content_subscriber = getattr(
            scanner.config, 'add_content_subscriber', None)
        if add_content_subscriber is not None:
            add_content_subscriber(
                wrapped,
                [self.event, self.obj],
                **self.predicates
                )

class subscribe_added(_FolderEventSubscriber):
    """ Decorator for registering an object added event subscriber
    (a subscriber for ObjectAdded)."""
    event = IObjectAdded

class subscribe_removed(_FolderEventSubscriber):
    """ Decorator for registering an object removed event subscriber
    (a subscriber for ObjectRemoved)."""
    event = IObjectRemoved

class subscribe_will_be_added(_FolderEventSubscriber):
    """ Decorator for registering an object will-be-added event subscriber
    (a subscriber for ObjectWillBeAdded)."""
    event = IObjectWillBeAdded

class subscribe_will_be_removed(_FolderEventSubscriber):
    """ Decorator for registering an object will-be-removed event subscriber
    (a subscriber for ObjectWillBeRemoved)."""
    event = IObjectWillBeRemoved

class subscribe_modified(_ContentEventSubscriber):
    """ Decorator for registering an object modified event subscriber
    (a subscriber for ObjectModified)."""
    event = IObjectModified

class subscribe_acl_modified(_ContentEventSubscriber):
    """ Decorator for registering an acl modified event subscriber
    (a subscriber for ObjectModified)."""
    event = IACLModified

class subscribe_created(_ContentEventSubscriber):
    """ Decorator for registering an object created event subscriber
    (a subscriber for ContentCreated)."""
    event = IContentCreated

class subscribe_logged_in(_SimpleSubscriber):
    """ Decorator for registering an event listener for when a user is logged
    in """
    event = ILoggedIn

class subscribe_root_added(_SimpleSubscriber):
    """ Decorator for registering an event listener for when a root object
    has a database connection """
    event = IRootAdded

def add_content_subscriber(config, subscriber, iface=None, **predicates):
    """ Configurator directive that works like Pyramid's ``add_subscriber``,
    except it wraps the subscriber in something that first adds the
    ``registry`` attribute to the event being sent before the wrapped
    subscriber is called."""
    registry = config.registry
    def wrapper(event, *arg): # *arg ignored, XXX it can go away pyr1.4b1+
        event.registry = registry
        return subscriber(event)
    if hasattr(subscriber, '__name__'):
        update_wrapper(wrapper, subscriber)
    wrapper.wrapped = subscriber
    config.add_subscriber(wrapper, iface, **predicates)

class _ContentTypePredicate(object):
    def __init__(self, val, config):
        self.val = val
        self.registry = config.registry

    def phash(self):
        return 'content_type = %s' % (self.val,)

    text = phash

    def __call__(self, event, *arg):
        # NB: accept *arg so we can be used as either a folder event
        # predicate or as a content event predicate.  (yes, it's lame).
        # XXX *arg can go away once a Pyramid 1.4 final is out (or if used
        # against Pyramid 1.4b1+)
        return self.registry.content.istype(event.object, self.val)
    
def includeme(config): # pragma: no cover
    config.add_directive('add_content_subscriber', add_content_subscriber)
    config.add_subscriber_predicate('content_type', _ContentTypePredicate)
