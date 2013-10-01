import unittest
from pyramid import testing

class Test_set_yaml(unittest.TestCase):
    def _callFUT(self, registry):
        from . import set_yaml
        return set_yaml(registry)

    def test_loader_and_dumper_set(self):
        registry = DummyRegistry(None)
        self._callFUT(registry)
        self.assertEqual(registry['yaml_loader'].__name__, 'SLoader')
        self.assertEqual(registry['yaml_dumper'].__name__, 'SDumper')

    def test_iface_representer(self):
        import io
        import yaml
        registry = DummyRegistry(None)
        self._callFUT(registry)
        stream = io.BytesIO()
        yaml.dump(DummyInterface, stream, Dumper=registry['yaml_dumper'],
                  encoding='utf-8')
        self.assertEqual(
            stream.getvalue(),
            b"!interface 'substanced.dump.tests.DummyInterface'\n"
            )

    def test_iface_constructor(self):
        import io
        import yaml
        registry = DummyRegistry(None)
        self._callFUT(registry)
        stream = io.BytesIO(
            b"!interface 'substanced.dump.tests.DummyInterface'\n"
            )
        result = yaml.load(stream, Loader=registry['yaml_loader'])
        self.assertEqual(result, DummyInterface)

    def test_blob_representer(self):
        import io
        import yaml
        from ZODB.blob import Blob
        registry = DummyRegistry(None)
        self._callFUT(registry)
        stream = io.BytesIO()
        blob = Blob(b'abc')
        yaml.dump(blob, stream, Dumper=registry['yaml_dumper'],
                  encoding='utf-8')
        self.assertEqual(
            stream.getvalue(),
            b"!blob 'YWJj\n\n  '\n"
            )

    def test_blob_constructor(self):
        import io
        import yaml
        registry = DummyRegistry(None)
        self._callFUT(registry)
        stream = io.BytesIO(
            b"!blob 'YWJj\n\n  '\n"
            )
        result = yaml.load(stream, Loader=registry['yaml_loader'])
        with result.open('r') as f:
            self.assertEqual(f.read(), b'abc')

class Test_get_dumpers(unittest.TestCase):
    def _callFUT(self, registry):
        from . import get_dumpers
        return get_dumpers(registry)

    def test_ordered_is_not_None(self):
        def f(n, reg):
            self.assertEqual(n, 1)
            self.assertEqual(reg, registry)
            return 'dumpers'
        registry = DummyRegistry([(1, f)])
        result = self._callFUT(registry)
        self.assertEqual(result, ['dumpers'])

    def test_ordered_is_None(self):
        def f(n, reg):
            self.assertEqual(n, 1)
            self.assertEqual(reg, registry)
            return 'dumpers'
        registry = DummyRegistry(None)
        registry['_sd_dumpers'] = [(1, f, None, None)]
        result = self._callFUT(registry)
        self.assertEqual(result, ['dumpers'])
        self.assertEqual(registry.ordered, [(1, f)])

