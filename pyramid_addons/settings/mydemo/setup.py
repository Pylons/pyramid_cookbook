from setuptools import setup

requires = [
    'pyramid',
]

setup(name='mydemo',
      install_requires=requires,
      entry_points="""\
      [paste.app_factory]
      main = mydemo:main
      """,
)