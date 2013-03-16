==============================================
2: Packaging for the Wiki Tutorial Application
==============================================

Most modern Python development is done using Python packages,
an approach Pyramid puts to good use. In this step, we start writing our
Wiki application as a standard Python package.

Objectives
==========

- Get a minimum Python package in place by making a ``setup.py``

- Get our basic directory structure in place

- Install our ``tutorial`` package

Steps
=====

#. Use the previous step as the basis for this step:

   .. code-block:: bash

    (env33)$ cd ..; mkdir step02; cd step02

#. In ``setup.py``, enter the following:

    .. literalinclude:: setup.py
        :linenos:

#. Make the new package installed for development then make a directory
   for the actual code:

   .. code-block:: bash

    (env33)$ python3.3 setup.py develop
    (env33)$ mkdir tutorial

#. Enter the following into ``tutorial/__init__.py``:

    .. literalinclude:: tutorial/__init__.py

#. Enter the following into ``tutorial/wikiapp.py``:

    .. literalinclude:: tutorial/wikiapp.py

#. Enter the following into ``tutorial/views.py``:

    .. literalinclude:: tutorial/views.py

#. Run the WSGI application with:

   .. code-block:: bash

    (env33)$ python3.3 tutorial/wikiapp.py

#. Open ``http://127.0.0.1:6547/`` in your browser.

Analysis
========

In this case we have a Python package called ``tutorial``. We use the
same name in each step of the Wiki tutorial, to avoid unnecessary
re-typing.

We moved our views out to a second file ``views.py``. We then told the
``Configurator`` to go scan for anything that looks like a
configuration instruction, such as the ``@view_config`` decorator.

Extra Credit
============

#. Why do we make an extra hop in the directory with ``tutorial``?

#. Could we have eliminated ``wikiapp.py`` and put the WSGI
   application startup in ``__init__.py``? How would that have affected
   the command used to start the application?

#. The previous example used ``config.add_view``. This example uses a
   ``@view_config`` decorator. Does Pyramid treat the imperative
   (``add_view``) configuration differently than the declarative
   (``@view_config``) approach?
