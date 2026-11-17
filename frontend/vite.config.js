import { fileURLToPath, URL } from 'node:url'

import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import vueDevTools from 'vite-plugin-vue-devtools'
import tailwindcss from '@tailwindcss/vite'

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
