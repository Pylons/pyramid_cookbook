.. meta::
   :description: How to use alternate, YAML or JSON, configuration file
                 formats with a Pyramid application.
   :keywords: Pyramid, YAML, JSON, Configuration, Settings, TOML

.. author: Karl O. Pinc <kop@karlpinc.com>

.. index::
   single: configuration
   single: settings
   single: packaging
   single: pyproject.toml
   pair: alternate; configuration file formats
   pair: JSON; configuration file formats
   pair: YAML; configuration file formats
.. _alternate-configs-yaml-json:

.. "Turn off" automatic line numbering, it interferes with cutting and
   pasting example code.  (Even though the argument is "python", this seems
   to fix shell, toml, and other sorts of code.)
.. highlight:: python
   :linenothreshold: 1000

Move from a :code:`.ini` to a YAML (or JSON) configuration file (and from setup.py to pyproject.toml)
=====================================================================================================

.. toctree::
   :maxdepth: 2

This tutorial demonstrates how to change from a :term:`PasteDeploy`
:code:`.ini` configuration file to a YAML configuration file.
Because JSON is a subset of YAML, JSON is also supported.

.. topic:: TL;DR

   Modify and use the sample YAML :app:`Pyramid` configuration files
   given in the appendixes.
   Adjust your :code:`MANIFEST.in` file to include :code:`*.toml`,
   :code:`*.yaml`, and :code:`*.json` files.

   Update your current :app:`Pyramid` project:

     Modify the sample :code:`pyproject.toml` file provided in the
     Appendix, below.
     Remove the directives configured in :code:`pyproject.toml` from
     your :code:`setup.py` file; perhaps :code:`setup.py` can be deleted.

   Begin a new :app:`Pyramid` project:

     Use the (at the time of this writing) the development version of
     the :code:`pyramid-cookiecutter-starter` package.
     (The :code:`cookiecutter` package must be installed.
     There is an example below.)

     .. code-block:: shell

        cookiecutter gh:Pylons/pyramid-cookiecutter-starter --checkout main

     Alter your :code:`pyproject.toml` file.
     Add :code:`plaster_yaml` to :code:`dependencies`.
     And add the following :term:`entry point`\ s to the
     :code:`[project]` section:

     .. literalinclude:: yaml_and_json_configs/pyproject.toml
        :language: toml
        :lines: 48-50

.. topic:: Why Is Packaging Involved?

   It is the python package that connects your application to a
   configuration file loader, so a packaging example is required.

   This tutorial produces a package which is configured with a
   :code:`pyproject.toml` file, and uses the new :code:`build`
   front-end along with the traditional :term:`setuptools` build
   back-end to actually make the package.
   Should a different back-end be desired, changing it is
   straightforward.

The tutorial begins by creating a "classic" :term:`PasteDeploy`
:app:`Pyramid` application, configured with a :code:`.ini` file.

At the end of the tutorial, you'll have:

* A "Hello World" application that:

  * accepts the traditional :term:`PasteDeploy` :code:`.ini`
    configuration file

  * displays "Hello World" text obtained from a configuration file

  * accepts a sample YAML configuration file, one having a ".yaml" suffix

  * accepts a JSON configuration file, one having a ".json" suffix

* A :code:`pyproject.toml` file suitable for packaging the app;
  with the :pep:`517` compatible :code:`build` program, with
  :term:`setuptools` as the build back-end

* An understanding of how to package a new :app:`Pyramid` application,
  or repackage an existing one, so that it accepts any one of, or all
  of, the :term:`PasteDeploy` :code:`.ini`, YAML, or JSON
  configuration file formats

* A basic understanding of how to set setting values in a YAML
  configuration file and how to access those settings in a
  :app:`Pyramid` application.

Many of the sub-steps of this tutorial test that the previous steps
were completed correctly.
These "check" steps can be skipped, if desired.


Why YAML?
---------

