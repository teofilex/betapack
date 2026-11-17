// Podaci za prerender: izvrsava se samo u Node-u pri build-u (vite-ssg), nikad u browseru.
// Lista proizvoda i kategorija se dovlaci jednom po prodavnici, pa se koristi za sve strane.
// Ako API ne odgovori ili vrati prazno, baca gresku: build mora da padne, a ne da objavi
// sajt sa praznim stranama.
import axios from 'axios'

const API_URL = import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000/api'
const STORE_IDS = ['steel', 'ambalaza']
const ATTEMPTS = 3
const TIMEOUT_MS = 30000

const sleep = (ms) => new Promise((resolve) => setTimeout(resolve, ms))

async function getJson(path, params) {
  let lastError
  for (let attempt = 1; attempt <= ATTEMPTS; attempt++) {
    try {
      const res = await axios.get(`${API_URL}/${path}`, { params, timeout: TIMEOUT_MS })
      if (!Array.isArray(res.data)) {
        throw new Error('odgovor nije lista (primljeno: ' + typeof res.data + ')')
      }
      return res.data
    } catch (error) {
      lastError = error
      if (attempt < ATTEMPTS) await sleep(2000 * attempt)
    }
  }
  const reason = lastError.response ? `HTTP ${lastError.response.status}` : lastError.message
  throw new Error(
    `[prerender] API nije dostupan ili vraca neispravan odgovor: ${API_URL}/${path}` +
    `${params ? '?' + new URLSearchParams(params) : ''} (${reason}). ` +
    'Build je prekinut da se ne bi objavio sajt sa praznim stranama.'
  )
}

let cache = null

// { steel: { products, categories }, ambalaza: { ... } }
export function loadCatalog() {
  if (!cache) {
    cache = (async () => {
      const entries = await Promise.all(STORE_IDS.map(async (store) => {
        const [products, categories] = await Promise.all([
          getJson('products/', { store }),
          getJson('categories/', { store }),
        ])
        if (products.length === 0 || categories.length === 0) {
          throw new Error(
            `[prerender] Prodavnica "${store}" vratila ${products.length} proizvoda i ` +
            `${categories.length} kategorija. Build je prekinut da se ne bi objavio sajt sa praznim stranama.`
          )
        }
        const unusable = products.filter((p) => !p.slug || !p.name)
        if (unusable.length > 0) {
          throw new Error(
            `[prerender] Prodavnica "${store}": ${unusable.length} proizvoda bez slug-a ili naziva ` +
            `(npr. id ${unusable[0].id}). Build je prekinut.`
          )
        }
        return [store, { products, categories }]
      }))
      return Object.fromEntries(entries)
    })()
    // Neuspeh se ne kesira: sledeci poziv bi probao ponovo, ali build ionako staje
    cache.catch(() => { cache = null })
  }
  return cache
}

// Sve javne strane koje se prerenderuju (kategorije preko ?category=N nisu zasebni HTML-ovi)
export async function prerenderPaths() {
  const catalog = await loadCatalog()
  const paths = ['/', '/404']
  for (const store of STORE_IDS) {
    paths.push(`/${store}`, `/${store}/o-nama`, `/${store}/kontakt`)
    for (const product of catalog[store].products) {
      paths.push(`/${store}/proizvod/${product.slug}`)
    }
  }
  return paths
}

// Postavlja u pinia podatke koje strana na putanji `to` treba za iscrtavanje
export async function fillStores(to, { productStore, categoryStore }) {
  const store = to.meta?.store
  if (!store) return
  const catalog = (await loadCatalog())[store]

  if (to.name === `${store}-shop`) {
    productStore.products = catalog.products
    productStore.currentStore = store
    productStore.prerendered = true
    categoryStore.categories = catalog.categories
    categoryStore.currentStore = store
  } else if (to.name === `${store}-product-detail`) {
    const key = String(to.params.slugOrId)
    const product = catalog.products.find((p) => p.slug === key || String(p.id) === key)
    if (!product) {
      throw new Error(`[prerender] Proizvod "${key}" ne postoji u prodavnici "${store}".`)
    }
    productStore.prerenderedProduct = product
  }
}
