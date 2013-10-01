##############################################################################
#
# Copyright (c) 2008-2012 Agendaless Consulting and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the BSD-like license at
# http://www.repoze.org/LICENSE.txt.  A copy of the license should accompany
# this distribution.  THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL
# EXPRESS OR IMPLIED WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO,
# THE IMPLIED WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND
# FITNESS FOR A PARTICULAR PURPOSE
#
##############################################################################

import os

from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))
try:
    README = open(os.path.join(here, 'README.rst')).read()
    CHANGES = open(os.path.join(here, 'CHANGES.txt')).read()
except IOError:
    README = CHANGES = ''

install_requires = [
    'pyramid>=1.5dev', # route_name argument to resource_url
    'ZODB3', 
    'hypatia>=0.1a6', # check_query method of text index
    'venusian>=1.0a3',  # pyramid wants this too (prefer_finals...)
    'deform>=0.9.6', # retail form rendering capability (for documentability)
    'colander>=1.0a1', # subclassable schemanodes
    'deform_bootstrap',
    'pyramid_zodbconn',
    'pyramid_chameleon',
    'pyramid_mailer',
    'cryptacular',
    'python-magic',
    'PyYAML',
    'zope.copy',
    'zope.component', # implictly depended upon by zope.copy
    'zope.deprecation',
    'statsd',
    'pytz',
    ]

docs_extras = ['Sphinx', 'repoze.sphinx.autointerface']
testing_extras = ['nose', 'coverage', 'mock', 'virtualenv', 'nose-selecttests']

setup(name='substanced',
      version='0.0',
      description='An application server built using Pyramid',
      long_description=README + '\n\n' + CHANGES,
      classifiers=[
        "Intended Audience :: Developers",
        "Programming Language :: Python",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 2.6",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.2",
        "Programming Language :: Python :: 3.3",
        "Programming Language :: Python :: Implementation :: CPython",
        "Framework :: Pylons",
        "Topic :: Internet :: WWW/HTTP :: WSGI",
        "License :: Repoze Public License",
        ],
      keywords='wsgi pylons pyramid zodb catalog zope',
      author="Chris McDonough",
      author_email="pylons-devel@googlegroups.com",
      url="http://docs.pylonsproject.org",
      license="BSD-derived (http://www.repoze.org/LICENSE.txt)",
      packages=find_packages(),
      include_package_data=True,
      zip_safe=False,
      install_requires=install_requires,
      tests_require=install_requires,
      test_suite="substanced",
      entry_points="""
      [console_scripts]
      sd_evolve = substanced.scripts.evolve:main
      sd_reindex = substanced.scripts.reindex:main
      sd_drain_indexing = substanced.scripts.drain_indexing:main
      sd_dump = substanced.scripts.dump:main
      [pyramid.scaffold]
      substanced=substanced.scaffolds:SubstanceDProjectTemplate
      """,
      extras_require = {
          'testing':testing_extras,
          'docs':docs_extras,
          },
      )
