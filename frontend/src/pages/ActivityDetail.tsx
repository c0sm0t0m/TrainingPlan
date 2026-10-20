/**
 * Activity Detail Page
 * 
 * Full-page view of a single activity with:
 * - Hero section with key metrics
 * - GPS map (if available)
 * - Time-series charts (pace, HR, power, elevation)
 * - Lap splits table
 * - Activity metadata
 */
import React, { useEffect, useState } from 'react';
import { useParams, useNavigate, useLocation } from 'react-router-dom';
import {
  Box,
  Container,
  Card,
  CardContent,
  Typography,
  Grid,
  IconButton,
  Breadcrumbs,
  Link,
  Skeleton,
  Alert,
  Chip,
  Button,
  CircularProgress,
  useTheme,
  useMediaQuery,
} from '@mui/material';
import {
  ArrowBack as ArrowBackIcon,
  Edit as EditIcon,
  Share as ShareIcon,
  MoreVert as MoreVertIcon,
  DirectionsRun as RunIcon,
  DirectionsBike as BikeIcon,
  Pool as SwimIcon,
  FitnessCenter as StrengthIcon,
  Favorite as FavoriteIcon,
  Terrain as TerrainIcon,
  LocalFireDepartment as CaloriesIcon,
  Speed as SpeedIcon,
  LinkOff as LinkOffIcon,
  Check as CheckIcon,
} from '@mui/icons-material';
import { format } from 'date-fns';
import api from '../services/api';
import ActivityMap from '../components/activity/ActivityMap';
import ActivityCharts from '../components/activity/ActivityCharts';
import ActivitySplits from '../components/activity/ActivitySplits';
import ActivityIgShareDialog from '../components/activity/ActivityIgShareDialog';
import { isCyclingSport } from '../utils/sportTypes';

// Types
interface Activity {
  id: number;
  garmin_activity_id: string;
  activity_name: string;
  activity_type: string;
  start_time_local: string;
  date: string;
  duration_seconds?: number;
  elapsed_duration_seconds?: number;
  moving_duration_seconds?: number;
  distance_meters?: number;
  average_speed_mps?: number;
  elevation_gain_meters?: number;
  elevation_loss_meters?: number;
  average_hr?: number;
  max_hr?: number;
  average_power_watts?: number;
  normalized_power_watts?: number;
  calculated_tss?: number;
  intensity_factor?: number;
  calories?: number;
  average_cadence?: number;
  location_name?: string;
  has_polyline: boolean;
  matched_workout?: {
    id: number;
    training_plan_id: number;
    title: string;
    date: string;
    sport_type: string;
    duration_minutes?: number;
    distance_km?: number;
    target_tss?: number;
    intensity_zone?: string;
    match_confidence?: number;
    match_status?: string;
    match_needs_review: boolean;
    performed_on_planned_day?: boolean;
    actual_date?: string | null;
    comparison?: {
      label: string;
      planned?: string | null;
      actual?: string | null;
      delta?: string | null;
      tone?: string;
    }[];
  } | null;
}

interface TrackPoint {
  lat: number;
  lng: number;
  ele?: number;
  timestamp?: string;
}

interface ActivityTrack {
  activity_id: number;
  track_points: TrackPoint[];
  total_points: number;
  has_elevation: boolean;
}

type MatchedWorkout = NonNullable<Activity['matched_workout']>;

function formatDayLabel(iso?: string | null): string {
  if (!iso) return '';
  const [year, month, day] = iso.slice(0, 10).split('-').map(Number);
  if (!year || !month || !day) return iso;
  return format(new Date(year, month - 1, day), 'EEE, MMM d');
}

