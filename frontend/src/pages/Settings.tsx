import React, { useState, useEffect } from 'react'
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
  List,
  ListItem,
  ListItemText,
  Chip,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  useMediaQuery,
  useTheme,
  LinearProgress,
  Menu,
  IconButton,
  ListItemIcon,
} from '@mui/material'
import {
  Link as LinkIcon,
  LinkOff as LinkOffIcon,
  Sync as SyncIcon,
  CheckCircle as CheckCircleIcon,
  FitnessCenter as FitnessCenterIcon,
  MoreVert as MoreVertIcon,
  DirectionsRun as DirectionsRunIcon,
} from '@mui/icons-material'
import apiClient from '../services/api'

interface GarminStatus {
  connected: boolean
  email: string | null
  last_sync: string | null
}

const Settings: React.FC = () => {
  const theme = useTheme();
  const isMobile = useMediaQuery('(max-width:1400px)');
  
  console.log('Settings - isMobile:', isMobile, 'window.innerWidth:', window.innerWidth);
  
  const [garminStatus, setGarminStatus] = useState<GarminStatus | null>(null)
  const [loading, setLoading] = useState(true)
  const [syncDays, setSyncDays] = useState(30) // Days to sync
  const [connecting, setConnecting] = useState(false)
  const [menuAnchor, setMenuAnchor] = useState<null | HTMLElement>(null)

  // Set document title
  useEffect(() => {
    document.title = 'Settings - Kinesis';
  }, []);
  const [syncing, setSyncing] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [success, setSuccess] = useState<string | null>(null)
  
  // Connect dialog state
  const [connectDialogOpen, setConnectDialogOpen] = useState(false)
  const [garminEmail, setGarminEmail] = useState('')
  const [garminPassword, setGarminPassword] = useState('')
  
  // Mobile menu state
  const [mobileMenuAnchor, setMobileMenuAnchor] = useState<null | HTMLElement>(null)
  const mobileMenuOpen = Boolean(mobileMenuAnchor)

  useEffect(() => {
    fetchGarminStatus()
  }, [])

  const fetchGarminStatus = async () => {
    try {
      setLoading(true)
      const response = await apiClient.get('/garmin/status')
      setGarminStatus(response.data)
    } catch (err: any) {
      setError('Failed to fetch Garmin connection status')
    } finally {
      setLoading(false)
    }
  }

  const handleConnectGarmin = async () => {
    if (!garminEmail || !garminPassword) {
      setError('Please enter both email and password')
      return
    }

    try {
      setConnecting(true)
      setError(null)
      
      await apiClient.post('/garmin/connect', {
        email: garminEmail,
        password: garminPassword,
      })
      
      setSuccess('Successfully connected to Garmin!')
      setConnectDialogOpen(false)
      setGarminEmail('')
      setGarminPassword('')
      
      // Refresh status
      await fetchGarminStatus()
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to connect to Garmin')
    } finally {
      setConnecting(false)
    }
  }

  const handleDisconnectGarmin = async () => {
    if (!window.confirm('Are you sure you want to disconnect your Garmin account?')) {
      return
    }

    try {
      setLoading(true)
      setError(null)
      
      await apiClient.delete('/garmin/disconnect')
      
      setSuccess('Successfully disconnected from Garmin')
      await fetchGarminStatus()
    } catch (err: any) {
      setError('Failed to disconnect from Garmin')
    } finally {
      setLoading(false)
    }
  }

  const handleSyncActivities = async () => {
    try {
      setSyncing(true)
      setError(null)
      
      // Use longer timeout for sync (can take 60+ seconds for 2 years of data)
      const response = await apiClient.post('/garmin/sync-activities', { days: syncDays }, {
        timeout: 120000, // 2 minutes
      })
      
      setSuccess(response.data.message)
      await fetchGarminStatus()
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to sync activities')
    } finally {
      setSyncing(false)
    }
  }

  const handleSyncWorkouts = async () => {
    try {
      setSyncing(true)
      setError(null)
      setMobileMenuAnchor(null) // Close menu
      
      const response = await apiClient.post('/garmin/sync-workouts', {
        days_ahead: 14
      })
      
      if (response.data) {
        const { synced, scheduled, skipped, failed } = response.data
        setSuccess(
          `Workout Sync Complete: ${synced} synced, ${scheduled} scheduled, ${skipped} skipped, ${failed} failed`
        )
        await fetchGarminStatus()
      }
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to sync workouts')
    } finally {
      setSyncing(false)
    }
  }

  const handleSyncAll = async () => {
    try {
      setSyncing(true)
      setError(null)
      setMobileMenuAnchor(null) // Close menu
      
      // Sync activities first
      await apiClient.post('/garmin/sync-activities', { days: syncDays }, {
        timeout: 120000,
      })
      
      // Then sync workouts
      const response = await apiClient.post('/garmin/sync-workouts', {
        days_ahead: 14
      })
      
      if (response.data) {
        const { synced, scheduled, skipped, failed } = response.data
        setSuccess(
          `Full Sync Complete: Activities synced, ${synced} workouts synced, ${scheduled} scheduled, ${skipped} skipped, ${failed} failed`
        )
        await fetchGarminStatus()
      }
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to sync')
    } finally {
      setSyncing(false)
    }
  }

  const handleDisconnectClick = () => {
    setMobileMenuAnchor(null)
    handleDisconnectGarmin()
  }

  if (loading && !garminStatus) {
    return (
      <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
        <Box display="flex" justifyContent="center" alignItems="center" minHeight="60vh">
          <CircularProgress />
        </Box>
      </Container>
    )
  }

  return (
    <Container maxWidth="lg" sx={{ mt: { xs: 2, sm: 4 }, mb: { xs: 2, sm: 4 }, px: { xs: 2, sm: 3 } }}>
      <Typography variant="h4" gutterBottom sx={{ fontSize: { xs: '1.75rem', sm: '2.125rem' } }}>
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

      {/* Garmin Connect Integration */}
      <Paper sx={{ p: { xs: 2, sm: 3 }, mb: 3 }}>
        <Typography variant="h5" gutterBottom sx={{ fontSize: { xs: '1.25rem', sm: '1.5rem' } }}>
          Integrations
        </Typography>
        <Divider sx={{ mb: 3 }} />

        <Card variant="outlined">
          <CardContent sx={{ p: { xs: 2, sm: 3 } }}>
            <Box display="flex" alignItems="center" justifyContent="space-between" mb={2} flexWrap="wrap" gap={1}>
              <Box display="flex" alignItems="center" gap={2} flexWrap="wrap">
                <Typography 
                  variant="h6" 
                  sx={{ 
                    fontSize: { xs: '0.95rem', sm: '1.25rem' },
                    wordBreak: 'break-word'
                  }}
                >
                  Garmin Connect
                </Typography>
                {garminStatus?.connected ? (
                  <Chip
                    icon={<CheckCircleIcon />}
                    label="Connected"
                    color="success"
                    size="small"
                  />
                ) : (
                  <Chip label="Not Connected" color="default" size="small" />
                )}
              </Box>
            </Box>

            <Typography 
              variant="body2" 
              color="text.secondary" 
              paragraph
              sx={{ fontSize: { xs: '0.8rem', sm: '0.875rem' } }}
            >
              Connect your Garmin account to automatically sync your activities and workouts.
            </Typography>

            {garminStatus?.connected && (
              <Box mt={2}>
                <List dense>
                  <ListItem>
                    <ListItemText
                      primary="Garmin Account"
                      secondary={garminStatus.email}
                      primaryTypographyProps={{ fontSize: { xs: '0.85rem', sm: '0.875rem' } }}
                      secondaryTypographyProps={{ 
                        fontSize: { xs: '0.75rem', sm: '0.8125rem' },
                        sx: { wordBreak: 'break-word' }
                      }}
                    />
                  </ListItem>
                  {garminStatus.last_sync && (
                    <ListItem>
                      <ListItemText
                        primary="Last Sync"
                        secondary={new Date(garminStatus.last_sync).toLocaleString()}
                        primaryTypographyProps={{ fontSize: { xs: '0.85rem', sm: '0.875rem' } }}
                        secondaryTypographyProps={{ fontSize: { xs: '0.75rem', sm: '0.8125rem' } }}
                      />
                    </ListItem>
                  )}
                </List>
              </Box>
            )}
          </CardContent>

          <CardActions sx={{ flexDirection: 'column', alignItems: 'stretch', gap: 2, p: 2 }}>
            {syncing && (
              <LinearProgress sx={{ width: '100%', mb: -1 }} />
            )}
            {garminStatus?.connected ? (
              <>
                {/* Sync Period Selector */}
                <FormControl size="small" fullWidth>
                  <InputLabel>Sync Period</InputLabel>
                  <Select
                    value={syncDays}
                    label="Sync Period"
                    onChange={(e) => setSyncDays(Number(e.target.value))}
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

                {/* Mobile Layout: Primary Action + Menu */}
                {isMobile ? (
                  <>
                    <Box sx={{ display: 'flex', gap: 1 }}>
                      <Button
                        startIcon={<SyncIcon />}
                        onClick={handleSyncAll}
                        disabled={syncing}
                        variant="contained"
                        fullWidth
                        sx={{ 
                          fontSize: '0.875rem',
                          py: 1.25,
                          minHeight: 44
                        }}
                      >
                        {syncing ? 'Syncing...' : 'Sync All'}
                      </Button>
                      <IconButton
                        onClick={(e) => setMobileMenuAnchor(e.currentTarget)}
                        disabled={syncing}
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
                  </>
                ) : (
                  /* Desktop Layout: All buttons visible */
                  <>
                    <Box sx={{ display: 'flex', gap: 2 }}>
                      <Button
                        startIcon={<DirectionsRunIcon />}
                        onClick={handleSyncActivities}
                        disabled={syncing}
                        variant="outlined"
                        sx={{ flex: 1 }}
                      >
                        {syncing ? 'Syncing...' : 'Sync Activities'}
                      </Button>
                      <Button
                        startIcon={<FitnessCenterIcon />}
                        onClick={handleSyncWorkouts}
                        disabled={syncing}
                        variant="outlined"
                        color="primary"
                        sx={{ flex: 1 }}
                      >
                        {syncing ? 'Syncing...' : 'Sync Workouts'}
                      </Button>
                    </Box>
                    <Button
                      startIcon={<LinkOffIcon />}
                      onClick={handleDisconnectGarmin}
                      color="error"
                      variant="outlined"
                      sx={{ maxWidth: 200 }}
                    >
                      Disconnect
                    </Button>
                  </>
                )}

                {/* Mobile Menu */}
                <Menu
                  anchorEl={mobileMenuAnchor}
                  open={mobileMenuOpen}
                  onClose={() => setMobileMenuAnchor(null)}
                  anchorOrigin={{ vertical: 'bottom', horizontal: 'right' }}
                  transformOrigin={{ vertical: 'top', horizontal: 'right' }}
                >
                  <MenuItem onClick={handleSyncActivities} disabled={syncing}>
                    <ListItemIcon>
                      <DirectionsRunIcon fontSize="small" />
                    </ListItemIcon>
                    <ListItemText>Sync Activities Only</ListItemText>
                  </MenuItem>
                  <MenuItem onClick={handleSyncWorkouts} disabled={syncing}>
                    <ListItemIcon>
                      <FitnessCenterIcon fontSize="small" />
                    </ListItemIcon>
                    <ListItemText>Sync Workouts Only</ListItemText>
                  </MenuItem>
                  <Divider />
                  <MenuItem onClick={handleDisconnectClick} disabled={syncing}>
                    <ListItemIcon>
                      <LinkOffIcon fontSize="small" color="error" />
                    </ListItemIcon>
                    <ListItemText sx={{ color: 'error.main' }}>Disconnect</ListItemText>
                  </MenuItem>
                </Menu>
              </>
            ) : (
              <Button
                startIcon={<LinkIcon />}
                onClick={() => setConnectDialogOpen(true)}
                variant="contained"
                fullWidth
                sx={{ minHeight: 44 }}
              >
                Connect Garmin
              </Button>
            )}
          </CardActions>
        </Card>
      </Paper>

      {/* Connect Garmin Dialog */}
      <Dialog open={connectDialogOpen} onClose={() => setConnectDialogOpen(false)} maxWidth="sm" fullWidth>
        <DialogTitle>Connect Garmin Account</DialogTitle>
        <DialogContent>
          <Alert severity="info" sx={{ mb: 3 }}>
            Enter your Garmin Connect credentials to link your account.
          </Alert>
          
          <TextField
            autoFocus
            margin="dense"
            label="Garmin Email"
            type="email"
            fullWidth
            value={garminEmail}
            onChange={(e) => setGarminEmail(e.target.value)}
            disabled={connecting}
            sx={{ mb: 2 }}
          />
          
          <TextField
            margin="dense"
            label="Garmin Password"
            type="password"
            fullWidth
            value={garminPassword}
            onChange={(e) => setGarminPassword(e.target.value)}
            disabled={connecting}
          />
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setConnectDialogOpen(false)} disabled={connecting}>
            Cancel
          </Button>
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
  )
}

export default Settings
