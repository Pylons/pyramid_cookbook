======================
Step 02: Form Handling
======================

The previous step was the smallest possible step into a Colander schema
and Deform form based on that schema. Let's take another very small
step, but show processing the form.

Goals
=====

- More validation

- Handle form submission

Objectives
==========

- Process the submitted form by detecting a POST

- Show the 3-way code path: GET vs. valid POST vs. invalid POST

- Display the validated values

Steps
=====

#. ``$ cd ../../forms_schema; mkdir step02; cd step02``

#. (Unchanged) Copy the following into ``step02/application.py``:

   .. literalinclude:: application.py
      :linenos:

#. Copy the following into ``step02/views.py``:

   .. literalinclude:: views.py
      :linenos:

#. Copy the following into ``step02/templates/site_view.pt``:

   .. literalinclude:: templates/site_view.pt
      :language: html
      :linenos:

#. Copy the following into ``step02/tests.py``:

   .. literalinclude:: tests.py
      :linenos:

#. ``$ nosetests`` should report running 2 tests.

#. ``$ python application.py``

#. Open ``http://127.0.0.1:8080/`` in your browser.

Extra Credit
============

#. If the form was successfully submitted, display a status message at
   the top of the screen.

Analysis
========

In this step we see the explicit branching in a self-posting form. This
is important: it's useful to have a common pattern to see which code
path goes where, especially on a large project with lots of forms.

In many cases, this self-posting form isn't going to return itself on
success. Instead, it will redirect using
``pyramid.httpexceptions.HTTPFound`` to the newly-created resource.

Discussion
==========

- Impact of a form library on test writing
