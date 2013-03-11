===============
7: View Classes
===============

Free-standing functions are the regular way to do views. Many times,
though, you have several views that are closely related. For example,
a wiki might have many different ways to look at it (home page, add,
view, edit, delete, table of contents, etc.)

For some people, grouping these together makes logical sense. A view
class lets you group these views, sharing some state assignments and
helper functions as class methods.

Objectives
==========

- Introduce a view class for our wiki-related views

- Start making this more like Wiki by adding more views and templates

Steps
=====

#. Let's again use the previous package as a starting point for a new
   distribution:

   .. code-block:: bash

    (env33)$ cd ..; cp -r step06 step07; cd step07
    (env33)$ python3.3 setup.py develop

#. Edit ``tutorial/views.py`` to include a view class with several more
   views, along with a "layout" template:

   .. literalinclude:: tutorial/views.py
    :linenos:

#. Since we have new views, our ``__init__.py`` needs new routes:

    .. literalinclude:: tutorial/__init__.py
        :linenos:

#. Now we make some new templates. First,
   ``tutorial/templates/layout.pt``:

    .. literalinclude:: tutorial/templates/layout.pt
        :linenos:
        :language: html

#. Next, ``tutorial/templates/wiki_view.pt``:

    .. literalinclude:: tutorial/templates/wiki_view.pt
        :linenos:
        :language: html

#. Next, ``tutorial/templates/wikipage_addedit.pt``:

    .. literalinclude:: tutorial/templates/wikipage_addedit.pt
        :linenos:
        :language: html

#. Finally, ``tutorial/templates/wikipage_view.pt``:

    .. literalinclude:: tutorial/templates/wikipage_view.pt
        :linenos:
        :language: html

#. Since we have more views, we need more tests in
   ``tutorial/tests.py``:

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



- view defaults

- route with an id

- layout template

- HTTPFound

Extra Credit
============