class Test_DumpAndLoad(unittest.TestCase):
    def setUp(self):
        self.config = testing.setUp()

    def tearDown(self):
        testing.tearDown()

    def _makeOne(self):
        from . import _DumpAndLoad
        return _DumpAndLoad()

    def test__make_dump_context(self):
        inst = self._makeOne()
        c = inst._make_dump_context('dir', 'reg', 'dumpers', True, False)
        self.assertEqual(c.__class__.__name__, '_ResourceDumpContext')

    def test__make_load_context(self):
        inst = self._makeOne()
        c = inst._make_load_context('dir', 'reg', 'dumpers', True, False)
        self.assertEqual(c.__class__.__name__, '_ResourceLoadContext')

    def test_dump_no_subresources(self):
        inst = self._makeOne()
        resource = testing.DummyResource()
        context = DummyResourceDumpContext()
        inst._make_dump_context = lambda *arg, **kw: context
        inst.dump(resource, 'directory', subresources=False)
        self.assertEqual(context.dumped, resource)

    def test_dump_with_subresources_resource_is_not_folder(self):
        inst = self._makeOne()
        resource = testing.DummyResource()
        resource['a'] = testing.DummyResource()
        context = DummyResourceDumpContext()
        inst._make_dump_context = lambda *arg, **kw: context
        inst.dump(resource, 'directory', subresources=True)
        self.assertEqual(context.dumped, resource)

    def test_dump_with_subresources_resource_is_folder(self):
        from zope.interface import directlyProvides
        from substanced.interfaces import IFolder
        inst = self._makeOne()
        resource = testing.DummyResource()
        directlyProvides(resource, IFolder)
        resource['a'] = testing.DummyResource()
        context = DummyResourceDumpContext()
        inst._make_dump_context = lambda *arg, **kw: context
        inst.dump(resource, 'directory', subresources=True)
        self.assertEqual(context.dumped, resource['a'])

    def test_dump_callbacks(self):
        from zope.interface import directlyProvides
        from substanced.interfaces import IFolder
        self.config.registry
        inst = self._makeOne()
        def callback(rsrc):
            self.assertEqual(rsrc, resource)
        self.config.registry['dumper_callbacks'] = [callback]
        resource = testing.DummyResource()
        directlyProvides(resource, IFolder)
        context = DummyResourceDumpContext()
        inst._make_dump_context = lambda *arg, **kw: context
        inst.dump(resource, 'directory', subresources=True)
        self.assertEqual(context.dumped, resource)

    def test_load_no_subresources(self):
        inst = self._makeOne()
        resource = testing.DummyResource()
        context = DummyResourceDumpContext(resource)
        inst._make_load_context = lambda *arg, **kw: context
        result = inst.load('directory', subresources=False)
        self.assertEqual(result, resource)

    def test_load_with_subresources(self):
        inst = self._makeOne()
        inst.ospath = DummyOSPath()
        inst.oslistdir = DummyOSListdir(['a'])
        resource = testing.DummyResource()
        context = DummyResourceDumpContext(resource)
        inst._make_load_context = lambda *arg, **kw: context
        result = inst.load('directory', subresources=True)
        self.assertEqual(result, resource)

    def test_load_loader_callbacks(self):
        inst = self._makeOne()
        resource = testing.DummyResource()
        def cb(rsrc):
            self.assertEqual(rsrc, resource)
        self.config.registry['loader_callbacks'] = [cb]
        context = DummyResourceDumpContext(resource)
        inst._make_load_context = lambda *arg, **kw: context
        result = inst.load('directory', subresources=False)
        self.assertEqual(result, resource)

class Test_FileOperations(unittest.TestCase):
    def _makeOne(self):
        from . import _FileOperations
        return _FileOperations()

    def test__makedirs(self):
        import os, tempfile, shutil
        inst = self._makeOne()
        try:
            td = tempfile.mkdtemp()
            dn = os.path.join(td, 'foo')
            inst._makedirs(dn)
            self.assertTrue(os.path.isdir(dn))
        finally:
            shutil.rmtree(td)

    def test__open(self):
        import os
        foo = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            'fixture', 'foo.txt'
            )
        inst = self._makeOne()
        with inst._open(foo, 'rb') as fp:
            self.assertEqual(fp.read(), b'Foo.\n')

    def test__exists(self):
        import os
        foo = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            'fixture', 'foo.txt'
            )
        inst = self._makeOne()
        self.assertTrue(inst._exists(foo))

    def test__get_fullpath_makedirs_true(self):
        import os
        inst = self._makeOne()
        prefix = os.path.dirname(os.path.abspath(__file__))
        def makedirs(dn):
            self.assertEqual(os.path.normpath(dn), os.path.normpath(prefix))
        inst._exists = lambda *arg: False
        inst._makedirs = makedirs
        inst.directory = os.path.join(prefix)
        result = inst._get_fullpath('bar', makedirs=True)
        self.assertEqual(result, os.path.join(prefix, 'bar'))

    def test__get_fullpath_makedirs_false(self):
        import os
        inst = self._makeOne()
        prefix = os.path.dirname(os.path.abspath(__file__))
        inst.directory = os.path.join(prefix)
        result = inst._get_fullpath('bar', makedirs=False)
        self.assertEqual(result, os.path.join(prefix, 'bar'))

    def test_openfile_w(self):
        inst = self._makeOne()
        def _get_fullpath(fn, makedirs):
            self.assertEqual(fn, 'a')
            self.assertEqual(makedirs, True)
            return fn
        inst._get_fullpath = _get_fullpath
        def _open(path, mode):
            self.assertEqual(path, 'a')
            self.assertEqual(mode, 'w')
            return 'fp'
        inst._open = _open
        self.assertEqual(inst.openfile_w('a'), 'fp')

    def test_openfile_r(self):
        inst = self._makeOne()
        def _get_fullpath(fn, makedirs=False):
            self.assertEqual(fn, 'a')
            self.assertEqual(makedirs, False)
            return fn
        inst._get_fullpath = _get_fullpath
        def _open(path, mode):
            self.assertEqual(path, 'a')
            self.assertEqual(mode, 'r')
            return 'fp'
        inst._open = _open
        self.assertEqual(inst.openfile_r('a'), 'fp')

    def test_exists(self):
        inst = self._makeOne()
        def _get_fullpath(fn, makedirs=False):
            self.assertEqual(fn, 'a')
            self.assertEqual(makedirs, False)
            return fn
        inst._get_fullpath = _get_fullpath
        def _exists(path):
            self.assertEqual(path, 'a')
            return True
        inst._exists = _exists
        self.assertEqual(inst.exists('a'), True)

