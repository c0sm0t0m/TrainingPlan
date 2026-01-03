import { Card, CardContent, Typography, Box } from '@mui/material'
import { TrendingUp, TrendingDown, TrendingFlat } from '@mui/icons-material'

interface MetricCardProps {
  title: string
  value: number | string
  unit?: string
  trend?: 'up' | 'down' | 'flat'
  trendValue?: string
  color?: string
  icon?: React.ReactNode
}

export default function MetricCard({
  title,
  value,
  unit = '',
  trend,
  trendValue,
  color = 'primary.main',
  icon,
}: MetricCardProps) {
  const getTrendIcon = () => {
    if (trend === 'up') return <TrendingUp sx={{ fontSize: 16, color: '#4caf50' }} />
    if (trend === 'down') return <TrendingDown sx={{ fontSize: 16, color: '#f44336' }} />
    if (trend === 'flat') return <TrendingFlat sx={{ fontSize: 16, color: '#757575' }} />
    return null
  }

  return (
    <Card sx={{ height: '100%' }}>
      <CardContent>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', mb: 2 }}>
          <Typography variant="body2" color="text.secondary" fontWeight={500}>
            {title}
          </Typography>
          {icon && <Box sx={{ color }}>{icon}</Box>}
        </Box>

        <Box sx={{ display: 'flex', alignItems: 'baseline', gap: 0.5, mb: 1 }}>
          <Typography variant="h4" fontWeight={600} sx={{ color }}>
            {typeof value === 'number' ? value.toFixed(1) : value}
          </Typography>
          {unit && (
            <Typography variant="body2" color="text.secondary">
              {unit}
            </Typography>
          )}
        </Box>

        {trend && trendValue && (
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
            {getTrendIcon()}
            <Typography variant="caption" color="text.secondary">
              {trendValue}
            </Typography>
          </Box>
        )}
      </CardContent>
    </Card>
  )
}
