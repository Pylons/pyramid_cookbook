import os
import deform
from pkg_resources import resource_filename
from deform.template import ZPTTemplateLoader
from translationstring import ChameleonTranslate

from pyramid.i18n import get_localizer
from pyramid.renderers import get_renderer
from pyramid.threadlocal import get_current_request

class WidgetRendererFactory(object):
    """
    Construct a custom Chameleon ZPT :term:`renderer` for Deform/Substance D.

    If the template name is an asset spec (ends with a concrete filename
    extension), use the Pyramid rendering machinery to resolve it.
    Otherwise, fall back to the Deform rendering (search-path-based)
    machinery to resolve it.

    This allows users to specify templates without the trouble of needing to
    add search paths to the deform rendering machinery.

    **Arguments**

    search_path
      A sequence of strings representing fully qualified filesystem
      directories containing Deform Chameleon template sources.  The
      order in which the directories are listed within ``search_path``
      is the order in which they are checked for the template provided
      to the renderer.

    auto_reload
       If true, automatically reload templates when they change (slows
       rendering).  Default: ``True``.

    debug
       If true, show nicer tracebacks during Chameleon template rendering
       errors (slows rendering).  Default: ``True``.

    encoding
       The encoding that the on-disk representation of the templates
       and all non-ASCII values passed to the template should be
       expected to adhere to.  Default: ``utf-8``.

    translator
       A translation function used for internationalization when the
       ``i18n:translate`` attribute syntax is used in the Chameleon
       template is active or a
       :class:`translationstring.TranslationString` is encountered
       during output.  It must accept a translation string and return
       an interpolated translation.  Default: ``None`` (no translation
       performed).
    """
    def __init__(self, search_path, auto_reload=True, debug=False,
                 encoding='utf-8', translator=None):
        self.translate = translator
        loader = ZPTTemplateLoader(search_path=search_path,
                                   auto_reload=auto_reload,
                                   debug=debug,
                                   encoding=encoding,
                                   translate=ChameleonTranslate(translator))
        self.loader = loader

    def __call__(self, template_name, **kw):
        return self.load(template_name)(**kw)

    def load(self, template_name):
        name, ext = os.path.splitext(template_name)
        if ext:
            return get_renderer(template_name).implementation()
        else:
            return self.loader.load(template_name + '.pt')

def translator(term): # pragma: no cover
    return get_localizer(get_current_request()).translate(term)

def includeme(config): # pragma: no cover
    # specify both deform and deform_bootstrap templates as "fallback"
    # locations; assume user-supplied templates will be specified using asset
    # specs instead.
    deform_dir = resource_filename('deform', 'templates/')
    deform_bootstrap_dir = resource_filename('deform_bootstrap', 'templates/')
    search_path = (deform_bootstrap_dir, deform_dir)
    renderer = WidgetRendererFactory(search_path, translator=translator)
    deform.Form.set_default_renderer(renderer)
