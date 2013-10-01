.. _substanced_api:

:mod:`substanced` API
---------------------------

.. automodule:: substanced

.. autofunction:: includeme

.. autofunction:: include

.. autofunction:: scan

:mod:`substanced.audit` API
---------------------------

.. automodule:: substanced.audit

.. autoclass:: AuditLog
   :members:

:mod:`substanced.catalog` API
-----------------------------

.. automodule:: substanced.catalog

.. autoclass:: Text

.. autoclass:: Field

.. autoclass:: Keyword

.. autoclass:: Facet

.. autoclass:: Allowed

.. autoclass:: Path

.. autoclass:: Catalog
   :members:
   :inherited-members:

   .. automethod:: __setitem__

   .. automethod:: __getitem__

   Retrieve an index.

   .. automethod:: get

   Retrieve an index or return failobj.

.. autoclass:: CatalogsService
   :members:

.. autofunction:: is_catalogable

.. autofunction:: catalog_factory

.. autofunction:: includeme

.. autofunction:: add_catalog_factory

.. autofunction:: add_indexview

.. autoclass:: indexview

.. autoclass:: indexview_defaults

:mod:`substanced.catalog.indexes` API
-------------------------------------

.. automodule:: substanced.catalog.indexes

.. autoclass:: FieldIndex
   :members:

.. autoclass:: KeywordIndex
   :members:

.. autoclass:: TextIndex
   :members:

.. autoclass:: FacetIndex
   :members:

.. autoclass:: PathIndex
   :members:

.. autoclass:: AllowedIndex
   :members:


:mod:`hypatia.query` API
-------------------------------

.. module:: hypatia.query

Comparators
~~~~~~~~~~~

.. autoclass:: Contains

.. autoclass:: Eq

.. autoclass:: NotEq

.. autoclass:: Gt

.. autoclass:: Lt

.. autoclass:: Ge

.. autoclass:: Le

.. autoclass:: Contains

.. autoclass:: NotContains

.. autoclass:: Any

.. autoclass:: NotAny

.. autoclass:: All

.. autoclass:: NotAll

.. autoclass:: InRange

.. autoclass:: NotInRange

Boolean Operators
~~~~~~~~~~~~~~~~~

.. autoclass:: Or

.. autoclass:: And

.. autoclass:: Not

Other Helpers
~~~~~~~~~~~~~

.. autoclass:: Name

.. autofunction:: parse_query

:mod:`hypatia.util` API
-------------------------------

.. module:: hypatia.util

.. autoclass:: ResultSet
   :members:

:mod:`substanced.content` API
-----------------------------

.. automodule:: substanced.content

.. autoclass:: content
   :members:

.. autoclass:: service
   :members:

.. autofunction:: add_content_type

.. autofunction:: add_service_type

.. autoclass:: ContentRegistry
   :members:

.. autofunction:: includeme

:mod:`substanced.db` API
------------------------

.. automodule:: substanced.db

.. autofunction:: root_factory

:mod:`substanced.dump` API
-----------------------------

.. automodule:: substanced.dump

.. autofunction:: dump

.. autofunction:: load

.. autofunction:: add_dumper

.. autofunction:: includeme

:mod:`substanced.editable` API
------------------------------

.. automodule:: substanced.editable

.. autointerface:: IEditable
   :members:
   :inherited-members:

.. autoclass:: FileEditable

.. autofunction:: register_editable_adapter

:mod:`substanced.event` API
---------------------------

.. automodule:: substanced.event

.. autoclass:: ObjectAdded
   :members:
   :inherited-members:

.. autoclass:: ObjectWillBeAdded
   :members:
   :inherited-members:

.. autoclass:: ObjectRemoved
   :members:
   :inherited-members:

.. autoclass:: ObjectWillBeRemoved
   :members:
   :inherited-members:

.. autoclass:: ObjectModified
   :members:
   :inherited-members:

.. autoclass:: ACLModified
   :members:
   :inherited-members:

.. autoclass:: LoggedIn
   :members:
   :inherited-members:

.. autoclass:: RootAdded
   :members:
   :inherited-members:

.. autoclass:: subscribe_added
   :members:
   :inherited-members:

.. autoclass:: subscribe_removed
   :members:
   :inherited-members:

.. autoclass:: subscribe_will_be_added
   :members:
   :inherited-members:

.. autoclass:: subscribe_will_be_removed
   :members:
   :inherited-members:

.. autoclass:: subscribe_modified
   :members:
   :inherited-members:

.. autoclass:: subscribe_acl_modified
   :members:
   :inherited-members:

.. autoclass:: subscribe_logged_in
   :members:
   :inherited-members:

.. autoclass:: subscribe_root_added
   :members:
   :inherited-members:

:mod:`substanced.evolution` API
--------------------------------

.. automodule:: substanced.evolution

.. autofunction:: add_evolution_step

.. autofunction:: mark_unfinished_as_finished

.. autofunction:: includeme

:mod:`substanced.file` API
-----------------------------

.. automodule:: substanced.file

.. attribute:: USE_MAGIC

   A constant value used as an argument to various methods of the
   :class:`substanced.file.File` class.

.. autoclass:: File
   :members:

   .. automethod:: __init__

   .. attribute:: blob

      The ZODB blob object associated with this file.

   .. attribute:: mimetype
 
      The mimetype of this file object (a string).

