================
Defining Content
================

:term:`Resource` is the term that Substance D uses to describe an object
placed in the :term:`resource tree`.  

Ideally, all resources in your resource tree will be :term:`content`. "Content"
is the term that Substance D uses to describe resource objects that are
particularly well-behaved when they appear in the SDI management interface.
The Substance D management interface (aka :term:`SDI`) is a set of views
imposed upon the resource tree that allow you to add, delete, change and
otherwise manage resources.

You can convince the management interface that your particular resources are
content.  To define a resource as content, you need to associate a resource
with a :term:`content type`.

.. _registering_content:

Registering Content
===================

In order to add new content to the system, you need to associate a
:term:`resource factory` with a :term:`content type`.  A resource factory that
generates content must have these properties:

- It must be a class, or a factory function that returns an instance of a
  resource class.

- Instances of the resource class must be *persistent* (it must derive from
  the ``persistent.Persistent`` class or a class that derives from Persistent
  such as :class:`substanced.folder.Folder`).

- The resource class or factory must be decorated with the ``@content``
  decorator, or must be added at configuration time via
  ``config.add_content_type``.

- It must have a *type*.  A type acts as a globally unique categorization
  marker, and allows the content to be constructed, enumerated, and
  introspected by various Substance D UI elements such as "add forms", and
  queries by the management interface for the icon name of a resource.  A
  type can be any hashable Python object, but it's most often a string.

Here's an example which defines a content resource factory as a class:

.. code-block:: python

   # in a module named blog.resources

   from persistent import Persistent
   from substanced.content import content

   @content('Blog Entry')
   class BlogEntry(Persistent):
       def __init__(self, title='', body=''):
           self.title = title
           self.body = body

Here's an example of defining a content resource factory using a function
instead:

.. code-block:: python

   # in a module named blog.resources

   from persistent import Persistent
   from substanced.content import content

   class BlogEntry(Persistent):
       def __init__(self, title, body):
           self.title = title
           self.body = body

   @content('Blog Entry')
   def make_blog_entry(title='', body=''):
       return BlogEntry(title, body)

When a resource factory is not a class, Substance D will wrap the resource
factory in something that changes the resource object returned from the
factory.  In the above case, the BlogEntry instance returned from
``make_blog_entry`` will be changed; its ``__factory_type__`` attribute will be
mutated.

Notice that when we decorate a resource factory class with ``@content``, and
the class' ``__init__`` function takes arguments, we provide those arguments
with default values.  This is mandatory if you'd like your content objects to
participate in a "dump".  Dumping a resource requires that the resource be
creatable without any mandatory arguments.  It's a similar story if our factory
is a function; the function decorated by the ``@content`` decorator should
provide defaults to any argument.  In general, a resource factory can take
arguments, but each parameter of the factory's callable should be given a
default value.  This also means that all arguments to a resource factory
should be keyword arguments, and not positional arguments.

In order to activate a ``@content`` decorator, it must be *scanned* using the
Pyramid ``config.scan()`` machinery:

.. code-block:: python

   # in a module named blog.__init__

   from pyramid.config import Configurator

   def main(global_config, **settings):
       config = Configurator()
       config.include('substanced')
       config.scan('blog.resources')
       # .. and so on ...

Instead of using the ``@content`` decorator, you can alternately add a
content resource imperatively at configuration time using the
``add_content_type`` method of the Configurator:

.. code-block:: python

   # in a module named blog.__init__

   from pyramid.config import Configurator
   from .resources import BlogEntry

   def main(global_config, **settings):
       config = Configurator()
       config.include('substanced')
       config.add_content_type('Blog Entry', BlogEntry)

This does the same thing as using the ``@content`` decorator, but you don't
need to ``scan()`` your resources if you use ``add_content_type`` instead of
the ``@content`` decorator.

Once a content type has been defined (and scanned, if it's been defined using
a decorator), an instance of the resource can be constructed from within a
view that lives in your application:

