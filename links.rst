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


.. _Pyramid manual: http://docs.pylonsproject.org/projects/pyramid/en/1.3-branch/
.. _Installing Pyramid: http://docs.pylonsproject.org/projects/pyramid/en/1.3-branch/narr/install.html
.. _Creating Your First Pyramid Application: http://docs.pylonsproject.org/projects/pyramid/en/1.3-branch/narr/firstapp.html

.. _Akhet:   http://docs.pylonsproject.org/projects/akhet/en/latest/
.. _Beaker:  http://beaker.readthedocs.org/en/latest/sessions.html
