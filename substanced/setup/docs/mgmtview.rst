================
Management Views
================

A :term:`management view` is a :term:`view configuration` that applies only
when the URL is prepended with the :term:`manage prefix`. The manage prefix
is usually ``/manage``, unless you've changed it from its default by setting
a custom ``substanced.manage_prefix`` in your application's ``.ini`` file.

This means that views declared as management views will never show up in your
application's "retail" interface (the interface that normal unprivileged
users see).  They'll only show up when a user is using the :term:`SDI` to
manage content.

There are two ways to define management views:

- Using the :class:`substanced.sdi.mgmt_view` decorator on a function,
  method, or class.

- Using the :func:`substanced.sdi.add_mgmt_view` Configurator (aka.
  ``config.add_mgmt_view``) API.

The former is most convenient, but they are functionally equivalent.
``mgmt_view`` just calls into ``add_mgmt_view`` when found via a
:term:`scan`.

Declaring a management view is much the same as declaring a "normal" Pyramid
view using :class:`pyramid.view.view_config` with a ``route_name`` of
``substanced_manage``.  For example, each of the following view declarations
will register a view that will show up when the ``/manage/foobar`` URL is
visited:

.. code-block:: python
   :linenos:

   from pyramid.view import view_config

   @view_config(
       renderer='string',
       route_name='substanced_manage', 
       name='foobar',
       permission='sdi.view',
       )
   def foobar(request):
       return 'Foobar!'

The above is largely functionally the same as this:

.. code-block:: python
   :linenos:

   from substanced.sdi import mgmt_view

   @mgmt_view(renderer='string', name='foobar')
   def foobar(request):
       return 'Foobar!'

Management views, in other words, are really just plain-old Pyramid views
with a slightly shorter syntax for definition.  Declaring a view a management
view, however, does do some extra things that make it advisable to use rather
than a plain Pyramid view registration:

- It registers *introspectable* objects that the SDI interface uses to try to
  find management interface tabs (the row of actions at the top of every
  management view rendering).

- It allows you to associate a tab title, a tab condition, and cross-site
  request forgery attributes with the view.

- It uses the default permission ``sdi.view``.

So if you want things to work right when developing management views, you'll
use ``@mgmt_view`` instead of ``@view_config``, and ``config.add_mgmt_view``
instead of ``config.add_view``.

As you use management views in the SDI, you might notice that the URL
includes ``@@`` as  "goggles". For example,
``http://0.0.0.0:6541/manage/@@contents`` is the URL for seeing the
folder contents. The ``@@`` is a way to ensure that you point at the
URL for a *view* and not get some resource with the ``__name__`` of
``contents``. You can still get to the folder contents management view
using ``http://0.0.0.0:6541/manage/contents``...until that folder
contains something names ``contents``.

``mgmt_view`` View Predicates
=============================

Since ``mgmt_view`` is an extension of Pyramid's ``view_config``,
it re-uses the same concept of view predicates as well as some of the
same actual predicates:

- ``request_type``, ``request_method``, ``request_param``,
  ``containment``, ``attr``, ``renderer``, ``wrapper``, ``xhr``,
  ``accept``, ``header``, ``path_info``, ``context``, ``name``,
  ``custom_predicates``, ``decorator``, ``mapper``, and ``http_cache``
  are supported and behave the same.

- ``permission`` is the same but defaults to ``sdi.view``.

The following are new view predicates introduced for ``mgmt_view``:

- ``tab_title`` takes a string for the label placed on the tab.

- ``tab_condition`` takes a callable that returns ``True`` or ``False``,
  or ``True`` or ``False``. If you state a callable, this callable is
  passed ``context`` and ``request``. The boolean determines whether the
  tab is listed in a certain situation.

- ``tab_before`` takes the view name of a ``mgmt_view`` that this ``mgmt_view``
  should appear after (covered in detail in the next section.)

- ``tab_after`` takes the view name of a ``mgmt_view``
  that this ``mgmt_view`` should appear after. Also covered below.

- ``tab_near`` takes a "sentinel" from ``substanced.sdi`` (or ``None``) that
  makes a best effort at placement independent of another particular
  ``mgmt_view``. Also covered below. The possible sentinel values are::

    substanced.sdi.LEFT
    substanced.sdi.MIDDLE
    substanced.sdi.RIGHT


Tab Ordering
============

