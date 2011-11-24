from pyramid.decorator import reify
from pyramid.location import lineage
from pyramid.renderers import get_renderer

from resources import Company
from resources import Site

class Layouts(object):
    @reify
    def global_template(self):
        renderer = get_renderer("templates/global_layout.pt")
        return renderer.implementation().macros['layout']

    @reify
    def global_macros(self):
        renderer = get_renderer("templates/macros.pt")
        return renderer.implementation().macros

    @reify
    def site(self):
        # From somewhere deep in hierarchy, reach up and grab site
        for l in lineage(self.context):
            if isinstance(l, Site):
                return l
        return None

    @reify
    def company(self):
        # From somewhere deep in hierarchy, reach up and grab company
        for l in lineage(self.context):
            if isinstance(l, Company):
                return l
        return None

    @reify
    def message(self):
        return self.request.GET.get('msg', None)

    @reify
    def site_menu(self):
        new_menu = []
        for c in [self.site,] + self.site.values():
            url = self.request.resource_url(c)
            new_menu.append({'href': url, 'title': c.title})
        return new_menu

