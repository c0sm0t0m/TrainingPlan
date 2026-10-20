import { useState, useEffect } from 'react'
import { Container, Box, Typography, ToggleButtonGroup, ToggleButton, Paper, useMediaQuery, useTheme } from '@mui/material'
import { useNavigate } from 'react-router-dom'
import { useAuthStore } from '../store/authStore'
import HRVStatsWidget from '../components/analytics/HRVStatsWidget'
import TSSPerWeekWidget from '../components/analytics/TSSPerWeekWidget'
import HRZoneDistributionWidget from '../components/analytics/HRZoneDistributionWidget'
import PerformanceTrendWidget from '../components/analytics/PerformanceTrendWidget'
import ThresholdPaceTrendChart from '../components/ThresholdPaceTrendChart'
import KeySessionsWidget from '../components/KeySessionsWidget'
import { Assessment } from '@mui/icons-material'

export default function Analytics() {
  const navigate = useNavigate()
  const theme = useTheme()
  const isMobile = useMediaQuery(theme.breakpoints.down('sm'))
  const { user, isAuthenticated, fetchUser } = useAuthStore()
  const [timeRange, setTimeRange] = useState<number>(30)  // Default to 30 days

  // Set document title
  useEffect(() => {
    document.title = 'Analytics - Kinesis'
  }, [])

  useEffect(() => {
    if (!isAuthenticated) {
      navigate('/login')
    } else if (!user) {
      fetchUser()
    }
  }, [isAuthenticated, user, navigate, fetchUser])

  // Auth token is enough to load widgets; don't block the page on /auth/me.
  if (!isAuthenticated) {
    return <div>Loading...</div>
  }

  return (
    <Box sx={{ 
      position: 'fixed',
      top: { xs: 56, sm: 64 }, // AppBar height
      bottom: { xs: 56, sm: 0 }, // Bottom nav on mobile
      left: 0,
      right: 0,
      display: 'flex', 
      flexDirection: 'column',
      overflow: 'hidden',
    }}>
      {/* Fixed Header */}
      <Paper 
        elevation={2}
        sx={{ 
          flexShrink: 0,
          borderRadius: 0,
          py: { xs: 1.5, sm: 2 },
          px: { xs: 2, sm: 3 }
        }}
      >
        <Box sx={{ 
          display: 'flex', 
          flexDirection: { xs: 'column', sm: 'row' },
          alignItems: { xs: 'flex-start', sm: 'center' }, 
          justifyContent: 'space-between',
          gap: { xs: 2, sm: 0 },
          mb: 0 
        }}>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            <Assessment sx={{ fontSize: { xs: 28, sm: 32 }, color: 'primary.main' }} />
            <Typography variant="h4" component="h1" sx={{ fontSize: { xs: '1.5rem', sm: '2.125rem' }, fontWeight: 600 }}>
              Analytics
            </Typography>
          </Box>

          {/* Time Range Selector */}
          <Box sx={{ display: 'flex', alignItems: 'center', gap: { xs: 1, sm: 2 }, width: { xs: '100%', sm: 'auto' } }}>
            {!isMobile && (
              <Typography variant="body2" color="text.secondary">
                Time Range:
              </Typography>
            )}
            <ToggleButtonGroup
              value={timeRange}
              exclusive
              onChange={(_, newValue) => {
                if (newValue !== null) {
                  setTimeRange(newValue)
                }
              }}
              size="small"
              sx={{ 
                width: { xs: '100%', sm: 'auto' },
                '& .MuiToggleButton-root': {
                  flex: { xs: 1, sm: 'initial' },
                  fontSize: { xs: '0.75rem', sm: '0.875rem' }
                }
              }}
            >
              <ToggleButton value={7}>7d</ToggleButton>
              <ToggleButton value={14}>14d</ToggleButton>
              <ToggleButton value={30}>30d</ToggleButton>
              <ToggleButton value={90}>90d</ToggleButton>
              <ToggleButton value={180}>180d</ToggleButton>
              <ToggleButton value={365}>1yr</ToggleButton>
              <ToggleButton value={730}>2yr</ToggleButton>
            </ToggleButtonGroup>
          </Box>
        </Box>
      </Paper>

      {/* Scrollable Content Area */}
      <Box
        sx={{ 
          flex: 1,
          overflowY: 'auto',
          overflowX: 'hidden',
        }}
      >
        <Container 
          maxWidth="lg" 
          sx={{ 
            py: { xs: 2, sm: 3 },
            px: { xs: 2, sm: 3 }
          }}
        >
          {/* Performance over the year (pace / power) */}
          <Box sx={{ mb: 4 }}>
            <PerformanceTrendWidget key={`perf-${timeRange}`} daysBack={timeRange} />
          </Box>

          {/* Threshold pace from key run sessions */}
          <Box sx={{ mb: 4 }}>
            <ThresholdPaceTrendChart key={`threshold-pace-${timeRange}`} sport="running" daysBack={timeRange} />
          </Box>

          {/* Key sessions scatter */}
          <Box sx={{ mb: 4 }}>
            <KeySessionsWidget key={`key-sessions-${timeRange}`} sport="running" daysBack={timeRange} limit={24} />
          </Box>

          {/* HRV Stats Widget */}
          <Box sx={{ mb: 4 }}>
            <HRVStatsWidget key={`hrv-${timeRange}`} daysBack={timeRange} />
          </Box>

          {/* TSS per Week Widget */}
          <Box sx={{ mb: 4 }}>
            <TSSPerWeekWidget key={`tss-${timeRange}`} daysBack={timeRange} />
          </Box>

          {/* HR Zone Distribution Widget */}
          <Box sx={{ mb: 4 }}>
            <HRZoneDistributionWidget key={`hrzone-${timeRange}`} daysBack={timeRange} />
          </Box>
        </Container>
      </Box>
    </Box>
  )
}
