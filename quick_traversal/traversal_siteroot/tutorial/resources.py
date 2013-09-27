class SiteFolder(dict):
    def __init__(self, title):
        self.title = title


def bootstrap(request):
    root = SiteFolder('My Site')

    return root