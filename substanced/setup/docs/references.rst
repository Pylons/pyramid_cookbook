==========
References
==========

Objects that live in the Substance D resource tree can be related to one
another using references.

The most user-visible facet of references is the SDI "References" tab, which is
presented to SDI admin users when the object they're looking at is involved in
a reference relation.  For example, you'll notice that the built-in user and
group implementations already have references to each other, and you can visit
their References tabs to see them.  Likewise, when you use the Security tab to
change the ACL associated with an object, and include in the ACL a user or
group that lives in the principals folder, a relation is formed between the
ACL-bearing object and the principal.  So, as you can see, references aren't
just for application developers; Substance D itself uses references under the
hood to do its job too.

A reference has a type and a direction.  A reference is formed using methods of
the :term:`object map`.

.. code-block:: python

   from substanced.interfaces import ReferenceType
   from substanced.objectmap import find_objectmap

   class ContextToRoot(ReferenceType):
       pass

   def connect_reference(context, request):
       objectmap = find_objectmap(context)
       root = request.root
       objectmap.connect(context, root, ContextToRoot)

A reference type is a class (not an instance) that inherits from
:class:`substanced.interfaces.ReferenceType`.  The reference's name should
indicate its directionality.

.. warning::

   One caveat: reference types are *pickled*, so if you move a reference type
   from one location to another, you'll have to leave behind a backwards
   compatibility import in its original location "forever", so choose its name
   and location wisely.  We recommend that you place it in an ``interfaces.py``
   file in your project.

A reference can be removed using the object map too:

.. code-block:: python

   from substanced.interfaces import ReferenceType
   from substanced.objectmap import find_objectmap

   class ContextToRoot(ReferenceType):
       pass

   def disconnect_reference(context, request):
       objectmap = find_objectmap(context)
       root = request.root
       objectmap.disconnect(context, root, ContextToRoot)

The first two arguments to :meth:`~substanced.objectmap.ObjectMap.connect` or
:meth:`~substanced.objectmap.ObjectMap.disconnect` are *source* and *target*.
These can be either resource objects or oids.  The third argument to these
functions is the reference type.

Once a reference is formed between two objects, you can see the reference
within the "References" tab in the SDI.  The References tab of either side of
the reference (in the above example, either the root or the context) when
visited in the SDI will display the reference to the other side.  

Once a reference is made between two objects, the object map can be queried for
objects which take part in the reference.

.. code-block:: python

   from substanced.interfaces import ReferenceType
   from substanced.objectmap import find_objectmap

   class ContextToRoot(ReferenceType):
       pass

   def query_reference_sources(context, request):
       objectmap = find_objectmap(context)
       return objectmap.sourceids(request.root, ContextToRoot)

   def query_reference_targets(context, request):
       objectmap = find_objectmap(context)
       return objectmap.targetids(context, ContextToRoot)

The :meth:`~substanced.objectmap.ObjectMap.sourceids` method returns the set of
objectids which are *sources* of the object and reference type it's passed.
The :meth:`~substanced.objectmap.ObjectMap.targetids` method returns the set of
objectids which are *targets* of the object and reference type it's passed.  If
no objects are involved in the relation, an empty set will be returned in
either case.  :meth:`~substanced.objectmap.ObjectMap.sources` and
:meth:`~substanced.objectmap.ObjectMap.targets` methods also exist which are
analgous, but return the actual objects involved in the relation instead of the
objectids:

.. code-block:: python

   from substanced.interfaces import ReferenceType
   from substanced.objectmap import find_objectmap

   class ContextToRoot(ReferenceType):
       pass

   def query_reference_sources(context, request):
       objectmap = find_objectmap(context)
       return objectmap.sources(request.root, ContextToRoot)

   def query_reference_targets(context, request):
       objectmap = find_objectmap(context)
       return objectmap.targets(context, ContextToRoot)


A reference type can claim that it is "integral", which just means that the
deletion of either the source or the target of a reference will be
prevented.  Here's an example of a "source integral" reference type:

.. code-block:: python

   from substanced.interfaces import ReferenceType

   class UserToGroup(ReferenceType):
       source_integrity = True

This reference type will prevent any object on the "user" side of the
UserToGroup reference (as opposed to the group side) from being deleted.  When
a user attempts to delete a user that's related to a group using this reference
type, a :class:`substanced.objectmap.SourceIntegrityError` will be raised and
the deletion will be prevented.  Only when the reference is removed or the
group is deleted will the user deletion be permitted.

The flip side of this is target integrity:

.. code-block:: python

   from substanced.interfaces import ReferenceType

   class UserToGroup(ReferenceType):
       target_integrity = True

This is the inverse.  The reference will prevent any object on the "group" side
of the UserToGroup reference from being deleted unless the associated user is
first removed or the reference itself is no longer active.  When a user
attempts to delete a user that's related to a group using this reference type,
a :class:`substanced.objectmap.TargetIntegrityError` will be raised and the
deletion will be prevented.

:class:`substanced.objectmap.SourceIntegrityError` and
:class:`substanced.objectmap.TargetIntegrityError` both inherit from
:class:`substanced.objectmap.ReferentialIntegrityError`, so you can catch
either in your code.

There are convenience functions that you can add to your resource objects that
give them special behavior:
:func:`~substanced.objectmap.reference_sourceid_property`,
:func:`~substanced.objectmap.reference_targetid_property`,
:func:`~substanced.objectmap.reference_source_property`,
:func:`~substanced.objectmap.reference_target_property`,
:func:`~substanced.objectmap.multireference_sourceid_property`,
:func:`~substanced.objectmap.multireference_targetid_property`,
:func:`~substanced.objectmap.reference_source_property`, and
:func:`~substanced.objectmap.reference_target_property`.

Here's use of a reference property:

.. code-block:: python
   :linenos:

   from persistent import Persistent
   from substanced.objectmap import reference_sourceid_property
   from substanced.interfaces import ReferenceType

   class LineItemToOrder(ReferenceType):
       pass

   class LineItem(Persistent):
       order = reference_target_property(LineItemToOrder)

Once you've seated a resource object in a folder, you can then begin to use its
special properties:

.. code-block:: python
   :linenos:

   from mysystem import LineItem, Order

   lineitem = LineItem()
   folder['lineitem'] = lineitem
   lineitem.order = Order()

This is just a nicer way to use the objectmap query API; you don't have to
interact with it at all, just assign and ask for attributes of your object.
The ``multireference_*`` variants are similar to the reference variants, but
they allow for more than one object on the "other side".

ACLs and Principal References
=============================

When an ACL is modified on a resource, a statement is being made about
a relationship between that resource and a principal or group of
principals. Wouldn't it be great if a reference was established,
allowing you to then see such connections in the SDI?

This is indeed exactly how Substance D behaves: a source-integral
PrincipalToACLBearing reference is set up between an ACL-bearing
resource and the principals referred to within the ACL.
