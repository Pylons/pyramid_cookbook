.. _customrendererxlsx:

Render into xlsx
----------------

What if we want to have a renderer that always takes the
same data as our main renderer (such as mako or jinja2),
but renders them into something
else, for example xlsx. Then we could do something like this:

.. code-block:: python

    # the first view_config for the xlsx renderer that
    # kicks in when there is a request parameter xlsx
    @view_config(context="myapp.resources.DBContext",
                 renderer="dbtable.xlsx",
                 request_param="xlsx")
    # the second view_config for mako
    @view_config(context="myapp.resources.DBContext",
                 renderer="templates/dbtable.mako")
    def dbtable(request):
        # any code that prepares the data
        # this time, the data have been loaded into context
        return {}


That means that the approach described in :ref:`custom renderers
<customrenderers>` is not enough. We have to define a template
system. Our renderer will have to lookup the template, render
it, and return as an xlsx document.

Let's define the template interface. Our templates will be plain
python files placed into the project's xlsx subdirectory,
with 2 functions defined:

  - ``get_header`` will return the table header cells
  - ``iterate_rows`` will yield the table rows

Our renderer will have to:

  - import the template
  - run the functions to get the data
  - put the data into an xlsx file
  - return the file

As our templates will be python files, we will use a trick.
In the ``view_config`` we change the suffix of the template
to ``.xlsx`` so that we can configure our view. In the renderer
we look up that filename with the ``.py`` suffix instead
of ``.xlsx``.

Add following into a ``xlsxrenderer.py`` in your application.

.. code-block:: python

   import importlib

   import openpyxl
   import openpyxl.styles
   import openpyxl.writer.excel


   class XLSXRenderer(object):
       XLSX_CONTENT_TYPE = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
       def __init__(self, info):
           self.suffix = info.type
           self.templates_pkg = info.package.__name__ + ".xlsx"

       def __call__(self, value, system):
           templ_name = system["renderer_name"][:-len(self.suffix)]
           templ_module = importlib.import_module("." + templ_name, self.templates_pkg)
           wb = openpyxl.Workbook()
           ws = wb.active
           if "get_header" in dir(templ_module):
               ws.append(getattr(templ_module, "get_header")(system, value))
               ws.row_dimensions[1].font = openpyxl.styles.Font(bold=True)
           if "iterate_rows" in dir(templ_module):
               for row in getattr(templ_module, "iterate_rows")(system, value):
                   ws.append(row)

           request = system.get('request')
           if not request is None:
               response = request.response
               ct = response.content_type
               if ct == response.default_content_type:
                   response.content_type = XLSXRenderer.XLSX_CONTENT_TYPE
               response.content_disposition = 'attachment;filename=%s.xlsx' % templ_name

           return openpyxl.writer.excel.save_virtual_workbook(wb)


Now you have a renderer. Let's register with our application's
``Configurator``:

.. code-block:: python

   config.add_renderer('.xlsx', 'myapp.renderers.CSVRenderer')

Of course, modify the dotted-string to point to the module location you
decided upon. You must also write the templates in the directory
``myapp/xlsx``, such as ``myapp/xlsx/dbtable.py``. Here is an example
of a dummy template:

.. code-block:: python

    def get_header(system, value):
        # value is the dictionaty returned from the view
        # request = system["request"]
        # context = system["context"]
        return ["Row number", "A number", "A string"]

    def iterate_rows(system, value):
        for row in range(100):
            return [row, 100, "A string"]


To see a working example of this approach, visit:

- `Pyramid Sample Application <https://github.com/petrblahos/pyrasample>`_

There is a Czech version of this recipe here:

- `XLSX z Pyramid bezbolestně <https://www.blahos.com/blog/pyramid-render-xlsx/>`_

For more information on how to add custom Renderers, see the following sections
of the Pyramid documentation:

- `Adding a new Renderer <https://docs.pylonsproject.org/projects/pyramid/en/latest/narr/renderers.html#adding-a-new-renderer>`_
- `Varying Attributes of Rendered Responses <https://docs.pylonsproject.org/projects/pyramid/en/latest/narr/renderers.html#varying-attributes-of-rendered-responses>`_
- :ref:`Custom renderers recipe <customrenderers>`