.. code-block:: python

   # in a module named blog.views

   from pyramid.httpexceptions import HTTPFound

   @view_config(name='add_blog_entry', request_method='POST')
   def add_blogentry(request):
       title = request.POST['title']
       body = request.POST['body']
       entry = request.registry.content.create('Blog Entry', title, body)
       context['title'] = entry
       return HTTPFound(request.resource_url(entry))

The arguments passed to ``request.registry.content.create`` must start with
the content type, and must be followed with whatever arguments are required
by the resource factory.

Creating an instance of content this way isn't particularly more useful than
creating an instance of the resource object by calling its class ``__init__``
directly unless you're building a highly abstract system.  But even if you're
not building a very abstract system, types can be very useful.  For instance,
types can be enumerated:

.. code-block:: python

   # in a module named blog.views

   @view_config(name='show_types', renderer='show_types.pt')
   def show_types(request):
       all_types = request.registry.content.all()
       return {'all_types':all_types}

``request.registry.content.all()`` will return all the types you've defined
and scanned.

Metadata
========

A content's type can be associated with metadata about that type, including the
content type's name, its icon in the SDI management interface, an add view
name, and other things.  Pass arbitrary keyword arguments to the ``@content``
decorator or ``config.add_content_type`` to specify metadata.

Names
-----

You can associate a content type registration with a name that shows up when
someone attempts to add such a piece of content using the SDI management
interface "Add" tab by passing a ``name`` keyword argument to ``@content``
or ``config.add_content_type``.

.. code-block:: python

   # in a module named blog.resources

   from persistent import Persistent
   from substanced.content import content

   @content('Blog Entry', name='Cool Blog Entry')
   class BlogEntry(Persistent):
       def __init__(self, title='', body=''):
           self.title = title
           self.body = body

Once you've done this, the "Add" tab in the SDI management interface will
show your content as addable using this name instead of the type name.

Icons
-----

You can associate a content type registration with a management view icon by
passing an ``icon`` keyword argument to ``@content`` or ``add_content_type``.

.. code-block:: python

   # in a module named blog.resources

   from persistent import Persistent
   from substanced.content import content

   @content('Blog Entry', icon='icon-file')
   class BlogEntry(Persistent):
       def __init__(self, title='', body=''):
           self.title = title
           self.body = body

Once you've done this, content you add to a folder in the sytem will display
the icon next to it in the contents view of the management interface and in
the breadcrumb list.  The available icon names are listed at
http://twitter.github.com/bootstrap/base-css.html#icons .

You can also pass a callback as an ``icon`` argument:

.. code-block:: python

   from persistent import Persistent
   from substanced.content import content

   def blogentry_icon(context, request):
       if context.body:
           return 'icon-file'
       else:
           return 'icon-gift'

   @content('Blog Entry', icon=blogentry_icon)
   class BlogEntry(Persistent):
       def __init__(self, title='', body=''):
           self.title = title
           self.body = body

A callable used as ``icon`` must accept two arguments: ``context`` and
``request``.  ``context`` will be an instance of the type and ``request`` will
be the current request; your callback will be called at the time the folder
view is drawn.  The callable should return either an icon name or ``None``.
For example, the above ``blogentry_icon`` callable tells the SDI to use an icon
representing a file if the blogentry has a body, otherwise show an icon
representing gift.

Add Views
---------

You can associate a content type with a view that will allow the type to be
added by passing the name of the add view as a keyword argument to
``@content`` or ``add_content_type``.

.. code-block:: python

   # in a module named blog.resources

   from persistent import Persistent
   from substanced.content import content

   @content('Blog Entry', add_view='add_blog_entry')
   class BlogEntry(Persistent):
       def __init__(self, title='', body=''):
           self.title = title
           self.body = body

Once you've done this, if the button is clicked in the "Add" tab for this
content type, the related view will be presented to the user.

