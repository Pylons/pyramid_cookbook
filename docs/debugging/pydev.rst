Debugging with PyDev
++++++++++++++++++++

``pdb`` is a great tool for debugging python scripts, but it has some
limitations to its usefulness. For example, you must modify your code
to insert breakpoints, and its command line interface can be somewhat obtuse.

Many developers use custom text editors that that allow them to add wrappers
to the basic command line environment, with support for git and other
development tools. In many cases, however, debugging support basically
ends up being simply a wrapper around basic ``pdb`` functionality.

`PyDev <http://pydev.org>`_ is an `Eclipse <http://eclipse.org>`_ plugin
for the Python language, providing an integrated development environment
that includes a built in python interpreter, Git support, integration with
task management, and other useful development functionality.

The PyDev debugger allows you to execute code without modifying the source
to set breakpoints, and has a gui interface that allows you to inspect
and modify internal state.

Lars Vogella has provided a clear `tutorial
<http://www.vogella.com/articles/Python/article.html>`_
on setting up pydev and getting started with the PyDev debugger. Full
documentation on using the PyDev debugger may be found `here
<http://www.pydev.org/manual_adv_debugger.html>`_. You can also debug
programs not running under Eclipse using the `Remote Debugging
<http://www.pydev.org/manual_adv_remote_debugger.html>`_ feature.

PyDev allows you to configure the system to use any python intepreter you
have installed on your machine, and with proper configuration you can support
both 2.x and 3.x syntax.

Configuring PyDev for a virtualenv
----------------------------------

Most of the time you want to be running your code in a virtualenv in order
to be sure that your code is isolated and all the right versions of your
package dependencies are available. You can ``pip install virtualenv`` if
you like, but I recommend `virtualenvwrapper
<https://bitbucket.org/dhellmann/virtualenvwrapper>`_
which eliminates much of the busywork of setting up virtualenvs.

PyDev will look through all the libraries on your ``PYTHONPATH`` to resolve all
your external references, such as imports, etc. So you will want the virtualenv
libraries on your ``PYTHONPATH`` to avoid unnecessary name-resolution problems.

To use PyDev with virtualenv takes some additional configuration that isn't
covered in the above tutorial. Basically, you just need to make sure your
virtualenv libraries are in the ``PYTHONPATH``.

.. note::

   If you have never configured a python interpreter for your workspace,
   you will not be able to create a project without doing so. You should follow
   the steps below to configure python, but you should NOT include any
   virtualenv libraries for it. Then you will be able to create projects using
   this primary python interpreter. After you create your project, you should
   then follow the steps below to configure a new interpreter specifically for
   your project which does include the virtualenv libraries. This way, each
   project can be related to a specific virtualenv without confusion.

First, open the project properties by right clicking over the project name
and selecting *Properties*.

In the Properties dialog, select *PyDev - Interpreter/Grammar*, and make
sure that the project type *Python* is selected. Click on the "Click here
to configure an interpreter not listed" link. The *Preferences* dialog will
come up with *Python Interpreters* page, and your current interpreter
selected. Click on the *New...* button.

Enter a name (e.g. ``pytest_python``) and browse to your virtualenv bin 
directory (e.g. ``~/.virtual_envs/pytest/bin/python``) to select
the python interpreter in that location, then select *OK*.

A dialog will then appear asking you to choose the libraries that should 
be on the ``PYTHONPATH``. Most of the necessary libraries should be automatically
selected. Hit *OK*, and your virtualenv python is now configured.

.. note::

   On the Mac, the system libraries are not selected. Select them all.

You will finally be back on the dialog for configuring your project python
interpreter/grammar. Choose the interpreter you just configured and click
*OK*. You may also choose the grammar level (2.7, 3.0, etc.) at this time.

At this point, formerly unresolved references to libraries installed in your
virtualenv should no longer be called out as errors. (You will have to 
close and reopen any python modules before the new interpreter will take
effect.)

Remember also when using the PyDev console, to choose the interpreter
associated with the project so that references in the console will
be properly resolved.

Running/Debugging Pyramid under Pydev
-------------------------------------

(Thanks to Michael Wilson for much of this - see `Setting up Eclipse
(PyDev) for Pyramid
<http://mikeiz404-terminal.blogspot.com/2012/05/setting-up-eclipse-pydev-for-pyramid.html>`_)

.. note::

   This section assumes you have created a virtualenv with Pyramid installed,
   and have configured your PyDev as above for this virtualenv.
   We further assume you are using ``virtualenvwrapper`` (see above) so that
   ``$WORKON_HOME`` is the location of your ``.virtualenvs`` directory
   and ``proj_venv`` is the name of your virtualenv.
   ``$WORKSPACE`` is the name of the PyDev workspace containing your project
   
   To create a working example, copy the `pyramid tutorial step03 
   <https://pyramid_tutorials.readthedocs.org/en/latest/getting_started/03-config/index.html>`_
   code into $WORKSPACE/tutorial.
   
   After copying the code, cd to ``$WORKSPACE/tutorial`` and run
   ``python setup.py develop``
   
   You should now be ready to setup PyDev to run the tutorial step03 code.

We will set up PyDev to run pserve as part of a run or debug configuration.

First, copy ``pserve.py`` from your virtualenv to a location outside of your
project library path::

	cp $WORKON_HOME/proj_venv/bin/pserve.py $WORKSPACE

.. note::

   IMPORTANT: Do not put this in your project library path!
   
Now we need to have PyDev run this by default. To create a new run
configuration, right click on the project and select
*Run As -> Run Configurations...*. Select *Python Run* as your
configuration type, and click on the new configuration icon. Add your
project name (or browse to it), in this case "tutorial".

Add these values to the *Main* tab::

	Project: RunPyramid
	Main Module: ${workspace_loc}/pserve.py
	
Add these values to the *Arguments* tab::

	Program arguments: ${workspace_loc:tutorial/development.ini} --reload

.. note::

   Do not add ``--reload`` if you are trying to debug with
   Eclipse. It has been reported that this causes problems.
   
   We recommend you create a separate debug configuration
   without the ``--reload``, and instead of checking "Run"
   in the "Display in favorites menu", check "Debug".

On the *Common* tab::

	Uncheck "Launch in background"
	In the box labeled "Display in favorites menu", check "Run"

Hit *Run* (*Debug*) to run (debug) your configuration immediately,
or *Apply* to create the configuration without running it.

You can now run your application at any time by selecting the *Run/Play*
button and selecting the *RunPyramid* command. Similarly, you can
debug your application by selecting the *Debug* button and selecting
the *DebugPyramid* command (or whatever you called it!).

The console should show that the server has started. To verify, open
your browser to 127.0.0.1:6547. You should see the hello world text.

Note that when debugging, breakpoints can be set as with ordinary code,
but they will only be hit when the view containing the breakpoint
is served.

