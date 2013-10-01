import sys
import colander
import unittest

from pyramid import testing
from pyramid.httpexceptions import HTTPFound
import mock

from substanced._compat import u
_FOOBAR = u('foobar')

class Test_name_validator(unittest.TestCase):
    def _callFUT(self, node, kw):
        from ..views import name_validator
        return name_validator(node, kw)

    def _makeKw(self, exc=None):
        request = testing.DummyRequest()
        request.context = DummyContainer(exc)
        return dict(request=request)

    def test_it_exception(self):
        exc = KeyError('wrong')
        kw = self._makeKw(exc)
        node = object()
        v = self._callFUT(node, kw)
        self.assertRaises(colander.Invalid, v, node, 'abc')

    def test_it_no_exception(self):
        kw = self._makeKw()
        node = object()
        v = self._callFUT(node, kw)
        result = v(node, 'abc')
        self.assertEqual(result, None)

class Test_rename_duplicated_resource(unittest.TestCase):
    def _callFUT(self, context, name):
        from ..views import rename_duplicated_resource
        return rename_duplicated_resource(context, name)
        
    def test_rename_first(self):
        context = testing.DummyResource()
        new_name = self._callFUT(context, 'foobar')
        self.assertEqual(new_name, 'foobar')

    def test_rename_second(self):
        context = testing.DummyResource()
        context['foobar'] = testing.DummyResource()
        new_name = self._callFUT(context, 'foobar')
        self.assertEqual(new_name, 'foobar-1')

    def test_rename_twentyfirst(self):
        context = testing.DummyResource()
        context['foobar-21'] = testing.DummyResource()
        new_name = self._callFUT(context, 'foobar-21')
        self.assertEqual(new_name, 'foobar-22')

    def test_rename_multiple_dashes(self):
        context = testing.DummyResource()
        context['foo-bar'] = testing.DummyResource()
        new_name = self._callFUT(context, 'foo-bar')
        self.assertEqual(new_name, 'foo-bar-1')

    def test_rename_take_fisrt_available(self):
        context = testing.DummyResource()
        context['foobar'] = testing.DummyResource()
        context['foobar-1'] = testing.DummyResource()
        context['foobar-2'] = testing.DummyResource()
        context['foobar-4'] = testing.DummyResource()
        new_name = self._callFUT(context, 'foobar')
        self.assertEqual(new_name, 'foobar-3')

class TestAddFolderView(unittest.TestCase):
    def _makeOne(self, context, request):
        from ..views import AddFolderView
        return AddFolderView(context, request)

    def _makeRequest(self, **kw):
        request = testing.DummyRequest()
        request.registry.content = DummyContent(**kw)
        request.sdiapi = DummySDIAPI()
        return request

    def test_add_success(self):
        resource = testing.DummyResource()
        request = self._makeRequest(Folder=resource)
        context = testing.DummyResource()
        inst = self._makeOne(context, request)
        resp = inst.add_success({'name': 'name'})
        self.assertEqual(context['name'], resource)
        self.assertEqual(resp.location, '/mgmt_path')

