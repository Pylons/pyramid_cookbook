from pyramid.renderers import get_renderer
from pyramid.decorator import reify

from dummy_data import COMPANY
from dummy_data import SITE_MENU

class Layouts(object):

    @reify
    def global_template(self):
        renderer = get_renderer("templates/global_layout.pt")
        return renderer.implementation().macros['layout']

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


