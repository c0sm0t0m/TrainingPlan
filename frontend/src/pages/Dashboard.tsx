import { useEffect, useState } from 'react'
import { Container, Box, Typography, Card, CardContent, Grid, Button, ToggleButtonGroup, ToggleButton } from '@mui/material'
import { useNavigate } from 'react-router-dom'
import { useAuthStore } from '../store/authStore'
import api from '../services/api'
import MetricCard from '../components/MetricCard'
import PerformanceChart from '../components/PerformanceChart'
import SportFitnessWidget from '../components/SportFitnessWidget'
import { FitnessCenter, TrendingUp, Speed, Timeline } from '@mui/icons-material'

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

  // Set document title
  useEffect(() => {
    document.title = 'Dashboard - TrainingPlan'
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
        const [metricsResponse, loadResponse] = await Promise.all([
          api.get('/garmin/training-metrics'),
          api.get(`/garmin/training-load?days=${timeRange}`)
        ])
        
        setTrainingMetrics(metricsResponse.data)
        setPerformanceData(loadResponse.data)
        
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

  // Auto-sync activities on startup (7 days)
  useEffect(() => {
    const autoSync = async () => {
      try {
        // Check if Garmin is connected
        const statusResponse = await api.get('/garmin/status')
        if (statusResponse.data.connected) {
          console.log('Auto-syncing Garmin activities (last 7 days)...')
          await api.post('/garmin/sync-activities', { days: 7 })
          console.log('Auto-sync completed')
          
          // Refresh all stats after sync
          const [statsResponse, metricsResponse, loadResponse] = await Promise.all([
            api.get('/garmin/activities/stats'),
            api.get('/garmin/training-metrics'),
            api.get(`/garmin/training-load?days=${timeRange}`)
          ])
          
          setActivityStats(statsResponse.data)
          setTrainingMetrics(metricsResponse.data)
          setPerformanceData(loadResponse.data)
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
    return <div>Loading...</div>
  }

  return (
    <Container maxWidth="lg" sx={{ py: 3 }}>
      <Box sx={{ mb: 3 }}>
        <Typography variant="h4" component="h1" gutterBottom sx={{ fontWeight: 600 }}>
          Training Dashboard
        </Typography>
      </Box>

      <Grid container spacing={3}>
          {/* Metric Cards Row - Reordered: ATL, CTL, TSB, Weekly TSS */}
          <Grid item xs={12} sm={6} md={3}>
            <MetricCard
              title="Fatigue (ATL)"
              value={trainingMetrics.atl}
              color="#ff9800"
              icon={<TrendingUp />}
            />
          </Grid>
          <Grid item xs={12} sm={6} md={3}>
            <MetricCard
              title="Fitness (CTL)"
              value={trainingMetrics.ctl}
              color="#2196f3"
              icon={<FitnessCenter />}
              trend={trainingMetrics.trend}
              trendValue="vs last week"
            />
          </Grid>
          <Grid item xs={12} sm={6} md={3}>
            <MetricCard
              title="Form (TSB)"
              value={trainingMetrics.tsb}
              color={trainingMetrics.tsb > 0 ? '#4caf50' : '#f44336'}
              icon={<Speed />}
            />
          </Grid>
          <Grid item xs={12} sm={6} md={3}>
            <MetricCard
              title="Weekly TSS"
              value={trainingMetrics.weekly_tss}
              color="primary.main"
              icon={<Timeline />}
            />
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
                  </ToggleButtonGroup>
                </Box>
                <PerformanceChart data={performanceData} />
              </CardContent>
            </Card>
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
        </Grid>
    </Container>
  )
}
