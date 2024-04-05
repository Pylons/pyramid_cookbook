The example below is the current Pyramid scaffold's :code:`setup.py`,
translated into TOML, with some exceptions.

The exceptions are:

* The scaffold's :code:`setup.py` adds the content of the
  :code:`CHANGES.txt` file to the readme text.
  The example does not.

* Some of the "empty values" of the setup.py are commented out because
  they generate configuration errors when used as-is.

* The :code:`sqlalchemy` related portions are omitted.
