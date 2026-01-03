import { create } from 'zustand'
import apiClient from '../services/api'

// Development mode auto-login (set credentials in .env.local)
const DEV_AUTO_LOGIN = import.meta.env.VITE_DEV_AUTO_LOGIN === 'true'
const DEV_EMAIL = import.meta.env.VITE_DEV_EMAIL || ''
const DEV_PASSWORD = import.meta.env.VITE_DEV_PASSWORD || ''

interface User {
  id: number
  email: string
  full_name?: string
  is_active: boolean
}

interface AuthState {
  user: User | null
  token: string | null
  isAuthenticated: boolean
  isLoading: boolean
  error: string | null
  
  login: (email: string, password: string) => Promise<void>
  register: (email: string, password: string, fullName?: string) => Promise<void>
  logout: () => void
  fetchUser: () => Promise<void>
}

export const useAuthStore = create<AuthState>((set, get) => ({
  user: null,
  token: localStorage.getItem('access_token'),
  isAuthenticated: !!localStorage.getItem('access_token'),
  isLoading: false,
  error: null,

  login: async (email: string, password: string) => {
    set({ isLoading: true, error: null })
    try {
      // OAuth2 format requires form data
      const formData = new FormData()
      formData.append('username', email) // OAuth2 uses 'username' field
      formData.append('password', password)
      
      const response = await apiClient.post('/auth/login', formData, {
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' }
      })
      
      const { access_token } = response.data
      localStorage.setItem('access_token', access_token)
      set({ token: access_token, isAuthenticated: true })
      
      // Fetch user info
      await get().fetchUser()
    } catch (error: any) {
      set({ error: error.response?.data?.detail || 'Login failed', isLoading: false })
      throw error
    }
  },

  register: async (email: string, password: string, fullName?: string) => {
    set({ isLoading: true, error: null })
    try {
      await apiClient.post('/auth/register', {
        email,
        password,
        full_name: fullName
      })
      
      // Auto-login after registration
      await get().login(email, password)
    } catch (error: any) {
      set({ error: error.response?.data?.detail || 'Registration failed', isLoading: false })
      throw error
    }
  },

  logout: () => {
    localStorage.removeItem('access_token')
    set({ user: null, token: null, isAuthenticated: false })
  },

  fetchUser: async () => {
    try {
      const response = await apiClient.get('/auth/me')
      set({ user: response.data, isLoading: false })
    } catch (error) {
      set({ isLoading: false })
      get().logout()
      
      // Auto-login in development if enabled
      if (DEV_AUTO_LOGIN && DEV_EMAIL && DEV_PASSWORD) {
        console.log('🔧 Development mode: Auto-login enabled')
        try {
          await get().login(DEV_EMAIL, DEV_PASSWORD)
        } catch (err) {
          console.error('Auto-login failed:', err)
        }
      }
    }
  }
}))

// Initialize: Try to fetch user if token exists, or auto-login in dev mode
if (localStorage.getItem('access_token')) {
  useAuthStore.getState().fetchUser()
} else if (DEV_AUTO_LOGIN && DEV_EMAIL && DEV_PASSWORD) {
  console.log('🔧 Development mode: Auto-login on startup')
  useAuthStore.getState().login(DEV_EMAIL, DEV_PASSWORD).catch(() => {
    console.error('Auto-login failed')
  })
}
