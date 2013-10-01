import os
import datetime
import transaction
from optparse import OptionParser

def main():
    from pyramid.paster import bootstrap
    from ..resources import BlogEntry
    parser = OptionParser(description=__doc__, usage='usage: %prog [options]')
    parser.add_option('-c', '--config', dest='config',
                      help='Specify a paster config file.')
    parser.add_option('-i', '--num', dest='num', default='10000',
                      help='Specify the number of blog entries to add.')
    options, args = parser.parse_args()
    config = options.config
    num = int(options.num)
    if config is None:
       raise ValueError('must supply config file name')
    config = os.path.abspath(os.path.normpath(config))

    env = bootstrap(config)
    root = env['root']
    registry = env['registry']
    closer = env['closer']
    for n in range(0, num):
        print ("adding", n)
        entry = registry.content.create(
            'Blog Entry',
            'title %s' % n,
            'entry %s' % n,
            'html',
            datetime.date.today(),
            )
        id = 'blogentry_%s' % n
        root[id] = entry
        if n % 10000 == 0:
            print ('committing')
            transaction.commit()
    print ('committing')
    transaction.commit()
    root._p_jar._db.close()
    closer()
           
if __name__ == '__main__':
   main()
