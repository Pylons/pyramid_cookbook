===================================
9: Forms and Validation With Deform
===================================

Modern web applications deal extensively with forms. Developers,
though, have a wide range of philosophies about how frameworks should
help them with their forms. As such, Pyramid doesn't directly bundle
one particular form library. Instead, there are a variety of form
libraries that are easy to use in Pyramid.

Deform is one such library. In this step, we introduce Deform for our
forms and validation.

Objectives
==========

- Make a schema using Colander, the companion to Deform

- Create a form with Deform and change our views to handle validation

Steps
=====


#. Let's use the previous package as a starting point for a new
   distribution. Also, use ``easy_install`` to install Deform:

   .. code-block:: bash

    (env33)$ cd ..; cp -r step08 step09; cd step09
    (env33)$ easy_install-3.3 deform
    (env33)$ python3.3 setup.py develop

#. Deform has CSS and JS that help make it look pretty. Change the
   ``tutorial/__init__.py`` to add a static view for Deform's static
   assets:

   .. literalinclude:: tutorial/__init__.py
    :linenos:

#. To keep our dummy data out of our ``views.py`` (and pave the way for
   a future step that does modeling), let's move ``pages`` to
   ``tutorial/models.py``:

   .. literalinclude:: tutorial/models.py

#. Our ``tutorial/views.py`` has some significant changes. The add and
   edit views handle both GET and POST (form submission),
   we have methods, and most of all, a form schema for WikiPage:

   .. literalinclude:: tutorial/views.py
    :linenos:

#. We don't want to include the Deform JS/CSS in every page. We thus need
   a "slot" in ``tutorial/templates/layout.pt`` into which we can insert
   these static assets:

   .. literalinclude:: tutorial/templates/layout.pt
    :linenos:
    :language: html

#. ``tutorial/templates/wikipage_addedit.pt`` needs to iterate over the
   resources and insert them in the slot we just made,
   as well as insert the rendered form:

    .. literalinclude:: tutorial/templates/wikipage_addedit.pt
        :linenos:
        :language:  html

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

This step helps illustrate the utility of asset specifications for
static assets. We have an outside package called Deform with static
assets which need to be published. We don't have to know where on disk
it is located. We point at the package, then the path inside the package.

We just need to include a call to ``add_static_view`` to make that
directory available at a URL. For Pyramid-specific pages,
Pyramid provides a facility (``config.include()``) which even makes
that unnecessary for consumers of a package. (Deform is not specific to
Pyramid.)

Our add and edit views use a pattern called *self-posting forms*.
Meaning, the same URL is used to ``GET`` the form as is used to
``POST`` the form. The route, the view, and the template are the same
whether you are walking up to it the first time or you clicked "submit".

Inside the view we do ``if 'submit' in self.request.params:`` to see if
this form was a ``POST`` where the user clicked on a particular button
``<input name="submit">``.

The form controller then follows a typical pattern:

- If you are doing a GET, skip over and just return the form

- If you are doing a POST, validate the form contents

- If the form is invalid, bail out by re-rendering the form with the
  supplied ``POST`` data

- If the validation succeeeded, perform some action and issue a
  redirect via ``HTTPFound``.

We are, in essence, writing our own form controller. Other
Pyramid-based systems, including ``pyramid_deform``, provide a
form-centric view class which automates much of this branching and
routing.

Extra Credit
============

#. Do I have to publish my Deform static assets at the
   ``/deform_static/`` URL path? What happens if I change it? (Give
   this a try by editing ``deform_static`` in ``tutorial/__init__.py``.)

#. Analyze the following and discern what is the intention:

   .. code-block:: python
    :linenos:

    @view_defaults(route_name='wikipage_edit',
                   renderer='templates/wikipage_addedit.pt')
    class WikiPageViews(object):

        def __init__(self, request):
            self.request = request

        @view_config(request_param='form.update')
        def wikipage_update(self):
            # some work
            return dict(title="Form Update")

        @view_config(request_param='form.draft')
        def wikipage_draft(self):
            # some work
            return dict(title="Form Draft")

        @view_config(request_param='form.delete')
        def wikipage_delete(self):
            # some work
            return dict(title="Form Delete")

