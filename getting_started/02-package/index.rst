==============================================
2: Packaging for the Wiki Tutorial Application
==============================================

Most modern Python development is done using Python packages. Pyramid
puts packages to good use. In this step, we start writing our Wiki
application as a standard Python package.

Goals
=====

- Get a minimum Python package in place

- Start writing a Wiki application as our tutorial

Objectives
==========

- Make a ``setup.py``

- Get our basic directory structure in place

- Install our ``tutorial`` package

Steps
=====

#. ``(env33)$ cd ..; mkdir step02; cd step02``

#. In ``setup.py``, enter the following:

    .. literalinclude:: setup.py
        :linenos:

#. ``(env33)$ python3.3 setup.py develop``

#. ``mkdir tutorial``

#. Enter the following into ``tutorial/__init__.py``:

    .. literalinclude:: tutorial/__init__.py

#. Enter the following into ``tutorial/helloworld.py``:

    .. literalinclude:: tutorial/helloworld.py

#. Enter the following into ``tutorial/views.py``:

    .. literalinclude:: tutorial/views.py

#. Run the WSGI application with::

    (env33)$ python3.3 tutorial/helloworld.py

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

#. Could we have eliminated ``helloworld.py`` and put the WSGI
   application startup in ``__init__.py``? How would that have affected
   the command used to start the application?

#. The previous example used ``config.add_view``. This example uses a
   ``@view_config`` decorator. Does Pyramid treat the imperative
   (``add_view``) configuration differently than the declarative
   (``@view_config``) approach?

Discussion
==========

- Pyramid's philosophy of configuration