class TestFolderContents(unittest.TestCase):
    def setUp(self):
        self.config = testing.setUp()

    def tearDown(self):
        testing.tearDown()

    def _makeOne(self, context, request):
        from ..views import FolderContents
        return FolderContents(context, request)

    def _makeRequest(self, **kw):
        request = testing.DummyRequest()
        request.sdiapi = DummySDIAPI()
        request.sdiapi.flash_with_undo = request.session.flash
        request.registry.content = DummyContent(**kw)
        return request

    def _makeCatalogs(self, oids=()):
        catalogs = DummyCatalogs()
        catalog = DummyCatalog(oids)
        catalogs['system'] = catalog
        return catalogs

    def test_get_buttons_is_None(self):
        context = testing.DummyResource()
        request = self._makeRequest(buttons=None)
        inst = self._makeOne(context, request)
        result = inst.get_buttons()
        self.assertEqual(result, [])

    def test_get_buttons_is_clbl(self):
        context = testing.DummyResource()
        def sdi_buttons(context, request, default_buttons):
            return 'abc'
        request = self._makeRequest(buttons=sdi_buttons)
        inst = self._makeOne(context, request)
        result = inst.get_buttons()
        self.assertEqual(result, 'abc')

    def test_get_columns_custom_columns_is_None(self):
        context = testing.DummyResource()
        request = self._makeRequest(columns=None)
        inst = self._makeOne(context, request)
        result = inst.get_columns(None)
        self.assertEqual(result, [])

    def test_get_columns_custom_columns_doesnt_exist(self):
        context = testing.DummyResource()
        request = self._makeRequest()
        inst = self._makeOne(context, request)
        result = inst.get_columns(None)
        self.assertEqual(len(result), 1)
        
    def test_get_columns_custom_columns_exists(self):
        context = testing.DummyResource()
        def columns(context, subobject, request, columns):
            self.assertEqual(len(columns), 1)
            return ['abc', '123', 'def']
        request = self._makeRequest(columns=columns)
        inst = self._makeOne(context, request)
        result = inst.get_columns(None)
        self.assertEqual(len(result), 3)

    def test__column_headers_for_non_sortable_columns(self):
        context = testing.DummyResource(is_ordered=lambda: False)
        request = self._makeRequest()
        inst = self._makeOne(context, request)
        columns = [
            {'name': 'Col 1',
             'value': 'col1',
             'sorter':True},
            {'name': 'Col 2',
             'value': 'col2'}
            ]
        result = inst._column_headers(columns)
        self.assertEqual(len(result), 2)

        col = result[0]
        self.assertEqual(col['id'], 'Col 1')
        self.assertEqual(col['field'], 'Col 1')
        self.assertEqual(col['name'], 'Col 1')
        self.assertEqual(col['width'], 120)
        self.assertEqual(col['formatterName'], '')
        self.assertEqual(col['cssClass'], 'cell-Col-1')
        self.assertEqual(col['sortable'], True)

        col = result[1]
        self.assertEqual(col['id'], 'Col 2')
        self.assertEqual(col['field'], 'Col 2')
        self.assertEqual(col['name'], 'Col 2')
        self.assertEqual(col['width'], 120)
        self.assertEqual(col['formatterName'], '')
        self.assertEqual(col['cssClass'], 'cell-Col-2')
        self.assertEqual(col['sortable'], False)

    def test__column_headers_sortable_false_for_ordered_folder(self):
        context = testing.DummyResource(is_ordered=lambda: True)
        request = self._makeRequest()
        inst = self._makeOne(context, request)
        columns = [
                {'name': 'Col 1',
                 'value': 'col1',
                 'sorter': True},
                {'name': 'Col 2',
                 'value': 'col2',
                 'sorter': True}
                ]
        result = inst._column_headers(columns)
        self.assertEqual(len(result), 2)

        col = result[0]
        self.assertEqual(col['field'], 'Col 1')
        self.assertEqual(col['sortable'], False)

        col = result[1]
        self.assertEqual(col['field'], 'Col 2')
        self.assertEqual(col['sortable'], False)

    def test__column_headers_sortable_false_for_nonresortable(self):
        context = testing.DummyResource(is_ordered = lambda *arg: False)
        request = self._makeRequest()
        inst = self._makeOne(context, request)
        columns = [
                {'name': 'Col 1',
                 'value': 'col1',
                 'sorter': True,
                 'resortable':False,},
                ]
        result = inst._column_headers(columns)
        self.assertEqual(len(result), 1)

        col = result[0]
        self.assertEqual(col['field'], 'Col 1')
        self.assertEqual(col['sortable'], False)

    def test__column_headers_no_custom(self):
        context = testing.DummyResource(is_ordered=lambda: False)
        request = self._makeRequest()
        inst = self._makeOne(context, request)
        default_columns =  [
            {'name': 'Name',
             'value': 'myname',
             'formatter': 'icon_label_url',
             'sorter': True}
            ]
        result = inst._column_headers(default_columns)
        self.assertEqual(len(result), 1)
        self.assertEqual(
            result[0],
            {'minWidth': 120,
             'field': 'Name',
             'sortable': True,
             'name': 'Name',
             'width': 120,
             'formatterName': 'icon_label_url',
             'cssClass': 'cell-Name',
             'id': 'Name',
             'validatorName':'',
             'editorName':'',
             }
        )

    def test__column_headers_None(self):
        context = testing.DummyResource()
        context.is_ordered = lambda: False
        request = self._makeRequest()
        inst = self._makeOne(context, request)
        result = inst._column_headers([])
        self.assertEqual(len(result), 0)

    def test__column_headers_cssClass(self):
        context = testing.DummyResource(is_ordered=lambda: False)
        request = self._makeRequest()

        inst = self._makeOne(context, request)
        columns = [
            {'name': 'Col 1',
             'value': 'col1',
             'sorter': True,
             'css_class': 'customClass'},
            {'name': 'Col 2',
             'value': 'col2',
             'sorter': True},
            {'name': 'Col 3',
             'value': 'col3',
             'sorter': True,
             'css_class': 'customClass1 customClass2'},
            ]
        result = inst._column_headers(columns)
        self.assertEqual(len(result), 3)
        self.assertEqual(result[0]['cssClass'], 'cell-Col-1 customClass')
        self.assertEqual(result[1]['cssClass'], 'cell-Col-2')
        self.assertEqual(
            result[2]['cssClass'], 'cell-Col-3 customClass1 customClass2')

    def test__sort_info_context_is_ordered(self):
        context = testing.DummyResource(
            is_ordered=lambda: True,
            sort=lambda resultset, **kw: resultset
            )
        request = self._makeRequest()
        inst = self._makeOne(context, request)
        result = inst._sort_info([])
        self.assertEqual(result['column'], None)
        sorter = result['sorter']
        resultset = DummyResultSet([1])
        self.assertEqual(
            sorter(context, resultset, reverse=True, limit=1),
            resultset
            )
        self.assertEqual(result['column_name'], None)

    def test__sort_info_context_unordered_default_sort_column(self):
        context = testing.DummyResource(
            is_ordered=lambda: False,
            )
        request = self._makeRequest()
        inst = self._makeOne(context, request)
        columns = [{'name':'col1'}, {'name':'col2', 'sorter':True}]
        result = inst._sort_info(columns)
        self.assertEqual(result['column'], columns[1])
        self.assertEqual(result['sorter'], True)
        self.assertEqual(result['column_name'], 'col2')

    def test__sort_info_context_unordered_nondefault_sort_column_exists(self):
        context = testing.DummyResource(
            is_ordered=lambda: False,
            )
        request = self._makeRequest()
        inst = self._makeOne(context, request)
        columns = [{'name':'col1', 'sorter':'a'}, {'name':'col2', 'sorter':'b'}]
        result = inst._sort_info(columns, sort_column_name='col2')
        self.assertEqual(result['column'], columns[1])
        self.assertEqual(result['sorter'], 'b')
        self.assertEqual(result['column_name'], 'col2')

    def test__sort_info_context_unordered_nondefault_sort_column_notexist(self):
        context = testing.DummyResource(
            is_ordered=lambda: False,
            )
        request = self._makeRequest()
        inst = self._makeOne(context, request)
        columns = [{'name':'col1', 'sorter':'a'}, {'name':'col2', 'sorter':'b'}]
        result = inst._sort_info(columns, sort_column_name='col3')
        self.assertEqual(result['column'], None)
        self.assertEqual(result['sorter'], None)
        self.assertEqual(result['column_name'], 'col3')
        
    def test__sort_info_context_unordered_default_sort_column_via_initial(self):
        context = testing.DummyResource(
            is_ordered=lambda: False,
            )
        request = self._makeRequest()
        inst = self._makeOne(context, request)
        columns = [{'name':'col1', 'sorter':True},
                   {'name':'col2', 'sorter':True,
                    'initial_sort_column':True}]
        result = inst._sort_info(columns)
        self.assertEqual(result['column'], columns[1])
        self.assertEqual(result['sorter'], True)
        self.assertEqual(result['column_name'], 'col2')
        
    def test__folder_contents_columns_callable(self):
        from substanced.interfaces import IFolder
        context = DummyFolder(__provides__=IFolder)
        request = self._makeRequest()
        context['catalogs'] = self._makeCatalogs(oids=[1])
        result = testing.DummyResource()
        result.col1 = 'val1'
        result.col2 = 'val2'
        result.__name__ = 'fred'
        context.__objectmap__ = DummyObjectMap(result)
        def get_columns(folder, subobject, request, default_columns):
            self.assertEqual(len(default_columns), 1)
            return [{'name': 'Col 1',
                     'value': getattr(subobject, 'col1', None)},
                    {'name': 'Col 2',
                     'value': getattr(subobject, 'col2', None)}]
        inst = self._makeOne(context, request)
        request.registry.content = DummyContent(columns=get_columns)
        info = inst._folder_contents()
        length, records = info['length'], info['records']
        self.assertEqual(length, 1)
        self.assertEqual(len(records), 1)
        item = records[0]
        self.assertEqual(item['Col 1'], 'val1')
        self.assertEqual(item['Col 2'], 'val2')

    def test__folder_contents_columns_None(self):
        from substanced.interfaces import IFolder
        context = DummyFolder(__provides__=IFolder)
        request = self._makeRequest()
        context['catalogs'] = self._makeCatalogs(oids=[1])
        result = testing.DummyResource()
        result.col1 = 'val1'
        result.col2 = 'val2'
        result.__name__ = 'fred'
        context.__objectmap__ = DummyObjectMap(result)
        inst = self._makeOne(context, request)
        request.registry.content = DummyContent(columns=None)
        info = inst._folder_contents()
        length, records = info['length'], info['records']
        self.assertEqual(length, 1)
        self.assertEqual(len(records), 1)
        item = records[0]
        self.assertEqual(
            item,
            {'name': 'fred',
             'disable': [],
             'id': 'fred'}
            )

    def test__folder_contents_with_global_filter_value(self):
        from substanced.interfaces import IFolder
        context = DummyFolder(__provides__=IFolder)
        request = self._makeRequest()
        context['catalogs'] = self._makeCatalogs(oids=[1])
        result = testing.DummyResource()
        result.__name__ = 'fred'
        context.__objectmap__ = DummyObjectMap(result)
        inst = self._makeOne(context, request)
        request.registry.content = DummyContent()
        info = inst._folder_contents(filter_values=[('', 'abc')])
        length, records = info['length'], info['records']
        self.assertEqual(length, 1)
        self.assertEqual(len(records), 1)

    def test__folder_contents_with_global_filter_value_multiple_words(self):
        from substanced.interfaces import IFolder
        context = DummyFolder(__provides__=IFolder)
        request = self._makeRequest()
        context['catalogs'] = self._makeCatalogs(oids=[1])
        result = testing.DummyResource()
        result.__name__ = 'fred'
        context.__objectmap__ = DummyObjectMap(result)
        inst = self._makeOne(context, request)
        request.registry.content = DummyContent()
        info = inst._folder_contents(filter_values=[('', 'abc def')])
        length, records = info['length'], info['records']
        self.assertEqual(length, 1)
        self.assertEqual(len(records), 1)

    def test__folder_contents_with_nonglobal_filter_value(self):
        from substanced.interfaces import IFolder
        context = DummyFolder(__provides__=IFolder)
        request = self._makeRequest()
        context['catalogs'] = self._makeCatalogs(oids=[1])
        result = testing.DummyResource()
        result.__name__ = 'fred'
        context.__objectmap__ = DummyObjectMap(result)
        inst = self._makeOne(context, request)
        content = DummyContent()
        def filt(ctx, val, q):
            self.assertEqual(ctx, context)
            self.assertEqual(val, 'woo')
            self.assertEqual(q.__class__, DummyIndex)
            return q
        def cols(*arg):
            return [{'name':'colname', 'filter':filt, 'value':'val'}]
        content.columns = cols
        request.registry.content = content
        info = inst._folder_contents(filter_values=[('colname', 'woo')])
        length, records = info['length'], info['records']
        self.assertEqual(length, 1)
        self.assertEqual(len(records), 1)
        
    def test__folder_contents_with_nonglobal__and_global_filter_values(self):
        from substanced.interfaces import IFolder
        context = DummyFolder(__provides__=IFolder)
        request = self._makeRequest()
        context['catalogs'] = self._makeCatalogs(oids=[1])
        result = testing.DummyResource()
        result.__name__ = 'fred'
        context.__objectmap__ = DummyObjectMap(result)
        inst = self._makeOne(context, request)
        def gtf(ctx, val, q):
            self.assertEqual(val, 'boo')
            q.gtf_called = True
            return q
        inst._global_text_filter = gtf
        content = DummyContent()
        def filt(ctx, val, q):
            self.assertTrue(q.gtf_called)
            self.assertEqual(ctx, context)
            self.assertEqual(val, 'woo')
            self.assertEqual(q.__class__, DummyIndex)
            return q
        def cols(*arg):
            return [{'name':'colname', 'filter':filt, 'value':'val'}]
        content.columns = cols
        request.registry.content = content
        info = inst._folder_contents(
            filter_values=[('', 'boo'), ('colname', 'woo')]
            )
        length, records = info['length'], info['records']
        self.assertEqual(length, 1)
        self.assertEqual(len(records), 1)

    def test__folder_contents_columns_initial_sort_reverse(self):
        from substanced.interfaces import IFolder
        context = DummyFolder(__provides__=IFolder)
        request = self._makeRequest()
        context['catalogs'] = self._makeCatalogs(oids=[1])
        result = testing.DummyResource()
        result.col1 = 'val1'
        result.col2 = 'val2'
        result.__name__ = 'fred'
        context.__objectmap__ = DummyObjectMap(result)
        inst = self._makeOne(context, request)
        def sorter(context, resultset, reverse, limit):
            self.assertTrue(reverse)
            return resultset
        def get_columns(folder, subobject, request, default_columns):
            self.assertEqual(len(default_columns), 1)
            return [{'name': 'Col 1',
                     'value': getattr(subobject, 'col1', None),
                     'sorter':sorter,
                     'initial_sort_reverse':True,}]
        request.registry.content = DummyContent(columns=get_columns)
        inst._folder_contents()
        
    def test__folder_contents_button_enabled_for_true(self):
        from substanced.interfaces import IFolder
        context = DummyFolder(__provides__=IFolder)
        context['catalogs'] = self._makeCatalogs(oids=[1])
        result = testing.DummyResource()
        result.__name__ = 'fred'
        context.__objectmap__ = DummyObjectMap(result)
        def sdi_buttons(contexr, request, default_buttons):
            return [{'type': 'single',
                     'buttons': [{'enabled_for': lambda x,y,z: True,
                                  'id': 'Button'}]}]
        request = self._makeRequest(buttons=sdi_buttons)
        inst = self._makeOne(context, request)
        folder_contents = inst._folder_contents()
        length, records = folder_contents['length'], folder_contents['records']
        self.assertEqual(length, 1)
        self.assertEqual(records[0]['disable'], [])

    def test__folder_contents_button_enabled_for_false(self):
        from substanced.interfaces import IFolder
        context = DummyFolder(__provides__=IFolder)
        context['catalogs'] = self._makeCatalogs(oids=[1])
        result = testing.DummyResource()
        result.__name__ = 'fred'
        context.__objectmap__ = DummyObjectMap(result)
        def sdi_buttons(context, request, default_buttons):
            return [{'type': 'single',
                     'buttons': [{'enabled_for': lambda x,y,z: False,
                                  'id': 'Button'}]}]
        request = self._makeRequest(buttons=sdi_buttons)
        inst = self._makeOne(context, request)
        folder_contents = inst._folder_contents()
        length, records = folder_contents['length'], folder_contents['records']
        self.assertEqual(length, 1)
        self.assertEqual(records[0]['disable'], ['Button'])

    def test__folder_contents_button_enabled_for_non_callable(self):
        from substanced.interfaces import IFolder
        context = DummyFolder(__provides__=IFolder)
        context['catalogs'] = self._makeCatalogs(oids=[1])
        result = testing.DummyResource()
        result.__name__ = 'fred'
        context.__objectmap__ = DummyObjectMap(result)
        def sdi_buttons(contexr, request, default_buttons):
            return [{'type': 'single',
                     'buttons': [{'enabled_for': 'not callable',
                                  'id': 'Button'}]}]
        request = self._makeRequest(buttons=sdi_buttons)
        inst = self._makeOne(context, request)
        folder_contents = inst._folder_contents()
        length, records = folder_contents['length'], folder_contents['records']
        self.assertEqual(length, 1)
        self.assertEqual(records[0]['disable'], [])

    def test_get_filter_values(self):
        from substanced.interfaces import IFolder
        context = DummyFolder(__provides__=IFolder)
        request = self._makeRequest()
        request.params = DummyContent()
        request.params.items = lambda *arg: [
                ('filter.', 'abc'),
                ('filter.foo', 'def'),
                ('filter.bar', 'ghi'),
                ]
        inst = self._makeOne(context, request)
        result = inst.get_filter_values()
        self.assertEqual(result, [
                ('', 'abc'),
                ('foo', 'def'),
                ('bar', 'ghi'),
                ])
        
    def test__folder_contents_folder_is_ordered(self):
        from substanced.interfaces import IFolder
        context = DummyFolder(__provides__=IFolder)
        context.sort = lambda resultset, **kw: resultset
        request = self._makeRequest()
        context['catalogs'] = self._makeCatalogs(oids=[1])
        result = testing.DummyResource()
        result.__name__ = 'fred'
        context.__objectmap__ = DummyObjectMap(result)
        inst = self._makeOne(context, request)
        context.is_ordered = lambda *arg: True
        context.oids = lambda *arg: [1, 2]
        request.registry.content = DummyContent()
        info = inst._folder_contents()
        length, records = info['length'], info['records']
        self.assertEqual(length, 1)
        self.assertEqual(len(records), 1)

    def test_show_no_columns(self):
        folder_contents = {
            'length':1,
            'sort_column_name':None,
            'show_checkbox_column':True,
            'sort_reverse':True,
            'columns':[],
            'records': [{
                    'name': 'the_name',
                    'name_url': 'http://foo.bar',
                    'id': 'the_name',
                    'name_icon': 'the_icon',
                    }]
            }
        context = testing.DummyResource()
        request = self._makeRequest(columns=None)
        inst = self._makeOne(context, request)
        inst._folder_contents = mock.Mock(
            return_value=folder_contents
            )
        inst.sdi_add_views = mock.Mock(return_value=('b',))
        context.is_reorderable = mock.Mock(return_value=False)
        context.is_ordered = mock.Mock(return_value=False)
        result = inst.show()
        self.assertTrue('slickgrid_wrapper_options' in result)
        slickgrid_wrapper_options = result['slickgrid_wrapper_options']
        self.assertTrue('slickgridOptions' in slickgrid_wrapper_options)
        self.assertEqual(
            slickgrid_wrapper_options['configName'],
            'sdi-content-grid'
            )
        # None because it cannot be sorted.  
        self.assertEqual(slickgrid_wrapper_options['isReorderable'], False)
        self.assertEqual(slickgrid_wrapper_options['showCheckboxColumn'], True)
        self.assertEqual(slickgrid_wrapper_options['sortCol'], None)   
        self.assertEqual(slickgrid_wrapper_options['sortDir'], False)
        self.assertEqual(slickgrid_wrapper_options['url'], '')
        self.assertTrue('items' in slickgrid_wrapper_options)
        self.assertEqual(slickgrid_wrapper_options['items']['from'], 0)
        self.assertEqual(slickgrid_wrapper_options['items']['to'], 40)
        self.assertEqual(slickgrid_wrapper_options['items']['total'], 1)
        self.assertTrue('records' in slickgrid_wrapper_options['items'])
        records = slickgrid_wrapper_options['items']['records']
        self.assertEqual(len(records), 1)
        self.assertEqual(records[0], {
            'name': 'the_name',
            'name_url': 'http://foo.bar',
            'id': 'the_name',
            'name_icon': 'the_icon',
            })
        addables = result['addables']
        self.assertEqual(addables, ('b',))
        buttons = result['buttons']
        self.assertEqual(len(buttons), 2)

    def test_show_with_columns(self):
        columns = [
            {
            'name': 'col1',
            'sorter':True,
            },
            {
            'name': 'col2',
            }
            ]
        folder_contents = {
            'length':1,
            'show_checkbox_column':True,
            'sort_column_name':'col1',
            'sort_reverse':False,
            'columns': columns,
            'records':[{
                    'name': 'the_name',
                    'col1': 'value4col1',
                    'col2': 'value4col2',
                    'name_url': 'http://foo.bar',
                    'id': 'the_name',
                    'name_icon': 'the_icon',
                    }]
            }
        context = testing.DummyResource()
        request = self._makeRequest()
        inst = self._makeOne(context, request)
        inst._folder_contents = mock.Mock(
            return_value=folder_contents
            )
        inst.sdi_add_views = mock.Mock(return_value=('b',))
        context.is_reorderable = mock.Mock(return_value=False)
        context.is_ordered = mock.Mock(return_value=False)
        with mock.patch(
            'substanced.folder.views.find_catalog') as find_catalog:
            find_catalog.return_value = {'col1': 'COL1', 'col2': 'COL2'}
            result = inst.show()
        self.assertTrue('slickgrid_wrapper_options' in result)
        slickgrid_wrapper_options = result['slickgrid_wrapper_options']
        self.assertTrue('slickgridOptions' in slickgrid_wrapper_options)
        self.assertEqual(
            slickgrid_wrapper_options['configName'], 'sdi-content-grid'
            )
        self.assertEqual(slickgrid_wrapper_options['isReorderable'], False)
        self.assertEqual(slickgrid_wrapper_options['sortCol'], 'col1')  
        self.assertEqual(slickgrid_wrapper_options['sortDir'], True)
        self.assertEqual(slickgrid_wrapper_options['url'], '')
        self.assertTrue('items' in slickgrid_wrapper_options)
        self.assertEqual(slickgrid_wrapper_options['items']['from'], 0)
        self.assertEqual(slickgrid_wrapper_options['items']['to'], 40)
        self.assertEqual(slickgrid_wrapper_options['items']['total'], 1)
        self.assertTrue('records' in slickgrid_wrapper_options['items'])
        records = slickgrid_wrapper_options['items']['records']
        self.assertEqual(len(records), 1)
        self.assertEqual(records[0], {
            'name': 'the_name',
            'col1': 'value4col1',
            'col2': 'value4col2',
            'name_url': 'http://foo.bar',
            'id': 'the_name',
            'name_icon': 'the_icon',
            })

        addables = result['addables']
        self.assertEqual(addables, ('b',))
        buttons = result['buttons']
        self.assertEqual(len(buttons), 2)

    def test_show_json(self):
        folder_contents = {
            'length':1,
            'sort_column_name':None,
            'records': [{
                    'name': 'the_name',
                    'name_url': 'http://foo.bar',
                    'id': 'the_name',
                    'name_icon': 'the_icon',
                    }]
            }

        context = testing.DummyResource()
        request = self._makeRequest()
        request.params['from'] = '1'
        request.params['to'] = '2'
        inst = self._makeOne(context, request)
        inst._folder_contents = mock.Mock(
            return_value=folder_contents
            )
        result = inst.show_json()
        self.assertEqual(
            result,
            {'from':1, 'to':2, 'records':folder_contents['records'], 'total':1}
            )

    def test_show_json_no_from(self):
        context = testing.DummyResource()
        request = self._makeRequest()
        inst = self._makeOne(context, request)
        result = inst.show_json()
        self.assertEqual(
            result,
            {}
            )

    def test_delete_none_deleted(self):
        context = testing.DummyResource()
        request = self._makeRequest()
        request.POST = DummyPost()
        inst = self._makeOne(context, request)
        result = inst.delete()
        self.assertEqual(request.session['_f_'], ['No items deleted'])
        self.assertEqual(result.location, '/mgmt_path')

    def test_delete_one_deleted(self):
        context = testing.DummyResource()
        context['a'] = testing.DummyResource()
        request = self._makeRequest()
        request.POST = DummyPost(None, 'a')
        inst = self._makeOne(context, request)
        result = inst.delete()
        self.assertEqual(request.session['_f_'], ['Deleted 1 item'])
        self.assertEqual(result.location, '/mgmt_path')
        self.assertFalse('a' in context)

    def test_delete_multiple_deleted(self):
        context = testing.DummyResource()
        context['a'] = testing.DummyResource()
        context['b'] = testing.DummyResource()
        request = self._makeRequest()
        request.POST = DummyPost(None, 'a/b')
        inst = self._makeOne(context, request)
        result = inst.delete()
        self.assertEqual(request.session['_f_'], ['Deleted 2 items'])
        self.assertEqual(result.location, '/mgmt_path')
        self.assertFalse('a' in context)
        self.assertFalse('b' in context)

    def test_delete_undeletable_item(self):
        context = testing.DummyResource()
        context['a'] = testing.DummyResource()
        request = self._makeRequest()
        request.POST = DummyPost(None, 'a/b')
        inst = self._makeOne(context, request)
        result = inst.delete()
        self.assertEqual(request.session['_f_'], ['Deleted 1 item'])
        self.assertEqual(result.location, '/mgmt_path')
        self.assertFalse('a' in context)

    @mock.patch('substanced.folder.views.rename_duplicated_resource')
    def test_duplicate_multiple(self, mock_rename_duplicated_resource):
        context = mock.Mock()
        request = mock.Mock()
        request.view_name = 'contents'
        request.params = {}
        request.POST.get.return_value = 'a/b'
        mock_rename_duplicated_resource.side_effect = ['a-1', 'b-1']

        inst = self._makeOne(context, request)
        inst.duplicate()

        mock_rename_duplicated_resource.assert_any_call(context, 'a')
        mock_rename_duplicated_resource.assert_any_call(context, 'b')
        request.sdiapi.flash_with_undo.assert_called_once_with(
            'Duplicated 2 items')
        request.sdiapi.mgmt_path.called_once_with(context, '@@contents')
        context.copy.assert_any_call('a', context, 'a-1')
        context.copy.assert_any_call('b', context, 'b-1')

    def test_duplicate_none(self):
        context = mock.Mock()
        request = mock.Mock()
        request.view_name = 'contents'
        request.params = {}
        request.POST.get.return_value = ''
        inst = self._makeOne(context, request)
        inst.duplicate()

        self.assertEqual(context.mock_calls, [])
        request.session.flash.assert_called_once_with('No items duplicated')
        request.sdiapi.mgmt_path.called_once_with(context, '@@contents')

    @mock.patch('substanced.folder.views.rename_duplicated_resource')
    def test_duplicate_one(self, mock_rename_duplicated_resource):
        mock_rename_duplicated_resource.side_effect = ['a-1']
        context = mock.Mock()
        request = mock.Mock()
        request.view_name = 'contents'
        request.params = {}
        request.POST.get.return_value = 'a'
        inst = self._makeOne(context, request)
        inst.duplicate()

        mock_rename_duplicated_resource.assert_any_call(context, 'a')
        context.copy.assert_any_call('a', context, 'a-1')
        request.sdiapi.flash_with_undo.assert_called_once_with(
            'Duplicated 1 item')
        request.sdiapi.mgmt_path.called_once_with(context, '@@contents')

    def test_rename_one(self):
        context = testing.DummyResource()
        context['foobar'] = testing.DummyResource()
        request = self._makeRequest()
        request.POST = DummyPost(None, 'foobar')
        inst = self._makeOne(context, request)
        result = inst.rename()
        self.assertEqual(result, {'torename': [context['foobar']]})

    def test_rename_missing_child(self):
        context = testing.DummyResource()
        context['foobar'] = testing.DummyResource()
        request = self._makeRequest()
        request.POST = DummyPost(None, 'foobar/foobar1')
        inst = self._makeOne(context, request)
        result = inst.rename()
        self.assertEqual(result, {'torename': [context['foobar']]})

    def test_rename_multiple(self):
        context = testing.DummyResource()
        context['foobar'] = testing.DummyResource()
        context['foobar2'] = testing.DummyResource()
        context['foobar3'] = testing.DummyResource()
        request = self._makeRequest()
        request.POST = DummyPost(None, 'foobar/foobar3')
        inst = self._makeOne(context, request)
        result = inst.rename()
        self.assertEqual(result, {'torename': [context['foobar'],
                                               context['foobar3']]})

    def test_rename_none(self):
        context = testing.DummyResource()
        context['foobar'] = testing.DummyResource()
        context['foobar2'] = testing.DummyResource()
        context['foobar3'] = testing.DummyResource()
        request = self._makeRequest()
        request.POST = DummyPost(None, '')
        inst = self._makeOne(context, request)
        result = inst.rename()
        self.assertEqual(request.session['_f_'], ['No items renamed'])
        self.assertEqual(result.location, '/mgmt_path')

    def test_rename_finish(self):
        context = mock.Mock()
        request = mock.Mock()
        request.view_name = 'contents'
        request.params = {}
        request.POST.getall.return_value = ('foobar',)
        request.POST.get.side_effect = lambda x: {
            'foobar': 'foobar2',
            'form.rename_finish': 'rename_finish'}[x]

        inst = self._makeOne(context, request)
        inst.rename_finish()
        request.sdiapi.flash_with_undo.assert_called_once_with(
            'Renamed 1 item')
        context.rename.assert_called_once_with('foobar', 'foobar2')

    def test_rename_finish_multiple(self):
        context = mock.Mock()
        request = mock.Mock()
        request.view_name = 'contents'
        request.params = {}
        request.POST.getall.return_value = ('foobar', 'foobar1')
        request.POST.get.side_effect = lambda x: {
            'foobar': 'foobar0',
            'foobar1': 'foobar11',
            'form.rename_finish': 'rename_finish'}[x]

        inst = self._makeOne(context, request)
        inst.rename_finish()

        request.sdiapi.flash_with_undo.assert_called_once_with(
            'Renamed 2 items')
        context.rename.assert_any_call('foobar', 'foobar0')
        context.rename.assert_any_call('foobar1', 'foobar11')

    def test_rename_finish_cancel(self):
        context = mock.Mock()
        request = mock.Mock()
        request.view_name = 'contents'
        request.params = {}
        request.POST.getall.return_value = ('foobar',)
        request.POST.get.side_effect = lambda x: {
            'foobar': 'foobar0',
            'form.rename_finish': 'cancel'}[x]
        inst = self._makeOne(context, request)
        inst.rename_finish()

        request.session.flash.assert_called_once_with('No items renamed')
        self.assertFalse(context.rename.called)

    def test_rename_finish_already_exists(self):
        from .. import FolderKeyError
        context = mock.MagicMock()
        context.rename.side_effect = FolderKeyError(_FOOBAR)
        request = mock.Mock()
        request.view_name = 'contents'
        request.params = {}
        request.POST.getall.return_value = ('foobar',)
        request.POST.get.side_effect = lambda x: {
            'foobar': 'foobar0',
            'foobar1': 'foobar0',
            'form.rename_finish': 'rename_finish'}[x]
        inst = self._makeOne(context, request)

        self.assertRaises(HTTPFound, inst.rename_finish)
        context.rename.assert_any_call('foobar', 'foobar0')
        request.session.flash.assert_called_once_with(_FOOBAR, 'error')

    @mock.patch('substanced.folder.views.get_oid')
    def test_copy_one(self, mock_get_oid):
        context = mock.Mock()
        context.get.side_effect = lambda x: {
            'foobar': 'foobar',
            'foobar1': 'foobar1'}[x]
        request = mock.MagicMock()
        request.POST.get.return_value = 'foobar'

        inst = self._makeOne(context, request)
        inst.copy()

        request.session.flash.assert_called_once_with(
            'Choose where to copy the items:', 'info')
        self.assertEqual(mock_get_oid.mock_calls, [mock.call('foobar')])
        self.assertTrue(request.session.__setitem__.called)

    @mock.patch('substanced.folder.views.get_oid')
    def test_copy_multi(self, mock_get_oid):
        context = mock.Mock()
        context.get.side_effect = lambda x: {'foobar': 'foobar',
                                             'foobar1': 'foobar1',
                                             'foobar2': 'foobar2'}[x]
        request = mock.MagicMock()
        request.POST.get.return_value = 'foobar/foobar1'

        inst = self._makeOne(context, request)
        inst.copy()

        request.session.flash.assert_called_once_with(
            'Choose where to copy the items:', 'info')
        self.assertEqual(mock_get_oid.mock_calls,
                         [mock.call('foobar'), mock.call('foobar1')])
        self.assertTrue(request.session.__setitem__.called)

    @mock.patch('substanced.folder.views.get_oid')
    def test_copy_missing_child(self, mock_get_oid):
        context = mock.Mock()
        context.get.side_effect = lambda x: {
            'foobar': 'foobar',
            'foobar2': 'foobar2'}.get(x, None)
        request = mock.MagicMock()
        request.POST.get.return_value = 'foobar/foobar1'

        inst = self._makeOne(context, request)
        inst.copy()
        request.session.flash.assert_called_once_with(
            'Choose where to copy the items:', 'info')
        self.assertEqual(mock_get_oid.mock_calls, [mock.call('foobar')])
        self.assertTrue(request.session.__setitem__.called)

    @mock.patch('substanced.folder.views.get_oid')
    def test_copy_none(self, mock_get_oid):
        context = mock.Mock()
        context.__contains__ = mock.Mock(return_value=True)
        request = mock.MagicMock()
        request.POST.get.return_value = ''

        inst = self._makeOne(context, request)
        inst.copy()

        request.session.flash.assert_called_once_with('No items to copy')
        self.assertFalse(mock_get_oid.called)

    def test_copy_finish_cancel(self):
        context = mock.Mock()
        request = mock.MagicMock()
        request.POST.get.return_value = ('foobar',)
        request.POST.get.side_effect = lambda x: {
            'foobar': 'foobar0',
            'form.copy_finish_cancel': 'cancel'}[x]
        inst = self._makeOne(context, request)
        inst.copy_finish_cancel()

        request.session.flash.assert_called_once_with('No items copied')
        self.assertEqual(request.session.__delitem__.call_args,
                         mock.call('tocopy'))

    @mock.patch('substanced.folder.views.find_objectmap')
    def test_copy_finish_zero(self, mock_find_objectmap):
        context = mock.MagicMock()
        mock_folder = mock_find_objectmap().object_for()
        mock_folder.__parent__ = mock.MagicMock()
        mock_folder.__name__ = mock.sentinel.name
        request = mock.MagicMock()
        request.session.__getitem__.return_value = [123]
        request.POST.get.side_effect = lambda x: {
            'form.copy_finish': 'copy_finish'}[x]

        inst = self._makeOne(context, request)

        # content type wont be addable, because we haven't patched
        # sdi_add_views to return a valid content type set

        inst.copy_finish()

        call_list = request.session.flash.call_args_list
        self.assertEqual(len(call_list), 2)

        request.session.flash.assert_any_call(
            'No items copied')
        request.session.flash.assert_any_call(
            '"%s" is of a type (%s) that is not addable here, not copied' % (
                mock.sentinel.name, request.registry.content.typeof(None)
                ), 'error',
            )
            
        self.assertEqual(request.session.__delitem__.call_args,
                         mock.call('tocopy'))
        
    @mock.patch('substanced.folder.views.find_objectmap')
    def test_copy_finish_one(self, mock_find_objectmap):
        context = mock.MagicMock()
        mock_folder = mock_find_objectmap().object_for()
        mock_folder.__parent__ = mock.MagicMock()
        mock_folder.__name__ = mock.sentinel.name
        request = mock.MagicMock()
        request.session.__getitem__.return_value = [123]
        request.POST.get.side_effect = lambda x: {
            'form.copy_finish': 'copy_finish'}[x]

        inst = self._makeOne(context, request)
        ct = request.registry.content.typeof(None)
        inst.sdi_add_views = lambda *arg: [ {'content_type':ct} ]
        inst.copy_finish()

        self.assertEqual(mock_folder.__parent__.copy.call_args,
                         mock.call(mock.sentinel.name, context))
        request.sdiapi.flash_with_undo.assert_called_once_with('Copied 1 item')
        self.assertEqual(request.session.__delitem__.call_args,
                         mock.call('tocopy'))

    @mock.patch('substanced.folder.views.find_objectmap')
    def test_copy_finish_multi(self, mock_find_objectmap):
        context = mock.MagicMock()
        mock_folder = mock_find_objectmap().object_for()
        mock_folder.__parent__ = mock.MagicMock()
        mock_folder.__name__ = mock.sentinel.name
        request = mock.MagicMock()
        request.session.__getitem__.return_value = [123, 456]
        request.POST.get.side_effect = lambda x: {
            'form.copy_finish': 'copy_finish'}[x]

        inst = self._makeOne(context, request)
        ct = request.registry.content.typeof(None)
        inst.sdi_add_views = lambda *arg: [ {'content_type':ct} ]
        inst.copy_finish()

        self.assertTrue(mock.call(123) in
                        mock_find_objectmap().object_for.mock_calls)
        self.assertTrue(mock.call(456) in
                        mock_find_objectmap().object_for.mock_calls)
        self.assertEqual(mock_folder.__parent__.copy.call_args,
                         mock.call(mock.sentinel.name, context))
        request.sdiapi.flash_with_undo.assert_called_once_with('Copied 2 items')
        self.assertEqual(request.session.__delitem__.call_args,
                         mock.call('tocopy'))

    @mock.patch('substanced.folder.views.find_objectmap')
    def test_copy_finish_already_exists(self, mock_find_objectmap):
        from .. import FolderKeyError
        context = mock.MagicMock()
        mock_folder = mock_find_objectmap().object_for()
        mock_folder.__parent__ = mock.MagicMock()
        mock_folder.__parent__.copy.side_effect = FolderKeyError(_FOOBAR)
        mock_folder.__name__ = mock.sentinel.name
        request = mock.MagicMock()
        request.session.__getitem__.return_value = [123]
        request.POST.get.side_effect = lambda x: {
            'form.copy_finish': 'copy_finish'}[x]

        inst = self._makeOne(context, request)
        ct = request.registry.content.typeof(None)
        inst.sdi_add_views = lambda *arg: [ {'content_type':ct} ]
        self.assertRaises(HTTPFound, inst.copy_finish)
        request.session.flash.assert_called_once_with(_FOOBAR, 'error')

    @mock.patch('substanced.folder.views.get_oid')
    def test_move_one(self, mock_get_oid):
        context = mock.Mock()
        context.get.side_effect = lambda x: {
            'foobar': 'foobar',
            'foobar1': 'foobar1'}[x]
        request = mock.MagicMock()
        request.POST.get.return_value = 'foobar'

        inst = self._makeOne(context, request)
        inst.move()

        request.session.flash.assert_called_once_with(
            'Choose where to move the items:', 'info')
        self.assertEqual(mock_get_oid.mock_calls, [mock.call('foobar')])
        self.assertTrue(request.session.__setitem__.call_args,
                        [mock.call('tomove')])

    @mock.patch('substanced.folder.views.get_oid')
    def test_move_multi(self, mock_get_oid):
        context = mock.Mock()
        context.get.side_effect = lambda x: {'foobar': 'foobar',
                                             'foobar1': 'foobar1'}[x]
        request = mock.MagicMock()
        request.POST.get.return_value = 'foobar/foobar1'

        inst = self._makeOne(context, request)
        inst.move()

        request.session.flash.assert_called_once_with(
            'Choose where to move the items:', 'info')
        self.assertEqual(mock_get_oid.mock_calls,
                         [mock.call('foobar'), mock.call('foobar1')])
        self.assertTrue(request.session.__setitem__.call_args,
                        [mock.call('tomove')])

    @mock.patch('substanced.folder.views.get_oid')
    def test_move_missing_child(self, mock_get_oid):
        context = mock.Mock()
        context.get.side_effect = lambda x: {'foobar': 'foobar',
                                             'foobar1': 'foobar1'}.get(x, None)
        request = mock.MagicMock()
        request.POST.get.return_value = 'foobar/foobar2'

        inst = self._makeOne(context, request)
        inst.move()

        request.session.flash.assert_called_once_with(
            'Choose where to move the items:', 'info')
        self.assertEqual(mock_get_oid.mock_calls, [mock.call('foobar')])
        self.assertTrue(request.session.__setitem__.call_args,
                        [mock.call('tomove')])

    @mock.patch('substanced.folder.views.get_oid')
    def test_move_none(self, mock_get_oid):
        context = mock.Mock()
        context.get.side_effect = lambda x: {'foobar': 'foobar',
                                             'foobar1': 'foobar1'}.get(x, None)
        request = mock.MagicMock()
        request.POST.get.return_value = ''

        inst = self._makeOne(context, request)
        inst.move()

        request.session.flash.assert_called_once_with('No items to move')
        self.assertFalse(mock_get_oid.called)
        self.assertFalse(request.session.__setitem__.called)

    def test_move_finish_cancel(self):
        context = mock.Mock()
        request = mock.MagicMock()
        request.POST.get.return_value = 'foobar'
        request.POST.get.side_effect = lambda x: {
            'foobar': 'foobar0',
            'form.move_finish': 'cancel'}[x]
        inst = self._makeOne(context, request)
        inst.move_finish_cancel()

        request.session.flash.assert_called_once_with('No items moved')
        self.assertEqual(request.session.__delitem__.call_args,
                         mock.call('tomove'))

    @mock.patch('substanced.folder.views.find_objectmap')
    def test_move_finish_zero(self, mock_find_objectmap):
        context = mock.MagicMock()
        mock_folder = mock_find_objectmap().object_for()
        mock_folder.__parent__ = mock.MagicMock()
        mock_folder.__name__ = mock.sentinel.name
        request = mock.MagicMock()
        request.session.__getitem__.return_value = [123]
        request.POST.get.side_effect = lambda x: {
            'form.move_finish': 'move_finish'}[x]

        inst = self._makeOne(context, request)

        # content type wont be addable, because we haven't patched
        # sdi_add_views to return a valid content type set

        inst.move_finish()

        call_list = request.session.flash.call_args_list
        self.assertEqual(len(call_list), 2)

        request.session.flash.assert_any_call(
            'No items moved')
        request.session.flash.assert_any_call(
            '"%s" is of a type (%s) that is not addable here, not moved' % (
                mock.sentinel.name, request.registry.content.typeof(None)
                ), 'error',
            )
            
        self.assertEqual(request.session.__delitem__.call_args,
                         mock.call('tomove'))
        
    @mock.patch('substanced.folder.views.find_objectmap')
    def test_move_finish_one(self, mock_find_objectmap):
        context = mock.MagicMock()
        mock_folder = mock_find_objectmap().object_for()
        mock_folder.__parent__ = mock.MagicMock()
        mock_folder.__name__ = mock.sentinel.name
        request = mock.MagicMock()
        request.session.__getitem__.return_value = [123]
        request.POST.get.side_effect = lambda x: {
            'form.move_finish': 'move_finish'}[x]

        inst = self._makeOne(context, request)
        ct = request.registry.content.typeof(None)
        inst.sdi_add_views = lambda *arg: [ {'content_type':ct} ]
        inst.move_finish()

        self.assertEqual(mock_folder.__parent__.move.call_args,
                         mock.call(mock.sentinel.name, context))
        request.sdiapi.flash_with_undo.assert_called_once_with('Moved 1 item')
        self.assertEqual(request.session.__delitem__.call_args,
                         mock.call('tomove'))

    @mock.patch('substanced.folder.views.find_objectmap')
    def test_move_finish_multi(self, mock_find_objectmap):
        context = mock.MagicMock()
        mock_folder = mock_find_objectmap().object_for()
        mock_folder.__parent__ = mock.MagicMock()
        mock_folder.__name__ = mock.sentinel.name
        request = mock.MagicMock()
        request.session.__getitem__.return_value = [123, 456]
        request.POST.get.side_effect = lambda x: {
            'form.move_finish': 'move_finish'}[x]

        inst = self._makeOne(context, request)
        ct = request.registry.content.typeof(None)
        inst.sdi_add_views = lambda *arg: [ {'content_type':ct} ]
        inst.move_finish()

        self.assertTrue(mock.call(123) in
                        mock_find_objectmap().object_for.mock_calls)
        self.assertTrue(mock.call(456) in
                        mock_find_objectmap().object_for.mock_calls)
        self.assertEqual(mock_folder.__parent__.move.call_args,
                         mock.call(mock.sentinel.name, context))
        self.assertEqual(request.session.__delitem__.call_args,
                         mock.call('tomove'))
        request.sdiapi.flash_with_undo.assert_called_once_with('Moved 2 items')

    @mock.patch('substanced.folder.views.find_objectmap')
    def test_move_finish_already_exists(self, mock_find_objectmap):
        from .. import FolderKeyError
        context = mock.MagicMock()
        mock_folder = mock_find_objectmap().object_for()
        mock_folder.__parent__ = mock.MagicMock()
        mock_folder.__parent__.move.side_effect = FolderKeyError(_FOOBAR)
        mock_folder.__name__ = mock.sentinel.name
        request = mock.MagicMock()
        request.session.__getitem__.return_value = [123]
        request.POST.get.side_effect = lambda x: {
            'form.move_finish': 'move_finish'}[x]

        inst = self._makeOne(context, request)
        ct = request.registry.content.typeof(None)
        inst.sdi_add_views = lambda *arg: [ {'content_type':ct} ]
        self.assertRaises(HTTPFound, inst.move_finish)
        request.session.flash.assert_called_once_with(_FOOBAR, 'error')

    def test_reorder_rows(self):
        context = testing.DummyResource()
        request = self._makeRequest()
        request.params['item-modify'] = 'a/b'
        request.params['insert-before'] = 'c'
        def reorder(item_modify, insert_before):
            self.assertEqual(item_modify, ['a', 'b'])
            self.assertEqual(insert_before, 'c')
        context.reorder = reorder
        inst = self._makeOne(context, request)
        def _get_json():
            return {'foo':'bar'}
        inst._get_json = _get_json
        mockundowrapper = mock.Mock(
            return_value='STATUSMESSG<a>Undo</a>'
            )
        request.sdiapi.get_flash_with_undo_snippet = mockundowrapper
        result = inst.reorder_rows()
        mockundowrapper.assert_called_once_with('2 rows moved.')
        self.assertEqual(
            result,
            {'foo': 'bar', 'flash': 'STATUSMESSG<a>Undo</a>'}
            )

    def test_reorder_rows_after_last(self):
        context = testing.DummyResource()
        request = self._makeRequest()
        request.params['item-modify'] = 'a/b'
        request.params['insert-before'] = ''
        def reorder(item_modify, insert_before):
            self.assertEqual(item_modify, ['a', 'b'])
            self.assertEqual(insert_before, None)
        context.reorder = reorder
        inst = self._makeOne(context, request)
        def _get_json():
            return {'foo':'bar'}
        inst._get_json = _get_json
        mockundowrapper = mock.Mock(
            return_value='STATUSMESSG<a>Undo</a>'
            )
        request.sdiapi.get_flash_with_undo_snippet = mockundowrapper
        result = inst.reorder_rows()
        mockundowrapper.assert_called_once_with('2 rows moved.')
        self.assertEqual(
            result,
            {'foo': 'bar', 'flash': 'STATUSMESSG<a>Undo</a>'}
            )

    def test__name_sorter_index_is_None(self):
        context = testing.DummyResource()
        request = self._makeRequest()
        inst = self._makeOne(context, request)
        resource = testing.DummyResource()
        resultset = 123
        inst.system_catalog = {}
        result = inst._name_sorter(resource, resultset, 1, True)
        self.assertEqual(result, resultset)
        
    def test__name_sorter_index_is_not_None(self):
        context = testing.DummyResource()
        request = self._makeRequest()
        resource = testing.DummyResource()
        catalog = DummyCatalog()
        class ResultSet(object):
            def sort(innerself, index, limit=None, reverse=None):
                self.assertEqual(index.__class__.__name__, 'DummyIndex')
                self.assertEqual(limit, 1)
                self.assertEqual(reverse, True)
                return innerself
        resultset = ResultSet()
        inst = self._makeOne(context, request)
        inst.system_catalog = catalog
        result = inst._name_sorter(resource, resultset, 1, True)
        self.assertEqual(result, resultset)

    def test_get_columns_no_icon(self):
        fred = testing.DummyResource()
        fred.__name__ = 'fred'
        request = self._makeRequest(icon=None)
        context = testing.DummyResource()
        inst = self._makeOne(context, request)
        result = inst.get_columns(fred)
        self.assertEqual(
           result,
           [
                {'sorter': inst._name_sorter, 
                 'name': 'Name',
                 'formatter':'html',
                 'value':'<i class=""> </i> <a href="/mgmt_path">fred</a>'},
                ]
           )

    def test_get_columns_named_icon(self):
        fred = testing.DummyResource()
        fred.__name__ = 'fred'
        request = self._makeRequest(icon='icon')
        context = testing.DummyResource()
        inst = self._makeOne(context, request)
        result = inst.get_columns(fred)
        self.assertEqual(
           result,
           [
                {'sorter': inst._name_sorter, 
                 'name': 'Name',
                 'formatter':'html',
                 'value':'<i class="icon"> </i> <a href="/mgmt_path">fred</a>'},
                ]
           )

    def test_get_columns_with_callable_icon(self):
        fred = testing.DummyResource()
        fred.__name__ = 'fred'
        request = self._makeRequest(icon=lambda *arg: 'icon')
        context = testing.DummyResource()
        inst = self._makeOne(context, request)
        result = inst.get_columns(fred)
        self.assertEqual(
           result,
           [
                {'sorter': inst._name_sorter, 
                 'name': 'Name',
                 'formatter':'html',
                 'value':'<i class="icon"> </i> <a href="/mgmt_path">fred</a>'},
                ]
           )
        
    def test_get_buttons_novals(self):
        self.config.testing_securitypolicy(permissive=True)
        request = self._makeRequest()
        context = testing.DummyResource()
        inst = self._makeOne(context, request)
        result = inst.get_buttons()
        self.assertEqual(len(result), 2)
        main_buttons = result[0]
        self.assertEqual(main_buttons['type'], 'group')
        buttons = main_buttons['buttons']
        self.assertEqual(len(buttons), 4)
        self.assertEqual(buttons[0]['text'], 'Rename')
        self.assertEqual(buttons[1]['text'], 'Copy')
        self.assertEqual(buttons[2]['text'], 'Move')
        self.assertEqual(buttons[3]['text'], 'Duplicate')
        self.assertEqual(result[1]['type'], 'group')

        buttons = result[1]['buttons']
        self.assertEqual(len(buttons), 1)
        delete_button = buttons[0]
        self.assertEqual(delete_button['text'], 'Delete')
        self.assertEqual(delete_button['class'], 'btn-danger btn-sdi-sel')
        self.assertEqual(delete_button['name'], 'form.delete')
        self.assertEqual(delete_button['value'], 'delete')
        self.assertEqual(delete_button['id'], 'delete')
        self.assertTrue(delete_button['enabled_for'])

    def test_get_buttons_delete_enabled_for_no_sdi_deletable_attr_can_mg(self):
        self.config.testing_securitypolicy(permissive=True)
        request = self._makeRequest()
        context = testing.DummyResource()
        inst = self._makeOne(context, request)
        result = inst.get_buttons()
        delete_button = result[1]['buttons'][0]
        delete_enabled_for = delete_button['enabled_for']
        result = delete_enabled_for(context, context, request)
        self.assertTrue(result)

    def test_get_buttons_delete_enabled_for_no_sdi_deletable_attr_cant_mg(self):
        self.config.testing_securitypolicy(permissive=False)
        request = self._makeRequest()
        context = testing.DummyResource()
        inst = self._makeOne(context, request)
        result = inst.get_buttons()
        delete_button = result[1]['buttons'][0]
        delete_enabled_for = delete_button['enabled_for']
        result = delete_enabled_for(context, context, request)
        self.assertFalse(result)
        
    def test_get_buttons_delete_enabled_for_callable_sdi_deletable_attr(self):
        self.config.testing_securitypolicy(permissive=True)
        request = self._makeRequest()
        context = testing.DummyResource()
        subobject = testing.DummyResource()
        def deletable(_subobject, _request):
            self.assertEqual(_subobject, subobject)
            self.assertEqual(_request, request)
            return False
        subobject.__sdi_deletable__ = deletable
        inst = self._makeOne(context, request)
        result = inst.get_buttons()
        delete_button = result[1]['buttons'][0]
        delete_enabled_for = delete_button['enabled_for']
        result = delete_enabled_for(context, subobject, request)
        self.assertFalse(result)

    def test_get_buttons_delete_enabled_for_boolean_sdi_deletable_attr(self):
        self.config.testing_securitypolicy(permissive=True)
        request = self._makeRequest()
        context = testing.DummyResource()
        subobject = testing.DummyResource()
        subobject.__sdi_deletable__ = False
        inst = self._makeOne(context, request)
        result = inst.get_buttons()
        delete_button = result[1]['buttons'][0]
        delete_enabled_for = delete_button['enabled_for']
        result = delete_enabled_for(context, subobject, request)
        self.assertFalse(result)
        
    def test_get_buttons_tocopy(self):
        self.config.testing_securitypolicy(permissive=True)
        request = self._makeRequest()
        context = testing.DummyResource()
        request.session['tocopy'] = True
        inst = self._makeOne(context, request)
        result = inst.get_buttons()
        self.assertEqual(
            result,
            [
              {'buttons': 
                [{'text': 'Copy here', 
                  'class': 'btn-primary btn-sdi-act', 
                  'id': 'copy_finish', 
                  'value': 'copy_finish', 
                  'name': 'form.copy_finish'}, 
                 {'text': 'Cancel', 
                  'class': 'btn-danger btn-sdi-act', 
                  'id': 'cancel', 
                  'value': 'cancel', 
                  'name': 'form.copy_finish_cancel'}],
               'type': 'single'}
               ]
               )

    def test_get_buttons_tomove(self):
        self.config.testing_securitypolicy(permissive=True)
        request = self._makeRequest()
        context = testing.DummyResource()
        request.session['tomove'] = True
        inst = self._makeOne(context, request)
        result = inst.get_buttons()
        self.assertEqual(
            result, [
            {'buttons': [
                {'text': 'Move here',
                 'class': 'btn-primary btn-sdi-act',
                 'id': 'move_finish',
                 'value': 'move_finish',
                 'name': 'form.move_finish'},
                {'text': 'Cancel',
                 'class': 'btn-danger btn-sdi-act',
                 'id': 'cancel',
                 'value': 'cancel',
                 'name':'form.move_finish_cancel'}],
             'type': 'single'}
            ]            
            )

