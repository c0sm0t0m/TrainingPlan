import React, { useState, useEffect } from 'react';
import {
  Container,
  Paper,
  Typography,
  Box,
  Button,
  TextField,
  Alert,
  CircularProgress,
  Card,
  CardContent,
  CardActions,
  Divider,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Tabs,
  Tab,
  Grid,
  InputAdornment,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  Chip,
  useMediaQuery,
  useTheme,
  Menu,
  IconButton,
  ListItemIcon,
  ListItemText,
  FormControlLabel,
  Checkbox,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  Stack,
} from '@mui/material';
import {
  Link as LinkIcon,
  LinkOff as LinkOffIcon,
  Sync as SyncIcon,
  CheckCircle as CheckCircleIcon,
  DirectionsBike as BikeIcon,
  DirectionsRun as RunIcon,
  Pool as SwimIcon,
  Favorite as HeartIcon,
  Save as SaveIcon,
  Calculate as CalculateIcon,
  Info as InfoIcon,
  Science as ExperimentIcon,
  Settings as SettingsIcon,
  MoreVert as MoreVertIcon,
  FitnessCenter as FitnessCenterIcon,
  ExpandMore as ExpandMoreIcon,
  LibraryBooks as LibraryIcon,
} from '@mui/icons-material';
import apiClient from '../services/api';
import FeatureFlagsPanel from '../components/FeatureFlagsPanel';
import Breadcrumbs from '../components/Breadcrumbs';
import {
  getLibraryPreferences,
  listWorkoutTemplates,
  updateLibraryPreferences,
  WorkoutTemplateSummary,
} from '../services/workoutLibrary';

interface GarminStatus {
  connected: boolean;
  email: string | null;
  last_sync: string | null;
}

interface IcuStatus {
  connected: boolean;
  athlete_id: string | null;
  athlete_name: string | null;
  last_sync: string | null;
}

interface UserThresholds {
  // Cycling
  ftp: number | null;
  cycling_threshold_hr: number | null;
  
  // Running  
  threshold_pace: number | null;  // seconds per km
  running_threshold_hr: number | null;
  
  // Swimming
  swim_threshold_pace: number | null;  // seconds per 100m
  swim_threshold_hr: number | null;
  
  // General HR
  max_hr: number | null;
  resting_hr: number | null;
}

interface TabPanelProps {
  children?: React.ReactNode;
  index: number;
  value: number;
}

function TabPanel(props: TabPanelProps) {
  const { children, value, index, ...other } = props;

  return (
    <div
      role="tabpanel"
      hidden={value !== index}
      id={`settings-tabpanel-${index}`}
      aria-labelledby={`settings-tab-${index}`}
      {...other}
    >
      {value === index && <Box sx={{ py: 3 }}>{children}</Box>}
    </div>
  );
}

