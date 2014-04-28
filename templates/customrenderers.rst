.. _customrenderers:

Custom Renderers
----------------

Here's a basic CSV renderer to output a csv file to the browser.
Add the following to your renderers.py or create a new renderes.py::

   class CSVRenderer(object):
      def __init__(self, info):
      pass
    
   def __call__(self, value, system):
      fout = StringIO.StringIO()
      writer = csv.writer(fout, delimiter=',',quotechar =',',quoting=csv.QUOTE_MINIMAL)
    
      writer.writerow(value['header'])
      writer.writerows(value['rows'])
      filename = value['filename']
    
      resp = system['request'].response
      resp.content_type = 'text/csv'
      resp.content_disposition = 'attachment;filename='+filename+'.csv'
      return fout.getvalue()
      
Be sure that in either case, you import both ``csv`` and ``StringIO``

Now you have a renderer. To use the renderer, create a view::

   @view_config(route_name='route', renderer='csv')
   def route(self):
      d = datetime.now()
      qeury = DBSession.query(table).all()
      header = ['First Name', 'Last Name']
      rows = []
      //returns filename of report with timestamp and beginning 0 removed
      filename = "report" + d.strftime(" %m/%d").replace(' 0', '')
      for i in query:
      items = [i.first_name, i.last_name]
      rows.append(items)
      return {
         'header': header,
         'rows': rows,
         'filename': filename
      }
      
This view does a few things, not all of which are required. Qeury your database in your ``query`` variable, establish your headers and initialize ``rows[]``. Then it determines the filename. You only need a name here, but I've added the month and day using ``datetime()`` and ``strftime()``

Then it loops the query in ``items[]`` and then appends the result into the ``rows[]`` array we intialized earlier. 

Lastly, we return all of our data to pass it to the CSV renderer. Like I said, not all of what you see is required. The only thing the renderer requires is a header, rows, and a filename. Now you need to configure your route and renderer::

    config.add_route('route','/route')
    config.add_renderer(name='csv', factory='package.custom.CSVRenderer')
    
In my enrivonment, I placed the ``CSVRenderer`` class in a file called ``custom.py``. If you modify your renderers.py in your pyramid installation, your factory would be ``pyramid.renderers.CSVRenderer`` 