:mod:`substanced.folder` API
----------------------------

.. automodule:: substanced.folder

.. autoclass:: FolderKeyError

.. autoclass:: Folder
   :members:

   .. automethod:: __init__

   .. attribute:: order

     A tuple of name values. If set, controls the order in which names should
     be returned from ``__iter__()``, ``keys()``, ``values()``, and
     ``items()``.  If not set, use an effectively random order.

.. autoclass:: SequentialAutoNamingFolder

   .. automethod:: __init__

   .. automethod:: add_next

   .. automethod:: next_name

   .. automethod:: add

.. autoclass:: RandomAutoNamingFolder

   .. automethod:: __init__

   .. automethod:: add_next

   .. automethod:: next_name

:mod:`substanced.folder.views` API
----------------------------------

.. automodule:: substanced.folder.views

.. autofunction:: add_folder_contents_views

.. autoclass:: folder_contents_views

.. autoclass:: FolderContents

:mod:`substanced.form` API
----------------------------

.. automodule:: substanced.form

.. autoclass:: Form
   :members:

.. autoclass:: FormView
   :members:

.. autoclass:: FileUploadTempStore
   :members:


:mod:`substanced.locking` API
-----------------------------

.. automodule:: substanced.locking

.. autoclass:: Lock
   :members:

   .. attribute:: ownerid

      The owner oid for this lock.

   .. attribute:: owner

      The owner object of this lock (a User).

   .. attribute:: resourceid

      The oid of the resource related to this lock.

   .. attribute:: resource

      The resource object related to this lock.

.. autoclass:: LockError

.. autoclass:: UnlockError

.. autofunction:: lock_resource

.. autofunction:: unlock_resource

.. autofunction:: discover_resource_locks

:mod:`substanced.objectmap` API
--------------------------------

.. automodule:: substanced.objectmap

.. autoclass:: ObjectMap
   :members:

.. autoclass:: Multireference
   :members:

.. autofunction:: reference_sourceid_property

.. autofunction:: reference_source_property

.. autofunction:: reference_targetid_property

.. autofunction:: reference_target_property

.. autofunction:: multireference_sourceid_property

.. autofunction:: multireference_source_property

.. autofunction:: multireference_targetid_property

.. autofunction:: multireference_target_property

.. autoclass:: ReferentialIntegrityError
   :members:

.. autoclass:: SourceIntegrityError

.. autoclass:: TargetIntegrityError

:mod:`substanced.principal` API
--------------------------------

.. automodule:: substanced.principal

.. autoclass:: Principals
   :members:

.. autoclass:: Users
   :members:

.. autoclass:: Groups
   :members:

.. autoclass:: GroupSchema
   :members:

.. autoclass:: Group
   :members:

.. autoclass:: UserSchema
   :members:

.. autoclass:: User
   :members:

   .. attribute:: timezone

      A Python "tzinfo" object representing the user's preferred timezone.

.. autofunction:: groupfinder

:mod:`substanced.property` API
--------------------------------

.. automodule:: substanced.property

.. autoclass:: PropertySheet
   :members:

:mod:`substanced.schema` API
----------------------------

.. automodule:: substanced.schema

.. autoclass:: Schema
   :members:

.. autoclass:: NameSchemaNode

.. autoclass:: PermissionsSchemaNode

:mod:`substanced.sdi` API
----------------------------

.. automodule:: substanced.sdi

.. autofunction:: add_mgmt_view

.. autoclass:: mgmt_view

.. attribute:: LEFT

.. attribute:: MIDDLE

.. attribute:: RIGHT

.. autofunction:: includeme

:mod:`substanced.root` API
--------------------------

.. automodule:: substanced.root

.. autoclass:: Root
   :members:

:mod:`substanced.stats` API
---------------------------

.. automodule:: substanced.stats

.. autofunction:: statsd_timer

.. autofunction:: statsd_gauge

.. autofunction:: statsd_incr


:mod:`substanced.util` API
--------------------------

.. automodule:: substanced.util

.. autofunction:: acquire

.. autofunction:: get_oid

.. autofunction:: set_oid

.. autofunction:: get_acl

.. autofunction:: set_acl

.. autofunction:: get_interfaces

.. autofunction:: get_content_type

.. autofunction:: find_content

.. autofunction:: find_service

.. autofunction:: find_services

.. autofunction:: find_objectmap

.. autofunction:: find_catalogs

.. autofunction:: find_catalog

.. autofunction:: find_index

.. autofunction:: get_principal_repr

.. autofunction:: is_folder

.. autofunction:: is_service

.. autofunction:: get_factory_type

.. autofunction:: coarse_datetime_repr

.. autofunction:: postorder

.. autofunction:: merge_url_qs

.. autofunction:: chunks

.. autofunction:: renamer

.. autofunction:: get_dotted_name

.. autofunction:: get_icon_name

.. autofunction:: get_auditlog

.. autoclass:: Batch
   :members:

:mod:`substanced.widget` API
----------------------------

.. automodule:: substanced.widget

.. autofunction:: includeme

:mod:`substanced.workflow` API
------------------------------

.. automodule:: substanced.workflow
   :members:

:mod:`substanced.interfaces`
----------------------------

These represent interfaces implemented by various Substance D objects.

.. automodule:: substanced.interfaces
   :members:
