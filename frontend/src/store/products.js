import { defineStore } from 'pinia'
import { api } from '@/services/api'

export const useProductStore = defineStore('products', {
    state: () => ({
        products: [],
        loading: false,
        currentStore: 'steel',
        // Podaci stigli iz prerenderovane strane (build-time); ShopView ih prvi put
        // koristi bez spinnera, a sveze podatke dovlaci tiho posle montiranja.
        prerendered: false,
        // Proizvod sa prerenderovane strane proizvoda (isti oblik kao odgovor API-ja)
        prerenderedProduct: null
    }),

    getters: {
        filteredProducts: (state) => (filters) => {
            let res = state.products.filter(p => p.store === state.currentStore || !p.store)

            if (filters.category) {
                res = res.filter(p => p.category === filters.category)
            }

            if (filters.search) {
                const q = filters.search.toLowerCase()
                res = res.filter(p =>
                    p.name.toLowerCase().includes(q) ||
                    p.description.toLowerCase().includes(q) ||
                    p.category_name.toLowerCase().includes(q)
                )
            }

            if (filters.minPrice) {
                res = res.filter(p => parseFloat(p.current_price) >= filters.minPrice)
            }
            if (filters.maxPrice) {
                res = res.filter(p => parseFloat(p.current_price) <= filters.maxPrice)
            }

            if (filters.showOnlyOnSale) {
                res = res.filter(p => p.on_sale)
            }

            return res
        }
    },

    actions: {
        // silent: osvezavanje bez spinnera (lista se samo zameni kad stignu podaci)
        async fetchProducts(store = 'steel', { silent = false } = {}) {
            if (!silent) this.loading = true
            this.currentStore = store
            try {
                // Bez cache-bustera: server kesira listu i poništava kes pri svakoj izmeni
                // proizvoda, pa je odgovor uvek svez.
                const res = await api.get('products/', {
                    params: { store }
                })
                this.products = res.data
            } finally {
                if (!silent) this.loading = false
            }
        }
    }
})
