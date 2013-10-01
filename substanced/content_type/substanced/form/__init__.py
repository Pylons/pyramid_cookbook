import binascii
import os

import deform
import deform.form
import deform.exception
import deform.widget

from pyramid.exceptions import ConfigurationError

from ..util import chunks

# assume jquery is already loaded in our widget resource list, use asset
# specs instead of relative paths

default_resources = {
    'jquery': {
        None:{},
        },
    'jqueryui': {
        None:{
            'js':'deform:static/scripts/jquery-ui-1.8.11.custom.min.js',
            'css':'deform:static/css/ui-lightness/jquery-ui-1.8.11.custom.css',
            },
        },
    'jquery.form': {
        None:{
            'js':'deform:static/scripts/jquery.form-3.09.js',
            },
        },
    'jquery.maskedinput': {
        None:{
            'js':'deform:static/scripts/jquery.maskedinput-1.2.2.min.js',
            },
        },
    'jquery.maskMoney': {
        None:{
            'js':'deform:static/scripts/jquery.maskMoney-1.4.1.js',
            },
        },
    'datetimepicker': {
        None:{
            'js':'deform:static/scripts/jquery-ui-timepicker-addon.js',
            'css':'deform:static/css/jquery-ui-timepicker-addon.css',
            },
        },
    'deform': {
        None:{
            'js':('deform:static/scripts/jquery.form-3.09.js', 
                  'deform:static/scripts/deform.js',
                  'deform_bootstrap:static/deform_bootstrap.js'),
            'css':'deform:static/css/form.css',
            },
        },
    'bootstrap': {
        None: {},
    },
    'tinymce': {
        None:{
            'js':'deform:static/tinymce/jscripts/tiny_mce/tiny_mce.js',
            },
        },
    'chosen': {
        None:{
            'js':'deform_bootstrap:static/jquery_chosen/chosen.jquery.js',
            'css':('deform_bootstrap:static/chosen_bootstrap.css',
                   'deform_bootstrap:static/jquery_chosen/chosen.css')
            },
        },
    'modernizr': {
        None:{
            'js':('deform:static/scripts/modernizr.custom.input-types-and-atts.js',),
            },
        },
    }

# NB: don't depend on deform_bootstrap.css, it uses less, and its .less
# includes 1) the bootstrap css, 2) the datepicker css and 3) the chosen css.
# We supply chosen requirements above, and we already depend on the bootstrap
# css sitewide.  We don't yet depend on the datepicker css, but when we do,
# we'll also just add it sitewide.  Rationale: the deform_bootstrap css when
# included causes the halfling images to go missing and it makes the CSS harder
# to debug due to all the repetition with the sitewide-loaded bootstrap CSS.  I
# should fix at least the halflings images portion of this and submit a patch
# upstream.

resource_registry = deform.widget.ResourceRegistry(use_defaults=False)
resource_registry.registry = default_resources

class FormError(Exception):
    """Non-validation-related error.
    """

class Form(deform.form.Form):
    """ Subclass of ``deform.form.Form`` which uses a custom resource
    registry designed for Substance D. XXX point at deform docs. """
    default_resource_registry = resource_registry

