Forms
%%%%%

Pyramid does not include a form library because there are several good ones on
PyPI, but none that is obviously better than the others.

Deform_ is a form library written for Pyramid, and maintained by the Pylons
Project.  It has a `demo <https://github.com/Pylons/deform>`_.

You can use WebHelpers and FormEncode in Pyramid just like in Pylons.  Use
pyramid_simpleform_ to organize your view code.  (This replaces Pylons'
@validate decorator, which has no equivalent in Pyramid.) FormEncode's
documentation is a bit obtuse and sparse, but it's so widely flexible that you
can do things in FormEncode that you can't in other libraries, and you can also
use it for non-HTML validation; e.g., to validate the settings in the INI file.

Some Pyramid users have had luck with WTForms, Formish, ToscaWidgets, etc.

There are also form packages tied to database records, most notably
FormAlchemy. These will publish a form to add/modify/delete records of a
certain ORM class.


Articles
--------

.. toctree::

   file_uploads


.. include::  ../links.rst