You can also pass a callback as an ``add_view`` argument:

.. code-block:: python

   from persistent import Persistent
   from substanced.content import content
   from substanced.folder import Folder

   def add_blog_entry(context, request):
       if request.registry.content.istype(context, 'Blog'):
           return 'add_blog_entry'

   @content('Blog')
   class Blog(Folder):
       pass

   @content('Blog Entry', add_view=add_blog_entry)
   class BlogEntry(Persistent):
       def __init__(self, title='', body=''):
           self.title = title
           self.body = body

A callable used as ``add_view`` must accept two arguments: ``context`` and
``request``.  ``context`` will be the potential parent object of the content
(when the SDI folder view is drawn), and ``request`` will be the current
request at the time the folder view is drawn.  The callable should return
either a view name or ``None`` if the content should not be addable in this
circumstance.  For example, the above ``add_blog_entry`` callable asserts that
Blog Entry content should only be addable if the context we're adding to is of
type Blog; it returns None otherwise, signifying that the content is not
addable in this circumstance.

Obtaining Metadata About a Content Object's Type
------------------------------------------------

``request.registry.content.metadata(blogentry, 'icon')``

  Will return the icon for the blogentry's content type or ``None`` if it
  does not exist.

``request.registry.content.metadata(blogentry, 'icon', 'icon-file')``

  Will return the icon for the blogentry's content type or ``icon-file`` if
  it does not exist.

Affecting Content Creation
==========================

In some cases you might want your resource to perform some actions that
can only take place after it has been seated in its container and but
before the creation events have fired. The ``@content`` decorator and
``add_content_type`` method both support an ``after_create`` argument,
pointed at a callable.

For example:

.. code-block:: python

    @content(
        'Document',
        icon='icon-align-left',
        add_view='add_document',
        propertysheets = (
            ('Basic', DocumentPropertySheet),
            ),
        after_create='after_creation'
        )
    class Document(Persistent):

        name = renamer()

        def __init__(self, title, body):
            self.title = title
            self.body = body

        def after_creation(self, inst, registry):
            pass

If the value provided for ``after_create`` is a string, it's assumed to
be a method of the created object. If it's a sequence, each value
should be a string or a callable, which will be called in turn. The
callable(s) are passed the instance being created and the registry.
Afterwards, :class:`substanced.event.ContentCreatedEvent` is emitted.

Construction of the root folder in Substance D is a special case. Most
Substance D applications will start with:

.. code-block:: python

    from substanced.db import root_factory
    def main(global_config, **settings):
        """ This function returns a Pyramid WSGI application.
        """
        config = Configurator(settings=settings, root_factory=root_factory)

The :py:func:`substanced.db.root_factory` callable contains the following
line:

.. code-block:: python

    app_root = registry.content.create('Root')

In many cases you want to perform some extra work on the ``Root``. For
example, you might want to create a catalog with indexes. Substance D
emits an event when the root is created, so you can subscribe to that
event and perform some actions:

.. code-block:: python

    from substanced.root import Root
    from substanced.event import subscribe_created
    from substanced.catalog import Catalog

    @subscribe_created(Root)
    def root_created(event):
        catalog = Catalog()
        event.object.add_service('catalog', catalog)
        catalog.update_indexes('system', reindex=True)
        catalog.update_indexes('sdidemo', reindex=True)


Names and Renaming
==================

A resource's "name" (``__name__``) is important to the system in
Substance D. For example, traversal uses the value in URLs and paths to
walk through hierarchy. Containers need to know when a resource's
``__name__`` changes.

To help support this, Substance D provides
:py:func:`substanced.util.renamer`. You use it as a class attribute
wrapper on resources that want "managed" names. These resources then
gain a ``name`` attribute with a getter/setter from ``renamer``.
Getting the ``name`` returns the ``__name__``. Setting ``name`` grabs
the container and calls the ``rename`` method on the folder.

For example:

.. code-block:: python

    class Document(Persistent):
        name = renamer()

