====================================
Step 02: Unit and Functional Testing
====================================

Sure, testing helps ensure future quality and facilitate refactoring.
But it also makes up-front development faster, particularly in smart
editors and IDEs. Restarting your app and clicky-clicking in your
browser is a drag.

In this step keep the same code as ``step01`` but here we add some tests.

Goals
=====

- Create unit tests on code

- Create functional tests on responses

Objectives
==========

- Write a Pyramid-style unit test

- Use WebTest to include a functional test in the tests module

- Use ``nose`` and the ``nosetests`` test runner to execute tests

Steps
=====

#. ``$ cd ../../creatingux; mkdir step02; cd step02``

   This ensures that you make the next directory in the right location.

#. Copy the following into ``step02/application.py``:

   .. literalinclude:: application.py
      :linenos:

   This is the same module as we saw in ``step01``.

#. Copy the following into ``step02/tests.py``:

   .. literalinclude:: tests.py
      :linenos:

#. ``$ nosetests``

   You should see the following output::

    ..
    --------------------------------------------------------
    Ran 2 tests in 0.301s

    OK


Extra Credit
============

#. How does ``nose`` know the tests are in ``tests.py``?

#. Did WebTest really launch an HTTP server and issue an HTTP request?

#. If your code generates an error, will Pyramid handle it gracefully?

Analysis
========

Unit tests are hard. Unit tests with a framework is even harder.
The culture of Pyramid, though, is dedicated to full test coverage,
and thus Pyramid works very hard to make test writing a productive
experience.

Even if you don't provide full test coverage, you will find that the
most basic unit test will catch obvious errors quicker than re-clicking
in your browser on every change. This is somewhat similar to setting
up your editor or IDE to run ``pylint`` to let you know,
before saving (much less before executing) if you have a bogus variable.

Functional tests are even easier to write, and for UX people,
help on the part of the problem that is the focus.

Discussion
==========

- Pyramid (and repoze.bfg before it) and the commitment to test coverage

- Philosophies on unit tests vs. functional tests vs. doctests

- The challenge in setup/teardown regarding configuration, registries,
  and machinery under the surface (both the frameworks *and* yours!)
