import { defineStore } from "pinia";
import { api } from "@/services/api";
import { storage } from "@/utils/storage";

export const useAuthStore = defineStore('auth', {
    // Pocetno stanje je prazno (isto kao u prerenderu); sesija iz localStorage-a se
    // ucitava pozivom loadFromStorage() pre ili posle montiranja (vidi main.js)
    state: () => ({
        user: null,
        accessToken: null,
        refreshToken: null
    }),

    getters: {
        isAuthenticated: (state) => !!state.accessToken,
        isAdmin: (state) => state.user?.is_staff || false
    },

    actions: {
        loadFromStorage() {
            try {
                this.user = JSON.parse(storage.get('user')) || null
            } catch {
                this.user = null
            }
            this.accessToken = storage.get('access') || null
            this.refreshToken = storage.get('refresh') || null
        },

        async login(username, password) {
            try {
                const response = await api.post('/auth/login/', {
                    username, password
                })

                this.accessToken = response.data.access
                this.refreshToken = response.data.refresh

                storage.set('access', this.accessToken)
                storage.set('refresh', this.refreshToken)

                await this.fetchUser()

                // OVDE nakon fetchUser-a imamo user objekt → sacuvaj ga
                storage.set("user", JSON.stringify(this.user))

                return true

            } catch (error) {
                console.error('login failed:', error)
                return false
            }
        },

        async fetchUser() {
            try {
                const response = await api.get('/auth/user/', {
                    headers: {
                        Authorization: `Bearer ${this.accessToken}`,
                    },
                })

                this.user = response.data

            } catch (error) {
                console.error('fetch user failed:', error)
            }
        },

        async refreshAccessToken() {
            if (!this.refreshToken) {
                return false
            }

            try {
                const response = await api.post('/auth/refresh/', {
                    refresh: this.refreshToken
                })

                this.accessToken = response.data.access
                storage.set('access', this.accessToken)

                if (response.data.refresh) {
                    this.refreshToken = response.data.refresh
                    storage.set('refresh', this.refreshToken)
                }

                return true
            } catch (error) {
                console.error('refresh token failed:', error)
                this.logout()
                return false
            }
        },

        async initialize() {
            // Ako korisnik nije ulogovan, ne radi ništa
            if (!this.accessToken || !this.refreshToken) {
                return false
            }

            // Proveri da li je access token validan tako što ćeš pokušati da dobiješ korisnika
            try {
                await this.fetchUser()
                // Ako je uspešno, token je validan
                return true
            } catch (error) {
                // Ako je token istekao, pokušaj da ga osvežiš
                if (error.response?.status === 401) {
                    const refreshed = await this.refreshAccessToken()
                    if (refreshed) {
                        // Pokušaj ponovo da dobiješ korisnika sa novim tokenom
                        await this.fetchUser()
                        return true
                    }
                }
                return false
            }
        },

        logout() {
            this.user = null
            this.accessToken = null
            this.refreshToken = null
            storage.remove('access')
            storage.remove('refresh')
            storage.remove('user')
        },
    },
})
