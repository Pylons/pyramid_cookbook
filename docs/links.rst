..
    This file contains external links referenced in one or more Cookbook
    articles.

    The Cookbook configuration has an "intersphinx inventory", which allows you
    to link to sections in the Pyramid manual and glossary without providing
    absolute URLs. To get a list of current reference names, download
    https://docs.pylonsproject.org/projects/pyramid/en/latest/objects.inv and
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


.. _Pyramid manual: https://docs.pylonsproject.org/projects/pyramid/en/latest/
.. _Tutorials: https://docs.pylonsproject.org/projects/pyramid/en/latest/#tutorials
.. _Installing Pyramid: https://docs.pylonsproject.org/projects/pyramid/en/latest/narr/install.html
.. _Creating a Pyramid Project: https://docs.pylonsproject.org/projects/pyramid/en/latest/narr/project.html

.. _Akhet:   https://docs.pylonsproject.org/projects/akhet/en/latest/
.. _Beaker:  https://beaker.readthedocs.io/en/latest/sessions.html
.. _SQLAlchemy manual:  http://docs.sqlalchemy.org/en/latest/
.. _pyramid_handlers:  https://docs.pylonsproject.org/projects/pyramid-handlers/en/latest/
.. _pyramid_routehelper:  https://github.com/Pylons/pyramid_routehelper/blob/master/pyramid_routehelper/__init__.py

.. _Deform:  https://docs.pylonsproject.org/projects/deform/en/latest/
.. _pyramid_simpleform:  http://pythonhosted.org/pyramid_simpleform/

.. _Kotti:  https://kotti.readthedocs.io/en/latest/
.. _Ptah:  https://ptahproject.readthedocs.io/en/latest/
.. _Khufu: https://github.com/khufuproject
