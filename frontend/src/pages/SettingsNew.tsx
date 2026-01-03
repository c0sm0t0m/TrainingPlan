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
} from '@mui/icons-material';
import apiClient from '../services/api';

interface GarminStatus {
  connected: boolean;
  email: string | null;
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
  const [tabValue, setTabValue] = useState(0);
  const [garminStatus, setGarminStatus] = useState<GarminStatus | null>(null);
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
  const [syncing, setSyncing] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);
  
  // Connect dialog state
  const [connectDialogOpen, setConnectDialogOpen] = useState(false);
  const [garminEmail, setGarminEmail] = useState('');
  const [garminPassword, setGarminPassword] = useState('');

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
    document.title = 'Settings - TrainingPlan';
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
      
      // Fetch Garmin status
      const garminResponse = await apiClient.get('/garmin/status');
      setGarminStatus(garminResponse.data);
      
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
    } catch (err: any) {
      setError('Failed to load settings');
    } finally {
      setLoading(false);
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

  const handleSyncActivities = async () => {
    try {
      setSyncing(true);
      setError(null);
      
      await apiClient.post('/garmin/sync-activities', { days: syncDays });
      
      setSuccess(`Successfully synced activities from last ${syncDays} days!`);
      await fetchSettings();
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to sync activities');
    } finally {
      setSyncing(false);
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
                    <Box sx={{ display: 'flex', gap: 1, alignItems: 'center' }}>
                      <Button
                        variant="contained"
                        startIcon={calculatingPowerZones ? <CircularProgress size={16} color="inherit" /> : <CalculateIcon />}
                        onClick={() => calculateCyclingPowerZones(thresholds.ftp, powerMethod, true)}
                        disabled={!thresholds.ftp || calculatingPowerZones}
                      >
                        Recalculate Zones
                      </Button>
                      <Typography variant="caption" color="text.secondary">
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
                    <Box sx={{ display: 'flex', gap: 1, alignItems: 'center' }}>
                      <Button
                        variant="contained"
                        startIcon={calculatingRunPaceZones ? <CircularProgress size={16} color="inherit" /> : <CalculateIcon />}
                        onClick={() => calculateRunningPaceZones(thresholds.threshold_pace, runPaceMethod, true)}
                        disabled={!thresholds.threshold_pace || calculatingRunPaceZones}
                      >
                        Recalculate Pace Zones
                      </Button>
                      <Typography variant="caption" color="text.secondary">
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
                    <Box sx={{ display: 'flex', gap: 1, alignItems: 'center' }}>
                      <Button
                        variant="contained"
                        startIcon={calculatingRunHRZones ? <CircularProgress size={16} color="inherit" /> : <CalculateIcon />}
                        onClick={() => calculateRunningHRZones(thresholds.running_threshold_hr, thresholds.max_hr, runningHRMethod, true)}
                        disabled={!thresholds.running_threshold_hr || !thresholds.max_hr || calculatingRunHRZones}
                      >
                        Recalculate HR Zones
                      </Button>
                      <Typography variant="caption" color="text.secondary">
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
                    <Box sx={{ display: 'flex', gap: 1, alignItems: 'center' }}>
                      <Button
                        variant="contained"
                        startIcon={calculatingSwimPaceZones ? <CircularProgress size={16} color="inherit" /> : <CalculateIcon />}
                        onClick={() => calculateSwimPaceZones(thresholds.swim_threshold_pace, swimPaceMethod, true)}
                        disabled={!thresholds.swim_threshold_pace || calculatingSwimPaceZones}
                      >
                        Recalculate Pace Zones
                      </Button>
                      <Typography variant="caption" color="text.secondary">
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
                        </Select>
                      </FormControl>
                    </Box>
                  </>
                )}
              </CardContent>

              <CardActions sx={{ justifyContent: 'flex-end', px: 2, pb: 2 }}>
                {garminStatus?.connected ? (
                  <>
                    <Button
                      startIcon={syncing ? <CircularProgress size={20} /> : <SyncIcon />}
                      onClick={handleSyncActivities}
                      disabled={syncing}
                    >
                      Sync Activities
                    </Button>
                    <Button
                      variant="outlined"
                      startIcon={<LinkOffIcon />}
                      onClick={handleDisconnectGarmin}
                      disabled={connecting}
                    >
                      Disconnect
                    </Button>
                  </>
                ) : (
                  <Button
                    variant="contained"
                    startIcon={<LinkIcon />}
                    onClick={() => setConnectDialogOpen(true)}
                  >
                    Connect Garmin
                  </Button>
                )}
              </CardActions>
            </Card>
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
    </Container>
  );
};

export default SettingsNew;
