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
} from '@mui/icons-material';
import { format } from 'date-fns';
import api from '../services/api';
import ActivityMap from '../components/activity/ActivityMap';

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

      // Fetch GPS track if available
      if (response.data.has_polyline) {
        try {
          const trackResponse = await api.get(`/activities/${activityId}/track`);
          setTrackData(trackResponse.data);
        } catch (err) {
          console.warn('Failed to load GPS track:', err);
        }
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

  const formatDistance = (meters?: number): string => {
    if (!meters) return '--';
    return (meters / 1000).toFixed(2);
  };

  const getSportIcon = (activityType: string) => {
    const type = activityType.toLowerCase();
    if (type.includes('run')) return <RunIcon />;
    if (type.includes('bike') || type.includes('cycl')) return <BikeIcon />;
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

  const handleShare = async () => {
    if (navigator.share) {
      try {
        await navigator.share({
          title: activity?.activity_name || 'Activity',
          text: `Check out my ${activity?.activity_type}`,
          url: window.location.href,
        });
      } catch (err) {
        console.log('Share cancelled or failed:', err);
      }
    } else {
      // Fallback: Copy link
      navigator.clipboard.writeText(window.location.href);
      alert('Link copied to clipboard!');
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
              {!isMobile && (
                <>
                  <IconButton onClick={handleEdit}>
                    <EditIcon />
                  </IconButton>
                  <IconButton onClick={handleShare}>
                    <ShareIcon />
                  </IconButton>
                  <IconButton>
                    <MoreVertIcon />
                  </IconButton>
                </>
              )}
            </Box>
          </Box>

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
                    {formatPace(activity.average_speed_mps)}
                  </Typography>
                  <Typography variant="caption" color="text.secondary">
                    avg pace
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
        {/* Left Column - Map & Charts (Placeholder) */}
        <Grid item xs={12} md={8}>
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
                  No GPS data available for this activity
                </Typography>
              </CardContent>
            </Card>
          )}

          {/* Charts Card (Placeholder) */}
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Activity Charts
              </Typography>
              <Box
                sx={{
                  height: 300,
                  bgcolor: 'grey.100',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  borderRadius: 1,
                }}
              >
                <Typography variant="body2" color="text.secondary">
                  Charts will be here (HR, Pace, Power, Elevation)
                </Typography>
              </Box>
            </CardContent>
          </Card>
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
                          {Math.round(activity.average_cadence)} spm
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
              </Grid>
            </CardContent>
          </Card>

          {/* Splits Card (Placeholder) */}
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Lap Splits
              </Typography>
              <Box
                sx={{
                  minHeight: 200,
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                }}
              >
                <Typography variant="body2" color="text.secondary">
                  Splits will be here
                </Typography>
              </Box>
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </Container>
  );
};

export default ActivityDetail;