class Test_YAMLOperations(unittest.TestCase):
    def _makeOne(self):
        from . import _YAMLOperations
        return _YAMLOperations()

    def test_load_yaml(self):
        import contextlib
        import io
        from yaml.loader import Loader
        inst = self._makeOne()
        stream = io.BytesIO(b'foo 1')
        @contextlib.contextmanager
        def openfile(fn, mode):
            self.assertEqual(fn, 'fn')
            self.assertEqual(mode, 'rb')
            yield stream
        inst.openfile_r = openfile
        inst.registry = {'yaml_loader':Loader}
        result = inst.load_yaml('fn')
        self.assertEqual(result, 'foo 1')

    def test_dump_yaml(self):
        import contextlib
        import io
        from yaml.dumper import Dumper
        inst = self._makeOne()
        stream = io.BytesIO()
        @contextlib.contextmanager
        def openfile(fn, mode):
            self.assertEqual(fn, 'fn')
            self.assertEqual(mode, 'wb')
            yield stream
        inst.openfile_w = openfile
        inst.registry = {'yaml_dumper':Dumper}
        result = inst.dump_yaml('abc', 'fn')
        self.assertEqual(result, None)
        self.assertEqual(stream.getvalue(), b'abc\n...\n')

class Test_ResourceContext(unittest.TestCase):
    def _makeOne(self):
        from . import _ResourceContext
        return _ResourceContext()

    def test_resolve_dotted_name(self):
        import substanced.dump.tests
        inst = self._makeOne()
        result = inst.resolve_dotted_name('substanced.dump.tests')
        self.assertEqual(result, substanced.dump.tests)

    def test_get_dotted_name(self):
        import substanced.dump.tests
        inst = self._makeOne()
        result = inst.get_dotted_name(substanced.dump.tests)
        self.assertEqual(result, 'substanced.dump.tests')

class Test_ResourceDumpContext(unittest.TestCase):
    def _makeOne(self, directory, registry, dumpers, verbose, dry_run):
        from . import _ResourceDumpContext
        return _ResourceDumpContext(
            directory, registry, dumpers, verbose, dry_run
            )

    def test_dump_resource(self):
        registry = {}
        inst = self._makeOne(None, registry, None, None, None)
        resource = testing.DummyResource()
        resource.__name__ = 'foo'
        resource.__is_service__ = True
        def get_content_type(rsrc, reg):
            self.assertEqual(rsrc, resource)
            self.assertEqual(reg, registry)
            return 'ct'
        def get_oid(resource):
            return 'oid'
        def dump_yaml(data, filename):
            self.assertEqual(data['content_type'], 'ct')
            self.assertEqual(data['name'], resource.__name__)
            self.assertEqual(data['oid'], 'oid')
            self.assertEqual(data['is_service'], True)
            return 'dumped'
        inst.get_content_type = get_content_type
        inst.get_oid = get_oid
        inst.dump_yaml = dump_yaml
        result = inst.dump_resource(resource)
        self.assertEqual(result, 'dumped')

    def test_dump(self):
        resource = testing.DummyResource()
        dumper = DummyDumperAndLoader()
        inst = self._makeOne(None, None, [dumper], None, None)
        def dump_resource(rsrc):
            self.assertEqual(rsrc, resource)
        inst.dump_resource = dump_resource
        inst.dump(resource)
        self.assertEqual(dumper.context, inst)

    def test_add_callback(self):
        registry = {}
        inst = self._makeOne(None, registry, None, None, None)
        inst.add_callback(True)
        self.assertEqual(registry['dumper_callbacks'], [True])