A YAML configuration file can supply your application with data
structures of arbitrary complexity.
YAML values have types, not just scalars like integers and strings
but also more complex types like sequences and mappings.
Your application receives each value put in a YAML configuration file
as Python data, converted from its YAML type to the corresponding
Python data type.
YAML sequences become lists, mappings become dicts, and so forth.

Unlike JSON, YAML support comments.

YAML fits well with Python because its syntax is similar to Python's.
We believe that YAML is usually more concise, consistent, and easier
to read than TOML, although this is a matter about which reasonable
people disagree.

.. topic:: Tips and Tooling

   Because YAML values have types, care must be taken when writing
   configuration files.
   As an example, there is a difference between "10" and 10.
   The former is a string, the latter an integer; a distinction
   important to your application.
   The safe, and readable, approach is to quote all string values.

   Typical YAML, including the samples given herein, rely on block
   indentation.
   The indentation has meaning; getting it wrong has severe consequences.
   Further, YAML syntax mistakes are not always obvious.

   The `yamllint <https://www.pylint.org/>`_ program is useful in this
   regard.
   It checks for valid YAML syntax, reporting errors, suggesting
   solutions, and providing other helpful tips.
   Running :app:`yamllint` on your configuration file after every edit
   helps prevent mis-configuration and the confusing problems it
   causes.

   It can be best to install :app:`yamllint` with your OS's package
   manager.
   This makes the program, and its documentation, readily available.

How it works
------------

:app:`Pyramid` uses the :term:`plaster` configuration loader
interface, which can be extended to use any configuration syntax
desired.
The `plaster-yaml <https://github.com/mardiros/plaster-yaml>`_ package
provides an extension which reads YAML config files.

.. index::
   pair: TOML; configuration file formats

At the time of this writing there are no known :term:`plaster` loaders
for file formats other than YAML, JSON and the :term:`PasteDeploy`
:code:`.ini` format.
Should you wish to support other configuration file syntaxes (for
example, TOML) the recommended approach is to fork and modify the
source of either ``plaster-pastedeploy``, the :code:`.ini` file
configuration file loader, or ``plaster-yaml``, the YAML/JSON loader.


Step 0: Create Python virtual environments
------------------------------------------

We suggest you start by creating a directory and cd-ing into it.
**The examples assume that your current working directory is always
the same, top-level, directory.**
They often begin by changing your current working directory to the
sub-directory holding your :app:`Pyramid` application.

A Python virtual environment is used to hold the Python packages
this tutorial needs to develop and package applications.
We will call this virtual environment :code:`devenv`.
Construct it with the following commands:

.. code-block:: shell

   python3 -m venv devenv
   ./devenv/bin/pip install --upgrade pip
   ./devenv/bin/pip install --upgrade setuptools
   ./devenv/bin/pip install build        ; # for building python packages
   ./devenv/bin/pip install cookiecutter ; # for pyramid setup

A second virtual environment is needed to provide a place in which to
install and run your application.
We will call this virtual environment :code:`appenv`.
Construct it with the following commands:

.. code-block:: shell

   python3 -m venv appenv   
   ./appenv/bin/pip install --upgrade pip
   ./appenv/bin/pip install --upgrade setuptools


Step 1: Create a Hello World application with an INI configuration file
-----------------------------------------------------------------------

Run the following code to create a new :app:`Pyramid` project:

.. code-block:: shell

   ./devenv/bin/cookiecutter --no-input gh:Pylons/pyramid-cookiecutter-starter

You now have an application with the boring name of "pyramid_scaffold".

The "check steps" for this are:

  Install and run the application with:

  .. code-block:: shell

     ./appenv/bin/pip install pyramid_scaffold/
     ./appenv/bin/pserve pyramid_scaffold/production.ini

  Test by using the URL http://localhost:6543 in your browser to
  view your application.

  The pserve server can be stopped by holding down the "Ctrl" key and
  pressing the "C" key in the terminal window.


Step 2: Package the application with a :code:`pyproject.toml` file
------------------------------------------------------------------

Delete the :code:`setup.py` file
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Delete the :code:`setup.py` file.
A :code:`pyproject.toml` file will replace it.

.. code-block:: shell

   cd pyramid_scaffold
   rm setup.py

