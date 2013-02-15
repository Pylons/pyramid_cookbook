Django-Style "settings.py" Configuration
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

If you enjoy accessing global configuration via import statements ala
Django's ``settings.py``, you can do something similar in Pyramid.

- Create a ``settings.py`` file in your application's package (for example,
  if your application is named "myapp", put it in the filesystem directory
  named ``myapp``; the one with an ``__init__.py`` in it.

- Add values to it at its top level.

For example::

  # settings.py
  import pytz

  timezone = pytz('US/Eastern')

Then simply import the module into your application::

  from myapp import settings

  def myview(request):
      timezone = settings.timezone
      return Response(timezone.zone)

This is all you really need to do if you just want some global configuration
values for your application.

However, more frequently, values in your ``settings.py`` file need to be
conditionalized based on deployment settings.  For example, the timezone
above is different between development and deployment.  In order to
conditionalize the values in your ``settings.py`` you can use *other* values
from the Pyramid ``development.ini`` or ``production.ini``.  To do so,
your ``settings.py`` might instead do this::

    import os

    ini = os.environ['PYRAMID_SETTINGS']
    config_file, section_name = ini.split('#', 1)

    from paste.deploy.loadwsgi import appconfig
    config = appconfig('config:%s' % config_file, section_name)

    import pytz
        
    timezone = pytz.timezone(config['timezone'])

The value of ``config`` in the above snippet will be a dictionary
representing your application's ``development.ini`` configuration section.
For example, for the above code to work, you'll need to add a ``timezone``
key/value pair to a section of your ``development.ini``::

   [app:myapp]
   use = egg:MyApp
   timezone = US/Eastern

If your ``settings.py`` is written like this, before starting Pyramid, ensure
you have an OS environment value (akin to Django's ``DJANGO_SETTINGS``) in
this format::

  export PYRAMID_SETTINGS=/place/to/development.ini#myapp

``/place/to/development.ini`` is the full path to the ini file. ``myapp`` is
the section name in the config file that represents your app
(e.g. ``[app:myapp]``).  In the above example, your application will refuse
to start without this environment variable being present.
