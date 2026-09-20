import { Card, CardContent, Typography, Box, useMediaQuery, useTheme } from '@mui/material'
import { TrendingUp, TrendingDown, TrendingFlat } from '@mui/icons-material'

interface MetricCardProps {
  title: string
  value: number | string
  unit?: string
  trend?: 'up' | 'down' | 'flat'
  trendValue?: string
  color?: string
  icon?: React.ReactNode
  compact?: boolean
  subtitle?: string
}

export default function MetricCard({
  title,
  value,
  unit = '',
  trend,
  trendValue,
  color = 'primary.main',
  icon,
  compact = false,
  subtitle,
}: MetricCardProps) {
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('sm'));
  const shouldCompact = compact && isMobile;

  const getTrendIcon = () => {
    if (trend === 'up') return <TrendingUp sx={{ fontSize: shouldCompact ? 12 : 16, color: 'success.main' }} />
    if (trend === 'down') return <TrendingDown sx={{ fontSize: shouldCompact ? 12 : 16, color: 'error.main' }} />
    if (trend === 'flat') return <TrendingFlat sx={{ fontSize: shouldCompact ? 12 : 16, color: 'text.secondary' }} />
    return null
  }

  return (
    <Card sx={{ height: '100%', minHeight: shouldCompact ? 100 : 120 }}>
      <CardContent sx={{ p: shouldCompact ? 1.5 : 2, '&:last-child': { pb: shouldCompact ? 1.5 : 2 } }}>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', mb: shouldCompact ? 0.5 : 2 }}>
          <Typography 
            variant={shouldCompact ? 'caption' : 'body2'} 
            color="text.secondary" 
            fontWeight={500}
            sx={{ 
              fontSize: shouldCompact ? '0.65rem' : undefined,
              lineHeight: shouldCompact ? 1.2 : undefined 
            }}
          >
            {title}
          </Typography>
          {icon && !shouldCompact && <Box sx={{ color }}>{icon}</Box>}
        </Box>

        <Box sx={{ display: 'flex', alignItems: 'baseline', gap: 0.5, mb: shouldCompact ? 0.5 : 1 }}>
          <Typography 
            variant={shouldCompact ? 'h6' : 'h4'} 
            fontWeight={600} 
            sx={{ 
              color,
              fontSize: shouldCompact ? '1.25rem' : undefined 
            }}
          >
            {typeof value === 'number' ? value.toFixed(1) : value}
          </Typography>
          {unit && (
            <Typography 
              variant={shouldCompact ? 'caption' : 'body2'} 
              color="text.secondary"
              sx={{ fontSize: shouldCompact ? '0.65rem' : undefined }}
            >
              {unit}
            </Typography>
          )}
        </Box>

        {subtitle && (
          <Typography 
            variant="caption" 
            color="text.secondary"
            sx={{ 
              fontSize: shouldCompact ? '0.65rem' : '0.75rem',
              display: 'block',
              mt: shouldCompact ? 0.5 : 0.5
            }}
          >
            {subtitle}
          </Typography>
        )}

        {trend && trendValue && !shouldCompact && (
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
