# Contribute to the Pyramid Community Cookbook

The Pyramid Community Cookbook is a collection of "recipes" that are
contributed by members of the Pyramid community. The recipes are supplemental
material to the [main Pyramid
documentation](http://docs.pylonsproject.org/projects/pyramid/en/latest/).

## Write a recipe

All projects under the Pylons Project follow guidelines.

- [How to Contribute](http://www.pylonsproject.org/community/how-to-contribute)
- [How to Participate](http://www.pylonsproject.org/community/how-to-participate)
- [Code of Conduct](http://www.pylonsproject.org/community/code-of-conduct)

### Requirements

Contributors must have a working knowledge of reStructuredText and Sphinx, as
well as how to set up a Python environment.

Contributors must build a local version of the HTML docs before submitting a
pull request to the repository.

### Coding Style

- PEP8 compliance.  Whitespace rules are relaxed: it is not necessary to put
  two newlines between classes.  But 79-column lines, in particular, are
  mandatory.  See
  http://docs.pylonsproject.org/en/latest/community/codestyle.html for more
  information.

### Getting started

1. While logged into your GitHub account, navigate to the Pyramid Community
   Cookbook repo on GitHub.

        https://github.com/Pylons/pyramid_cookbook

2. Fork and clone the Pyramid Community Cookbook repository to your GitHub
   account by clicking the "Fork" button.

3. Clone your fork of the Pyramid Community Cookbook from your GitHub account
   to your local computer, substituting your account username and specifying
   the destination as "hack-on-cookbook".

        $ cd ~
        $ git clone git@github.com:USERNAME/pyramid_cookbook.git hack-on-cookbook
        $ cd hack-on-cookbook
        # Configure remotes such that you can pull changes from the Pyramid
        # repository into your local repository.
        $ git remote add upstream https://github.com/Pylons/pyramid_cookbook.git
        # fetch and merge changes from upstream into master
        $ git fetch upstream
        $ git merge upstream/master

   Now your local repo is set up such that you will push changes to your
   GitHub repo, from which you can submit a pull request.

4. Create a virtualenv:

        $ export VENV=~/hack-on-cookbook/env
        $ virtualenv $VENV

5. Install the Pyramid Community Cookbook from the checkout into the virtualenv
   using the following command.

        $ $VENV/bin/python setup.py install

### Build the HTML docs

Once you have your environment set up, then change into the ``docs``
directory and build the HTML documentation.

    $ cd docs/
    $ make html SPHINXBUILD=$VENV/bin/sphinx-build

To view your docs, open the ``docs/_build/html/index.html`` file in a web
browser.

### Sign CONTRIBUTORS.txt

In the root of your local repository, open and sign the document
``CONTRIBUTORS.txt``.  This will become part of your pull request.

### Submit a pull request

Once your docs build successfully, then commit your changes to your local
repository, push your commit to your repository on GitHub, then submit a pull
request for the Pylons Project team members to review.

## Get support

First read the guidelines for [Get Support](http://www.pylonsproject.org/community/get-support)
in any project under the Pylons Project.

### Mailing list

[Pylons Discuss](http://groups.google.com/group/pylons-discuss) is a
good place to ask for help.

### IRC

Visit the ``#pyramid`` channel on IRC on ``irc.freenode.net``.

