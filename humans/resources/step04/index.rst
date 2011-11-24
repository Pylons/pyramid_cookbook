===============================
Step 04: Creating Basic Content
===============================

We are still in our simple content types (``SiteFolder``, ``Folder``,
and ``Document``.) We haven't yet switched back to ``Projector``.

Before we do, though, let's have the ability to add content. That is,
folders allow adding subfolders or documents.

Goals
=====

- Arbitrarily nested content

Objectives
==========

- Simple form which POSTs data

- A view which takes the POST data, creates a resource, and redirects
  to the newly-added resource

Steps
=====

#. ``$ cd ../../resources; mkdir step04; cd step04``

#. (Unchanged) Copy the following into ``step04/application.py``:

   .. literalinclude:: application.py
      :linenos:

#. Copy the following into ``step04/views.py``:

   .. literalinclude:: views.py
      :linenos:

#. (Unchanged) Copy the following into ``step04/resources.py``:

   .. literalinclude:: resources.py
      :linenos:

#. Copy the following into ``step04/templates/document_view.pt``:

   .. literalinclude:: templates/document_view.pt
      :language: html
      :linenos:

#. Copy the following into ``step04/templates/folder_view.pt``:

   .. literalinclude:: templates/folder_view.pt
      :language: html
      :linenos:

#. Copy the following into ``step04/templates/site_view.pt``:

   .. literalinclude:: templates/site_view.pt
      :language: html
      :linenos:

#. Copy the following into ``step04/tests.py``:

   .. literalinclude:: tests.py
      :linenos:

#. ``$ nosetests`` should report running 4 tests.

#. ``$ python application.py``

#. Open ``http://127.0.0.1:8080/`` in your browser.

Extra Credit
============

#. Can ``document_view`` simply return nothing instead of an empty
   dictionary?

#. Here's a hard one...try eliminating the add views by turning
   ``folder_view`` into a self-posting form.

Analysis
========

To enforce uniqueness, we randomly choose a satisfactorily large number.

Discussion
==========

- Different strategies for handling uniqueness in a container

- Concept of a content "factory" as expressed in past systems
