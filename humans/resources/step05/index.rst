=================================
Step 05: Projector with Resources
=================================

We have now seen how to create fake content in a hierarchy. Let's hook
this up with the UX we finished with in
:doc:`../../creatingux/step10/index`.

In particular, let's make a series of screens that let you add new
people, new companies, new projects, and new folders and documents
inside projects and folders.

Along the way we do a lot of refactoring. Since we are accumulating a
lot of code, we will dial back a bit on the tests.

Goals
=====

- Addable content in a generalized content and view space

- Helper functions which deal with URLs in hierarchies

Objectives
==========

- View methods which can act as self-posting forms

- Helper methods on view classes to act as "factories" to reduce
  repetitive code for making resources

- Helper functions on the layouts (and layout macros) to provide
  consistency, as well as place-neutral lookups

- Eliminate the dummy data

Steps
=====

#. ``$ cd ../../resources; mkdir step05; cd step05``

#. Copy the following into ``step05/application.py``:

   .. literalinclude:: application.py
      :linenos:

#. ``$ mkdir static``

#. Copy the following into ``step05/static/global_layout.css``:

   .. literalinclude:: static/global_layout.css
      :language: css
      :linenos:

#. Copy the following into ``step05/static/global_layout.js``:

   .. literalinclude:: static/global_layout.js
      :language: js
      :linenos:

#. Copy the following into ``step05/views.py``:

   .. literalinclude:: views.py
      :linenos:

#. Copy the following into ``step05/layouts.py``:

   .. literalinclude:: layouts.py
      :linenos:

#. Copy the following into ``step05/resources.py``:

   .. literalinclude:: resources.py
      :linenos:

#. Copy the following into ``step05/templates/global_layout.pt``:

   .. literalinclude:: templates/global_layout.pt
      :language: html
      :linenos:

#. Copy the following into ``step05/templates/macros.pt``:

   .. literalinclude:: templates/macros.pt
      :language: xml
      :linenos:

#. Copy the following into ``step05/templates/company.pt``:

   .. literalinclude:: templates/company.pt
      :language: html
      :linenos:

#. Copy the following into ``step05/templates/document.pt``:

   .. literalinclude:: templates/document.pt
      :language: html
      :linenos:

#. Copy the following into ``step05/templates/folder.pt``:

   .. literalinclude:: templates/folder.pt
      :language: html
      :linenos:

#. Copy the following into ``step05/templates/people.pt``:

   .. literalinclude:: templates/people.pt
      :language: html
      :linenos:

#. Copy the following into ``step05/templates/person.pt``:

   .. literalinclude:: templates/person.pt
      :language: html
      :linenos:

#. Copy the following into ``step05/templates/project.pt``:

   .. literalinclude:: templates/project.pt
      :language: html
      :linenos:

#. Copy the following into ``step05/templates/site.pt``:

   .. literalinclude:: templates/site.pt
      :language: html
      :linenos:

#. Copy the following into ``step05/test_views.py``:

   .. literalinclude:: test_views.py
      :linenos:

#. ``$ nosetests`` should report running 10 tests.

#. ``$ python application.py``

#. Open ``http://127.0.0.1:8080/`` in your browser.


Extra Credit
============

#. We no longer have a ``site_menu`` which omits the `<a>` from the
   current menu. What's a good way to add the functionality back in?

#. When adding something to a container, you have to pass a reference
   to the container, into the object's constructor. Is there a different
   pattern for this? (Hint: ``repoze.folder`` has the different
   pattern .))

#. Add the ability to delete something from a container.

Analysis
========

Our site menu is no longer hard coded. As you add ``Company`` resources
to the ``SiteFolder``, they will automatically appear in the menu.

All of the container views have templates with one or more ``<form>``
nodes in them. These let us quickly add a particular type of resource
to a container. We don't make these into a macro because the name on
submit button guides us to which kind of thing to add.

We are using self-posting forms in the views. That is,
the same view acts both as a GET and a POST handler. If you post data
to the view, we create a resource then redirect back to the GET view,
but with a message to be displayed.

We could have repeated a lot of the boilerplate on content creation in
each view. That means a lot more tests to write. Instead,
we made two "factory" functions. You pass in the class of the resource
you want created. The factory returns the redirect information.

``layouts.py`` gained some helper functions used to look up the
hierarchy. (We put these in the layout because it is needed by the
layout macros.) Walking up to find the site, or walking up to find
which company you are in, are common operations.

Listing items in a container is a repetitive task, so we made a macro
for it so we could use it in various templates.

Discussion
==========

- Getting close to having a framework

- OTOH, this shows that you can just as well write your own framework.
  Remember, you only have to pay for what you eat!
