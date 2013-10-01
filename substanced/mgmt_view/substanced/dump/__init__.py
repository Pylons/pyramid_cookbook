import logging
import os

from zope.interface import (
    Interface,
    directlyProvidedBy,
    alsoProvides,
    )
from zope.interface.interface import InterfaceClass
from pyramid.request import Request
from pyramid.security import AllPermissionsList, ALL_PERMISSIONS
from pyramid.threadlocal import get_current_registry
from pyramid.traversal import resource_path
from pyramid.util import (
    DottedNameResolver,
    TopologicalSorter,
    )
from ZODB.blob import Blob
import yaml

from substanced.workflow import STATE_ATTR
from substanced.objectmap import find_objectmap
from substanced.sdi import sdiapi
from substanced.util import (
    get_oid,
    set_oid,
    get_acl,
    get_dotted_name,
    get_content_type,
    is_folder,
    )
from .._compat import TEXT
from .._compat import u
from .._compat import decodebytes
from .._compat import encodebytes


logger = logging.getLogger(__name__)

RESOURCE_FILENAME = 'resource.yaml'
RESOURCES_DIRNAME = 'resources'

dotted_name_resolver = DottedNameResolver()

class IDumperFactories(Interface):
    pass

def set_yaml(registry):
    # grrr.. pyyaml has class-based global registries, so we need to
    # subclass to provide them

    class SDumper(yaml.Dumper):
        pass

    class SLoader(yaml.Loader):
        pass

    registry['yaml_loader'] = SLoader
    registry['yaml_dumper'] = SDumper

    def iface_representer(dumper, data):
        return dumper.represent_scalar(u('!interface'), get_dotted_name(data))
    def iface_constructor(loader, node):
        return dotted_name_resolver.resolve(node.value)

    SDumper.add_multi_representer(InterfaceClass, iface_representer)
    SLoader.add_constructor(u('!interface'), iface_constructor)

    def blob_representer(dumper, data):
        with data.open('r') as f:
            data = f.read()
        encoded = encodebytes(data)
        u_encoded = encoded.decode('ascii')
        return dumper.represent_scalar(u('!blob'), u_encoded)
    def blob_constructor(loader, node):
        value = node.value
        if isinstance(value, TEXT):
            value = value.encode('ascii')
        return Blob(decodebytes(value))

    SDumper.add_representer(Blob, blob_representer)
    SLoader.add_constructor(u('!blob'), blob_constructor)


def get_dumpers(registry):
    ordered = registry.queryUtility(IDumperFactories, default=None)
    if ordered is None:
        tsorter = TopologicalSorter()
        dumpers = registry.pop('_sd_dumpers', [])
        for n, f, b, a in dumpers:
            tsorter.add(n, f, before=b, after=a)
        ordered = tsorter.sorted()
        registry.registerUtility(ordered, IDumperFactories)
    dumpers = [f(n, registry) for n, f in ordered]
    return dumpers

class _DumpAndLoad(object):
    # this is only a class for testing purposes

    set_yaml = staticmethod(set_yaml) # for testing
    get_dumpers = staticmethod(get_dumpers) # for testing
    ospath = os.path # for testing
    oslistdir = staticmethod(os.listdir) # for testing
    logger = logger # for testing

    def _make_dump_context(
        self, directory, registry, dumpers, verbose, dry_run
        ):
        # broken out for testing
        return _ResourceDumpContext(
            directory,
            registry,
            dumpers,
            verbose,
            dry_run
            )

    def _make_load_context(
        self, directory, registry, dumpers, verbose, dry_run
        ):
        # broken out for testing
        return _ResourceLoadContext(
            directory,
            registry,
            dumpers,
            verbose,
            dry_run
            )

    def dump(
        self,
        resource,
        directory,
        subresources=True,
        verbose=False,
        dry_run=False,
        registry=None
        ):
        """ Dump a resource to ``directory``. The resource will be represented
        by at least one properties file and other subdirectories.
        Sub-resources will dumped as subdirectories if ``subresources`` is
        True."""

        if registry is None:
            registry = get_current_registry()

        self.set_yaml(registry)

        dumpers = self.get_dumpers(registry)

        stack = [(self.ospath.abspath(self.ospath.normpath(directory)),
                  resource)]
        first = None

        while stack: # breadth-first is easiest

            directory, resource = stack.pop()

            if first is None:
                first = resource

            context = self._make_dump_context(
                directory,
                registry,
                dumpers,
                verbose,
                dry_run
                )

            logger.info('Dumping %s' % resource_path(resource))
            context.dump(resource)

            if not subresources:
                break

            if is_folder(resource):
                for subresource in resource.values():
                    subdirectory = self.ospath.join(
                        directory,
                        RESOURCES_DIRNAME,
                        subresource.__name__
                        )
                    stack.append((subdirectory, subresource))

        callbacks = registry.pop('dumper_callbacks', ())

        for callback in callbacks:
            callback(first)

    def load(
        self,
        directory,
        parent=None,
        subresources=True,
        verbose=False,
        dry_run=False,
        registry=None
        ):
        """ Load a dump of a resource and return the resource."""

        if registry is None:
            registry = get_current_registry()

        self.set_yaml(registry)

        stack = [(self.ospath.abspath(self.ospath.normpath(directory)), parent)]

        first = None

        dumpers = self.get_dumpers(registry)

        while stack: # breadth-first is easiest

            directory, parent = stack.pop()

            context = self._make_load_context(
                directory,
                registry,
                dumpers,
                verbose,
                dry_run
                )

            self.logger.info('Loading %s' % directory)
            resource = context.load(parent)

            if first is None:
                first = resource

            if not subresources:
                break

            subobjects_dir = self.ospath.join(directory, RESOURCES_DIRNAME)

            if self.ospath.exists(subobjects_dir):
                for fn in self.oslistdir(subobjects_dir):
                    fullpath = self.ospath.join(subobjects_dir, fn)
                    subresource_fn = self.ospath.join(
                        fullpath, RESOURCE_FILENAME
                        )
                    if ( self.ospath.isdir(fullpath) and
                         self.ospath.exists(subresource_fn) ):
                        stack.append((fullpath, resource))

        callbacks = registry.pop('loader_callbacks', ())
        for callback in callbacks:
            callback(first)

        return first

