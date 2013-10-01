""" Dump an object (and its subobjects) to the filesystem:

sd_dump [--source=ZODB-PATH] [--dest=FILESYSTEM-PATH] config_uri
  Dumps the object at ZODB-PATH and all of its subobjects to a
  filesystem path.  Such a dump can be loaded (programmatically)
  by using the substanced.dump.load function

e.g. sd_dump --source=/ --dest=/my/dump etc/development.ini
"""

import os
import sys
from optparse import OptionParser

from pyramid.paster import (
    setup_logging,
    bootstrap,
    )
from pyramid.traversal import traverse

from substanced.dump import dump

def _print(msg):
    sys.stdout.write('%s\n' % msg)

def usage(e=None):
    if e is not None:
        _print(e)
        _print('')
    sys.exit(2)

def main():
    parser = OptionParser(description=__doc__)
    parser.add_option('-s', '--source', dest='source',
        action="store", default='/', metavar='ZODB-PATH',
        help="The ZODB source path to dump (e.g. /foo/bar or /)")
    parser.add_option('-d', '--dest', dest='dest',
        action="store", default='dump', metavar='FILESYSTEM-PATH',
        help="The destination filesystem path to dump to.")

    options, args = parser.parse_args()

    if args:
        config_uri = args[0]
    else:
        parser.error("Requires a config_uri as an argument")

    source = options.source
    dest = os.path.expanduser(os.path.normpath(options.dest))

    setup_logging(config_uri)
    env = bootstrap(config_uri)
    root = env['root']

    source = traverse(root, source)['context']

    dump(source, dest)


