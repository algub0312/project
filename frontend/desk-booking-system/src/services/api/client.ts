import axios from 'axios'
import type { InternalAxiosRequestConfig } from 'axios'
import { useAuthStore } from '@/stores/auth.ts'
import { useSnackbarStore } from '@/stores/snackbar.ts'

const apiClient = axios.create({
  baseURL: 'http://localhost:8080', // Gateway port
  timeout: 15000,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Request interceptor: attach token
apiClient.interceptors.request.use((config: InternalAxiosRequestConfig) => {
  const auth = useAuthStore()
  const token = auth.token
  if (token && config.headers) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

// Response interceptor: on 401 try to refresh and retry once
apiClient.interceptors.response.use(
  (response) => response,
  async (error) => {
    const auth = useAuthStore()
    const snackbar = useSnackbarStore()
    const originalRequest = error.config

    // Handle network errors (backend offline, timeout, etc.)
    if (!error.response) {
      snackbar.error('Cannot reach server. Please try again.')
      return Promise.reject(error)
    }

    const status = error.response.status

    if (status === 401 && !originalRequest._retry) {
      // unauthorized
      originalRequest._retry = true

      const refreshed = await auth.refreshTokenIfNeeded()

      if (refreshed && auth.token) {
        // Retry request with new token
        originalRequest.headers = {
          ...originalRequest.headers,
          Authorization: `Bearer ${auth.token}`,
        }

        return apiClient(originalRequest)
      }

      // Refresh failed → logout happened
      snackbar.warning('Your session has expired.')
      return Promise.reject(error)
    }

    switch (status) {
      case 400:
        // Bad Request
        snackbar.error(error.response.data?.message || 'Bad request.')
        break
      case 403:
        // Forbidden
        snackbar.error('You do not have permission to perform this action.')
        break
      case 404:
        // Not Found
        snackbar.error('The requested resource was not found.')
        break
      case 500:
        // Internal Server Error
        snackbar.error('An internal server error occurred. Please try again later.')
        break
      default:
        // Other errors
        snackbar.error(
          error.response.data?.message || `An error occurred (status code: ${status}).`,
        )
    }
    return Promise.reject(error)
  },
)

export default apiClient
