import React, { useEffect, useState } from 'react';
import {
  Box,
  Button,
  Card,
  CardContent,
  Container,
  Typography,
  Grid,
  Chip,
  Alert,
  IconButton,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
} from '@mui/material';
import {
  ChevronLeft as ChevronLeftIcon,
  ChevronRight as ChevronRightIcon,
  CheckCircle as CheckCircleIcon,
  DirectionsRun as RunIcon,
  DirectionsBike as BikeIcon,
  Pool as SwimIcon,
  FitnessCenter as StrengthIcon,
} from '@mui/icons-material';
import { useNavigate } from 'react-router-dom';
import { useAuthStore } from '../store/authStore';
import api from '../services/api';
import WorkoutCard from '../components/WorkoutCard';
import { getSportColor, getTSSColor } from '../utils/sportColors';

interface Workout {
  id: number;
  training_plan_id: number;
  date: string;
  sport_type: string;
  workout_type: string;
  title: string;
  description?: string;
  duration_minutes?: number;
  distance_km?: number;
  intensity_zone?: string;
  is_completed: boolean;
  tss?: number; // TODO: Add to backend model
  actual_duration_minutes?: number;
  actual_distance_km?: number;
  notes?: string;
}

interface GarminActivity {
  id: number;
  garmin_activity_id: string;
  activity_name: string;
  activity_type: string;
  sport_type_id?: number;
  start_time_local: string;
  date: string;
  duration_seconds: number; // Backend uses duration_seconds
  moving_duration_seconds?: number;
  elapsed_duration_seconds?: number;
  distance_meters?: number; // Backend uses distance_meters
  calories?: number;
  average_hr?: number;
  max_hr?: number;
  elevation_gain_meters?: number;
  average_speed_mps?: number;
  average_power_watts?: number;
  normalized_power_watts?: number; // Normalized Power (NP)
  threshold_power_watts?: number; // FTP
  location_name?: string;
  training_load?: number; // Garmin's training load
  calculated_tss?: number; // Our calculated TSS
}

interface TrainingPlan {
  id: number;
  name: string;
  sport_type: string;
  workouts: Workout[];
}

