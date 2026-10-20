import { Card, CardContent, Box, Typography, Chip } from '@mui/material'
import { CheckCircle, DirectionsRun, DirectionsBike, Pool, SportsTennis, FitnessCenter } from '@mui/icons-material'
import { getSportColor, getTSSColor } from '../utils/sportColors'

interface WorkoutCardProps {
  title: string
  sport: string
  duration?: number
  distance?: number
  intensity?: string
  tss?: number
  isCompleted?: boolean
  onClick?: () => void
  draggable?: boolean
  onDragStart?: (e: React.DragEvent) => void
  onDragOver?: (e: React.DragEvent) => void
  onDrop?: (e: React.DragEvent) => void
}

const SportIcon = ({ sport }: { sport: string }) => {
  const normalizedSport = sport.toLowerCase().replace(/[_\s-]/g, '')
  
  if (normalizedSport.includes('run')) return <DirectionsRun />
  if (normalizedSport.includes('bike') || normalizedSport.includes('cycl')) return <DirectionsBike />
  if (normalizedSport.includes('swim')) return <Pool />
  if (normalizedSport.includes('tennis')) return <SportsTennis />
  if (normalizedSport.includes('strength') || normalizedSport.includes('gym')) return <FitnessCenter />
  
  return <FitnessCenter />
}

export default function WorkoutCard({
  title,
  sport,
  duration,
  distance,
  intensity,
  tss,
  isCompleted = false,
  onClick,
  draggable = false,
  onDragStart,
  onDragOver,
  onDrop,
}: WorkoutCardProps) {
  const sportColor = getSportColor(sport)
  const tssColor = tss ? getTSSColor(tss) : null

  return (
    <Card
      draggable={draggable}
      onDragStart={onDragStart}
      onDragOver={onDragOver}
      onDrop={onDrop}
      sx={{
        border: isCompleted ? '2px solid' : '2px dashed',
        borderColor: isCompleted ? sportColor.main : sportColor.main,
        bgcolor: isCompleted ? sportColor.light : 'background.paper',
        opacity: isCompleted ? 1 : 0.85,
        cursor: onClick ? (draggable ? 'grab' : 'pointer') : 'default',
        transition: 'all 0.2s',
        '&:hover': onClick
          ? {
              transform: 'translateY(-2px)',
              boxShadow: 3,
            }
          : {},
      }}
      onClick={onClick}
    >
      <CardContent sx={{ p: 1.5, '&:last-child': { pb: 1.5 } }}>
        {/* Header */}
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 0.5 }}>
          <SportIcon sport={sport} />
          {isCompleted && <CheckCircle fontSize="small" sx={{ color: sportColor.dark }} />}
          <Typography
            variant="body2"
            fontWeight={isCompleted ? 600 : 500}
            sx={{ flexGrow: 1, color: isCompleted ? sportColor.dark : 'text.primary' }}
          >
            {title}
          </Typography>
        </Box>

        {/* Details */}
        <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.5, alignItems: 'center' }}>
          {duration && (
            <Typography variant="caption" color="text.secondary">
              {duration} min
            </Typography>
          )}
          {distance && (
            <>
              <Typography variant="caption" color="text.secondary">
                •
              </Typography>
              <Typography variant="caption" color="text.secondary">
                {distance} km
              </Typography>
            </>
          )}
          {intensity && (
            <>
              <Typography variant="caption" color="text.secondary">
                •
              </Typography>
              <Typography variant="caption" color="text.secondary">
                {intensity}
              </Typography>
            </>
          )}
        </Box>

        {/* TSS Badge - Always show if provided, even if 0 */}
        {tss !== undefined && (
          <Box sx={{ mt: 1 }}>
            <Chip
              label={tss > 0 ? `TSS ${tss}` : `TSS -`}
              size="small"
              sx={{
                bgcolor: tss > 0 && tssColor ? tssColor.main : 'action.disabled',
                color: tss > 0 && tssColor ? (tssColor.contrastText || '#fff') : 'text.secondary',
                fontWeight: 600,
                height: 20,
                fontSize: '0.7rem',
              }}
            />
          </Box>
        )}
      </CardContent>
    </Card>
  )
}
