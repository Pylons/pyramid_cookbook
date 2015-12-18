======================
4: Type-Specific Views
======================

Type-specific views by registering a view against a class.

Background
==========

In :doc:`hierarchy` we had 3 "content types" (SiteFolder, Folder, and
Document.) All, however, used the same view and template.

Pyramid traversal lets you bind a view to a particular content type. This
ability to make your URLs "object oriented" is one of the distinguishing
features of traversal, and makes crafting a URL space more natural. Once
Pyramid finds the :term:`context` object in the URL path, developers have a lot
of flexibility in view predicates.

Objectives
==========

- Use a decorator ``@view_config`` which uses the ``context`` attribute to
  associate a particular view with ``context`` instances of a particular class.

- Create views and templates which are unique to a particular class (a.k.a.,
  type).

- Learn patterns in test writing to handle multiple kinds of contexts.

Steps
=====

#. We are going to use the previous step as our starting point:

   .. code-block:: bash

    $ cd ..; cp -r hierarchy typeviews; cd typeviews
    $ $VENV/bin/python setup.py develop

#. Our views in ``typeviews/tutorial/views.py`` need type-specific
   registrations:

   .. literalinclude:: typeviews/tutorial/views.py
      :linenos:
      :emphasize-lines: 4-9,17-20,23-33

#. We have a new contents subtemplate at
   ``typeviews/tutorial/templates/contents.jinja2``:

   .. literalinclude:: typeviews/tutorial/templates/contents.jinja2
      :language: jinja
      :linenos:

#. Make a template for viewing the root at
   ``typeviews/tutorial/templates/root.jinja2``:

   .. literalinclude:: typeviews/tutorial/templates/root.jinja2
      :language: jinja
      :linenos:

#. Now make a template for viewing folders at
   ``typeviews/tutorial/templates/folder.jinja2``:

   .. literalinclude:: typeviews/tutorial/templates/folder.jinja2
      :language: jinja
      :linenos:

#. Finally make a template for viewing documents at
   ``typeviews/tutorial/templates/document.jinja2``:

   .. literalinclude:: typeviews/tutorial/templates/document.jinja2
      :language: jinja
      :linenos:

#. More tests are needed in ``typeviews/tutorial/tests.py``:

   .. literalinclude:: typeviews/tutorial/tests.py
      :linenos:
      :emphasize-lines: 8,12-33,43-

#. ``$ $VENV/bin/nosetests`` should report running 4 tests.

#. Run your Pyramid application with:

   .. code-block:: bash

    $ $VENV/bin/pserve development.ini --reload

#. Open http://localhost:6543/ in your browser.

Analysis
========

For the most significant change, our ``@view_config`` now matches on a
``context`` view predicate. We can say "use this view when looking at *this*
kind of thing." The concept of a route as an intermediary step between URLs and
views has been eliminated.

Extra Credit
============

#. Should you calculate the list of children on the Python side, or access it
   on the template side by operating on the context?

#. What if you need different traversal policies?

#. In Zope, *interfaces* were used to register a view. How do you register a
   Pyramid view against instances that support a particular interface? When
   should you?

#. Let's say you need a more specific view to be used on a particular instance
   of a class, letting a more general view cover all other instances. What are
   some of your options?

.. seealso::
   :ref:`Traversal Details <pyramid:traversal_chapter>`
   :ref:`Hybrid Traversal and URL Dispatch <pyramid:hybrid_chapter>`
