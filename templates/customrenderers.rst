.. _customrenderers:

Custom Renderers
----------------

Pyramid supports custom renderers, alongside the
:ref:`default renderers <pyramid:built_in_renderers>` shipped with Pyramid.

Here's a basic comma-separated value (CSV) renderer to output a CSV file to
the browser. Add the following to a ``renderers.py`` module in your
application (or anywhere else you'd like to place such things):

.. code-block:: python

   import csv
   try:
       from StringIO import StringIO # python 2
   except ImportError:
       from io import StringIO # python 3

   class CSVRenderer(object):
      def __init__(self, info):
         pass

      def __call__(self, value, system):
         """ Returns a plain CSV-encoded string with content-type
         ``text/csv``. The content-type may be overridden by
         setting ``request.response.content_type``."""

         request = system.get('request')
         if request is not None:
            response = request.response
            ct = response.content_type
            if ct == response.default_content_type:
               response.content_type = 'text/csv'

         fout = io.StringIO()
         writer = csv.writer(fout, delimiter=',', quotechar=',', quoting=csv.QUOTE_MINIMAL)

         writer.writerow(value.get('header', []))
         writer.writerows(value.get('rows', []))

         return fout.getvalue()

Now you have a renderer. Let's register with our application's
``Configurator``:

.. code-block:: python

   config.add_renderer('csv', 'myapp.renderers.CSVRenderer')

Of course, modify the dotted-string to point to the module location you
decided upon. To use the renderer, create a view:

.. code-block:: python

   @view_config(route_name='data', renderer='csv')
   def my_view(request):
      query = DBSession.query(table).all()
      header = ['First Name', 'Last Name']
      rows = [[item.first_name, item.last_name] for item in query]

      # override attributes of response
      filename = 'report.csv'
      request.response.content_disposition = 'attachment;filename=' + filename

      return {
         'header': header,
         'rows': rows,
      }

   def main(global_config, **settings):
       config = Configurator(settings=settings)
       config.add_route('data', '/data')
       config.scan()
       return config.make_wsgi_app()

Query your database in your ``query`` variable, establish your ``headers`` and initialize
``rows``.

Override attributes of response as required by your use case. We implement this aspect in view code to keep our custom renderer code focused to the task.

Lastly, we pass ``headers`` and ``rows`` to the CSV renderer.

For more information on how to add custom Renderers, see the following sections
of the Pyramid documentation:

- `Adding a new Renderer <http://docs.pylonsproject.org/projects/pyramid/en/latest/narr/renderers.html#adding-a-new-renderer>`_
- `Varying Attributes of Rendered Responses <http://docs.pylonsproject.org/projects/pyramid/en/latest/narr/renderers.html#varying-attributes-of-rendered-responses>`_
