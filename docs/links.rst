..
    This file contains external links referenced in one or more Cookbook
    articles.

    The Cookbook configuration has an "intersphinx inventory", which allows you
    to link to sections in the Pyramid manual and glossary without providing
    absolute URLs. To get a list of current reference names, download
    http://docs.pylonsproject.org/projects/pyramid/dev/objects.inv and
    uncompress it (GZIP format). It will be a text file with lines like this:

    response std:term -1 glossary.html#term-$ -
    mako_templates std:label -1 narr/templates.html#mako-templates Templating With Mako Templates

    Lines with "std:term" are glossary entries. You can put :term:`response` in
    your article and it will be rendered as a link to the glossary term. Lines
    with "std:label" are section targets. You can put :term:`mako_templates` in
    your article and it will be rendered as a link to that section in the
    Pyramid manual with the section title as the link text. Or you can override
    the link text with the Docutils text syntax: :ref:`Mako <mako_templates>`.

    Note: this isn't working for me with multiword terms with spaces.


.. _Pyramid manual: http://docs.pylonsproject.org/projects/pyramid/en/1.3-branch/index.html
.. _Tutorials: http://docs.pylonsproject.org/projects/pyramid/en/1.3-branch/index.html#tutorials
.. _Installing Pyramid: http://docs.pylonsproject.org/projects/pyramid/en/1.3-branch/narr/install.html
.. _Creating a Pyramid Project: http://docs.pylonsproject.org/projects/pyramid/en/1.3-branch/narr/project.html

.. _Akhet:   http://docs.pylonsproject.org/projects/akhet/en/latest/
.. _Beaker:  http://beaker.readthedocs.org/en/latest/sessions.html
.. _SQLAlchemy manual:  http://docs.sqlalchemy.org/
.. _pyramid_handlers:  http://docs.pylonsproject.org/projects/pyramid_handlers/en/latest/
.. _pyramid_routehelper:  https://github.com/Pylons/pyramid_routehelper/blob/master/pyramid_routehelper/__init__.py

.. _Deform:  http://docs.pylonsproject.org/projects/deform/en/latest/
.. _pyramid_simpleform:  http://packages.python.org/pyramid_simpleform/

.. _Kotti:  http://kotti.readthedocs.org/en/latest/index.html
.. _Ptah:  http://ptahproject.readthedocs.org/en/latest/index.html
.. _Khufu: http://pypi.python.org/pypi?%3Aaction=search&term=khufu&submit=search
