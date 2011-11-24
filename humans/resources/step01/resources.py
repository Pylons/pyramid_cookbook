class SiteFolder(dict):
    __name__ = ''
    __parent__ = None

    def __init__(self, title):
        self.title = title

def bootstrap(request):
    root = SiteFolder('Projector Site')

    return root
