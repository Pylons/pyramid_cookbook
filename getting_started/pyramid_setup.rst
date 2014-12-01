=============
Pyramid Setup
=============

Installing Pyramid is easy and normal from a Python packaging
perspective. Again, *make sure* you have your virtual environment first
in your path using ``source bin/activate``.

.. code-block:: bash

  (env33)$ easy_install-3.3 pyramid
  ....chuggalugga...
  (env33)$ which pserve

You now have Pyramid installed. The second command confirms this by
looking for the Pyramid ``pserve`` command that should be in the
``bin`` of your virtual environment.

Installing Everything
=====================

Later parts of the tutorial install more packages. Most likely,
you'd like to go ahead and get all of it now:

.. code-block:: bash

  (env33)$ easy_install-3.3 pyramid nose webtest deform sqlalchemy pyramid_chameleon pyramid_tm zope.sqlalchemy
