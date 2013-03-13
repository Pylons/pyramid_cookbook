===============
7: View Classes
===============

Free-standing functions are the simple way to do views. Many times,
though, you have several views that are closely related. For example,
a wiki might have many different ways to look at it (home page, add,
view, edit, delete, table of contents, etc.)

For some people, grouping these together makes logical sense. A view
class lets you group these views, sharing some state assignments and
helper functions as class methods.

Objectives
==========

- Introduce a view class for our wiki-related views

- Start making this more like our wiki application by adding more
  views and templates

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

Our ``_init__`` shows us a new feature we are using with our
``add_route`` configurations: *named parameters*. These variables,
indicated with curly braces, later become available on
``request.matchdict``.

We are adding multiple views to our site now. Rather than repeat the
same stuff in ``<head>`` and the other "chrome" common to all
templates, we make a master template available in the view class as
``layout``. Attributes and methods of the view class instance are
available inside the template from the ``view`` variable,
as we saw with ``view.layout``.

The master template defines slots that can be filled by the view
templates. Our ``layout.pt`` used ``metal:define-slot="content"`` to
make one such slot. Each view template filled this with
``metal:fill-slot="content"``.

Our ``wikipage_delete`` returns an ``HTTPFound``. This is Pyramid's way
of issuing a redirect.

In our unit tests we have to add an extra step to create an instance of
the view class, and then call the view being tested.

Extra Credit
============

#. If we wanted to make a set of statements to several views in a view
   class at once, how would we do that?

#. Can I put multiple named parameters in my routes?