class Test_ResourceLoadContext(unittest.TestCase):
    def setUp(self):
        self.config = testing.setUp()

    def tearDown(self):
        testing.tearDown()

    def _makeOne(self, directory, registry, dumpers, verbose, dry_run):
        from . import _ResourceLoadContext
        return _ResourceLoadContext(
            directory, registry, dumpers, verbose, dry_run
            )

    def test_load_resource(self):
        import datetime
        from . import RESOURCE_FILENAME
        registry = self.config.registry
        resource = testing.DummyResource()
        content = DummyContentRegistry(resource)
        registry.content = content
        now = datetime.datetime.now()
        data = {
            'name':'name',
            'oid':1,
            'created':now,
            'is_service':True,
            'content_type':'content_type',
            }
        def load_yaml(fn):
            self.assertEqual(fn, RESOURCE_FILENAME)
            return data
        inst = self._makeOne(None, registry, None, None, None)
        inst.load_yaml = load_yaml
        name, result = inst.load_resource()
        self.assertEqual(name, 'name')
        self.assertEqual(result, resource)
        self.assertEqual(resource.__name__, 'name')
        self.assertEqual(resource.__oid__, 1)
        self.assertTrue(resource.__is_service__)
        self.assertEqual(content.content_type, 'content_type')
        self.assertEqual(content.oid, 1)

    def test_load_resource_create_exc(self):
        import datetime
        from . import RESOURCE_FILENAME
        registry = self.config.registry
        resource = testing.DummyResource()
        content = DummyContentRegistry(resource, raises=ValueError)
        registry.content = content
        now = datetime.datetime.now()
        data = {
            'name':'name',
            'oid':1,
            'created':now,
            'is_service':True,
            'content_type':'content_type',
            }
        def load_yaml(fn):
            self.assertEqual(fn, RESOURCE_FILENAME)
            return data
        inst = self._makeOne(None, registry, None, None, None)
        inst.load_yaml = load_yaml
        class DummyLogger(object):
            def __init__(self):
                self._errors = []
            def error(self, *args, **kw):
                self._errors.append((args, kw))
        inst.logger = logger = DummyLogger()
        self.assertRaises(ValueError, inst.load_resource)

    def test_load(self):
        resource = testing.DummyResource()
        def load_resource():
            return 'name', resource
        loader = DummyDumperAndLoader()
        registry = self.config.registry
        inst = self._makeOne(None, registry, [loader], None, None)
        inst.load_resource = load_resource
        parent = DummyParent()
        result = inst.load(parent)
        self.assertEqual(result, resource)
        self.assertEqual(parent.name, 'name')
        self.assertEqual(parent.resource, resource)
        self.assertEqual(loader.context, inst)

    def test_add_callback(self):
        registry = {}
        inst = self._makeOne(None, registry, None, None, None)
        inst.add_callback(True)
        self.assertEqual(registry['loader_callbacks'], [True])

