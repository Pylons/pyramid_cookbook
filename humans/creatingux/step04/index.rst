=======================
Step 04: Skeleton Views
=======================

Enough "hello world", now we start working on *Projector*. The UX
person usually has a series of screens they need to prototype,
mapping to a URL structure.

We want to make that process fast and productive.

In this step we mock up the structure of the site map::

  /
  /about.html
  /acme
  /people

...and make a series of URLs that implement these. Along the way,
we make more views and more templates.

Goals
=====

- Introduce UX workflow of "screens" using dummy data

Objectives
==========

- "Default" and "named" views

- More ZPT constructs

Steps
=====

#. ``$ cd ../../creatingux; mkdir step04; cd step04``

#. (Unchanged) Copy the following into ``step04/application.py``:

   .. literalinclude:: application.py
      :linenos:

#. Copy the following into ``step04/views.py``:

   .. literalinclude:: views.py
      :linenos:

#. Copy the following into ``step04/index.pt``:

   .. literalinclude:: index.pt
      :language: html
      :linenos:

#. Copy the following into ``step04/about.pt``:

   .. literalinclude:: about.pt
      :language: html
      :linenos:

#. Copy the following into ``step04/company.pt``:

   .. literalinclude:: company.pt
      :language: html
      :linenos:

#. Copy the following into ``step04/people.pt``:

   .. literalinclude:: people.pt
      :language: html
      :linenos:

#. Copy the following into ``step04/tests.py``:

   .. literalinclude:: tests.py
      :linenos:

#. ``$ nosetests`` should report running 6 tests.

#. ``$ python application.py``

#. Open ``http://127.0.0.1:8080/`` in your browser.


Extra Credit
============

#. What happens if you have two view registrations with no ``@name``
   attribute, meaning both as the default?

#. Is Chameleon (now at version 2) any better at showing you error
   messages? Give it a try, put some errors into your Python expressions.

#. Will the WebTest correctly trigger that error?

#. Does ending your URLs in ``.html`` have any effect?

Analysis
========

We are beginning the process of making a URL space that maps to objects
and a hierarchy in our application. At the moment,
we are simulating this with views.

Although our number of tests went up, each are still very small. Even
such a simple test will still catch most of the silly errors that creep
up during initial development. Hopefully you'll find that running
``nosetests`` is more productive than clickety-click.

Discussion
==========

- How do the registrations happen under the hood?

- Chameleon, caching, and writing compiled versions to disk
