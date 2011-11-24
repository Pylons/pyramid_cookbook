=============================
Step 01: Hello World for ACLs
=============================

Pyramid resources are protected with security statements called *access
control lists* (or ACLs.) This is a familiar security concept,
in which you state::

  [(Action, Principal, Permission),]

...where action is either ``Allow`` or ``Deny``.

Goals
=====

- Associate a security statement with a resource

Objectives
==========

- Put an ACL on the class for the ``SiteFolder``

- Place a permission in the ``@view_config`` for a view

Steps
=====

#. ``$ cd ../../security; mkdir step01; cd step01``

#. (Unchanged) Copy the following into ``step01/application.py``:

   .. literalinclude:: application.py
      :linenos:

#. Copy the following into ``step01/views.py``:

   .. literalinclude:: views.py
      :linenos:

#. Copy the following into ``step01/resources.py``:

   .. literalinclude:: resources.py
      :linenos:

#. Copy the following into ``step01/templates/default_view.pt``:

   .. literalinclude:: templates/default_view.pt
      :language: html
      :linenos:

#. ``$ python application.py``

#. Open ``http://127.0.0.1:8080/`` in your browser. Visit the ``Edit``
   link.

Extra Credit
============

#. What if you put no ACL on ``SiteFolder``? What would be the effect?

#. Do you have to use the imported constants for ``Allow`` and ``Deny``
   or can you just use a string?

#. Do we have to use ACLs? Is there some other way to protect resources?

#. We have a subfolder at ``/folder1/``. Do security statements apply
   to it? (Give it a try in your browser.)

#. But wait...we put the ACL on ``SiteFolder`` not ``Folder``. What's
   going on?

Analysis
========

The ``application.py`` grew an ``authentication_policy`` keyword
argument in the configuration. *That* is the place where you decide
what kind of authentication system to use.

Of course we aren't using this too much until we actually do logins in
the next step.

We are using the default authorization policy, which is the ACL
authorization policy.

Once you turn on security, you get an *implicit ``Deny``*.

Discussion
==========

- How are ACL statements stacked with allow and deny?

- Does Pyramid support hierarchical security, like Zope?