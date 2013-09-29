from setuptools import setup

requires = [
    'pyramid',
    'pyramid_jinja2',
    'ZODB3',
    'pyramid_zodbconn',
    'pyramid_tm',
    'pyramid_debugtoolbar'
]

setup(name='tutorial',
      install_requires=requires,
      entry_points="""\
      [paste.app_factory]
      main = tutorial:main
      """,
)
