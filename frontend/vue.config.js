const { defineConfig } = require('@vue/cli-service')
const path = require('path')

module.exports = defineConfig({
  transpileDependencies: true,
  devServer: {
    host: 'localhost',
    port: process.env.VUE_APP_PORT || 8080,
    https: process.env.VUE_APP_ENV === 'production' || process.env.VUE_APP_PROTOCOL === 'https',
    allowedHosts: [process.env.VUE_APP_DOMAIN || 'localhost']
  },
  css: {
    loaderOptions: {
      sass: {
        additionalData: `@use "@/assets/styles/variables" as *;`
      }
    }
  },
  configureWebpack: {
    resolve: {
      alias: {
        '@': path.resolve(__dirname, 'src')
      }
    }
  }
})
