=====
Forms
=====

When writing a Substance D application, you are free to use any library
you would like for forms and schemas. This applies both for your retail
views and for the management views that you plug into the SDI.

For the built-in content types and management views,
you will see that Substance D has standardized on :term:`Colander` and
:term:`Deform` (along with ``deform_bootstrap``) for schemas and forms.
Additionally, Substance D defines a :py:class:`substanced.form.FormView`
class, discussed below.

``FormView``
============

Form handling is ground that is frequently covered, usually in different
ways. Substance D provides a class to help implement common patterns in
form handling.

Imagine this example:

.. code-block:: python

    @mgmt_view(
        context=IFolder,
        name='add_document',
        tab_title='Add Document',
        permission='sdi.add-content',
        renderer='substanced.sdi:templates/form.pt',
        tab_condition=False,
    )
    class AddDocumentView(FormView):
        title = 'Add Document'
        schema = DocumentSchema()
        buttons = ('add',)

        def add_success(self, appstruct):
            registry = self.request.registry
            name = appstruct.pop('name')
            document = registry.content.create('Document', **appstruct)
            self.context[name] = document
            return HTTPFound(
                self.request.mgmt_path(self.context, '@@contents'))

This ``mgmt_view`` adds a view ``add_document`` to resources with the
``IFolder`` interface. The form gets a ``title``, a Colander schema,
and asks for just one button.

Since the ``mgmt_view`` is associated with a renderer,
we have an SDI template ``form.pt`` which does the basics of laying out
the rendering before handing the work over to Deform.

The ``@action`` of the form is the ``mgmt_view`` itself,
making it a self-posting form. The button that was clicked causes the
``FormView`` to, upon validation success, route processing to a handler
for that button. By convention, ``FormView`` looks for a method
starting with the name of the button (e.g. ``add``) and finishing with
``_success`` (e.g. ``add_success``.) The class also supports a similar
protocol for ``_failure``.

``FormView`` also supports the following methods that can be overridden:

- ``before(self, form)`` is called validation and processing any
  ``_success`` or ``_failure`` methods

- ``failure(self, e)`` is called with the exception, if the there is no
  button-specific ``_failure`` method

- ``show(self, form)`` returns ``{'form':form.render()}`` and thus
  can be a place to affect form rendering
