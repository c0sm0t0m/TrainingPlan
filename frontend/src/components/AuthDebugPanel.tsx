import { useEffect, useState } from 'react'
import { Box, Button, Typography, Paper } from '@mui/material'
import {
  getAuthDebugEvents,
  getAuthRuntimeInfo,
  subscribeAuthDebug,
  type AuthDebugEvent,
} from '../store/authStore'
import { useAuthStore } from '../store/authStore'

function shouldShowAuthDebug(): boolean {
  if (typeof window === 'undefined') return false
  const params = new URLSearchParams(window.location.search)
  if (params.get('debug') === '1' || params.get('debug') === 'true') return true
  const host = window.location.hostname
  return host !== 'localhost' && host !== '127.0.0.1' && host !== '::1'
}

export default function AuthDebugPanel() {
  const [events, setEvents] = useState<AuthDebugEvent[]>(() => getAuthDebugEvents())
  const [open, setOpen] = useState(true)
  const { isAuthenticated, isLoading, error, lastStatusCode, user, token } = useAuthStore()

  useEffect(() => subscribeAuthDebug(() => setEvents(getAuthDebugEvents())), [])

  if (!shouldShowAuthDebug()) return null

  const info = getAuthRuntimeInfo()

  const copyReport = async () => {
    const report = {
      runtime: info,
      store: {
        isAuthenticated,
        isLoading,
        error,
        lastStatusCode,
        userEmail: user?.email ?? null,
        hasTokenInStore: !!token,
      },
      events,
    }
    const text = JSON.stringify(report, null, 2)
    try {
      await navigator.clipboard.writeText(text)
    } catch {
      console.log('AUTH_DEBUG_REPORT', report)
    }
  }

  return (
    <Paper
      elevation={0}
      sx={{
        mt: 2,
        p: 1.5,
        bgcolor: '#111',
        color: '#d4d4d4',
        fontFamily: 'ui-monospace, SFMono-Regular, Menlo, monospace',
        fontSize: 11,
        borderRadius: 1,
        maxHeight: open ? 360 : 40,
        overflow: 'auto',
      }}
    >
      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: open ? 1 : 0 }}>
        <Typography sx={{ fontSize: 11, fontWeight: 700, color: '#fbbf24', flex: 1 }}>
          Auth debug (auto-login OFF)
        </Typography>
        <Button size="small" onClick={() => setOpen((v) => !v)} sx={{ color: '#93c5fd', minWidth: 0 }}>
          {open ? 'Hide' : 'Show'}
        </Button>
        <Button size="small" onClick={copyReport} sx={{ color: '#86efac', minWidth: 0 }}>
          Copy
        </Button>
      </Box>
      {open && (
        <>
          <Box component="pre" sx={{ m: 0, whiteSpace: 'pre-wrap', wordBreak: 'break-all' }}>
            {`host: ${info.hostname}
href: ${info.href}
api: ${info.apiBaseUrl}
VITE_DEV_AUTO_LOGIN: ${info.viteDevAutoLoginEnv || '(unset)'}
autoLoginEnabled: ${info.autoLoginEnabled}
token: ${info.tokenPreview ?? '(none)'}
isAuthenticated: ${isAuthenticated}
isLoading: ${isLoading}
lastStatus: ${lastStatusCode ?? '-'}
error: ${error ?? '-'}
user: ${user?.email ?? '-'}`}
          </Box>
          <Typography sx={{ mt: 1, mb: 0.5, fontSize: 11, color: '#fbbf24' }}>
            Event log (newest last)
          </Typography>
          <Box component="pre" sx={{ m: 0, whiteSpace: 'pre-wrap', wordBreak: 'break-all' }}>
            {events.length === 0
              ? '(no events yet)'
              : events
                  .map(
                    (e) =>
                      `${e.t.slice(11, 19)} [${e.level}] ${e.message}` +
                      (e.detail !== undefined ? ` ${JSON.stringify(e.detail)}` : '')
                  )
                  .join('\n')}
          </Box>
        </>
      )}
    </Paper>
  )
}
