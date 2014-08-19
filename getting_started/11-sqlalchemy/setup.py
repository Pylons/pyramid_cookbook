from setuptools import setup

requires = [
    'pyramid',
    'pyramid_chameleon',
]

setup(name='tutorial',
      install_requires=requires,
      entry_points="""\
      [paste.app_factory]
      main = tutorial:main
      [console_scripts]
      initialize_tutorial_db = tutorial.scripts.initializedb:main
      """,
)