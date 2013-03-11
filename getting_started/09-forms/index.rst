===================================
9: Forms and Validation With Deform
===================================

Modern web applications deal extensively with forms. Developers,
though, have a wide range of philosophies about how frameworks should
help them with their forms. As such, Pyramid doesn't directly bundle
one particular form library. Instead, there are a variety of form
libraries that are easy to use in Pyramid.

Deform is one such library. In this step, we introduce Deform for our
forms and validation.

Objectives
==========

- Make a schema using Colander, the companion to Deform

- Create a form with Deform and change our views to handle validation

Steps
=====


#. Let's use the previous package as a starting point for a new
   distribution. Also, use ``easy_install`` to install Deform:

   .. code-block:: bash

    (env33)$ cd ..; cp -r step08 step09; cd step09
    (env33)$ easy_install-3.3 deform
    (env33)$ python3.3 setup.py develop

#. Deform has CSS and JS that help make it look pretty. Change the
   ``tutorial/__init__.py`` to add a static view:

   .. literalinclude:: tutorial/__init__.py
    :linenos:

#. To keep our dummy data out of our ``views.py`` (and pave the way for
   a future step that does modeling), let's move ``pages`` to
   ``tutorial/models.py``:

   .. literalinclude:: tutorial/models.py

#. Our ``tutorial/views.py`` has some significant changes. The add and
   edit views handle both GET and POST (form submission),
   we have methods, and most of all, a form schema for WikiPage:

   .. literalinclude:: tutorial/views.py
    :linenos:

#. We don't want to include the Deform JS/CSS in every page so we need
   a "slot" in ``tutorial/templates/layout.pt`` where we can insert
   these static assets:

   .. literalinclude:: tutorial/templates/layout.pt
    :linenos:
    :language: html

#. ``tutorial/templates/wikipage_addedit.pt`` needs to iterate over the
   resources and insert them in the slot we just made,
   as well as insert the rendered form:

    .. literalinclude:: tutorial/templates/wikipage_addedit.pt
        :linenos:
        :language:  html

#. Run the tests in your package using ``nose``:

   .. code-block:: bash

    (env33)$ nosetests .
    ..
    -----------------------------------------------------------------
    Ran 2 tests in 1.971s

    OK

#. Run the WSGI application:

   .. code-block:: bash

    (env33)$ pserve development.ini --reload

#. Open ``http://127.0.0.1:6547/`` in your browser.

Analysis
========

- Package spec for Deform add_static_view?

Extra Credit
============

- Can I provide a one-liner for including static assets in my Pyramid
  libraries?