Create a :code:`pyproject.toml` file
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Current Python packaging practice uses a :code:`pyproject.toml` file
to control packaging.
This file goes in your project's directory, in this case in the
:code:`pyramid_scaffold` directory.

.. include:: yaml_and_json_configs/yaml_config_exceptions.rst

Copy the following text into the
:code:`pyramid_scaffold/pyproject.toml` file:

.. literalinclude:: yaml_and_json_configs/pyproject.toml
   :language: toml
   :lines: 1-8, 10-29, 31-45, 51-57, 59-64, 66-
   :emphasize-lines: 9, 28, 43, 50, 56

All highlighted lines *but* the second designate the name of the
application's package.

The second highlighted line configures support for :code:`.ini`
configuration files.
Removing this line removes support for :term:`PasteDeploy`
:code:`.ini` configuration files.

Add :code:`pyproject.toml` to :code:`MANIFEST.in`
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

In the :code:`MANIFEST.in` file, change the line reading::

  include *.txt *.ini *.cfg *.rst

to read::

  include *.txt *.ini *.cfg *.rst *.toml

With this change the :code:`pyproject.toml` file becomes a part of
your packaged application.

.. 
.. Included section: "Build the package"
.. 
.. include:: yaml_and_json_configs/build.rst

Run the :app:`Pyramid` regression tests
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

(This is a "check step".)

Check that all the regression tests pass by running:

.. code-block:: shell

   cd pyramid_scaffold
   ../devenv/bin/pip install -e ".[tests]"
   ../devenv/bin/pytest -q

Install and run the packaged application
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

(This is a "check step".)

Check that the package works by installing and running it with:

.. code-block:: shell

   cd pyramid_scaffold
   ../appenv/bin/pip install dist/pyramid_scaffold-0.0.tar.gz
   ../appenv/bin/pserve production.ini

Access the application in your web browser by going to:
http://localhost:6543

The application can be stopped by holding down the "Ctrl" key and
pressing the "C" key.


Step 3: Make the displayed text configurable
--------------------------------------------

Add a configuration setting to your configuration file
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Edit the :code:`pyramid_scaffold/development.ini` configuration file.
Add the line ":code:`hello_text = Hello World!`" to the
:code:`[app:main]` section.
You may add a comment if you wish to explain the new line's purpose.

When done, the :code:`[app:main]` section should look something like:

.. code-block:: ini
   :emphasize-lines: 16-17

   [app:main]
   use = egg:pyramid_scaffold

   pyramid.reload_templates = true
   pyramid.debug_authorization = false
   pyramid.debug_notfound = false
   pyramid.debug_routematch = false
   pyramid.default_locale_name = en
   pyramid.includes =
       pyramid_debugtoolbar

   # By default, the toolbar only appears for clients from IP addresses
   # '127.0.0.1' and '::1'.
   # debugtoolbar.hosts = 127.0.0.1 ::1

   # My new configuration setting
   hello_text = Hello World!

Give the new setting to the template for rendering
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The code of the application's view must be altered to pass the new
setting to the template for rendering into HTML.

Edit the :code:`pyramid_scaffold/pyramid_scaffold/views/default.py` file.

Change the line that reads:

.. code-block:: python

   return {'project': 'Pyramid Scaffold'}
                
To two lines that read:

.. code-block:: python
   :emphasize-lines: 2

   return {'project': 'Pyramid Scaffold',
           'hello_msg': request.registry.settings['hello_text']}

.. topic:: Setting names are not template variable names

   The name of the setting in our application is :code:`hello_text`,
   but the value of the setting is passed to the template in a
   variable named :code:`hello_msg`.

   The relevant line of code in
   :code:`pyramid_scaffold/pyramid_scaffold/views/default.py` is
   highlighted, above.

Change the template to render the message
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Edit the
:code:`pyramid_scaffold/pyramid_scaffold/templates/mytemplate.jinja2`
file.

