import axios from 'axios'

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000/api'

export const api = axios.create({
    baseURL: API_BASE_URL
})

api.interceptors.request.use(
    (config) => {
        const token = localStorage.getItem('access')
        if (token) {
            config.headers.Authorization = `Bearer ${token}`
        }
        return config
    },
    (error) => Promise.reject(error)
)

let refreshPromise = null

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
                return Promise.reject(error)
            }

            const token = localStorage.getItem('access')
            if (token) {
                originalRequest.headers.Authorization = `Bearer ${token}`
            }

            return api.request(originalRequest)
        } catch (refreshError) {
            return Promise.reject(refreshError)
        }
    }
)
