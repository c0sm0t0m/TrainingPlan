import {
  Box,
  Typography,
  useTheme,
} from '@mui/material';
import {
  startOfMonth,
  endOfMonth,
  eachDayOfInterval,
  format,
  isSameMonth,
  isToday,
  startOfWeek,
  endOfWeek,
} from 'date-fns';
import { getTSSColor } from '../../utils/sportColors';

interface Workout {
  id: number;
  date: string;
  sport_type: string;
  target_tss?: number;
  tss?: number;
  is_completed?: boolean;
}

interface GarminActivity {
  id: number;
  date: string;
  activity_type: string;
  calculated_tss?: number;
}

interface MonthCalendarViewProps {
  currentMonth: Date;
  workouts: Workout[];
  activities: GarminActivity[];
  onDateClick: (date: Date) => void;
}

const getSportColorDot = (sportType: string): string => {
  const type = sportType.toLowerCase();
  if (type.includes('run')) return '#f44336'; // red
  if (type.includes('bike') || type.includes('cycling')) return '#2196f3'; // blue
  if (type.includes('swim')) return '#4caf50'; // green
  return '#9e9e9e'; // grey for strength/other
};

export default function MonthCalendarView({
  currentMonth,
  workouts,
  activities,
  onDateClick,
}: MonthCalendarViewProps) {
  const theme = useTheme();

  // Get all days to display (including padding days from previous/next month)
  const monthStart = startOfMonth(currentMonth);
  const monthEnd = endOfMonth(currentMonth);
  const calendarStart = startOfWeek(monthStart, { weekStartsOn: 1 }); // Monday
  const calendarEnd = endOfWeek(monthEnd, { weekStartsOn: 1 });
  
  const allDays = eachDayOfInterval({ start: calendarStart, end: calendarEnd });

  const getDayData = (date: Date) => {
    const dateStr = format(date, 'yyyy-MM-dd');
    
    const dayWorkouts = workouts.filter(w => w.date === dateStr);
    const dayActivities = activities.filter(a => a.date === dateStr);
    
    // Show completed TSS if available, otherwise show target TSS
    const completedTSS = [
      ...dayWorkouts.filter(w => w.is_completed).map(w => w.tss || 0),
      ...dayActivities.map(a => a.calculated_tss || 0)
    ].reduce((sum, tss) => sum + tss, 0);
    
    const targetTSS = dayWorkouts
      .filter(w => !w.is_completed)
      .reduce((sum, w) => sum + (w.target_tss || 0), 0);
    
    const totalTSS = completedTSS > 0 ? completedTSS : targetTSS;
    
    // Get unique sports for dot indicators
    const sports = new Set([
      ...dayWorkouts.map(w => w.sport_type),
      ...dayActivities.map(a => a.activity_type)
    ]);
    
    return { totalTSS, sports: Array.from(sports), hasTarget: targetTSS > 0 && completedTSS === 0 };
  };

  const getHeatmapColor = (tss: number): string => {
    if (tss === 0) return 'transparent';
    if (tss < 30) return getTSSColor(30); // Light
    if (tss < 60) return getTSSColor(60); // Moderate
    if (tss < 100) return getTSSColor(100); // Hard
    return getTSSColor(150); // Very hard
  };

  return (
    <Box sx={{ px: 2, pb: 2 }}>
      {/* Day Names Header */}
      <Box
        sx={{
          display: 'grid',
          gridTemplateColumns: 'repeat(7, 1fr)',
          gap: 0.5,
          mb: 1,
        }}
      >
        {['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'].map((day) => (
          <Typography
            key={day}
            variant="caption"
            sx={{
              textAlign: 'center',
              fontWeight: 600,
              fontSize: '0.7rem',
              color: 'text.secondary',
            }}
          >
            {day}
          </Typography>
        ))}
      </Box>

      {/* Calendar Grid */}
      <Box
        sx={{
          display: 'grid',
          gridTemplateColumns: 'repeat(7, 1fr)',
          gap: 0.5,
        }}
      >
        {allDays.map((day) => {
          const today = isToday(day);
          const currentMonthDay = isSameMonth(day, currentMonth);
          const { totalTSS, sports, hasTarget } = getDayData(day);
          
          return (
            <Box
              key={day.toISOString()}
              onClick={() => onDateClick(day)}
              sx={{
                aspectRatio: '1',
                borderRadius: 1,
                bgcolor: currentMonthDay ? getHeatmapColor(totalTSS) : 'transparent',
                border: today ? `2px solid ${theme.palette.primary.main}` : '1px solid',
                borderColor: today ? 'primary.main' : currentMonthDay ? 'divider' : 'transparent',
                display: 'flex',
                flexDirection: 'column',
                alignItems: 'center',
                justifyContent: 'center',
                position: 'relative',
                cursor: 'pointer',
                transition: 'all 0.2s',
                opacity: currentMonthDay ? (hasTarget ? 0.7 : 1) : 0.3,
                '&:active': {
                  transform: 'scale(0.95)',
                },
              }}
            >
              {/* Date Number */}
              <Typography
                variant="body2"
                sx={{
                  fontWeight: today ? 700 : 600,
                  fontSize: '0.85rem',
                  color: totalTSS > 100 ? 'primary.contrastText' : currentMonthDay ? 'text.primary' : 'text.secondary',
                }}
              >
                {format(day, 'd')}
              </Typography>

              {/* TSS Badge */}
              {totalTSS > 0 && (
                <Typography
                  variant="caption"
                  sx={{
                    fontSize: '0.6rem',
                    fontWeight: 600,
                    color: totalTSS > 100 ? 'primary.contrastText' : 'text.secondary',
                  }}
                >
                  {Math.round(totalTSS)}
                </Typography>
              )}

              {/* Sport Dots */}
              {sports.length > 0 && (
                <Box
                  sx={{
                    position: 'absolute',
                    bottom: 2,
                    display: 'flex',
                    gap: 0.25,
                  }}
                >
                  {sports.slice(0, 3).map((sport, i) => (
                    <Box
                      key={i}
                      sx={{
                        width: 4,
                        height: 4,
                        borderRadius: '50%',
                        bgcolor: getSportColorDot(sport),
                        border: totalTSS > 100 ? '0.5px solid white' : 'none',
                      }}
                    />
                  ))}
                </Box>
              )}
            </Box>
          );
        })}
      </Box>
    </Box>
  );
}
