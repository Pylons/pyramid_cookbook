==============
Using Auditing
==============

Substance D keeps an audit log of all meaningful operations performed against
content if you have an audit database configured.  At the time of this writing, "meaningful" is defined as:

- When an ACL is changed.

- When a resource is added or removed.

- When a resource is modified.

The audit log is of a fixed size (currently 10,000 items).  When the audit log
fills up, the oldest audit event is thrown away.  Currently we don't have an
archiving mechanism in place to keep around the items popped off the end of the
log when it fills up; this is planned.

You can extend the auditing system by using the
:class:`substanced.audit.AuditLog`, writing your own events to the log.

Configuring the Audit Database
==============================

In order to enable auditing, you have to add an ``audit`` database to your
Substance D configuration.  This means adding a key to your application's 
section in the ``.ini`` file associated with the app::

  zodbconn.uri.audit = <some ZODB uri>

An example of "some ZODB URI" above might be (for a FileStorage database, if 
your application doesn't use multiple processes)::

  zodbconn.uri.audit = file://%(here)s/auditlog.fs

Or if your application uses multiple processes, use a ZEO URL.

The database cannot be your main database.  The reason that the audit database
must live in a separate ZODB database is that we don't want undo operations to
undo the audit log data.

Note that if you do not configure an audit database, real-time SDI features
such as your folder contents views updating without a manual refresh will not 
work.

Once you've configured the audit database, you need to add an audit log object
to the new database.  You can do this using pshell::

    [chrism@thinko sdnet]$ bin/pshell etc/development.ini 
    Python 3.3.2 (default, Jun  1 2013, 04:46:52) 
    [GCC 4.6.3] on linux
    Type "help" for more information.

    Environment:
      app          The WSGI application.
      registry     Active Pyramid registry.
      request      Active request object.
      root         Root of the default resource tree.
      root_factory Default root factory used to create `root`.

    >>> from substanced.audit import set_auditlog
    >>> set_auditlog(root)
    >>> import transaction; transaction.commit()

Once you've done this, the "Auditing" tab of the root object in the SDI should
no longer indicate that auditing is not configured.

Viewing the Audit Log
=====================

The root object will have a tab named "Auditing".  You can view the currently
active audit log entries from this page.  Accessing this tab requires the
``sdi.view-auditlog`` permission.

Adding an Audit Log Entry
=========================

Here's an example of adding an audit log entry of type ``NailsFiled`` to the
audit log:

.. code-block:: python

   from substanced.util import get_oid, get_auditlog

   def myview(context, request):
       auditlog = get_auditlog(context)
       auditlog.add('NailsFiled', get_oid(context), type='fingernails')
       ...

.. warning::

   If you don't have an audit database defined, the 
   :func:`~substanced.util.get_auditlog` API will return ``None``.

This will add a``NailsFiled`` event with the payload
``{'type':'fingernails'}`` to the audit log.  The payload will also
automatically include a UNIX timestamp as the key ``time``.  The first argument
is the audit log typename.  Audit entries of the same kind should share the
same type name.  It should be a string.  The second argument is the oid of the
content object which this event is related to.  It may be ``None`` indicating
that the event is global, and unrelated to any particular piece of content.
You can pass any number of keyword arguments to
:meth:`substanced.audit.AuditLog.add`, each will be added to the payload.
Each value supplied as a keyword argument *must* be JSON-serializable.  If one
is not, you will receive an error when you attempt to add the event.

Using The ``auditstream-sse`` View
==================================

If you have auditing enabled, you can use a view named ``auditstream-sse`` 
against any resource in your resource tree using JavaScript.  It will return
an event stream suitable for driving an HTML5 ``EventSource`` (an HTML 5 
feature, see http://www.html5rocks.com/en/tutorials/eventsource/basics/ for more
information).  The event stream will contain auditing events.  This can be used
for progressive enhancement of your application's UI.  Substance D's SDI uses
it for that purpose.  For example, when an object's ACL is changed, a user
looking at the "Security" tab of that object in the SDI will see the change
immediately, rather than upon the next page refresh.

Obtain events for the context of the view only::

 var source = new EventSource(
    "${request.sdiapi.mgmt_path(context, 'auditstream-sse')}");

Obtain events for a single OID unrelated to the context::

 var source = new EventSource(
    "${request.sdiapi.mgmt_path(context, 'auditstream-sse', query={'oid':'12345'})}");

Obtain events for a set of OIDs::

 var source = new EventSource(
    "${request.sdiapi.mgmt_path(context, 'auditstream-sse', query={'oid':['12345', '56789']})}");

Obtain all events for all oids::

 var source = new EventSource(
    "${request.sdiapi.mgmt_path(context, 'auditstream-sse', query={'all':'1'})}");

The executing user will need to possess the ``sdi.view-auditstream`` permission
against the context on which the view is invoked.  Each event payload will
contain detailed information about the audit event as a string which represents
a JSON dictionary.

See the ``acl.pt`` template in the ``substanced/sdi/views/templates`` directory
of Substance D to see a "real-world" usage of this feature.

