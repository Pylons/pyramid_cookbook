.. _chameleon_i18n:

Chameleon Internationalization
------------------------------

.. note:: This recipe was created to document the process of internationalization
   (i18n) and localization (l10n) of chameleon templates. There is not much to 
   it, really, but as the author was baffled by this fact, it seems a good idea 
   to describe the few necessary steps.

We start off with a virtualenv and a fresh Pyramid project created via paster:

.. code-block:: text
   :linenos:

   $ virtualenv --no-site-packages env
   $ env/bin/pip install pyramid
   $ env bin/paster create -t pyramid_routesalchemy ChameleonI18n 




First, add dependencies to your Pyramid project's ``setup.py``:

.. code-block:: python
   :linenos:

   requires = [
       ...
       'Babel',
       'lingua',
       ]
   ...
   message_extractors = { '.': [
       ('**.py',   'lingua_python', None ),
       ('**.pt',   'lingua_xml', None ),
       ]},
   


Next, add a folder for the locales POT & PO files:

.. code-block:: text
   :linenos:

   $ mkdir chameleoni18n/locale


Well, let's translate some parts of the given template ``mytemplate.pt``. Add a 
namespace and an i18n:domain to the <html> tag:

.. code-block:: text
   -<html xmlns="http://www.w3.org/1999/xhtml" xml:lang="en" xmlns:tal="http://xml.zope.org/namespaces/tal">
   +<html xmlns="http://www.w3.org/1999/xhtml" xml:lang="en" xmlns:tal="http://xml.zope.org/namespaces/tal"
   +      xmlns:i18n="http://xml.zope.org/namespaces/i18n"
   +      i18n:domain="ChameleonI18n">
    

The important bit -- the one the author was missing -- is that the i18n:domain 
must be spelled exactely like the POT/PO/MO files created later on, including
case. Without this, the translations will not be picked up.

So now we can mark a part of the template for translation:

.. code-block:: text
   -          <h2>Search documentation</h2>
   +          <h2 i18n:translate="search_documentation">Search documentation</h2>

The i18n:translate attribute tells lingua to extract the contents of the h2 tag
to the catalog POT. You don't have to add a description (like in this example
'search_documentation'), but it makes it easier for translators.


Now you need to run these commands in your project's directory:

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

The first command will extract the strings for translation to your projects
locale/<project-name>.pot file, in this case ChameleonI18n.pot 

.. note::

   The gettext sub-directory of your project is ``locale/`` in Pyramid, and
   not ``i18n/`` as it was in Pylons. You'll notice that in the default
   setup.cfg of a Pyramid project, which has all the necessary settings to
   make the above commands work.


At this point you'll also need to add your local directory to your 
project's configuration:

.. code-block:: python
   :linenos:

    def main(...):
       ...
       config.add_translation_dirs('YOURPROJECT:locale')


You can now change the default locale for your project in ``development.ini``
and see if the translations are being picked up.

.. code-block:: text
   :linenos:

   -  pyramid.default_locale_name = en
   +  pyramid.default_locale_name = de

