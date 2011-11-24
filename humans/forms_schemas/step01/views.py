import colander
from deform import Form
from pyramid.view import view_config

class Person(colander.MappingSchema):
    name = colander.SchemaNode(colander.String())

class ProjectorViews(object):
    def __init__(self, request):
        self.request = request

    @view_config(renderer="templates/site_view.pt")
    def site_view(self):
        schema = Person()
        myform = Form(schema, buttons=('submit',))

        return {"form": myform.render()}

