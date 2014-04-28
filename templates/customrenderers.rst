.. _customrenderers:

Custom Renderers
----------------

Pyramid supports completely custom renderers, alongside the
:ref:`default renderers <pyramid:build_in_renderers>` shipped with Pyramid.

Here's a basic CSV renderer to output a csv file to the browser.
Add the following to a ``renderers.py`` module in your application (or
anywhere else you'd like to place such things):

.. code-block:: python

   import csv
   import io

   class CSVRenderer(object):
      def __init__(self, info):
          pass

   def __call__(self, value, system):
      fout = io.StringIO()
      writer = csv.writer(fout, delimiter=',',quotechar =',',quoting=csv.QUOTE_MINIMAL)

      writer.writerow(value['header'])
      writer.writerows(value['rows'])
      filename = value['filename']

      resp = system['request'].response
      resp.content_type = 'text/csv'
      resp.content_disposition = 'attachment;filename=' + filename + '.csv'
      return fout.getvalue()

Now you have a renderer. Let's register with our application's
``Configurator``:

.. code-block:: python

   config.add_renderer('csv', 'myapp.renderers.CSVRenderer')

Of course, modify the dotted-string to point to the module location you
decided upon. To use the renderer, create a view:

.. code-block:: python

   @view_config(route_name='data', renderer='csv')
   def my_view(self):
      d = datetime.now()
      query = DBSession.query(table).all()
      header = ['First Name', 'Last Name']
      rows = []

      # returns filename of report with timestamp and beginning 0 removed
      filename = "report" + d.strftime(" %m/%d").replace(' 0', '')
      for i in query:
          items = [i.first_name, i.last_name]
          rows.append(items)

      return {
         'header': header,
         'rows': rows,
         'filename': filename
      }

   def main(global_config, **settings):
       config = Configurator(settings=settings)
       config.add_route('data', '/data')
       return config.make_wsgi_app()

This view does a few things, not all of which are required. Query your database
in your ``query`` variable, establish your headers and initialize ``rows[]``.
Then it determines the filename. You only need a name here, but I've added the
month and day using ``datetime()`` and ``strftime()``

Then it loops the query in ``items[]`` and then appends the result into the
``rows[]`` array we intialized earlier.

Lastly, we return all of our data to pass it to the CSV renderer. Not all of
what you see is required. The only thing the renderer requires is a header,
rows, and a filename.