class TestACLDumper(unittest.TestCase):
    def _makeOne(self, name, registry):
        from . import ACLDumper
        return ACLDumper(name, registry)

    def test_init_adds_yaml_stuff(self):
        from pyramid.security import ALL_PERMISSIONS
        from .._compat import u
        yamlthing = DummyYAMLDumperLoader()
        registry = {'yaml_loader':yamlthing, 'yaml_dumper':yamlthing}
        self._makeOne('name', registry)
        self.assertEqual(len(yamlthing.constructors), 1)
        self.assertEqual(len(yamlthing.representers), 1)
        self.assertEqual(
            yamlthing.constructors[0][1](None, None), ALL_PERMISSIONS
            )
        dumper = testing.DummyResource()
        def represent_scalar(one, two):
            self.assertEqual(one, u('!all_permissions'))
        dumper.represent_scalar = represent_scalar
        yamlthing.representers[0][1](dumper, None)

    def test_dump_no_acl(self):
        yamlthing = DummyYAMLDumperLoader()
        registry = {'yaml_loader':yamlthing, 'yaml_dumper':yamlthing}
        inst = self._makeOne('name', registry)
        context = testing.DummyResource()
        resource = testing.DummyResource()
        context.resource = resource
        result = inst.dump(context)
        self.assertEqual(result, None)

    def test_dump_with_acl(self):
        yamlthing = DummyYAMLDumperLoader()
        registry = {'yaml_loader':yamlthing, 'yaml_dumper':yamlthing}
        inst = self._makeOne('name', registry)
        resource = testing.DummyResource()
        resource.__acl__ = []
        context = DummyResourceDumpContext(resource)
        context.resource = resource
        result = inst.dump(context)
        self.assertEqual(result, None)
        self.assertEqual(context.dumped, [])

    def test_load(self):
        yamlthing = DummyYAMLDumperLoader()
        registry = {'yaml_loader':yamlthing, 'yaml_dumper':yamlthing}
        inst = self._makeOne('name', registry)
        resource = testing.DummyResource()
        context = DummyResourceDumpContext([])
        context.resource = resource
        inst.load(context)
        self.assertEqual(resource.__acl__, [])

class TestWorkflowDumper(unittest.TestCase):
    def _makeOne(self, name, registry):
        from . import WorkflowDumper
        return WorkflowDumper(name, registry)

    def test_dump(self):
        from . import STATE_ATTR
        def dump_yaml(v, fn):
            self.assertEqual(v, True)
            self.assertEqual(fn, 'name.yaml')
        context = testing.DummyResource()
        context.dump_yaml = dump_yaml
        resource = testing.DummyResource()
        context.resource = resource
        setattr(resource, STATE_ATTR, True)
        inst = self._makeOne('name', None)
        inst.dump(context)

    def test_load(self):
        from . import STATE_ATTR
        def load_yaml(fn):
            self.assertEqual(fn, 'name.yaml')
            return True
        context = testing.DummyResource()
        context.exists = lambda *arg: True
        context.load_yaml = load_yaml
        resource = testing.DummyResource()
        context.resource = resource
        inst = self._makeOne('name', None)
        inst.load(context)
        self.assertEqual(getattr(resource, STATE_ATTR), True)

class TestReferencesDumper(unittest.TestCase):
    def _makeOne(self, name, registry):
        from . import ReferencesDumper
        return ReferencesDumper(name, registry)

    def test_dump(self):
        context = testing.DummyResource()
        resource = testing.DummyResource()
        context.resource = resource
        inst = self._makeOne('name', None)
        objectmap = DummyObjectmap([1], [2])
        inst.find_objectmap = lambda *arg: objectmap
        def dump_yaml(references, fn):
            self.assertEqual(
                references,
                {'reftype': {'sources': [1], 'targets': [2]}}
                )
            self.assertEqual(fn, 'name.yaml')
        context.dump_yaml = dump_yaml
        inst.dump(context)

    def test_load(self):
        context = testing.DummyResource()
        context.exists = lambda *arg: True
        resource = testing.DummyResource()
        context.resource = resource
        inst = self._makeOne('name', None)
        inst.get_oid = lambda *arg: 0
        objectmap = DummyObjectmap([1], [2])
        inst.find_objectmap = lambda *arg: objectmap
        def load_yaml(fn):
            self.assertEqual(fn, 'name.yaml')
            return {'reftype': {'sources': [1], 'targets': [2]}}
        callbacks = []
        def add_callback(f):
            callbacks.append(f)
        context.load_yaml = load_yaml
        context.add_callback = add_callback
        inst.load(context)
        self.assertEqual(len(callbacks), 1)
        callbacks[0](inst)
        self.assertEqual(
            objectmap.connected,
            [(0, 2, 'reftype'), (1, 0, 'reftype')]
            )