const Calendar: React.FC = () => {
  const navigate = useNavigate();
  const { user } = useAuthStore();
  const [currentWeekStart, setCurrentWeekStart] = useState<Date>(() => {
    // Start from the Monday of current week
    const today = new Date();
    const dayOfWeek = today.getDay();
    const diff = dayOfWeek === 0 ? -6 : 1 - dayOfWeek; // If Sunday, go back 6 days, else go to Monday
    const monday = new Date(today);
    monday.setDate(today.getDate() + diff);
    monday.setHours(0, 0, 0, 0);
    return monday;
  });
  const [weeksToShow] = useState(104); // Show 104 weeks (2 years) for scrolling
  const [plans, setPlans] = useState<TrainingPlan[]>([]);
  const [workouts, setWorkouts] = useState<Workout[]>([]);
  const [activities, setActivities] = useState<GarminActivity[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedWorkout, setSelectedWorkout] = useState<Workout | null>(null);
  const [selectedActivity, setSelectedActivity] = useState<GarminActivity | null>(null);
  const [detailDialogOpen, setDetailDialogOpen] = useState(false);
  const calendarCardRef = React.useRef<HTMLDivElement>(null);

  // Memoize weeks generation to avoid recalculating on every scroll
  const generateWeeks = React.useMemo(() => {
    const weeks: Date[] = [];
    const today = new Date();
    const yearAgo = new Date(today);
    yearAgo.setFullYear(today.getFullYear() - 1);
    
    // Find Monday of that week
    const dayOfWeek = yearAgo.getDay();
    const diff = dayOfWeek === 0 ? -6 : 1 - dayOfWeek;
    const startDate = new Date(yearAgo);
    startDate.setDate(yearAgo.getDate() + diff);
    startDate.setHours(0, 0, 0, 0);
    
    for (let i = 0; i < weeksToShow; i++) {
      const weekStart = new Date(startDate);
      weekStart.setDate(startDate.getDate() + (i * 7));
      weeks.push(weekStart);
    }
    return weeks;
  }, [weeksToShow]);

  useEffect(() => {
    document.title = 'Training Calendar - TrainingPlan';
  }, []);

  useEffect(() => {
    if (!user) {
      navigate('/login');
      return;
    }
    fetchData();
  }, [user, navigate]); // Remove currentDate dependency - load all data once

  // Scroll to today's week when calendar loads
  useEffect(() => {
    if (!loading && calendarCardRef.current) {
      const today = new Date();
      const dayOfWeek = today.getDay();
      const diff = dayOfWeek === 0 ? -6 : 1 - dayOfWeek;
      const monday = new Date(today);
      monday.setDate(today.getDate() + diff);
      monday.setHours(0, 0, 0, 0);
      
      setTimeout(() => {
        const weekElement = document.getElementById(`week-${monday.getTime()}`);
        const cardElement = calendarCardRef.current;
        if (weekElement && cardElement) {
          const weekTop = weekElement.offsetTop;
          cardElement.scrollTo({ top: weekTop - 180, behavior: 'auto' });
        }
      }, 100);
    }
  }, [loading]);

  // Update month display when scrolling
  useEffect(() => {
    const cardElement = calendarCardRef.current;
    if (!cardElement) return;

    let scrollTimeout: NodeJS.Timeout;
    const handleScroll = () => {
      // Debounce scroll handler for better performance
      clearTimeout(scrollTimeout);
      scrollTimeout = setTimeout(() => {
        const scrollTop = cardElement.scrollTop;
        
        // Find the first visible week
        for (const weekStart of generateWeeks) {
          const weekElement = document.getElementById(`week-${weekStart.getTime()}`);
          if (weekElement) {
            const weekTop = weekElement.offsetTop;
            const weekHeight = weekElement.offsetHeight;
            
            // Check if this week is in the visible area (with same offset as scroll navigation)
            if (weekTop + weekHeight > scrollTop + 180) {
              // Update month display if it changed
              if (currentWeekStart.getTime() !== weekStart.getTime()) {
                setCurrentWeekStart(weekStart);
              }
              break;
            }
          }
        }
      }, 100); // Debounce by 100ms
    };

    cardElement.addEventListener('scroll', handleScroll);
    return () => {
      clearTimeout(scrollTimeout);
      cardElement.removeEventListener('scroll', handleScroll);
    };
  }, [currentWeekStart, generateWeeks]);

  const fetchData = async () => {
    try {
      setLoading(true);
      
      // Fetch planned workouts
      const response = await api.get('/training-plans');
      const allPlans = response.data;
      
      const plansWithWorkouts = await Promise.all(
        allPlans.map(async (plan: any) => {
          const detailResponse = await api.get(`/training-plans/${plan.id}`);
          return detailResponse.data;
        })
      );
      
      setPlans(plansWithWorkouts);
      const allWorkouts = plansWithWorkouts.flatMap((plan: TrainingPlan) => plan.workouts);
      setWorkouts(allWorkouts);
      
      // Fetch completed activities for wider range (12 months)
      const today = new Date();
      const twelveMonthsAgo = new Date(today);
      twelveMonthsAgo.setMonth(today.getMonth() - 12);
      
      const startDate = twelveMonthsAgo.toISOString().split('T')[0];
      const endDate = today.toISOString().split('T')[0];
      
      try {
        const activitiesResponse = await api.get('/garmin/activities/by-date-range', {
          params: { start_date: startDate, end_date: endDate }
        });
        setActivities(activitiesResponse.data);
      } catch (actErr: any) {
        console.log('No Garmin activities loaded:', actErr.response?.data?.detail);
        setActivities([]);
      }
      
      setError(null);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to load calendar data');
    } finally {
      setLoading(false);
    }
  };

  const getDaysInMonth = (date: Date) => {
    const year = date.getFullYear();
    const month = date.getMonth();
    const firstDay = new Date(year, month, 1);
    const lastDay = new Date(year, month + 1, 0);
    const daysInMonth = lastDay.getDate();
    const startDayOfWeek = firstDay.getDay();
    
    return { daysInMonth, startDayOfWeek };
  };

  const getWorkoutsForDate = (date: Date) => {
    // Format date as YYYY-MM-DD without timezone conversion
    const year = date.getFullYear();
    const month = String(date.getMonth() + 1).padStart(2, '0');
    const day = String(date.getDate()).padStart(2, '0');
    const dateStr = `${year}-${month}-${day}`;
    return workouts.filter((w) => w.date === dateStr);
  };

  const getActivitiesForDate = (date: Date) => {
    const year = date.getFullYear();
    const month = String(date.getMonth() + 1).padStart(2, '0');
    const day = String(date.getDate()).padStart(2, '0');
    const dateStr = `${year}-${month}-${day}`;
    return activities.filter((a) => a.date === dateStr);
  };

  // Generate weeks from fixed reference point (1 year ago to 1 year future)
  // Calculate weekly summary stats
  const getWeeklySummary = (weekStart: Date) => {
    let totalTSS = 0;
    let totalMinutes = 0;
    let totalDistance = 0;
    let workoutCount = 0;
    let runDistance = 0;
    let bikeDistance = 0;
    let swimDistance = 0;

    for (let i = 0; i < 7; i++) {
      const date = new Date(weekStart);
      date.setDate(weekStart.getDate() + i);
      const dayActivities = getActivitiesForDate(date);

      // Only count activities (actual completed workouts from Garmin)
      // Planned workouts don't count toward weekly totals
      dayActivities.forEach(a => {
        // Use calculated_tss (our calculation) or training_load (Garmin's), or 0
        const tss = a.calculated_tss || a.training_load || 0;
        // Duration is in seconds in backend
        const minutes = a.duration_seconds ? Math.round(a.duration_seconds / 60) : 0;
        // Distance is in meters in backend
        const distance = a.distance_meters ? a.distance_meters / 1000 : 0;
        
        totalTSS += tss;
        totalMinutes += minutes;
        totalDistance += distance;
        workoutCount++;
        
        // Track sport-specific distances
        const sportType = a.activity_type.toLowerCase();
        if (sportType.includes('run')) {
          runDistance += distance;
        } else if (sportType.includes('cycl') || sportType.includes('bike')) {
          bikeDistance += distance;
        } else if (sportType.includes('swim')) {
          swimDistance += distance;
        }
      });
    }

    const summary = {
      totalTSS: Math.round(totalTSS),
      totalHours: Math.floor(totalMinutes / 60),
      totalMinutes: totalMinutes % 60,
      totalDistance: totalDistance.toFixed(1),
      runDistance: runDistance.toFixed(1),
      bikeDistance: bikeDistance.toFixed(1),
      swimDistance: swimDistance.toFixed(1),
      workoutCount
    };
    
    return summary;
  };

  const handleToday = () => {
    const today = new Date();
    const dayOfWeek = today.getDay();
    const diff = dayOfWeek === 0 ? -6 : 1 - dayOfWeek;
    const monday = new Date(today);
    monday.setDate(today.getDate() + diff);
    monday.setHours(0, 0, 0, 0);
    setCurrentWeekStart(monday);
    
    // Scroll to today's week within the card container
    setTimeout(() => {
      const weekElement = document.getElementById(`week-${monday.getTime()}`);
      const cardElement = calendarCardRef.current;
      if (weekElement && cardElement) {
        const weekTop = weekElement.offsetTop;
        cardElement.scrollTo({ top: weekTop - 180, behavior: 'smooth' });
      }
    }, 100);
  };

  const getSportIcon = (sportType: string) => {
    const type = sportType.toLowerCase();
    if (type.includes('run')) return <RunIcon sx={{ fontSize: 12 }} />;
    if (type.includes('bike') || type.includes('cycling')) return <BikeIcon sx={{ fontSize: 12 }} />;
    if (type.includes('swim')) return <SwimIcon sx={{ fontSize: 12 }} />;
    if (type.includes('strength') || type.includes('gym')) return <StrengthIcon sx={{ fontSize: 12 }} />;
    return null;
  };

  const handleWorkoutClick = (workout: Workout) => {
    setSelectedWorkout(workout);
    setSelectedActivity(null);
    setDetailDialogOpen(true);
  };

  const handleActivityClick = (activity: GarminActivity) => {
    setSelectedActivity(activity);
    setSelectedWorkout(null);
    setDetailDialogOpen(true);
  };

  const handleToggleComplete = async (workout: Workout) => {
    try {
      await api.put(`/training-plans/${workout.training_plan_id}/workouts/${workout.id}`, {
        is_completed: !workout.is_completed,
      });
      fetchData();
      setDetailDialogOpen(false);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to update workout');
    }
  };

  const dayNames = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'];
  const weeks = generateWeeks; // Use memoized array directly

  if (!user) {
    return null;
  }

  const handlePreviousMonth = () => {
    const newDate = new Date(currentWeekStart);
    newDate.setMonth(newDate.getMonth() - 1);
    newDate.setDate(1); // First of month
    
    // Find Monday of that week
    const dayOfWeek = newDate.getDay();
    const diff = dayOfWeek === 0 ? -6 : 1 - dayOfWeek;
    newDate.setDate(newDate.getDate() + diff);
    
    setCurrentWeekStart(newDate);
    
    // Scroll to that week within the card container
    setTimeout(() => {
      const weekElement = document.getElementById(`week-${newDate.getTime()}`);
      const cardElement = calendarCardRef.current;
      if (weekElement && cardElement) {
        const weekTop = weekElement.offsetTop;
        cardElement.scrollTo({ top: weekTop - 180, behavior: 'smooth' });
      }
    }, 50);
  };

  const handleNextMonth = () => {
    const newDate = new Date(currentWeekStart);
    newDate.setMonth(newDate.getMonth() + 1);
    newDate.setDate(1); // First of month
    
    // Find Monday of that week
    const dayOfWeek = newDate.getDay();
    const diff = dayOfWeek === 0 ? -6 : 1 - dayOfWeek;
    newDate.setDate(newDate.getDate() + diff);
    
    setCurrentWeekStart(newDate);
    
    // Scroll to that week within the card container
    setTimeout(() => {
      const weekElement = document.getElementById(`week-${newDate.getTime()}`);
      const cardElement = calendarCardRef.current;
      if (weekElement && cardElement) {
        const weekTop = weekElement.offsetTop;
        cardElement.scrollTo({ top: weekTop - 180, behavior: 'smooth' });
      }
    }, 50);
  };

  return (
    <Container maxWidth="xl" sx={{ mt: 0, mb: 0, pt: 0, pb: 0, height: 'calc(100vh - 64px)', display: 'flex', flexDirection: 'column', overflow: 'hidden' }}>
      {/* Month Navigation Bar - Sticky at top */}
      <Box sx={{ 
        display: 'flex', 
        alignItems: 'center', 
        gap: 1, 
        py: 0.5,
        px: 2,
        borderBottom: 1,
        borderColor: 'divider',
        bgcolor: 'background.paper',
        position: 'sticky',
        top: 0,
        zIndex: 10,
        flexShrink: 0
      }}>
        <IconButton onClick={handlePreviousMonth} size="small" color="primary">
          <ChevronLeftIcon />
        </IconButton>
        <Typography variant="h6" sx={{ minWidth: 180, textAlign: 'center', fontWeight: 500 }}>
          {currentWeekStart.toLocaleDateString('en-US', { month: 'long', year: 'numeric' })}
        </Typography>
        <IconButton onClick={handleNextMonth} size="small" color="primary">
          <ChevronRightIcon />
        </IconButton>
        <Button variant="contained" size="small" onClick={handleToday} sx={{ ml: 1 }}>
          Today
        </Button>
      </Box>

      {error && (
        <Alert severity="error" sx={{ mx: 2, my: 1, flexShrink: 0 }} onClose={() => setError(null)}>
          {error}
        </Alert>
      )}

      {/* Calendar Card - fills remaining space, scrollable */}
      <Card ref={calendarCardRef} sx={{ flex: 1, display: 'flex', flexDirection: 'column', overflow: 'auto', mt: 0, mx: 0, borderRadius: 0 }}>
        <CardContent sx={{ p: 0, flex: 1, display: 'flex', flexDirection: 'column', '&:last-child': { pb: 0 } }}>
          {/* Header row with day names + Week Summary - Sticky within card */}
          <Box sx={{ display: 'flex', borderBottom: 1, borderColor: 'divider', bgcolor: 'grey.100', position: 'sticky', top: 0, zIndex: 5, flexShrink: 0 }}>
            {dayNames.map((day, index) => (
              <Box 
                key={day} 
                sx={{ 
                  flex: '1 1 0',
                  textAlign: 'center', 
                  fontWeight: 'bold', 
                  py: 1,
                  borderRight: index < 6 ? 1 : 0,
                  borderColor: 'divider',
                  fontSize: '0.875rem'
                }}
              >
                {day}
              </Box>
            ))}
            <Box sx={{ width: '200px', textAlign: 'center', fontWeight: 'bold', py: 1, bgcolor: 'primary.light', fontSize: '0.875rem' }}>
              Week Summary
            </Box>
          </Box>

          {/* Weeks container - scrollable */}
          <Box sx={{ flex: 1 }}>
            {weeks.map((weekStart) => {
              const weekSummary = getWeeklySummary(weekStart);
              const weekEnd = new Date(weekStart);
              weekEnd.setDate(weekStart.getDate() + 6);
              const isCurrentWeek = 
                currentWeekStart.getTime() >= weekStart.getTime() &&
                currentWeekStart.getTime() < new Date(weekStart.getTime() + 7 * 24 * 60 * 60 * 1000).getTime();

              return (
                <Box 
                  key={weekStart.getTime()} 
                  id={`week-${weekStart.getTime()}`}
                  sx={{ 
                    display: 'flex', 
                    borderBottom: 1, 
                    borderColor: 'divider',
                    minHeight: 120,
                    bgcolor: isCurrentWeek ? 'action.hover' : 'background.paper'
                  }}
                >
                  {/* 7 day columns */}
                  {[0, 1, 2, 3, 4, 5, 6].map((dayOffset) => {
                    const date = new Date(weekStart);
                    date.setDate(weekStart.getDate() + dayOffset);
                    const dayWorkouts = getWorkoutsForDate(date);
                    const dayActivities = getActivitiesForDate(date);
                    const dailyTSS = [
                      ...dayWorkouts.map(w => w.tss || 0),
                      ...dayActivities.map(a => a.training_stress_score || 0)
                    ].reduce((sum, tss) => sum + tss, 0);
                    const isToday = date.toDateString() === new Date().toDateString();

                    return (
                      <Box
                        key={dayOffset}
                        sx={{
                          flex: '1 1 0',
                          minWidth: 0,
                          borderRight: dayOffset < 6 ? 1 : 0,
                          borderColor: 'divider',
                          display: 'flex',
                          flexDirection: 'column',
                          bgcolor: isToday ? 'rgba(25, 118, 210, 0.08)' : 'transparent',
                        }}
                      >
                        {/* Day header */}
                        <Box sx={{ 
                          display: 'flex', 
                          justifyContent: 'space-between', 
                          alignItems: 'center', 
                          px: 0.5,
                          py: 0.5, 
                          bgcolor: isToday ? 'primary.main' : 'grey.50', 
                          borderBottom: 1, 
                          borderColor: 'divider',
                          color: isToday ? 'white' : 'inherit',
                          minHeight: 28
                        }}>
                          <Typography variant="caption" fontWeight={isToday ? 'bold' : 'normal'} sx={{ fontSize: '0.75rem' }}>
                            {date.getDate()}
                          </Typography>
                          {dailyTSS > 0 && (() => {
                            const tssColor = getTSSColor(dailyTSS);
                            return (
                              <Chip
                                label={Math.round(dailyTSS)}
                                size="small"
                                sx={{
                                  bgcolor: tssColor.main,
                                  color: 'white',
                                  fontWeight: 600,
                                  height: 18,
                                  fontSize: '0.7rem',
                                  '& .MuiChip-label': { px: 0.75 }
                                }}
                              />
                            );
                          })()}
                        </Box>

                        {/* Workouts and Activities - compact display */}
                        <Box sx={{ p: 0.5, flexGrow: 1, overflowY: 'auto', display: 'flex', flexDirection: 'column', gap: 0.5 }}>
                          {dayWorkouts.map((workout) => (
                            <Box
                              key={`workout-${workout.id}`}
                              onClick={() => handleWorkoutClick(workout)}
                              sx={{
                                fontSize: '0.75rem',
                                px: 0.5,
                                py: 0.5,
                                borderRadius: 0.5,
                                border: 1.5,
                                borderStyle: workout.is_completed ? 'solid' : 'dashed',
                                borderColor: getSportColor(workout.sport_type).main,
                                bgcolor: workout.is_completed ? getSportColor(workout.sport_type).light : 'transparent',
                                cursor: 'pointer',
                                display: 'flex',
                                alignItems: 'center',
                                gap: 0.5,
                                '&:hover': { boxShadow: 1 },
                              }}
                            >
                              {workout.is_completed && <CheckCircleIcon sx={{ fontSize: 12 }} />}
                              {getSportIcon(workout.sport_type)}
                              <Typography variant="caption" sx={{ fontSize: '0.7rem', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap', flexGrow: 1 }}>
                                {workout.title}
                              </Typography>
                            </Box>
                          ))}
                          {dayActivities.map((activity) => (
                            <Box
                              key={`activity-${activity.id}`}
                              onClick={() => handleActivityClick(activity)}
                              sx={{
                                fontSize: '0.75rem',
                                px: 0.5,
                                py: 0.5,
                                borderRadius: 0.5,
                                bgcolor: getSportColor(activity.activity_type).light,
                                border: 1.5,
                                borderColor: getSportColor(activity.activity_type).main,
                                cursor: 'pointer',
                                display: 'flex',
                                alignItems: 'center',
                                gap: 0.5,
                                '&:hover': { boxShadow: 1 },
                              }}
                            >
                              <CheckCircleIcon sx={{ fontSize: 12, color: getSportColor(activity.activity_type).dark }} />
                              {getSportIcon(activity.activity_type)}
                              <Box sx={{ flexGrow: 1, minWidth: 0 }}>
                                <Typography variant="caption" sx={{ fontSize: '0.7rem', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap', display: 'block' }}>
                                  {activity.activity_name}
                                </Typography>
                                {activity.distance_meters && (
                                  <Typography variant="caption" sx={{ fontSize: '0.65rem', color: 'text.secondary' }}>
                                    {(activity.distance_meters / 1000).toFixed(1)}km
                                  </Typography>
                                )}
                              </Box>
                            </Box>
                          ))}
                        </Box>
                      </Box>
                    );
                  })}

                  {/* Weekly Summary Column */}
                  <Box sx={{ 
                    width: '200px', 
                    bgcolor: 'grey.50',
                    borderLeft: 2,
                    borderColor: 'divider',
                    p: 1,
                    display: 'flex',
                    flexDirection: 'column',
                    gap: 0.5
                  }}>
                    <Typography variant="caption" color="text.secondary" fontWeight={600} sx={{ fontSize: '0.7rem', mb: 0.5 }}>
                      {weekStart.toLocaleDateString('en-US', { month: 'short', day: 'numeric' })} - {weekEnd.toLocaleDateString('en-US', { month: 'short', day: 'numeric' })}
                    </Typography>
                    
                    {/* TSS */}
                    <Box sx={{ display: 'flex', alignItems: 'baseline', gap: 0.5, borderBottom: 1, borderColor: 'divider', pb: 0.5 }}>
                      <Typography variant="h6" fontWeight={700} color="primary">
                        {weekSummary.totalTSS}
                      </Typography>
                      <Typography variant="caption" color="text.secondary">TSS</Typography>
                    </Box>
                    
                    {/* Time */}
                    <Typography variant="caption" sx={{ fontSize: '0.75rem' }}>
                      ⏱ {weekSummary.totalHours}h {weekSummary.totalMinutes}m
                    </Typography>
                    
                    {/* Total Distance */}
                    <Typography variant="caption" fontWeight={600} sx={{ fontSize: '0.75rem', mt: 0.5 }}>
                      📏 {weekSummary.totalDistance} km total
                    </Typography>
                    
                    {/* Sport-specific distances */}
                    {parseFloat(weekSummary.runDistance) > 0 && (
                      <Typography variant="caption" sx={{ fontSize: '0.7rem', pl: 1 }}>
                        🏃 {weekSummary.runDistance} km
                      </Typography>
                    )}
                    {parseFloat(weekSummary.bikeDistance) > 0 && (
                      <Typography variant="caption" sx={{ fontSize: '0.7rem', pl: 1 }}>
                        🚴 {weekSummary.bikeDistance} km
                      </Typography>
                    )}
                    {parseFloat(weekSummary.swimDistance) > 0 && (
                      <Typography variant="caption" sx={{ fontSize: '0.7rem', pl: 1 }}>
                        🏊 {weekSummary.swimDistance} km
                      </Typography>
                    )}
                    
                    {/* Workout count */}
                    <Typography variant="caption" fontWeight={600} sx={{ fontSize: '0.75rem', mt: 0.5 }}>
                      {weekSummary.workoutCount} {weekSummary.workoutCount === 1 ? 'workout' : 'workouts'}
                    </Typography>
                  </Box>
                </Box>
              );
            })}
          </Box>
        </CardContent>
      </Card>

      {/* Workout/Activity Detail Dialog */}
      <Dialog open={detailDialogOpen} onClose={() => setDetailDialogOpen(false)} maxWidth="sm" fullWidth>
        {selectedWorkout && (
          <>
            <DialogTitle>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                {getSportIcon(selectedWorkout.sport_type)}
                {selectedWorkout.title}
                {selectedWorkout.is_completed && <CheckCircleIcon color="success" />}
              </Box>
              <Typography variant="caption" color="text.secondary">Planned Workout</Typography>
            </DialogTitle>
            <DialogContent>
              <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
                <Box>
                  <Typography variant="body2" color="text.secondary">Date</Typography>
                  <Typography variant="body1">{new Date(selectedWorkout.date).toLocaleDateString()}</Typography>
                </Box>
                {selectedWorkout.description && (
                  <Box>
                    <Typography variant="body2" color="text.secondary">Description</Typography>
                    <Typography variant="body1">{selectedWorkout.description}</Typography>
                  </Box>
                )}
                <Box sx={{ display: 'flex', gap: 2 }}>
                  <Chip label={selectedWorkout.sport_type} color="primary" />
                  <Chip label={selectedWorkout.workout_type} />
                </Box>
                {selectedWorkout.duration_minutes && (
                  <Box>
                    <Typography variant="body2" color="text.secondary">Duration</Typography>
                    <Typography variant="body1">{selectedWorkout.duration_minutes} minutes</Typography>
                  </Box>
                )}
                {selectedWorkout.distance_km && (
                  <Box>
                    <Typography variant="body2" color="text.secondary">Distance</Typography>
                    <Typography variant="body1">{selectedWorkout.distance_km} km</Typography>
                  </Box>
                )}
                {selectedWorkout.intensity_zone && (
                  <Box>
                    <Typography variant="body2" color="text.secondary">Intensity</Typography>
                    <Typography variant="body1">{selectedWorkout.intensity_zone}</Typography>
                  </Box>
                )}
              </Box>
            </DialogContent>
            <DialogActions>
              <Button onClick={() => setDetailDialogOpen(false)}>Close</Button>
              <Button
                variant="contained"
                onClick={() => handleToggleComplete(selectedWorkout)}
                color={selectedWorkout.is_completed ? 'secondary' : 'success'}
              >
                {selectedWorkout.is_completed ? 'Mark Incomplete' : 'Mark Complete'}
              </Button>
            </DialogActions>
          </>
        )}
        {selectedActivity && (() => {
          // Calculate Intensity Factor (IF)
          const calculateIF = () => {
            // For cycling: IF = NP / FTP
            if (selectedActivity.normalized_power_watts && selectedActivity.threshold_power_watts && selectedActivity.threshold_power_watts > 0) {
              return (selectedActivity.normalized_power_watts / selectedActivity.threshold_power_watts).toFixed(3);
            }
            // For running/other: IF = avg_hr / threshold_hr (we don't have threshold_hr in frontend, so skip)
            return null;
          };
          
          const intensityFactor = calculateIF();
          const movingTime = selectedActivity.moving_duration_seconds || selectedActivity.duration_seconds;
          const elapsedTime = selectedActivity.elapsed_duration_seconds || selectedActivity.duration_seconds;
          
          return (
            <>
              <DialogTitle sx={{ pb: 1 }}>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                  <CheckCircleIcon color="success" />
                  {getSportIcon(selectedActivity.activity_type)}
                  <Box>
                    <Typography variant="h6" component="div" sx={{ fontWeight: 600 }}>
                      {selectedActivity.activity_name}
                    </Typography>
                    <Typography variant="caption" color="text.secondary">
                      {new Date(selectedActivity.start_time_local).toLocaleDateString('en-US', { 
                        weekday: 'short', month: 'short', day: 'numeric', year: 'numeric' 
                      })} • {new Date(selectedActivity.start_time_local).toLocaleTimeString('en-US', {
                        hour: '2-digit', minute: '2-digit'
                      })}
                    </Typography>
                  </Box>
                </Box>
              </DialogTitle>
              <DialogContent sx={{ pt: 2 }}>
                {/* Key Metrics Row - TrainingPeaks Style */}
                <Box sx={{ 
                  display: 'grid', 
                  gridTemplateColumns: 'repeat(auto-fit, minmax(140px, 1fr))', 
                  gap: 2, 
                  mb: 3,
                  p: 2,
                  bgcolor: 'grey.50',
                  borderRadius: 1
                }}>
                  {selectedActivity.calculated_tss && (
                    <Box sx={{ textAlign: 'center' }}>
                      <Typography variant="caption" color="text.secondary" sx={{ fontWeight: 600, textTransform: 'uppercase' }}>TSS</Typography>
                      <Typography variant="h5" sx={{ fontWeight: 700, color: getTSSColor(selectedActivity.calculated_tss) }}>
                        {Math.round(selectedActivity.calculated_tss)}
                      </Typography>
                    </Box>
                  )}
                  {intensityFactor && (
                    <Box sx={{ textAlign: 'center' }}>
                      <Typography variant="caption" color="text.secondary" sx={{ fontWeight: 600, textTransform: 'uppercase' }}>IF</Typography>
                      <Typography variant="h5" sx={{ fontWeight: 700 }}>
                        {intensityFactor}
                      </Typography>
                    </Box>
                  )}
                  {movingTime && (
                    <Box sx={{ textAlign: 'center' }}>
                      <Typography variant="caption" color="text.secondary" sx={{ fontWeight: 600, textTransform: 'uppercase' }}>Time</Typography>
                      <Typography variant="h5" sx={{ fontWeight: 700 }}>
                        {Math.floor(movingTime / 3600)}:{String(Math.floor((movingTime % 3600) / 60)).padStart(2, '0')}
                      </Typography>
                    </Box>
                  )}
                  {selectedActivity.distance_meters && (
                    <Box sx={{ textAlign: 'center' }}>
                      <Typography variant="caption" color="text.secondary" sx={{ fontWeight: 600, textTransform: 'uppercase' }}>Distance</Typography>
                      <Typography variant="h5" sx={{ fontWeight: 700 }}>
                        {(selectedActivity.distance_meters / 1000).toFixed(1)} km
                      </Typography>
                    </Box>
                  )}
                </Box>

                {/* Detailed Stats - Two Column Layout */}
                <Grid container spacing={2}>
                  {/* Left Column */}
                  <Grid item xs={12} sm={6}>
                    {selectedActivity.location_name && (
                      <Box sx={{ mb: 1.5 }}>
                        <Typography variant="caption" color="text.secondary" sx={{ fontWeight: 600 }}>LOCATION</Typography>
                        <Typography variant="body1">{selectedActivity.location_name}</Typography>
                      </Box>
                    )}
                    {selectedActivity.average_speed_mps && selectedActivity.average_speed_mps > 0 && (
                      <Box sx={{ mb: 1.5 }}>
                        <Typography variant="caption" color="text.secondary" sx={{ fontWeight: 600 }}>AVG PACE</Typography>
                        <Typography variant="body1">
                          {(() => {
                            const kmh = selectedActivity.average_speed_mps * 3.6;
                            const minPerKm = 60 / kmh;
                            const min = Math.floor(minPerKm);
                            const sec = Math.round((minPerKm - min) * 60);
                            return `${min}:${String(sec).padStart(2, '0')} /km`;
                          })()}
                        </Typography>
                      </Box>
                    )}
                    {selectedActivity.normalized_power_watts && (
                      <Box sx={{ mb: 1.5 }}>
                        <Typography variant="caption" color="text.secondary" sx={{ fontWeight: 600 }}>NORMALIZED POWER (NP)</Typography>
                        <Typography variant="body1">{Math.round(selectedActivity.normalized_power_watts)} W</Typography>
                      </Box>
                    )}
                    {selectedActivity.average_power_watts && (
                      <Box sx={{ mb: 1.5 }}>
                        <Typography variant="caption" color="text.secondary" sx={{ fontWeight: 600 }}>AVG POWER</Typography>
                        <Typography variant="body1">{Math.round(selectedActivity.average_power_watts)} W</Typography>
                      </Box>
                    )}
                    {selectedActivity.average_hr && (
                      <Box sx={{ mb: 1.5 }}>
                        <Typography variant="caption" color="text.secondary" sx={{ fontWeight: 600 }}>AVG HEART RATE</Typography>
                        <Typography variant="body1">{selectedActivity.average_hr} bpm</Typography>
                      </Box>
                    )}
                  </Grid>

                  {/* Right Column */}
                  <Grid item xs={12} sm={6}>
                    {elapsedTime && movingTime && elapsedTime !== movingTime && (
                      <Box sx={{ mb: 1.5 }}>
                        <Typography variant="caption" color="text.secondary" sx={{ fontWeight: 600 }}>ELAPSED TIME</Typography>
                        <Typography variant="body1">
                          {Math.floor(elapsedTime / 3600)}:{String(Math.floor((elapsedTime % 3600) / 60)).padStart(2, '0')}:{String(Math.floor(elapsedTime % 60)).padStart(2, '0')}
                        </Typography>
                      </Box>
                    )}
                    {selectedActivity.elevation_gain_meters && (
                      <Box sx={{ mb: 1.5 }}>
                        <Typography variant="caption" color="text.secondary" sx={{ fontWeight: 600 }}>ELEVATION GAIN</Typography>
                        <Typography variant="body1">{Math.round(selectedActivity.elevation_gain_meters)} m</Typography>
                      </Box>
                    )}
                    {selectedActivity.max_hr && (
                      <Box sx={{ mb: 1.5 }}>
                        <Typography variant="caption" color="text.secondary" sx={{ fontWeight: 600 }}>MAX HEART RATE</Typography>
                        <Typography variant="body1">{selectedActivity.max_hr} bpm</Typography>
                      </Box>
                    )}
                    {selectedActivity.calories && (
                      <Box sx={{ mb: 1.5 }}>
                        <Typography variant="caption" color="text.secondary" sx={{ fontWeight: 600 }}>CALORIES</Typography>
                        <Typography variant="body1">{selectedActivity.calories} kcal</Typography>
                      </Box>
                    )}
                  </Grid>
                </Grid>
              </DialogContent>
              <DialogActions>
                <Button onClick={() => setDetailDialogOpen(false)}>Close</Button>
              </DialogActions>
            </>
          );
        })()}
      </Dialog>
    </Container>
  );
};

export default Calendar;
