const esbuild = require('esbuild')
const sassPlugin = require('esbuild-plugin-sass')
const vuePlugin  = require('esbuild-plugin-vue3')

esbuild.build({
  entryPoints: ['./js/vue/apps.js'],
  bundle: true,
  minify: true,
  outfile: '/srv/static/js/vue.apps.bundle.js',
  watch: {
    onRebuild(error, result) {
      if (error) console.error('watch build failed:', error)
      else { 
        console.log('watch build succeeded:', result)
        // HERE: somehow restart the server from here, e.g., by sending a signal that you trap and react to inside the server.
      }
    },
  },
  sourcemap: true,
  plugins: [sassPlugin(), vuePlugin()],
}).then(result => {
  console.log('watching...')
}).catch((e) => console.error(e.message))
