Serving File Content Dynamically
--------------------------------

Usually you'll use a static view (via "config.add_static_view") to
serve file content that lives on the filesystem.  But sometimes files need to
be composed and read from a nonstatic area, or composed on the fly by view
code and served out (for example, a view callable might construct and return
a PDF file or an image).

By way of example, here's a Pyramid application which serves a single static
file (a jpeg) when the URL ``/test.jpg`` is executed::

    from pyramid.view import view_config
    from pyramid.config import Configurator
    from pyramid.response import FileResponse
    from paste.httpserver import serve

    @view_config(route_name='jpg')
    def test_page(request):
        response = FileResponse(
            '/home/chrism/groundhog1.jpg', 
            request=request,
            content_type='image/jpeg'
            )
        return response

    if __name__ == '__main__':
        config = Configurator()
        config.add_route('jpg', '/test.jpg')
        config.scan('__main__')
        serve(config.make_wsgi_app())

Basically, use a ``pyramid.response.FileResponse`` as the response object and
return it.  Note that the ``request`` and ``content_type`` arguments are
optional.  If ``request`` is not supplied, any ``wsgi.file_wrapper``
optimization supplied by your WSGI server will not be used when serving the
file.  If ``content_type`` is not supplied, it will be guessed using the
``mimetypes`` module (which uses the file extension); if it cannot be guessed
successfully, the ``application/octet-stream`` content type will be used.

Serving a Single File from the Root
-----------------------------------

If you need to serve a single file such as ``/robots.txt`` or
``/favicon.ico`` that *must* be served from the root, you cannot use a
static view to do it, as static views cannot serve files from the
root (a static view must have a nonempty prefix such as ``/static``).  To
work around this limitation, create views "by hand" that serve up the raw
file data.  Below is an example of creating two views: one serves up a
``/favicon.ico``, the other serves up ``/robots.txt``.

At startup time, both files are read into memory from files on disk using
plain Python.  A Response object is created for each.  This response is
served by a view which hooks up the static file's URL.

.. code-block::  python
   :linenos:

   # this module = myapp.views

   import os

   from pyramid.response import Response
   from pyramid.view import view_config

   # _here = /app/location/myapp

   _here = os.path.dirname(__file__)

   # _icon = /app/location/myapp/static/favicon.ico

   _icon = open(os.path.join(
                _here, 'static', 'favicon.ico')).read()
   _fi_response = Response(content_type='image/x-icon', 
                           body=_icon)

   # _robots = /app/location/myapp/static/robots.txt

   _robots = open(os.path.join(
                  _here, 'static', 'robots.txt')).read()
   _robots_response = Response(content_type='text/plain',
                               body=_robots)

   @view_config(name='favicon.ico')
   def favicon_view(context, request):
       return _fi_response

   @view_config(name='robots.txt')
   def robotstxt_view(context, request):
       return _robots_response

Root-Relative Custom Static View (URL Dispatch Only)
----------------------------------------------------

The :class:`pyramid.static.static_view` helper class generates a Pyramid view
callable.  This view callable can serve static assets from a directory.  An
instance of this class is actually used by the
:meth:`pyramid.config.Configurator.add_static_view` configuration method, so
its behavior is almost exactly the same once it's configured.

.. warning:: 

   The following example *will not work* for applications that use
   traversal, it will only work if you use URL dispatch
   exclusively.  The root-relative route we'll be registering will always be
   matched before traversal takes place, subverting any views registered via
   ``add_view`` (at least those without a ``route_name``).  A
   :class:`pyramid.static.static_view` cannot be made root-relative when you
   use traversal.

To serve files within a directory located on your filesystem at
``/path/to/static/dir`` as the result of a "catchall" route hanging from the
root that exists at the end of your routing table, create an instance of the
:class:`pyramid.static.static_view` class inside a ``static.py`` file in your
application root as below::

   from pyramid.static import static_view
   www = static_view('/path/to/static/dir', use_subpath=True)

.. note:: For better cross-system flexibility, use an asset
   specification as the argument to :class:`pyramid.static.static_view`
   instead of a physical absolute filesystem path, e.g. ``mypackage:static``
   instead of ``/path/to/mypackage/static``.

Subsequently, you may wire the files that are served by this view up to be
accessible as ``/<filename>`` using a configuration method in your
application's startup code::

   # .. every other add_route and/or add_handler declaration should come
   # before this one, as it will, by default, catch all requests

   config.add_route('catchall_static', '/*subpath', 'myapp.static.www')

The special name ``*subpath`` above is used by the
:class:`pyramid.static.static_view` view callable to signify the path of the
file relative to the directory you're serving.

Basic File Uploads
------------------

There are two parts necessary for handling file uploads.  The first is to
make sure you have a form that's been setup correctly to accept files.  This
means adding ``enctype`` attribute to your ``form`` element with the value of
``multipart/form-data``.  A very simple example would be a form that accepts
an mp3 file.  Notice we've setup the form as previously explained and also
added an ``input`` element of the ``file`` type.

.. code-block:: html
    :linenos:

    <form action="/store_mp3_view" method="post" accept-charset="utf-8"
          enctype="multipart/form-data">

        <label for="mp3">Mp3</label>
        <input id="mp3" name="mp3" type="file" value="" />

        <input type="submit" value="submit" />
    </form>