Add a new line reading ":code:`<h1><span
class="font-semi-bold">{{hello_msg}}</h1>`", above the line reading
:code:`</div>`.

The :code:`div` element should now look like:

.. code-block:: html
   :emphasize-lines: 4

   <div class="content">
     <h1><span class="font-semi-bold">Pyramid</span> <span class="smaller">Starter project</span></h1>
     <p class="lead">Welcome to <span class="font-normal">{{project}}</span>, a&nbsp;Pyramid application generated&nbsp;by<br><span class="font-normal">Cookiecutter</span>.</p>
     <h1><span class="font-semi-bold">{{hello_msg}}</h1>
   </div>

Test by running the application in development mode
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

(This is a "check step".)

Check to see that your changes worked by running the application.
The development virtual environment has your application installed in
"editable mode", so it is not necessary to re-package and re-install
the application to reflect changes to the project.
Use the development settings, so the debugtoolbar appears.

Run the application with:

.. code-block:: shell

   cd pyramid_scaffold
   ../devenv/bin/pserve development.ini

Access the application in your web browser by going to:
http://localhost:6543
You should see the "Hello World!" text.

Again, the application can be stopped by holding down the "Ctrl" key
and pressing the "C" key.


Step 4: Support a YAML configuration file format
------------------------------------------------

Require the :code:`plaster-yaml` package
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Change the packaging requirements to make :code:`plaster-yaml` a
required package.

Edit the :code:`pyramid_scaffold/pyproject.toml` file and add
":code:`plaster_yaml`" to the dependences.
The new :code:`dependencies` list should look like:

.. literalinclude:: yaml_and_json_configs/pyproject.toml
   :language: toml
   :lines: 27-35
   :emphasize-lines: 3

Because both the :code:`plaster-pastedeploy` and the
:code:`plaster-yaml` packages are installed the application will (when
the rest of the steps in this section are completed) accept either
:code:`.ini` or YAML confguration files.

"Register" the :code:`plaster-yaml` plugin as a YAML configuration file loader
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The project's packaging must, again, be changed before the
:code:`plaster-yaml` plugin can be used.

A new :term:`entry point` is needed to "register" the ":code:`.yaml`"
file extension, to associate the extension with the configuration file
loader supporting YAML content.
Configure this :term:`entry point` by adding the following lines to
(the :code:`[project]` section of) the
:code:`pyramid_scaffold/pyproject.toml` file:

.. literalinclude:: yaml_and_json_configs/pyproject.toml
   :language: toml
   :lines: 48-49

Create the YAML configuration files
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Create the :code:`development.yaml` and :code:`production.yaml`
configuration files in the :code:`pyramid_scaffold` directory.

The :code:`development.yaml` file:

.. development.yaml
.. literalinclude:: yaml_and_json_configs/config.yaml
   :language: yaml
   :lines: 1, 3-8, 10-22, 31-32, 37-
   :emphasize-lines: 22

The :code:`production.yaml` file:

.. production.yaml
.. literalinclude:: yaml_and_json_configs/config.yaml
   :language: yaml
   :lines: 2-8, 10, 23-32, 37-
   :emphasize-lines: 18

Add the YAML configuration files to :code:`MANIFEST.in`
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

In the :code:`MANIFEST.in` file, change the line reading::

  include *.txt *.ini *.cfg *.rst *.toml

to read::

  include *.txt *.ini *.cfg *.rst *.toml *.yaml

With this change the YAML configuration files become a part of your
packaged application.

.. 
.. Included section: "Build the package"
.. 
.. include:: yaml_and_json_configs/build.rst


Install and run the packaged application
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

(This is a "check step".)

Check that the package works by installing and running it with:

.. code-block:: shell

   cd pyramid_scaffold
   ../appenv/bin/pip install dist/pyramid_scaffold-0.0.tar.gz
   ../appenv/bin/pserve production.yaml

Access the application in your web browser by going to:
http://localhost:6543

The application can be stopped by holding down the "Ctrl" key and
pressing the "C" key.

You can also check that the package continues to work with the
:code:`development.ini` file with:

.. code-block:: shell

   cd pyramid_scaffold
   ../appenv/bin/pserve development.ini

      
Step 5: Configure the packaging to support JSON configuration files
-------------------------------------------------------------------

Create the JSON configuration files
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

JSON does not allow comments.
Remove them when creating the JSON configuration files.

.. code-block:: shell

   cd pyramid_scaffold
   sed '/^ *#/d' < production.yaml > production.json
   sed '/^ *#/d' < development.yaml > development.json

"Register" the :code:`plaster-yaml` plugin as a JSON configuration file loader
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The project's packaging must be changed before the
:code:`plaster-yaml` plugin will load JSON configuration files.

A new :term:`entry point` is needed to "register" the ":code:`.json`"
file extension, to associate the extension with a configuration file loader
supporting JSON content.
Configure this :term:`entry point` by adding the following line to
:code:`[project.entry-points.'plaster.loader_factory']` section of the
:code:`pyramid_scaffold/pyproject.toml` file.

.. literalinclude:: yaml_and_json_configs/pyproject.toml
   :language: toml
   :lines: 50

The section should now look like:

.. literalinclude:: yaml_and_json_configs/pyproject.toml
   :language: toml
   :lines: 48-50
   :emphasize-lines: 3

Add the JSON configuration files to :code:`MANIFEST.in`
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

In the :code:`MANIFEST.in` file, change the line reading::

  include *.txt *.ini *.cfg *.rst *.toml *.yaml

to read::

  include *.txt *.ini *.cfg *.rst *.toml *.yaml *.json

With this change the JSON configuration files become a part of your
packaged application.

.. 
.. Included section: "Build the package"
.. 
.. include:: yaml_and_json_configs/build.rst

Install and run the packaged application
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

(This is a "check step".)

Check that the package works by installing and running it with:

.. code-block:: shell

   cd pyramid_scaffold
   ../appenv/bin/pip install dist/pyramid_scaffold-0.0.tar.gz
   ../appenv/bin/pserve production.yaml

Access the application in your web browser by going to:
http://localhost:6543

The application can be stopped by holding down the "Ctrl" key and
pressing the "C" key.

The package will continue to work with :code:`.ini` and YAML
configuration files.
The :code:`plaster-pastedeploy` package handles parsing files with a
:code:`.ini` suffix.
The :code:`plaster-yaml` package, with the 2 :term:`entry point`\ s
configured above, handles parsing files with :code:`.json` or
:code:`.yaml` suffixes.


Appendix: A sample :code:`pyproject.toml` file
----------------------------------------------

This file supports :code:`.ini`, YAML, and JSON configuration files.


.. include:: yaml_and_json_configs/yaml_config_exceptions.rst

Significant lines are highlighted.

The highlighted lines containing ":app:`MYAPP`" must be changed to the
name of your package or your package will either fail to build or
won't work as intended.
(And, of course, the project's description, author, and so forth must
also be changed.
See: the `pyproject.toml specification
<https://packaging.python.org/en/latest/specifications/pyproject-toml/>`_)

