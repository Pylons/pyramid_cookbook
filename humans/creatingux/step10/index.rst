==================================
Step 10: Re-usable Template Macros
==================================

In :doc:`../step05/index` we made a main template that was used for all
screens in the site. We used ZPT machinery as the solution.

Sometimes, though, it isn't a global look and feel that needs re-use. 
It is a little snippet that is common to some of the pages, 
but not all. Or perhaps, a block that looks different on some screens 
versus others.

ZPT macros are the solution here.

Goals
=====

- Share small snippets of code between view templates

Objectives
==========

- Make a ZPT template file with some re-usable macros

- Associate that template file with the layouts

- Provide any logic needed in the snippet

Steps
=====

#. ``$ cd ../../creatingux; mkdir step10; cd step10``

#. Copy the following into ``step10/application.py``:

   .. literalinclude:: application.py
      :linenos:

#. ``$ mkdir static``

#. Copy the following into ``step10/static/global_layout.css``:

   .. literalinclude:: static/global_layout.css
      :language: css
      :linenos:

#. Copy the following into ``step10/static/global_layout.js``:

   .. literalinclude:: static/global_layout.js
      :language: js
      :linenos:

#. Copy the following into ``step10/views.py``:

   .. literalinclude:: views.py
      :linenos:

#. Copy the following into ``step10/layouts.py``:

   .. literalinclude:: layouts.py
      :linenos:

#. Copy the following into ``step10/dummy_data.py``:

   .. literalinclude:: dummy_data.py
      :linenos:

#. Copy the following "global template" into
   ``step10/templates/global_layout.pt``:

   .. literalinclude:: templates/global_layout.pt
      :language: html
      :linenos:

#. Copy the following "macros template" into
   ``step10/templates/macros.pt``:

   .. literalinclude:: templates/macros.pt
      :language: xml
      :linenos:

#. Copy the following into ``step10/templates/index.pt``:

   .. literalinclude:: templates/index.pt
      :language: html
      :linenos:

#. Copy the following into ``step10/templates/about.pt``:

   .. literalinclude:: templates/about.pt
      :language: html
      :linenos:

#. Copy the following into ``step10/templates/company.pt``:

   .. literalinclude:: templates/company.pt
      :language: html
      :linenos:

#. Copy the following into ``step10/templates/people.pt``:

   .. literalinclude:: templates/people.pt
      :language: html
      :linenos:

#. Copy the following into ``step10/test_views.py``:

   .. literalinclude:: test_views.py
      :linenos:

#. Copy the following into ``step10/test_layout.py``:

   .. literalinclude:: test_layout.py
      :linenos:

#. ``$ nosetests`` should report running 10 tests.

#. ``$ python application.py``

#. Open ``http://127.0.0.1:8080/`` in your browser and look at the
   ``ACME, Inc.`` link to see the projects menu.


Extra Credit
============

#. Could you generate the macro from a string of HTML in the Python code?

#. Have a conditional selection of which macros are used,
   where the choice is made on the Python side.

#. Move the ``projects`` from being provided by each view,
   into the view class.  Then, move it to the layout.

Analysis
========

Macros are a long-standing feature in the world of Zope, and as such,
are a mature and well-understood way to decompose UX into re-usable
snippets.

The indirections in Zope (2, 3, CMF, Plone), though,
has made "Where did that pixel come from?" into a crazy adventure. But
if you remove the pluggability, macros become a less mysterious and
more useful tool.

Discussion
==========

- Where is the right place to put stuff like ``projects``? That is,
  data that is needed in a macro. Each view, each view class,
  the "Template API" (aka layout)?

- Are macros performant in Chameleon?

- With all this decomposition, has the original idea of ZPT (the
  Dreamweaver person can co-own the artifact) been made inoperative?
