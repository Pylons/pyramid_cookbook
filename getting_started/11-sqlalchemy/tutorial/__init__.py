from pyramid.authentication import AuthTktAuthenticationPolicy
from pyramid.authorization import ACLAuthorizationPolicy
from pyramid.config import Configurator

from sqlalchemy import engine_from_config

from .models import DBSession, Base
from .security import groupfinder


def main(global_config, **settings):
    engine = engine_from_config(settings, 'sqlalchemy.')
    DBSession.configure(bind=engine)
    Base.metadata.bind = engine
    config = Configurator(settings=settings,
                          root_factory='tutorial.models.Root')

    # Security policies
    authn_policy = AuthTktAuthenticationPolicy(
        'sosecret', callback=groupfinder, hashalg='sha512')
    authz_policy = ACLAuthorizationPolicy()
    config.set_authentication_policy(authn_policy)
    config.set_authorization_policy(authz_policy)

    config.add_route('wiki_view', '/')
    config.add_route('login', '/login')
    config.add_route('logout', '/logout')
    config.add_route('wikipage_add', '/add')
    config.add_route('wikipage_view', '/{uid}')
    config.add_route('wikipage_edit', '/{uid}/edit')
    config.add_route('wikipage_delete', '/{uid}/delete')
    config.add_static_view(name='static', path='tutorial:static')
    config.add_static_view('deform_static', 'deform:static/')
    config.scan()
    return config.make_wsgi_app()
