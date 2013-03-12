==================================================
10: Security With Authentication and Authorization
==================================================

Our application has URLs that allow people to add/edit/delete content
via a web browser. Time to add security to the application.

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

#. ``tutorial/templats/layout.pt`` needs a conditional link to appear
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


Extra Credit
============

