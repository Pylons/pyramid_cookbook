=================================
Step 03: Hello World in Chameleon
=================================

Most web systems feature template languages for generating HTML. This
lets a UX person focus on the thing they know (markup) and sprinkle in
code, rather than the reverse.

Pyramid doesn't have too much of an opinion on templating languages.
This tutorial does though. We're Chameleon/ZPT folks. So let's do
"hello world" using a page template.

Goals
=====

- Simplest step possible to bring in a template

Objectives
==========

- Move the views out to a separate module

- Change ``application.py`` to scan a module for view declarations

- Illustrate the coolness of renderers and data-oriented views,
  particularly for testing

- Modify tests to be data-oriented

Steps
=====

#. Remember that :doc:`../../setup` said to do
   ``$ export PYRAMID_RELOAD_TEMPLATES=1`` lets you edit templates and
   not have to restart your Pyramid application.

#. ``$ cd ../../creatingux; mkdir step03; cd step03``

#. Copy the following into ``step03/application.py``:

   .. literalinclude:: application.py
      :linenos:

#. Copy the following into ``step03/views.py``:

   .. literalinclude:: views.py
      :linenos:

#. Copy the following into ``step03/hello.pt``:

   .. literalinclude:: hello.pt
      :language: html
      :linenos:

#. Copy the following into ``step03/tests.py``:

   .. literalinclude:: tests.py
      :linenos:

#. ``$ nosetests``

   You should see the following output::

    ..
    ----------------------------------------------------------------
    Ran 2 tests in 0.885s

    OK
    
#. ``$ python application.py``

#. Open ``http://127.0.0.1:8080/`` in your browser.

Extra Credit
============

#. If you edit the template, do you have to restart to see your change?

#. What other values are possible for ``renderer`` on ``@view_config``?

Analysis
========

This step introduces code scanning. There are several different ways to
do configuration in Pyramid: imperative (which we saw in
:doc:`../step01/index`), scanning (common in many modern web frameworks),
and our old friend ZCML.  The choice is mainly one of style,
though there are some sharp edges in some cases.

Note the coolness...all you have to do is return a dictionary in your
view, and your template gets called on the way out the door,
with that data.

Discussion
==========

- The history of configuration in Zope2, Zope3, BFG, then Pyramid

- How things worked before renderers