The highlighted lines containing ":code:`plaster`" add YAML and JSON
configuration file support: the :code:`plaster-yaml` package is one of
the project's :code:`dependencies`, and there are :term:`entry point`\
s for YAML and JSON file parsing.

A sample :code:`pyproject.toml` file:

.. literalinclude:: yaml_and_json_configs/pyproject.toml
   :language: toml
   :lines: 1-9, 11-44, 46-56, 58-63, 65-
   :emphasize-lines: 9, 29, 46-48, 55, 61


Appendix: Sample YAML configuration files, and their use
--------------------------------------------------------

This appendix contains 2 sample YAML configuration files, one for
development and the other for production.
It also briefly describes how :app:`Pyramid` delivers :term:`settings`
to an application.

.. topic:: Configuration files and settings

   Settings are named values that control the application.
   Configuration files can contain settings, but :app:`Pyramid`
   settings can come from other places as well -- including from
   application startup code.

   It is important to remember that the settings given in a
   configuration file may not tell the whole story when it comes to
   controlling a :app:`Pyramid` application's behavior.

Both example YAML configuration files must be modified before they can
be used.
The highlighted lines, 8 and 17-21, indicate the lines to change.

Line 8 identifies the name (":app:`MYAPP`") of your application's
package.
It *must* be changed to your package's name in order to connect your
application to the WSGI server.

