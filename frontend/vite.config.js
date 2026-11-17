import { fileURLToPath, URL } from 'node:url'
import fs from 'node:fs'
import path from 'node:path'

import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import vueDevTools from 'vite-plugin-vue-devtools'
import tailwindcss from '@tailwindcss/vite'

const outDir = fileURLToPath(new URL('./dist', import.meta.url))

// https://vite.dev/config/
export default defineConfig({
  plugins: [
    vue(),
    tailwindcss(),
    vueDevTools(),
  ],
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url))
    },
  },
  // Prerender javnih strana (vite-ssg): vidi src/main.js i src/prerender/loadData.js
  ssgOptions: {
    dirStyle: 'nested',
    // Bez ugradjivanja "kriticnog CSS-a": izgled i redosled ucitavanja ostaju kao do sada
    beastiesOptions: false,
    formatting: 'none',
    // Prazna ljuska bez prerenderovanog sadrzaja (spa.html): vercel.json je koristi za
    // strane koje nisu prerenderovane (korpa, naplata, admin, proizvod dodat posle
    // poslednjeg build-a). index.html posle build-a je prerenderovana pocetna.
    onBeforePageRender(route, indexHTML) {
      fs.writeFileSync(path.resolve(outDir, 'spa.html'), indexHTML)
    },
    // Strana 404: Vercel za nepostojecu adresu vraca /404.html sa statusom 404
    onFinished() {
      const nested = path.resolve(outDir, '404', 'index.html')
      fs.renameSync(nested, path.resolve(outDir, '404.html'))
      fs.rmdirSync(path.dirname(nested))
    },
  },
  build: {
    rollupOptions: {
      output: {
        // Jedan 'vendor' fajl za biblioteke koje koriste sve javne strane. One se retko
        // menjaju, pa ostaju u kesu pregledaca i posle objave nove verzije sajta.
        // Admin biblioteke (Chart.js, vuedraggable, PrimeVue) namerno NISU ovde:
        // ostaju uz lazy admin rute.
        manualChunks(id) {
          if (!id.includes('node_modules')) return undefined
          const publicLibs = [
            '/node_modules/vue/dist/vue.runtime.esm-bundler',
            '/node_modules/@vue/runtime-core/',
            '/node_modules/@vue/runtime-dom/',
            '/node_modules/@vue/reactivity/',
            '/node_modules/@vue/shared/',
            '/node_modules/vue-router/',
            '/node_modules/pinia/',
            '/node_modules/axios/',
            '/node_modules/@unhead/',
            '/node_modules/unhead/',
            '/node_modules/hookable/',
            '/node_modules/@vercel/analytics/',
          ]
          return publicLibs.some((lib) => id.includes(lib)) ? 'vendor' : undefined
        },
      },
    },
  },
})
