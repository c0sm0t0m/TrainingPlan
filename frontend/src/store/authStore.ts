import { create } from 'zustand'
import apiClient from '../services/api'

/**
 * Auth debug ring buffer — visible on Login when ?debug=1 or non-localhost.
 * Auto-login is intentionally disabled (caused NAS deploy login loops).
 */

export type AuthDebugEvent = {
  t: string
  level: 'info' | 'warn' | 'error'
  message: string
  detail?: unknown
}

const MAX_EVENTS = 40
const debugEvents: AuthDebugEvent[] = []
const debugListeners = new Set<() => void>()

function emitDebug(level: AuthDebugEvent['level'], message: string, detail?: unknown) {
  const event: AuthDebugEvent = {
    t: new Date().toISOString(),
    level,
    message,
    detail,
  }
  debugEvents.push(event)
  if (debugEvents.length > MAX_EVENTS) debugEvents.shift()
  const line = `[auth] ${message}`
  if (level === 'error') console.error(line, detail ?? '')
  else if (level === 'warn') console.warn(line, detail ?? '')
  else console.log(line, detail ?? '')
  debugListeners.forEach((l) => l())
}

export function getAuthDebugEvents(): AuthDebugEvent[] {
  return [...debugEvents]
}

export function subscribeAuthDebug(listener: () => void): () => void {
  debugListeners.add(listener)
  return () => debugListeners.delete(listener)
}

export function getAuthRuntimeInfo() {
  return {
    hostname: typeof window !== 'undefined' ? window.location.hostname : '',
    href: typeof window !== 'undefined' ? window.location.href : '',
    apiBaseUrl: apiClient.defaults.baseURL,
    viteDevAutoLoginEnv: String(import.meta.env.VITE_DEV_AUTO_LOGIN ?? ''),
    autoLoginEnabled: false,
    hasAccessToken: !!localStorage.getItem('access_token'),
    tokenPreview: (() => {
      const t = localStorage.getItem('access_token')
      if (!t) return null
      return `${t.slice(0, 12)}…(${t.length} chars)`
    })(),
  }
}

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
  lastStatusCode: number | null

  login: (email: string, password: string) => Promise<void>
  register: (email: string, password: string, fullName?: string) => Promise<void>
  logout: () => void
  fetchUser: () => Promise<void>
}

emitDebug('info', 'authStore module loaded', getAuthRuntimeInfo())

export const useAuthStore = create<AuthState>((set, get) => ({
  user: null,
  token: localStorage.getItem('access_token'),
  isAuthenticated: !!localStorage.getItem('access_token'),
  isLoading: false,
  error: null,
  lastStatusCode: null,

  login: async (email: string, password: string) => {
    set({ isLoading: true, error: null, lastStatusCode: null })
    emitDebug('info', 'login start', { email, api: apiClient.defaults.baseURL })
    try {
      const formData = new URLSearchParams()
      formData.append('username', email)
      formData.append('password', password)

      const response = await apiClient.post('/auth/login', formData, {
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
      })

      const { access_token } = response.data
      localStorage.setItem('access_token', access_token)
      set({ token: access_token, isAuthenticated: true, lastStatusCode: response.status })
      emitDebug('info', 'login ok — token stored', { status: response.status })

      await get().fetchUser()
    } catch (error: any) {
      const status = error.response?.status ?? null
      const detail = error.response?.data?.detail || error.message || 'Login failed'
      emitDebug('error', 'login failed', {
        status,
        detail,
        data: error.response?.data,
        url: error.config?.url,
        baseURL: error.config?.baseURL,
      })
      set({
        error: typeof detail === 'string' ? detail : JSON.stringify(detail),
        isLoading: false,
        isAuthenticated: false,
        token: null,
        lastStatusCode: status,
      })
      localStorage.removeItem('access_token')
      throw error
    }
  },

  register: async (email: string, password: string, fullName?: string) => {
    set({ isLoading: true, error: null, lastStatusCode: null })
    emitDebug('info', 'register start', { email })
    try {
      const response = await apiClient.post('/auth/register', {
        email,
        password,
        full_name: fullName,
      })
      emitDebug('info', 'register ok', { status: response.status })
      await get().login(email, password)
    } catch (error: any) {
      const status = error.response?.status ?? null
      const detail = error.response?.data?.detail || error.message || 'Registration failed'
      emitDebug('error', 'register failed', { status, detail, data: error.response?.data })
      set({
        error: typeof detail === 'string' ? detail : JSON.stringify(detail),
        isLoading: false,
        lastStatusCode: status,
      })
      throw error
    }
  },

  logout: () => {
    emitDebug('info', 'logout')
    localStorage.removeItem('access_token')
    set({
      user: null,
      token: null,
      isAuthenticated: false,
      error: null,
      lastStatusCode: null,
    })
  },

  fetchUser: async () => {
    emitDebug('info', 'fetchUser /auth/me')
    try {
      const response = await apiClient.get('/auth/me')
      set({
        user: response.data,
        isAuthenticated: true,
        isLoading: false,
        lastStatusCode: response.status,
      })
      emitDebug('info', 'fetchUser ok', { email: response.data?.email })
    } catch (error: any) {
      const status = error.response?.status ?? null
      emitDebug('warn', 'fetchUser failed — clearing token', {
        status,
        detail: error.response?.data?.detail || error.message,
      })
      set({
        isLoading: false,
        user: null,
        token: null,
        isAuthenticated: false,
        lastStatusCode: status,
      })
      localStorage.removeItem('access_token')
    }
  },
}))

// Validate existing token only — never auto-login (removed for NAS deploy stability).
if (localStorage.getItem('access_token')) {
  emitDebug('info', 'found existing access_token — validating via /auth/me')
  useAuthStore.getState().fetchUser()
} else {
  emitDebug('info', 'no access_token — waiting for manual login')
}
