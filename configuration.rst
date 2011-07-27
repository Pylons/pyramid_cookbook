.. _configuration:

Django-Style "settings.py" Configuration
----------------------------------------

If you enjoy accessing global configuration via import statemetns ala
Django's ``settings.py``, you can do something similar in Pyramid.

- Create a ``settings.py`` file in your application's package (for example,
  if your application is named "myapp", put it in the filesystem directory
  named ``myapp``; the one with an ``__init__.py`` in it.

- Add values to it at its top level.

For example:

.. code-block:: python

  # settings.py

  import pytz

  timezone = pytz('US/Eastern')

Then simply import the module into your application:

.. code-block:: python

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

Chaining Decorators
-------------------

Pyramid has a ``decorator=`` argument to its view configuration.  It accepts
a single decorator that will wrap the *mapped* view callable represented by
the view configuration.  That means that, no matter what the signature and
return value of the original view callable, the decorated view callable will
receive two arguments: ``context`` and ``request`` and will return a response
object:

.. code-block:: python

    # the decorator

    def decorator(view_callable):
        def inner(context, request):
            return view_callable(context, request)
        return inner

    # the view configuration

    @view_config(decorator=decorator, renderer='json')
    def myview(request):
        return {'a':1}

But the ``decorator`` argument only takes a single decorator.  What happens
if you want to use more than one decorator?  You can chain them together:

.. code-block:: python

    def combine(*decorators):
        def floo(view_callable):
            for decorator in decorators:
                view_callable = decorator(view_callable)
            return view_callable
        return floo

    def decorator1(view_callable):
        def inner(context, request):
            return view_callable(context, request)
        return inner

    def decorator2(view_callable):
        def inner(context, request):
            return view_callable(context, request)
        return inner

    def decorator3(view_callable):
        def inner(context, request):
            return view_callable(context, request)
        return inner

    alldecs = combine(decorator1, decorator2, decorator3)
    two_and_three = combine(decorator2, decorator3)
    one_and_three = combine(decorator1, decorator3)

    @view_config(decorator=alldecs, renderer='json')
    def myview(request):
        return {'a':1}
