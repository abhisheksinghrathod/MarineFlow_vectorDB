const path = require("path");
const { CleanWebpackPlugin } = require("clean-webpack-plugin");
const BundleTracker = require("webpack-bundle-tracker");

module.exports = {
  entry: "./src/index.js",
  output: {
    path: path.resolve(__dirname, "./static/"),
    filename: "bundle.js",
    publicPath: "/static/",
  },
  plugins: [
    new CleanWebpackPlugin(),
    new BundleTracker({ filename: "./webpack-stats.json" }),
  ],
  module: {
    rules: [
      {
        test: /\.js$/,
        exclude: /node_modules/,
        use: "babel-loader",
      },
      {
        test: /\.css$/i,
        use: ["style-loader", "css-loader"],
      },
    ],
  },
  mode: "development", // change to "production" for deployment
};