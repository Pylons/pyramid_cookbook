from .db import root_factory # b/c
root_factory = root_factory

def include(config): # pragma: no cover
    """ Perform all ``config.include`` tasks required for Substance D and the
    default aspects of the SDI to work."""
    config.include('pyramid_chameleon')
    config.include('pyramid_zodbconn')
    config.include('pyramid_mailer')
    config.include('.evolution')
    config.include('.stats')
    config.include('.folder')
    config.include('.event')
    config.include('.sdi')
    config.include('.content')
    config.include('.objectmap')
    config.include('.property')
    config.include('.catalog')
    config.include('.widget')
    config.include('.workflow')
    config.include('.dump')
    config.include('.locking')
    config.include('.audit')
    config.include('.editable')

def scan(config): # pragma: no cover
    """ Perform all ``config.scan`` tasks required for Substance D and the
    default aspects of the SDI to work."""
    config.scan('.stats')
    config.scan('.catalog')
    config.scan('.file')
    config.scan('.folder')
    config.scan('.objectmap')
    config.scan('.principal')
    config.scan('.property')
    config.scan('.root')
    config.scan('.sdi')
    config.scan('.db')
    config.scan('.workflow')
    config.scan('.audit')
    config.scan('.locking')
    
def includeme(config): # pragma: no cover
    """ Do the work of :func:`substanced.include`, then
    :func:`substanced.scan`.  Makes ``config.include(substanced)`` work."""
    # NB: includes of packages which register directives must be done before
    # scans of packages which use venusian decorators that use those directives
    # e.g. (@subscribe_*, @mgmt_view, @content).  This is why we do all
    # includes first, then we scan afterwards instead of intermingling scans
    # and includes.
    config.include(include)
    config.include(scan)
