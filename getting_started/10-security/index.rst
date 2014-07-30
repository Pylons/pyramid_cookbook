==================================================
10: Security With Authentication and Authorization
==================================================

Our application has URLs that allow people to add/edit/delete content
via a web browser. Time to add security to the application. Let's
protect our add/edit/delete views to require a login (username of
``editor`` and password of ``editor``.) We will allow the other views
to continue working without a password.

Objectives
==========

- Introduce the Pyramid concepts of authentication, authorization,
  permissions, and access control lists (ACLs)

- Create login/logout views

Steps
=====

#. Copy the results from the previous step:

   .. code-block:: bash

    (env33)$ cd ..; cp -r step09 step10; cd step10
    (env33)$ python3.3 setup.py develop

#. Update ``tutorial/models.py`` to include statements from Pyramid's
   declarative security features:

   .. literalinclude:: tutorial/models.py
    :linenos:

#. Our ``__init__.py`` needs this root factory, our
   authentication/authorization policies, and routes to login/logout:

   .. literalinclude:: tutorial/__init__.py
    :linenos:

#. Create a ``tutorial/security.py`` module that can find our user
   information by providing an *authentication policy callback*:

   .. literalinclude:: tutorial/security.py
    :linenos:

#. Our ``tutorial/views.py`` needs some changes: permissions on the
   add/edit/delete views, new views for login/logout,
   and a way to track whether a user is ``logged_in``:

   .. literalinclude:: tutorial/views.py
    :linenos:

#. We have a login view that needs a template at
   ``tutorial/templates/login.pt``:

   .. literalinclude:: tutorial/templates/login.pt
    :linenos:
    :language: html

#. ``tutorial/templates/layout.pt`` needs a conditional link to appear
   on all pages, for either logging in or logging out:

   .. literalinclude:: tutorial/templates/layout.pt
    :linenos:
    :language: html

#. Let's style that link by adding a float to
   ``tutorial/static/wiki.css``:

   .. literalinclude:: tutorial/static/wiki.css
    :language: css

#. Finally, we need to change our functional tests, as requests to
   add/edit/delete get redirected to the login screen:

   .. literalinclude:: tutorial/tests.py
    :linenos:

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

Unlike many web frameworks, Pyramid includes a built-in (but optional)
security model for authentication and authorization. This security
system is intended to be flexible and support many needs.

This simple tutorial step can be boiled down to the following:

- A view can require a *permission* (``edit``)

- The context for our view (the ``Root``) has an access control list
  (ACL)

- This ACL says that the ``edit`` permission is available on ``Root``
  to the ``group:editors`` *principal*

- The registered ``groupfinder`` answers whether a particular user
  (``editor``) has a particular group (``group:editors``)

In summary: ``wikipage_add`` wants ``edit`` permission, ``Root`` says
``group:editors`` has ``edit`` permission.

Of course, this only applies on ``Root``. Some other part of the site
(a.k.a. *context*) might have a different ACL.

If you are not logged in and click on ``Add WikiPage``, you need to get
sent to a login screen. How does Pyramid know what is the login page to
use? We explicitly told Pyramid that the ``login`` view should be used
by decorating the view with ``@forbidden_view_config``.

Extra Credit
============

#. Can I use a database behind my ``groupfinder`` to look up principals?

#. Do I have to put a ``renderer`` in my ``@forbidden_view_config``
   decorator?

#. Once I am logged in, does any user-centric information get jammed
   onto each request? Use ``import pdb; pdb.set_trace()`` to answer
   this.
