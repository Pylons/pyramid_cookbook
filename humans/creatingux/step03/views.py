from pyramid.view import view_config

@view_config(renderer="hello.pt")
def hello_view(request):
    return {"tutorial": "Little Dummy"}
