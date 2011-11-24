from pyramid.view import view_config

@view_config(renderer="index.pt")
def index_view(request):
    return {}


@view_config(renderer="about.pt", name="about.html")
def about_view(request):
    return {}


@view_config(renderer="company.pt", name="acme")
def company_view(request):
    return {"company": COMPANY, "projects": PROJECTS}


@view_config(renderer="people.pt", name="people")
def people_view(request):
    return {"company": COMPANY, "people": PEOPLE}

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