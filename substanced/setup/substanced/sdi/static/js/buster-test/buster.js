
var config = module.exports;

config["sdi.grid.remotemodel"] = {
    rootPath: "../",
    environment: "browser",
    libs: [
        "buster-test/testlib/jquery-1.7.2.js"
    ],
    sources: [
        "sdi.grid.remotemodel.js"
    ],
    tests: [
        "buster-test/sdi.grid.remotemodel-test.js"
    ]
};
