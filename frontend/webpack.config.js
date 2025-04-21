module.exports = {
    mode: 'development',
    entry: './main.js',
    output: {
        filename: 'main.js',
        publicPath: 'dist/'
    },
    devtool: 'source-map',
    module: {
        rules: [
            {
                test: /\.js$/,
                enforce: 'pre',
                use: ['source-map-loader'],
            }
        ]
    }
};