Unlike all other application settings, line 8, the ":code:`use`"
setting, is not passed to your application.
It is for internal use only.

Lines 17-21 are sample settings.
They should be replaced with your application's actual settings.

.. topic:: A :app:`Pyramid` overview of settings and their use

   The narrative documentation's :ref:`project_narr` page has an
   introduction to the topics mentioned in this appendix, and others.
   It contains code samples and concept explainations.
   The page describes :term:`view callable`\ s access to settings, and
   has a section on :app:`Pyramid` configuration and the meaning of
   various settings.

.. index::
   :pair: YAML: application settings

.. _alternate_configs_yaml_application_settings:

Application settings
^^^^^^^^^^^^^^^^^^^^

Nearly the entire YAML ":code:`app`" mapping, lines 7-18, line 8 being
omitted, make up the application :term:`settings` supplied by the
configuration file.
In addition to settings specific to your application, the application
settings includes settings that control :app:`Pyramid` and
related components, like the debug toolbar.
(Commented out in the :code:`cookiecutter` supplied configurations,
the debug toolbar settings are not included in the sample YAML
configuration files given here.)
Your application receives the YAML mapping of all application
settings, those loaded from the configuration file and those supplied
by your application's startup code, as a Python dict.

Line 18 contains an application setting, named
":code:`sample_setting`".

.. topic:: Accessing and manipulating application settings

   Application settings are stored in a dict, itself an attribute of
   your application's :term:`registry <application registry>`.
   The registry becomes part of a web :term:`request`, and is made
   available to your :term:`view callable` code, the code that accepts
   a web request and produces a response for rendering.

   To be specific, the given example :code:`sample_setting`
   application setting's value is available in a :term:`view callable`
   via:

   .. code-block:: python

      request.registry.settings["sample_setting"]

   That is, if the usual coding idiom is used and the :term:`view callable`
   takes a parameter named :code:`request`, as follows:

   .. code-block:: python

      def some_view(request):

   During application startup there are at least 2 ways to access, or
   modify and add to, the application settings :app:`Pyramid` loads
   from external files, or possibly other sources.
   The registry is available in a :term:`Configurator` instance's
   :code:`registry` attribute, making the settings dict available as a
   registry attribute, as above.
   And, the settings dict, already loaded with settings from external
   sources by a configuration loader like :code:`plaster-yaml`, is
   passed to the application's :code:`main` function.
   Settings are passed to :code:`main` in a positional parameter
   named :code:`settings`, or that is the parameter name in
   :ref:`typical configuration code <init_py>`.

.. index::
   :pair: YAML: global settings

.. _alternate_configs_yaml_global_settings:
   
Global settings
^^^^^^^^^^^^^^^

The optional :code:`DEFAULT` mapping, lines 20-21, is for global
settings.
Global settings are available to all applications, servers, and
middleware defined in the configuration file.
Global settings are well suited to passing values used only during
application startup.

Line 21 contains a global setting, named
":code:`sample_global_setting`".

.. topic:: Accessing global settings

   The :code:`DEFAULT` mapping is passed, as a dict, to your
   application's :code:`main` function as a positional pararameter
   named :code:`global_config`.
   That is, if the usual coding idiom is used and :code:`main` takes
   a parameter named :code:`global_config`, as in :ref:`typical
   configuration code <init_py>`.

A sample :code:`development.yaml` file
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. literalinclude:: yaml_and_json_configs/config.yaml
   :language: yaml
   :linenos:
   :lines: 1, 3-9, 11-19, 33-
   :emphasize-lines: 8, 17-21

A sample :code:`production.yaml` file
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. literalinclude:: yaml_and_json_configs/config.yaml
   :language: yaml
   :linenos:
   :lines: 2-9, 23-31, 33-
   :emphasize-lines: 8, 17-21
