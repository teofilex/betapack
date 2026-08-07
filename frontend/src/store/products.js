import { defineStore } from 'pinia'
import { api } from '@/services/api'

export const useProductStore = defineStore('products', {
    state: () => ({
        products: [],
        loading: false,
        currentStore: 'steel'
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
        async fetchProducts(store = 'steel') {
            this.loading = true
            this.currentStore = store
            try {
                const res = await api.get('products/', {
                    params: { store, _: Date.now() }
                })
                this.products = res.data
            } finally {
                this.loading = false
            }
        }
    }
})
