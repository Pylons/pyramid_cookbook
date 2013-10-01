""" Run database evolution steps """

import datetime
import getopt
import sys
import transaction

from pyramid.paster import (
    setup_logging,
    bootstrap,
    )

def _print(msg):
    sys.stdout.write('%s\n' % msg)

def main(argv=sys.argv): # pragma: no cover
    from substanced.evolution import EvolutionManager

    def usage(e=None):
        if e is not None:
            _print(e)
            _print('')
        _print("""\
    sd_evolve [--latest] [--dry-run] [--mark-finished=stepname] [--mark-unfinished=stepname] config_uri
      Evolves new database with changes from scripts in evolve packages
         - with no arguments, evolve displays finished and unfinished steps
         - with the --latest argument, evolve runs scripts as necessary
         - with the --dry-run argument, evolve runs scripts but does not issue any commits
         - with the --mark-finished argument, marks the stepname as finished
         - with the --mark-unfinished argument, marks the stepname as unfinished

    e.g. sd_evolve --latest etc/development.ini""")
        sys.exit(2)

    name, argv = argv[0], argv[1:]
    latest = False
    dry_run = False
    mark_finished = []
    mark_unfinished = []

    try:
        opts, args = getopt.getopt(argv, 'l?hdu:f:',
                                         ['latest',
                                          'help',
                                          'dry-run',
                                          'mark-unfinished=',
                                          'mark-finished=',
                                         ])
    except getopt.GetoptError as e:
        usage(e)

    if args:
        config_uri = args[0]
    else:
        usage('Requires a config_uri as an argument')

    for k, v in opts:
        if k in ('-h', '-?', '--help'):
            usage()
        if k in ('-l', '--latest'):
            latest = True
        if k in ('-d', '--dry-run'):
            dry_run = True
        if k in ('-f', '--mark-finished'):
            mark_finished.append(v)
        if k in ('-u', '--mark-unfinished'):
            mark_unfinished.append(v)

    if latest and dry_run:
        usage('--latest and --dry-run cannot be used together')

    if (latest or dry_run) and (mark_finished or mark_unfinished):
        usage('--latest/--dry-run cannot be used with --mark-finished/--mark-unfinished')

    setup_logging(config_uri)
    env = bootstrap(config_uri)
    root = env['root']
    registry = env['registry']

    manager = EvolutionManager(root, registry)

    if latest or dry_run:
        complete = manager.evolve(latest)

        if complete:
            if dry_run:
                _print('Evolution steps dry-run:')
            else:
                _print('Evolution steps executed:')
            for item in complete:
                _print('   %s' % item)
        else:
            if dry_run:
                _print('No evolution steps dry-run')
            else:
                _print('No evolution steps executed')

    elif mark_finished or mark_unfinished:
        t = transaction.get()

        for step in mark_finished:
            finished_steps = manager.get_finished_steps()
            unfinished_steps = dict(manager.get_unfinished_steps())
            if step in finished_steps:
                _print('Step %s already marked as finished' % step)
            else:
                if step in unfinished_steps:
                    manager.add_finished_step(step)
                    _print('Step %s marked as finished' % step)
                    t.note('Marked %s evolution step as finished' % step)
                else:
                    _print('Unknown step %s, not marking as finished' % step)

        for step in mark_unfinished:
            finished_steps = manager.get_finished_steps()
            unfinished_steps = dict(manager.get_unfinished_steps())
            if step in finished_steps:
                manager.remove_finished_step(step)
                _print('Step %s marked as unfinished' % step)
                t.note('Marked %s evolution step as unfinished' % step)
            else:
                if step in unfinished_steps:
                    _print('Step %s already marked as unfinished' % step)
                else:
                    _print('Unknown step %s, not marking as unfinished' % step)

        t.commit()

    else:
        _print('Finished steps:\n')
        for ts, stepname in manager.get_finished_steps_by_value():
            tp = datetime.datetime.fromtimestamp(ts).strftime(
                '%Y-%m-%d %H:%M:%S')
            _print('    %s %s' % (tp, stepname))
        _print ('\nUnfinished steps:\n')
        for stepname, func in manager.get_unfinished_steps():
            _print(' '*24 + stepname)

if __name__ == '__main__':
    main()
