import { defineStore } from "pinia";
import axios from "axios";

// Production API URL
const API_URL = import.meta.env.VITE_API_BASE_URL?.replace('/api', '') || 'http://127.0.0.1:8000'

export const useAuthStore = defineStore('auth', {
    state: () => ({
        user: JSON.parse(localStorage.getItem("user")) || null,
        accessToken: localStorage.getItem('access') || null,
        refreshToken: localStorage.getItem('refresh') || null
    }),

    getters: {
        isAuthenticated: (state) => !!state.accessToken,
        isAdmin: (state) => state.user?.is_staff || false
    },

    actions: {
        async login(username, password) {
            try {
                const response = await axios.post(`${API_URL}/api/auth/login/`, {
                    username, password
                })

                this.accessToken = response.data.access
                this.refreshToken = response.data.refresh

                localStorage.setItem('access', this.accessToken)
                localStorage.setItem('refresh', this.refreshToken)

                await this.fetchUser()

                // OVDE nakon fetchUser-a imamo user objekt → sacuvaj ga
                localStorage.setItem("user", JSON.stringify(this.user))

                return true

            } catch (error) {
                console.error('login failed:', error)
                return false
            }
        },

        async fetchUser() {
            try {
                const response = await axios.get(`${API_URL}/api/auth/user/`, {
                    headers: {
                        Authorization: `Bearer ${this.accessToken}`,
                    },
                })

                this.user = response.data

            } catch (error) {
                console.error('fetch user failed:', error)
            }
        },

        async refreshToken() {
            if (!this.refreshToken) {
                return false
            }

            try {
                const response = await axios.post(`${API_URL}/api/auth/refresh/`, {
                    refresh: this.refreshToken
                })

                this.accessToken = response.data.access
                localStorage.setItem('access', this.accessToken)

                // Ako refresh token postoji u odgovoru, ažuriraj ga
                if (response.data.refresh) {
                    this.refreshToken = response.data.refresh
                    localStorage.setItem('refresh', this.refreshToken)
                }

                return true
            } catch (error) {
                console.error('refresh token failed:', error)
                // Ako refresh token nije validan, odloguj korisnika
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
                    const refreshed = await this.refreshToken()
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
            localStorage.removeItem('access')
            localStorage.removeItem('refresh')
            localStorage.removeItem('user')
        },
    },
})