class TestSDIPropertiesDumper(unittest.TestCase):
    def _makeOne(self, name, registry):
        from . import SDIPropertiesDumper
        return SDIPropertiesDumper(name, registry)

    def test_dump(self):
        context = testing.DummyResource()
        resource = testing.DummyResource()
        def _p_activate():
            pass # this will not be covered if not run
        context.resource = resource
        resource._p_activate = _p_activate
        resource.__sdi_hidden__ = True
        def dump_yaml(v, fn):
            self.assertEqual(v, {'__sdi_hidden__':True})
            self.assertEqual(fn, 'name.yaml')
        context.dump_yaml = dump_yaml
        inst = self._makeOne('name', None)
        inst.dump(context)

    def test_load(self):
        context = testing.DummyResource()
        resource = testing.DummyResource()
        context.exists = lambda *arg: True
        def _p_activate():
            pass # this will not be covered if not run
        context.resource = resource
        resource._p_activate = _p_activate
        def load_yaml(fn):
            self.assertEqual(fn, 'name.yaml')
            return {'a':1}
        context.load_yaml = load_yaml
        inst = self._makeOne('name', None)
        inst.load(context)
        self.assertTrue(resource._p_changed)
        self.assertEqual(resource.a, 1)

class TestDirectlyProvidedInterfacesDumper(unittest.TestCase):
    def _makeOne(self, name, registry):
        from . import DirectlyProvidedInterfacesDumper
        return DirectlyProvidedInterfacesDumper(name, registry)

    def test_dump(self):
        from zope.interface import directlyProvides
        context = testing.DummyResource()
        resource = testing.DummyResource()
        context.resource = resource
        def get_dotted_name(i):
            return 'substanced.dump.IDummy'
        context.get_dotted_name = get_dotted_name
        directlyProvides(resource, IDummy)
        def dump_yaml(v, fn):
            self.assertEqual(v, ['substanced.dump.IDummy'])
            self.assertEqual(fn, 'name.yaml')
        context.dump_yaml = dump_yaml
        inst = self._makeOne('name', None)
        inst.dump(context)

    def test_load(self):
        from zope.interface import directlyProvidedBy
        context = testing.DummyResource()
        resource = testing.DummyResource()
        context.exists = lambda *arg: True
        context.resource = resource
        def resolve_dotted_name(n):
            return IDummy
        context.resolve_dotted_name = resolve_dotted_name
        def load_yaml(fn):
            self.assertEqual(fn, 'name.yaml')
            return ['substanced.dump.IDummy']
        context.load_yaml = load_yaml
        inst = self._makeOne('name', None)
        inst.load(context)
        self.assertEqual(list(directlyProvidedBy(resource).interfaces()),
                         [IDummy])

class TestFolderOrderDumper(unittest.TestCase):
    def _makeOne(self, name, registry):
        from . import FolderOrderDumper
        return FolderOrderDumper(name, registry)

    def test_dump(self):
        from zope.interface import directlyProvides
        from substanced.interfaces import IFolder
        context = testing.DummyResource()
        resource = testing.DummyResource()
        resource.order = ['a']
        context.resource = resource
        def is_ordered():
            return True
        resource.is_ordered = is_ordered
        directlyProvides(resource, IFolder)
        def dump_yaml(v, fn):
            self.assertEqual(v, ['a'])
            self.assertEqual(fn, 'name.yaml')
        context.dump_yaml = dump_yaml
        inst = self._makeOne('name', None)
        inst.dump(context)

    def test_load(self):
        context = testing.DummyResource()
        resource = testing.DummyResource()
        context.exists = lambda *arg: True
        context.resource = resource
        def load_yaml(fn):
            self.assertEqual(fn, 'name.yaml')
            return ['a']
        context.load_yaml = load_yaml
        callbacks = []
        def add_callback(f):
            callbacks.append(f)
        context.add_callback = add_callback
        registry = {}
        inst = self._makeOne('name', registry)
        inst.load(context)
        callbacks[0](inst)
        self.assertEqual(resource.order, ['a'])