function PlanVsActual({
  workout,
  linkBusy,
  onConfirm,
  onUnlink,
}: {
  workout: MatchedWorkout;
  linkBusy: boolean;
  onConfirm: () => void;
  onUnlink: () => void;
}) {
  const theme = useTheme();
  const rows = workout.comparison || [];
  const offPlan = workout.performed_on_planned_day === false;
  const toneColor = (tone?: string) => {
    if (tone === 'high') return theme.palette.error.main;
    if (tone === 'low') return theme.palette.info.main;
    if (tone === 'ok') return theme.palette.success.main;
    return theme.palette.text.secondary;
  };

  return (
    <Box
      sx={{
        mb: 3,
        border: 1,
        borderColor: 'divider',
        borderRadius: 1,
        px: 2,
        py: 1.5,
      }}
    >
      <Box sx={{ display: 'flex', justifyContent: 'space-between', gap: 1, alignItems: 'flex-start' }}>
        <Box sx={{ minWidth: 0 }}>
          <Typography variant="caption" color="text.secondary" sx={{ letterSpacing: 0.4 }}>
            Suggested vs actual
          </Typography>
          <Typography variant="subtitle1" fontWeight={600}>
            {workout.title}
          </Typography>
          {offPlan && (
            <Typography variant="body2" color="warning.main">
              Not done on the suggested day · planned {formatDayLabel(workout.date)} · done {formatDayLabel(workout.actual_date)}
            </Typography>
          )}
          {workout.match_needs_review && (
            <Typography variant="body2" color="text.secondary">
              Possible match
              {workout.match_confidence != null
                ? ` · ${Math.round(workout.match_confidence * 100)}%`
                : ''}
            </Typography>
          )}
        </Box>
        <Box sx={{ display: 'flex', gap: 1, flexShrink: 0 }}>
          {workout.match_needs_review && (
            <Button
              size="small"
              startIcon={linkBusy ? <CircularProgress size={14} /> : <CheckIcon />}
              disabled={linkBusy}
              onClick={onConfirm}
            >
              Confirm
            </Button>
          )}
          <Button
            size="small"
            color="inherit"
            startIcon={linkBusy ? <CircularProgress size={14} /> : <LinkOffIcon />}
            disabled={linkBusy}
            onClick={onUnlink}
          >
            Unlink
          </Button>
        </Box>
      </Box>

      {rows.length > 0 && (
        <Box
          sx={{
            mt: 1.5,
            display: 'grid',
            gridTemplateColumns: 'minmax(72px, 0.9fr) minmax(72px, 1fr) minmax(72px, 1fr) auto',
            columnGap: 1.5,
            rowGap: 0.75,
            alignItems: 'baseline',
          }}
        >
          <span />
          <Typography variant="caption" color="text.secondary">Suggested</Typography>
          <Typography variant="caption" color="text.secondary">Actual</Typography>
          <span />
          {rows.map((row) => (
            <React.Fragment key={row.label}>
              <Typography variant="body2" color="text.secondary">{row.label}</Typography>
              <Typography variant="body2">{row.planned || '—'}</Typography>
              <Typography variant="body2" fontWeight={600}>{row.actual || '—'}</Typography>
              <Typography variant="body2" sx={{ color: toneColor(row.tone), whiteSpace: 'nowrap' }}>
                {row.delta || ''}
              </Typography>
            </React.Fragment>
          ))}
        </Box>
      )}
    </Box>
  );
}