If you register a management view, a tab will be added in the list of tabs. If
no mgmt view specifies otherwise via its tab data, the tab order will use a
default sorting: alphabetical order by the ``tab_title`` parameter of each tab
(or the view name if no ``tab_title`` is provided.) The first tab in this tab
listing acts as the "default" that is open when you visit a resource. Substance
D does, though, give you some options to control tab ordering in larger systems
with different software registering management views.

Perhaps a developer wants to ensure that one of her tabs appears first in the
list and another appears last, no matter what other management views have been
registered by Substance D or any add-on packages. ``@mgmt_view`` (or the
imperative call) allow a keyword of ``tab_before`` or ``tab_after``. Each take
the string tab ``name`` of the management view to place before or after.  If
you don't care (or don't know) which view name to use as a ``tab_before`` or
``tab_after`` value, use ``tab_near``, which can be any of the sentinel values
:attr:`~substanced.sdi.MIDDLE`, :attr:`~substanced.sdi.LEFT`, or
:attr:`~substanced.sdi.RIGHT`, each of which specifies a target "zone" in the
tab order.  Substance D will make a best effort to do something sane with ``
tab_near``.

As in many cases, an illustration is helpful:

.. code-block:: python

    from substanced.sdi import LEFT, RIGHT

    @mgmt_view(
        name='tab_1',
        tab_title='Tab 1',
        renderer='templates/tab.pt'
        )
    def tab_1(context, request):
        return {}


    @mgmt_view(
        name='tab_2',
        tab_title='Tab 2',
        renderer='templates/tab.pt',
        tab_before='tab_1'
        )
    def tab_2(context, request):
        return {}


    @mgmt_view(
        name='tab_3',
        tab_title='Tab 3',
        renderer='templates/tab.pt',
        tab_near=RIGHT
        )
    def tab_3(context, request):
        return {}


    @mgmt_view(
        name='tab_4',
        tab_title='Tab 4',
        renderer='templates/tab.pt',
        tab_near=LEFT
        )
    def tab_4(context, request):
        return {}


    @mgmt_view(
        name='tab_5',
        tab_title='Tab 5',
        renderer='templates/tab.pt',
        tab_near=LEFT
        )
    def tab_5(context, request):
        return {}

This set of management views (combined with the built-in Substance D
management views for ``Contents`` and ``Security``) results in::

  Tab 4 | Tab 5 | Contents | Security | Tab 2 | Tab 1 | Tab 3

These management view arguments apply to any content type that the view
is registered for. What if you want to allow a content type to
influence the tab ordering? As mentioned in the
:doc:`content type docs <content>`, the ``tab_order`` parameter
overrides the mgmt_view tab settings, for a content type, with a
sequence of view names that should be ordered (and everything
not in the sequence, after.)

Filling Slots
=============

Each management view that you write plugs into various parts of the SDI
UI. This is done using normal ZPT ``fill-slot`` semantics:

- ``page-title`` is the ``<title>`` in the ``<head>``

- ``head-more`` is a place to inject CSS and JS in the ``<head>``
  *after* all the SDI elements

- ``tail-more`` does the same, just before the ``</body>``

- ``main`` is the main content area

SDI API
=======

All templates in the SDI share a common "layout". This layout needs
information from the environment to render markup that is common to
every screen, as well as the template used as the "main template."

This "template API" is known as the ``SDI API``. It is an instance of
the ``sdiapi`` class in ``substanced.sdi.__init__.py`` and is made
available as ``request.sdiapi``.

The template for your management view should start with a call to
``requests.sdiapi``:

.. code-block:: xml

  <div metal:use-macro="request.sdiapi.main_template">

The ``request.sdiapi`` object has other convenience features as well.
See the Substance D interfaces documentation for more information.

Flash Messages
==============

Often you perform an action on one view that needs a message displayed
by another view on the next request. For example, if you delete a
resource, the next request might confirm to the user "Deleted 1
resource." Pyramid supports this with "flash messages."

In Substance D, your applications can make a call to the ``sdiapi``
such as::

  request.sdiapi.flash('ACE moved up')

...and the next request will process this flash message:

- The message will be removed from the stack of messages

- It will then be displayed in the appropriate styling based on the
  "queue"

The ``sdiapi`` provides another helper:

  request.sdiapi.flash_with_undo('ACE moved up')

This displays a flash message as before, but also provides an ``Undo``
button to remove the previous transaction.

- title, content, flash messages, head, tail
