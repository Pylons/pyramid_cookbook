import functools
import itertools
import re

import colander
import venusian

from pyramid.decorator import reify
from pyramid.httpexceptions import HTTPFound
from pyramid.security import has_permission
from pyramid.util import action_method

from substanced.form import FormView
from substanced.interfaces import IFolder
from substanced.objectmap import find_objectmap
from substanced.schema import Schema
from substanced.util import (
    JsonDict,
    get_oid,
    find_catalog,
    get_icon_name,
    )
from substanced._compat import u

from ..sdi import (
    mgmt_view,
    sdi_add_views,
    )

from . import FolderKeyError

_marker = object()


class folder_contents_views(object):
    """ Decorator which causes a set of custom folder contents views to be
    added to the system; declarative variant of
    ``config.add_folder_contents_views``. Accepts the same arguments as
    ``add_folder_contents_views`` in its constructor, e.g.::

      from substanced.sdi,folder import (
          FolderContents,
          folder_contents_views,
          )
      
      @folder_contents_views(name='mycontents')
      class MyFolderContents(FolderContents):
          pass

    This is equivalent to imperatively registering new folder contents views
    like so::

      config.add_folder_contents_views(
          cls=MyFolderContents, name='mycontents'
          )

    Like ``view_config``, and ``mgmt_view``, the decorator must be found via a
    scan to have any effect.
    
    """
    venusian = venusian # for testing injection
    def __init__(self, **settings):
        self.settings = settings

    def __call__(self, wrapped):
        settings = self.settings.copy()
        depth = settings.pop('_depth', 0)
        
        def callback(context, name, ob):
            config = context.config.with_package(info.module)
            config.add_folder_contents_views(cls=ob, **settings)

        info = self.venusian.attach(
            wrapped,
            callback,
            category='substanced',
            depth=depth+1
            )

        settings['_info'] = info.codeinfo # fbo "action_method"
        return wrapped

def rename_duplicated_resource(context, name):
    """Finds next available name inside container by appending
    dash and positive number.
    """
    if name not in context:
        return name

    m = re.search(r'-(\d+)$', name)
    if m:
        new_id = int(m.groups()[0]) + 1
        new_name = name.rsplit('-', 1)[0] + u('-%d') % new_id
    else:
        new_name = name + u('-1')

    if new_name in context:
        return rename_duplicated_resource(context, new_name)
    else:
        return new_name

@colander.deferred
def name_validator(node, kw):
    context = kw['request'].context

    def namecheck(node, value):
        try:
            context.check_name(value)
        except Exception as e:
            raise colander.Invalid(node, e.args[0], value)

    return colander.All(
        colander.Length(min=1, max=100),
        namecheck,
        )

class AddFolderSchema(Schema):
    name = colander.SchemaNode(
        colander.String(),
        validator=name_validator,
        )

@mgmt_view(
    context=IFolder,
    name='add_folder',
    tab_condition=False,
    permission='sdi.add-content',
    renderer='substanced.sdi:templates/form.pt'
    )
class AddFolderView(FormView):
    title = 'Add Folder'
    schema = AddFolderSchema()
    buttons = ('add',)

    def add_success(self, appstruct):
        registry = self.request.registry
        name = appstruct['name']
        folder = registry.content.create('Folder')
        self.context[name] = folder
        return HTTPFound(location=self.request.sdiapi.mgmt_path(self.context))