The second part is handling the file upload in your view callable (above,
assumed to answer on ``/store_mp3_view``).  The uploaded file is added to the
request object as a ``cgi.FieldStorage`` object accessible through the
``request.POST`` multidict.  The two properties we're interested in are the
``file`` and ``filename`` and we'll use those to write the file to disk::

    import os
    import shutil

    from pyramid.response import Response

    def store_mp3_view(request):
        # ``filename`` contains the name of the file in string format.
        #
        # WARNING: Internet Explorer is known to send an absolute file
        # *path* as the filename.  This example is naive; it trusts
        # user input.
        filename = request.POST['mp3'].filename

        # ``input_file`` contains the actual file data which needs to be
        # stored somewhere.
        input_file = request.POST['mp3'].file

        # Using the filename like this without cleaning it is very
        # insecure so please keep that in mind when writing your own
        # file handling.
        file_path = os.path.join('/tmp', filename)
        with open(file_path, 'wb') as output_file:
            shutil.copyfileobj(input_file, output_file)

        return Response('OK')


Building JavaScript/CSS assets via Pyramid application command
--------------------------------------------------------------

Modern applications often require some kind of build step required for production static assets
bundling.
This recipe illustrates how to build a command that can help with this task, it also tries to
adhere some requirements:

* Frontend source code can be distributed as python packages
* Source code repository/site-packages is not being written to during building
* Make it possible to provide plugin architecture within your application with multiple
  static packages
* Application home directory as the destination of build process for easy HTTP serving by Apache
  or Nginx.
* Flexible - you can use Yarn, Webpack, Rollup or other favourite frontend tooling for JS/CSS
  to compose bigger pipelines

First we need to tell Pyramid it will have to serve static content from additional build directory
(this is useful for development, in production this will be often handled by Nginx).

In ini/configuration add locations for build process:

.. code-block:: ini

    # build result directory
    statics.dir = %(here)s/static
    # intermediate directory for build process
    statics.build_dir = %(here)s/static_build

In routing section of application:

.. code-block:: py3

    import pathlib
    # after default static view add bundled static support
    config.add_static_view(
        "static_bundled", "static_bundled", cache_max_age=1
    )
    path = pathlib.Path(config.registry.settings["statics.dir"])
    # create the directory if missing otherwise pyramid will not start
    path.mkdir(exist_ok=True)
    config.override_asset(
        to_override="yourapp:static_bundled/",
        override_with=config.registry.settings["statics.dir"],
    )

Now in your templates you can reference your build artifacts.

.. code-block:: html

    <script src="{{ request.static_url('yourapp:static_bundled/some-package.min.js') }}"></script>

In your application create a file ``build_static_assets.py``, for example in ``app/scripts`` package.

.. code-block:: py3

    import argparse
    import io
    import json
    import logging
    import os
    import pathlib
    import shutil
    import subprocess
    import sys

    import pkg_resources
    from pyramid.paster import bootstrap, setup_logging

    log = logging.getLogger(__name__)


    def build_assets(registry, *cmd_args, **cmd_kwargs):
        settings = registry.settings
        build_dir = settings["statics.build_dir"]
        try:
            shutil.rmtree(build_dir)
        except FileNotFoundError as exc:
            log.warning(exc)
        # your application frontend source code and configuration directory
        # usually the containing main package.json
        assets_path = os.path.abspath(
            pkg_resources.resource_filename("yourapp", "../../frontend")
        )
        # copy package static sources to temporary build dir
        shutil.copytree(
            assets_path,
            build_dir,
            ignore=shutil.ignore_patterns(
                "node_modules", "bower_components", "__pycache__"
            ),
        )
        # configuration files/variables can be picked up by webpack/rollup/gulp
        os.environ["FRONTEND_ASSSET_ROOT_DIR"] = settings["statics.dir"]
        worker_config = {'frontendAssetRootDir': settings["statics.dir"]}
        with io.open(pathlib.Path(build_dir) / 'pyramid_config.json', 'w') as f:
            f.write(json.dumps(worker_config))
        # your actual build commands to execute:

        # download all requirements
        subprocess.run(["yarn"], env=os.environ, cwd=build_dir, check=True)
        # run build process
        subprocess.run(["yarn", "build"], env=os.environ, cwd=build_dir, check=True)


    def parse_args(argv):
        parser = argparse.ArgumentParser()
        parser.add_argument("config_uri", help="Configuration file, e.g., development.ini")
        return parser.parse_args(argv[1:])


    def main(argv=sys.argv):
        args = parse_args(argv)
        setup_logging(args.config_uri)
        env = bootstrap(args.config_uri)
        request = env["request"]
        build_assets(request.registry)

Finally, tell package tools to create shell script you can use to start the process.

.. code-block:: py3

    setup(
        name='yourapp',
        ....
        install_requires=requires,
        entry_points={
            'paste.app_factory': [
                'main = channelstream_landing:main',
            ],
            'console_scripts': [
                'yourapp_build_statics = yourapp.scripts.build_static_assets:main',
            ]
        },
    )

Run ``pip install -e`` . again to register the console script.

Now you can configure/run your frontend pipeline with webpack/gulp/rollup or other solution.

If you run the command:

.. code-block:: bash

    yourapp_build_statics development.ini

It will start the build process and its result will be a fresh ``static`` directory in same
location that ini file was, it will contain all the build process artifacts ready for serving.

You can retrieve variables from pyramid application in your node build configuration files:

.. code-block:: javascript

    destinationRootDir = process.env.FRONTEND_ASSSET_ROOT_DIR

or you can load generated ``pyramid_config.json`` file in your node script for additional
information.
