import axios from 'axios'

// Use environment variable or default to local development
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000/api'

export const api = axios.create({
    baseURL: API_BASE_URL
})

// Add request interceptor to include auth token
api.interceptors.request.use(
    (config) => {
        const token = localStorage.getItem('access')
        if (token) {
            config.headers.Authorization = `Bearer ${token}`
        }
        return config
    },
    (error) => {
        return Promise.reject(error)
    }
)

// Add response interceptor to handle expired tokens
api.interceptors.response.use(
    (response) => response,
    (error) => {
        // Ako je 401 i razlog je expired token, obriši iz localStorage i retry bez tokena
        if (error.response?.status === 401 &&
            error.response?.data?.code === 'token_not_valid') {

            // Obriši expired token
            localStorage.removeItem('access')
            localStorage.removeItem('refresh')

            // Retry request bez Authorization header-a (za javne endpoint-e)
            const config = error.config
            delete config.headers.Authorization

            // Retry samo jednom (izbegni infinite loop)
            if (!config._retry) {
                config._retry = true
                return api.request(config)
            }
        }
        return Promise.reject(error)
    }
)
