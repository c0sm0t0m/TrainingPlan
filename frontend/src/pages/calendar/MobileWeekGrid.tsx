import {
  Box,
  Card,
  Typography,
  useTheme,
  alpha,
} from '@mui/material';
import {
  DirectionsRun as RunIcon,
  DirectionsBike as BikeIcon,
  Pool as SwimIcon,
  FitnessCenter as StrengthIcon,
  CheckCircle as CheckCircleIcon,
  Cancel as CancelIcon,
} from '@mui/icons-material';
import { format, addDays, isToday, isPast } from 'date-fns';
import { getSportColor, getTSSColor } from '../../utils/sportColors';

interface Workout {
  id: number;
  date: string;
  sport_type: string;
  title: string;
  target_tss?: number;
  tss?: number;
  duration_minutes?: number;
  is_completed: boolean;
}

interface GarminActivity {
  id: number;
  date: string;
  activity_type: string;
  activity_name: string;
  calculated_tss?: number;
  duration_seconds: number;
}

interface MobileWeekGridProps {
  currentWeekStart: Date;
  workouts: Workout[];
  activities: GarminActivity[];
  onWorkoutClick: (workout: Workout) => void;
  onActivityClick: (activity: GarminActivity) => void;
  onDateClick: (date: Date) => void;
  scrollRef?: React.Ref<HTMLDivElement>;
}

const getSportIcon = (sportType: string) => {
  const type = sportType.toLowerCase();
  if (type.includes('run') || type === 'running') return <RunIcon fontSize="small" />;
  if (type.includes('bike') || type.includes('cycling')) return <BikeIcon fontSize="small" />;
  if (type.includes('swim')) return <SwimIcon fontSize="small" />;
  return <StrengthIcon fontSize="small" />;
};