@folder_contents_views()
class FolderContents(object):
    """ The default folder contents views class """

    sdi_add_views = staticmethod(sdi_add_views) # for testing
    minimum_load = 40

    def __init__(self, context, request):
        self.context = context
        self.request = request
        
    def get_default_buttons(self):
        """ The default buttons content-type hook """
        context = self.context
        request = self.request
        
        buttons = []
        finish_buttons = []

        if 'tocopy' in request.session:
            finish_buttons.extend(
                [
                {'id': 'copy_finish',
                  'name': 'form.copy_finish',
                  'class': 'btn-primary btn-sdi-act',
                  'value': 'copy_finish',
                  'text': 'Copy here'},
                {'id': 'cancel',
                 'name': 'form.copy_finish_cancel',
                 'class': 'btn-danger btn-sdi-act',
                 'value': 'cancel',
                 'text': 'Cancel'},
                ])

        if 'tomove' in request.session:
            finish_buttons.extend(
                [{'id': 'move_finish',
                  'name': 'form.move_finish',
                  'class': 'btn-primary btn-sdi-act',
                  'value': 'move_finish',
                  'text': 'Move here'},
                 {'id': 'cancel',
                  'name': 'form.move_finish_cancel',
                  'class': 'btn-danger btn-sdi-act',
                  'value': 'cancel',
                  'text': 'Cancel'}])

        if finish_buttons:
            buttons.append(
              {'type':'single', 'buttons':finish_buttons}
              )

        if not 'tomove' in request.session and not 'tocopy' in request.session:

            can_manage = bool(
                has_permission('sdi.manage-contents', context, request)
                )

            def delete_enabled_for(folder, resource, request):
                """
                This function considers a subobject 'deletable' if the user has
                the ``sdi.manage-contents`` permission on ``folder`` or if the
                subobject has a ``__sdi_deletable__`` attribute which resolves
                to a boolean ``True`` value.

                This function honors one subobject hook::
                ``__sdi_deletable__``.  If a subobject has an attribute named
                ``__sdi_deletable__``, it is expected to be either a boolean or
                a callable.  If ``__sdi_deletable__`` is a boolean, the value
                is used verbatim.  If ``__sdi_deletable__`` is a callable, the
                callable is called with two positional arguments: the subobject
                and the request; the result is expected to be a boolean.  If a
                subobject has an ``__sdi_deletable__`` attribute, and its
                resolved value is not ``None``, the delete button will be off
                if it's a boolean False.  If ``__sdi_deletable__`` does not
                exist on a subobject or resolves to ``None``, the delete button
                will be turned off if current user does not have the
                ``sdi.manage-contents`` permission on the ``folder``.
                """
                deletable = getattr(resource, '__sdi_deletable__', None)
                if deletable is not None:
                    if callable(deletable):
                        deletable = deletable(resource, request)
                if deletable is None:
                    deletable = can_manage
                deletable = bool(deletable) # cast return/attr value to bool
                return deletable

            main_buttons = [
                 {'id': 'rename',
                  'name': 'form.rename',
                  'class': 'btn-sdi-sel',
                  'enabled_for':delete_enabled_for,
                  'value': 'rename',
                  'text': 'Rename'},
                  {'id': 'copy',
                  'name': 'form.copy',
                  'class': 'btn-sdi-sel',
                  'value': 'copy',
                  'text': 'Copy'},
                  {'id': 'move',
                  'name': 'form.move',
                  'class': 'btn-sdi-sel',
                  'enabled_for':delete_enabled_for,
                  'value': 'move',
                  'text': 'Move'},
                  {'id': 'duplicate',
                  'name': 'form.duplicate',
                  'class': 'btn-sdi-sel',
                  'value': 'duplicate',
                  'text': 'Duplicate'}
                  ]

            buttons.append({'type': 'group', 'buttons':main_buttons})

            delete_buttons = [
                  {'id': 'delete',
                   'name': 'form.delete',
                   'class': 'btn-danger btn-sdi-sel',
                   'enabled_for':delete_enabled_for,
                   'value': 'delete',
                   'text': 'Delete'},
                   ]

            buttons.append({'type': 'group', 'buttons':delete_buttons})

        return buttons

    def get_buttons(self):
        context = self.context
        request = self.request
        defaults = self.get_default_buttons()
        buttonsfn = request.registry.content.metadata(
            context,
            'buttons',
            _marker
            )
        if buttonsfn is None:
            return []
        if buttonsfn is _marker:
            return defaults
        else:
            return buttonsfn(context, request, defaults)

    def get_default_columns(self, resource):
        request = self.request
        name = getattr(resource, '__name__', '')
        icon = get_icon_name(resource, request) or ''
        url = request.sdiapi.mgmt_path(resource, '@@manage_main')
        value = '<i class="%s"> </i> <a href="%s">%s</a>' % (icon, url, name)
        columns = [
            {'name': 'Name',
             'value': value,
             'formatter': 'html',
             'sorter': self._name_sorter}
            ]
        return columns

    def get_columns(self, resource):
        context = self.context
        request = self.request
        defaults = self.get_default_columns(resource)
        columnsfn = request.registry.content.metadata(
            context,
            'columns',
            _marker
            )
        if columnsfn is None:
            return []
        if columnsfn is _marker:
            return defaults
        else:
            return columnsfn(context, resource, request, defaults)

    def get_options(self):
        # #33, allow overriding the grid's rowHeight among other
        # grid options. Like get_columns, you subclass to let a
        # custom contents view change the behavior of the grid.

        return dict(
            editable=False,
            enableAddRow=False,
            enableCellNavigation=True,
            asyncEditorLoading=True,
            forceFitColumns=True,
            rowHeight=35,
            )

    def get_default_query(self):
        """ The default query function for a folder """
        system_catalog = self.system_catalog
        folder = self.context
        request = self.request
        path = system_catalog['path']
        allowed = system_catalog['allowed']
        q = ( path.eq(folder, depth=1, include_origin=False) &
              allowed.allows(request, 'sdi.view') )
        return q

    get_query = get_default_query

    @reify
    def system_catalog(self):
        return find_catalog(self.context, 'system')

    def modified_items(self):
        items = self.request.POST.get('item-modify', '').split('/')
        modified = [x for x in  items if x] # remove empty
        return modified

    def get_filter_values(self):
        request = self.request
        filter_values = []
        for k, v in request.params.items():
            if v and k.startswith('filter'):
                name = k[6:]
                if name.startswith('.'):
                    name = name[1:]
                filter_values.append((name, v))
        return filter_values

    def get_redirect_response(self):
        request = self.request
        context = self.context
        qs = [ ('filter.' + k, v) for k, v in self.get_filter_values() ]
        return HTTPFound(
            request.sdiapi.mgmt_path(context, '@@' + request.view_name,
                                     _query=qs)
            )

    def show_checkbox_column(self, button_groups, columns, resultset):
        show_checkbox_column = False
        for button_group in button_groups:
            if len(button_group.get('buttons', [])):
                show_checkbox_column = True
        return show_checkbox_column

    def _name_sorter(self, resource, resultset, limit=None, reverse=False):
        index = self.system_catalog.get('name')
        if index is not None:
            resultset = resultset.sort(index, limit=limit, reverse=reverse)
        return resultset

    def _column_headers(self, columns):
        is_ordered = self.context.is_ordered()

        headers = []

        for order, column in enumerate(columns):
            name = column['name']
            sortable = column.get('sorter', None) is not None
            if sortable and not column.get('resortable', True):
                # allow column to specify a sorter but claim it's not resortable
                sortable = False

            if is_ordered:
                # We don't currently allow ordered folders to be resorted by
                # columns
                sortable = False

            formatter = column.get('formatter', '')
            editor = column.get('editor', '')
            validator = column.get('validator', '')
            width = int(column.get('width', 120))
            min_width = int(column.get('min_width', 120))

            css_class = column.get('css_class', '')
            css_name = name.replace(' ', '-')
            css_class = ("cell-%s %s" % (css_name, css_class)).strip()

            # XXX CM: Do we really need all of "id", "name", and "field" below?
            # Ree XXX RB The names are a bit messed up, the way slickgrid
            # defines them.  We probably only need 2 of id, name, field (the
            # field identifier called 'field', and the field label that is
            # called 'name') and could generate the third one on the client.

            headers.append({
                "id": name,
                "name": name,
                "field": name,
                "width": width,
                "minWidth": min_width,
                "cssClass": css_class,
                "sortable": sortable,
                "formatterName": formatter,
                "editorName": editor,
                "validatorName": validator,
            })

        return headers

    def _sort_info(self, columns, sort_column_name=None):
        context = self.context

        sort_column = None
        sorter = None
        
        # Is the folder content ordered?
        is_ordered = context.is_ordered()

        if is_ordered:
            # If the folder is ordered, use the folder itself as the sort
            # index; ordered folders cannot currently be viewed reordered
            # by anything except their explicit ordering.
            def sorter(folder, resultset, reverse=False, limit=None):
                return resultset.sort(folder, limit=limit, reverse=reverse)

        elif sort_column_name is None:
            # The default sort always uses the intitial_sort_column, defaulting
            # to the first column with a sorter if no initial_sort_colun is
            # found
            first = True
            for col in columns:
                if col.get('sorter'):
                    if first is True or col.get('initial_sort_column'):
                        sort_column_name = col['name']
                        sort_column = col
                        first = False

        else:
            # Nondefault sort column
            for col in columns:
                if col.get('name') == sort_column_name:
                    sort_column = col
                    break

        if sort_column is not None:
            sorter = sort_column['sorter']
            
        return {
            'column':sort_column,
            'column_name':sort_column_name,
            'sorter':sorter,
            }
   
    def _global_text_filter(self, context, filter_text, q):
        filter_text_globs = [x for x in filter_text.split() if x]
        if filter_text_globs:
            text = self.system_catalog['text']
            for filter_glob in filter_text_globs:
                if not filter_glob.endswith('*'):
                    filter_glob = filter_glob + '*' # glob (prefix) search
                if text.check_query(filter_glob):
                    q = q & text.eq(filter_glob)
        return q
    
    def _folder_contents(
        self,
        start=None,
        end=None,
        reverse=None,
        sort_column_name=None,
        filter_values=(),
        ):

        """
        Returns a dictionary containing:

        ``length``

          The folder's length (ie. `len(folder)`)
          
        ``records``

          A sequence of dictionaries that represent the folder's subobjects.
          The sequence is implemented as a generator.  Each dictionary in the
          ``records`` sequence reflects information about a single subobject in
          the folder, and will have the following keys:

          ``name``

            The name of the subobject.

          ``url``

            The URL to the subobject.  This will be
            ``/path/to/subob/@@manage_main``.

          ``columns``

            The column values obtained from this subobject's attributes, as
            defined by the ``columns`` content-type hook (or the default
            columns, if no hook was supplied).
          
        ``sort_column_name``

          The crrent sort_column_name

        ``sort_reverse``

          True if the current sort should be reversed.

        ``columns``

          A sequence of column header values.
        
        XXX TODO Document ``sort_column_name``, ``reverse``, and
        ``filter_values`` arguments.  Document ``columns`` return value.
        """
        folder = self.context
        request = self.request
        objectmap = find_objectmap(folder)

        if start is None:
            start = 0

        if end is None:
            end = start + self.minimum_load

        q = self.get_query()

        columns = self.get_columns(None)

        for name, value in filter_values:
            if name:
                for col in columns:
                    if col['name'] == name:
                        filt = col.get('filter')
                        if filt is not None:
                            q = filt(folder, value, q)
            else:
                q = self._global_text_filter(folder, value, q)

        resultset = q.execute()
        # NB: must take snapshot of folder_length before limiting the length
        # of the resultset via any sort
        folder_length = len(resultset)

        sort_info = self._sort_info(
            columns,
            sort_column_name=sort_column_name,
            )

        sorter = sort_info['sorter']
        sort_column_name = sort_info['column_name']
        if reverse is None:
            reverse = False
            column = sort_info['column']
            if column:
                reverse = column.get('initial_sort_reverse', False)

        if sorter is not None:
            resultset = sorter(
                folder, resultset, reverse=reverse, limit=end
                )

        ids = resultset.ids

        buttons = self.get_buttons()
        show_checkbox_column = self.show_checkbox_column(
            buttons, columns, resultset)

        records = []

        for oid in itertools.islice(ids, start, end):
            resource = objectmap.object_for(oid)
            name = getattr(resource, '__name__', '')
            record = dict(
                # Use the unique name as an id.  (A unique row id is needed
                # for slickgrid.  In addition, we will pass back this same id
                # from the client, when a row is selected for an operation.)
                id=name,
                name=name,
                )
            cols = self.get_columns(resource)
            for col in cols:
                # XXX CM: adding arbitrary keys to the record based on
                # configuration input is a bad idea here because we can't
                # guarantee a column name won't override the "reserved" names
                # (name, id) added to the record above.  Ree?
                cname = col['name']
                record[cname] = col['value']
            disable = []
            for button_group in buttons:
                for button in button_group['buttons']:
                    if 'enabled_for' not in button:
                        continue
                    condition = button['enabled_for']
                    if not callable(condition):
                        continue
                    if not condition(folder, resource, request):
                        disable.append(button['id'])
            record['disable'] = disable
            records.append(record)

        return {
            'length':folder_length,
            'records':records,
            'sort_column_name':sort_column_name,
            'sort_reverse':reverse,
            'columns':columns,
            'show_checkbox_column':show_checkbox_column,
            }

    def show(self):
        request = self.request
        context = self.context

        buttons = self.get_buttons()

        addables = self.sdi_add_views(context, request)

        # construct the default slickgrid widget options
        slickgrid_options = self.get_options()

        is_reorderable = context.is_reorderable()

        end = self.minimum_load # load at least this many records.
        start = 0 # start at record number zero

        filter_values = self.get_filter_values()
        folder_contents = self._folder_contents(
            start,
            end,
            filter_values=filter_values
            )

        records = folder_contents['records']
        folder_length = folder_contents['length']
        sort_column_name = folder_contents['sort_column_name']
        sort_reverse = folder_contents['sort_reverse']
        show_checkbox_column = folder_contents['show_checkbox_column']
        column_headers = self._column_headers(folder_contents['columns'])

        items  = {
            'from':start,
            'to':end,
            'records':records,
            'total':folder_length,
            }

        # We pass the wrapper options which contains all information
        # needed to configure the several components of the grid config.

        slickgrid_wrapper_options = JsonDict(
            # below line refers to slickgrid-config.js
            configName = 'sdi-content-grid',
            columns = column_headers,
            slickgridOptions = slickgrid_options,
            items = items,
            # initial sorting (The grid will really not sort the initial data,
            # just display it in the order we provide it. It will use the
            # information to just visually show in the headers the sorted
            # column.)
            sortCol = sort_column_name,
            sortDir = (not sort_reverse),
            # is the grid reorderable?
            isReorderable = is_reorderable,
            #
            # Parameters for the remote data model
            url = '',   # use same url for ajax
            minimumLoad = end,
            showCheckboxColumn = show_checkbox_column,
            # csrf needed for post requests
            csrfToken = request.session.get_csrf_token(),
            )

        result = dict(
            addables = addables,
            buttons = buttons,
            slickgrid_wrapper_options = slickgrid_wrapper_options,
            )

        return result

    def show_json(self):
        return self._get_json()

    def _get_json(self):
        request = self.request
        if 'from' in request.params:
            start = int(request.params.get('from'))
            end = int(request.params.get('to'))
            sort_column_name = request.params.get('sortCol')
            sort_dir = request.params.get('sortDir') in ('true', 'True')
            filter_values = self.get_filter_values()

            reverse = (not sort_dir)

            folder_contents = self._folder_contents(
                start,
                end,
                reverse=reverse,
                filter_values=filter_values,
                sort_column_name=sort_column_name,
                )

            folder_length = folder_contents['length']
            records = folder_contents['records']

            items = {
                'from': start,
                'to': end,
                'records': records,
                'total': folder_length,
                }
        else:
            # If the request did not ask for an data update,
            # just return an empty dict.
            items = {}

        return items

    def delete(self):
        request = self.request
        context = self.context
        todelete = self.modified_items()
        deleted = 0
        for name in todelete:
            v = context.get(name)
            if v is not None:
                del context[name]
                deleted += 1
        if not deleted:
            msg = 'No items deleted'
            request.session.flash(msg)
        elif deleted == 1:
            msg = 'Deleted 1 item'
            request.sdiapi.flash_with_undo(msg)
        else:
            msg = 'Deleted %s items' % deleted
            request.sdiapi.flash_with_undo(msg)
        return self.get_redirect_response()

    def duplicate(self):
        request = self.request
        context = self.context
        toduplicate = self.modified_items()
        for name in toduplicate:
            newname = rename_duplicated_resource(context, name)
            context.copy(name, context, newname)
        if not len(toduplicate):
            msg = 'No items duplicated'
            request.session.flash(msg)
        elif len(toduplicate) == 1:
            msg = 'Duplicated 1 item'
            request.sdiapi.flash_with_undo(msg)
        else:
            msg = 'Duplicated %s items' % len(toduplicate)
            request.sdiapi.flash_with_undo(msg)
        return self.get_redirect_response()

    def rename(self):
        request = self.request
        context = self.context
        torename = self.modified_items()
        if not torename:
            request.session.flash('No items renamed')
            return self.get_redirect_response()
        return dict(torename=[context.get(name)
                              for name in torename
                              if name in context])

    def rename_finish(self):
        request = self.request
        context = self.context

        if self.request.POST.get('form.rename_finish') == "cancel":
            request.session.flash('No items renamed')
            return self.get_redirect_response()

        torename = request.POST.getall('item-rename')
        try:
            for old_name in torename:
                new_name = request.POST.get(old_name)
                context.rename(old_name, new_name)
        except FolderKeyError as e:
            self.request.session.flash(e.args[0], 'error')
            raise self.get_redirect_response()

        if len(torename) == 1:
            msg = 'Renamed 1 item'
            request.sdiapi.flash_with_undo(msg)
        else:
            msg = 'Renamed %s items' % len(torename)
            request.sdiapi.flash_with_undo(msg)
        return self.get_redirect_response()

    def copy(self):
        request = self.request
        context = self.context
        tocopy = self.modified_items()
        
        if tocopy:
            l = []
            for name in tocopy:
                obj = context.get(name)
                if obj is not None:
                    l.append(get_oid(obj))
            request.session['tocopy'] = l
            request.session.flash('Choose where to copy the items:', 'info')
        else:
            request.session.flash('No items to copy')

        return self.get_redirect_response()

    def copy_finish_cancel(self):
        request = self.request
        del request.session['tocopy']
        request.session.flash('No items copied')
        return self.get_redirect_response()

    def copy_finish(self):
        request = self.request
        context = self.context
        objectmap = find_objectmap(context)
        tocopy = request.session['tocopy']
        del request.session['tocopy']

        num_copied = 0

        try:
            for oid in tocopy:
                obj = objectmap.object_for(oid)
                copied = self.move_here_if_addable(obj, copy=True)
                if copied:
                    num_copied += 1
        except FolderKeyError as e:
            self.request.session.flash(e.args[0], 'error')
            raise self.get_redirect_response()

        if num_copied == 0:
            msg = 'No items copied'
            request.session.flash(msg)
        elif num_copied == 1:
            msg = 'Copied 1 item'
            request.sdiapi.flash_with_undo(msg)
        else:
            msg = 'Copied %s items' % num_copied
            request.sdiapi.flash_with_undo(msg)

        return self.get_redirect_response()

    def move(self):
        request = self.request
        context = self.context
        tomove = self.modified_items()

        if tomove:
            l = []
            for name in tomove:
                obj = context.get(name)
                if obj is not None:
                    l.append(get_oid(obj))
            request.session['tomove'] = l
            request.session.flash('Choose where to move the items:', 'info')
        else:
            request.session.flash('No items to move')

        return self.get_redirect_response()

    def move_finish_cancel(self):
        request = self.request
        del request.session['tomove']
        request.session.flash('No items moved')
        return self.get_redirect_response()

    def move_finish(self):
        request = self.request
        context = self.context
        objectmap = find_objectmap(context)
        tomove = request.session['tomove']
        del request.session['tomove']

        num_moved = 0

        try:
            for oid in tomove:
                obj = objectmap.object_for(oid)
                moved = self.move_here_if_addable(obj)
                if moved:
                    num_moved += 1
        except FolderKeyError as e:
            self.request.session.flash(e.args[0], 'error')
            raise self.get_redirect_response()

        if num_moved == 0:
            msg = 'No items moved'
            request.session.flash(msg)
        elif num_moved == 1:
            msg = 'Moved 1 item'
            request.sdiapi.flash_with_undo(msg)
        else:
            msg = 'Moved %s items' % num_moved
            request.sdiapi.flash_with_undo(msg)

        return self.get_redirect_response()

    def reorder_rows(self):
        request = self.request
        context = self.context
        item_modify = self.modified_items()
        insert_before = request.params.get('insert-before')
        if not insert_before:
            # '' or None means appending after the last item.
            insert_before = None
        context.reorder(item_modify, insert_before)
        msg = '%i rows moved.' % (len(item_modify), )
        msg = request.sdiapi.get_flash_with_undo_snippet(msg)
        results = {
            'flash': msg,
            }
        # Generate content update as requested by the client.
        results.update(self._get_json())
        return results

    def get_addable_content_types(self):
        add_views = self.sdi_add_views(self.context, self.request)
        content_types = set([ x['content_type'] for x in add_views ])
        return content_types

    def move_here_if_addable(self, obj, copy=False):
        request = self.request
        context = self.context
        content_types = self.get_addable_content_types()
        obj_type = request.registry.content.typeof(obj)
        obj_name = obj.__name__
        if obj_type in content_types:
            if copy:
                obj.__parent__.copy(obj_name, context)
            else:
                obj.__parent__.move(obj_name, context)
            return True
        if copy:
            action = 'copied'
        else:
            action = 'moved'
        self.request.session.flash(
            '"%s" is of a type (%s) that is not addable here, not %s' % (
                obj_name, obj_type, action), 'error'
            )
        return False
        