_dumpandload = _DumpAndLoad()

dump = _dumpandload.dump
load = _dumpandload.load
                    
class _FileOperations(object):

    def _makedirs(self, path): # for testing
        return os.makedirs(path)

    def _open(self, path, mode): # for testing
        return open(path, mode)

    def _exists(self, path): # for testing
        return os.path.exists(path) 

    def _get_fullpath(self, filename, makedirs=False):
        subdirs, filename = os.path.split(os.path.normpath(filename))

        # self.directory defined in subclasses
        prefix = os.path.join(self.directory, subdirs)

        if makedirs:
            if not self._exists(prefix):
                # XXX race condition
                self._makedirs(prefix)

        fullpath = os.path.join(prefix, filename)

        return fullpath
        
    def openfile_w(self, filename, mode='w', makedirs=True):
        path = self._get_fullpath(filename, makedirs=makedirs)
        fp = self._open(path, mode)
        return fp

    def openfile_r(self, filename, mode='r'):
        path = self._get_fullpath(filename)
        fp = self._open(path, mode)
        return fp

    def exists(self, filename):
        path = self._get_fullpath(filename)
        return self._exists(path)

class _YAMLOperations(_FileOperations):

    def load_yaml(self, filename):
        with self.openfile_r(filename, 'rb') as fp:
            return yaml.load(fp, Loader=self.registry['yaml_loader'])

    def dump_yaml(self, obj, filename):
        with self.openfile_w(filename, 'wb') as fp:
            return yaml.dump(obj, fp, Dumper=self.registry['yaml_dumper'],
                             encoding='utf-8')

class _ResourceContext(_YAMLOperations):
    dotted_name_resolver = dotted_name_resolver
    
    def resolve_dotted_name(self, dotted):
        return self.dotted_name_resolver.resolve(dotted)

    def get_dotted_name(self, obj):
        return get_dotted_name(obj)

class _ResourceDumpContext(_ResourceContext):

    get_content_type = staticmethod(get_content_type) # testing
    get_oid = staticmethod(get_oid) # testing

    def __init__(self, directory, registry, dumpers, verbose, dry_run):
        self.directory = directory
        self.registry = registry
        self.dumpers = dumpers
        self.verbose = verbose
        self.dry_run = dry_run

    def dump_resource(self, resource):
        registry = self.registry
        ct = self.get_content_type(resource, registry)
        data = {
            'content_type':ct,
            'name':resource.__name__,
            'oid':self.get_oid(resource),
            'is_service':bool(getattr(resource, '__is_service__', False)),
            }
        return self.dump_yaml(data, RESOURCE_FILENAME)

    def dump(self, resource):
        self.resource = resource
        self.dump_resource(resource)
        for dumper in self.dumpers:
            dumper.dump(self)

    def add_callback(self, callback):
        dumper_callbacks = self.registry.setdefault('dumper_callbacks', [])
        dumper_callbacks.append(callback)