export default function MobileWeekGrid({
  currentWeekStart,
  workouts,
  activities,
  onWorkoutClick,
  onActivityClick,
  onDateClick,
  scrollRef,
}: MobileWeekGridProps) {
  const theme = useTheme();

  const getDayData = (dayOffset: number) => {
    const date = addDays(currentWeekStart, dayOffset);
    const dateStr = format(date, 'yyyy-MM-dd');
    
    const dayWorkouts = workouts.filter(w => w.date === dateStr);
    const dayActivities = activities.filter(a => a.date === dateStr);
    
    // Calculate TSS: show completed TSS if available, otherwise show target TSS
    const completedTSS = [
      ...dayWorkouts.filter(w => w.is_completed).map(w => w.tss || 0),
      ...dayActivities.map(a => a.calculated_tss || 0)
    ].reduce((sum, tss) => sum + tss, 0);
    
    const targetTSS = dayWorkouts
      .filter(w => !w.is_completed)
      .reduce((sum, w) => sum + (w.target_tss || 0), 0);
    
    const totalTSS = completedTSS > 0 ? completedTSS : targetTSS;
    
    return { date, dateStr, workouts: dayWorkouts, activities: dayActivities, totalTSS, hasTarget: targetTSS > 0 && completedTSS === 0 };
  };

  return (
    <Box
      ref={scrollRef}
      sx={{
        display: 'flex',
        gap: 0.5,
        px: 0.5,
        pt: 2,
        pb: 0,
        width: '100%',
        overflowX: 'auto',
        '&::-webkit-scrollbar': { display: 'none' },
        scrollbarWidth: 'none',
      }}
    >
      {[0, 1, 2, 3, 4, 5, 6].map((dayOffset) => {
        const { date, workouts: dayWorkouts, activities: dayActivities, totalTSS, hasTarget } = getDayData(dayOffset);
        const today = isToday(date);
        const allWorkouts = [...dayWorkouts, ...dayActivities];
        
        return (
          <Card
            key={dayOffset}
            onClick={() => onDateClick(date)}
            sx={{
              flex: '0 0 auto',
              width: 110,
              minHeight: 160,
              p: 1,
              display: 'flex',
              flexDirection: 'column',
              alignItems: 'center',
              cursor: 'pointer',
              transition: 'all 0.2s',
              border: today ? `2px solid ${theme.palette.primary.main}` : '1px solid',
              borderColor: today ? 'primary.main' : 'divider',
              bgcolor: today ? alpha(theme.palette.primary.main, 0.12) : 'background.paper',
              '&:hover': {
                boxShadow: 3,
                transform: 'translateY(-3px)',
              },
              '&:active': {
                transform: 'scale(0.96)',
              },
            }}
          >
            {/* Day Letter */}
            <Typography
              variant="caption"
              sx={{
                fontSize: '0.7rem',
                fontWeight: 600,
                textTransform: 'uppercase',
                color: today ? 'primary.main' : 'text.primary',
                lineHeight: 1,
              }}
            >
              {format(date, 'EEEEE')}
            </Typography>

            {/* Date Number */}
            <Typography
              variant="h6"
              sx={{
                fontSize: '1.25rem',
                fontWeight: 800,
                lineHeight: 1,
                mt: 0.25,
                color: today ? 'primary.main' : 'text.primary',
              }}
            >
              {format(date, 'd')}
            </Typography>

            {/* TSS Badge */}
            {totalTSS > 0 && (
              <Box
                sx={{
                  bgcolor: hasTarget ? alpha(getTSSColor(totalTSS).main, 0.6) : getTSSColor(totalTSS).main,
                  color: 'white',
                  px: 1,
                  py: 0.5,
                  borderRadius: 1.5,
                  fontSize: '0.75rem',
                  fontWeight: 700,
                  lineHeight: 1,
                  mt: 0.5,
                  boxShadow: '0 2px 4px rgba(0,0,0,0.15)',
                  minWidth: 32,
                  textAlign: 'center',
                }}
              >
                {Math.round(totalTSS)}
              </Box>
            )}

            {/* Workout Icons (stacked vertically, max 3 visible) */}
            <Box
              sx={{
                display: 'flex',
                flexDirection: 'column',
                alignItems: 'center',
                gap: 0.5,
                mt: 0.75,
                flex: 1,
                overflow: 'hidden',
              }}
            >
              {/* Completed Activities first (always visible — not crowded out by plans) */}
              {dayActivities.slice(0, 3).map((activity) => {
                const sportColor = getSportColor(activity.activity_type).main;
                
                return (
                  <Box
                    key={`activity-${activity.id}`}
                    onClick={(e) => {
                      e.stopPropagation();
                      onActivityClick(activity);
                    }}
                    sx={{
                      position: 'relative',
                      width: 28,
                      height: 28,
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                      borderRadius: '50%',
                      bgcolor: alpha(sportColor, 0.25),
                      border: `2px solid ${sportColor}`,
                      color: sportColor,
                      cursor: 'pointer',
                      '& svg': {
                        fontSize: '0.875rem',
                      },
                      '&:hover': {
                        opacity: 0.9,
                      },
                      '&:active': {
                        transform: 'scale(0.9)',
                      },
                    }}
                  >
                    {getSportIcon(activity.activity_type)}
                  </Box>
                );
              })}

              {/* Planned Workouts — fill remaining icon slots */}
              {dayWorkouts.slice(0, Math.max(0, 3 - Math.min(dayActivities.length, 3))).map((workout) => {
                const isMissed = isPast(new Date(workout.date)) && !workout.is_completed && !isToday(new Date(workout.date));
                const sportColor = getSportColor(workout.sport_type).main;
                
                return (
                  <Box
                    key={`workout-${workout.id}`}
                    onClick={(e) => {
                      e.stopPropagation();
                      onWorkoutClick(workout);
                    }}
                    sx={{
                      position: 'relative',
                      width: 28,
                      height: 28,
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                      borderRadius: '50%',
                      bgcolor: isMissed 
                        ? 'error.main'
                        : workout.is_completed
                        ? alpha(sportColor, 0.25)
                        : 'transparent',
                      border: isMissed
                        ? 'none'
                        : workout.is_completed
                        ? `2px solid ${sportColor}`
                        : `2px dashed ${alpha(sportColor, 0.6)}`,
                      color: isMissed ? 'white' : sportColor,
                      cursor: 'pointer',
                      '& svg': {
                        fontSize: '0.875rem',
                      },
                      '&:hover': {
                        opacity: 0.9,
                      },
                      '&:active': {
                        transform: 'scale(0.9)',
                      },
                    }}
                  >
                    {isMissed ? (
                      <CancelIcon sx={{ fontSize: 14, color: 'white' }} />
                    ) : (
                      <>
                        {getSportIcon(workout.sport_type)}
                        {workout.is_completed && (
                          <CheckCircleIcon
                            sx={{
                              position: 'absolute',
                              bottom: -2,
                              right: -2,
                              fontSize: 10,
                              bgcolor: 'white',
                              borderRadius: '50%',
                              color: sportColor,
                            }}
                          />
                        )}
                      </>
                    )}
                  </Box>
                );
              })}

              {/* Show overflow count */}
              {allWorkouts.length > 3 && (
                <Typography
                  variant="caption"
                  sx={{
                    fontSize: '0.6rem',
                    fontWeight: 600,
                    color: 'text.secondary',
                    mt: 0.25,
                  }}
                >
                  +{allWorkouts.length - 3}
                </Typography>
              )}

              {/* Empty State */}
              {allWorkouts.length === 0 && (
                <Box
                  sx={{
                    width: 28,
                    height: 28,
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    borderRadius: '50%',
                    border: '2px dashed',
                    borderColor: 'divider',
                    mt: 0.5,
                  }}
                >
                  <Typography variant="caption" color="text.disabled" sx={{ fontSize: '0.75rem' }}>
                    —
                  </Typography>
                </Box>
              )}
            </Box>
          </Card>
        );
      })}
    </Box>
  );
}