const ActivityDetail: React.FC = () => {
  const { activityId } = useParams<{ activityId: string }>();
  const navigate = useNavigate();
  const location = useLocation();
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('md'));

  const [activity, setActivity] = useState<Activity | null>(null);
  const [trackData, setTrackData] = useState<ActivityTrack | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [linkBusy, setLinkBusy] = useState(false);
  const [igShareOpen, setIgShareOpen] = useState(false);
  const [trackLoading, setTrackLoading] = useState(false);

  useEffect(() => {
    if (!activityId) return;
    fetchActivityDetail();
  }, [activityId]);

  const fetchActivityDetail = async () => {
    try {
      setLoading(true);
      setError(null);

      // Fetch main activity data
      const response = await api.get(`/activities/${activityId}`);
      setActivity(response.data);

      // Fetch GPS track if available (may lazy-download FIT — can take a few seconds)
      if (response.data.has_polyline) {
        try {
          setTrackLoading(true);
          const trackResponse = await api.get(`/activities/${activityId}/track`, {
            timeout: 120000,
          });
          setTrackData(trackResponse.data);
        } catch (err) {
          console.warn('Failed to load GPS track:', err);
        } finally {
          setTrackLoading(false);
        }
      } else {
        setTrackData(null);
      }
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to load activity');
    } finally {
      setLoading(false);
    }
  };

  const formatDuration = (seconds?: number): string => {
    if (!seconds) return '--';
    const hours = Math.floor(seconds / 3600);
    const minutes = Math.floor((seconds % 3600) / 60);
    const secs = Math.floor(seconds % 60);
    if (hours > 0) {
      return `${hours}:${String(minutes).padStart(2, '0')}:${String(secs).padStart(2, '0')}`;
    }
    return `${minutes}:${String(secs).padStart(2, '0')}`;
  };

  const formatPace = (speedMps?: number): string => {
    if (!speedMps || speedMps === 0) return '--';
    const minPerKm = 1000 / speedMps / 60;
    const min = Math.floor(minPerKm);
    const sec = Math.round((minPerKm - min) * 60);
    return `${min}:${String(sec).padStart(2, '0')} /km`;
  };

  const formatSpeedKmh = (speedMps?: number): string => {
    if (!speedMps || speedMps === 0) return '--';
    return `${(speedMps * 3.6).toFixed(1)} km/h`;
  };

  const formatDistance = (meters?: number): string => {
    if (!meters) return '--';
    return (meters / 1000).toFixed(2);
  };

  const getSportIcon = (activityType: string) => {
    const type = activityType.toLowerCase();
    if (isCyclingSport(activityType)) return <BikeIcon />;
    if (type.includes('run')) return <RunIcon />;
    if (type.includes('swim')) return <SwimIcon />;
    if (type.includes('strength') || type.includes('gym')) return <StrengthIcon />;
    return <RunIcon />;
  };

  const getTSSColor = (tss?: number): string => {
    if (!tss) return theme.palette.text.secondary;
    if (tss < 50) return theme.palette.success.main;
    if (tss < 100) return theme.palette.info.main;
    if (tss < 150) return theme.palette.warning.main;
    return theme.palette.error.main;
  };

  const getIFColor = (intensity?: number): string => {
    if (!intensity) return theme.palette.text.secondary;
    if (intensity < 0.75) return theme.palette.success.main;
    if (intensity < 0.85) return theme.palette.success.light;
    if (intensity < 0.95) return theme.palette.warning.main;
    if (intensity < 1.05) return theme.palette.warning.dark;
    return theme.palette.error.main;
  };

  const getIFLabel = (intensity?: number): string => {
    if (!intensity) return '';
    if (intensity < 0.75) return 'Easy';
    if (intensity < 0.85) return 'Endurance';
    if (intensity < 0.95) return 'Tempo';
    if (intensity < 1.05) return 'Threshold';
    return 'VO2max';
  };

  const handleBack = () => {
    // Check if we came from calendar with state
    const state = location.state as { weekStart?: string; fromCalendar?: boolean } | null;
    if (state?.fromCalendar && state?.weekStart) {
      // Navigate back to calendar with the week state preserved
      // Use replace: true to avoid creating duplicate history entries
      navigate('/calendar', { state: { weekStart: state.weekStart }, replace: true });
    } else {
      // Use browser history to go back
      navigate(-1);
    }
  };

  const handleEdit = () => {
    // TODO: Open edit dialog
    console.log('Edit activity:', activityId);
  };

  const handleShare = () => {
    setIgShareOpen(true);
  };

  const handleUnlink = async () => {
    if (!activityId || !activity?.matched_workout) return;
    if (!confirm('Unlink this activity from the planned workout? The plan will show on the calendar again.')) {
      return;
    }
    try {
      setLinkBusy(true);
      const response = await api.post(`/activities/${activityId}/unlink-workout`);
      setActivity(response.data);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to unlink');
    } finally {
      setLinkBusy(false);
    }
  };

  const handleConfirmMatch = async () => {
    if (!activityId) return;
    try {
      setLinkBusy(true);
      const response = await api.post(`/activities/${activityId}/confirm-match`);
      setActivity(response.data);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to confirm match');
    } finally {
      setLinkBusy(false);
    }
  };

  if (loading) {
    return (
      <Container maxWidth="xl" sx={{ py: 3 }}>
        <Skeleton variant="text" width={200} height={40} sx={{ mb: 2 }} />
        <Card sx={{ mb: 3 }}>
          <CardContent>
            <Skeleton variant="text" width="60%" height={48} sx={{ mb: 2 }} />
            <Skeleton variant="rectangular" height={120} />
          </CardContent>
        </Card>
        <Grid container spacing={3}>
          <Grid item xs={12} md={8}>
            <Skeleton variant="rectangular" height={400} />
          </Grid>
          <Grid item xs={12} md={4}>
            <Skeleton variant="rectangular" height={400} />
          </Grid>
        </Grid>
      </Container>
    );
  }

  if (error || !activity) {
    return (
      <Container maxWidth="xl" sx={{ py: 3 }}>
        <Alert severity="error" sx={{ mb: 2 }}>
          {error || 'Activity not found'}
        </Alert>
        <IconButton onClick={handleBack}>
          <ArrowBackIcon /> Back to Calendar
        </IconButton>
      </Container>
    );
  }

  return (
    <Container maxWidth="xl" sx={{ py: 3 }}>
      {/* Back Button */}
      <Box sx={{ mb: 2 }}>
        <IconButton onClick={handleBack} sx={{ mr: 1 }}>
          <ArrowBackIcon />
        </IconButton>
      </Box>

      {/* Breadcrumbs */}
      <Breadcrumbs sx={{ mb: 2 }}>
        <Link
          component="button"
          variant="body2"
          onClick={() => navigate('/dashboard')}
          sx={{ cursor: 'pointer' }}
        >
          Home
        </Link>
        <Link
          component="button"
          variant="body2"
          onClick={() => navigate('/calendar')}
          sx={{ cursor: 'pointer' }}
        >
          Calendar
        </Link>
        <Typography variant="body2" color="text.primary">
          {activity.activity_name}
        </Typography>
      </Breadcrumbs>

      {/* Hero Section */}
      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', mb: 3 }}>
            <Box sx={{ flex: 1 }}>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
                <Chip
                  icon={getSportIcon(activity.activity_type)}
                  label={activity.activity_type}
                  size="small"
                  color="primary"
                />
                {activity.location_name && (
                  <Chip label={activity.location_name} size="small" variant="outlined" />
                )}
              </Box>
              <Typography variant={isMobile ? 'h5' : 'h4'} gutterBottom fontWeight={600}>
                {activity.activity_name}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                {format(new Date(activity.start_time_local), 'EEEE, MMMM d, yyyy • h:mm a')}
              </Typography>
            </Box>
            <Box>
              <IconButton onClick={handleShare} aria-label="Share for Instagram" title="Share for Instagram">
                <ShareIcon />
              </IconButton>
              {!isMobile && (
                <>
                  <IconButton onClick={handleEdit}>
                    <EditIcon />
                  </IconButton>
                  <IconButton>
                    <MoreVertIcon />
                  </IconButton>
                </>
              )}
            </Box>
          </Box>

          {activity.matched_workout && (
            <PlanVsActual
              workout={activity.matched_workout}
              linkBusy={linkBusy}
              onConfirm={handleConfirmMatch}
              onUnlink={handleUnlink}
            />
          )}

          {/* Key Metrics Grid */}
          <Grid container spacing={3}>
            {activity.distance_meters && (
              <Grid item xs={6} sm={3}>
                <Box sx={{ textAlign: 'center' }}>
                  <Typography variant={isMobile ? 'h4' : 'h3'} fontWeight={700} color="primary">
                    {formatDistance(activity.distance_meters)}
                  </Typography>
                  <Typography variant="caption" color="text.secondary">
                    km
                  </Typography>
                </Box>
              </Grid>
            )}
            <Grid item xs={6} sm={3}>
              <Box sx={{ textAlign: 'center' }}>
                <Typography variant={isMobile ? 'h4' : 'h3'} fontWeight={700} color="primary">
                  {formatDuration(activity.duration_seconds)}
                </Typography>
                <Typography variant="caption" color="text.secondary">
                  duration
                </Typography>
              </Box>
            </Grid>
            {activity.average_speed_mps && (
              <Grid item xs={6} sm={3}>
                <Box sx={{ textAlign: 'center' }}>
                  <Typography variant={isMobile ? 'h5' : 'h3'} fontWeight={700} color="primary">
                    {isCyclingSport(activity.activity_type)
                      ? formatSpeedKmh(activity.average_speed_mps)
                      : formatPace(activity.average_speed_mps)}
                  </Typography>
                  <Typography variant="caption" color="text.secondary">
                    {isCyclingSport(activity.activity_type) ? 'avg speed' : 'avg pace'}
                  </Typography>
                </Box>
              </Grid>
            )}
            {activity.calculated_tss && (
              <Grid item xs={6} sm={3}>
                <Box sx={{ textAlign: 'center' }}>
                  <Typography variant={isMobile ? 'h4' : 'h3'} fontWeight={700} sx={{ color: getTSSColor(activity.calculated_tss) }}>
                    {Math.round(activity.calculated_tss)}
                  </Typography>
                  <Typography variant="caption" color="text.secondary">
                    TSS
                  </Typography>
                </Box>
              </Grid>
            )}
            {activity.intensity_factor && (
              <Grid item xs={6} sm={3}>
                <Box sx={{ textAlign: 'center' }}>
                  <Typography variant={isMobile ? 'h4' : 'h3'} fontWeight={700} sx={{ color: getIFColor(activity.intensity_factor) }}>
                    {activity.intensity_factor.toFixed(2)}
                  </Typography>
                  <Typography variant="caption" color="text.secondary">
                    IF · {getIFLabel(activity.intensity_factor)}
                  </Typography>
                </Box>
              </Grid>
            )}
          </Grid>
        </CardContent>
      </Card>

      {/* Main Content Grid */}
      <Grid container spacing={3}>
        {/* Left Column — charts first (power/pace), then map */}
        <Grid item xs={12} md={8}>
          <ActivityCharts activityId={activity.id} activityType={activity.activity_type} />

          {/* Map Card */}
          {activity.has_polyline && trackData && trackData.total_points > 0 ? (
            <Card sx={{ mb: 3 }}>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Route Map
                </Typography>
                <ActivityMap
                  trackPoints={trackData.track_points}
                  activityName={activity.activity_name}
                  showElevation={trackData.has_elevation}
                />
              </CardContent>
            </Card>
          ) : (
            <Card sx={{ mb: 3 }}>
              <CardContent>
                <Typography variant="body2" color="text.secondary" align="center">
                  {trackLoading
                    ? 'Loading GPS track…'
                    : activity.has_polyline
                      ? 'GPS track not available yet (open again after Garmin FIT sync)'
                      : 'No GPS data available for this activity'}
                </Typography>
                {trackLoading && (
                  <Box sx={{ display: 'flex', justifyContent: 'center', mt: 2 }}>
                    <CircularProgress size={28} />
                  </Box>
                )}
              </CardContent>
            </Card>
          )}
        </Grid>

        {/* Right Column - Stats & Splits */}
        <Grid item xs={12} md={4}>
          {/* Stats Card */}
          <Card sx={{ mb: 3 }}>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Performance Stats
              </Typography>
              <Grid container spacing={2}>
                {activity.average_hr && (
                  <Grid item xs={6}>
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                      <FavoriteIcon sx={{ color: 'error.main', fontSize: 20 }} />
                      <Box>
                        <Typography variant="body2" fontWeight={600}>
                          {activity.average_hr} bpm
                        </Typography>
                        <Typography variant="caption" color="text.secondary">
                          Avg HR
                        </Typography>
                      </Box>
                    </Box>
                  </Grid>
                )}
                {activity.max_hr && (
                  <Grid item xs={6}>
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                      <FavoriteIcon sx={{ color: 'error.main', fontSize: 20 }} />
                      <Box>
                        <Typography variant="body2" fontWeight={600}>
                          {activity.max_hr} bpm
                        </Typography>
                        <Typography variant="caption" color="text.secondary">
                          Max HR
                        </Typography>
                      </Box>
                    </Box>
                  </Grid>
                )}
                {activity.elevation_gain_meters && (
                  <Grid item xs={6}>
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                      <TerrainIcon sx={{ color: 'success.main', fontSize: 20 }} />
                      <Box>
                        <Typography variant="body2" fontWeight={600}>
                          +{Math.round(activity.elevation_gain_meters)} m
                        </Typography>
                        <Typography variant="caption" color="text.secondary">
                          Elevation
                        </Typography>
                      </Box>
                    </Box>
                  </Grid>
                )}
                {activity.calories && (
                  <Grid item xs={6}>
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                      <CaloriesIcon sx={{ color: 'warning.main', fontSize: 20 }} />
                      <Box>
                        <Typography variant="body2" fontWeight={600}>
                          {activity.calories}
                        </Typography>
                        <Typography variant="caption" color="text.secondary">
                          Calories
                        </Typography>
                      </Box>
                    </Box>
                  </Grid>
                )}
                {activity.average_cadence && (
                  <Grid item xs={6}>
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                      <SpeedIcon sx={{ color: 'info.main', fontSize: 20 }} />
                      <Box>
                        <Typography variant="body2" fontWeight={600}>
                          {Math.round(activity.average_cadence)}{' '}
                          {isCyclingSport(activity.activity_type) ? 'rpm' : 'spm'}
                        </Typography>
                        <Typography variant="caption" color="text.secondary">
                          Cadence
                        </Typography>
                      </Box>
                    </Box>
                  </Grid>
                )}
                {activity.normalized_power_watts && (
                  <Grid item xs={6}>
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                      <SpeedIcon sx={{ color: 'warning.main', fontSize: 20 }} />
                      <Box>
                        <Typography variant="body2" fontWeight={600}>
                          {Math.round(activity.normalized_power_watts)} W
                        </Typography>
                        <Typography variant="caption" color="text.secondary">
                          NP
                        </Typography>
                      </Box>
                    </Box>
                  </Grid>
                )}
                {activity.average_power_watts && (
                  <Grid item xs={6}>
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                      <SpeedIcon sx={{ color: 'warning.dark', fontSize: 20 }} />
                      <Box>
                        <Typography variant="body2" fontWeight={600}>
                          {Math.round(activity.average_power_watts)} W
                        </Typography>
                        <Typography variant="caption" color="text.secondary">
                          Avg power
                        </Typography>
                      </Box>
                    </Box>
                  </Grid>
                )}
              </Grid>
            </CardContent>
          </Card>

          <ActivitySplits activityId={activity.id} activityType={activity.activity_type} />
        </Grid>
      </Grid>

      <ActivityIgShareDialog
        open={igShareOpen}
        onClose={() => setIgShareOpen(false)}
        activityName={activity.activity_name}
        activityType={activity.activity_type}
        startTimeLocal={activity.start_time_local}
        durationSeconds={activity.duration_seconds}
        distanceMeters={activity.distance_meters}
        calculatedTss={activity.calculated_tss}
        trackPoints={trackData?.track_points}
        matchedWorkout={
          activity.matched_workout
            ? {
                title: activity.matched_workout.title,
                duration_minutes: activity.matched_workout.duration_minutes,
                distance_km: activity.matched_workout.distance_km,
                target_tss: activity.matched_workout.target_tss,
              }
            : null
        }
      />
    </Container>
  );
};

export default ActivityDetail;
