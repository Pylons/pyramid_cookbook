import pathlib


def includeme(config):
    config.add_static_view('static', 'static', cache_max_age=3600)
    config.add_route('home', '/')
    # after default static view add bundled static support
    config.add_static_view(
        "static_bundled", "static_bundled", cache_max_age=1
    )
    path = pathlib.Path(config.registry.settings["statics.dir"])
    # create the directory if missing otherwise pyramid will not start
    path.mkdir(exist_ok=True)
    config.override_asset(
        to_override="bundling_example:static_bundled/",
        override_with=config.registry.settings["statics.dir"],
    )
