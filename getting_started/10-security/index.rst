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

- change models.py: root factory
- change __init__.py: auth policies
-


#. Again, let's use the previous package as a starting point for a new
   distribution. Also, make a directory for the templates:

   .. code-block:: bash

    (env33)$ cd ..; cp -r step04 step05; cd step05
    (env33)$ python3.3 setup.py develop
    (env33)$ mkdir tutorial/templates

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