class Test_folder_contents_views_decorator(unittest.TestCase):
    def setUp(self):
        testing.setUp()

    def tearDown(self):
        testing.tearDown()

    def _getTargetClass(self):
        from ..views import folder_contents_views
        return folder_contents_views

    def _makeOne(self, *arg, **kw):
        return self._getTargetClass()(*arg, **kw)

    def test_create_defaults(self):
        decorator = self._makeOne()
        self.assertEqual(decorator.settings, {})

    def test_create_nondefaults(self):
        decorator = self._makeOne(
            name='frank',
            match_param='match_param',
            )
        self.assertEqual(decorator.settings['name'], 'frank')
        self.assertEqual(decorator.settings['match_param'], 'match_param')

    def test_call_class(self):
        decorator = self._makeOne()
        venusian = DummyVenusian()
        decorator.venusian = venusian
        class foo(object): pass
        wrapped = decorator(foo)
        self.assertTrue(wrapped is foo)
        config = call_venusian(venusian)
        settings = config.settings
        self.assertEqual(len(settings), 1)
        self.assertEqual(len(settings[0]), 2)
        self.assertEqual(settings[0]['cls'], None) # comes from call_venusian
        self.assertEqual(settings[0]['_info'], 'codeinfo')

    def test_stacking(self):
        decorator1 = self._makeOne(name='1')
        venusian1 = DummyVenusian()
        decorator1.venusian = venusian1
        venusian2 = DummyVenusian()
        decorator2 = self._makeOne(name='2')
        decorator2.venusian = venusian2
        def foo(): pass
        wrapped1 = decorator1(foo)
        wrapped2 = decorator2(wrapped1)
        self.assertTrue(wrapped1 is foo)
        self.assertTrue(wrapped2 is foo)
        config1 = call_venusian(venusian1)
        self.assertEqual(len(config1.settings), 1)
        self.assertEqual(config1.settings[0]['name'], '1')
        config2 = call_venusian(venusian2)
        self.assertEqual(len(config2.settings), 1)
        self.assertEqual(config2.settings[0]['name'], '2')

    def test_with_custom_predicates(self):
        decorator = self._makeOne(custom_predicates=(1,))
        venusian = DummyVenusian()
        decorator.venusian = venusian
        def foo(context, request): pass
        decorated = decorator(foo)
        self.assertTrue(decorated is foo)
        config = call_venusian(venusian)
        settings = config.settings
        self.assertEqual(settings[0]['custom_predicates'], (1,))

    def test_call_withdepth(self):
        decorator = self._makeOne(_depth=1)
        venusian = DummyVenusian()
        decorator.venusian = venusian
        def foo(): pass
        decorator(foo)
        self.assertEqual(venusian.depth, 2)

