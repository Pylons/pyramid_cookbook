============================
5: Unit and Functional Tests
============================

Test coverage is a badge of honor for Pyramid, which has 100% test (and
documentation) coverage from its inception. Equally,
Pyramid wants to help Pyramid developers be productive in writing tests
for their code, providing facilities to promote this.

Pyramid has a first-class concept of
:ref:`configuration <pyramid:configuration_narr>` distinct from code.
This approach is optional, but its presence makes it distinct from
other Python web frameworks.

Sure, testing helps ensure future quality and facilitate refactoring.
But it also makes up-front development faster, particularly in smart
editors and IDEs. Restarting your app and clicky-clicking in your
browser is a drag.

Goals
=====

- Provide both :ref:`unit <pyramid:testing_chapter>` and
  :ref:`functional <pyramid:functional_tests>` tests for our
  Wiki application

Objectives
==========

- Create a new module ``tutorial/tests.py``

- Write unit tests and write functional tests using
  `WebTest <http://webtest.pythonpaste.org/en/latest/>`_

- Run both under the
  `nose <https://nose.readthedocs.org/en/latest/>`_ test runner

Steps
=====

#. Again, let's use the previous package as a starting point for a new
   distribution, then making it active. We will also install ``nose``
   and ``WebTest``:

   .. code-block:: bash

    (env33)$ cd ..; cp -r step03 step05; cd step05
    (env33)$ python3.3 setup.py develop
    (env33)$ easy_install nose webtest

#. Many Pyramid apps put the logic for setting up the WSGI app into the
   distribution's ``__init__.py``, so enter the following into
   ``tutorial/__init__.py``:

   .. literalinclude:: tutorial/tests.py
    :linenos:

#. Now run the tests in your package using ``nose``:

   .. code-block:: bash

    (env33)$ nosetests .
    ..
    -----------------------------------------------------------------
    Ran 2 tests in 1.971s

    OK

Analysis
========

Our unit tests are first. We have on unit test, which simply executes
our view and ensures it returns the proper status code.

Our functional test is second. To run, WebTest needs to be pointed at
the callable that returns our WSGI application. We then execute a web
request at the ``/`` URL and ensure that it returns a body with a
string we are expecting.

Extra Credit
============

#. How does ``nose`` know the tests are in ``tests.py``?

#. Did WebTest really launch an HTTP server and issue an HTTP request?

#. If your code generates an error, will Pyramid handle it gracefully?

Discussion
==========

- Pyramid and the commitment to test coverage

- Philosophies on unit tests vs. integration tests vs.
  functional tests vs. doctests

- The challenge in setup/teardown regarding configuration, registries,
  and machinery under the surface (both the frameworks *and* yours!)
