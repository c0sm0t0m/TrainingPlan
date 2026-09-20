import React, { useEffect, useState, useMemo } from 'react';
import {
  Box,
  Button,
  Card,
  CardContent,
  Container,
  Typography,
  Grid,
  Chip,
  useTheme,
  useMediaQuery,
  Alert,
  Divider,
  IconButton,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  AppBar,
  Toolbar,
  SpeedDial,
  SpeedDialAction,
  TextField,
  Stack,
  SwipeableDrawer,
  ToggleButtonGroup,
  ToggleButton,
  Tooltip,
  alpha,
} from '@mui/material';
import {
  ChevronLeft as ChevronLeftIcon,
  ChevronRight as ChevronRightIcon,
  CheckCircle as CheckCircleIcon,
  DirectionsRun as RunIcon,
  DirectionsBike as BikeIcon,
  Pool as SwimIcon,
  FitnessCenter as StrengthIcon,
  Event as EventIcon,
  Add as AddIcon,
} from '@mui/icons-material';
import { useNavigate, useLocation } from 'react-router-dom';
import { useAuthStore } from '../store/authStore';
import api from '../services/api';
import WorkoutCard from '../components/WorkoutCard';
import EmptyState from '../components/EmptyState';
import CalendarSkeleton from '../components/skeletons/CalendarSkeleton';
import { getSportColor, getTSSColor } from '../utils/sportColors';
import { useSwipeable } from 'react-swipeable';
import { format, addDays, startOfMonth, getWeek, startOfWeek } from 'date-fns';
import MobileWeekGrid from './calendar/MobileWeekGrid';
import WeeklySummaryBar from '../components/calendar/WeeklySummaryBar';
import MonthCalendarView from './calendar/MonthCalendarView';

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
  target_tss?: number; // Target/planned TSS
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
  intensity_factor?: number; // Intensity Factor (IF) - workout intensity relative to threshold
}

interface TrainingPlan {
  id: number;
  name: string;
  sport_type: string;
  workouts: Workout[];
}