class Test_add_folder_contents_views(unittest.TestCase):
    def _callFUT(self, config, **kw):
        from ..views import add_folder_contents_views
        return add_folder_contents_views(config, **kw)
    
    def test_it_gardenpath(self):
        from ..views import FolderContents
        from substanced.interfaces import IFolder
        config = DummyConfig()
        self._callFUT(config)
        self.assertEqual(len(config.settings), 13)
        self.assertEqual(config.settings[0]['view'], FolderContents)
        self.assertEqual(config.settings[0]['context'], IFolder)

    def test_it_override_context_and_cls(self):
        config = DummyConfig()
        class Foo(object): pass
        self._callFUT(config, cls=Foo, context=Foo)
        self.assertEqual(config.settings[0]['view'], Foo)
        self.assertEqual(config.settings[0]['context'], Foo)

    def test_it_with_extra_predicates(self):
        config = DummyConfig()
        class Foo(object): pass
        self._callFUT(config, slamdunk=1)
        self.assertEqual(config.settings[0]['slamdunk'], 1)
        
class DummyContainer(object):
    oid_store = {}

    def __init__(self, exc=None):
        self.exc = exc

    def check_name(self, name):
        if self.exc:
            raise self.exc
        return name

class DummyContent(object):
    def __init__(self, **kw):
        self.__dict__.update(kw)

    def create(self, iface, *arg, **kw):
        return getattr(self, iface, None)

    def metadata(self, context, name, default=None):
        return getattr(self, name, default)


