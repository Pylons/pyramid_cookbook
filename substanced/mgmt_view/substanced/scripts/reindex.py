""" Reindex the catalog  """

import re
from optparse import OptionParser

from pyramid.paster import (
    setup_logging,
    bootstrap,
    )

from pyramid.traversal import resource_path

from substanced.objectmap import find_objectmap

from substanced.catalog import Catalog

from substanced.util import get_dotted_name

def main():
    parser = OptionParser(description=__doc__)
    parser.add_option('-d', '--dry-run', dest='dry_run',
        action="store_true", default=False,
        help="Don't commit the transactions")
    parser.add_option('-i', '--interval', dest='commit_interval',
        action="store", default=3000,
        help="Commit every N transactions")
    parser.add_option('-p', '--path', dest='path',
        action="store", default=None, metavar='EXPR',
        help="Reindex only objects whose path matches a regular expression")
    parser.add_option('-n', '--index', dest='indexes',
        action="append", help="Reindex only the given index (can be repeated)")
    parser.add_option('-c', '--catalog', dest='catalog_specs', action="append",
        help=("Reindex only the catalog provided (may be a path or a name "
              "and may be specified multiple times)"))

    options, args = parser.parse_args()

    if args:
        config_uri = args[0]
    else:
        parser.error("Requires a config_uri as an argument")

    commit_interval = int(options.commit_interval)
    if options.path:
        path_re = re.compile(options.path)
    else:
        path_re = None

    kw = {}
    if options.indexes:
        kw['indexes'] = options.indexes

    setup_logging(config_uri)
    env = bootstrap(config_uri)
    site = env['root']
    registry = env['registry']

    kw['registry'] = registry

    objectmap = find_objectmap(site)

    catalog_oids = objectmap.get_extent(get_dotted_name(Catalog))

    for oid in catalog_oids:

        catalog = objectmap.object_for(oid)

        path = resource_path(catalog)

        if options.catalog_specs:

            if ( (not path in options.catalog_specs) and 
                 (not catalog.__name__ in options.catalog_specs) ):
                    continue

        catalog.reindex(path_re=path_re, commit_interval=commit_interval,
                        dry_run=options.dry_run, **kw)

if __name__ == '__main__':
    main()
