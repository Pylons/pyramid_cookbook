================================
Step 01: Hello World with Deform
================================

Many times you want forms generated for you. If you can live within the
constraints, you gain a lot: slick widgets, automatic layout,
validation, add and edit handling, and even Ajax submission.

Deform is a part of a set of Pylons libraries that break this
functionality into its logically-separate parts:

- Peppercorn for marshalling form data from requests

- Colander for expressing constraints and fields as schemas

- Deform for generating HTML form markup from a Colander schema,
  with built-in widgets and support for custom widgets

In this step we do the smallest possible step with Deform and Colander.

Goals
=====

- Hello world using Deform and Colander

Objectives
==========

- Add a static view for Deform's static resources

- Include those resources (CSS, JS) in the template's ``<head>``

- Define a basic schema

Steps
=====

#. ``easy_install deform``

#. ``$ cd ../../forms_schema; mkdir step01; cd step01``

#. Copy the following into ``step01/application.py``:

   .. literalinclude:: application.py
      :linenos:

#. Copy the following into ``step01/views.py``:

   .. literalinclude:: views.py
      :linenos:

#. Copy the following into ``step01/templates/site_view.pt``:

   .. literalinclude:: templates/site_view.pt
      :language: html
      :linenos:

#. Copy the following into ``step01/tests.py``:

   .. literalinclude:: tests.py
      :linenos:

#. ``$ nosetests`` should report running 2 tests.

#. ``$ python application.py``

#. Open ``http://127.0.0.1:8080/`` in your browser.

Extra Credit
============

#. Read the Colander docs and allow the name field to be optionally
   missing without raising an validation warning.

#. Add an integer field.

Analysis
========

The ``application.py`` added a static view to the configuration for
``deform_static``.

There is no real form hanlding being done. However,
the form does do validation.

Discussion
==========

- Previous attempts at forms, and other form packages comparison and
  contrast

- Reminder: Every choice on form libraries is doomed

- Other ways to "discover" the path to the static views for deform