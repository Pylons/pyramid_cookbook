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
        pkg_resources.resource_filename("bundling_example", "../../frontend")
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
