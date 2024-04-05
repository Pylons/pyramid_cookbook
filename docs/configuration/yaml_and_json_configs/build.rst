Build the package
^^^^^^^^^^^^^^^^^

(This is a "check step".)

Test to see if the package builds successfully by running:

.. code-block::

   cd pyramid_scaffold
   rm -f dist/*
   ../devenv/bin/python -m build

The package should build without errors.
The only warnings should be from MANIFEST.in processing, warning that
no files matching particular patterns are found.
The :code:`pyramid_scaffold/dist` directory should contain 2 files: a
source package and a wheel package.
