# Requirements:
# Preserve existing URLs
# Map first line to title
# Ignore label
# Convert remainder of file to body
# For pubdate, use filename datestamp first; otherwise, use subversion last changed date
# Use HTML format for body text
# Take one or more file names in the /entries directory on the command line, follow
# process as laid out above
# Script opens database at the beginning, gets ahold of the container (blog),
# start looping the files
# Be able to run the script in "verbose" mode and "dry run" mode

import os
import datetime
import transaction
from optparse import OptionParser
from subprocess import Popen
from subprocess import PIPE

def main():
    from pyramid.paster import get_app
    from pyramid.scripting import get_root
    from ..resources import BlogEntry
    parser = OptionParser(description=__doc__, usage='usage: %prog [options]')
    parser.add_option('-c', '--config', dest='config',
                      help='Specify a paster config file.')
    parser.add_option('-n', '--name', dest='name', default='zodb',
                      help='Specify a section name.')
    options, args = parser.parse_args()
    config = options.config
    name = options.name
    if config is None:
       raise ValueError('must supply config file name')
    config = os.path.abspath(os.path.normpath(config))
    app = get_app(config, name)
    root, closer = get_root(app)
    for arg in args:
        print ("filename:", arg)
        if not os.path.isfile(arg):
           print ('not a file')
           continue
        path, filename = os.path.split(arg)
        id, ext = os.path.splitext(filename)
        print ("id:", id)
        lines = open(arg, 'r').readlines()
        title = lines[0]
        print ('title:', title)
        entry = '\n'.join(lines[2:])
        print ('entry:', entry[:40])
        pieces = id.split('-')
        last = pieces[-1]
        pubdate = None
        if last.startswith('200'):
           if len(last) == 8:
              year, month, day = last[0:4], last[4:6], last[6:8]
              pubdate = datetime.date(int(year), int(month), int(day))
        if pubdate is None:
           p1 = Popen(["svn", "info", arg], stdout=PIPE)
           p2 = Popen(["grep", "Last Changed Date"], stdin=p1.stdout,
                      stdout=PIPE)
           output = p2.communicate()[0]
           lines = output.split(':', 1)
           datestr = lines[1].strip()
           datestr = datestr.split(' ', 1)[0]
           year, month, day = datestr[0:4], datestr[5:7], datestr[8:10]
           pubdate = datetime.date(int(year), int(month), int(day))
        print ('pubdate:', pubdate)
        entry = BlogEntry(title.decode('UTF-8'), entry.decode('UTF-8'), 
                          id.decode('UTF-8'), pubdate, 'html', None, None)
        root[id] = entry
    transaction.commit()
           
if __name__ == '__main__':
   main()
