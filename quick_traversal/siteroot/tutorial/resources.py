class Root(dict):
    __name__ = ''
    __parent__ = None
    def __init__(self, title):
        self.title = title


def bootstrap(request):
    root = Root('My Site')

    return root