Special Colander Support
========================

Forms and schemas for resources become pretty easy in Substance D. To
make it easier for forms to interact with the Substance D machinery,
it includes some special Colander schema nodes you can use on your forms.

``NameSchemaNode``
------------------

If you want your form to affect the ``__name__`` of a resource,
certain constraints become applicable. These constraints might be
different, so you might want to know if you are on an add form versus
an edit form. :py:class:`substanced.schema.NameSchemaNode` provides a
schema node and default widget that bundles up the common rules for this.
For example:

.. code-block:: python

    class BlogEntrySchema(Schema):
        name = NameSchemaNode()

The above provides the basics of support for editing a name property,
especially when combined with the ``renamer()`` utility mentioned above.

By default the name is limited to 100 characters. ``NameSchemaNode``
accepts an argument that can set a different limit:

.. code-block:: python

    class BlogEntrySchema(Schema):
        name = NameSchemaNode(max_len=20)

You can also provide an ``editing`` argument, either as a boolean or a
callable which returns a boolean, which determines whether the form is
rendered in "editing" mode. For example:

.. code-block:: python

    class BlogEntrySchema(Schema):
        name = NameSchemaNode(
            editing=lambda c, r: r.registry.content.istype(c, 'BlogEntry')
            )

``PermissionSchemaNode``
------------------------

A form might want to allow selection of zero or more permissions from
the site's defined list of permissions.
:py:class:`PermissionSchemaNode` collects the possible
state from the system, the currently-assigned values, and presents a
widget that manages the values.

``MultireferenceIdSchemaNode``
------------------------------

References are a very powerful facility in Substance D. Naturally
you'll want your application's forms to assign references.
:py:class:`MultireferenceIdSchemaNode` gives a schema node and widget
that allows multiple selections of possible values in the system for
references, including the current assignments.

As an example, the built-in :py:class:`substanced.principal.UserSchema`
uses this schema node:

.. code-block:: python

    class UserSchema(Schema):
        """ The property schema for :class:`substanced.principal.User`
        objects."""
        groupids = MultireferenceIdSchemaNode(
            choices_getter=groups_choices,
            title='Groups',
            )

Overriding Existing Content Types
=================================

Perhaps you would like to slightly adjust an existing content type,
such as ``Folder``, without re-implementing it. For exampler,
perhaps you would like to override just the ``add_view`` and provide
your own view, such as:

.. code-block:: python

    @mgmt_view(
        context=IFolder,
        name='my_add_folder',
        tab_condition=False,
        permission='sdi.add-content',
        renderer='substanced.sdi:templates/form.pt'
    )
    class MyAddFolderView(AddFolderView):

        def before(self, form):
            # Perform some custom work before validation
            pass

With this you can override any of the view predicates (such as
``permission``) and override any part of the form handling (such as
adding a ``before`` that performs some custom processing.)

To make this happen, you can re-register, so to speak,
the content type during startup:

.. code-block:: python

    from substanced.folder import Folder
    from .views import MyAddFolderView
    config.add_content_type('Folder', Folder,
                            add_view='my_add_folder',
                            icon='icon-folder-close')

This, however, keeps the same content type class. You can also go
further by overriding the content type definition itself:

.. code-block:: python

    @content(
        'Folder',
        icon='icon-folder-close',
        add_view='my_add_folder',
    )
    @implementer(IFolder)
    class MyFolder(Folder):

        def send_email(self):
            pass

The class for the 'Folder' content type has now been replaced. Instead
of ``substanced.folder.Folder`` it is ``MyFolder``.

.. note::

    Overriding a content type is a pain-free way to make a custom
    ``Root`` object. You could supply your own ``root_factory`` to
    the ``Configurator`` but that means replicating all its rather
    complicated goings-on. Instead, provide your own content type
    factory, as above, for ``Root``.

Affecting the Tab Order for Management Views
============================================

