===========================
Configuring Folder Contents
===========================

The folder contents, as mentioned previously in
:ref:`sdi-folder-contents`, the SDI's folder contents uses a powerful
datagrid to view and manage items in a folder. This chapter covers how
your content types can plug into the folder contents view.

Adding Columns
==============

Perhaps your system has content types with extra attributes that are
meaningful and you'd like your contents listings to show that column.
You can change the columns available on folder contents listings by
passing in a ``columns`` argument to the ``@content`` directive. The
value of this argument is a callable which returns a sequence of
mappings conforming to the datagrid's contract. For example:

.. code-block:: python

    def binder_columns(folder, subobject, request, default_columnspec):
        subobject_name = getattr(subobject, '__name__', str(subobject))
        objectmap = find_objectmap(folder)
        user_oid = getattr(subobject, 'creator', None)
        created = getattr(subobject, 'created', None)
        modified = getattr(subobject, 'modified', None)
        if user_oid is not None:
            user = objectmap.object_for(user_oid)
            user_name = getattr(user, '__name__', 'anonymous')
        else:
            user_name = 'anonymous'
        if created is not None:
            created = created.isoformat()
        if modified is not None:
            modified = modified.isoformat()
        return default_columnspec + [
            {'name': 'Title',
            'value': getattr(subobject, 'title', subobject_name),
            },
            {'name': 'Created',
            'value': created,
            'formatter': 'date',
            },
            {'name': 'Last edited',
            'value': modified,
            'formatter': 'date',
            },
            {'name': 'Creator',
            'value': user_name,
            }
            ]

    @content(
        'Binder',
        icon='icon-book',
        add_view='add_binder',
        propertysheets = (
            ('Basic', BinderPropertySheet),
            ),
        columns=binder_columns,
        )

The callable is passed the folder, a subobject, the ``request``,
and a set of default column specifications. To display the datagrid
column headers, your callable is invoked on the first resource.
Later, this callable is used to get the value for the fields of each
column for each resource in a request's batch.

The mappings returned can indicate whether a particular column should be
sorted.  If you want your column to be sortable, you must provide a ``sorter``
key in the mapping.  If supplied, the ``sorter`` value must either be ``None``
if the column is not sortable, or a function which accepts a resource (the
folder), a "resultset", a ``limit`` keyword argument, and a ``reverse`` keyword
argument and which must return a sorted result set.  Here's an example sorter:

