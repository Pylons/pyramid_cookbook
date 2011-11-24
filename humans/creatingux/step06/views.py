from pyramid.renderers import get_renderer
from pyramid.decorator import reify
from pyramid.view import view_config

from dummy_data import COMPANY
from dummy_data import PEOPLE
from dummy_data import PROJECTS
from dummy_data import SITE_MENU

class ProjectorViews(object):

    def __init__(self, request):
        self.request = request
        renderer = get_renderer("templates/global_layout.pt")
        self.global_template = renderer.implementation().macros['layout']

    @reify
    def company_name(self):
        return COMPANY

    @reify
    def site_menu(self):
        new_menu = SITE_MENU[:]
        url = self.request.url
        for menu in new_menu:
            if menu['title'] == 'Home':
                menu['current'] = url.endswith('/')
            else:
                menu['current'] = url.endswith(menu['href'])
        return new_menu

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