class TestPropertySheetDumper(unittest.TestCase):
    def _makeOne(self, name, registry):
        from . import PropertySheetDumper
        return PropertySheetDumper(name, registry)

    def test_init_adds_yaml_stuff(self):
        import colander
        from .._compat import u
        yamlthing = DummyYAMLDumperLoader()
        registry = {'yaml_loader':yamlthing, 'yaml_dumper':yamlthing}
        self._makeOne('name', registry)
        self.assertEqual(len(yamlthing.constructors), 1)
        self.assertEqual(len(yamlthing.representers), 2)
        self.assertEqual(
            yamlthing.constructors[0][1](None, None), colander.null
            )
        dumper = testing.DummyResource()
        def represent_scalar(one, two):
            self.assertEqual(one, u('!colander_null'))
        dumper.represent_scalar = represent_scalar
        yamlthing.representers[0][1](dumper, None)

    def test__get_sheets(self):
        yamlthing = DummyYAMLDumperLoader()
        registry = DummyRegistry(None)
        registry.update({'yaml_loader':yamlthing, 'yaml_dumper':yamlthing})
        inst = self._makeOne('name', registry)
        context = testing.DummyResource()
        resource = testing.DummyResource()
        context.exists = lambda *arg: True
        context.resource = resource
        sheet = DummySheet(None)
        def sheetfactory(rsrc, req):
            self.assertEqual(rsrc, resource)
            self.assertEqual(req.__class__.__name__, 'Request')
            return sheet
        content = DummyContentRegistry([('', sheetfactory)])
        registry.content = content
        val = inst._get_sheets(context)
        result = list(val)
        self.assertEqual(
            result,
            [('__unnamed__', sheet)]
            )
        self.assertEqual(sheet.deleted, '_csrf_token_')

    def test_dump(self):
        yamlthing = DummyYAMLDumperLoader()
        registry = DummyRegistry(None)
        registry.update({'yaml_loader':yamlthing, 'yaml_dumper':yamlthing})
        inst = self._makeOne('name', registry)
        context = testing.DummyResource()
        sheet = DummySheet({'a':1})
        def _get_sheets(ctx):
            self.assertEqual(ctx, context)
            return [('sheet', sheet)]
        inst._get_sheets = _get_sheets
        def dump_yaml(cstruct, fn):
            self.assertEqual(cstruct, {'a':1})
            self.assertEqual(fn, 'propsheets/sheet/properties.yaml')
        context.dump_yaml = dump_yaml
        inst.dump(context)

    def test_load(self):
        yamlthing = DummyYAMLDumperLoader()
        registry = DummyRegistry(None)
        registry.update({'yaml_loader':yamlthing, 'yaml_dumper':yamlthing})
        inst = self._makeOne('name', registry)
        context = testing.DummyResource()
        def add_callback(cb):
            context.cb = cb
        context.exists = lambda *arg: True
        context.add_callback = add_callback
        sheet = DummySheet(None)
        def _get_sheets(ctx):
            self.assertEqual(ctx, context)
            return [('', sheet)]
        inst._get_sheets = _get_sheets
        def load_yaml(fn):
            self.assertEqual(fn, 'propsheets/__unnamed__/properties.yaml')
            return {'a':1}
        context.load_yaml = load_yaml
        inst.load(context)
        context.cb(None)
        self.assertEqual(sheet.appstruct, {'a':1})

class TestAdhocAttrDumper(unittest.TestCase):
    def _makeOne(self, name, registry):
        from . import AdhocAttrDumper
        return AdhocAttrDumper(name, registry)

    def test_dump(self):
        def dump_yaml(v, fn):
            self.assertEqual(v, {'a':1})
            self.assertEqual(fn, 'name.yaml')
        context = testing.DummyResource()
        context.dump_yaml = dump_yaml
        resource = testing.DummyResource()
        context.resource = resource
        def dump():
            return {'a':1}
        resource.__dump__ = dump
        inst = self._makeOne('name', None)
        inst.dump(context)

    def test_load(self):
        def load_yaml(fn):
            self.assertEqual(fn, 'name.yaml')
            return {'a':1}
        context = testing.DummyResource()
        context.exists = lambda *arg: True
        context.load_yaml = load_yaml
        resource = testing.DummyResource()
        context.resource = resource
        def load(values):
            self.assertEqual(values, {'a':1})
        resource.__load__ = load
        inst = self._makeOne('name', None)
        inst.load(context)

    def test_load_without_underunder_load(self):
        def load_yaml(fn):
            self.assertEqual(fn, 'name.yaml')
            return {'a':1}
        context = testing.DummyResource()
        context.exists = lambda *arg: True
        context.load_yaml = load_yaml
        resource = testing.DummyResource()
        context.resource = resource
        inst = self._makeOne('name', None)
        inst.load(context)
        self.assertEqual(resource.a, 1)