class _ResourceLoadContext(_ResourceContext):

    logger = logger # testing

    def __init__(self, directory, registry, loaders, verbose, dry_run):
        self.directory = directory
        self.registry = registry
        self.loaders = loaders
        self.verbose = verbose
        self.dry_run = dry_run

    def load_resource(self):
        registry = self.registry
        data = self.load_yaml(RESOURCE_FILENAME)
        name = data['name']
        oid = data['oid']
        is_service = data['is_service']
        try:
            resource = registry.content.create(data['content_type'], __oid=oid)
        except:
            self.logger.error(
                'While trying to load resource with data %r' % (data,)
                )
            raise
        resource.__name__ = name
        set_oid(resource, oid)
        if is_service:
            resource.__is_service__ = True
        return name, resource

    def load(self, parent):
        name, resource = self.load_resource()
        self.name = name
        self.resource = resource
        if parent is not None:
            parent.load(name, resource, registry=self.registry)
        for loader in self.loaders:
            loader.load(self)
        return resource

    def add_callback(self, callback):
        loader_callbacks = self.registry.setdefault('loader_callbacks', [])
        loader_callbacks.append(callback)

class ACLDumper(object):

    get_acl = staticmethod(get_acl) # testing

    def __init__(self, name, registry):
        self.name = name
        self.registry = registry
        self.fn = '%s.yaml' % self.name
        def ap_constructor(loader, node):
            return ALL_PERMISSIONS
        def ap_representer(dumper, data):
            return dumper.represent_scalar(u('!all_permissions'), '')
        registry['yaml_loader'].add_constructor(
            u('!all_permissions'),
            ap_constructor,
            )
        registry['yaml_dumper'].add_representer(
            AllPermissionsList,
            ap_representer,
            )

    def dump(self, context):
        acl = self.get_acl(context.resource, None)
        if acl is None:
            return
        context.dump_yaml(acl, self.fn)

    def load(self, context):
        if context.exists(self.fn):
            acl = context.load_yaml(self.fn)
            context.resource.__acl__ = acl

class WorkflowDumper(object):
    def __init__(self, name, registry):
        self.name = name
        self.registry = registry
        self.fn = '%s.yaml' % self.name

    def dump(self, context):
        resource = context.resource
        if hasattr(resource, STATE_ATTR):
            context.dump_yaml(getattr(resource, STATE_ATTR), self.fn)

    def load(self, context):
        if context.exists(self.fn):
            states = context.load_yaml(self.fn)
            setattr(context.resource, STATE_ATTR, states)

class ReferencesDumper(object):

    find_objectmap = staticmethod(find_objectmap) # testing
    get_oid = staticmethod(get_oid)

    def __init__(self, name, registry):
        self.name = name
        self.registry = registry
        self.fn = '%s.yaml' % self.name

    def dump(self, context):
        resource = context.resource
        objectmap = self.find_objectmap(resource)
        references = {}
        if objectmap is not None:
            if objectmap.has_references(resource):
                for reftype in objectmap.get_reftypes():
                    sourceids = list(objectmap.sourceids(resource, reftype))
                    targetids = list(objectmap.targetids(resource, reftype))
                    if sourceids:
                        d = references.setdefault(reftype, {})
                        d['sources'] = sourceids
                    if targetids:
                        d = references.setdefault(reftype, {})
                        d['targets'] = targetids
        if references:
            context.dump_yaml(references, self.fn)

    def load(self, context):
        if context.exists(self.fn):
            references = context.load_yaml(self.fn)
            resource = context.resource
            oid = self.get_oid(resource)
            def add_references(root):
                objectmap = self.find_objectmap(root)
                if objectmap is not None:
                    for reftype, d in references.items():
                        targets = d.get('targets', ())
                        sources = d.get('sources', ())
                        if objectmap is not None:
                            for target in targets:
                                objectmap.connect(oid, target, reftype)
                            for source in sources:
                                objectmap.connect(source, oid, reftype)
            context.add_callback(add_references)

class SDIPropertiesDumper(object):
    def __init__(self, name, registry):
        self.name = name
        self.registry = registry
        self.fn = '%s.yaml' % self.name

    def dump(self, context):
        resource = context.resource
        resource._p_activate()
        d = resource.__dict__
        attributes = {}
        for name in ('__sdi_hidden__', '__sdi_addable__', '__sdi_deletable__'):
            val = d.get(name)
            if val is not None:
                attributes[name] = val
        if attributes:
            context.dump_yaml(attributes, self.fn)

    def load(self, context):
        resource = context.resource
        if context.exists(self.fn):
            attributes = context.load_yaml(self.fn)
            resource._p_activate()
            resource.__dict__.update(attributes)
            resource._p_changed = True