class FormView(object):
    """ A class which can be used as a view which introspects a schema to
    present the form.  XXX describe better using ``pyramid_deform``
    documentation."""
    form_class = Form
    buttons = ()
    schema = None

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def _build_form(self):
        use_ajax = getattr(self, 'use_ajax', False)
        ajax_options = getattr(self, 'ajax_options', '{}')
        action = getattr(self, 'action', '')
        method = getattr(self, 'method', 'POST')
        formid = getattr(self, 'formid', 'deform')
        autocomplete = getattr(self, 'autocomplete', None)
        self.schema = self.schema.bind(
            request=self.request, context=self.context)
        form = self.form_class(self.schema, action=action, method=method,
                               buttons=self.buttons, formid=formid,
                               use_ajax=use_ajax, ajax_options=ajax_options,
                               autocomplete=autocomplete)
        # XXX override autocomplete; should be part of deform_bootstrap
        form.widget.template = 'substanced:widget/templates/form.pt' 
        self.before(form)
        reqts = form.get_widget_resources()
        return form, reqts

    def __call__(self):
        form, reqts = self._build_form()
        result = None

        for button in form.buttons:
            if button.name in self.request.POST:
                success_method = getattr(self, '%s_success' % button.name)
                try:
                    controls = self.request.POST.items()
                    validated = form.validate(controls)
                except deform.exception.ValidationFailure as e:
                    fail = getattr(self, '%s_failure' % button.name, None)
                    if fail is None:
                        fail = self.failure
                    result = fail(e)
                else:
                    try:
                        result = success_method(validated)
                    except FormError as e:
                        snippet = '<div class="error">Failed: %s</div>' % e
                        self.request.session.flash(snippet, 'error',
                                                allow_duplicate=True)
                        result = {'form': form.render(validated)}
                break

        if result is None:
            result = self.show(form)

        if isinstance(result, dict):
            result['js_links'] = reqts['js']
            result['css_links'] = reqts['css']

        return result

    def before(self, form):
        pass

    def failure(self, e):
        return {
            'form':e.render(),
            }

    def show(self, form):
        return {
            'form':form.render(),
            }

_marker = object()

class FileUploadTempStore(object):
    """ A Deform ``FileUploadTempStore`` implementation that stores file
    upload data in the Pyramid session and on disk.  The request passed to
    its constructor must be a fully-initialized Pyramid request (it have a
    ``registry`` attribute, which must have a ``settings`` attribute, which
    must be a dictionary).  The ``substanced.uploads_tempdir`` variable in the
    ``settings`` dictionary must be set to the path of an existing directory
    on disk.  This directory will temporarily store file upload data on
    behalf of Deform and Substance D when a form containing a file upload
    widget fails validation.

    See the :term:`Deform` documentation for more information about
    ``FileUploadTempStore`` objects.
    """
    def __init__(self, request):
        try:
            self.tempdir=request.registry.settings['substanced.uploads_tempdir']
        except KeyError:
            raise ConfigurationError(
                'To use FileUploadTempStore, you must set a  '
                '"substanced.uploads_tempdir" key in your .ini settings. It '
                'points to a directory which will temporarily '
                'hold uploaded files when form validation fails.')
        self.request = request
        self.session = request.session
        
    def preview_url(self, uid):
        root = self.request.virtual_root
        return self.request.sdiapi.mgmt_path(
            root, '@@preview_image_upload', uid)

    def __contains__(self, name):
        return name in self.session.get('substanced.tempstore', {})

    def __setitem__(self, name, data):
        newdata = data.copy()
        stream = newdata.pop('fp', None)

        if stream is not None:
            while True:
                randid = binascii.hexlify(os.urandom(20)).decode('ascii')
                fn = os.path.join(self.tempdir, randid)
                if not os.path.exists(fn): # XXX race condition
                    break
            newdata['randid'] = randid
            with open(fn, 'w+b') as fp:
                for chunk in chunks(stream):
                    fp.write(chunk)

        self._tempstore_set(name, newdata)

    def _tempstore_set(self, name, data):
        # cope with sessioning implementations that cant deal with
        # in-place mutation of mutable values (temporarily?)
        existing = self.session.get('substanced.tempstore', {})
        existing[name] = data
        self.session['substanced.tempstore'] = existing

    def clear(self):
        data = self.session.pop('substanced.tempstore', {})
        for k, v in data.items():
            if 'randid' in v:
                randid = v['randid']
                fn = os.path.join(self.tempdir, randid)
                try:
                    os.remove(fn)
                except OSError:
                    pass

    def get(self, name, default=None):
        data = self.session.get('substanced.tempstore', {}).get(name)

        if data is None:
            return default

        newdata = data.copy()
            
        randid = newdata.get('randid')

        if randid is not None:

            fn = os.path.join(self.tempdir, randid)
            try:
                newdata['fp'] = open(fn, 'rb')
            except IOError:
                pass

        return newdata

    def __getitem__(self, name):
        data = self.get(name, _marker)
        if data is _marker:
            raise KeyError(name)
        return data

