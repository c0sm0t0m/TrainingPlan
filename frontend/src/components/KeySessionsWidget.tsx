import React, { useEffect, useState } from 'react'
import {
  Card,
  CardContent,
  Typography,
  Box,
  CircularProgress,
  Alert,
} from '@mui/material'
import { FitnessCenter } from '@mui/icons-material'
import {
  ScatterChart,
  Scatter,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  ZAxis,
} from 'recharts'
import api from '../services/api'

interface KeySession {
  activity_id: number
  date: string
  activity_name: string
  sport_type: string
  duration_minutes: number
  distance_km: number | null
  avg_heart_rate: number
  max_heart_rate: number | null
  avg_pace: number | null
  threshold_estimate: number
  threshold_pace: number | null
  estimation_method: string
  confidence_score: number
  intensity_factor: number | null
  tss: number | null
  training_load: number | null
  calories: number | null
  notes: string | null
}

interface KeySessionsWidgetProps {
  sport?: string
  limit?: number
  daysBack?: number
}

// Custom tooltip component
const CustomTooltip = ({ active, payload }: any) => {
  if (active && payload && payload.length) {
    const session = payload[0].payload as KeySession
    
    const formatPace = (paceMinPerKm: number | null): string => {
      if (!paceMinPerKm) return 'N/A'
      const minutes = Math.floor(paceMinPerKm)
      const seconds = Math.round((paceMinPerKm - minutes) * 60)
      return `${minutes}:${seconds.toString().padStart(2, '0')}`
    }

    const formatDuration = (minutes: number) => {
      const hours = Math.floor(minutes / 60)
      const mins = Math.round(minutes % 60)
      return hours > 0 ? `${hours}h ${mins}m` : `${mins}m`
    }

    return (
      <Box
        sx={{
          bgcolor: 'background.paper',
          p: 2,
          border: 1,
          borderColor: 'divider',
          borderRadius: 1,
          boxShadow: 2,
        }}
      >
        <Typography variant="subtitle2" sx={{ fontWeight: 600, mb: 1 }}>
          {session.activity_name}
        </Typography>
        <Typography variant="body2" color="text.secondary" sx={{ mb: 1 }}>
          {new Date(session.date).toLocaleDateString()}
        </Typography>
        <Box sx={{ display: 'grid', gridTemplateColumns: 'auto 1fr', gap: 0.5, fontSize: '0.875rem' }}>
          <Typography variant="body2" sx={{ fontWeight: 600 }}>Duration:</Typography>
          <Typography variant="body2">{formatDuration(session.duration_minutes)}</Typography>
          
          <Typography variant="body2" sx={{ fontWeight: 600 }}>Avg HR:</Typography>
          <Typography variant="body2">{session.avg_heart_rate} bpm</Typography>
          
          <Typography variant="body2" sx={{ fontWeight: 600 }}>Avg Pace:</Typography>
          <Typography variant="body2">{formatPace(session.avg_pace)} /km</Typography>
          
          <Typography variant="body2" sx={{ fontWeight: 600 }}>IF:</Typography>
          <Typography variant="body2">
            {session.intensity_factor ? session.intensity_factor.toFixed(2) : 'N/A'}
          </Typography>
          
          <Typography variant="body2" sx={{ fontWeight: 600 }}>TSS:</Typography>
          <Typography variant="body2" color="primary.main" sx={{ fontWeight: 600 }}>
            {session.tss ? session.tss.toFixed(0) : 'N/A'}
          </Typography>
        </Box>
      </Box>
    )
  }

  return null
}

export default function KeySessionsWidget({ 
  sport = 'running', 
  limit = 10, 
  daysBack = 90 
}: KeySessionsWidgetProps) {
  const [sessions, setSessions] = useState<KeySession[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    const fetchKeySessions = async () => {
      try {
        setLoading(true)
        setError(null)
        
        const response = await api.get('/analytics/key-sessions', {
          params: { sport, limit, days_back: daysBack }
        })
        
        setSessions(response.data.sessions)
      } catch (err: any) {
        console.error('Failed to fetch key sessions:', err)
        setError(err.response?.data?.detail || 'Failed to load key sessions')
      } finally {
        setLoading(false)
      }
    }

    fetchKeySessions()
  }, [sport, limit, daysBack])

  // Calculate date range based on daysBack
  const endDate = new Date()
  const startDate = new Date()
  startDate.setDate(startDate.getDate() - daysBack)
  
  const minTimestamp = startDate.getTime()
  const maxTimestamp = endDate.getTime()

  // Prepare chart data - sort by date ascending for proper time series
  const chartData = sessions
    .filter(s => s.tss !== null)
    .sort((a, b) => new Date(a.date).getTime() - new Date(b.date).getTime())
    .map(session => ({
      ...session,
      timestamp: new Date(session.date).getTime(),
      dateFormatted: new Date(session.date).toLocaleDateString('en-US', { 
        month: 'short', 
        day: 'numeric' 
      }),
    }))
  
  // DEBUG: Log sessions received from API
  React.useEffect(() => {
    if (sessions.length > 0) {
      console.log(`[KeySessions] Received ${sessions.length} sessions from API`)
      console.log('[KeySessions] Date range:', sessions.map(s => s.date).sort())
      console.log('[KeySessions] First session:', sessions[0])
      console.log('[KeySessions] Last session:', sessions[sessions.length - 1])
    }
  }, [sessions])

  return (
    <Card>
      <CardContent>
        <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
          <FitnessCenter sx={{ mr: 1, color: 'primary.main' }} />
          <Typography variant="h6">
            Key {sport.charAt(0).toUpperCase() + sport.slice(1)} Sessions
          </Typography>
        </Box>

        <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
          Training Stress Score (TSS) over time from key sessions
        </Typography>

        {loading && (
          <Box sx={{ display: 'flex', justifyContent: 'center', py: 3 }}>
            <CircularProgress />
          </Box>
        )}

        {error && (
          <Alert severity="error" sx={{ mb: 2 }}>
            {error}
          </Alert>
        )}

        {!loading && !error && sessions.length === 0 && (
          <Alert severity="info">
            No key sessions found in the last {daysBack} days.
          </Alert>
        )}

        {!loading && !error && chartData.length > 0 && (
          <Box sx={{ width: '100%', height: 400 }}>
            <ResponsiveContainer width="100%" height="100%">
              <ScatterChart
                margin={{ top: 20, right: 20, bottom: 20, left: 20 }}
              >
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis
                  dataKey="timestamp"
                  type="number"
                  domain={[minTimestamp, maxTimestamp]}
                  tickFormatter={(timestamp) => {
                    const date = new Date(timestamp)
                    return `${date.getMonth() + 1}/${date.getDate()}`
                  }}
                  label={{ value: 'Date', position: 'insideBottom', offset: -10 }}
                />
                <YAxis
                  dataKey="tss"
                  type="number"
                  domain={[0, 'dataMax + 10']}
                  label={{ value: 'TSS', angle: -90, position: 'insideLeft' }}
                />
                <ZAxis range={[100, 400]} />
                <Tooltip content={<CustomTooltip />} />
                <Scatter
                  name="Key Sessions"
                  data={chartData}
                  fill="#f44336"
                  fillOpacity={0.7}
                  stroke="#d32f2f"
                  strokeWidth={2}
                />
              </ScatterChart>
            </ResponsiveContainer>
          </Box>
        )}
      </CardContent>
    </Card>
  )
}
