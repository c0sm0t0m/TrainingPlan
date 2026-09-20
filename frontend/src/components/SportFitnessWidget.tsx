import { useEffect, useState } from 'react'
import { Card, CardContent, Typography, Box, Grid } from '@mui/material'
import { LineChart, Line, ResponsiveContainer, YAxis } from 'recharts'
import api from '../services/api'
import { DirectionsRun, DirectionsBike, Pool } from '@mui/icons-material'

interface SportFitnessWidgetProps {
  sport: 'running' | 'cycling' | 'swimming'
}

interface TrainingMetrics {
  ctl: number
  atl: number
  tsb: number
}

interface PerformanceData {
  date: string
  ctl: number
}

const sportConfig = {
  running: {
    icon: DirectionsRun,
    color: '#2196f3',
    label: 'Running'
  },
  cycling: {
    icon: DirectionsBike,
    color: '#ff9800',
    label: 'Cycling'
  },
  swimming: {
    icon: Pool,
    color: '#00bcd4',
    label: 'Swimming'
  }
}

export default function SportFitnessWidget({ sport }: SportFitnessWidgetProps) {
  const [metrics, setMetrics] = useState<TrainingMetrics>({ ctl: 0, atl: 0, tsb: 0 })
  const [chartData, setChartData] = useState<{
    days7: PerformanceData[]
    days28: PerformanceData[]
    days90: PerformanceData[]
    days365: PerformanceData[]
  }>({
    days7: [],
    days28: [],
    days90: [],
    days365: []
  })
  const [loading, setLoading] = useState(true)

  const config = sportConfig[sport]
  const Icon = config.icon

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [metricsRes, data7, data28, data90, data365] = await Promise.all([
          api.get(`/garmin/training-metrics?sport_type=${sport}`),
          api.get(`/garmin/training-load?days=7&sport_type=${sport}`),
          api.get(`/garmin/training-load?days=28&sport_type=${sport}`),
          api.get(`/garmin/training-load?days=90&sport_type=${sport}`),
          api.get(`/garmin/training-load?days=365&sport_type=${sport}`)
        ])

        setMetrics(metricsRes.data)
        setChartData({
          days7: data7.data,
          days28: data28.data,
          days90: data90.data,
          days365: data365.data
        })
      } catch (error) {
        console.error(`Failed to fetch ${sport} metrics:`, error)
      } finally {
        setLoading(false)
      }
    }

    fetchData()
  }, [sport])

  const renderMiniChart = (data: PerformanceData[], label: string) => (
    <Box sx={{ textAlign: 'center' }}>
      <Typography variant="caption" color="text.secondary" sx={{ mb: 0, display: 'block', fontSize: '0.65rem' }}>
        {label}
      </Typography>
      <ResponsiveContainer width="100%" height={50}>
        <LineChart data={data}>
          <YAxis domain={['auto', 'auto']} hide />
          <Line 
            type="monotone" 
            dataKey="ctl" 
            stroke={config.color} 
            strokeWidth={2}
            dot={false}
          />
        </LineChart>
      </ResponsiveContainer>
    </Box>
  )

  return (
    <Card>
      <CardContent sx={{ pb: 1, '&:last-child': { pb: 1.5 } }}>
        {/* Header with sport icon and name */}
        <Box sx={{ display: 'flex', alignItems: 'center', mb: 1.5 }}>
          <Icon sx={{ fontSize: 28, color: config.color, mr: 1 }} />
          <Typography variant="h6" sx={{ fontWeight: 500, fontSize: '1rem' }}>
            {config.label}
          </Typography>
        </Box>

        {/* ATL, CTL, TSB metrics - Reordered and condensed */}
        <Grid container spacing={1} sx={{ mb: 2 }}>
          <Grid item xs={4}>
            <Box sx={{ textAlign: 'center', p: 0.5, bgcolor: 'action.hover', borderRadius: 1 }}>
              <Typography variant="caption" color="text.secondary" sx={{ textTransform: 'uppercase', fontSize: '0.65rem' }}>
                ATL
              </Typography>
              <Typography variant="h6" sx={{ fontWeight: 600, lineHeight: 1.2 }}>
                {loading ? '-' : Math.round(metrics.atl)}
              </Typography>
              <Typography variant="caption" color="text.secondary" sx={{ fontSize: '0.65rem' }}>
                Fatigue
              </Typography>
            </Box>
          </Grid>
          <Grid item xs={4}>
            <Box sx={{ textAlign: 'center', p: 0.5, bgcolor: 'action.hover', borderRadius: 1 }}>
              <Typography variant="caption" color="text.secondary" sx={{ textTransform: 'uppercase', fontSize: '0.65rem' }}>
                CTL
              </Typography>
              <Typography variant="h6" sx={{ fontWeight: 600, color: config.color, lineHeight: 1.2 }}>
                {loading ? '-' : Math.round(metrics.ctl)}
              </Typography>
              <Typography variant="caption" color="text.secondary" sx={{ fontSize: '0.65rem' }}>
                Fitness
              </Typography>
            </Box>
          </Grid>
          <Grid item xs={4}>
            <Box sx={{ textAlign: 'center', p: 0.5, bgcolor: 'action.hover', borderRadius: 1 }}>
              <Typography variant="caption" color="text.secondary" sx={{ textTransform: 'uppercase', fontSize: '0.65rem' }}>
                TSB
              </Typography>
              <Typography 
                variant="h6" 
                sx={{ 
                  fontWeight: 600,
                  lineHeight: 1.2,
                  color: metrics.tsb > 0 ? '#4caf50' : metrics.tsb < -10 ? '#f44336' : 'text.primary'
                }}
              >
                {loading ? '-' : Math.round(metrics.tsb)}
              </Typography>
              <Typography variant="caption" color="text.secondary" sx={{ fontSize: '0.65rem' }}>
                Form
              </Typography>
            </Box>
          </Grid>
        </Grid>

        {/* Mini CTL charts */}
        <Grid container spacing={1}>
          <Grid item xs={3}>
            {renderMiniChart(chartData.days7, '7d')}
          </Grid>
          <Grid item xs={3}>
            {renderMiniChart(chartData.days28, '28d')}
          </Grid>
          <Grid item xs={3}>
            {renderMiniChart(chartData.days90, '90d')}
          </Grid>
          <Grid item xs={3}>
            {renderMiniChart(chartData.days365, '1y')}
          </Grid>
        </Grid>
      </CardContent>
    </Card>
  )
}
