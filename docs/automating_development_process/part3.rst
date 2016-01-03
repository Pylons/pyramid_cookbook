How it works pyramid_starter_seed
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

Note well that if you want to integrate a Pyramid application with the 
Yeoman workflow you can choose different strategies. 
So the pyramid_starter_seed's way is just one of the possible 
implementations.


.ini configurations
===================
Production vs development .ini configurations.

Production:

.. code-block:: ini

    [app:main]
    use = egg:pyramid_starter_seed

    PRODUCTION = true
    minify = dist

    ...

Development:

.. code-block:: ini

    [app:main]
    use = egg:pyramid_starter_seed
    
    PRODUCTION = false
    minify = app
    ...

View callables
==============

The view callable gets a different renderer depending on the production 
vs development settings:

.. code-block:: python

    from pyramid.view import view_config
    
    @view_config(route_name='home', renderer='webapp/%s/index.html')
    def my_view(request):
        return {'project': 'pyramid_starter_seed'}

Since there is no .html renderer, pyramid_starter_seed register a custom 
Pyramid renderer based on ZPT/Chameleon. 
See `.html renderer <https://github.com/davidemoro/pyramid_starter_seed/blob/master/pyramid_starter_seed/renderer.py>`_

Templates
=========

Css and javascript
------------------

.. code-block:: html

    <tal:production tal:condition="production">
        <script src="${request.static_url('pyramid_starter_seed:webapp/%s/scripts/plugins.js' % minify)}">
        </script>
    </tal:production>
    <tal:not_production tal:condition="not:production">
        <script src="${request.static_url('pyramid_starter_seed:webapp/%s/bower_components/bootstrap/js/alert.js' % minify)}">
        </script>
        <script src="${request.static_url('pyramid_starter_seed:webapp/%s/bower_components/bootstrap/js/dropdown.js' % minify)}">
        </script>
    </tal:not_production>
    <!-- build:js scripts/plugins.js -->
    <tal:comment replace="nothing">
        <!-- DO NOT REMOVE this block (minifier) -->
        <script src="./bower_components/bootstrap/js/alert.js"></script>
        <script src="./bower_components/bootstrap/js/dropdown.js"></script>
    </tal:comment>
    <!-- endbuild -->

Note: the above verbose syntax could be avoided hacking with the 
grunt-bridge task. 
See `grunt-bridge <https://github.com/palazzem/grunt-bridge>`_.

Images
------

.. code-block:: html

    <img class="logo img-responsive" 
         src="${request.static_url('pyramid_starter_seed:webapp/%s/images/pyramid.png' % minify)}"
         alt="pyramid web framework" />


How to fork pyramid_starter_seed
================================

Fetch pyramid_starter_seed, personalize it and then clone it!

Pyramid starter seed can be fetched, personalized and released with another 
name. So other developer can bootstrap, build, release and distribute their 
own starter templates without having to write a new package template 
generator. For example you could create a more opinionated starter seed 
based on SQLAlchemy, ZODB nosql or powered by a javascript framework like 
AngularJS and so on.

The clone method should speed up the process of creation of new more 
evoluted packages based on Pyramid, also people that are not keen on 
writing their own reusable scaffold templates.

So if you want to release your own customized template based on 
pyramid_starter_seed you'll have to call a console script named 
pyramid_starter_seed_clone with the following syntax (obviously 
you'll have to call this command outside the root directory of 
pyramid_starter_seed):

.. code-block:: bash

    $ YOUR_VIRTUALENV_PYTHON_PATH/bin/pyramid_starter_seed_clone new_template

and you'll get as a result a perfect renamed clone new_template.

The clone console script it might not work in some corner cases just in case 
you choose a new package name that contains reserved words or the name of a 
dependency of your plugin, but it should be quite easy to fix by hand or 
improving the console script.
But if you provide tests you can check immediately if something went wrong 
during the cloning process and fix.

How pyramid_starter_seed works under the hood
=============================================

More details explained on the original article (part 3): 

- `How pyramid_starter_seed works under the hood <http://davidemoro.blogspot.com/2014/09/pyramid-starter-seed-yeoman-part-3.html>`_

