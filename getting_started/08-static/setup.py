from setuptools import setup

requires = [
    'pyramid',
    'pyramid_chameleon'
    ]

setup(name='tutorial',
      entry_points="""\
      [paste.app_factory]
      main = tutorial:main
      """,
      )