The ``tab_order`` parameter overrides the mgmt_view tab settings,
for a content type, with a sequence of view names that should be
ordered (and everything not in the sequence, after.)

Handling Content Events
=======================

Adding and modifying data related to content is, thanks to the framework,
easy to do. Sometimes, though, you want to intervene and, for example,
perform some extra work when content resources are added. Substance D
has several framework events you can subscribe to using
:ref:`Pyramid events <pyramid:events_chapter>`.

The :py:mod:`substanced.events` module imports these events as interfaces
from :py:mod:`substanced.interfaces` and then provides decorator
subscribers as convenience for each:

- :py:class:`substanced.interfaces.IObjectAdded` as subscriber
  ``@subscriber_added``

- :py:class:`substanced.interfaces.IObjectWillBeAdded` as subscriber
  ``@subscriber_will_be_added``

- :py:class:`substanced.interfaces.IObjectRemoved` as subscriber
  ``@subscriber_removed``

- :py:class:`substanced.interfaces.IObjectWillBeRemoved` as subscriber
  ``@subscriber_will_be_removed``

- :py:class:`substanced.interfaces.IObjectModified` as subscriber
  ``@subscriber_modified``

- :py:class:`substanced.interfaces.IACLModified` as subscriber
  ``@subscriber_acl_modified``

- :py:class:`substanced.interfaces.IContentCreated` as subscriber
  ``@subscriber_created``

As an example, the
:py:func:`substanced.principal.subscribers.user_added` function is a
subscriber to the ``IObjectAdded`` event:

.. code-block:: python

    @subscribe_added(IUser)
    def user_added(event):
        """ Give each user permission to change their own password."""
        if event.loading: # fbo dump/load
            return
        user = event.object
        registry = event.registry
        set_acl(
            user,
            [(Allow, get_oid(user), ('sdi.view', 'sdi.change-password'))],
            registry=registry,
            )

As with the rest of Pyramid, you can do imperative configuration if you
don't like decorator-based configuration, using
``config.add_content_subscriber`` Both the declarative and imperative
forms result in :func:`substanced.event.add_content_subscriber`.

.. note::

    While the event subscriber is de-coupled logically from the action
    that triggers the event, both the action and the subscriber run
    in the same transaction.

The ``IACLModified`` event (and ``@subscriber_acl_modified`` subscriber)
is used internally to Substance D to re-index information the system
catalog's ACL index. Substance D also uses this event to maintain
references between resources and principals. Substance D applications
can use this in different ways, for example recording a security audit
trail on security changes.

Sometimes when you perform operations on objects you don't want to
perform the standard events. For example, in folder contents you can
select a number of resources and move them to another folder. Normally
this would fire content change events that re-index the files. This is
fairly pointless: the content of the file hasn't changed.

If you looked at the interface for one of the content events,
you would see some extra information supported. For example, in
:py:class:`substanced.interfaces.IObjectWillBeAdded`:

.. code-block:: python

    class IObjectWillBeAdded(IObjectEvent):
        """ An event type sent when an before an object is added """
        object = Attribute('The object being added')
        parent = Attribute('The folder to which the object is being added')
        name = Attribute('The name which the object is being added to the folder '
                         'with')
        moving = Attribute('None or the folder from which the object being added '
                           'was moved')
        loading = Attribute('Boolean indicating that this add is part of a load '
                            '(during a dump load process)')
        duplicating = Attribute('The object being duplicated or ``None``')

``moving``, ``loading``, and ``duplicating`` are flags that can be set
on the event when certain actions are triggered. These help in cases
such as the one above: certain subscribers might want "flavors" of
standard events and, in some cases, handle the event in a different
way. This helps avoid lots of special-case events or the need for a
hierarchy of events.

Thus in the case above, the catalog subscriber can see that the changes
triggered by the event where in the special case of "moving". This can
be seen in :attr:`substanced.catalog.subscribers.object_added`.
