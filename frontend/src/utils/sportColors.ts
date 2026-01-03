// Sport-specific colors following TrainingPeaks pattern
export const SPORT_COLORS = {
  running: {
    main: '#4CAF50',    // Green
    light: '#E8F5E9',
    dark: '#2E7D32',
  },
  cycling: {
    main: '#FF9800',    // Orange
    light: '#FFF3E0',
    dark: '#E65100',
  },
  swimming: {
    main: '#2196F3',    // Blue
    light: '#E3F2FD',
    dark: '#1565C0',
  },
  strength: {
    main: '#9C27B0',    // Purple
    light: '#F3E5F5',
    dark: '#6A1B9A',
  },
  other: {
    main: '#607D8B',    // Grey
    light: '#ECEFF1',
    dark: '#37474F',
  },
} as const

export type SportType = keyof typeof SPORT_COLORS

export const getSportColor = (sport: string) => {
  const normalizedSport = sport.toLowerCase().replace(/[_-]/g, '') as SportType
  
  // Map common variations
  if (normalizedSport.includes('run')) return SPORT_COLORS.running
  if (normalizedSport.includes('bike') || normalizedSport.includes('cycl')) return SPORT_COLORS.cycling
  if (normalizedSport.includes('swim')) return SPORT_COLORS.swimming
  if (normalizedSport.includes('strength') || normalizedSport.includes('gym')) return SPORT_COLORS.strength
  
  return SPORT_COLORS[normalizedSport as SportType] || SPORT_COLORS.other
}

// TSS color coding following TrainingPeaks pattern
// Sport icon emojis
export const getSportIcon = (sport: string) => {
  const normalizedSport = sport.toLowerCase().replace(/[_\s-]/g, '')
  
  if (normalizedSport.includes('run')) return '🏃'
  if (normalizedSport.includes('bike') || normalizedSport.includes('cycl')) return '🚴'
  if (normalizedSport.includes('swim')) return '🏊'
  if (normalizedSport.includes('strength') || normalizedSport.includes('gym')) return '💪'
  
  return '⚪'
}

// TSS color coding with proper color values
export const getTSSColor = (tss: number) => {
  if (tss === 0) return { main: '#9e9e9e', label: 'Rest' }
  if (tss < 50) return { main: '#4caf50', label: 'Easy' }
  if (tss < 100) return { main: '#2196f3', label: 'Moderate' }
  if (tss < 150) return { main: '#ff9800', label: 'Hard' }
  return { main: '#f44336', label: 'Very Hard' }
}

export const getTSSBackgroundColor = (tss: number) => {
  if (tss === 0) return '#fafafa'
  if (tss < 50) return '#e8f5e9'
  if (tss < 100) return '#e3f2fd'
  if (tss < 150) return '#fff3e0'
  return '#ffebee'
}

// Workout status colors
export const WORKOUT_STATUS_COLORS = {
  planned: {
    border: '2px dashed',
    borderColor: 'primary.main',
    bgcolor: 'background.paper',
    opacity: 0.8,
  },
  completed: {
    border: '2px solid',
    borderColor: 'success.main',
    bgcolor: 'success.light',
    opacity: 1,
  },
  skipped: {
    border: '1px solid',
    borderColor: 'grey.400',
    bgcolor: 'grey.100',
    opacity: 0.5,
  },
} as const
