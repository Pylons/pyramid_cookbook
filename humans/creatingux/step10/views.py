from random import randint

from pyramid.view import view_config

from dummy_data import COMPANY
from dummy_data import PEOPLE
from dummy_data import PROJECTS

from layouts import Layouts

class ProjectorViews(Layouts):

    def __init__(self, request):
        self.request = request

    @view_config(renderer="templates/index.pt")
    def index_view(self):
        return {"page_title": "Home"}

    @view_config(renderer="templates/about.pt", name="about.html")
    def about_view(self):
        return {"page_title": "About"}

    @view_config(renderer="templates/company.pt",
                 name="acme")
    def company_view(self):
        return {"page_title": COMPANY + " Projects",
                "projects": PROJECTS}

    @view_config(renderer="templates/people.pt", name="people")
    def people_view(self):
        return {"page_title": "People", "people": PEOPLE}

    @view_config(renderer="json", name="updates.json")
    def updates_view(self):
        return [
            randint(0,100),
            randint(0,100),
            randint(0,100),
            randint(0,100),
            888,
        ]


