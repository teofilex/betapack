import '../assets/style.css'
import { ViteSSG } from 'vite-ssg'
import { createPinia } from 'pinia'
import { inject } from '@vercel/analytics'
import App from './App.vue'
import { routes, scrollBehavior, installRouterGuards } from './router'
import { useProductStore } from './store/products'
import { useCategoryStore } from './store/categories'
import { useCartStore } from './store/cart'
import { useAuthStore } from './store/auth'

// PrimeVue i primeicons su samo za admin: ucitavaju se uz /admin rute (admin/setup.js)

// Javne strane su prerenderovane (vite-ssg): server vraca gotov HTML, a Vue ga preuzima
// (hidracija). Strane koje nisu prerenderovane (korpa, naplata, admin, proizvod dodat posle
// poslednjeg build-a) stizu kao prazna ljuska (spa.html) i iscrtavaju se u browseru.
function isPrerenderedDocument() {
  if (typeof window === 'undefined') return false
  const root = document.getElementById('app')
  return !!root?.hasAttribute('data-server-rendered') && !!window.__INITIAL_STATE__
}

function canHydrate() {
  if (!isPrerenderedDocument()) return false
  // /steel?category=N: HTML je prerenderovan za /steel (svi proizvodi), a strana sa
  // kategorijom prikazuje drugaciju listu. Ne hidrira se nego iscrtava iznova, sa istim
  // podacima iz stanja (bez spinnera).
  const isShop = /^\/(steel|ambalaza)$/.test(location.pathname)
  return !(isShop && new URLSearchParams(location.search).has('category'))
}

export const createApp = ViteSSG(
  App,
  { routes, base: import.meta.env.BASE_URL, scrollBehavior },
  ({ app, router, initialState }) => {
    const pinia = createPinia()
    app.use(pinia)
    installRouterGuards(router, app)

    if (import.meta.env.SSR) {
      // Prerender: stanje se serijalizuje u HTML, a ruter pre iscrtavanja puni store-ove
      initialState.pinia = pinia.state.value
      router.beforeResolve(async (to) => {
        const { fillStores } = await import('./prerender/loadData')
        await fillStores(to, {
          productStore: useProductStore(pinia),
          categoryStore: useCategoryStore(pinia),
        })
      })
      return
    }

    pinia.state.value = initialState.pinia || {}

    // Korpa i prijava zive u localStorage-u, kojeg server nema. Prerenderovana strana se
    // hidrira sa praznim stanjem (isti DOM kao u HTML-u), pa se one ucitavaju odmah posle
    // montiranja (pre prvog crtanja na ekranu). Ostale strane ih ucitavaju pre rutera.
    const loadSession = () => {
      useCartStore(pinia).loadFromStorage()
      useAuthStore(pinia).loadFromStorage()
    }
    if (canHydrate()) {
      const mount = app.mount
      app.mount = (...args) => {
        const vm = mount(...args)
        loadSession()
        return vm
      }
    } else {
      loadSession()
    }

    // Vercel Web Analytics: prati i promene ruta u SPA-u (history API)
    inject()
  },
  {
    // Hidrira samo prerenderovana strana; prazna ljuska se iscrtava od nule
    get hydration() {
      return canHydrate()
    },
  }
)

// Spisak strana za prerender (vite-ssg ga cita iz ulaza); podaci dolaze sa API-ja
export async function includedRoutes() {
  const { prerenderPaths } = await import('./prerender/loadData')
  return prerenderPaths()
}
