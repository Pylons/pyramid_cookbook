=====================================
The Substance D Management Interface
=====================================

Substance D's prime directive is to help developers quickly build
custom content management applications with a custom user experience.
For the Substance D parts, though, a polished, stable,
and supported management UI is provided.

The Substance D management interface (aka :term:`SDI`) is a set of :term:`view`
registrations that are imposed upon the :term:`resource tree` of your
application.  The SDI allows you to add, delete, change and otherwise manage
resources and services.

.. image:: images/sdi.png

Benefits and Features
=====================

- CRUD on content resources

- Extensible actions for each content type via management views

- Built-in support for hierarchies with security

- Already-done UIs for all supported features (e.g. references,
  principals)

- Undo facility to back out of the last transaction

- Copy and paste

Background and Motivation
=========================

In prehistoric times there was a Python-based application server,
derived from a commercial predecessor released in 1996. Zope and its
predecessor had a unique, "through-the-web" (TTW) UI for interacting
with the system. This UI, called the "Zope Management Interface" (ZMI),
had a number of capabilities for a number of audiences. Plone,
built on Zope, extended this idea. Other systems, such as Django,
have found that providing an out-of-the-box (OOTB) starting point with
attractive pixels on the screen can be a key selling point.

Substance D taps into this. In particular, lessons learned from our
long experience in this area are applied to the SDI:

- Attractive, official, supported OOTB management UI

- Be successful by being very clear what the SDI *isn't*

What Is and Isn't the SDI
=========================

The SDI is for:

- Developers to use while building their application

- Administrators to use after deployment, to manage certain Substance D
  or application settings provided by the developer

- Certain power users to use as a behind-the-scenese UI

The SDI is *not* for:

- The *retail UI* for your actual application. Unlike Plone,
  we don't expect developers to squeeze their UX expectations into an
  existing UX

- Overridable, customizable, replaceable, frameworky new expectations

The SDI does have a short list of clearly-defined places for developers
to plug in parts of their application. As a prime example, you can
define a :doc:`Management View <mgmtview>` that gets added as a new
tab on a resource.

The SDI is extensible and allows you to plug your own views into it, so you
can present nontechnical users with a way to manage arbitrary kinds of
custom content.

Once again, for clarity: the SDI is not a framework, it is an
application. It is not your retail UI.

Layout
======

The SDI has a mostly-familiar layout:

- A *header* that shows the username as a dropdown menu containing a
  link to the principal screen as well as a logout link

- *Breadcrumbs* with a path from the root

- A series of *tabs* for the management views of the current resource

- Optionally, a *flash message* showing results of the previous
  operation, a warning, or some other notice

- A *footer*

.. _sdi-folder-contents:

Folder Contents
===============

Folders show a listing of items they contain using a powerful data grid
based on SlickGrid:

.. image:: images/contents.png

This dynamic grid features:

- Only loading the items needed for display, to speed up operations on
  large folders

- "Infinite scrolling" via the scrollbar to go directly to a batch at
  any point in the folder

- Column resizing and re-ordering

- Sorting on sort-supported columns

- Filtering based on search string

- Selection of one or more items and performing an operation by
  clicking on a button

- Styling integrated with Twitter Bootstrap

- Detection and re-layout on responsive design operations

The :doc:`folder_contents` chapter covers how Substance D developers
can plug their custom content types into folder contents.

Undo
====

In Substance D, many transactions can be undone and redone after
commit. This "Undo" ability is one of the key features that people
notice immediately and it has real, deep value to a developer's
customers.

Many of the built-in operations dispay an undo button. For example, if we
delete an item from a folder, we get a "flash" message telling us the deletion
was performed, but with a button allowing us to undo if that was a mistake:

.. image:: images/undo1.png

Clicking "undo" restores the deleted item, with a flash message
offering to redo the undo:

.. image:: images/undo2.png

Undo button support is enabled by the developer in their management views
that commit data. It isn't available on every kind of change. Instead
developers need to wrap their commit with certain information used by the SDI's
undo features.

All actions that change data (even ones without undo button support) can be
undone.  These screenshots show an ``Undo`` tab on the site's root folder. This
provides a global way to see recent transactions and perform an undo:

.. image:: images/undo3.png

Sometimes a particular transaction cannot be undone without undoing an earlier
transaction. For example, if you make 3 changes to a resource, the first two
can't be undone without first undoing the last, as the resource will have been
changed by a later transaction.

Catalog
=======

With :doc:`cataloging <cataloging>` developers have a powerful facility
that can be added to their application. Like other first-class parts of
Substance D's machinery, this includes an SDI UI for interacting with
the catalog:

.. image:: images/catalog.png

Catalogues are content, meaning they show up as folder items in the SDI. You
can visit a a catalog and update its indexes, or see some statistics for those
index. Finally, you can also use the SDI to reindex the contents of an index,
if you suspect it has gotten out of sync with the content.

The catalog also registers a management view on content resources which
gain a ``Indexing`` tab:

.. image:: images/indexing.png

This shows some statistics and allows an SDI user to reindex an
individual resource.

Principals
==========

Managing users and groups, aka principals, is more interesting in a
system like Substance D with rich hierarchies. You can add a folder of
principals to any folder or other kind of container that allows adding
principals:

.. image:: images/principals.png

A principals folder allows you to manage (e.g. add/edit/delete/rename)
users and groups via the SDI, as well as password resets. Since users
and groups are content, you gain some of the other SDI tabs for
managing them (e.g. Security, References):

.. image:: images/user.png

Users and groups can also grow extra attributes and behavior because they're
just content, so you can customize your user model out of the box.

Workflows
=========

The :doc:`workflows service <workflows>` provides a powerful system for
managing states and transitions. This service shows up in the SDI as a
tab on content types that have workflows registered for them:

.. image:: images/workflows.png

This provides a way, via the SDI, to transition the workflow state of a
resource.

References
==========

With the built-in support for :doc:`references <references>`, Substance D
helps manage relationships between resources. The SDI provides a UI into the
reference service.

If the resource you are viewing has any references, a ``References``
tab will appear:

.. image:: images/references.png

In this example, ``mydoc1`` is a target of an ACL reference from the
``admin1`` user.

An integrity error can occur if you try to delete a source or target of
a reference that claims to be "integral". The SDI will then show this
with an explanation:

.. image:: images/integrityerror.png

Manage Database
===============

The object database inside Substance D has some management knobs that
can be adjusted via the SDI:

.. image:: images/managedb.png

This tab appears on the root object of the site and lets you:

- Pack the old revisions of objects in the database.

- Inspect and run evolution steps  

- Flush the object cache.

- See details and statistics about the database, the connection, and
  activity

Implementation Notes
====================

While it doesn't matter for developers of Substance D applications,
some notes below regarding how the SDI is implemented:

- High-performance, modern, responsive UI based on Twitter Bootstrap

- We use the upstream LESS variables from Bootstrap in a LESS file for
  parts of the SDI

- Our grid is based on SlickGrid



