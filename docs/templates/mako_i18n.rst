.. _mako_i18n:

Mako Internationalization
-------------------------

.. note:: This recipe is extracted, with permission, from a `blog post made
   by Alexandre Bourget
   <http://blog.abourget.net/2011/1/13/pyramid-and-mako:-how-to-do-i18n-the-pylons-way/>`_.

First, add subscribers within your Pyramid project's ``__init__.py``::

   def main(...):
       ...
       config.add_subscriber('YOURPROJECT.subscribers.add_renderer_globals',
                             'pyramid.events.BeforeRender')
       config.add_subscriber('YOURPROJECT.subscribers.add_localizer',
                             'pyramid.events.NewRequest')

Then add, a ``subscribers.py`` module to your project's package directory::

   # subscribers.py

   from pyramid.i18n import get_localizer, TranslationStringFactory

   def add_renderer_globals(event):
       ...
       request = event['request']
       event['_'] = request.translate
       event['localizer'] = request.localizer

   tsf = TranslationStringFactory('YOUR_GETTEXT_DOMAIN')

   def add_localizer(event):
       request = event.request
       localizer = get_localizer(request)
       def auto_translate(*args, **kwargs):
           return localizer.translate(tsf(*args, **kwargs))
       request.localizer = localizer
       request.translate = auto_translate

After this has been done, the next time you start your application, in your
Mako template, you'll be able to use the simple ``${_(u"Translate this string
please")}`` without having to use ``get_localizer`` explicitly, as its
functionality will be enclosed in the ``_`` function, which will be exposed
as a top-level template name. ``localizer`` will also be available for plural
forms and fancy stuff.

This will also allow you to use translation in your view code, using
something like::

   def my_view(request):
       _ = request.translate
       request.session.flash(_("Welcome home"))

For all that to work, you'll need to:

.. code-block:: text
   :linenos:

   (env)$ easy_install Babel

And you'll also need to run these commands in your project's directory:

.. code-block:: text
   :linenos:

   (env)$ python setup.py extract_messages
   (env)$ python setup.py init_catalog -l en
   (env)$ python setup.py init_catalog -l fr
   (env)$ python setup.py init_catalog -l es
   (env)$ python setup.py init_catalog -l it
   (env)$ python setup.py update_catalog
   (env)$ python setup.py compile_catalog

Repeat the ``init_catalog`` step for each of the langauges you need.

.. note::

   The gettext sub-directory of your project is ``locale/`` in Pyramid, and
   not ``i18n/`` as it was in Pylons. You'll notice that in the default
   setup.cfg of a Pyramid project.

At this point you'll also need to add your local directory to your 
project's configuration::

    def main(...):
       ...
       config.add_translation_dirs('YOURPROJECT:locale')

Lastly, you'll want to have your Mako files extracted when you run
extract_messages, so add these to your setup.py (yes, you read me right, in
setup.py so that Babel can use it when invoking it's commands)::

   setup(
       ...
       install_requires=[
           ...
           Babel,
           ...
           ],
       message_extractors = {'yourpackage': [
               ('**.py', 'python', None),
               ('templates/**.html', 'mako', None),
               ('templates/**.mako', 'mako', None),
               ('static/**', 'ignore', None)]},
       ...
       )

In the above triples the last element, ``None`` in this snippet, may be used
to pass an options dictionary to the specified extractor. For instance, you may
need to set Mako input encoding using the corresponding option::
    
    ...
               ('templates/**.mako', 'mako', {'input_encoding': 'utf-8'}),
    ...
