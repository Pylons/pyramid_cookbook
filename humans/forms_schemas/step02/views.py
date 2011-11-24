from pyramid.view import view_config

import colander
from deform import Form
from deform import ValidationFailure

class Person(colander.MappingSchema):
    name = colander.SchemaNode(colander.String())
    shoe_size = colander.SchemaNode(
        colander.Integer(),
        missing = 0,
    )

class ProjectorViews(object):
    def __init__(self, request):
        self.request = request

    @view_config(renderer="templates/site_view.pt")
    def site_view(self):
        schema = Person()
        myform = Form(schema, buttons=('submit',))

        if 'submit' in self.request.POST:
            controls = self.request.POST.items()
            try:
                appstruct = myform.validate(controls)
            except ValidationFailure, e:
                return {'form':e.render(), 'values': False}
            # Process the valid form data, do some work
            values = {
                "name": appstruct['name'],
                "shoe_size": appstruct['shoe_size'],
                }
            return {"form": myform.render(), "values": values}

        # We are a GET not a POST
        return {"form": myform.render(), "values": None}

