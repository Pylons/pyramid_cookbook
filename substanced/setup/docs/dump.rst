=======================
Dumping Content to Disk
=======================

Substance D's object database stores native Python representations of
resources. This is easy enough to work with: you can run
``bin/pshell`` to get an interactive prompt, write longer ad-hoc
console scripts, or just put code into your application.

However, production sites usually want exportable representations of
important data stored in a long-term format. For this,
Substance D provides a dump facility for content types to be serialized
in a `YAML <http://yaml.org/>`_  representation on disk.

.. note::

    You'll note in the following the absence of docs on *loading* data.
    This is intentional. The process of loading data into a new,
    or semi-new, or newer-than-new site has many policy implications.
    Too many to fit into a single loading script. Substance D considers
    the particulars of loading data to be in the province of the
    application developer.

Dumping Resources Using ``sd_dump``
===================================

The ``sd_dump`` console script loads your Substance D application,
connects to your object database, and writes serialized representations
of resources to disk in a directory hierarchy::

    $ ../bin/sd_dump --help
    Usage: sd_dump [options]

     Dump an object (and its subobjects) to the filesystem:  sd_dump [--source
    =ZODB-PATH] [--dest=FILESYSTEM-PATH] config_uri   Dumps the object at ZODB-
    PATH and all of its subobjects to a   filesystem path.  Such a dump can be
    loaded (programmatically)   by using the substanced.dump.load function  e.g.
    sd_dump --source=/ --dest=/my/dump etc/development.ini

    Options:
      -h, --help            show this help message and exit
      -s ZODB-PATH, --source=ZODB-PATH
                            The ZODB source path to dump (e.g. /foo/bar or /)
      -d FILESYSTEM-PATH, --dest=FILESYSTEM-PATH
                            The destination filesystem path to dump to.

For example::

    $ ../bin/sd_dump ../etc/development.ini
    2013-01-07 13:27:03,939 INFO  [ZEO.ClientStorage][MainThread] ('localhost', 9963) ClientStorage (pid=93148) created RW/normal for storage: 'main'
    2013-01-07 13:27:03,941 INFO  [ZEO.cache][MainThread] created temporary cache file '<fdopen>'
    2013-01-07 13:27:03,981 WARNI [ZEO.zrpc][Connect([(2, ('localhost', 9963))])] (93148) CW: error connecting to ('fe80::1%lo0', 9963): EHOSTUNREACH
    2013-01-07 13:27:03,982 WARNI [ZEO.zrpc][Connect([(2, ('localhost', 9963))])] (93148) CW: error connecting to ('fe80::1%lo0', 9963): EHOSTUNREACH
    2013-01-07 13:27:04,002 WARNI [ZEO.zrpc][Connect([(2, ('localhost', 9963))])] (93148) CW: error connecting to ('::1', 9963): EINVAL
    2013-01-07 13:27:04,003 INFO  [ZEO.ClientStorage][Connect([(2, ('localhost', 9963))])] ('localhost', 9963) Testing connection <ManagedClientConnection ('127.0.0.1', 9963)>
    2013-01-07 13:27:04,004 INFO  [ZEO.zrpc.Connection(C)][('localhost', 9963) zeo client networking thread] (127.0.0.1:9963) received handshake 'Z3101'
    2013-01-07 13:27:04,105 INFO  [ZEO.ClientStorage][Connect([(2, ('localhost', 9963))])] ('localhost', 9963) Server authentication protocol None
    2013-01-07 13:27:04,106 INFO  [ZEO.ClientStorage][Connect([(2, ('localhost', 9963))])] ('localhost', 9963) Connected to storage: ('localhost', 9963)
    2013-01-07 13:27:04,108 INFO  [ZEO.ClientStorage][Connect([(2, ('localhost', 9963))])] ('localhost', 9963) No verification necessary -- empty cache
    2013-01-07 13:27:04,727 INFO  [substanced.catalog][MainThread] system update_indexes: no indexes added or removed
    2013-01-07 13:27:04,730 INFO  [substanced.catalog][MainThread] sdidemo update_indexes: no indexes added or removed
    2013-01-07 13:27:04,732 INFO  [substanced.dump][MainThread] Dumping /
    2013-01-07 13:27:04,749 INFO  [substanced.dump][MainThread] Dumping /principals
    2013-01-07 13:27:04,754 INFO  [substanced.dump][MainThread] Dumping /principals/users
    2013-01-07 13:27:04,760 INFO  [substanced.dump][MainThread] Dumping /principals/users/admin
    2013-01-07 13:27:04,779 INFO  [substanced.dump][MainThread] Dumping /principals/resets
    2013-01-07 13:27:04,783 INFO  [substanced.dump][MainThread] Dumping /principals/groups

