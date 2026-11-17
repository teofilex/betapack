import '../assets/style.css'
import { createPinia } from 'pinia'
import { createHead } from '@unhead/vue/client'
import { inject } from '@vercel/analytics'
import { app } from './app'
import router from './router'

// PrimeVue i primeicons su samo za admin: ucitavaju se uz /admin rute (admin/setup.js)
const head = createHead()

app.use(head)
app.use(createPinia())
app.use(router)

// Vercel Web Analytics: prati i promene ruta u SPA-u (history API)
inject()

app.mount('#app')
