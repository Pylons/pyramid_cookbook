""" Drain deferred indexing actions """

from optparse import OptionParser

from pyramid.paster import (
    setup_logging,
    bootstrap,
    )

from substanced.catalog.deferred import BasicActionProcessor

def main():
    parser = OptionParser(description=__doc__)

    options, args = parser.parse_args()

    if args:
        config_uri = args[0]
    else:
        parser.error("Requires a config_uri as an argument")

    setup_logging(config_uri)
    env = bootstrap(config_uri)
    site = env['root']

    processor = BasicActionProcessor(site)
    processor.process() # loops

if __name__ == '__main__':
    main()
