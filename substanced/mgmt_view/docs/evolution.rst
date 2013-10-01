==========================================
Changing Resource Structure With Evolution
==========================================

As you develop your software and make changes to structures,
your existing content will be in an old state. Whether in production or
during development, you need a facility to correct out-of-date data.

Evolution provides a rich facility for "evolving" your resources to
match changes during development. Substance D's evolution facility
gives Substance D developers full control over the data updating process:

- Write scripts for each package that get called during an update

- Set revision markers in the data to indicate the revision level a
  database is at

- Console script and SDI GUI that can be run to "evolve" a database

Running an Evolution from the Command Line
==========================================

Substance D applications generate a console script at
``bin/sdi_evolve``. Running this without arguments displays some help:

.. code-block:: bash

    $ bin/sd_evolve
    Requires a config_uri as an argument

        sd_evolve [--latest] [--dry-run] [--mark-finished=stepname] [--mark-unfinished=stepname] config_uri
          Evolves new database with changes from scripts in evolve packages
             - with no arguments, evolve displays finished and unfinished steps
             - with the --latest argument, evolve runs scripts as necessary
             - with the --dry-run argument, evolve runs scripts but does not issue any commits
             - with the --mark-finished argument, marks the stepname as finished
             - with the --mark-unfinished argument, marks the stepname as unfinished

        e.g. sd_evolve --latest etc/development.ini

Running with your INI file, as explained in the help,
shows information about the version numbers of various packages:

.. code-block:: bash

    $ bin/sd_evolve etc/development.ini

    Finished steps:

        2013-06-14 13:01:28 substanced.evolution.legacy_to_new

    Unfinished steps:

This shows that one evolution step has already been run and that there are no
unfinished evolution steps.

Running an Evolution from the SDI
=================================

The Evolution section of the ``Database`` tab of the Substance D root object
allows you to do what you might have otherwise done using the ``sd_evolve``
console script described above.

In some circumstances when Substance D itself needs to be upgraded, you may
need to use the ``sd_evolve`` script rather than the GUI.  For example, if the
way that Substance D ``Folder`` objects work is changed and folder objects need
to be evolved, it may be impossible to view the evolution GUI, and you may need
to use the console script.

Autoevolve
==========

If you add `substanced.autoevolve = true` within your application .ini file,
all pending evolution upgrade steps will be run when your application starts.
Alternately you can use the ``SUBSTANCED_AUTOEVOLVE`` evnironment variable
(e.g. ``export SUBSTANCED_AUTOEVOLVE=true``) to do the same thing.

Adding Evolution Support To a Package
=====================================

Let's say we have been developing an ``sdidemo`` package and,
with content already in the database, we want to add evolution support.
Our ``sdidemo`` package is designed to be included into a site,
so we have the traditional Pyramid ``includeme`` support. In there we
add the following:

.. code-block:: python

    import logging

    logger = logging.getLogger('evolution')

    def evolve_stuff(root):
        logger.info('Stuff evolved.')

    def includeme(config):
        config.add_evolution_step(evolve_stuff)

We've used the :func:`substanced.evolution.add_evolution_step` API to add an
evolution step in this package's ``includeme`` function.

Running ``sd_evolve`` *without* ``--latest`` (meaning,
without performing an evolution) shows that Substance D's evolution now
knows about our package:

.. code-block:: bash

    $ bin/sd_evolve etc/development.ini

    Finished steps:

        2013-06-14 13:01:28 substanced.evolution.legacy_to_new

    Unfinished steps:

                            sdidemo.evolve_stuff

Let's now run ``sd_evolve`` "for real".  This will cause the evolution step to
be executed and marked as finished.

.. code-block:: bash

    $ bin/sd_evolve --latest etc/development.ini

    2013-06-14 13:22:51,475 INFO  [evolution][MainThread] Stuff evolved.
    Evolution steps executed:
       substanced.evolution.evolve_stuff

This examples shows a number of points:

- Each package can easily add evolution support via the
  ``config.add_evolution_step()`` directive.  You can learn more about this
  directive by reading its API documentation at
  :func:`substanced.evolution.add_evolution_step`.

- Substance D's evolution service looks at the database to see which steps
  haven't been run, then runs all the needed evolve scripts, sequentially, to
  bring the database up to date.

- All changes within an evolve script are in the scope of a
  transaction. If all the evolve scripts run to completion without
  exception, the transaction is committed.

Manually Marking a Step As Evolved
==================================

In some cases you might have performed the work in an evolve step by hand and
you know there is no need to re-perform that work. You'd like to mark the step
as finished for one or more evolve scripts, so these steps don't get run.  The
``--mark-step-finished`` argument to ``sd_evolve`` accomplishes this.  The
"Mark finished" button in the SDI evolution GUI does the same.

Baselining
==========

Evolution is baselined at first startup. When there's no initial list of
finished steps in the database.  Substance D, in the root factory, says: "I
know all the steps participating in evolution, so when I first create the
root object, I will set all of those steps to finished."

