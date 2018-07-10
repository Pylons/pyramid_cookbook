uWSGI
+++++

This brief chapter covers how to configure a `uWSGI <https://uwsgi-docs.readthedocs.io/en/latest/>`_ server for Pyramid.

Pyramid is a Paste-compatible web application framework. As such, you can use the uWSGI ``--paste`` option to conveniently deploy your application.

For example, if you have a virtual environment in ``/opt/env`` containing a Pyramid application called ``wiki`` configured in ``/opt/env/wiki/development.ini``:

.. code-block:: bash

    uwsgi --paste config:/opt/env/wiki/development.ini --socket :3031 -H /opt/env

The example is modified from the `original example for Turbogears <https://uwsgi-docs.readthedocs.io/en/latest/Python.html#paste-support>`_.
