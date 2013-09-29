import os
import sys
import transaction

from sqlalchemy import engine_from_config

from pyramid.paster import (
    get_appsettings,
    setup_logging,
    )

from .models import (
    DBSession,
    Document,
    Node,
    Folder,
    Root,
    Base,
    )


def usage(argv):
    cmd = os.path.basename(argv[0])
    print('usage: %s <config_uri>\n'
          '(example: "%s development.ini")' % (cmd, cmd))
    sys.exit(1)


def main(argv=sys.argv):
    if len(argv) != 2:
        usage(argv)
    config_uri = argv[1]
    setup_logging(config_uri)
    settings = get_appsettings(config_uri)
    engine = engine_from_config(settings, 'sqlalchemy.')
    DBSession.configure(bind=engine)
    Base.metadata.create_all(engine)

    with transaction.manager:
        root = Root(name='', title='My SQLTraversal Root')
        DBSession.add(root)
        DBSession.flush()
        root = DBSession.query(Node).filter_by(name=u'').one()
        f1 = Folder(title='Folder 1')
        DBSession.add(f1)
        root['f1'] = f1
        da = Document(title='Document A')
        DBSession.add(da)
        f1['da'] = da