...with logging messages being emitted until all known content is
dumped. A ``dump`` subdirectory in the current directory is created (if
no argument is provided) containing::

    $ ls
    acl.yaml	propsheets	references.yaml	resource.yaml	resources

.. note::

    To correctly encode as much meaning as possible,
    the dump files contain some advanced and custom YAML constructs
    when needed.

``acl.yaml`` For Security Settings
-----------------------------------

This YAML file contains security settings for this resource. For
example::

    - !!python/tuple [Allow, 1644064392535565429, !all_permissions '']

``references.yaml`` for Reference Information
---------------------------------------------

Data about references aren't stored on the resources involved in the
reference. Instead, they are stored in the objectmap. This file
contains the reference information for the resource identified at the
current dump directory. For example::

    !interface 'substanced.interfaces.PrincipalToACLBearing':
      sources: [1644064392535565429]

``workflow.yaml`` for Workflow Settings
---------------------------------------

The workflow engine can contain information about resource state. For
example::

    !!python/object:persistent.mapping.PersistentMapping
    data: {document: draft}

``propsheets`` Directory for Property Sheet Data
------------------------------------------------

Resources can have multiple system-defined or application-defined
property sheets on resources. These are serialized as subdirectories
under ``propsheets``, with a directory for each property sheet. For
example, a resources ``propsheets/Basic/properties.yaml`` might contain::

    {body: !!python/unicode 'The quick brown fox jumps over the lazy dog. The quick brown
        fox jumps over the lazy dog.  The quick brown fox jumps over the lazy dog.
        The quick brown fox jumps over the lazy dog. The quick brown fox jumps over the
        lazy dog. The quick brown fox jumps over the lazy dog. The quick brown fox jumps
        over the lazy dog. The quick brown fox jumps over the lazy dog. The quick brown
        fox jumps over the lazy dog. ', name: !!python/unicode 'document_0', title: !!python/unicode 'Document
        0 Binder 0'}

``resource.yaml`` for Content Type Information
----------------------------------------------

Each directory after the top corresponds to a resource in the database.
As such, the resource likely has content type information. The dump
script encodes this into a YAML file in the resource's dump directory::

    {content_type: Root, created: !!timestamp '2013-01-07 14:23:23.133436', is_service: false,
      name: null, oid: 1644064392535565415}


``resources`` for Contained Resources in Containers
---------------------------------------------------

If the resource at a current dump directory is a ``Folder`` or some
other kind of container, it will contain a ``resources`` subdirectory.
This might contain more subfolders and thus subdirectories. It might
also contain individual resources, as a subdirectory named with the
resource name.

Custom Dumping with ``__dump__``
================================

The built-in facilities allow automatic dumping of most information for
your content, including information in your property sheets,
the content type, security settings, references, workflows, etc.

If you do need extra information dumped to YAML about your content type,
Substance D has a Python protocol using an ``__dump__`` on your
``@content`` class. As an example,
:py:meth:``substanced.principal.User.dump`` is a callable which returns
a mapping of simple Python objects. The dumper checks to see if a
resource has a ``__dump__`` method. If so, it calls the method,
encodes the result to YAML, and writes it to an ``adhoc.yaml`` file in
the dumped-resource's directory.

The inverse is also true. If a content type has a ``__load__`` method,
information from that method is added to the state that is loaded.

Adding New Dumpers
==================

The ``adhoc.yaml`` file that we just saw is an example of the
``AdhocAttrDumper``. There are seven other dumpers built-in: acl,
workflow, references, sdiproperties, interfaces, order, and propsheets.

If you would like a custom dumper, you can register it with
``config.add_dumper``. For example,
:py:func:`substanced.dump.includeme` registers the existing dumpers and
their dumper factories:

.. code-block:: python

    def includeme(config):
        DEFAULT_DUMPERS = [
            ('acl', ACLDumper),
            ('workflow', WorkflowDumper),
            ('references', ReferencesDumper),
            ('sdiproperties', SDIPropertiesDumper),
            ('interfaces', DirectlyProvidedInterfacesDumper),
            ('order', FolderOrderDumper),
            ('propsheets', PropertySheetDumper),
            ('adhoc', AdhocAttrDumper),
            ]
        config.add_directive('add_dumper', add_dumper)
        for dumper_name, dumper_factory in DEFAULT_DUMPERS:
            config.add_dumper(dumper_name, dumper_factory)
