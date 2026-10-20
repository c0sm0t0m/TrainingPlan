/**
 * API client configuration and axios instance
 */
import axios from 'axios'

const isLocalHostname = (hostname: string): boolean => {
  return hostname === 'localhost' || hostname === '127.0.0.1' || hostname === '::1'
}

// Auto-detect API URL based on current hostname.
// If VITE_API_URL is explicitly set to localhost but app runs on NAS/IP/domain,
// ignore that env override to avoid broken auth/login calls.
const getApiBaseUrl = (): string => {
  const currentHostname = window.location.hostname
  const envUrl = import.meta.env.VITE_API_URL

  if (envUrl) {
    try {
      const envHostname = new URL(envUrl).hostname
      if (!(isLocalHostname(envHostname) && !isLocalHostname(currentHostname))) {
        return envUrl
      }

      console.warn(
        `Ignoring VITE_API_URL="${envUrl}" because app is running on "${currentHostname}".`
      )
    } catch {
      console.warn(`Invalid VITE_API_URL="${envUrl}", falling back to auto-detection.`)
    }
  }

  // Production nginx proxies /api to the backend. Dev still calls :8000 directly.
  if (import.meta.env.PROD) {
    return '/api/v1'
  }

  const protocol = window.location.protocol
  return `${protocol}//${currentHostname}:8000/api/v1`
}

const API_BASE_URL = getApiBaseUrl()

console.log('API Base URL:', API_BASE_URL)

export const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
})

export const getApiUrl = () => API_BASE_URL

apiClient.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    // Analytics aggregates many activities from NAS Postgres; allow slower responses.
    const url = String(config.url || '')
    if (url.includes('/analytics/') || url.includes('/garmin/hrv')) {
      config.timeout = Math.max(config.timeout ?? 0, 45000)
    }
    return config
  },
  (error) => Promise.reject(error)
)

apiClient.interceptors.response.use(
  (response) => response,
  async (error) => {
    if (error.response?.status === 401) {
      const url = String(error.config?.url || '')
      // Clear stale token on /auth/me failures only. Never hard-redirect here —
      // full page reloads cause endless loops with auto-login / route guards.
      if (url.includes('/auth/me')) {
        localStorage.removeItem('access_token')
      }
    }
    return Promise.reject(error)
  }
)

export default apiClient
