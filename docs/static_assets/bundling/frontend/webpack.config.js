require('style-loader');
require('css-loader');
var CopyWebpackPlugin = require('copy-webpack-plugin');
const MiniCssExtractPlugin = require("mini-css-extract-plugin");
var path = require('path');

const projectName = 'channelstream_landing';
let devDestinationDir = path.join(__dirname, '..', 'static');

destinationRootDir = process.env.FRONTEND_ASSSET_ROOT_DIR || devDestinationDir;
console.log('Root directory:', destinationRootDir);
outputDir = path.resolve(destinationRootDir);

module.exports = {
    // Tell Webpack which file kicks off our app.
    entry: {
        main: path.resolve(__dirname, 'src/index.js'),
        sass: path.resolve(__dirname, 'src/sass.js')
    },
    output: {
        filename: 'bundle-[name].js',
        path: outputDir
    },
    // Tell Webpack which directories to look in to resolve import statements.
    // Normally Webpack will look in node_modules by default but since we’re overriding
    // the property we’ll need to tell it to look there in addition to the
    // bower_components folder.
    resolve: {
        modules: [
            path.resolve(__dirname, 'node_modules')
        ]
    },
    // These rules tell Webpack how to process different module types.
    // Remember, *everything* is a module in Webpack. That includes
    // CSS, and (thanks to our loader) HTML.
    module: {
        rules: [
            {
                test: /\.scss$/,
                use: [
                    MiniCssExtractPlugin.loader,
                    "css-loader", // translates CSS into CommonJS
                    "sass-loader" // compiles Sass to CSS
                ]
            }
        ]
    },
    plugins: [
        new MiniCssExtractPlugin({
            // Options similar to the same options in webpackOptions.output
            // both options are optional
            filename: "css/main.css"
        }),
        // Polyfills
        // This plugin will copy files over to ‘./dist’ without transforming them.
        // That's important because the custom-elements-es5-adapter.js MUST
        // remain in ES2015. We’ll talk about this a bit later :)
        new CopyWebpackPlugin([            {
            from: '**/*.js',
            context: path.resolve(__dirname, 'node_modules/@webcomponents/webcomponentsjs'),
            to: path.join(outputDir, 'node_modules/@webcomponents/webcomponentsjs')
        }])
    ]
};
