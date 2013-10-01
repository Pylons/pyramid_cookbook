from zope.interface import (
    Interface,
    implementer,
    )

from ..file import IFile
from ..util import chunks

class IEditable(Interface):
    """ Adapter interface for editing content as a file.
    """
    def get():
        """ Return ``(body_iter, mimetype)`` representing the context.

        - ``body_iter`` is an iterable, whose chunks are bytes represenating
          the context as an editable file.

        - ``mimetype`` is the MIMEType corresponding to ``body_iter``.
        """

    def put(fileish):
        """ Update context based on the contents of ``fileish``.

        - ``fileish`` is a file-type object:  its ``read`` method should
          return the (new) file representation of the context.
        """

@implementer(IEditable)
class FileEditable(object):
    """ IEditable adapter for stock SubstanceD 'File' objects.
    """
    def __init__(self, context, request):
        self.context = context
        self.request = request

    def get(self):
        """ See IEditable.
        """
        return (
            chunks(open(self.context.blob.committed(), 'rb')),
            self.context.mimetype or 'application/octet-stream',
            )

    def put(self, fp):
        """ See IEditable.
        """
        self.context.upload(fp)

def register_editable_adapter(config, adapter, iface): # pragma: no cover
    """ Configuration directive: register ``IEditable`` adapter for ``iface``.

    - ``adapter`` is the adapter factory (a class or other callable taking
      ``(context, request)``).

    - ``iface`` is the interface / class for which the adapter is registerd.
    """
    def register():
        intr['registered'] = adapter
        config.registry.registerAdapter(adapter, (iface, Interface), IEditable)

    discriminator = ('sd-editable-adapter', iface)
    intr = config.introspectable(
        'sd editable adapters',
        discriminator,
        iface.__name__,
        'sd editable adapter'
        )
    intr['adapter'] = adapter

    config.action(discriminator, callable=register, introspectables=(intr,))

def includeme(config): # pragma: no cover
    config.add_directive('register_editable_adapter', register_editable_adapter)
    config.register_editable_adapter(FileEditable, IFile)