class DirectlyProvidedInterfacesDumper(object):
    def __init__(self, name, registry):
        self.name = name
        self.registry = registry
        self.fn = '%s.yaml' % self.name

    def dump(self, context):
        resource = context.resource
        ifaces = list(directlyProvidedBy(resource).interfaces())
        if ifaces:
            dotted_names = [ context.get_dotted_name(i) for i in ifaces ]
            context.dump_yaml(dotted_names, self.fn)

    def load(self, context):
        if context.exists(self.fn):
            dotted_names = context.load_yaml(self.fn)
            for name in dotted_names:
                iface = context.resolve_dotted_name(name)
                alsoProvides(context.resource, iface)

class FolderOrderDumper(object):
    def __init__(self, name, registry):
        self.name = name
        self.registry = registry
        self.fn = '%s.yaml' % self.name

    def dump(self, context):
        resource = context.resource
        if is_folder(resource) and resource.is_ordered():
            context.dump_yaml(resource.order, self.fn)
                
    def load(self, context):
        if context.exists(self.fn):
            resource = context.resource
            order = context.load_yaml(self.fn)
            def add_order(root):
                resource.order = order
            # need to defer in order for children to be added
            # XXX keep a reference to resource, ok?
            # XXX _set_order doesn't preserve existing keys?
            context.add_callback(add_order)

class PropertySheetDumper(object):
    def __init__(self, name, registry):
        import colander
        from substanced.objectmap import Multireference
        self.name = name
        self.registry = registry
        def cn_constructor(loader, node):
            return colander.null
        def cn_representer(dumper, data):
            return dumper.represent_scalar(u('!colander_null'), '')
        registry['yaml_loader'].add_constructor(
            u('!colander_null'),
            cn_constructor,
            )
        registry['yaml_dumper'].add_representer(
            colander.null.__class__,
            cn_representer,
            )
        registry['yaml_dumper'].add_representer(
            Multireference,
            cn_representer,
            )

    def _get_sheets(self, context):
        registry = self.registry
        resource = context.resource
        sheets = registry.content.metadata(resource, 'propertysheets', ())
        for sheetname, sheetfactory in sheets:
            if not sheetname:
                sheetname = '__unnamed__'
            request = Request.blank('/')
            request.registry = self.registry
            request.context = context.resource
            request.sdiapi = sdiapi(request)
            sheet = sheetfactory(context.resource, request)
            sheet.schema = sheet.schema.bind(
                request=request, context=context.resource, loading=True
                )
            if '_csrf_token_' in sheet.schema:
                del sheet.schema['_csrf_token_']
            yield sheetname, sheet

    def dump(self, context):
        sheets = self._get_sheets(context)
        for sheetname, sheet in sheets:
            appstruct = sheet.get()
            cstruct = sheet.schema.serialize(appstruct)
            context.dump_yaml(
                cstruct,
                'propsheets/%s/properties.yaml' % sheetname,
                )

    def load(self, context):
        sheets = self._get_sheets(context)
        for sheetname, sheet in sheets:
            if not sheetname:
                sheetname = '__unnamed__'
            fn = 'propsheets/%s/properties.yaml' % sheetname
            if context.exists(fn):
                def callback(root, sheet=sheet, fn=fn, context=context):
                    cstruct = context.load_yaml(fn)
                    appstruct = sheet.schema.deserialize(cstruct)
                    sheet.set(appstruct)
                # this needs to be a callback due to multireference properties
                # that require other objects to be in the objectmap before
                # they can be assigned.
                context.add_callback(callback)

class AdhocAttrDumper(object):
    def __init__(self, name, registry):
        self.name = name
        self.registry = registry
        self.fn = '%s.yaml' % self.name

    def dump(self, context):
        resource = context.resource
        if hasattr(resource, '__dump__'):
            values = resource.__dump__()
            context.dump_yaml(values, self.fn)

    def load(self, context):
        if context.exists(self.fn):
            values = context.load_yaml(self.fn)
            resource = context.resource
            if hasattr(resource, '__load__'):
                resource.__load__(values)
            else:
                for k, v in values.items():
                    setattr(resource, k, v)

def add_dumper(config, dumper_name, dumper_factory, before=None, after=None):
    """ Configurator directive for adding a dumper """
    registry = config.registry
    def register():
        dumpers = registry.setdefault('_sd_dumpers', [])
        dumpers.append([dumper_name, dumper_factory, before, after])
    discriminator = ('sd_dumper', dumper_name)
    config.action(discriminator, callable=register)

def includeme(config): # pragma: no cover
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