class DummyPost(dict):
    def __init__(self, getall_result=(), get_result=None):
        self.getall_result = getall_result
        self.get_result = get_result

    def getall(self, name): # pragma: no cover
        return self.getall_result

    def get(self, name, default=None):
        if self.get_result is None: # pragma: no cover
            return default
        return self.get_result

class DummySDIAPI(object):
    def mgmt_path(self, *arg, **kw):
        return '/mgmt_path'

class DummyFolder(testing.DummyResource):
    def is_ordered(self):
        return False

class DummyCatalogs(testing.DummyResource):
    __is_service__ = True

class DummyCatalog(object):
    def __init__(self, result=()):
        if result is not None:
            result = DummyResultSet(result)
        self.result = result

    def __getitem__(self, name):
        result = self.result
        if result is not None:
            result = DummyIndex(self.result)
        return result

    def get(self, name, default=None):
        return self[name]

class DummyResultSet(object):
    def __init__(self, result):
        self.ids = result

    def sort(self, *arg, **kw):
        return self

    def __len__(self):
        return len(self.ids)

class DummyIndex(object):
    def __init__(self, result):
        self.result = result

    def execute(self):
        return self.result
        
    def eq(self, *arg, **kw):
        return self

    def allows(self, *arg, **kw):
        pass

    def __and__(self, other):
        return self

    def check_query(self, querytext):
        return True
    
class DummyObjectMap(object):
    def __init__(self, result):
        self.result = result
    def object_for(self, oid):
        return self.result

class DummyVenusianInfo(object):
    scope = 'notaclass'
    module = sys.modules['substanced.folder.tests.test_views']
    codeinfo = 'codeinfo'

class DummyVenusian(object):
    def __init__(self, info=None):
        if info is None:
            info = DummyVenusianInfo()
        self.info = info
        self.attachments = []

    def attach(self, wrapped, callback, category=None, depth=1):
        self.attachments.append((wrapped, callback, category))
        self.depth = depth
        return self.info

class DummyRegistry(object):
    pass

class DummyConfig(object):
    _ainfo = None
    def __init__(self):
        self.settings = []
        self.registry = DummyRegistry()

    def add_folder_contents_views(self, **kw):
        self.settings.append(kw)

    add_mgmt_view = add_folder_contents_views

    def with_package(self, pkg):
        self.pkg = pkg
        return self

class DummyVenusianContext(object):
    def __init__(self):
        self.config = DummyConfig()
    
def call_venusian(venusian, context=None):
    if context is None:
        context = DummyVenusianContext()
    for wrapped, callback, category in venusian.attachments:
        callback(context, None, None)
    return context.config
