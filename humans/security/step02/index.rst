=========================
Step 02: Login and Logout
=========================

Our first step introduced security ACL statements on our site root. In
this next example, we add the ability to log in and log out.

Goals
=====

- Allow users (in groups) to access protected stuff

- Custom login forms

Objectives
==========

- When the system generates forbidden error (via an ACL) you are
  redirected to login

- A login leads to an authenticated user who might have some groups

- Logout clears the "ticket" for the login

Steps
=====

#. ``$ cd ../../security; mkdir step02; cd step02``

#. Copy the following into ``step02/application.py``:

   .. literalinclude:: application.py
      :linenos:

#. Copy the following into ``step02/views.py``:

   .. literalinclude:: views.py
      :linenos:

#. Copy the following into ``step02/resources.py``:

   .. literalinclude:: resources.py
      :linenos:

#. Copy the following into ``step02/usersdb.py``:

   .. literalinclude:: usersdb.py
      :linenos:

#. Copy the following into ``step02/templates/default_view.pt``:

   .. literalinclude:: templates/default_view.pt
      :language: html
      :linenos:

#. Copy the following into ``step02/templates/login.pt``:

   .. literalinclude:: templates/login.pt
      :language: html
      :linenos:

#. ``$ python application.py``

#. Open ``http://127.0.0.1:8080/`` in your browser.

Extra Credit
============

#. Change ``Document`` to be editable by the world.

#. Make your ``doc2`` document which, only for that resource instance,
   is editable by the world.

#. Can you make a view that that catches some other exception besides
   ``HTTPForbidden``? For example, Not Found.

#. We show an edit link even if the person doesn't have permission to
   edit. How can you make that conditional in the ZPT?

Analysis
========

The login view has two decorators that are "stacked". One makes sure
that the login view gets shown when your URL is "/login.html". (Normal
stuff.)

The second ``@view_config`` has a context of ``HTTPForbidden``. This is
invoked when *Pyramid raises the exception*.

We redirect back to where you came from when logging in,
which is a common pattern.

Discussion
==========

- Of course this isn't using *your* user database.

- What are all the hand-wavey plug points for all the misery involved
  in web framework authentication?
