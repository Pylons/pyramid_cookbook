from pyramid.renderers import get_renderer
from pyramid.view import view_config

def site_layout():
    renderer = get_renderer("templates/global_layout.pt")
    layout = renderer.implementation().macros['layout']
    return layout


@view_config(renderer="templates/index.pt")
def index_view(request):
    return {"layout": site_layout(),
            "page_title": "Home"}


@view_config(renderer="templates/about.pt", name="about.html")
def about_view(request):
    return {"layout": site_layout(),
            "page_title": "About"}


@view_config(renderer="templates/company.pt", name="acme")
def company_view(request):
    return {"layout": site_layout(),
            "page_title": COMPANY + " Projects",
            "company": COMPANY,
            "projects": PROJECTS}


@view_config(renderer="templates/people.pt", name="people")
def people_view(request):
    return {"layout": site_layout(),
            "page_title": "People", "company": COMPANY, "people": PEOPLE}

# Dummy data
COMPANY = "ACME, Inc."

PEOPLE = [
        {'name': 'sstanton', 'title': 'Susan Stanton'},
        {'name': 'bbarker', 'title': 'Bob Barker'},
]

PROJECTS = [
        {'name': 'sillyslogans', 'title': 'Silly Slogans'},
        {'name': 'meaninglessmissions', 'title': 'Meaningless Missions'},
]