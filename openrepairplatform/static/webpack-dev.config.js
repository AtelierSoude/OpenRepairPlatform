'use strict'
const path = require('path')
const glob = require('glob')
const { VueLoaderPlugin } = require('vue-loader')
const MiniCssExtractPlugin = require('mini-css-extract-plugin')

module.exports = {
  context: __dirname,
  watch: true,
  watchOptions: {
    aggregateTimeout: 100,
    poll: 100
  },
  entry: glob.sync('./js/modules/*.js'),
  mode: 'development',
  module: {
    rules: [
      {
        enforce: 'pre',
        test: /\.(js|vue)$/,
        loader: 'eslint-loader',
        exclude: /node_modules/
      },
      {
        test: /\.(ttf|woff|woff2|eot|svg)(\?v=[0-9]\.[0-9]\.[0-9])?$/,
        loader: 'file-loader',
        options: {
          name: '[name].[ext]',
          outputPath: '../webfonts'
        }
      },
      {
        test: /\.vue$/,
        use: 'vue-loader'
      },
      {
        test: /\.sass$/,
        use: [
          'vue-style-loader',
          MiniCssExtractPlugin.loader,
          'css-loader',
          {
            loader: 'sass-loader',
            options: {
              additionalData: '@import "./sass/base/_variables.sass"',
              sassOptions: {
                indentedSyntax: true
              }
            }
          }
        ]
      }
    ]
  },
  output: {
    path: path.resolve('./js/vue/'),
    filename: 'app.js',
    publicPath: '/static/js/vue/'
  },

  plugins: [
    new VueLoaderPlugin(),
    new MiniCssExtractPlugin({
      filename: '../../css/vue-app.css'
    })
  ],
  resolve: {
    modules: ['node_modules'],
    alias: {
      '@': path.resolve('./js/vue/')
    }
  }
}
