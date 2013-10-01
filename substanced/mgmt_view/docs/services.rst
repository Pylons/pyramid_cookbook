Services
--------

A :term:`service` is a name for a content object that provides a service to
application code.  It looks just like any other content object, but services
that are added to a site can be found by name using various Substance D APIs.

Services expose APIs that exist for the benefit of application developers.  For
instance, the ``catalogs`` service provides an API that allows a developer to
index and query for content objects using a structured query API.  The
``principals`` service allows a developer to add and enumerate users and
groups.

A service is added to a folder via the
:meth:`substanced.folder.Folder.add_service` API.

An existing service can be looked up in one of two ways: using the
:func:`substanced.util.find_service` API or the
:meth:`substanced.folder.Folder.find_service` API.  They are functionally
equivalent.  The latter exists only as a convenience so you don't need to
import a function if you know you're dealing with a :term:`folder`.

Either variant of ``find_service`` will look down the resource hierarchy
towards the root until it finds a parent folder that has had ``add_service``
called on it.  If the name passed in matches the service name, the object
will be returned, otherwise the search will continue down the tree.

Note that a content object may exist in the folder with the same name as
you're looking for via ``find_service``, but if that object was not added via
``add_service`` (instead it's just a "normal" content object), it won't be
found by ``find_service``.

Here's how to use :func:`substanced.util.find_service`:

.. code-block:: python

   from substanced.util import find_service
   principals = find_service(somecontext, 'principals')

``somecontext`` above is any :term:`resource` in the :term:`resource tree`.
For example, ``somecontext`` could be a "document" object you've added to a
folder.

Here's how to use :meth:`substanced.folder.Folder.find_service`:

.. code-block:: python

   principals = somefolder.find_service('principals')

``somefolder`` above is any :class:`substanced.folder.Folder` object (or any
object which inherits from that class) present in the :term:`resource tree`.

There is also the find-multiple-services variants
:func:`substanced.util.find_services` and
:meth:`substanced.folder.Folder.find_services`.