const Calendar: React.FC = () => {
  const theme = useTheme();
  const navigate = useNavigate();
  const location = useLocation();
  const { user } = useAuthStore();
  const isMobile = useMediaQuery(theme.breakpoints.down('md'));
  
  // Track if we restored from navigation state (coming back from activity detail)
  const restoredFromNavigation = React.useRef(false);
  
  const [currentWeekStart, setCurrentWeekStart] = useState<Date>(() => {
    // If returning from activity/workout detail, restore to saved date and view
    const state = location.state as { weekStart?: string; calendarView?: string } | null;
    if (state?.weekStart) {
      restoredFromNavigation.current = true; // Mark that we restored state
      const restoredDate = new Date(state.weekStart);
      restoredDate.setHours(0, 0, 0, 0);
      // Also restore the view
      if (state.calendarView) {
        setTimeout(() => setCalendarView(state.calendarView as 'month' | 'week' | 'day'), 0);
      }
      return restoredDate;
    }
    
    // Start from today (for day view)
    const today = new Date();
    today.setHours(0, 0, 0, 0);
    return today;
  });
  const [weeksToShow] = useState(156); // Show 156 weeks (3 years) for scrolling 12+ months ahead
  const [plans, setPlans] = useState<TrainingPlan[]>([]);
  const [workouts, setWorkouts] = useState<Workout[]>([]);
  const [activities, setActivities] = useState<GarminActivity[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedWorkout, setSelectedWorkout] = useState<Workout | null>(null);
  const [selectedActivity, setSelectedActivity] = useState<GarminActivity | null>(null);
  const [detailDialogOpen, setDetailDialogOpen] = useState(false);
  const calendarCardRef = React.useRef<HTMLDivElement>(null);
  const weekScrollRef = React.useRef<HTMLDivElement>(null);
  const weekGridScrollRefs = React.useRef<{ [key: number]: HTMLDivElement | null }>({});
  
  // Quick-add FAB state
  const [quickAddOpen, setQuickAddOpen] = useState(false);
  const [quickAddDate, setQuickAddDate] = useState<Date>(new Date());
  const [quickAddSport, setQuickAddSport] = useState<'running' | 'cycling' | 'swimming' | 'strength'>('running');
  const [quickAddTitle, setQuickAddTitle] = useState('');
  const [quickAddDuration, setQuickAddDuration] = useState(60);
  const [quickAddTSS, setQuickAddTSS] = useState(50);
  const [quickAddSaving, setQuickAddSaving] = useState(false);
  
  // Calendar view state - default to day view showing today
  const [calendarView, setCalendarView] = useState<'month' | 'week' | 'day'>('day');
  
  // Swipe handlers for mobile - DISABLED for week view
  // Week view uses scroll snap instead, handled by scroll event listener
  const swipeHandlers = useSwipeable({
    onSwipedLeft: () => {
      // Swipe handling for week view is done via scroll snap + scroll event listener
      // Only handle day view here
      if (isMobile && calendarView === 'day') nextWeek();
    },
    onSwipedRight: () => {
      // Swipe handling for week view is done via scroll snap + scroll event listener
      // Only handle day view here
      if (isMobile && calendarView === 'day') prevWeek();
    },
    trackMouse: false, // Only track touch
    preventScrollOnSwipe: false,
    delta: 50, // Minimum swipe distance
  });

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
    document.title = 'Training Calendar - Kinesis';
  }, []);

  // Scroll to center week when switching to week view OR when currentWeekStart changes
  useEffect(() => {
    if (isMobile && calendarView === 'week' && weekScrollRef.current) {
      // Disable scroll event handling during programmatic scroll
      (weekScrollRef.current as any).__isResetting = true;
      
      // Reset scroll to center immediately (no timeout to avoid flicker)
      if (weekScrollRef.current.offsetWidth > 0) {
        weekScrollRef.current.scrollLeft = weekScrollRef.current.offsetWidth;
      }
      
      // Reset the current week grid scroll to beginning (Monday) after refs are updated
      // Use longer timeout to ensure React has finished rendering and refs are updated
      const scrollResetTimer = setTimeout(() => {
        // Only reset the current week (weekOffset 0), not all weeks
        const currentWeekGrid = weekGridScrollRefs.current[0];
        if (currentWeekGrid && currentWeekGrid.scrollLeft !== 0) {
          currentWeekGrid.scrollLeft = 0;
        }
      }, 200);
      
      // Re-enable scroll event handling after scroll completes
      const timer = setTimeout(() => {
        if (weekScrollRef.current) {
          (weekScrollRef.current as any).__isResetting = false;
        }
      }, 300);
      
      return () => {
        clearTimeout(timer);
        clearTimeout(scrollResetTimer);
      };
    }
  }, [calendarView, isMobile, currentWeekStart]);

  // Handle week scroll snap to update currentWeekStart when user swipes
  useEffect(() => {
    if (!isMobile || calendarView !== 'week' || !weekScrollRef.current) return;

    const scrollContainer = weekScrollRef.current;
    let scrollTimeout: number;
    let isScrolling = false;
    let scrollStartPos = 0;

    const handleWeekScrollStart = () => {
      isScrolling = true;
      scrollStartPos = scrollContainer.scrollLeft;
    };

    const handleWeekScroll = () => {
      // Ignore scroll events during programmatic scroll reset
      if ((scrollContainer as any).__isResetting) {
        return;
      }

      // Debounce to detect when scrolling stops
      clearTimeout(scrollTimeout);
      scrollTimeout = window.setTimeout(() => {
        if (!scrollContainer || (scrollContainer as any).__isResetting) return;

        const scrollLeft = scrollContainer.scrollLeft;
        const containerWidth = scrollContainer.offsetWidth;
        const scrollDelta = Math.abs(scrollLeft - scrollStartPos);

        // Calculate scroll position as percentage of container width
        const scrollRatio = scrollLeft / containerWidth;
        
        // Determine threshold for week change (50% of week width)
        const weekChangeThreshold = 0.5;

        // Check if user scrolled more than threshold
        if (scrollDelta > containerWidth * weekChangeThreshold) {
          // Strong swipe - change week
          const weekIndex = Math.round(scrollRatio);

          if (weekIndex === 0) {
            // Scrolled to previous week
            const newWeekStart = new Date(currentWeekStart);
            newWeekStart.setDate(currentWeekStart.getDate() - 7);
            newWeekStart.setHours(0, 0, 0, 0);
            setCurrentWeekStart(newWeekStart);
          } else if (weekIndex === 2) {
            // Scrolled to next week
            const newWeekStart = new Date(currentWeekStart);
            newWeekStart.setDate(currentWeekStart.getDate() + 7);
            newWeekStart.setHours(0, 0, 0, 0);
            setCurrentWeekStart(newWeekStart);
          }
        } else {
          // Gentle swipe - snap back to center
          (scrollContainer as any).__isResetting = true;
          scrollContainer.scrollTo({
            left: containerWidth,
            behavior: 'smooth'
          });
          setTimeout(() => {
            if (scrollContainer) {
              (scrollContainer as any).__isResetting = false;
            }
          }, 300);
        }

        isScrolling = false;
      }, 150);
    };

    scrollContainer.addEventListener('scrollstart', handleWeekScrollStart);
    scrollContainer.addEventListener('touchstart', handleWeekScrollStart);
    scrollContainer.addEventListener('scroll', handleWeekScroll);
    return () => {
      scrollContainer.removeEventListener('scrollstart', handleWeekScrollStart);
      scrollContainer.removeEventListener('touchstart', handleWeekScrollStart);
      scrollContainer.removeEventListener('scroll', handleWeekScroll);
      clearTimeout(scrollTimeout);
    };
  }, [isMobile, calendarView, currentWeekStart]);

  useEffect(() => {
    if (!user) {
      navigate('/login');
      return;
    }
    fetchData();
  }, [user, navigate]); // Remove currentDate dependency - load all data once

  // Scroll to week when calendar loads
  // Only auto-scroll to today on first visit, not when returning from activity detail
  useEffect(() => {
    if (!loading && calendarCardRef.current) {
      setTimeout(() => {
        const weekElement = document.getElementById(`week-${currentWeekStart.getTime()}`);
        const cardElement = calendarCardRef.current;
        if (weekElement && cardElement) {
          const weekTop = weekElement.offsetTop;
          // Use smooth scroll only if we restored from navigation (coming back from activity)
          // Use auto scroll if first visit to calendar
          const scrollBehavior = restoredFromNavigation.current ? 'smooth' : 'auto';
          cardElement.scrollTo({ top: weekTop - 180, behavior: scrollBehavior });
        }
      }, 100);
    }
  }, [loading]); // Only run when loading completes, not when currentWeekStart changes

  // Update month display when scrolling (but not immediately after navigation)
  useEffect(() => {
    const cardElement = calendarCardRef.current;
    if (!cardElement) return;

    // Don't update week via scroll immediately after component mounts with restored state
    let allowScrollUpdate = false;
    const enableScrollUpdate = setTimeout(() => {
      allowScrollUpdate = true;
    }, 500); // Wait 500ms before allowing scroll to change week

    let scrollTimeout: number;
    const handleScroll = () => {
      if (!allowScrollUpdate) return; // Don't update if we just restored state
      
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
      cardElement.removeEventListener('scroll', handleScroll);
      clearTimeout(enableScrollUpdate);
      clearTimeout(scrollTimeout);
    };
  }, [currentWeekStart, generateWeeks]);

  const fetchData = async () => {
    try {
      setLoading(true);
      
      // Fetch planned workouts (only from active training plans)
      const response = await api.get('/training-plans', {
        params: { active_only: true }
      });
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

  // Calculate 7-day IF data for a week (for sparkline)
  // Uses weighted average when multiple activities exist
  const getWeekIFData = (weekStart: Date): number[] => {
    const weekIFData: number[] = [];
    for (let i = 0; i < 7; i++) {
      const day = new Date(weekStart);
      day.setDate(weekStart.getDate() + i);
      const dateStr = format(day, 'yyyy-MM-dd');
      
      const dayActivities = activities
        .filter(a => a.date === dateStr && a.intensity_factor != null);
      
      if (dayActivities.length > 0) {
        if (dayActivities.length === 1) {
          // Single activity: use its IF
          weekIFData.push(dayActivities[0].intensity_factor!);
        } else {
          // Multiple activities: use TSS-weighted average IF
          const totalTSS = dayActivities.reduce((sum, a) => sum + (a.calculated_tss || a.training_load || 0), 0);
          if (totalTSS > 0) {
            const weightedIF = dayActivities.reduce((sum, a) => {
              const tss = a.calculated_tss || a.training_load || 0;
              return sum + (a.intensity_factor! * tss);
            }, 0) / totalTSS;
            weekIFData.push(weightedIF);
          } else {
            // No TSS data, fall back to simple average
            const avgIF = dayActivities.reduce((sum, a) => sum + a.intensity_factor!, 0) / dayActivities.length;
            weekIFData.push(avgIF);
          }
        }
      } else {
        weekIFData.push(0);
      }
    }
    return weekIFData;
  };

  // Calculate 7-day TSS data for a week (for sparkline height)
  const getWeekTSSData = (weekStart: Date): number[] => {
    const weekTSSData: number[] = [];
    for (let i = 0; i < 7; i++) {
      const day = new Date(weekStart);
      day.setDate(weekStart.getDate() + i);
      const dateStr = format(day, 'yyyy-MM-dd');
      
      const dayActivities = activities.filter(a => a.date === dateStr);
      
      if (dayActivities.length > 0) {
        const totalTSS = dayActivities.reduce((sum, a) => sum + (a.calculated_tss || a.training_load || 0), 0);
        weekTSSData.push(totalTSS);
      } else {
        weekTSSData.push(0);
      }
    }
    return weekTSSData;
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
    let skiDistance = 0;
    let tennisHours = 0;
    let runMinutes = 0;
    let bikeMinutes = 0;
    let swimMinutes = 0;
    let skiMinutes = 0;
    let tennisMinutes = 0;

    for (let i = 0; i < 7; i++) {
      const date = new Date(weekStart);
      date.setDate(weekStart.getDate() + i);
      const dayActivities = getActivitiesForDate(date);
      const dayWorkouts = getWorkoutsForDate(date);

      // Count completed activities (actual workouts from Garmin)
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
        console.log(`Activity: ${a.activity_name} | Type: "${a.activity_type}" | Lowercase: "${sportType}" | Distance: ${distance}km`);
        if (sportType.includes('run')) {
          runDistance += distance;
          runMinutes += minutes;
        } else if (sportType.includes('cycl') || sportType.includes('bike') || sportType.includes('virtual')) {
          bikeDistance += distance;
          bikeMinutes += minutes;
          console.log(`  ✅ Added to bike: ${distance}km | Total bike: ${bikeDistance}km`);
        } else if (sportType.includes('swim')) {
          swimDistance += distance;
          swimMinutes += minutes;
        } else if (sportType.includes('ski')) {
          skiDistance += distance;
          skiMinutes += minutes;
        } else if (sportType.includes('tennis')) {
          tennisHours += minutes / 60;
          tennisMinutes += minutes;
        }
      });

      // Add target TSS from planned workouts that haven't been completed
      dayWorkouts.forEach(w => {
        if (!w.is_completed && w.target_tss) {
          totalTSS += w.target_tss;
          workoutCount++; // Count planned workouts too
          // Optionally include planned duration and distance
          if (w.duration_minutes) {
            totalMinutes += w.duration_minutes;
          }
          if (w.distance_km) {
            totalDistance += w.distance_km;
            const sportType = w.sport_type.toLowerCase();
            if (sportType.includes('run')) {
              runDistance += w.distance_km;
              if (w.duration_minutes) runMinutes += w.duration_minutes;
            } else if (sportType.includes('cycl') || sportType.includes('bike')) {
              bikeDistance += w.distance_km;
              if (w.duration_minutes) bikeMinutes += w.duration_minutes;
            } else if (sportType.includes('swim')) {
              swimDistance += w.distance_km;
              if (w.duration_minutes) swimMinutes += w.duration_minutes;
            }
          }
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
      skiDistance: skiDistance.toFixed(1),
      tennisHours: tennisHours.toFixed(1),
      runHours: (runMinutes / 60).toFixed(1),
      bikeHours: (bikeMinutes / 60).toFixed(1),
      swimHours: (swimMinutes / 60).toFixed(1),
      skiHours: (skiMinutes / 60).toFixed(1),
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
  
  // Mobile navigation
  const nextWeek = () => {
    if (calendarView === 'month') {
      // In month view, advance by 1 month
      const newDate = new Date(currentWeekStart);
      newDate.setMonth(currentWeekStart.getMonth() + 1);
      newDate.setDate(1);
      // Find Monday of that week
      const monday = startOfWeek(newDate, { weekStartsOn: 1 });
      setCurrentWeekStart(monday);
    } else if (calendarView === 'day') {
      // In day view, advance by 1 day
      const newDate = new Date(currentWeekStart);
      newDate.setDate(currentWeekStart.getDate() + 1);
      newDate.setHours(0, 0, 0, 0);
      setCurrentWeekStart(newDate);
    } else {
      // In week view, advance by 7 days to next Monday
      const newWeekStart = new Date(currentWeekStart);
      newWeekStart.setDate(currentWeekStart.getDate() + 7);
      newWeekStart.setHours(0, 0, 0, 0);
      setCurrentWeekStart(newWeekStart);
    }
  };
  
  const prevWeek = () => {
    if (calendarView === 'month') {
      // In month view, go back by 1 month
      const newDate = new Date(currentWeekStart);
      newDate.setMonth(currentWeekStart.getMonth() - 1);
      newDate.setDate(1);
      // Find Monday of that week
      const monday = startOfWeek(newDate, { weekStartsOn: 1 });
      setCurrentWeekStart(monday);
    } else if (calendarView === 'day') {
      // In day view, go back by 1 day
      const newDate = new Date(currentWeekStart);
      newDate.setDate(currentWeekStart.getDate() - 1);
      newDate.setHours(0, 0, 0, 0);
      setCurrentWeekStart(newDate);
    } else {
      // In week view, go back by 7 days to previous Monday
      const newWeekStart = new Date(currentWeekStart);
      newWeekStart.setDate(currentWeekStart.getDate() - 7);
      newWeekStart.setHours(0, 0, 0, 0);
      setCurrentWeekStart(newWeekStart);
    }
  };
  
  // Calculate week summary for mobile header
  const weekSummary = useMemo(() => {
    const summary = getWeeklySummary(currentWeekStart);
    
    // Calculate IF and TSS for each of the 7 days for sparkline
    const last7DaysIF: number[] = [];
    const last7DaysTSS: number[] = [];
    
    for (let i = 0; i < 7; i++) {
      const day = new Date(currentWeekStart);
      day.setDate(currentWeekStart.getDate() + i);
      const dateStr = format(day, 'yyyy-MM-dd');
      
      // Collect all activities for this day
      const dayActivities = activities.filter(a => a.date === dateStr);
      const dayActivitiesWithIF = dayActivities.filter(a => a.intensity_factor != null);
      
      // Calculate TSS (for bar height)
      const totalTSS = dayActivities.reduce((sum, a) => sum + (a.calculated_tss || a.training_load || 0), 0);
      last7DaysTSS.push(totalTSS);
      
      // Calculate IF (for bar color)
      if (dayActivitiesWithIF.length > 0) {
        if (dayActivitiesWithIF.length === 1) {
          // Single activity: use its IF
          last7DaysIF.push(dayActivitiesWithIF[0].intensity_factor!);
        } else {
          // Multiple activities: use TSS-weighted average IF
          if (totalTSS > 0) {
            const weightedIF = dayActivitiesWithIF.reduce((sum, a) => {
              const tss = a.calculated_tss || a.training_load || 0;
              return sum + (a.intensity_factor! * tss);
            }, 0) / totalTSS;
            last7DaysIF.push(weightedIF);
          } else {
            // No TSS data, fall back to simple average
            const avgIF = dayActivitiesWithIF.reduce((sum, a) => sum + a.intensity_factor!, 0) / dayActivitiesWithIF.length;
            last7DaysIF.push(avgIF);
          }
        }
      } else {
        last7DaysIF.push(0); // No activities with IF data
      }
    }
    
    return {
      totalTSS: summary.totalTSS,
      totalHours: summary.totalHours + summary.totalMinutes / 60,
      totalDistance: parseFloat(summary.totalDistance),
      last7DaysIF,
      last7DaysTSS,
    };
  }, [currentWeekStart, workouts, activities]);

  const getSportIcon = (sportType: string) => {
    const type = sportType.toLowerCase();
    if (type.includes('run')) return <RunIcon sx={{ fontSize: 12 }} />;
    if (type.includes('bike') || type.includes('cycling')) return <BikeIcon sx={{ fontSize: 12 }} />;
    if (type.includes('swim')) return <SwimIcon sx={{ fontSize: 12 }} />;
    if (type.includes('strength') || type.includes('gym')) return <StrengthIcon sx={{ fontSize: 12 }} />;
    return null;
  };

  const handleWorkoutClick = (workout: Workout) => {
    // Store current view context for potential navigation
    setSelectedWorkout(workout);
    setSelectedActivity(null);
    setDetailDialogOpen(true);
  };

  const handleActivityClick = (activity: GarminActivity) => {
    // Navigate to activity detail page, passing current date and view for return navigation
    navigate(`/activities/${activity.id}`, {
      state: { 
        weekStart: currentWeekStart.toISOString(),
        calendarView: calendarView,
        fromCalendar: true 
      }
    });
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

  const handleQuickAddOpen = (sport: 'running' | 'cycling' | 'swimming' | 'strength', date?: Date) => {
    setQuickAddSport(sport);
    setQuickAddDate(date || currentWeekStart);
    
    // Set smart defaults based on sport
    const defaults = {
      running: { title: 'Easy Run', duration: 45, tss: 50 },
      cycling: { title: 'Endurance Ride', duration: 90, tss: 70 },
      swimming: { title: 'Swim Workout', duration: 60, tss: 60 },
      strength: { title: 'Strength Training', duration: 45, tss: 30 },
    };
    
    setQuickAddTitle(defaults[sport].title);
    setQuickAddDuration(defaults[sport].duration);
    setQuickAddTSS(defaults[sport].tss);
    setQuickAddOpen(true);
  };

  const handleQuickAddSave = async () => {
    // Need to find or create a training plan first
    if (plans.length === 0) {
      setError('Please create a training plan first');
      return;
    }
    
    try {
      setQuickAddSaving(true);
      
      // Use first plan for now (TODO: let user select)
      const planId = plans[0].id;
      
      await api.post(`/training-plans/${planId}/workouts`, {
        date: format(quickAddDate, 'yyyy-MM-dd'),
        sport_type: quickAddSport,
        workout_type: 'custom',
        title: quickAddTitle,
        duration_minutes: quickAddDuration,
        tss: quickAddTSS,
      });
      
      setQuickAddOpen(false);
      await fetchData(); // Refresh calendar
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to create workout');
    } finally {
      setQuickAddSaving(false);
    }
  };

  const handleMonthDateClick = (date: Date) => {
    // Find Monday of the clicked date's week
    const dayOfWeek = date.getDay();
    const diff = dayOfWeek === 0 ? -6 : 1 - dayOfWeek;
    const monday = new Date(date);
    monday.setDate(date.getDate() + diff);
    monday.setHours(0, 0, 0, 0);
    
    // Set week start and switch to week view
    setCurrentWeekStart(monday);
    setCalendarView('week');
  };

  const dayNames = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'];
  const weeks = generateWeeks; // Use memoized array directly

  if (!user) {
    return null;
  }

  // Check if calendar is truly empty (no workouts AND no activities)
  const isCalendarEmpty = workouts.length === 0 && activities.length === 0;

  // Loading state
  if (loading) {
    return (
      <Container maxWidth="xl" sx={{ mt: 4, mb: 4 }}>
        <CalendarSkeleton />
      </Container>
    );
  }

  // Empty state
  if (isCalendarEmpty && !loading) {
    return (
      <Container maxWidth="xl" sx={{ mt: 4, mb: 4 }}>
        <Box sx={{ mb: 3 }}>
          <Typography variant="h4" component="h1" gutterBottom sx={{ fontWeight: 600 }}>
            Training Calendar
          </Typography>
        </Box>
        <EmptyState
          icon={<EventIcon />}
          title="No workouts scheduled"
          description="Your calendar is empty. Create a training plan to get started with scheduled workouts, or connect Garmin to see your past activities."
          actionLabel="Create Training Plan"
          onAction={() => navigate('/plans')}
          secondaryActionLabel="Connect Garmin"
          onSecondaryAction={() => navigate('/settings?tab=1')}
        />
      </Container>
    );
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

  // Mobile view (< 768px)
  if (isMobile) {
    return (
      <Box sx={{ height: 'calc(100vh - 120px)', display: 'flex', flexDirection: 'column', pb: 8 }}>
        {/* Mobile Header - Optimized for Option A */}
        <AppBar position="sticky" elevation={0} sx={{ bgcolor: 'background.paper', color: 'text.primary' }}>
          {/* Top Row: Navigation + View Toggle */}
          <Toolbar sx={{ justifyContent: 'space-between', minHeight: 48, py: 0.5 }}>
            <IconButton onClick={prevWeek} size="small">
              <ChevronLeftIcon />
            </IconButton>
            
            <ToggleButtonGroup
              value={calendarView}
              exclusive
              onChange={(e, newView) => {
                if (newView !== null) {
                  // When switching to week view, find Monday of current day
                  if (newView === 'week' && calendarView === 'day') {
                    const monday = startOfWeek(currentWeekStart, { weekStartsOn: 1 });
                    setCurrentWeekStart(monday);
                  }
                  setCalendarView(newView);
                }
              }}
              size="small"
            >
              <ToggleButton value="day" sx={{ px: 1.5, py: 0.5 }}>
                Day
              </ToggleButton>
              <ToggleButton value="week" sx={{ px: 1.5, py: 0.5 }}>
                Week
              </ToggleButton>
              <ToggleButton value="month" sx={{ px: 1.5, py: 0.5 }}>
                Month
              </ToggleButton>
            </ToggleButtonGroup>
            
            <IconButton onClick={nextWeek} size="small">
              <ChevronRightIcon />
            </IconButton>
          </Toolbar>

          {/* Fixed Week Wheel Picker - Only show in week view */}
          {calendarView === 'week' && (
            <Box 
              sx={{ 
                display: 'flex', 
                justifyContent: 'center',
                alignItems: 'center',
                py: 1.5, 
                px: 2,
                gap: 1,
              }}
            >
              {/* Previous 2 weeks - faded */}
              {[-2, -1].map((offset) => {
                const week = new Date(currentWeekStart);
                week.setDate(currentWeekStart.getDate() + (offset * 7));
                const weekNum = getWeek(week, { weekStartsOn: 1 });
                
                return (
                  <Box
                    key={offset}
                    onClick={() => setCurrentWeekStart(week)}
                    sx={{
                      minWidth: 48,
                      height: 48,
                      borderRadius: 1,
                      bgcolor: 'action.hover',
                      display: 'flex',
                      flexDirection: 'column',
                      alignItems: 'center',
                      justifyContent: 'center',
                      cursor: 'pointer',
                      opacity: offset === -1 ? 0.6 : 0.3,
                      transition: 'all 0.2s',
                      '&:active': {
                        transform: 'scale(0.95)',
                      },
                    }}
                  >
                    <Typography 
                      variant="caption" 
                      sx={{ 
                        fontSize: '0.65rem', 
                        fontWeight: 600,
                        color: 'text.secondary',
                        lineHeight: 1,
                      }}
                    >
                      CW {weekNum}
                    </Typography>
                    <Typography 
                      variant="caption" 
                      sx={{ 
                        fontSize: '0.8rem', 
                        fontWeight: 700,
                        color: 'text.secondary',
                        lineHeight: 1,
                        mt: 0.25,
                      }}
                    >
                      {format(week, 'MMM d')}
                    </Typography>
                  </Box>
                );
              })}

              {/* Current week - highlighted */}
              {(() => {
                const weekNum = getWeek(currentWeekStart, { weekStartsOn: 1 });
                const isToday = format(new Date(), 'yyyy-MM-dd') >= format(currentWeekStart, 'yyyy-MM-dd') && 
                                format(new Date(), 'yyyy-MM-dd') <= format(addDays(currentWeekStart, 6), 'yyyy-MM-dd');
                
                // Calculate week TSS
                const weekEnd = addDays(currentWeekStart, 6);
                const weekTSS = [...workouts, ...activities]
                  .filter(item => {
                    const itemDate = new Date(item.date);
                    return itemDate >= currentWeekStart && itemDate <= weekEnd;
                  })
                  .reduce((sum, item) => {
                    if ('target_tss' in item) {
                      return sum + (item.target_tss || 0);
                    } else {
                      const activity = item as GarminActivity;
                      return sum + (activity.calculated_tss || activity.training_load || 0);
                    }
                  }, 0);

                return (
                  <Box
                    sx={{
                      minWidth: 70,
                      height: 70,
                      borderRadius: 2,
                      bgcolor: 'primary.main',
                      display: 'flex',
                      flexDirection: 'column',
                      alignItems: 'center',
                      justifyContent: 'center',
                      border: isToday ? '3px solid' : '2px solid',
                      borderColor: isToday ? theme.palette.mode === 'dark' ? 'warning.main' : 'warning.light' : 'primary.main',
                      boxShadow: 3,
                      position: 'relative',
                    }}
                  >
                    <Typography 
                      variant="caption" 
                      sx={{ 
                        fontSize: '0.75rem', 
                        fontWeight: 700,
                        color: 'primary.contrastText',
                        lineHeight: 1,
                      }}
                    >
                      CW {weekNum}
                    </Typography>
                    <Typography 
                      variant="caption" 
                      sx={{ 
                        fontSize: '1rem', 
                        fontWeight: 900,
                        color: 'primary.contrastText',
                        lineHeight: 1,
                        mt: 0.5,
                      }}
                    >
                      {format(currentWeekStart, 'MMM d')}
                    </Typography>
                    {weekTSS > 0 && (
                      <Box 
                        sx={{ 
                          position: 'absolute',
                          bottom: 4,
                          width: '80%', 
                          height: 4, 
                          bgcolor: alpha(getTSSColor(weekTSS / 7).main, 0.8),
                          borderRadius: 1,
                        }} 
                      />
                    )}
                  </Box>
                );
              })()}

              {/* Next 2 weeks - faded */}
              {[1, 2].map((offset) => {
                const week = new Date(currentWeekStart);
                week.setDate(currentWeekStart.getDate() + (offset * 7));
                const weekNum = getWeek(week, { weekStartsOn: 1 });
                
                return (
                  <Box
                    key={offset}
                    onClick={() => setCurrentWeekStart(week)}
                    sx={{
                      minWidth: 48,
                      height: 48,
                      borderRadius: 1,
                      bgcolor: 'action.hover',
                      display: 'flex',
                      flexDirection: 'column',
                      alignItems: 'center',
                      justifyContent: 'center',
                      cursor: 'pointer',
                      opacity: offset === 1 ? 0.6 : 0.3,
                      transition: 'all 0.2s',
                      '&:active': {
                        transform: 'scale(0.95)',
                      },
                    }}
                  >
                    <Typography 
                      variant="caption" 
                      sx={{ 
                        fontSize: '0.65rem', 
                        fontWeight: 600,
                        color: 'text.secondary',
                        lineHeight: 1,
                      }}
                    >
                      CW {weekNum}
                    </Typography>
                    <Typography 
                      variant="caption" 
                      sx={{ 
                        fontSize: '0.8rem', 
                        fontWeight: 700,
                        color: 'text.secondary',
                        lineHeight: 1,
                        mt: 0.25,
                      }}
                    >
                      {format(week, 'MMM d')}
                    </Typography>
                  </Box>
                );
              })}
            </Box>
          )}
        </AppBar>

        {error && (
          <Alert severity="error" sx={{ mx: 2, my: 1 }} onClose={() => setError(null)}>
            {error}
          </Alert>
        )}

        {/* Calendar Content - Switch between Day, Week, and Month view */}
        {calendarView === 'day' ? (
          <Box sx={{ flex: 1, display: 'flex', flexDirection: 'column' }}>
            {/* Day View - Shows single day with details */}
            <Box
              {...swipeHandlers}
              sx={{
                display: 'flex',
                overflowX: 'hidden',
                flex: 1,
                position: 'relative',
              }}
            >
              <Box sx={{ flex: '0 0 100%', overflowY: 'auto', px: 2, pt: 2 }}>
                {/* Day Header */}
                <Typography variant="h5" sx={{ fontWeight: 700, mb: 2, textAlign: 'center' }}>
                  {format(currentWeekStart, 'EEEE, MMM d')}
                </Typography>

                {/* Day Summary */}
                {(() => {
                  const dayWorkouts = getWorkoutsForDate(currentWeekStart);
                  const dayActivities = getActivitiesForDate(currentWeekStart);
                  const dayTSS = [
                    ...dayWorkouts.filter(w => w.is_completed).map(w => w.tss || 0),
                    ...dayActivities.map(a => a.calculated_tss || 0)
                  ].reduce((sum, tss) => sum + tss, 0);

                  return (
                    <Box sx={{ mb: 3 }}>
                      <WeeklySummaryBar
                        totalTSS={Math.round(dayTSS)}
                        totalHours={0}
                        totalDistance={0}
                        last7DaysIF={[]}
                        last7DaysTSS={[]}
                      />
                    </Box>
                  );
                })()}

                {/* Planned Workouts */}
                {getWorkoutsForDate(currentWeekStart).length > 0 && (
                  <Box sx={{ mb: 3 }}>
                    <Typography variant="subtitle2" sx={{ mb: 1, color: 'text.secondary' }}>
                      Planned Workouts
                    </Typography>
                    {getWorkoutsForDate(currentWeekStart).map((workout) => (
                      <WorkoutCard
                        key={workout.id}
                        title={workout.title}
                        sport={workout.sport_type}
                        duration={workout.duration_minutes}
                        distance={workout.distance_km}
                        intensity={workout.intensity_zone}
                        tss={workout.target_tss}
                        isCompleted={workout.is_completed}
                        onClick={() => handleWorkoutClick(workout)}
                      />
                    ))}
                  </Box>
                )}

                {/* Completed Activities */}
                {getActivitiesForDate(currentWeekStart).length > 0 && (
                  <Box sx={{ mb: 3 }}>
                    <Typography variant="subtitle2" sx={{ mb: 1, color: 'text.secondary' }}>
                      Completed Activities
                    </Typography>
                    {getActivitiesForDate(currentWeekStart).map((activity) => (
                      <Card
                        key={activity.id}
                        onClick={() => handleActivityClick(activity)}
                        sx={{ mb: 1, cursor: 'pointer', '&:hover': { boxShadow: 3 } }}
                      >
                        <CardContent>
                          <Typography variant="subtitle1" sx={{ fontWeight: 600 }}>
                            {activity.activity_name}
                          </Typography>
                          <Typography variant="body2" color="text.secondary">
                            {activity.activity_type} • {Math.round(activity.duration_seconds / 60)} min
                          </Typography>
                        </CardContent>
                      </Card>
                    ))}
                  </Box>
                )}

                {/* Empty State */}
                {getWorkoutsForDate(currentWeekStart).length === 0 &&
                  getActivitiesForDate(currentWeekStart).length === 0 && (
                  <EmptyState
                    icon={<EventIcon />}
                    title="No workouts scheduled"
                    description="Swipe left or right to navigate days"
                  />
                )}
              </Box>
            </Box>
          </Box>
        ) : calendarView === 'month' ? (
          <Box sx={{ flex: 1, overflowY: 'auto', pt: 2 }}>
            <MonthCalendarView
              currentMonth={startOfMonth(currentWeekStart)}
              workouts={workouts}
              activities={activities}
              onDateClick={handleMonthDateClick}
            />
          </Box>
        ) : (
          /* Week View with Horizontal Scroll */
          <Box sx={{ flex: 1, display: 'flex', flexDirection: 'column' }}>
            {/* Horizontal Scrolling Week Container */}
            <Box
              ref={weekScrollRef}
              sx={{
                display: 'flex',
                overflowX: 'auto',
                scrollSnapType: 'none',
                WebkitOverflowScrolling: 'touch',
                flex: '0 0 auto',
                '&::-webkit-scrollbar': { display: 'none' },
                scrollbarWidth: 'none',
              }}
            >
              {/* Show 3 weeks: previous, current, next */}
              {[-1, 0, 1].map((weekOffset) => {
                const weekStart = new Date(currentWeekStart);
                weekStart.setDate(currentWeekStart.getDate() + (weekOffset * 7));
                
                return (
                  <Box
                    key={weekOffset}
                    sx={{
                      flex: '0 0 100%',
                      scrollSnapAlign: 'none',
                      overflowY: 'auto',
                      px: 1,
                      pb: 0,
                    }}
                  >
                    <MobileWeekGrid
                      currentWeekStart={weekStart}
                      workouts={workouts}
                      activities={activities}
                      onWorkoutClick={handleWorkoutClick}
                      onActivityClick={handleActivityClick}
                      onDateClick={(date) => {
                        // Switch to day view for the clicked date
                        setCurrentWeekStart(date);
                        setCalendarView('day');
                      }}
                      scrollRef={(el) => { weekGridScrollRefs.current[weekOffset] = el; }}
                    />
                  </Box>
                );
              })}
            </Box>

            {/* Week Summary Bar a1.5 Bottom */}
            <Box sx={{ px: 2, pt: 2, pb: 2, borderTop: 1, borderColor: 'divider', bgcolor: 'background.paper' }}>
              <WeeklySummaryBar
                totalTSS={weekSummary.totalTSS}
                totalHours={weekSummary.totalHours}
                totalDistance={weekSummary.totalDistance}
                last7DaysIF={weekSummary.last7DaysIF}
                last7DaysTSS={weekSummary.last7DaysTSS}
              />
            </Box>
          </Box>
        )}

        {/* Quick-Add FAB - Hidden on mobile */}
        {!isMobile && (
          <SpeedDial
            ariaLabel="Quick add workout"
            icon={<AddIcon />}
            direction="up"
            sx={{ position: 'fixed', bottom: 80, right: 16 }}
          >
            <SpeedDialAction
              icon={<RunIcon />}
              tooltipTitle="Quick Run"
              onClick={() => handleQuickAddOpen('running')}
            />
            <SpeedDialAction
              icon={<BikeIcon />}
              tooltipTitle="Quick Ride"
              onClick={() => handleQuickAddOpen('cycling')}
            />
            <SpeedDialAction
              icon={<SwimIcon />}
              tooltipTitle="Quick Swim"
              onClick={() => handleQuickAddOpen('swimming')}
            />
            <SpeedDialAction
              icon={<StrengthIcon />}
              tooltipTitle="Quick Strength"
              onClick={() => handleQuickAddOpen('strength')}
            />
          </SpeedDial>
        )}

        {/* Quick-Add Drawer */}
        <SwipeableDrawer
          anchor="bottom"
          open={quickAddOpen}
          onClose={() => setQuickAddOpen(false)}
          onOpen={() => {}}
        >
          <Box sx={{ p: 3, maxHeight: '70vh' }}>
            <Typography variant="h6" gutterBottom>
              Quick Add: {quickAddSport.charAt(0).toUpperCase() + quickAddSport.slice(1)}
            </Typography>
            
            <TextField
              label="Workout Title"
              value={quickAddTitle}
              onChange={(e) => setQuickAddTitle(e.target.value)}
              fullWidth
              sx={{ mt: 2 }}
            />

            <TextField
              label="Date"
              type="date"
              value={format(quickAddDate, 'yyyy-MM-dd')}
              onChange={(e) => setQuickAddDate(new Date(e.target.value))}
              fullWidth
              sx={{ mt: 2 }}
              InputLabelProps={{ shrink: true }}
            />

            <Stack direction="row" spacing={2} sx={{ mt: 2 }}>
              <TextField
                label="Duration (min)"
                type="number"
                value={quickAddDuration}
                onChange={(e) => setQuickAddDuration(parseInt(e.target.value) || 0)}
                fullWidth
              />
              <TextField
                label="TSS"
                type="number"
                value={quickAddTSS}
                onChange={(e) => setQuickAddTSS(parseInt(e.target.value) || 0)}
                fullWidth
              />
            </Stack>

            <Stack direction="row" spacing={2} sx={{ mt: 3 }}>
              <Button
                variant="outlined"
                fullWidth
                onClick={() => setQuickAddOpen(false)}
                disabled={quickAddSaving}
              >
                Cancel
              </Button>
              <Button
                variant="contained"
                fullWidth
                onClick={handleQuickAddSave}
                disabled={!quickAddTitle || quickAddSaving}
              >
                {quickAddSaving ? 'Saving...' : 'Add Workout'}
              </Button>
            </Stack>
          </Box>
        </SwipeableDrawer>
      </Box>
    );
  }

  // Desktop view (>= 768px)
  return (
    <Box sx={{
      position: 'fixed',
      top: { xs: 56, sm: 64 },
      bottom: { xs: 56, sm: 0 },
      left: 0,
      right: 0,
      display: 'flex',
      flexDirection: 'column',
      overflow: 'hidden',
    }}>
      <Container maxWidth="xl" sx={{ flex: 1, display: 'flex', flexDirection: 'column', overflow: 'hidden', p: 0, m: 0, maxWidth: '100% !important' }}>
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
          <Box sx={{ display: 'flex', borderBottom: 1, borderColor: 'divider', bgcolor: theme.palette.mode === 'dark' ? 'grey.900' : 'grey.100', position: 'sticky', top: 0, zIndex: 5, flexShrink: 0 }}>
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
            <Box sx={{ width: '200px', textAlign: 'center', fontWeight: 'bold', py: 1, bgcolor: 'primary.main', color: 'primary.contrastText', fontSize: '0.875rem' }}>
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
                          bgcolor: isToday ? 'primary.main' : 'action.selected', 
                          borderBottom: 1, 
                          borderColor: 'divider',
                          color: isToday ? 'primary.contrastText' : 'inherit',
                          minHeight: 28
                        }}>
                          <Typography variant="caption" fontWeight={isToday ? 'bold' : 'normal'} sx={{ fontSize: '0.75rem' }}>
                            {date.getDate()}
                          </Typography>
                          {(() => {
                            // Calculate target TSS from planned workouts
                            const targetTSS = dayWorkouts.reduce((sum, w) => sum + (w.target_tss || 0), 0);
                            const completedTSS = dailyTSS;
                            const displayTSS = completedTSS > 0 ? completedTSS : targetTSS;
                            
                            if (displayTSS > 0) {
                              const tssColor = getTSSColor(displayTSS);
                              return (
                                <Chip
                                  label={Math.round(displayTSS)}
                                  size="small"
                                  sx={{
                                    bgcolor: completedTSS > 0 ? tssColor.main : tssColor.main + '80',
                                    color: 'white',
                                    fontWeight: 600,
                                    height: 18,
                                    fontSize: '0.7rem',
                                    '& .MuiChip-label': { px: 0.75 }
                                  }}
                                />
                              );
                            }
                            return null;
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
                                bgcolor: workout.is_completed ? 'action.selected' : 'transparent',
                                color: 'text.primary',
                                cursor: 'pointer',
                                display: 'flex',
                                alignItems: 'center',
                                gap: 0.5,
                                '&:hover': { boxShadow: 1 },
                              }}
                            >
                              {workout.is_completed && <CheckCircleIcon sx={{ fontSize: 12, color: getSportColor(workout.sport_type).main }} />}
                              {getSportIcon(workout.sport_type)}
                              <Typography variant="caption" sx={{ fontSize: '0.7rem', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap', flexGrow: 1 }}>
                                {workout.title}
                              </Typography>
                              {workout.target_tss !== undefined && (
                                <Chip
                                  label={workout.target_tss || '-'}
                                  size="small"
                                  sx={{
                                    height: 16,
                                    fontSize: '0.65rem',
                                    bgcolor: workout.target_tss > 0 ? getTSSColor(workout.target_tss).main + '40' : 'action.disabled',
                                    color: 'text.primary',
                                    fontWeight: 600,
                                    '& .MuiChip-label': { px: 0.5 }
                                  }}
                                />
                              )}
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
                                bgcolor: 'action.selected',
                                color: 'text.primary',
                                border: 1.5,
                                borderColor: getSportColor(activity.activity_type).main,
                                cursor: 'pointer',
                                display: 'flex',
                                alignItems: 'center',
                                gap: 0.5,
                                '&:hover': { boxShadow: 1 },
                              }}
                            >
                              <CheckCircleIcon sx={{ fontSize: 12, color: getSportColor(activity.activity_type).main }} />
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
                    bgcolor: 'action.hover',
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
                    
                    {/* Time + Distance combined */}
                    <Box sx={{ 
                      fontSize: '0.75rem', 
                      display: 'flex', 
                      alignItems: 'center', 
                      gap: 0.75,
                      color: 'text.primary',
                      mb: 0.5
                    }}>
                      <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5, whiteSpace: 'nowrap' }}>
                        📏 {weekSummary.totalDistance} km
                      </Box>
                      <Box sx={{ color: 'text.secondary', fontSize: '0.65rem', lineHeight: 1 }}>
                        •
                      </Box>
                      <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5, whiteSpace: 'nowrap' }}>
                        ⏱ {weekSummary.totalHours}h {weekSummary.totalMinutes}m
                      </Box>
                    </Box>

                    {/* Mini Intensity Sparkline (IF-based color, TSS-based height) */}
                    {(() => {
                      const weekIFData = getWeekIFData(weekStart);
                      const weekTSSData = getWeekTSSData(weekStart);
                      const hasData = weekIFData.some(v => v > 0);
                      
                      if (!hasData) return null;
                      
                      const getIFColor = (intensity: number) => {
                        if (intensity === 0) return 'transparent';
                        if (intensity < 0.75) return theme.palette.success.main;
                        if (intensity < 0.85) return theme.palette.success.light;
                        if (intensity < 0.95) return theme.palette.warning.main;
                        if (intensity < 1.05) return theme.palette.warning.dark;
                        return theme.palette.error.main;
                      };
                      
                      const dayLabels = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'];
                      const maxTSS = 200; // Max TSS for 100% height
                      
                      return (
                        <Box sx={{ mb: 0.5 }}>
                          <Typography variant="caption" color="text.secondary" sx={{ fontSize: '0.65rem', mb: 0.25, display: 'block' }}>
                            Intensity
                          </Typography>
                          <Box sx={{ display: 'flex', gap: 0.25, alignItems: 'flex-end', height: 24 }}>
                            {weekIFData.map((intensity, idx) => {
                              const tss = weekTSSData[idx] || 0;
                              const height = tss === 0 ? 2 : Math.min((tss / maxTSS) * 100, 100);
                              const color = getIFColor(intensity);
                              
                              return (
                                <Tooltip 
                                  key={idx} 
                                  title={`${dayLabels[idx]}: ${intensity > 0 ? `IF ${intensity.toFixed(2)} | TSS ${Math.round(tss)}` : 'Rest'}`}
                                  arrow
                                  placement="top"
                                >
                                  <Box
                                    sx={{
                                      flex: 1,
                                      height: `${height}%`,
                                      minHeight: intensity > 0 ? 4 : 2,
                                      bgcolor: color,
                                      borderRadius: 0.25,
                                      cursor: 'help',
                                      border: intensity === 0 ? `1px dashed ${theme.palette.divider}` : 'none',
                                      transition: 'all 0.2s',
                                      '&:hover': {
                                        transform: 'scaleY(1.1)',
                                        filter: 'brightness(1.2)',
                                      }
                                    }}
                                  />
                                </Tooltip>
                              );
                            })}
                          </Box>
                        </Box>
                      );
                    })()}

                    {/* Visual separator */}
                    <Divider sx={{ my: 1, borderColor: 'divider', opacity: 0.5 }} />
                    
                    {/* Sport-specific distances */}
                    {parseFloat(weekSummary.runDistance) > 0 && (
                      <Typography variant="caption" sx={{ fontSize: '0.7rem', pl: 1 }}>
                        🏃 {weekSummary.runDistance} km ({weekSummary.runHours} h)
                      </Typography>
                    )}
                    {parseFloat(weekSummary.bikeDistance) > 0 && (
                      <Typography variant="caption" sx={{ fontSize: '0.7rem', pl: 1 }}>
                        🚴 {weekSummary.bikeDistance} km ({weekSummary.bikeHours} h)
                      </Typography>
                    )}
                    {parseFloat(weekSummary.swimDistance) > 0 && (
                      <Typography variant="caption" sx={{ fontSize: '0.7rem', pl: 1 }}>
                        🏊 {weekSummary.swimDistance} km ({weekSummary.swimHours} h)
                      </Typography>
                    )}
                    {parseFloat(weekSummary.skiDistance) > 0 && (
                      <Typography variant="caption" sx={{ fontSize: '0.7rem', pl: 1 }}>
                        ⛷️ {weekSummary.skiDistance} km ({weekSummary.skiHours} h)
                      </Typography>
                    )}
                    {parseFloat(weekSummary.tennisHours) > 0 && (
                      <Typography variant="caption" sx={{ fontSize: '0.7rem', pl: 1 }}>
                        🎾 {weekSummary.tennisHours} h
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
                <Box>
                  <Typography variant="body2" color="text.secondary">Target TSS</Typography>
                  <Typography 
                    variant="body1" 
                    sx={{ 
                      fontWeight: 600, 
                      color: selectedWorkout.target_tss ? getTSSColor(selectedWorkout.target_tss) : 'text.disabled' 
                    }}
                  >
                    {selectedWorkout.target_tss !== undefined && selectedWorkout.target_tss !== null 
                      ? selectedWorkout.target_tss 
                      : '-'}
                  </Typography>
                </Box>
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
          // Use pre-calculated Intensity Factor (IF) from backend
          const intensityFactor = selectedActivity.intensity_factor;
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
                  {intensityFactor != null && (
                    <Box sx={{ textAlign: 'center' }}>
                      <Typography variant="caption" color="text.secondary" sx={{ fontWeight: 600, textTransform: 'uppercase' }}>IF</Typography>
                      <Typography variant="h5" sx={{ fontWeight: 700, color: (() => {
                        if (intensityFactor < 0.75) return theme.palette.success.main;
                        if (intensityFactor < 0.85) return theme.palette.success.light;
                        if (intensityFactor < 0.95) return theme.palette.warning.main;
                        if (intensityFactor < 1.05) return theme.palette.warning.dark;
                        return theme.palette.error.main;
                      })() }}>
                        {intensityFactor.toFixed(2)}
                      </Typography>
                      <Typography variant="caption" color="text.secondary" sx={{ fontSize: '0.65rem', display: 'block', mt: -0.5 }}>
                        {intensityFactor < 0.75 ? 'Easy' : 
                         intensityFactor < 0.85 ? 'Endurance' : 
                         intensityFactor < 0.95 ? 'Tempo' : 
                         intensityFactor < 1.05 ? 'Threshold' : 'VO2max'}
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
    </Box>
  );
};

export default Calendar;
