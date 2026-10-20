import { lazy, Suspense, useEffect, useRef, useState } from 'react'
import { Container, Box, Typography, Card, CardContent, Grid, ToggleButtonGroup, ToggleButton, CircularProgress } from '@mui/material'
import { FitnessCenter, TrendingUp, Speed, Timeline, DirectionsRun, Favorite } from '@mui/icons-material'
import { useNavigate } from 'react-router-dom'
import { useAuthStore } from '../store/authStore'
import api from '../services/api'
import MetricCard from '../components/MetricCard'
import EmptyState from '../components/EmptyState'
import DashboardSkeleton from '../components/skeletons/DashboardSkeleton'
import { enqueue } from '../utils/requestQueue'
import { LoadPoint, summarizeLoad } from '../utils/trainingLoad'

const PerformanceChart = lazy(() => import('../components/PerformanceChart'))
const SportFitnessWidget = lazy(() => import('../components/SportFitnessWidget'))

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
  const [performanceData, setPerformanceData] = useState<LoadPoint[]>([])
  const [statsLoaded, setStatsLoaded] = useState(false)
  const [metricsLoading, setMetricsLoading] = useState(true)
  const [chartLoading, setChartLoading] = useState(true)
  const [timeRange, setTimeRange] = useState<number>(90)
  const timeRangeRef = useRef(timeRange)
  timeRangeRef.current = timeRange
  const seriesRef = useRef<LoadPoint[]>([])
  const initialLoadRef = useRef<Promise<void>>(Promise.resolve())
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
    if (!isAuthenticated || !user) return
    let cancelled = false

    const applyHrv = (hrvResponse: { data: { data?: Array<{ rmssd_7day_avg?: number; rmssd_30day_lower?: number; rmssd_30day_upper?: number }> } }) => {
      if (!hrvResponse.data.data || hrvResponse.data.data.length === 0) return
      const latestData = hrvResponse.data.data[hrvResponse.data.data.length - 1]
      if (!latestData?.rmssd_7day_avg) return
      const value = Math.round(latestData.rmssd_7day_avg)
      const lower = Math.round(latestData.rmssd_30day_lower || 0)
      const upper = Math.round(latestData.rmssd_30day_upper || 0)
      setHrvStatus({
        value,
        isInRange: value >= lower && value <= upper,
        threshold_lower: lower,
        threshold_upper: upper,
      })
    }

    const fetchStats = async () => {
      try {
        const statsResponse = await api.get('/garmin/activities/stats')
        if (!cancelled) setActivityStats(statsResponse.data)
      } catch (error) {
        console.error('Failed to fetch activity stats:', error)
        try {
          const stored = await api.get('/garmin/activities/stored', { params: { limit: 1 } })
          const hasAny = Array.isArray(stored.data) && stored.data.length > 0
          if (!cancelled) {
            setActivityStats({
              total_activities: hasAny ? 1 : 0,
              activities_this_week: 0,
              activities_this_month: 0,
            })
          }
        } catch {
          if (!cancelled) setActivityStats(null)
        }
      } finally {
        if (!cancelled) setStatsLoaded(true)
      }
    }

    const fetchHrv = async () => {
      const hrvResponse = await api.get('/garmin/hrv?days=7').catch(() => ({ data: { data: [] } }))
      if (!cancelled) applyHrv(hrvResponse)
    }

    fetchStats()
    fetchHrv()
    return () => {
      cancelled = true
    }
  }, [isAuthenticated, user])

  useEffect(() => {
    if (!isAuthenticated || !user) return
    let cancelled = false

    const cached = seriesRef.current
    if (cached.length >= timeRange) {
      setPerformanceData(cached.slice(-timeRange))
      setTrainingMetrics(summarizeLoad(cached))
      setMetricsLoading(false)
      setChartLoading(false)
      return
    }

    setChartLoading(true)
    const load = enqueue(() => api.get<LoadPoint[]>(`/garmin/training-load?days=${timeRange}`))
      .then((loadResponse) => {
        if (cancelled || !loadResponse?.data) return
        seriesRef.current = loadResponse.data
        setPerformanceData(loadResponse.data)
        setTrainingMetrics(summarizeLoad(loadResponse.data))
      })
      .catch((err) => {
        console.error('training-load failed', err)
      })
      .finally(() => {
        if (!cancelled) {
          setChartLoading(false)
          setMetricsLoading(false)
        }
      })

    initialLoadRef.current = load
    return () => {
      cancelled = true
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
          
          if (!shouldSync) return

          await Promise.all([
            api.post('/garmin/sync-activities', { days: syncDays, include_details: false }, {
              timeout: Math.min(180000, Math.max(60000, syncDays * 5000)),
            }),
            api.post('/garmin/sync-health-data', { days: syncDays }).catch(err => {
              console.log('Health data sync skipped:', err)
            })
          ])

          localStorage.setItem(lastSyncKey, now.toString())
          console.log('Auto-sync completed')

          const days = timeRangeRef.current
          const [statsResponse, loadResponse, hrvResponse] = await Promise.all([
            api.get('/garmin/activities/stats').catch((err) => {
              console.error('post-sync stats failed', err)
              return null
            }),
            enqueue(() => api.get<LoadPoint[]>(`/garmin/training-load?days=${days}`)).catch((err) => {
              console.error('post-sync load failed', err)
              return null
            }),
            api.get('/garmin/hrv?days=7').catch(() => ({ data: { data: [] } })),
          ])

          if (statsResponse?.data) setActivityStats(statsResponse.data)
          if (loadResponse?.data) {
            seriesRef.current = loadResponse.data
            setPerformanceData(loadResponse.data.slice(-days))
            setTrainingMetrics(summarizeLoad(loadResponse.data))
          }

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
                threshold_upper: upper,
              })
            }
          }
        }
      } catch (error) {
        console.log('Auto-sync skipped or failed:', error)
      }
    }

    if (isAuthenticated && user) {
      let cancelled = false
      initialLoadRef.current.finally(() => {
        if (!cancelled) autoSync()
      })
      return () => {
        cancelled = true
      }
    }
  }, [isAuthenticated, user])



  if (!user) {
    return (
      <Container maxWidth="lg" sx={{ py: 3 }}>
        <DashboardSkeleton />
      </Container>
    )
  }

  if (statsLoaded && activityStats?.total_activities === 0) {
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
          description="No activities found for this account. If Garmin is already connected, open Settings and run a sync — or check that Mac→NAS push finished with activities."
          actionLabel="Open Settings"
          onAction={() => navigate('/settings')}
          secondaryActionLabel="View Calendar"
          onSecondaryAction={() => navigate('/calendar')}
        />
      </Container>
    )
  }

  const metricValue = (value: number) => (metricsLoading ? '—' : value)

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
              value={metricValue(trainingMetrics.ctl)}
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
              value={metricValue(trainingMetrics.atl)}
              color="#ff9800"
              icon={<TrendingUp />}
              compact
            />
          </Grid>
          <Grid item xs={4} sm={6} md={4}>
            <MetricCard
              title="Form (TSB)"
              value={metricValue(trainingMetrics.tsb)}
              color={trainingMetrics.tsb > 0 ? '#4caf50' : '#f44336'}
              icon={<Speed />}
              compact
            />
          </Grid>
          
          {/* Weekly Metrics Row - Weekly TSS and HRV Status side by side */}
          <Grid item xs={6} sm={6} md={6}>
            <MetricCard
              title="Weekly TSS"
              value={metricValue(trainingMetrics.weekly_tss)}
              color="primary.main"
              icon={<Timeline />}
              compact
            />
          </Grid>
          <Grid item xs={6} sm={6} md={6}>
            <MetricCard
              title="HRV Status"
              value={hrvStatus ? hrvStatus.value : '—'}
              unit="ms"
              color={hrvStatus?.isInRange ? '#4caf50' : '#f44336'}
              icon={<Favorite />}
              subtitle={hrvStatus ? `7d avg | 30d: ${hrvStatus.threshold_lower}-${hrvStatus.threshold_upper} ms` : '7-day avg'}
              compact
            />
          </Grid>

          {!metricsLoading && (
          <Suspense fallback={null}>
          <Grid item xs={12} md={4}>
            <SportFitnessWidget sport="running" />
          </Grid>
          <Grid item xs={12} md={4}>
            <SportFitnessWidget sport="cycling" />
          </Grid>
          <Grid item xs={12} md={4}>
            <SportFitnessWidget sport="swimming" />
          </Grid>
          </Suspense>
          )}

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
                {chartLoading ? (
                  <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: 300 }}>
                    <CircularProgress size={28} />
                  </Box>
                ) : (
                  <Suspense fallback={
                    <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: 300 }}>
                      <CircularProgress size={28} />
                    </Box>
                  }>
                    <PerformanceChart data={performanceData} />
                  </Suspense>
                )}
              </CardContent>
            </Card>
          </Grid>
        </Grid>
    </Container>
  )
}
