const esbuild = require('esbuild')
const sassPlugin = require('esbuild-plugin-sass')
const vuePlugin  = require('esbuild-plugin-vue3')

esbuild.build({
  entryPoints: ['./js/vue/apps.js'],
  bundle: true,
  watch: true,
  outfile: 'js/vue.apps.bundle.js',
  plugins: [sassPlugin(), vuePlugin()],
}).then( server => {
  console.log(server)
}).catch((e) => console.error(e.message))
