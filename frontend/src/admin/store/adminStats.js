import { defineStore } from 'pinia'
import { api } from '../../services/api'
import { useAuthStore } from '../../store/auth'

export const useAdminStatsStore = defineStore('adminStats', {
    state: () => ({
        categories: 0,
        subcategories: 0,
        products: 0,
        orders: 0,
        contactMessages: 0,
    }),

    actions: {
        async refresh() {
            const auth = useAuthStore()

            // Proveri da li je korisnik autentifikovan
            if (!auth.isAuthenticated || !auth.accessToken) {
                console.warn("Korisnik nije autentifikovan, preskačem osvežavanje brojača")
                return
            }

            try {
                const [cats, subs, prods, ords, msgs] = await Promise.all([
                    api.get('/categories/'),
                    api.get('/subcategories/'),
                    api.get('/products/'),
                    api.get('/orders/', {
                        headers: { Authorization: `Bearer ${auth.accessToken}` }
                    }),
                    api.get('/contact-messages/', {
                        headers: { Authorization: `Bearer ${auth.accessToken}` }
                    })
                ])

                this.categories = cats.data.length
                this.subcategories = subs.data.length
                this.products = prods.data.length
                this.orders = ords.data.length
                this.contactMessages = msgs.data.length


            } catch (e) {
                console.error("Greška pri učitavanju brojača:", e)
                // Ako je greška 401 (Unauthorized), token je verovatno istekao
                // Pokušaj da osvežiš token i ponovi poziv
                if (e.response?.status === 401) {
                    const refreshed = await auth.refreshToken()
                    if (refreshed) {
                        // Pokušaj ponovo
                        try {
                            const [cats, subs, prods, ords, msgs] = await Promise.all([
                                api.get('/categories/'),
                                api.get('/subcategories/'),
                                api.get('/products/'),
                                api.get('/orders/', {
                                    headers: { Authorization: `Bearer ${auth.accessToken}` }
                                }),
                                api.get('/contact-messages/', {
                                    headers: { Authorization: `Bearer ${auth.accessToken}` }
                                })
                            ])

                            this.categories = cats.data.length
                            this.subcategories = subs.data.length
                            this.products = prods.data.length
                            this.orders = ords.data.length
                            this.contactMessages = msgs.data.length
                        } catch (retryError) {
                            console.error("Greška pri ponovnom učitavanju brojača:", retryError)
                        }
                    }
                }
            }
        }
    }
})