@action_method
def add_folder_contents_views(
    config,
    cls=None,
    name='contents',
    context=None,
    renderer='substanced.folder:templates/contents.pt', # do not abbreviate
    view_permission='sdi.view',
    manage_contents_permission='sdi.manage-contents',
    tab_title=None,
    tab_condition=True,
    tab_before=None,
    tab_after=None,
    tab_near=None,
    **predicates
    ):
    """
    A directive which adds a set of folder contents views.
    
    XXX the below was ripped out of its context from another method's docstring
    and needs to be recontextualized here.
    
    This function honors three content type hooks: ``icon``, ``buttons``,
    and ``columns``.

    The first content type hook is named ``icon``.  If the ``icon``
    supplied to the content type configuration of a subobject is a
    callable, the callable will be passed the subobject and the
    ``request``; it is expected to return an icon name or ``None``.
    ``icon`` may alternately be either ``None`` or a string representing a
    icon name instead of a callable.

    The second content type hook is named ``buttons``.  The folder contents
    view is a good place to wire up application specific functionality that
    depends on content selection, so the button toolbar that shows up at
    the bottom of the page is customizable. The default buttons can be
    overridden by supplying a ``buttons`` keyword argument to the content
    type argument list.  It must be a callable object which accepts
    ``context, request, default_buttonspec`` and which returns a list of
    dictionaries; each dictionary represents a button or a button group.

    The ``buttons`` callable you supply will be passed the ``context`` and
    the ``request`` and ``buttonspec`` (a sequence of default button
    specifications). It must return a list of dictionaries representing
    button specifications with at least a ``type`` key for the button
    specification type and a ``buttons`` key with a list of dictionaries
    representing the buttons. The ``type`` should be one of the string
    values ``group`` or ``single``. A group will display its buttons side
    by side, with no margin, while the single type will display each button
    separately.

    Each button in a ``buttons`` dictionary is rendered using the button
    tag and requires five keys: ``id`` for the button's id attribute,
    ``name`` for the button's name attribute, ``class`` for any additional
    css classes to be applied to it (see below), ``value`` for the value
    that will be passed as a request parameter when the form is submitted
    and ``text`` for the button's text.

    The ``class`` value is special because it will define the button's
    behavior. There are four mutually exclusive class names that can be
    used. ``btn-sdi-act`` is for buttons that will always be enabled,
    independently of any selected content items. ``btn-sdi-sel`` means
    the button will start as disabled and will only be enabled once one
    or more items are selected. ``btn-sdi-one`` means the button will
    only be enabled if there's exactly one item selected. Finally,
    ``btn-sdi-del`` means the button will stay disabled until one or
    more *deletable* items are selected. You *must* use one of these
    classes for the button to be enabled.
    
    The ``class`` value can contain several classes separated by spaces.
    In addition to the classes mentioned above, any custom css class or any
    bootstrap button class can be used.
    
    Finally, each button can optionally include an ``enabled_for`` key,
    which will point to a callable that will be passed a subobject from the
    current folder and must return True if the button should be enabled for
    that subobject or False if not.

    Most of the time, the best strategy for using the buttons callable will
    be to return a value containing the default buttonspec sequence passed
    in to the function (it will be a list).::

      def custom_buttons(context, request, default_buttonspec):
          def some_condition(folder, subobject, request):
              return getattr(context, 'can_use_button1', False)

          custom_buttonspec = [{'type': 'single',
                               'buttons': [{'id': 'button1',
                                            'name': 'button1',
                                            'class': 'btn-sdi-sel',
                                            'enabled_for': some_condition,
                                            'value': 'button1',
                                            'text': 'Button 1'},
                                           {'id': 'button2',
                                            'name': 'button2',
                                            'class': 'btn-sdi-act',
                                            'value': 'button2',
                                            'text': 'Button 2'}]}]
          return default_buttonspec + custom_buttonspec

      @content(
          'My Custom Folder',
          buttons=custom_buttons,
          )
      class MyCustomFolder(Persistent):
          pass

    Once the buttons are defined, a view needs to be registered to handle
    the new buttons. The view configuration has to set Folder as a context
    and include a ``request_param`` predicate with the same name as the
    ``value`` defined for the corresponding button. The following template
    can be used to register such views, changing only the ``request_param``
    value::

      @mgmt_view(
      context=IFolder,
      name='contents',
      renderer='substanced.folder:templates/contents.pt',
      permission='sdi.manage-contents',
      request_method='POST',
      request_param='button1',
      tab_condition=False,
      )
      def button1(context, request):
          # add button functionality here, then go back to contents
          request.session.flash('Just did what button1 does')
          return HTTPFound(request.sdiapi.mgmt_path(context, '@@contents'))

    Note that context has to be IFolder for this to work. If you need to
    restrict a button to some specific list of content types, the Pyramid
    ``content_type`` predicate can be used.

    The third content-type hook is named ``columns``.  To display the
    contents using a table with any given subobject attributes, a callable
    named ``columns`` can be passed to a content type as metadata.  When
    the folder contents SDI view is invoked against an object of the type,
    the ``columns`` callable will be passed the folder, a subobject, the
    ``request``, and a default column specification. It will be called once
    for every object in the folder to obtain column representations for
    each of its subobjects.  It must return a list of dictionaries with at
    least a ``name`` key for the column header and a ``value`` key with
    the correct column value given the subobject. The callable **must** be
    prepared to receive subobjects that will *not* have the desired
    attributes (the subobject passed will be ``None`` at least once in
    order for the system to compute headers).

    In addition to ``name`` and ``value``, the column dictionary may
    contain the keys ``sorter``, ``initial_sort_column``,
    ``initial_sort_reverse``, and ``formatter``. The ``sorter`` will either
    be ``None`` if the column is not sortable, or a callback which accepts
    a resource (the folder), a resultset, a ``limit`` keyword argument, and
    a ``reverse`` keyword argument and which must return a sorted result
    set.  The default ``sorter`` value is ``None``. The
    ``initial_sort_column`` should be the ``True`` if this column should
    be the initial sort column (it must also have a ``sorter``).  If no
    column is marked as the initial sort column, the first column with a
    ``sorter`` will be used as the initial sort column.  The
    ``initial_sort_reverse`` key can be ``True`` or ``False`` if you want
    the initial rendering to be sorted reverse or not.  The last key,
    ``formatter``, can give the name of a javascript method for formatting
    the ``value``.  Currently, available formatters are ``icon_label_url``
    and ``date``.
    
    The ``icon_label_url`` formatter gets the URL and icon (if any) of the
    subobject and creates a link using ``value`` as link text. The ``date``
    formatter expects that ``value`` is an ISO date and returns a text date
    in the format "<month name> <day>, <year>".

    Here's an example of using the ``columns`` content type hook::

      from substanced.util import find_index

      def sorter(folder, resultset, reverse=False, limit=None):
          index = find_index(folder, 'mycatalog', 'date')
          if index is not None:
              resultset = resultset.sort(
                                   index, reverse=reverse, limit=limit)
          return resultset

      def custom_columns(folder, subobject, request, default_columnspec):
          return default_columnspec + [
              {'name': 'Review Date',
               'value': getattr(subobject, 'review_date', ''),
               'sorter': sorter,
               'formatter': 'date'},
              {'name': 'Rating',
               'value': getattr(subobject, 'rating', '')}
              ]

      @content(
          'My Custom Folder',
          columns=custom_columns,
          )
      class MyCustomFolder(Persistent):
          pass
          
    In some cases, it might be needed to override the custom columns
    defined for an already existing content type. This can be accomplished
    by registering the content type a second time, but passing the columns
    then. For example, to add columns to the user folder content listing
    from substanced::
    
      from substanced import root_factory
      from substanced.interfaces import IUsers
      from substanced.principal import Users
      from myapp import custom_user_columns
      
      def main(global_config, **settings):
          config = Configurator(
              root_factory=root_factory,
              settings=settings
              )
          config.include('substanced')
          config.add_content_type(
              IUsers,
              factory=Users,
              icon='icon-list-alt',
              columns=custom_user_columns
              )
          config.scan()

    """

    if cls is None:
        cls = FolderContents

    if context is None:
        context = IFolder
        
    add_fc_view = functools.partial(
        config.add_mgmt_view,
        view=cls,
        name=name,
        renderer=renderer,
        context=context,
        tab_condition=False,
        **predicates
        )

    add_fc_view(
        request_method='GET',
        permission=view_permission,
        tab_condition=tab_condition,
        tab_before=tab_before,
        tab_after=tab_after,
        tab_near=tab_near,
        tab_title=tab_title,
        xhr=False,
        attr='show',
        )
    add_fc_view(
        request_method='GET',
        permission=view_permission,
        xhr=True,
        renderer='json',
        attr='show_json',
        )
    add_fc_view(
        request_method='POST',
        request_param='form.delete',
        permission=manage_contents_permission,
        check_csrf=True,
        attr='delete',
        )
    add_fc_view(
        request_method='POST',
        request_param='form.duplicate',
        permission=manage_contents_permission,
        check_csrf=True,
        attr='duplicate',
        )
    add_fc_view(
        request_method='POST',
        request_param='form.rename',
        permission=manage_contents_permission,
        renderer='templates/rename.pt',
        check_csrf=True,
        attr='rename',
        )
    add_fc_view(
        request_method='POST',
        request_param='form.rename_finish',
        permission=manage_contents_permission,
        check_csrf=True,
        attr='rename_finish',
        )
    add_fc_view(
        request_method='POST',
        request_param='form.copy',
        permission=view_permission,
        check_csrf=True,
        attr='copy',
        )
    add_fc_view(
        request_method='POST',
        request_param='form.copy_finish',
        permission=manage_contents_permission,
        check_csrf=True,
        attr='copy_finish',
        )
    add_fc_view(
        request_method='POST',
        request_param='form.copy_finish_cancel',
        permission=view_permission,
        check_csrf=True,
        attr='copy_finish_cancel',
        )
    add_fc_view(
        request_method='POST',
        request_param='form.move',
        permission=view_permission,
        check_csrf=True,
        attr='move',
        )
    add_fc_view(
        request_method='POST',
        request_param='form.move_finish',
        permission=manage_contents_permission,
        check_csrf=True,
        attr='move_finish',
        )
    add_fc_view(
        request_method='POST',
        request_param='form.move_finish_cancel',
        permission=view_permission,
        check_csrf=True,
        attr='move_finish_cancel',
        )
    add_fc_view(
        request_method='POST',
        renderer='json',
        request_param='ajax.reorder',
        permission=manage_contents_permission,
        check_csrf=True,
        attr='reorder_rows',
        )
        
def includeme(config): # pragma: no cover
    config.add_directive(
        'add_folder_contents_views',
        add_folder_contents_views,
        action_wrap=False
        )
