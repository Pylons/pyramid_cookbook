============================
Step 03: Type-Specific Views
============================

In :doc:`../step03/index` we had 3 "content types" (SiteFolder, Folder,
and Document.) All, however, used the same view and template.

Pyramid traversal though lets you bind a view to a particular content
type.

Goals
=====

- Type-specific views by registering a view against a class

Objectives
==========

- ``@view_config`` which uses the ``context`` attribute to associate a
  particular view with ``context`` instances of a particular class

- Views and templates which are unique to a particular class (aka type)

- Patterns in test writing to handle multiple kinds of contexts

Steps
=====

#. ``$ cd ../../resources; mkdir step03; cd step03``

#. (Unchanged) Copy the following into ``step03/application.py``:

   .. literalinclude:: application.py
      :linenos:

#. Copy the following into ``step03/views.py``:

   .. literalinclude:: views.py
      :linenos:

#. (Unchanged) Copy the following into ``step03/resources.py``:

   .. literalinclude:: resources.py
      :linenos:

#. Copy the following into ``step03/templates/document_view.pt``:

   .. literalinclude:: templates/document_view.pt
      :language: html
      :linenos:

#. Copy the following into ``step03/templates/folder_view.pt``:

   .. literalinclude:: templates/folder_view.pt
      :language: html
      :linenos:

#. Copy the following into ``step03/templates/site_view.pt``:

   .. literalinclude:: templates/site_view.pt
      :language: html
      :linenos:

#. Copy the following into ``step03/tests.py``:

   .. literalinclude:: tests.py
      :linenos:

#. ``$ nosetests`` should report running 4 tests.

#. ``$ python application.py``

#. Open ``http://127.0.0.1:8080/`` in your browser.


Extra Credit
============

#. In Zope, *interfaces* were used to register a view. How do you do
   register a Pyramid view against instances that support a particular
   interface?

#. Can Pyramid accept view registrations against a superclass?

#. Can you associate a view with multiple classes?

Analysis
========

Our container views now calculate the list of children and pass into
the template, letting us navigate to children.

The tests now need more ceremony to mock up some dummy values,
then test against them.

Discussion
==========

- Should you calculate the list of children on the Python side,
  or access it on the template side by operating on the context?

- In what cases are interfaces a better binding mechanism?

- Are there times when you want different traversal policies that
  Pyramid's default traverser?
