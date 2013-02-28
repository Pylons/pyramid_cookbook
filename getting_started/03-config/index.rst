=================================
3: Configuration Files and pserve
=================================

Pyramid has a first-class concept of
:ref:`configuration <pyramid:configuration_narr>` distinct from code.
This approach is optional, but its presence makes it distinct from
other Python web frameworks

Goals
=====

- Illustrate a configuration-driven application

Objectives
==========

- Create an application driven by a ``.ini`` file

- Startup the application with Pyramid's ``pserve`` command

- Move code into the package's ``__init__.py``

Steps
=====

#. Let's begin using the previous package as a starting point for a new
   distribution, then making it active:

   .. code-block:: bash

    (env33)$ cd ..; cp -r step02 step03; cd step03
    (env33)$ python3.3 setup.py develop

#. Pyramid can use a .ini-formatted configuration file as its launching
   point. Type the following into ``development.ini`` inside
   ``step3``:

   .. literalinclude:: development.ini
    :linenos:

#. Many Pyramid apps put the logic for setting up the WSGI app into the
   distribution's ``__init__.py``, so enter the following into
   ``tutorial/__init__.py``:

   .. literalinclude:: tutorial/__init__.py
    :linenos:

#. Let's eliminate our ``wikiapp.py``, as its functionality is now
   merged into ``__init__.py``:

   .. code-block:: bash

    (env33)$ rm tutorial/wikiapp.py*

   We do ``.py*`` to ensure we get the byte-compiled ``.pyc`` file.

#. Run the WSGI application with::

    (env33)$ pserve development.ini

#. Open ``http://127.0.0.1:6547/`` in your browser.

Analysis
========

Our ``development.ini`` file is read by ``pserve`` and serves to
bootstrap our application. Processing then proceeds as described in
the Pyramid chapter on
:ref:`application startup <pyramid:startup_chapter>`:

- ``pserve`` looks for ``[app:main]`` and finds ``use = egg:tutorial``

- The package's ``setup.py`` has defined this (lines 9-10) for the
  distribution (egg) as ``tutorial:main``

- The ``tutorial`` distribution's ``__init__`` has a ``main`` function

- This function is invoked, with the values from certain ``.ini``
  sections passed in

The ``.ini`` file is also used for two other functions:

- ``[server:main]]`` wires up the choice of WSGI *server* fro your WSGI
  *application*

- Pyramid uses Python standard logging, which needs a number of
  configuration values. The ``.ini`` serves this function

In this case, ``pserve`` finds the server
defined by ``[server:main]`` and the application defined by
``[app:main]``. The latter's ``use = egg:tutorial`` governs

The code from ``wikiapp.py`` that launched our application not only
was moved to ``__init__.py``...it also got shorter,
as it didn't need to wire up a WSGI server.

Extra Credit
============

- Is it possible to develop your application separately from the
  configuration? Is that a good idea?

- Can you have more than one ``.ini`` file for an application?

- If you don't like configuration and/or ``.ini`` files,
  could you do this yourself in Python code?