.. code-block:: python

    from substanced.util import find_index

    def sorter(folder, resultset, reverse=False, limit=None):
        index = find_index(folder, 'mycatalog', 'date')
        if index is not None:
            resultset = resultset.sort(index, reverse=reverse, limit=limit)
        return resultset

    def my_columns(folder, subobject, request, default_columnspec):
        return default_columnspec + [
            {'name': 'Date',
            'value': getattr(subobject, 'title', subobject_name),
            'sorter': 'sorter',
            },

Most often, sorting is done by passing a catalog index into the resultset.sort
method as above (resultset.sort returns another resultset), but sorting can be
performed manually, as long as the sorter returns a resultset.

Buttons
=======

As we just showed, you can extend the folder contents with extra
columns to display and possibly sort on. You can also add new buttons
that will trigger operations on selected resources.

As with columns, we pass a new argument to the ``@content`` directive.
For example, the folder contents view for the catalogs folder allows you
to reindex multiple indexes at once:

.. image:: images/catalog_contents.png

The ``Reindex`` button illustrates a useful facility for performing
many custom operations at once.

The :py:mod:`substanced.catalog` module's ``@content`` directive has a
``buttons`` argument:

.. code-block:: python

    @content(
        'Catalog',
        icon='icon-search',
        service_name='catalog',
        buttons=catalog_buttons,
        )

This points at a callable:

.. code-block:: python

    def catalog_buttons(context, request, default_buttons):
        """ Show a reindex button before default buttons in the folder contents
        view of a catalog"""
        buttons = [
            {'type':'single',
             'buttons':
             [
                 {'id':'reindex',
                  'name':'form.reindex',
                  'class':'btn-primary btn-sdi-sel',
                  'value':'reindex',
                  'text':'Reindex'}
                 ]
             }
            ] + default_buttons
        return buttons

In this case, the ``Reindex`` button was inserted before the other
buttons, in the place where an add button would normally appear.

The ``class`` on your buttons affect behavior in the datagrid:

- ``btn-primary`` gives this button the styling for the primary button
  of a form, using Twitter Bootstrap form styling

- ``btn-sdi-act`` makes the button always enabled

- ``btn-sdi-sel`` disables the button until one or more items are
  selected

- ``btn-sdi-one`` disables the button until exactly one item is selected

- ``btn-sdi-del`` disables the button if any of the selected resources
  is marked as "non-deletable" (discussed below)

When clicked, this button will do a form ``POST`` of the selected
docids to a view that you have implemented. Which view? The
``'name': 'form.reindex'`` item sets the parameter on the POST. You can
then register a view against this.
:py:mod:`substanced.catalog.views.catalog` shows this:

.. code-block:: python

    @mgmt_view(
        context=IFolder,
        content_type='Catalog',
        name='contents',
        request_param='form.reindex',
        request_method='POST',
        renderer='substanced.folder:templates/contents.pt',
        permission='sdi.manage-contents',
        tab_condition=False,
        )
    def reindex_indexes(context, request):
        toreindex = request.POST.getall('item-modify')
        if toreindex:
            context.reindex(indexes=toreindex, registry=request.registry)
            request.session.flash(
                'Reindex of selected indexes succeeded',
                'success'
                )
        else:
            request.session.flash(
                'No indexes selected to reindex',
                'error'
                )

        return HTTPFound(request.sdiapi.mgmt_path(context, '@@contents'))

Selection and Button Enabling
=============================

As mentioned above, some buttons are driven by the selection. If
nothing is selected, the button is disabled.

Buttons can also be disabled if any selected item is "non-deletable".
How does that get signified? An item is 'deletable' if the user has
the ``sdi.manage-contents`` permission on ``folder`` *and* if the
subobject has a ``__sdi_deletable__`` attribute which resolves to a
boolean ``True`` value.

It is also possible to make button enabling and disabling depend on some
application-specific condition. To do this, assign a callable to the
``enabled_for`` key in the button spec. For example:

.. code-block:: python

    def catalog_buttons(context, request, default_buttons):
        def is_indexable(folder, subobject, request):
            """ only enable the button if subobject is indexable """
            return subobject.is_indexable()

        buttons = [
            {'type':'single',
             'buttons':
             [
                 {'id':'reindex',
                  'name':'form.reindex',
                  'class':'btn-primary btn-sdi-sel',
                  'value':'reindex',
                  'enabled_for': is_indexable,
                  'text':'Reindex'}
                 ]
             }
            ] + default_buttons
        return buttons

In the example above, we define a button similar to our previous reindex
button, except this time we have an ``enabled_for`` key that is assigned
the ``is_indexable`` function. When the buttons are rendered, each element
is passed to this function, along with the folder and request. If *any one*
of the folder subobjects returns ``False`` for this call, the button will
not be enabled.

Filtering What Can Be Added
===========================

Not all kinds of resources make sense to be added inside a certain kind
of container. For example, :py:class:`substanced.catalog.Catalog`
is a content type that can hold only indexes. That is,it isn't meant to
hold any arbitrary kind of thing.

To tell the SDI what can be added inside a container content type, add a
``__sdi_addable__`` method to your content type. This method is passed the
folder object representing the place the object might be added, and a Substance
D :term:`pyramid:introspectable` for a content type.  When Substance D tries to
figure out whether an object is addable to a particular folder, it will call
the ``__sdi_addable__`` method of your folderish type once for each content
type.

The introspectable is a dictionary-like object which contains information about
the content type.  The introspectable contains the following keys:

``meta``
  A dictionary representing "meta" values passed to
  :func:`~substanced.content.add_content_type`.  For example, if you pass
  ``add_view='foo'`` to :func:`~substanced.content.add_content_type`, the
  ``meta`` of the content type will be ``{'add_view':'foo'}``.

``content_type``
  The content type value passed to :func:`~substanced.content.add_content_type`.

``factory_type``
  The ``factory_type`` value passed to
  :func:`~substanced.content.add_content_type`.

``original_factory``
  The original content factory (without any wrapping) passed to
  :func:`~substanced.content.add_content_type`.

``factory``
  The potentially wrapped content factory derived from the original factory in
  :func:`~substanced.content.add_content_type`.

See :ref:`registering_content` for more information about content type
registration and what the above introspectable values mean.

Your ``__sdi_addable__`` method can perform some logic using the values it is
passed, and then it must return a filtered sequence.

As an example, the ``__sdi_addable__`` method on the ``Catalog``
filters out the kinds of things that can be added in a catalog.

Extending Which Columns Are Displayed
=====================================

The folder contents grid displays a number of columns by default. If
you are managing content with custom properties, in some cases you want
to list those properties in the columns the grid can display. You can
do so on custom folder content types by adding a ``columns`` argument
to your ``@content`` decorator.

As an example, imagine a ``Binder`` kind of container. It has a content
type declaration:

.. code-block:: python

    @content(
        'Binder',
        icon='icon-book',
        add_view='add_binder',
        propertysheets = (
            ('Basic', BinderPropertySheet),
            ),
        columns=binder_columns,
        )

The ``binder_columns`` points to a callable where we perform the work
to both add the column to the list of columns, but also specify how to
get the row data for that column:

.. code-block:: python

    def binder_columns(folder, subobject, request, default_columnspec):
        subobject_name = getattr(subobject, '__name__', str(subobject))
        objectmap = find_objectmap(folder)
        user_oid = getattr(subobject, 'creator', None)
        created = getattr(subobject, 'created', None)
        modified = getattr(subobject, 'modified', None)
        if user_oid is not None:
            user = objectmap.object_for(user_oid)
            user_name = getattr(user, '__name__', 'anonymous')
        else:
            user_name = 'anonymous'
        if created is not None:
            created = created.isoformat()
        if modified is not None:
            modified = modified.isoformat()
        return default_columnspec + [
            {'name': 'Title',
            'value': getattr(subobject, 'title', subobject_name),
            },
            {'name': 'Created',
            'value': created,
            'formatter': 'date',
            },
            {'name': 'Last edited',
            'value': modified,
            'formatter': 'date',
            },
            {'name': 'Creator',
            'value': user_name,
            }
            ]

Here we add four columns to the standard set of grid columns,
whenever we are in a ``Binder`` folder.

Adding New Folder Contents Buttons
==================================

The grid in folder contents makes it easy to select multiple resources
then click a button to perform an action. Wouldn't it be great, though,
if we could add a new button to all or certain folders,
to perform custom actions?

In the previous section we saw how to pass another argument to the
``@content`` decorator. We do the same for new buttons. A content type
can pass in ``buttons=callable`` to modify the list of buttons on a
particular kind of folder.

For example, the :py:func:`substanced.catalog.catalog_buttons` callable
adds a new ``Reindex`` button in front of the standard set of buttons:

.. code-block:: python

    def catalog_buttons(context, request, default_buttons):
        """ Show a reindex button before default buttons in the folder contents
        view of a catalog"""
        buttons = [
            {'type':'single',
             'buttons':
             [
                 {'id':'reindex',
                  'name':'form.reindex',
                  'class':'btn-primary btn-sdi-sel',
                  'value':'reindex',
                  'text':'Reindex'}
                 ]
             }
            ] + default_buttons
        return buttons

The button is disabled until one or more resources are selected which
have the correct permission (discussed above.) If our new button is
clicked, the form is posted with the ``form.reindex`` value in post
data. You can then make a ``@mgmt_view`` with
``request_param='form.reindex'`` in the declaration to handle the form
post when that button is clicked.