const SettingsNew: React.FC = () => {
  const theme = useTheme();
  const isMobile = useMediaQuery('(max-width:900px)');
  const [tabValue, setTabValue] = useState(0);
  const [garminStatus, setGarminStatus] = useState<GarminStatus | null>(null);
  const [icuStatus, setIcuStatus] = useState<IcuStatus | null>(null);
  const [menuAnchor, setMenuAnchor] = useState<null | HTMLElement>(null);
  const [thresholds, setThresholds] = useState<UserThresholds>({
    ftp: null,
    cycling_threshold_hr: null,
    threshold_pace: null,
    running_threshold_hr: null,
    swim_threshold_pace: null,
    swim_threshold_hr: null,
    max_hr: null,
    resting_hr: null,
  });
  
  // Zone calculation method selections
  const [runningHRMethod, setRunningHRMethod] = useState('friel');
  const [powerMethod, setPowerMethod] = useState('coggan');
  const [runPaceMethod, setRunPaceMethod] = useState('friel');
  const [swimPaceMethod, setSwimPaceMethod] = useState('friel');
  
  // Current zones (applied/saved)
  const [cyclingPowerZones, setCyclingPowerZones] = useState<any[]>([]);
  const [runningPaceZones, setRunningPaceZones] = useState<any[]>([]);
  const [runningHRZones, setRunningHRZones] = useState<any[]>([]);
  const [swimPaceZones, setSwimPaceZones] = useState<any[]>([]);
  
  // Preview zones (calculated but not applied)
  const [previewCyclingPowerZones, setPreviewCyclingPowerZones] = useState<any[] | null>(null);
  const [previewRunningPaceZones, setPreviewRunningPaceZones] = useState<any[] | null>(null);
  const [previewRunningHRZones, setPreviewRunningHRZones] = useState<any[] | null>(null);
  const [previewSwimPaceZones, setPreviewSwimPaceZones] = useState<any[] | null>(null);
  
  // Zone calculation loading states
  const [calculatingPowerZones, setCalculatingPowerZones] = useState(false);
  const [calculatingRunPaceZones, setCalculatingRunPaceZones] = useState(false);
  const [calculatingRunHRZones, setCalculatingRunHRZones] = useState(false);
  const [calculatingSwimPaceZones, setCalculatingSwimPaceZones] = useState(false);
  
  // Temporary text values for pace inputs (allows partial input like "4:" before "4:30")
  const [runPaceText, setRunPaceText] = useState<string>('');
  const [swimPaceText, setSwimPaceText] = useState<string>('');
  
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [syncDays, setSyncDays] = useState(30);
  const [connecting, setConnecting] = useState(false);
  const [icuConnecting, setIcuConnecting] = useState(false);
  const [syncing, setSyncing] = useState(false);
  const [icuSyncing, setIcuSyncing] = useState(false);
  const [healthSyncing, setHealthSyncing] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);
  
  // Connect dialog state
  const [connectDialogOpen, setConnectDialogOpen] = useState(false);
  const [icuConnectDialogOpen, setIcuConnectDialogOpen] = useState(false);
  const [garminEmail, setGarminEmail] = useState('');
  const [garminPassword, setGarminPassword] = useState('');
  const [icuApiKey, setIcuApiKey] = useState('');
  const [icuDaysAhead, setIcuDaysAhead] = useState(14);

  // Workout library (Calendar add picker)
  const [libraryTemplates, setLibraryTemplates] = useState<WorkoutTemplateSummary[]>([]);
  const [libraryEnabledIds, setLibraryEnabledIds] = useState<Set<string>>(new Set());
  const [libraryUsingDefaults, setLibraryUsingDefaults] = useState(true);
  const [libraryLoading, setLibraryLoading] = useState(false);
  const [librarySaving, setLibrarySaving] = useState(false);
  
  // Sync progress state
  const [syncProgressOpen, setSyncProgressOpen] = useState(false);
  const [syncElapsedTime, setSyncElapsedTime] = useState(0);
  const [syncActivityCount, setSyncActivityCount] = useState(0);
  const [initialActivityCount, setInitialActivityCount] = useState(0);
  const [syncStartDate, setSyncStartDate] = useState<string>('');
  const [syncEndDate, setSyncEndDate] = useState<string>('');
  const [syncProgress, setSyncProgress] = useState(0);

  // Helper to convert pace (min:sec/km) to seconds
  const paceToSeconds = (minPerKm: string): number | null => {
    if (!minPerKm) return null;
    const parts = minPerKm.split(':');
    if (parts.length !== 2) return null;
    const min = parseInt(parts[0]);
    const sec = parseInt(parts[1]);
    if (isNaN(min) || isNaN(sec)) return null;
    return min * 60 + sec;
  };

  // Helper to convert seconds to pace (min:sec/km)
  const secondsToPace = (seconds: number | null): string => {
    if (!seconds) return '';
    const min = Math.floor(seconds / 60);
    const sec = seconds % 60;
    return `${min}:${sec.toString().padStart(2, '0')}`;
  };

  // Helper to safely parse integer input
  const parseIntInput = (value: string): number | null => {
    if (!value || value.trim() === '') return null;
    const parsed = parseInt(value);
    return isNaN(parsed) ? null : parsed;
  };

  useEffect(() => {
    document.title = 'Settings - Kinesis';
    fetchSettings();
  }, []);

  // Load zones once when settings are fetched (not on threshold changes)
  useEffect(() => {
    // Only load zones once when component mounts and we have saved thresholds
    if (thresholds.ftp && cyclingPowerZones.length === 0) {
      calculateCyclingPowerZones(thresholds.ftp, powerMethod, false);
    }
    if (thresholds.threshold_pace && runningPaceZones.length === 0) {
      calculateRunningPaceZones(thresholds.threshold_pace, runPaceMethod, false);
    }
    if (thresholds.running_threshold_hr && thresholds.max_hr && runningHRZones.length === 0) {
      calculateRunningHRZones(thresholds.running_threshold_hr, thresholds.max_hr, runningHRMethod, false);
    }
    if (thresholds.swim_threshold_pace && swimPaceZones.length === 0) {
      calculateSwimPaceZones(thresholds.swim_threshold_pace, swimPaceMethod, false);
    }
  }, [loading]);

  const fetchSettings = async () => {
    try {
      setLoading(true);
      
      // Fetch Garmin + ICU status
      const [garminResponse, icuResponse] = await Promise.all([
        apiClient.get('/garmin/status'),
        apiClient.get('/icu/status').catch(() => ({ data: { connected: false, athlete_id: null, athlete_name: null, last_sync: null } })),
      ]);
      setGarminStatus(garminResponse.data);
      setIcuStatus(icuResponse.data);
      
      // Fetch user thresholds
      const thresholdsResponse = await apiClient.get('/auth/me');
      const userData = thresholdsResponse.data;
      
      setThresholds({
        ftp: userData.ftp,
        cycling_threshold_hr: userData.cycling_threshold_hr,
        threshold_pace: userData.threshold_pace,
        running_threshold_hr: userData.running_threshold_hr,
        swim_threshold_pace: userData.swim_threshold_pace,
        swim_threshold_hr: userData.swim_threshold_hr,
        max_hr: userData.max_hr,
        resting_hr: userData.resting_hr,
      });
      
      // Initialize pace text fields
      setRunPaceText(secondsToPace(userData.threshold_pace));
      setSwimPaceText(secondsToPace(userData.swim_threshold_pace));

      // Workout library preferences
      try {
        setLibraryLoading(true);
        const [templates, prefs] = await Promise.all([
          listWorkoutTemplates(),
          getLibraryPreferences(),
        ]);
        setLibraryTemplates(templates);
        const ids =
          prefs.enabled_ids ??
          prefs.default_ids ??
          [];
        setLibraryEnabledIds(new Set(ids));
        setLibraryUsingDefaults(prefs.using_defaults);
      } catch {
        // non-fatal
      } finally {
        setLibraryLoading(false);
      }
    } catch (err: any) {
      setError('Failed to load settings');
    } finally {
      setLoading(false);
    }
  };

  const toggleLibraryTemplate = (id: string) => {
    setLibraryEnabledIds((prev) => {
      const next = new Set(prev);
      if (next.has(id)) next.delete(id);
      else next.add(id);
      return next;
    });
    setLibraryUsingDefaults(false);
  };

  const selectAllLibrary = () => {
    setLibraryEnabledIds(new Set(libraryTemplates.map((t) => t.id)));
    setLibraryUsingDefaults(false);
  };

  const clearLibrary = () => {
    setLibraryEnabledIds(new Set());
    setLibraryUsingDefaults(false);
  };

  const handleSaveLibraryPreferences = async () => {
    try {
      setLibrarySaving(true);
      setError(null);
      const prefs = await updateLibraryPreferences(Array.from(libraryEnabledIds));
      setLibraryUsingDefaults(prefs.using_defaults);
      setSuccess(
        `Workout library updated — ${libraryEnabledIds.size} templates in Calendar add`
      );
      setTimeout(() => setSuccess(null), 3000);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to save workout library');
    } finally {
      setLibrarySaving(false);
    }
  };

  const handleSaveThresholds = async () => {
    try {
      setSaving(true);
      setError(null);
      
      await apiClient.patch('/auth/me', thresholds);
      
      setSuccess('Training zones saved successfully!');
      setTimeout(() => setSuccess(null), 3000);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to save settings');
    } finally {
      setSaving(false);
    }
  };

  const fetchZones = async (zoneType: string, method: string, threshold?: number, maxHr?: number) => {
    try {
      // Build query params based on zone type
      let url = `/auth/zones/${zoneType}?method=${method}`;
      if (threshold !== undefined) {
        url += `&threshold=${threshold}`;
      }
      if (maxHr !== undefined) {
        url += `&max_hr=${maxHr}`;
      }
      
      const response = await apiClient.get(url);
      return response.data;
    } catch (err: any) {
      console.error(`Failed to fetch ${zoneType} zones:`, err);
      setError(err.response?.data?.detail || `Failed to calculate ${zoneType} zones`);
      return [];
    }
  };

  // Calculate cycling power zones from current UI value
  const calculateCyclingPowerZones = async (ftpValue: number | null, method: string, isPreview: boolean) => {
    if (!ftpValue || ftpValue <= 0) return;
    
    setCalculatingPowerZones(true);
    try {
      const zones = await fetchZones('power', method, ftpValue);
      if (isPreview) {
        setPreviewCyclingPowerZones(zones);
      } else {
        setCyclingPowerZones(zones);
        setPreviewCyclingPowerZones(null);
      }
    } finally {
      setCalculatingPowerZones(false);
    }
  };

  // Calculate running pace zones from current UI value
  const calculateRunningPaceZones = async (paceValue: number | null, method: string, isPreview: boolean) => {
    if (!paceValue || paceValue <= 0) return;
    
    setCalculatingRunPaceZones(true);
    try {
      const zones = await fetchZones('pace_running', method, paceValue);
      if (isPreview) {
        setPreviewRunningPaceZones(zones);
      } else {
        setRunningPaceZones(zones);
        setPreviewRunningPaceZones(null);
      }
    } finally {
      setCalculatingRunPaceZones(false);
    }
  };

  // Calculate running HR zones from current UI value
  const calculateRunningHRZones = async (thresholdHR: number | null, maxHR: number | null, method: string, isPreview: boolean) => {
    if (!thresholdHR || thresholdHR <= 0 || !maxHR || maxHR <= 0) return;
    
    setCalculatingRunHRZones(true);
    try {
      const zones = await fetchZones('hr_running', method, thresholdHR, maxHR);
      if (isPreview) {
        setPreviewRunningHRZones(zones);
      } else {
        setRunningHRZones(zones);
        setPreviewRunningHRZones(null);
      }
    } finally {
      setCalculatingRunHRZones(false);
    }
  };

  // Calculate swim pace zones from current UI value
  const calculateSwimPaceZones = async (paceValue: number | null, method: string, isPreview: boolean) => {
    if (!paceValue || paceValue <= 0) return;
    
    setCalculatingSwimPaceZones(true);
    try {
      const zones = await fetchZones('pace_swimming', method, paceValue);
      if (isPreview) {
        setPreviewSwimPaceZones(zones);
      } else {
        setSwimPaceZones(zones);
        setPreviewSwimPaceZones(null);
      }
    } finally {
      setCalculatingSwimPaceZones(false);
    }
  };

  // Apply preview zones and save threshold
  const applyPowerZones = async () => {
    if (previewCyclingPowerZones) {
      setCyclingPowerZones(previewCyclingPowerZones);
      setPreviewCyclingPowerZones(null);
      // Save FTP to backend
      await handleSaveThresholds();
    }
  };

  const applyRunPaceZones = async () => {
    if (previewRunningPaceZones) {
      setRunningPaceZones(previewRunningPaceZones);
      setPreviewRunningPaceZones(null);
      // Save threshold pace to backend
      await handleSaveThresholds();
    }
  };

  const applyRunHRZones = async () => {
    if (previewRunningHRZones) {
      setRunningHRZones(previewRunningHRZones);
      setPreviewRunningHRZones(null);
      // Save threshold HR to backend
      await handleSaveThresholds();
    }
  };

  const applySwimPaceZones = async () => {
    if (previewSwimPaceZones) {
      setSwimPaceZones(previewSwimPaceZones);
      setPreviewSwimPaceZones(null);
      // Save swim threshold pace to backend
      await handleSaveThresholds();
    }
  };

  // Discard preview zones
  // Zone display component - shows current and preview side-by-side
  const renderZoneDisplay = (
    currentZones: any[],
    previewZones: any[] | null,
    formatValue: (zone: any) => string,
    onApply: () => void,
    zoneLabel: string
  ) => {
    if (currentZones.length === 0 && !previewZones) {
      return (
        <Box sx={{ mt: 2, p: 2, bgcolor: 'background.default', borderRadius: 1 }}>
          <Typography variant="body2" color="text.secondary">
            Configure your threshold value and select a calculation method, then click Recalculate to see your zones.
          </Typography>
        </Box>
      );
    }

    return (
      <Box sx={{ mt: 2 }}>
        <Grid container spacing={2}>
          {/* Current Zones */}
          {currentZones.length > 0 && (
            <Grid item xs={12} md={previewZones ? 6 : 12}>
              <Box sx={{ p: 2, bgcolor: 'background.default', borderRadius: 1 }}>
                <Typography variant="subtitle2" gutterBottom sx={{ fontWeight: 'bold' }}>
                  Current {zoneLabel}
                </Typography>
                {currentZones.map((zone) => (
                  <Box key={zone.zone} sx={{ display: 'flex', justifyContent: 'space-between', py: 0.5 }}>
                    <Typography variant="body2">Zone {zone.zone}: {zone.name}</Typography>
                    <Typography variant="body2" fontWeight="medium">{formatValue(zone)}</Typography>
                  </Box>
                ))}
              </Box>
            </Grid>
          )}

          {/* Preview Zones */}
          {previewZones && (
            <Grid item xs={12} md={6}>
              <Box sx={{ p: 2, bgcolor: 'success.lighter', borderRadius: 1, border: '2px solid', borderColor: 'success.main' }}>
                <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 1 }}>
                  <Typography variant="subtitle2" sx={{ fontWeight: 'bold', color: 'success.dark' }}>
                    New {zoneLabel}
                  </Typography>
                  <Button size="small" onClick={onApply} variant="contained" color="success">
                    Apply & Save
                  </Button>
                </Box>
                {previewZones.map((zone) => (
                  <Box key={zone.zone} sx={{ display: 'flex', justifyContent: 'space-between', py: 0.5 }}>
                    <Typography variant="body2" fontWeight="medium">Zone {zone.zone}: {zone.name}</Typography>
                    <Typography variant="body2" fontWeight="bold" color="success.dark">{formatValue(zone)}</Typography>
                  </Box>
                ))}
              </Box>
            </Grid>
          )}
        </Grid>
      </Box>
    );
  };

  const handleConnectGarmin = async () => {
    if (!garminEmail || !garminPassword) {
      setError('Please enter both email and password');
      return;
    }

    try {
      setConnecting(true);
      setError(null);
      
      await apiClient.post('/garmin/connect', {
        email: garminEmail,
        password: garminPassword,
      });
      
      setSuccess('Successfully connected to Garmin!');
      setConnectDialogOpen(false);
      setGarminEmail('');
      setGarminPassword('');
      
      await fetchSettings();
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to connect to Garmin');
    } finally {
      setConnecting(false);
    }
  };

  const handleDisconnectGarmin = async () => {
    try {
      setConnecting(true);
      await apiClient.post('/garmin/disconnect');
      setSuccess('Disconnected from Garmin');
      await fetchSettings();
    } catch (err: any) {
      setError('Failed to disconnect from Garmin');
    } finally {
      setConnecting(false);
    }
  };

  const handleConnectIcu = async () => {
    if (!icuApiKey.trim()) {
      setError('Please enter your Intervals.icu API key');
      return;
    }
    try {
      setIcuConnecting(true);
      setError(null);
      await apiClient.post('/icu/connect', { api_key: icuApiKey.trim() });
      setSuccess('Successfully connected to Intervals.icu!');
      setIcuConnectDialogOpen(false);
      setIcuApiKey('');
      await fetchSettings();
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to connect to Intervals.icu');
    } finally {
      setIcuConnecting(false);
    }
  };

  const handleDisconnectIcu = async () => {
    try {
      setIcuConnecting(true);
      setError(null);
      await apiClient.delete('/icu/disconnect');
      setSuccess('Disconnected from Intervals.icu');
      await fetchSettings();
    } catch (err: any) {
      setError('Failed to disconnect from Intervals.icu');
    } finally {
      setIcuConnecting(false);
    }
  };

  const handleSyncIcuWorkouts = async () => {
    try {
      setIcuSyncing(true);
      setError(null);
      const response = await apiClient.post(
        '/icu/sync-workouts',
        { days_ahead: icuDaysAhead },
        { timeout: 120000 },
      );
      const { synced, total, plan_name, message } = response.data;
      setSuccess(
        message ||
          `Pushed ${synced ?? 0}/${total ?? 0} workouts to Intervals.icu` +
            (plan_name ? ` (${plan_name})` : '')
      );
      await fetchSettings();
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to sync workouts to Intervals.icu');
    } finally {
      setIcuSyncing(false);
    }
  };

  const handleSyncAll = async () => {
    try {
      setSyncing(true);
      setHealthSyncing(true);
      setError(null);
      
      // Sync activities first
      await handleSyncActivities();
      
      // Then sync health data
      await handleSyncHealthData();
      
      setSuccess('Successfully synced all data (activities + health data)!');
    } catch (err: any) {
      setError('Failed to sync all data');
    } finally {
      setSyncing(false);
      setHealthSyncing(false);
    }
  };

  const handleSyncActivities = async () => {
    let timerInterval: ReturnType<typeof setInterval> | undefined
    let pollInterval: ReturnType<typeof setInterval> | undefined

    try {
      setSyncing(true);
      setError(null);
      setSyncProgressOpen(true);
      setSyncElapsedTime(0);
      setSyncProgress(0);
      
      // Calculate date range
      const endDate = new Date();
      const startDate = new Date();
      startDate.setDate(startDate.getDate() - syncDays);
      setSyncStartDate(startDate.toLocaleDateString('en-US', { year: 'numeric', month: 'short', day: 'numeric' }));
      setSyncEndDate(endDate.toLocaleDateString('en-US', { year: 'numeric', month: 'short', day: 'numeric' }));
      
      // Get initial activity count
      let startingCount = 0
      try {
        const statsResponse = await apiClient.get('/garmin/activities/stats');
        startingCount = statsResponse.data.total_activities || 0;
        setInitialActivityCount(startingCount);
        setSyncActivityCount(startingCount);
      } catch (e) {
        setInitialActivityCount(0);
        setSyncActivityCount(0);
      }
      
      // Start elapsed time counter
      const startTime = Date.now();
      timerInterval = setInterval(() => {
        setSyncElapsedTime(Math.floor((Date.now() - startTime) / 1000));
      }, 1000);
      
      // Metadata-only sync is fast; details mode is intentionally not used for bulk ranges.
      const includeDetails = false
      const estimatedActivitiesPerDay = syncDays > 365 ? 1.5 : 2;
      const estimatedTotalActivities = Math.max(1, syncDays * estimatedActivitiesPerDay);
      
      // Start activity count polling (batch commits make this meaningful)
      pollInterval = setInterval(async () => {
        try {
          const statsResponse = await apiClient.get('/garmin/activities/stats');
          const currentCount = statsResponse.data.total_activities || 0;
          setSyncActivityCount(currentCount);
          
          const newActivities = currentCount - startingCount;
          if (newActivities > 0) {
            const progress = Math.min(95, (newActivities / estimatedTotalActivities) * 100);
            setSyncProgress(progress);
          } else {
            const timeProgress = Math.min(40, (Date.now() - startTime) / 3000);
            setSyncProgress(timeProgress);
          }
        } catch (e) {
          // Ignore polling errors
        }
      }, 3000);
      
      // Metadata sync: allow up to 5 min for large Garmin list fetches
      const timeoutMs = Math.min(300000, Math.max(90000, syncDays * 400));
      const response = await apiClient.post(
        '/garmin/sync-activities',
        { days: syncDays, include_details: includeDetails },
        { timeout: timeoutMs },
      );
      
      // Final activity count and 100% progress
      const finalStatsResponse = await apiClient.get('/garmin/activities/stats');
      setSyncActivityCount(finalStatsResponse.data.total_activities || 0);
      setSyncProgress(100);
      
      const { new_activities, updated_activities, activities_found, mode } = response.data;
      setSuccess(
        `Synced ${activities_found ?? syncDays} activities (${new_activities ?? 0} new, ${updated_activities ?? 0} updated, mode=${mode ?? 'metadata'})`
      );
      await fetchSettings();
      
      setTimeout(() => {
        setSyncProgressOpen(false);
      }, 2000);
    } catch (err: any) {
      setSyncProgressOpen(false);
      const isTimeout = err?.code === 'ECONNABORTED' || /timeout/i.test(err?.message || '');
      if (isTimeout) {
        setError(
          'Request timed out — the server may still be syncing. Wait a minute, refresh, or check the backend console.'
        );
      } else {
        setError(err.response?.data?.detail || 'Failed to sync activities');
      }
    } finally {
      if (timerInterval) clearInterval(timerInterval);
      if (pollInterval) clearInterval(pollInterval);
      setSyncing(false);
    }
  };

  const handleSyncHealthData = async () => {
    try {
      setHealthSyncing(true);
      setError(null);
      
      // Calculate timeout based on sync days
      // ~100ms per day, minimum 60 seconds, maximum 5 minutes
      const timeoutMs = Math.min(300000, Math.max(60000, syncDays * 100));
      
      const response = await apiClient.post('/garmin/sync-health-data', { days: syncDays }, {
        timeout: timeoutMs,
      });
      
      const { hrv_new, hrv_updated, total_records } = response.data;
      setSuccess(`Successfully synced health data: ${hrv_new} new HRV records, ${hrv_updated} updated!`);
      await fetchSettings();
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to sync health data');
    } finally {
      setHealthSyncing(false);
    }
  };

  if (loading) {
    return (
      <Container maxWidth="lg" sx={{ mt: 4, display: 'flex', justifyContent: 'center' }}>
        <CircularProgress />
      </Container>
    );
  }

  return (
    <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
      <Breadcrumbs
        items={[
          { label: 'Home', path: '/dashboard' },
          { label: 'Settings', icon: <SettingsIcon fontSize="small" /> },
        ]}
      />
      
      <Typography variant="h4" gutterBottom>
        Settings
      </Typography>

      {error && (
        <Alert severity="error" sx={{ mb: 2 }} onClose={() => setError(null)}>
          {error}
        </Alert>
      )}

      {success && (
        <Alert severity="success" sx={{ mb: 2 }} onClose={() => setSuccess(null)}>
          {success}
        </Alert>
      )}

      <Paper sx={{ mb: 3 }}>
        <Tabs value={tabValue} onChange={(_, newValue) => setTabValue(newValue)} sx={{ borderBottom: 1, borderColor: 'divider' }}>
          <Tab icon={<HeartIcon />} label="Training Zones" iconPosition="start" />
          <Tab icon={<LinkIcon />} label="Integrations" iconPosition="start" />
          <Tab icon={<ExperimentIcon />} label="Beta Features" iconPosition="start" />
        </Tabs>

        {/* Training Zones Tab */}
        <TabPanel value={tabValue} index={0}>
          <Container maxWidth="md">
            <Typography variant="h6" gutterBottom>
              Configure Your Training Thresholds
            </Typography>
            <Typography variant="body2" color="text.secondary" paragraph>
              Set your threshold values for accurate TSS calculations and zone-based training. These values are used to calculate training intensity and stress scores.
            </Typography>
            <Alert severity="info" sx={{ mb: 3 }} icon={<InfoIcon />}>
              <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                <Typography variant="body2">
                  Need help determining your thresholds?
                </Typography>
                <Button
                  size="small"
                  href="https://help.trainingpeaks.com/hc/en-us/articles/204071934-How-to-Calculate-Threshold-Values-for-Power-Heart-Rate-or-Pace"
                  target="_blank"
                  rel="noopener noreferrer"
                >
                  View Guide
                </Button>
              </Box>
            </Alert>

            {/* General Heart Rate Settings */}
            <Card sx={{ mb: 3 }}>
              <CardContent>
                <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                  <HeartIcon sx={{ mr: 1, color: 'error.main' }} />
                  <Typography variant="h6">Heart Rate Settings</Typography>
                </Box>
                <Grid container spacing={2}>
                  <Grid item xs={12} sm={6}>
                    <TextField
                      fullWidth
                      label="Maximum Heart Rate"
                      type="number"
                      value={thresholds.max_hr || ''}
                      onChange={(e) => setThresholds({ ...thresholds, max_hr: parseIntInput(e.target.value) })}
                      InputProps={{
                        endAdornment: <InputAdornment position="end">bpm</InputAdornment>,
                      }}
                      helperText="Your maximum heart rate (220 - age as estimate)"
                    />
                  </Grid>
                  <Grid item xs={12} sm={6}>
                    <TextField
                      fullWidth
                      label="Resting Heart Rate"
                      type="number"
                      value={thresholds.resting_hr || ''}
                      onChange={(e) => setThresholds({ ...thresholds, resting_hr: parseIntInput(e.target.value) })}
                      InputProps={{
                        endAdornment: <InputAdornment position="end">bpm</InputAdornment>,
                      }}
                      helperText="Your resting heart rate (measure in the morning)"
                    />
                  </Grid>
                </Grid>
              </CardContent>
            </Card>

            {/* Cycling Settings */}
            <Card sx={{ mb: 3 }}>
              <CardContent>
                <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                  <BikeIcon sx={{ mr: 1, color: 'primary.main' }} />
                  <Typography variant="h6">Cycling Thresholds</Typography>
                </Box>
                <Grid container spacing={2}>
                  <Grid item xs={12} sm={6}>
                    <TextField
                      fullWidth
                      label="Functional Threshold Power (FTP)"
                      type="number"
                      value={thresholds.ftp || ''}
                      onChange={(e) => setThresholds({ ...thresholds, ftp: parseIntInput(e.target.value) })}
                      InputProps={{
                        endAdornment: <InputAdornment position="end">watts</InputAdornment>,
                      }}
                      helperText="Your 20-minute power test × 0.95"
                    />
                  </Grid>
                  <Grid item xs={12} sm={6}>
                    <FormControl fullWidth size="small">
                      <InputLabel>Power Zone Calculation Method</InputLabel>
                      <Select
                        value={powerMethod}
                        label="Power Zone Calculation Method"
                        onChange={(e) => setPowerMethod(e.target.value)}
                      >
                        <MenuItem value="coggan">Andy Coggan (6 zones) - Racing and Training with Power Meter</MenuItem>
                        <MenuItem value="durata">Durata Training</MenuItem>
                        <MenuItem value="cts">CTS (Carmichael Training Systems)</MenuItem>
                        <MenuItem value="usat">USAT for Cycling (6 zones)</MenuItem>
                        <MenuItem value="8020">80/20 Running and Cycling (7 zones)</MenuItem>
                      </Select>
                    </FormControl>
                  </Grid>
                  <Grid item xs={12}>
                    <Box sx={{ display: 'flex', flexDirection: { xs: 'column', sm: 'row' }, gap: 1, alignItems: { xs: 'stretch', sm: 'center' } }}>
                      <Button
                        variant="contained"
                        startIcon={calculatingPowerZones ? <CircularProgress size={16} color="inherit" /> : <CalculateIcon />}
                        onClick={() => calculateCyclingPowerZones(thresholds.ftp, powerMethod, true)}
                        disabled={!thresholds.ftp || calculatingPowerZones}
                        fullWidth
                        sx={{ maxWidth: { sm: 'auto' } }}
                      >
                        Recalculate Zones
                      </Button>
                      <Typography variant="caption" color="text.secondary" sx={{ alignSelf: { xs: 'flex-start', sm: 'center' } }}>
                        Calculate zones using your current FTP value
                      </Typography>
                    </Box>
                    {renderZoneDisplay(
                      cyclingPowerZones,
                      previewCyclingPowerZones,
                      (zone) => `${zone.min}-${zone.max === 9999 || zone.max === 2000 ? '∞' : zone.max}W`,
                      applyPowerZones,
                      'Power Zones'
                    )}
                  </Grid>
                </Grid>
              </CardContent>
            </Card>

            {/* Running Settings */}
            <Card sx={{ mb: 3 }}>
              <CardContent>
                <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                  <RunIcon sx={{ mr: 1, color: 'success.main' }} />
                  <Typography variant="h6">Running Thresholds</Typography>
                </Box>
                <Grid container spacing={2}>
                  <Grid item xs={12} sm={6}>
                    <TextField
                      fullWidth
                      label="Threshold Pace"
                      type="text"
                      value={runPaceText}
                      onChange={(e) => {
                        const newValue = e.target.value;
                        setRunPaceText(newValue); // Allow any text input
                        const seconds = paceToSeconds(newValue);
                        if (seconds !== null) {
                          setThresholds({ ...thresholds, threshold_pace: seconds });
                        }
                      }}
                      onBlur={() => {
                        // On blur, format the value properly
                        setRunPaceText(secondsToPace(thresholds.threshold_pace));
                      }}
                      placeholder="4:30"
                      InputProps={{
                        endAdornment: <InputAdornment position="end">min/km</InputAdornment>,
                      }}
                      helperText="Your threshold pace (e.g., 4:30 for 4min 30sec/km)"
                    />
                  </Grid>
                  <Grid item xs={12} sm={6}>
                    <TextField
                      fullWidth
                      label="Lactate Threshold Heart Rate"
                      type="number"
                      value={thresholds.running_threshold_hr || ''}
                      onChange={(e) => setThresholds({ ...thresholds, running_threshold_hr: parseIntInput(e.target.value) })}
                      InputProps={{
                        endAdornment: <InputAdornment position="end">bpm</InputAdornment>,
                      }}
                      helperText="Your threshold heart rate for running"
                    />
                  </Grid>
                  <Grid item xs={12}>
                    <FormControl fullWidth size="small">
                      <InputLabel>Pace Zone Calculation Method</InputLabel>
                      <Select
                        value={runPaceMethod}
                        label="Pace Zone Calculation Method"
                        onChange={(e) => setRunPaceMethod(e.target.value)}
                      >
                        <MenuItem value="friel">Joe Friel for Running (7 zones)</MenuItem>
                        <MenuItem value="8020">80/20 Running (7 zones)</MenuItem>
                        <MenuItem value="cts">CTS - Carmichael Training Systems (7 zones)</MenuItem>
                      </Select>
                    </FormControl>
                  </Grid>
                  <Grid item xs={12}>
                    <Box sx={{ display: 'flex', flexDirection: { xs: 'column', sm: 'row' }, gap: 1, alignItems: { xs: 'stretch', sm: 'center' } }}>
                      <Button
                        variant="contained"
                        startIcon={calculatingRunPaceZones ? <CircularProgress size={16} color="inherit" /> : <CalculateIcon />}
                        onClick={() => calculateRunningPaceZones(thresholds.threshold_pace, runPaceMethod, true)}
                        disabled={!thresholds.threshold_pace || calculatingRunPaceZones}
                        fullWidth
                        sx={{ maxWidth: { sm: 'auto' } }}
                      >
                        Recalculate Pace Zones
                      </Button>
                      <Typography variant="caption" color="text.secondary" sx={{ alignSelf: { xs: 'flex-start', sm: 'center' } }}>
                        Calculate zones using your current threshold pace
                      </Typography>
                    </Box>
                    {renderZoneDisplay(
                      runningPaceZones,
                      previewRunningPaceZones,
                      (zone) => {
                        const maxDisplay = zone.max_display === '0:00' ? '∞' : zone.max_display;
                        const minDisplay = zone.min_display === '166:39' || zone.min_display === '9999:00' ? '∞' : zone.min_display;
                        return `${maxDisplay} - ${minDisplay} /km`;
                      },
                      applyRunPaceZones,
                      'Pace Zones'
                    )}
                  </Grid>
                  <Grid item xs={12}>
                    <FormControl fullWidth size="small">
                      <InputLabel>Heart Rate Zone Method (Running)</InputLabel>
                      <Select
                        value={runningHRMethod}
                        label="Heart Rate Zone Method (Running)"
                        onChange={(e) => setRunningHRMethod(e.target.value)}
                      >
                        <MenuItem value="friel">Joe Friel for Running (7 zones)</MenuItem>
                        <MenuItem value="coggan">Andy Coggan (5 zones)</MenuItem>
                      </Select>
                    </FormControl>
                  </Grid>
                  <Grid item xs={12}>
                    <Box sx={{ display: 'flex', flexDirection: { xs: 'column', sm: 'row' }, gap: 1, alignItems: { xs: 'stretch', sm: 'center' } }}>
                      <Button
                        variant="contained"
                        startIcon={calculatingRunHRZones ? <CircularProgress size={16} color="inherit" /> : <CalculateIcon />}
                        onClick={() => calculateRunningHRZones(thresholds.running_threshold_hr, thresholds.max_hr, runningHRMethod, true)}
                        disabled={!thresholds.running_threshold_hr || !thresholds.max_hr || calculatingRunHRZones}
                        fullWidth
                        sx={{ maxWidth: { sm: 'auto' } }}
                      >
                        Recalculate HR Zones
                      </Button>
                      <Typography variant="caption" color="text.secondary" sx={{ alignSelf: { xs: 'flex-start', sm: 'center' } }}>
                        Calculate zones using your current threshold and max HR
                      </Typography>
                    </Box>
                    {renderZoneDisplay(
                      runningHRZones,
                      previewRunningHRZones,
                      (zone) => `${zone.min}-${zone.max} bpm`,
                      applyRunHRZones,
                      'Heart Rate Zones'
                    )}
                  </Grid>
                </Grid>
              </CardContent>
            </Card>

            {/* Swimming Settings */}
            <Card sx={{ mb: 3 }}>
              <CardContent>
                <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                  <SwimIcon sx={{ mr: 1, color: 'info.main' }} />
                  <Typography variant="h6">Swimming Thresholds</Typography>
                </Box>
                <Grid container spacing={2}>
                  <Grid item xs={12} sm={6}>
                    <TextField
                      fullWidth
                      label="Threshold Pace"
                      type="text"
                      value={swimPaceText}
                      onChange={(e) => {
                        const newValue = e.target.value;
                        setSwimPaceText(newValue); // Allow any text input
                        const seconds = paceToSeconds(newValue);
                        if (seconds !== null) {
                          setThresholds({ ...thresholds, swim_threshold_pace: seconds });
                        }
                      }}
                      onBlur={() => {
                        // On blur, format the value properly
                        setSwimPaceText(secondsToPace(thresholds.swim_threshold_pace));
                      }}
                      placeholder="1:30"
                      InputProps={{
                        endAdornment: <InputAdornment position="end">min/100m</InputAdornment>,
                      }}
                      helperText="Your threshold pace per 100m (e.g., 1:30)"
                    />
                  </Grid>
                  <Grid item xs={12} sm={6}>
                    <TextField
                      fullWidth
                      label="Lactate Threshold Heart Rate"
                      type="number"
                      value={thresholds.swim_threshold_hr || ''}
                      onChange={(e) => setThresholds({ ...thresholds, swim_threshold_hr: parseIntInput(e.target.value) })}
                      InputProps={{
                        endAdornment: <InputAdornment position="end">bpm</InputAdornment>,
                      }}
                      helperText="Your threshold heart rate for swimming"
                    />
                  </Grid>
                  <Grid item xs={12}>
                    <FormControl fullWidth size="small">
                      <InputLabel>Pace Zone Calculation Method</InputLabel>
                      <Select
                        value={swimPaceMethod}
                        label="Pace Zone Calculation Method"
                        onChange={(e) => setSwimPaceMethod(e.target.value)}
                      >
                        <MenuItem value="friel">Joe Friel for Swimming (7 zones)</MenuItem>
                      </Select>
                    </FormControl>
                  </Grid>
                  <Grid item xs={12}>
                    <Box sx={{ display: 'flex', flexDirection: { xs: 'column', sm: 'row' }, gap: 1, alignItems: { xs: 'stretch', sm: 'center' } }}>
                      <Button
                        variant="contained"
                        startIcon={calculatingSwimPaceZones ? <CircularProgress size={16} color="inherit" /> : <CalculateIcon />}
                        onClick={() => calculateSwimPaceZones(thresholds.swim_threshold_pace, swimPaceMethod, true)}
                        disabled={!thresholds.swim_threshold_pace || calculatingSwimPaceZones}
                        fullWidth
                        sx={{ maxWidth: { sm: 'auto' } }}
                      >
                        Recalculate Pace Zones
                      </Button>
                      <Typography variant="caption" color="text.secondary" sx={{ alignSelf: { xs: 'flex-start', sm: 'center' } }}>
                        Calculate zones using your current threshold pace
                      </Typography>
                    </Box>
                    {renderZoneDisplay(
                      swimPaceZones,
                      previewSwimPaceZones,
                      (zone) => {
                        const maxDisplay = zone.max_display === '0:00' ? '∞' : zone.max_display;
                        const minDisplay = zone.min_display === '166:39' || zone.min_display === '9999:00' ? '∞' : zone.min_display;
                        return `${maxDisplay} - ${minDisplay} /100m`;
                      },
                      applySwimPaceZones,
                      'Pace Zones'
                    )}
                  </Grid>
                </Grid>
              </CardContent>
            </Card>

            <Box sx={{ display: 'flex', justifyContent: 'flex-end', gap: 2 }}>
              <Button
                variant="contained"
                startIcon={saving ? <CircularProgress size={20} /> : <SaveIcon />}
                onClick={handleSaveThresholds}
                disabled={saving}
              >
                Save Training Zones
              </Button>
            </Box>
          </Container>
        </TabPanel>

        {/* Integrations Tab */}
        <TabPanel value={tabValue} index={1}>
          <Container maxWidth="md">
            {/* Garmin Connect Integration */}
            <Card>
              <CardContent>
                <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 2 }}>
                  <Box sx={{ display: 'flex', alignItems: 'center' }}>
                    <img
                      src="/garmin-logo.png"
                      alt="Garmin"
                      style={{ width: 40, height: 40, marginRight: 16 }}
                      onError={(e) => {
                        (e.target as HTMLImageElement).style.display = 'none';
                      }}
                    />
                    <Box>
                      <Typography variant="h6">Garmin Connect</Typography>
                      <Typography variant="body2" color="text.secondary">
                        Sync activities from your Garmin device
                      </Typography>
                    </Box>
                  </Box>
                  {garminStatus?.connected ? (
                    <Chip
                      icon={<CheckCircleIcon />}
                      label="Connected"
                      color="success"
                      size="small"
                    />
                  ) : (
                    <Chip label="Not Connected" size="small" />
                  )}
                </Box>

                {garminStatus?.connected && (
                  <>
                    <Divider sx={{ my: 2 }} />
                    <Box sx={{ mb: 2 }}>
                      <Typography variant="body2" color="text.secondary">
                        <strong>Email:</strong> {garminStatus.email}
                      </Typography>
                      {garminStatus.last_sync && (
                        <Typography variant="body2" color="text.secondary">
                          <strong>Last Sync:</strong> {new Date(garminStatus.last_sync).toLocaleString()}
                        </Typography>
                      )}
                    </Box>

                    <Divider sx={{ my: 2 }} />
                    
                    <Box sx={{ mb: 2 }}>
                      <Typography variant="body2" gutterBottom>
                        Sync Period
                      </Typography>
                      <FormControl fullWidth size="small">
                        <Select
                          value={syncDays}
                          onChange={(e) => setSyncDays(e.target.value as number)}
                        >
                          <MenuItem value={7}>Last 7 days</MenuItem>
                          <MenuItem value={14}>Last 14 days</MenuItem>
                          <MenuItem value={30}>Last 30 days</MenuItem>
                          <MenuItem value={60}>Last 60 days</MenuItem>
                          <MenuItem value={90}>Last 90 days</MenuItem>
                          <MenuItem value={180}>Last 6 months</MenuItem>
                          <MenuItem value={365}>Last year</MenuItem>
                          <MenuItem value={730}>Last 2 years</MenuItem>
                        </Select>
                      </FormControl>
                      {syncDays >= 365 && (
                        <Alert severity="info" sx={{ mt: 1 }}>
                          Large sync ({syncDays} days) may take 2-5 minutes. Please be patient!
                        </Alert>
                      )}
                    </Box>
                  </>
                )}
              </CardContent>

              <CardActions sx={{ flexDirection: 'column', alignItems: 'stretch', gap: 1.5, px: 2, pb: 2 }}>
                {garminStatus?.connected ? (
                  isMobile ? (
                    /* Mobile: Sync All + Menu */
                    <>
                      <Box sx={{ display: 'flex', gap: 1 }}>
                        <Button
                          variant="contained"
                          startIcon={syncing || healthSyncing ? <CircularProgress size={20} /> : <SyncIcon />}
                          onClick={handleSyncAll}
                          disabled={syncing || healthSyncing}
                          fullWidth
                          sx={{ minHeight: 44 }}
                        >
                          Sync All
                        </Button>
                        <IconButton
                          onClick={(e) => setMenuAnchor(e.currentTarget)}
                          disabled={syncing || healthSyncing}
                          sx={{ 
                            border: 1,
                            borderColor: 'divider',
                            borderRadius: 1,
                            minWidth: 44,
                            minHeight: 44
                          }}
                        >
                          <MoreVertIcon />
                        </IconButton>
                      </Box>
                      <Menu
                        anchorEl={menuAnchor}
                        open={Boolean(menuAnchor)}
                        onClose={() => setMenuAnchor(null)}
                        anchorOrigin={{ vertical: 'bottom', horizontal: 'right' }}
                        transformOrigin={{ vertical: 'top', horizontal: 'right' }}
                      >
                        <MenuItem 
                          onClick={() => {
                            setMenuAnchor(null);
                            handleSyncActivities();
                          }}
                          disabled={syncing || healthSyncing}
                        >
                          <ListItemIcon>
                            <SyncIcon fontSize="small" />
                          </ListItemIcon>
                          <ListItemText>Sync Activities</ListItemText>
                        </MenuItem>
                        <MenuItem 
                          onClick={() => {
                            setMenuAnchor(null);
                            handleSyncHealthData();
                          }}
                          disabled={syncing || healthSyncing}
                        >
                          <ListItemIcon>
                            <HeartIcon fontSize="small" />
                          </ListItemIcon>
                          <ListItemText>Sync Health Data</ListItemText>
                        </MenuItem>
                        <Divider />
                        <MenuItem 
                          onClick={() => {
                            setMenuAnchor(null);
                            handleDisconnectGarmin();
                          }}
                          sx={{ color: 'error.main' }}
                        >
                          <ListItemIcon>
                            <LinkOffIcon fontSize="small" color="error" />
                          </ListItemIcon>
                          <ListItemText>Disconnect</ListItemText>
                        </MenuItem>
                      </Menu>
                    </>
                  ) : (
                    /* Desktop: All buttons visible */
                    <>
                      <Button
                        variant="contained"
                        startIcon={syncing ? <CircularProgress size={20} /> : <SyncIcon />}
                        onClick={handleSyncActivities}
                        disabled={syncing || healthSyncing}
                      >
                        Sync Activities
                      </Button>
                      <Button
                        variant="outlined"
                        startIcon={healthSyncing ? <CircularProgress size={20} /> : <HeartIcon />}
                        onClick={handleSyncHealthData}
                        disabled={syncing || healthSyncing}
                      >
                        {healthSyncing ? 'Syncing...' : 'Sync Health Data'}
                      </Button>
                      <Button
                        variant="outlined"
                        startIcon={<LinkOffIcon />}
                        onClick={handleDisconnectGarmin}
                        disabled={connecting || syncing || healthSyncing}
                      >
                        Disconnect
                      </Button>
                    </>
                  )
                ) : (
                  <Button
                    variant="contained"
                    startIcon={<LinkIcon />}
                    onClick={() => setConnectDialogOpen(true)}
                    fullWidth
                    sx={{ minHeight: 44 }}
                  >
                    Connect Garmin
                  </Button>
                )}
              </CardActions>
            </Card>

            {/* Bike workout library */}
            <Card sx={{ mt: 3 }}>
              <CardContent>
                <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                  <LibraryIcon sx={{ fontSize: 40, mr: 2, color: 'primary.main' }} />
                  <Box sx={{ flex: 1 }}>
                    <Typography variant="h6">Workout library</Typography>
                    <Typography variant="body2" color="text.secondary">
                      Choose structured bike workouts available in Calendar → Bike library (ERG)
                    </Typography>
                  </Box>
                  <Chip
                    size="small"
                    label={`${libraryEnabledIds.size} / ${libraryTemplates.length} selected`}
                    color={libraryEnabledIds.size > 0 ? 'primary' : 'default'}
                  />
                </Box>
                {libraryUsingDefaults && (
                  <Alert severity="info" sx={{ mb: 2 }}>
                    Showing starter defaults until you save a custom selection.
                  </Alert>
                )}
                <Stack direction="row" spacing={1} sx={{ mb: 2 }} flexWrap="wrap" useFlexGap>
                  <Button size="small" onClick={selectAllLibrary} disabled={libraryLoading}>
                    Select all
                  </Button>
                  <Button size="small" onClick={clearLibrary} disabled={libraryLoading}>
                    Clear
                  </Button>
                </Stack>
                {libraryLoading ? (
                  <Box sx={{ display: 'flex', justifyContent: 'center', py: 3 }}>
                    <CircularProgress size={28} />
                  </Box>
                ) : (
                  (() => {
                    const byCat: Record<string, WorkoutTemplateSummary[]> = {};
                    libraryTemplates.forEach((t) => {
                      const c = t.category || 'other';
                      (byCat[c] ||= []).push(t);
                    });
                    const catOrder = [
                      'test',
                      'recovery',
                      'endurance',
                      'tempo',
                      'sweet_spot',
                      'threshold',
                      'vo2max',
                      'race_pace',
                      'other',
                    ];
                    const cats = [
                      ...catOrder.filter((c) => byCat[c]?.length),
                      ...Object.keys(byCat).filter((c) => !catOrder.includes(c)),
                    ];
                    return cats.map((cat) => (
                      <Accordion key={cat} disableGutters elevation={0} sx={{ border: 1, borderColor: 'divider', mb: 1, '&:before': { display: 'none' } }}>
                        <AccordionSummary expandIcon={<ExpandMoreIcon />}>
                          <Typography sx={{ textTransform: 'capitalize', fontWeight: 600 }}>
                            {cat.replace(/_/g, ' ')} ({byCat[cat].length})
                          </Typography>
                        </AccordionSummary>
                        <AccordionDetails sx={{ pt: 0 }}>
                          {byCat[cat].map((t) => (
                            <FormControlLabel
                              key={t.id}
                              control={
                                <Checkbox
                                  checked={libraryEnabledIds.has(t.id)}
                                  onChange={() => toggleLibraryTemplate(t.id)}
                                  size="small"
                                />
                              }
                              label={
                                <Box>
                                  <Typography variant="body2">{t.name}</Typography>
                                  <Typography variant="caption" color="text.secondary">
                                    {t.durationMinutes} min · TSS {t.targetTSS ?? '—'} · {t.stepCount} steps
                                  </Typography>
                                </Box>
                              }
                              sx={{ alignItems: 'flex-start', display: 'flex', mb: 0.5, width: '100%' }}
                            />
                          ))}
                        </AccordionDetails>
                      </Accordion>
                    ));
                  })()
                )}
              </CardContent>
              <CardActions sx={{ px: 2, pb: 2 }}>
                <Button
                  variant="contained"
                  startIcon={librarySaving ? <CircularProgress size={18} /> : <SaveIcon />}
                  onClick={handleSaveLibraryPreferences}
                  disabled={librarySaving || libraryLoading}
                  fullWidth
                  sx={{ minHeight: 44 }}
                >
                  {librarySaving ? 'Saving…' : 'Save library selection'}
                </Button>
              </CardActions>
            </Card>

            {/* Intervals.icu Integration */}
            <Card sx={{ mt: 3 }}>
              <CardContent>
                <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 2 }}>
                  <Box sx={{ display: 'flex', alignItems: 'center' }}>
                    <FitnessCenterIcon sx={{ fontSize: 40, mr: 2, color: 'primary.main' }} />
                    <Box>
                      <Typography variant="h6">Intervals.icu</Typography>
                      <Typography variant="body2" color="text.secondary">
                        Push planned workouts to ICU (then to Garmin via ICU)
                      </Typography>
                    </Box>
                  </Box>
                  {icuStatus?.connected ? (
                    <Chip
                      icon={<CheckCircleIcon />}
                      label="Connected"
                      color="success"
                      size="small"
                    />
                  ) : (
                    <Chip label="Not Connected" size="small" />
                  )}
                </Box>

                {icuStatus?.connected && (
                  <>
                    <Divider sx={{ my: 2 }} />
                    <Box sx={{ mb: 2 }}>
                      {icuStatus.athlete_id && (
                        <Typography variant="body2" color="text.secondary">
                          <strong>Athlete ID:</strong> {icuStatus.athlete_id}
                        </Typography>
                      )}
                      {icuStatus.last_sync && (
                        <Typography variant="body2" color="text.secondary">
                          <strong>Last Sync:</strong> {new Date(icuStatus.last_sync).toLocaleString()}
                        </Typography>
                      )}
                    </Box>
                    <Box sx={{ mb: 2 }}>
                      <Typography variant="body2" gutterBottom>
                        Push upcoming workouts
                      </Typography>
                      <FormControl fullWidth size="small">
                        <Select
                          value={icuDaysAhead}
                          onChange={(e) => setIcuDaysAhead(e.target.value as number)}
                        >
                          <MenuItem value={7}>Next 7 days</MenuItem>
                          <MenuItem value={14}>Next 14 days</MenuItem>
                          <MenuItem value={30}>Next 30 days</MenuItem>
                        </Select>
                      </FormControl>
                      <Alert severity="info" sx={{ mt: 1 }}>
                        Syncs from your <strong>active</strong> training plan only. Enable Garmin
                        sync inside Intervals.icu to deliver workouts to your watch.
                      </Alert>
                    </Box>
                  </>
                )}
              </CardContent>
              <CardActions sx={{ flexDirection: 'column', alignItems: 'stretch', gap: 1.5, px: 2, pb: 2 }}>
                {icuStatus?.connected ? (
                  <>
                    <Button
                      variant="contained"
                      startIcon={icuSyncing ? <CircularProgress size={20} /> : <SyncIcon />}
                      onClick={handleSyncIcuWorkouts}
                      disabled={icuSyncing || icuConnecting}
                      fullWidth
                      sx={{ minHeight: 44 }}
                    >
                      {icuSyncing ? 'Syncing…' : 'Sync workouts to Intervals.icu'}
                    </Button>
                    <Button
                      variant="outlined"
                      startIcon={<LinkOffIcon />}
                      onClick={handleDisconnectIcu}
                      disabled={icuConnecting || icuSyncing}
                      fullWidth
                      sx={{ minHeight: 44 }}
                    >
                      Disconnect
                    </Button>
                  </>
                ) : (
                  <Button
                    variant="contained"
                    startIcon={<LinkIcon />}
                    onClick={() => setIcuConnectDialogOpen(true)}
                    fullWidth
                    sx={{ minHeight: 44 }}
                  >
                    Connect Intervals.icu
                  </Button>
                )}
              </CardActions>
            </Card>
          </Container>
        </TabPanel>
        
        {/* Beta Features Tab */}
        <TabPanel value={tabValue} index={2}>
          <Container maxWidth="md">
            <FeatureFlagsPanel />
          </Container>
        </TabPanel>
      </Paper>

      {/* Connect Garmin Dialog */}
      <Dialog open={connectDialogOpen} onClose={() => setConnectDialogOpen(false)} maxWidth="sm" fullWidth>
        <DialogTitle>Connect Garmin Account</DialogTitle>
        <DialogContent>
          <Typography variant="body2" color="text.secondary" paragraph>
            Enter your Garmin Connect credentials to sync your activities.
          </Typography>
          <TextField
            autoFocus
            margin="dense"
            label="Garmin Email"
            type="email"
            fullWidth
            value={garminEmail}
            onChange={(e) => setGarminEmail(e.target.value)}
            sx={{ mb: 2 }}
          />
          <TextField
            margin="dense"
            label="Garmin Password"
            type="password"
            fullWidth
            value={garminPassword}
            onChange={(e) => setGarminPassword(e.target.value)}
          />
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setConnectDialogOpen(false)}>Cancel</Button>
          <Button
            onClick={handleConnectGarmin}
            variant="contained"
            disabled={connecting || !garminEmail || !garminPassword}
          >
            {connecting ? <CircularProgress size={24} /> : 'Connect'}
          </Button>
        </DialogActions>
      </Dialog>

      {/* Connect Intervals.icu Dialog */}
      <Dialog
        open={icuConnectDialogOpen}
        onClose={() => setIcuConnectDialogOpen(false)}
        maxWidth="sm"
        fullWidth
      >
        <DialogTitle>Connect Intervals.icu</DialogTitle>
        <DialogContent>
          <Typography variant="body2" color="text.secondary" paragraph>
            Paste your API key from Intervals.icu → Settings → Developer Settings.
            Kinesis will push planned workouts to your ICU calendar (one-way).
          </Typography>
          <TextField
            autoFocus
            margin="dense"
            label="API Key"
            type="password"
            fullWidth
            value={icuApiKey}
            onChange={(e) => setIcuApiKey(e.target.value)}
            placeholder="Your Intervals.icu API key"
          />
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setIcuConnectDialogOpen(false)} disabled={icuConnecting}>
            Cancel
          </Button>
          <Button
            onClick={handleConnectIcu}
            variant="contained"
            disabled={icuConnecting || !icuApiKey.trim()}
          >
            {icuConnecting ? <CircularProgress size={24} /> : 'Connect'}
          </Button>
        </DialogActions>
      </Dialog>
      
      {/* Sync Progress Dialog */}
      <Dialog open={syncProgressOpen} maxWidth="sm" fullWidth>
        <DialogTitle>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            <SyncIcon sx={{ animation: 'spin 2s linear infinite', '@keyframes spin': { '0%': { transform: 'rotate(0deg)' }, '100%': { transform: 'rotate(360deg)' } } }} />
            Syncing Activities
          </Box>
        </DialogTitle>
        <DialogContent>
          <Box sx={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 3, py: 2 }}>
            <CircularProgress size={60} variant={syncProgress > 0 ? "determinate" : "indeterminate"} value={syncProgress} />
            
            <Box sx={{ textAlign: 'center', width: '100%' }}>
              <Typography variant="h6" gutterBottom>
                Fetching activities from Garmin Connect...
              </Typography>
              
              <Typography variant="body2" color="primary.main" gutterBottom sx={{ fontWeight: 500 }}>
                {syncStartDate} → {syncEndDate}
              </Typography>
              
              <Typography variant="body2" color="text.secondary" gutterBottom>
                This may take a minute or two for large date ranges
              </Typography>
              
              <Divider sx={{ my: 2 }} />
              
              <Box sx={{ display: 'flex', justifyContent: 'space-around', mt: 2 }}>
                <Box>
                  <Typography variant="caption" color="text.secondary">
                    Elapsed Time
                  </Typography>
                  <Typography variant="h6">
                    {Math.floor(syncElapsedTime / 60)}:{String(syncElapsedTime % 60).padStart(2, '0')}
                  </Typography>
                </Box>
                
                <Box>
                  <Typography variant="caption" color="text.secondary">
                    New Activities
                  </Typography>
                  <Typography variant="h6" color="primary.main">
                    {syncActivityCount > initialActivityCount 
                      ? `+${syncActivityCount - initialActivityCount}` 
                      : '0'}
                  </Typography>
                </Box>
                
                <Box>
                  <Typography variant="caption" color="text.secondary">
                    Progress
                  </Typography>
                  <Typography variant="h6" color="success.main">
                    {Math.round(syncProgress)}%
                  </Typography>
                </Box>
              </Box>
            </Box>
          </Box>
        </DialogContent>
      </Dialog>
    </Container>
  );
};

export default SettingsNew;
