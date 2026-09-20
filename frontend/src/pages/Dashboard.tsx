import { useEffect, useState } from 'react'
import { Container, Box, Typography, Card, CardContent, Grid, ToggleButtonGroup, ToggleButton } from '@mui/material'
import { useNavigate } from 'react-router-dom'
import { useAuthStore } from '../store/authStore'
import api from '../services/api'
import MetricCard from '../components/MetricCard'
import PerformanceChart from '../components/PerformanceChart'
import SportFitnessWidget from '../components/SportFitnessWidget'
import EmptyState from '../components/EmptyState'
import DashboardSkeleton from '../components/skeletons/DashboardSkeleton'
import { FitnessCenter, TrendingUp, Speed, Timeline, DirectionsRun, Favorite } from '@mui/icons-material'

interface ActivityStats {
  total_activities: number
  activities_this_week: number
  activities_this_month: number
}

interface TrainingMetrics {
  ctl: number
  atl: number
  tsb: number
  weekly_tss: number
  trend: 'up' | 'down' | 'flat'
}

interface PerformanceData {
  date: string
  ctl: number
  atl: number
  tsb: number
}

interface HRVStatus {
  value: number
  isInRange: boolean
  threshold_lower: number
  threshold_upper: number
}

export default function Dashboard() {
  const navigate = useNavigate()
  const { user, isAuthenticated, fetchUser } = useAuthStore()
  const [activityStats, setActivityStats] = useState<ActivityStats | null>(null)
  const [trainingMetrics, setTrainingMetrics] = useState<TrainingMetrics>({
    ctl: 0,
    atl: 0,
    tsb: 0,
    weekly_tss: 0,
    trend: 'flat'
  })
  const [performanceData, setPerformanceData] = useState<PerformanceData[]>([])
  const [loading, setLoading] = useState(true)
  const [timeRange, setTimeRange] = useState<number>(365)
  const [hrvStatus, setHrvStatus] = useState<HRVStatus | null>(null)

  // Set document title
  useEffect(() => {
    document.title = 'Dashboard - Kinesis'
  }, [])

  useEffect(() => {
    if (!isAuthenticated) {
      navigate('/login')
    } else if (!user) {
      fetchUser()
    }
  }, [isAuthenticated, user, navigate, fetchUser])

  useEffect(() => {
    const fetchStats = async () => {
      try {
        // Fetch activity stats
        const statsResponse = await api.get('/garmin/activities/stats')
        setActivityStats(statsResponse.data)
        
        // Fetch real training load metrics from backend
        const [metricsResponse, loadResponse, hrvResponse] = await Promise.all([
          api.get('/garmin/training-metrics'),
          api.get(`/garmin/training-load?days=${timeRange}`),
          api.get('/garmin/hrv?days=7').catch(() => ({ data: { data: [] } })) // Fail gracefully
        ])
        
        setTrainingMetrics(metricsResponse.data)
        setPerformanceData(loadResponse.data)
        
        // Extract latest 7-day average HRV and status
        if (hrvResponse.data.data && hrvResponse.data.data.length > 0) {
          const latestData = hrvResponse.data.data[hrvResponse.data.data.length - 1]
          if (latestData && latestData.rmssd_7day_avg) {
            const value = Math.round(latestData.rmssd_7day_avg)
            const lower = Math.round(latestData.rmssd_30day_lower || 0)
            const upper = Math.round(latestData.rmssd_30day_upper || 0)
            const isInRange = value >= lower && value <= upper
            
            setHrvStatus({
              value,
              isInRange,
              threshold_lower: lower,
              threshold_upper: upper
            })
          }
        }
        
      } catch (error) {
        console.error('Failed to fetch activity stats:', error)
        // Set default values on error
        setActivityStats({
          total_activities: 0,
          activities_this_week: 0,
          activities_this_month: 0
        })
        setTrainingMetrics({
          ctl: 0,
          atl: 0,
          tsb: 0,
          weekly_tss: 0,
          trend: 'flat'
        })
        setPerformanceData([])
      } finally {
        setLoading(false)
      }
    }

    if (isAuthenticated && user) {
      fetchStats()
    }
  }, [isAuthenticated, user, timeRange])

  // Auto-sync activities and health data on startup (adaptive sync interval)
  useEffect(() => {
    const autoSync = async () => {
      try {
        // Check if Garmin is connected
        const statusResponse = await api.get('/garmin/status')
        if (statusResponse.data.connected) {
          // Adaptive sync: more frequent = less data, less frequent = more data
          const lastSyncKey = 'lastGarminSyncTimestamp'
          const lastSyncTime = localStorage.getItem(lastSyncKey)
          const now = Date.now()
          const oneHourMs = 60 * 60 * 1000
          const sixHoursMs = 6 * 60 * 60 * 1000
          
          let shouldSync = true
          let syncDays = 7 // Default: full 7-day sync
          
          if (lastSyncTime) {
            const timeSinceLastSync = now - parseInt(lastSyncTime)
            
            if (timeSinceLastSync < oneHourMs) {
              // Less than 1 hour: skip completely
              shouldSync = false
              const nextSyncTime = new Date(parseInt(lastSyncTime) + oneHourMs)
              console.log(`Auto-sync skipped (last sync: ${new Date(parseInt(lastSyncTime)).toLocaleString()}, next sync after: ${nextSyncTime.toLocaleString()})`)
            } else if (timeSinceLastSync < sixHoursMs) {
              // 1-6 hours: quick sync (1 day only)
              syncDays = 1
              console.log(`Auto-syncing Garmin data (quick sync: 1 day, last sync: ${new Date(parseInt(lastSyncTime)).toLocaleString()})`)
            } else {
              // 6+ hours: full sync (7 days)
              syncDays = 7
              console.log(`Auto-syncing Garmin data (full sync: 7 days, last sync: ${new Date(parseInt(lastSyncTime)).toLocaleString()})`)
            }
          } else {
            // First sync ever: full 7 days
            console.log('Auto-syncing Garmin data (initial sync: 7 days)')
          }
          
          if (shouldSync) {
            // Sync activities and health data in parallel with adaptive days
            await Promise.all([
              api.post('/garmin/sync-activities', { days: syncDays }),
              api.post('/garmin/sync-health-data', { days: syncDays }).catch(err => {
                console.log('Health data sync skipped:', err)
              })
            ])
            
            // Update last sync timestamp
            localStorage.setItem(lastSyncKey, now.toString())
            console.log('Auto-sync completed')
          }
          
          // Refresh all stats (whether we synced or not)
          const [statsResponse, metricsResponse, loadResponse, hrvResponse] = await Promise.all([
            api.get('/garmin/activities/stats'),
            api.get('/garmin/training-metrics'),
            api.get(`/garmin/training-load?days=${timeRange}`),
            api.get('/garmin/hrv?days=7').catch(() => ({ data: { data: [] } }))
          ])
          
          setActivityStats(statsResponse.data)
          setTrainingMetrics(metricsResponse.data)
          setPerformanceData(loadResponse.data)
          
          // Update HRV status
          if (hrvResponse.data.data && hrvResponse.data.data.length > 0) {
            const latestData = hrvResponse.data.data[hrvResponse.data.data.length - 1]
            if (latestData && latestData.rmssd_7day_avg) {
              const value = Math.round(latestData.rmssd_7day_avg)
              const lower = Math.round(latestData.rmssd_30day_lower || 0)
              const upper = Math.round(latestData.rmssd_30day_upper || 0)
              const isInRange = value >= lower && value <= upper
              
              setHrvStatus({
                value,
                isInRange,
                threshold_lower: lower,
                threshold_upper: upper
              })
            }
          }
        }
      } catch (error) {
        // Fail silently - don't interrupt user experience
        console.log('Auto-sync skipped or failed:', error)
      }
    }

    if (isAuthenticated && user) {
      // Run after a short delay to let the page load first
      setTimeout(autoSync, 2000)
    }
  }, [isAuthenticated, user])



  if (!user) {
    return (
      <Container maxWidth="lg" sx={{ py: 3 }}>
        <DashboardSkeleton />
      </Container>
    )
  }

  // Empty state when user has no activities
  if (activityStats?.total_activities === 0 && !loading) {
    return (
      <Container maxWidth="lg" sx={{ py: 3 }}>
        <Box sx={{ mb: 3 }}>
          <Typography variant="h4" component="h1" gutterBottom sx={{ fontWeight: 600 }}>
            Training Dashboard
          </Typography>
        </Box>
        <EmptyState
          icon={<DirectionsRun />}
          title="No activities yet"
          description="Connect your Garmin account to automatically sync your activities and start tracking your training progress."
          actionLabel="Connect Garmin"
          onAction={() => navigate('/settings?tab=1')}
          secondaryActionLabel="View Calendar"
          onSecondaryAction={() => navigate('/calendar')}
        />
      </Container>
    )
  }

  // Loading skeleton
  if (loading) {
    return (
      <Container maxWidth="lg" sx={{ py: 3 }}>
        <DashboardSkeleton />
      </Container>
    )
  }

  return (
    <Container maxWidth="lg" sx={{ py: 3 }}>
      <Box sx={{ mb: 3 }}>
        <Typography variant="h4" component="h1" gutterBottom sx={{ fontWeight: 600 }}>
          Training Dashboard
        </Typography>
      </Box>

      <Grid container spacing={{ xs: 1.5, sm: 2, md: 3 }}>
          {/* Top 3 KPIs - Mobile optimized to fit in one row */}
          <Grid item xs={4} sm={6} md={4}>
            <MetricCard
              title="Fitness (CTL)"
              value={trainingMetrics.ctl}
              color="#2196f3"
              icon={<FitnessCenter />}
              trend={trainingMetrics.trend}
              trendValue="vs last week"
              compact
            />
          </Grid>
          <Grid item xs={4} sm={6} md={4}>
            <MetricCard
              title="Fatigue (ATL)"
              value={trainingMetrics.atl}
              color="#ff9800"
              icon={<TrendingUp />}
              compact
            />
          </Grid>
          <Grid item xs={4} sm={6} md={4}>
            <MetricCard
              title="Form (TSB)"
              value={trainingMetrics.tsb}
              color={trainingMetrics.tsb > 0 ? '#4caf50' : '#f44336'}
              icon={<Speed />}
              compact
            />
          </Grid>
          
          {/* Weekly Metrics Row - Weekly TSS and HRV Status side by side */}
          <Grid item xs={6} sm={6} md={6}>
            <MetricCard
              title="Weekly TSS"
              value={trainingMetrics.weekly_tss}
              color="primary.main"
              icon={<Timeline />}
              compact
            />
          </Grid>
          <Grid item xs={6} sm={6} md={6}>
            <MetricCard
              title="HRV Status"
              value={hrvStatus?.value || 0}
              unit="ms"
              color={hrvStatus?.isInRange ? '#4caf50' : '#f44336'}
              icon={<Favorite />}
              subtitle={hrvStatus ? `7d avg | 30d: ${hrvStatus.threshold_lower}-${hrvStatus.threshold_upper} ms` : '7-day avg'}
              compact
            />
          </Grid>

          {/* Sport-Specific Fitness Widgets */}
          <Grid item xs={12} md={4}>
            <SportFitnessWidget sport="running" />
          </Grid>
          <Grid item xs={12} md={4}>
            <SportFitnessWidget sport="cycling" />
          </Grid>
          <Grid item xs={12} md={4}>
            <SportFitnessWidget sport="swimming" />
          </Grid>

          {/* Performance Chart */}
          <Grid item xs={12}>
            <Card>
              <CardContent>
                <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
                  <Typography variant="h6">
                    Performance Chart
                  </Typography>
                  <ToggleButtonGroup
                    value={timeRange}
                    exclusive
                    onChange={(_, newValue) => newValue && setTimeRange(newValue)}
                    size="small"
                  >
                    <ToggleButton value={30}>30d</ToggleButton>
                    <ToggleButton value={90}>90d</ToggleButton>
                    <ToggleButton value={180}>180d</ToggleButton>
                    <ToggleButton value={365}>1y</ToggleButton>
                    <ToggleButton value={730}>2y</ToggleButton>
                  </ToggleButtonGroup>
                </Box>
                <PerformanceChart data={performanceData} />
              </CardContent>
            </Card>
          </Grid>
        </Grid>
    </Container>
  )
}