class Test_add_dumper(unittest.TestCase):
    def _callFUT(
        self, config, dumper_name, dumper_factory, before=None, after=None
        ):
        from . import add_dumper
        return add_dumper(
            config, dumper_name, dumper_factory, before=before, after=after
            )

    def test_it(self):
        config = DummyConfigurator()
        registry = {}
        config.registry = registry
        self._callFUT(config, 'dumper', 'factory', 'before', 'after')
        self.assertEqual(config.discriminator, ('sd_dumper', 'dumper'))
        config.callable()
        self.assertEqual(
            registry['_sd_dumpers'],
            [['dumper', 'factory', 'before', 'after']]
            )

from zope.interface import Interface

class IDummy(Interface):
    pass

class DummyConfigurator(object):
    def action(self, discriminator, callable=None):
        self.discriminator = discriminator
        self.callable = callable

class DummySheet(object):
    def __init__(self, result):
        self.result = result

    def get_schema(self):
        return self

    def set_schema(self, schema):
        self._schema = schema

    schema = property(get_schema, set_schema)

    def __contains__(self, val):
        return True

    def __delitem__(self, val):
        self.deleted = val

    def bind(self, request=None, context=None, loading=None):
        self.request = request
        self.context = context
        self.loading = loading

    def get(self):
        return self.result

    def set(self, appstruct):
        self.appstruct = appstruct

    def serialize(self, appstruct):
        return appstruct

    def deserialize(self, cstruct):
        return cstruct


class DummyObjectmap(object):
    def __init__(self, sourceids, targetids):
        self._sourceids = sourceids
        self._targetids = targetids
        self.connected = []

    def has_references(self, resource):
        return True

    def get_reftypes(self):
        return ['reftype']

    def sourceids(self, resource, reftype):
        return self._sourceids

    def targetids(self, resource, reftype):
        return self._targetids

    def connect(self, oid, target, reftype):
        self.connected.append((oid, target, reftype))

class DummyYAMLDumperLoader(object):
    def __init__(self):
        self.constructors = []
        self.representers = []
    def add_constructor(self, spec, ctor):
        self.constructors.append((spec, ctor))
    def add_representer(self, thing, repr):
        self.representers.append((thing, repr))

class DummyContentRegistry(object):
    def __init__(self, result, raises=None):
        self.result = result
        self.raises = raises

    def create(self, content_type, **kw):
        self.content_type = content_type
        self.oid = kw['__oid']
        if self.raises:
            raise self.raises
        return self.result

    def metadata(self, resource, what, default=None):
        return self.result

class DummyParent(object):
    def load(self, name, resource, registry=None):
        self.name = name
        self.resource = resource
        self.registry = registry

class DummyDumperAndLoader(object):
    def dump(self, context):
        self.context = context

    load = dump

class DummyResourceDumpContext(object):
    def __init__(self, result=None):
        self.result = result

    def dump(self, resource):
        self.dumped = resource

    def load(self, parent):
        return self.result

    def dump_yaml(self, obj, fn):
        self.dumped = obj

    def load_yaml(self, fn):
        return self.result

    def exists(self, fn):
        return True

class DummyInterface(Interface):
    pass

class DummyRegistry(dict):
    def __init__(self, result):
        self.result = result
        dict.__init__(self)

    def queryUtility(self, iface, default=None):
        return self.result

    def registerUtility(self, ordered, iface):
        self.ordered = ordered

class DummyOSPath(object):
    def join(self, directory, other):
        return other

    def exists(self, dir):
        return True

    def abspath(self, path):
        return path

    def normpath(self, path):
        return path

    def isdir(self, dir):
        return True

class DummyOSListdir(object):
    def __init__(self, results):
        self.results = results

    def __call__(self, dir):
        if self.results:
            return self.results.pop(0)
        return []
