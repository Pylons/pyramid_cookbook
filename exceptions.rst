Exceptions
==========

Configuring an HTTPException Exception View
-------------------------------------------

Pyramid, out of the box, requires that you *return* instances of WebOb HTTP
exceptions rather than *raise* them.  If you'd prefer to raise HTTP
exceptions rather than return them, you can add a view callable named
``error_view`` somewhere in your code.  This view callable should simply
return the context it is passed.

.. code-block:: python
   :linenos:

   def error_view(context, request):
       return context

This configure the ``error_view`` you've defined as the "exception view" when
an HTTPException is raised.

.. code-block:: python
   :linenos:

   from webob.exc import HTTPException
   config.add_view(error_view, context=HTTPException)

Once your application is configured with an HTTPException error view, you can
do this in your view code:

.. code-block:: python
   :linenos:

   raise HTTPFound(location='http://example.com')

Rather than:

.. code-block:: python
   :linenos:

   return HTTPFound(location='http://example.com')

This works because the exception is actually a valid response object.  Our
``error_view`` view callable just returns it when the exception view is
executed.

Raising WebOb HTTP exception objects directly will only work in Python 2.5+
(due to WebOb implementation constraints).

See also :ref:`exception_views`.
