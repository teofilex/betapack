import axios from 'axios'
import { storage } from '@/utils/storage'

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000/api'

export const api = axios.create({
    baseURL: API_BASE_URL
})

api.interceptors.request.use(
    (config) => {
        const token = storage.get('access')
        if (token) {
            config.headers.Authorization = `Bearer ${token}`
        }
        return config
    },
    (error) => Promise.reject(error)
)

let refreshPromise = null

// Kada osvezavanje tokena ne uspe, zahtev se ponavlja bez Authorization
// zaglavlja. Bez toga bi istekao token iz admin sesije obarao i javne
// endpointe, pa bi kupcu ponuda ostala prazna. Za zasticene endpointe
// ovaj pokusaj vrati 401, sto je i ispravno — korisnik ide na login.
const retryBezTokena = (request) => {
    storage.remove('access')
    storage.remove('refresh')
    if (request.headers) {
        delete request.headers.Authorization
    }
    return api.request(request)
}

api.interceptors.response.use(
    (response) => response,
    async (error) => {
        const originalRequest = error.config
        const isAuthRefresh = originalRequest?.url?.includes('/auth/refresh/')
        const isExpiredToken =
            error.response?.status === 401 &&
            error.response?.data?.code === 'token_not_valid'

        if (!isExpiredToken || isAuthRefresh || originalRequest?._retry) {
            return Promise.reject(error)
        }

        originalRequest._retry = true

        try {
            if (!refreshPromise) {
                const { useAuthStore } = await import('@/store/auth')
                const authStore = useAuthStore()
                refreshPromise = authStore.refreshAccessToken().finally(() => {
                    refreshPromise = null
                })
            }

            const refreshed = await refreshPromise
            if (!refreshed) {
                return retryBezTokena(originalRequest)
            }

            const token = storage.get('access')
            if (token) {
                originalRequest.headers.Authorization = `Bearer ${token}`
            }

            return api.request(originalRequest)
        } catch (refreshError) {
            return retryBezTokena(originalRequest)
        }
    }
)
