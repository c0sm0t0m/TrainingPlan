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
        `⚠️ Ignoring VITE_API_URL="${envUrl}" because app is running on "${currentHostname}".`
      )
    } catch {
      console.warn(`⚠️ Invalid VITE_API_URL="${envUrl}", falling back to auto-detection.`)
    }
  }
  
  // Use current hostname (works for localhost, IP address, or domain name)
  const protocol = window.location.protocol
  return `${protocol}//${currentHostname}:8000/api/v1`
}

const API_BASE_URL = getApiBaseUrl()

// Log the API URL for debugging
console.log('🌐 API Base URL:', API_BASE_URL)

export const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Export function to get current API URL
export const getApiUrl = () => API_BASE_URL

// Request interceptor - add auth token
apiClient.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// Response interceptor - handle errors
apiClient.interceptors.response.use(
  (response) => response,
  async (error) => {
    if (error.response?.status === 401) {
      // Only logout if it's an authentication endpoint error
      // Don't logout for 401 errors from third-party integrations like Garmin
      const url = error.config?.url || ''
      const isAuthEndpoint = url.includes('/auth/') || url.includes('/auth/me')
      
      if (isAuthEndpoint) {
        // Token expired or invalid - redirect to login
        localStorage.removeItem('access_token')
        window.location.href = '/login'
      }
    }
    return Promise.reject(error)
  }
)

export default apiClient
