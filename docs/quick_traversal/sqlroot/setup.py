from setuptools import setup

requires = [
    'pyramid',
    'pyramid_jinja2',
    'pyramid_tm',
    'sqlalchemy',
    'zope.sqlalchemy',
    'pyramid_debugtoolbar'
]

setup(name='tutorial',
      install_requires=requires,
      entry_points="""\
      [paste.app_factory]
      main = tutorial:main
      [console_scripts]
      initialize_tutorial_db = tutorial.initialize_db:main
      """,
)
