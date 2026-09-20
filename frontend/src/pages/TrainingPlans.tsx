import React, { useEffect, useState } from 'react';
import {
  Box,
  Button,
  Card,
  CardContent,
  CardActions,
  Container,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  Typography,
  Grid,
  Chip,
  MenuItem,
  Select,
  FormControl,
  InputLabel,
  IconButton,
  Alert,
  Tabs,
  Tab,
  Badge,
} from '@mui/material';
import { 
  Add as AddIcon, 
  Delete as DeleteIcon, 
  FitnessCenter, 
  EmojiEvents,
  AutoAwesome as AutoAwesomeIcon,
  Upload as UploadIcon,
  CheckCircle as CheckCircleIcon,
} from '@mui/icons-material';
import { useNavigate } from 'react-router-dom';
import { useAuthStore } from '../store/authStore';
import api from '../services/api';
import EmptyState from '../components/EmptyState';
import TrainingPlansSkeleton from '../components/skeletons/TrainingPlansSkeleton';
import AITrainingPlanImport from '../components/AITrainingPlanImport';

interface TrainingPlan {
  id: number;
  name: string;
  description?: string;
  start_date: string;
  end_date: string;
  sport_type: string;
  is_active: boolean;
  activation_date?: string;
  workout_count: number;
  completed_count: number;
  created_at: string;
}

interface Event {
  id: number;
  name: string;
  event_date: string;
  event_type: string;
  location?: string;
  description?: string;
  goal_time?: string;
  target_distance?: string;
  created_at: string;
}

const sportTypes = [
  { value: 'running', label: 'Running' },
  { value: 'cycling', label: 'Cycling' },
  { value: 'swimming', label: 'Swimming' },
  { value: 'triathlon', label: 'Triathlon' },
  { value: 'gym', label: 'Gym' },
  { value: 'other', label: 'Other' },
];

const TrainingPlans: React.FC = () => {
  const navigate = useNavigate();
  const { user } = useAuthStore();
  const [currentTab, setCurrentTab] = useState(0);
  const [plans, setPlans] = useState<TrainingPlan[]>([]);
  const [events, setEvents] = useState<Event[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [dialogOpen, setDialogOpen] = useState(false);
  const [eventDialogOpen, setEventDialogOpen] = useState(false);
  const [aiImportOpen, setAiImportOpen] = useState(false);
  const [activationDialogOpen, setActivationDialogOpen] = useState(false);
  const [deactivationDialogOpen, setDeactivationDialogOpen] = useState(false);
  const [selectedPlanForActivation, setSelectedPlanForActivation] = useState<TrainingPlan | null>(null);
  const [activationDate, setActivationDate] = useState<string>('');
  const [workoutAnalysis, setWorkoutAnalysis] = useState<{past: number, future: number} | null>(null);
  const [formData, setFormData] = useState({
    name: '',
    description: '',
    start_date: '',
    end_date: '',
    sport_type: 'running',
  });
  const [eventFormData, setEventFormData] = useState({
    name: '',
    event_date: '',
    event_type: 'race',
    location: '',
    description: '',
    goal_time: '',
    target_distance: '',
  });

  useEffect(() => {
    document.title = 'Training Plans - Kinesis';
  }, []);

  useEffect(() => {
    if (!user) {
      navigate('/login');
      return;
    }
    fetchPlans();
    fetchEvents();
  }, [user, navigate]);

  const fetchPlans = async () => {
    try {
      setLoading(true);
      const response = await api.get('/training-plans');
      setPlans(response.data);
      setError(null);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to load training plans');
    } finally {
      setLoading(false);
    }
  };

  const fetchEvents = async () => {
    try {
      setLoading(true);
      const response = await api.get('/events');
      setEvents(response.data);
      setError(null);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to load events');
    } finally {
      setLoading(false);
    }
  };

  const handleCreatePlan = async () => {
    try {
      await api.post('/training-plans', formData);
      setDialogOpen(false);
      setFormData({
        name: '',
        description: '',
        start_date: '',
        end_date: '',
        sport_type: 'running',
      });
      fetchPlans();
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to create training plan');
    }
  };

  const handleDeletePlan = async (planId: number) => {
    if (!confirm('Are you sure you want to delete this training plan?')) {
      return;
    }
    try {
      await api.delete(`/training-plans/${planId}`);
      fetchPlans();
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to delete training plan');
    }
  };

  const handleOpenActivationDialog = async (plan: TrainingPlan) => {
    setSelectedPlanForActivation(plan);
    
    // Set default activation date to today
    const today = new Date().toISOString().split('T')[0];
    setActivationDate(today);
    
    if (plan.is_active) {
      setDeactivationDialogOpen(true);
    } else {
      // Fetch plan workouts to analyze past/future split
      try {
        const response = await api.get(`/training-plans/${plan.id}`);
        const fullPlan = response.data;
        
        // Calculate past/future workouts based on today
        const todayDate = new Date(today);
        let pastCount = 0;
        let futureCount = 0;
        
        fullPlan.workouts?.forEach((workout: any) => {
          const workoutDate = new Date(workout.date);
          if (workoutDate < todayDate) {
            pastCount++;
          } else {
            futureCount++;
          }
        });
        
        setWorkoutAnalysis({ past: pastCount, future: futureCount });
      } catch (err) {
        console.error('Failed to fetch workout details:', err);
        setWorkoutAnalysis({ past: 0, future: plan.workout_count });
      }
      
      setActivationDialogOpen(true);
    }
  };

  const handleConfirmActivation = async () => {
    if (!selectedPlanForActivation) return;
    
    try {
      await api.post(`/training-plans/${selectedPlanForActivation.id}/activate`, {
        activation_date: activationDate
      });
      setActivationDialogOpen(false);
      setSelectedPlanForActivation(null);
      setActivationDate('');
      setWorkoutAnalysis(null);
      fetchPlans();
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to activate plan');
    }
  };

  const handleConfirmDeactivation = async () => {
    if (!selectedPlanForActivation) return;
    
    try {
      await api.post(`/training-plans/${selectedPlanForActivation.id}/deactivate`);
      setDeactivationDialogOpen(false);
      setSelectedPlanForActivation(null);
      fetchPlans();
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to deactivate plan');
    }
  };

  const handleCancelActivation = () => {
    setActivationDialogOpen(false);
    setDeactivationDialogOpen(false);
    setSelectedPlanForActivation(null);
    setActivationDate('');
    setWorkoutAnalysis(null);
  };

  const handleCreateEvent = async () => {
    try {
      await api.post('/events', eventFormData);
      setEventDialogOpen(false);
      setEventFormData({
        name: '',
        event_date: '',
        event_type: 'race',
        location: '',
        description: '',
        goal_time: '',
        target_distance: '',
      });
      fetchEvents();
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to create event');
    }
  };

  const handleDeleteEvent = async (eventId: number) => {
    if (!confirm('Are you sure you want to delete this event?')) {
      return;
    }
    try {
      await api.delete(`/events/${eventId}`);
      fetchEvents();
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to delete event');
    }
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString();
  };

  const getSportColor = (sport: string) => {
    const colors: { [key: string]: 'primary' | 'secondary' | 'success' | 'warning' | 'error' | 'info' } = {
      running: 'primary',
      cycling: 'secondary',
      swimming: 'info',
      triathlon: 'success',
      gym: 'warning',
      other: 'error',
    };
    return colors[sport] || 'default';
  };

  if (!user) {
    return null;
  }

  const handleTabChange = (event: React.SyntheticEvent, newValue: number) => {
    setCurrentTab(newValue);
  };

  return (
    <Box sx={{ display: 'flex', flexDirection: 'column', height: '100vh' }}>
      {/* Fixed Header */}
      <Container maxWidth="lg" sx={{ pt: 3, pb: 2 }}>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
          <Typography variant="h4" component="h1">
            Training Plans & Events
          </Typography>
          <Button
            variant="contained"
            startIcon={<AddIcon />}
            onClick={() => currentTab === 0 ? setDialogOpen(true) : setEventDialogOpen(true)}
          >
            {currentTab === 0 ? 'New Plan' : 'New Event'}
          </Button>
        </Box>

        {error && (
          <Alert severity="error" sx={{ mb: 2 }} onClose={() => setError(null)}>
            {error}
          </Alert>
        )}

        {/* Fixed Tabs */}
        <Tabs 
          value={currentTab} 
          onChange={handleTabChange}
          sx={{ 
            borderBottom: 1, 
            borderColor: 'divider',
            mb: 0
          }}
        >
          <Tab label="Plans" icon={<FitnessCenter />} iconPosition="start" />
          <Tab label="Events" icon={<EmojiEvents />} iconPosition="start" />
        </Tabs>
      </Container>

      {/* Scrollable Content Area */}
      <Box sx={{ flex: 1, overflow: 'auto' }}>
        <Container maxWidth="lg" sx={{ py: 3 }}>
          {/* Plans Tab Content */}
          {currentTab === 0 && (
            <>
              {/* Info Alert */}
              {plans.length > 0 && (
                <Alert severity="info" sx={{ mb: 3 }}>
                  <Typography variant="body2">
                    <strong>💡 Plan Activation:</strong> Only workouts from your active training plan appear in the calendar. 
                    Click "Activate Plan" to make a plan active. Only one plan can be active at a time - activating a new plan 
                    automatically deactivates the current one.
                  </Typography>
                </Alert>
              )}
              
              {/* AI Plan Generation Card */}
              <Card 
                sx={{ 
                  mb: 3,
                  background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
                  color: 'white',
                  cursor: 'pointer',
                  transition: 'transform 0.2s',
                  '&:hover': {
                    transform: 'translateY(-4px)',
                  }
                }}
                onClick={() => navigate('/ai-plan/generate')}
              >
                <CardContent>
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                    <AutoAwesomeIcon sx={{ fontSize: 48 }} />
                    <Box sx={{ flex: 1 }}>
                      <Typography variant="h5" component="h2" gutterBottom>
                        Generate AI Training Plan
                      </Typography>
                      <Typography variant="body2" sx={{ opacity: 0.9 }}>
                        Let AI create a personalized training plan based on your fitness data, goals, and schedule.
                        Uses ChatGPT or Claude to generate scientifically-backed training programs.
                      </Typography>
                    </Box>
                    <Box sx={{ display: 'flex', gap: 1 }}>
                      <Button 
                        variant="contained" 
                        sx={{ bgcolor: 'white', color: '#667eea', '&:hover': { bgcolor: '#f0f0f0' } }}
                        startIcon={<AutoAwesomeIcon />}
                        onClick={(e) => {
                          e.stopPropagation();
                          navigate('/ai-plan/generate');
                        }}
                      >
                        Generate
                      </Button>
                      <Button 
                        variant="outlined" 
                        sx={{ borderColor: 'white', color: 'white', '&:hover': { borderColor: 'white', bgcolor: 'rgba(255,255,255,0.1)' } }}
                        startIcon={<UploadIcon />}
                        onClick={(e) => {
                          e.stopPropagation();
                          setAiImportOpen(true);
                        }}
                      >
                        Import
                      </Button>
                    </Box>
                  </Box>
                </CardContent>
              </Card>

              {loading ? (
                <TrainingPlansSkeleton />
              ) : plans.length === 0 ? (
                <EmptyState
                  icon={<FitnessCenter />}
                  title="No training plans yet"
                  description="Create your first training plan to organize your workouts and track your progress. Choose from popular templates or build a custom plan."
                  actionLabel="Create Plan"
                  onAction={() => setDialogOpen(true)}
                  secondaryActionLabel="View Calendar"
                  onSecondaryAction={() => navigate('/calendar')}
                />
              ) : (
                <Grid container spacing={3}>
                  {plans.map((plan) => (
                    <Grid item xs={12} md={6} key={plan.id}>
                      <Card 
                        sx={{ 
                          position: 'relative',
                          borderLeft: plan.is_active ? 4 : 0,
                          borderLeftColor: 'success.main',
                          boxShadow: plan.is_active 
                            ? (theme) => `0 4px 12px ${theme.palette.mode === 'dark' ? 'rgba(76, 175, 80, 0.15)' : 'rgba(76, 175, 80, 0.12)'}`
                            : 1,
                          transition: 'all 0.3s ease',
                          '&:hover': {
                            boxShadow: plan.is_active ? 4 : 2,
                          }
                        }}
                      >
                        <CardContent>
                          {/* Header Row: Title + Active Badge (inline) | Sport Badge */}
                          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', mb: 2, gap: 1 }}>
                            {/* Left: Plan Name + Active Indicator */}
                            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, flexWrap: 'wrap', flex: 1, minWidth: 0 }}>
                              <Typography 
                                variant="h5" 
                                component="h2"
                                sx={{ 
                                  fontWeight: plan.is_active ? 600 : 500,
                                  wordBreak: 'break-word',
                                }}
                              >
                                {plan.name}
                              </Typography>
                              {plan.is_active && (
                                <Chip
                                  label="ACTIVE"
                                  color="success"
                                  size="small"
                                  icon={<CheckCircleIcon sx={{ fontSize: 16 }} />}
                                  sx={{
                                    height: 24,
                                    fontWeight: 700,
                                    fontSize: '0.7rem',
                                    letterSpacing: '0.5px',
                                  }}
                                />
                              )}
                            </Box>
                            {/* Right: Sport Type Badge */}
                            <Chip
                              label={plan.sport_type}
                              color={getSportColor(plan.sport_type)}
                              size="small"
                              sx={{ flexShrink: 0 }}
                            />
                          </Box>
                          {plan.description && (
                            <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                              {plan.description}
                            </Typography>
                          )}
                          <Box sx={{ mb: 2 }}>
                            <Typography variant="body2" color="text.secondary">
                              {formatDate(plan.start_date)} - {formatDate(plan.end_date)}
                            </Typography>
                          </Box>
                          <Box sx={{ display: 'flex', gap: 2, mb: 2 }}>
                            <Typography variant="body2">
                              <strong>{plan.workout_count}</strong> workouts
                            </Typography>
                            <Typography variant="body2">
                              <strong>{plan.completed_count}</strong> completed
                            </Typography>
                          </Box>
                          <Box sx={{ 
                            display: 'flex', 
                            alignItems: 'center', 
                            justifyContent: 'space-between',
                            pt: 1,
                            borderTop: 1,
                            borderColor: 'divider',
                          }}>
                            {plan.is_active ? (
                              <Button
                                variant="outlined"
                                color="error"
                                size="small"
                                onClick={() => handleOpenActivationDialog(plan)}
                                sx={{ fontWeight: 600 }}
                              >
                                Deactivate Plan
                              </Button>
                            ) : (
                              <Button
                                variant="contained"
                                color="primary"
                                size="small"
                                onClick={() => handleOpenActivationDialog(plan)}
                                sx={{ fontWeight: 600 }}
                              >
                                Activate Plan
                              </Button>
                            )}
                            <Typography variant="caption" color="text.secondary" sx={{ fontSize: '0.7rem' }}>
                              {plan.is_active ? 'Workouts shown in calendar' : 'Not shown in calendar'}
                            </Typography>
                          </Box>
                        </CardContent>
                        <CardActions>
                          <Button
                            size="small"
                            onClick={() => navigate(`/plans/${plan.id}`)}
                          >
                            View Details
                          </Button>
                          <IconButton
                            size="small"
                            color="error"
                            onClick={() => handleDeletePlan(plan.id)}
                          >
                            <DeleteIcon />
                          </IconButton>
                        </CardActions>
                      </Card>
                    </Grid>
                  ))}
                </Grid>
              )}
            </>
          )}

          {/* Events Tab Content */}
          {currentTab === 1 && (
            <>
              {loading ? (
                <TrainingPlansSkeleton />
              ) : events.length === 0 ? (
                <EmptyState
                  icon={<EmojiEvents />}
                  title="No events yet"
                  description="Add your upcoming races, competitions, or fitness events. Track your goals and build training plans around your key events."
                  actionLabel="Add Event"
                  onAction={() => setEventDialogOpen(true)}
                />
              ) : (
                <Grid container spacing={3}>
                  {events.map((event) => (
                    <Grid item xs={12} md={6} key={event.id}>
                      <Card>
                        <CardContent>
                          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', mb: 2 }}>
                            <Typography variant="h5" component="h2">
                              {event.name}
                            </Typography>
                            <Chip
                              label={event.event_type}
                              color="primary"
                              size="small"
                            />
                          </Box>
                          {event.location && (
                            <Typography variant="body2" color="text.secondary" sx={{ mb: 1 }}>
                              📍 {event.location}
                            </Typography>
                          )}
                          {event.description && (
                            <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                              {event.description}
                            </Typography>
                          )}
                          <Box sx={{ mb: 2 }}>
                            <Typography variant="body2" color="text.secondary">
                              📅 {formatDate(event.event_date)}
                            </Typography>
                          </Box>
                          {(event.target_distance || event.goal_time) && (
                            <Box sx={{ display: 'flex', gap: 2 }}>
                              {event.target_distance && (
                                <Typography variant="body2">
                                  <strong>Distance:</strong> {event.target_distance}
                                </Typography>
                              )}
                              {event.goal_time && (
                                <Typography variant="body2">
                                  <strong>Goal:</strong> {event.goal_time}
                                </Typography>
                              )}
                            </Box>
                          )}
                        </CardContent>
                        <CardActions>
                          <Button
                            size="small"
                            onClick={() => navigate(`/events/${event.id}`)}
                          >
                            View Details
                          </Button>
                          <IconButton
                            size="small"
                            color="error"
                            onClick={() => handleDeleteEvent(event.id)}
                          >
                            <DeleteIcon />
                          </IconButton>
                        </CardActions>
                      </Card>
                    </Grid>
                  ))}
                </Grid>
              )}
            </>
          )}
        </Container>
      </Box>

      {/* Create Plan Dialog */}
      <Dialog open={dialogOpen} onClose={() => setDialogOpen(false)} maxWidth="sm" fullWidth>
        <DialogTitle>Create Training Plan</DialogTitle>
        <DialogContent>
          <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2, mt: 2 }}>
            <TextField
              label="Plan Name"
              fullWidth
              value={formData.name}
              onChange={(e) => setFormData({ ...formData, name: e.target.value })}
              required
            />
            <TextField
              label="Description"
              fullWidth
              multiline
              rows={3}
              value={formData.description}
              onChange={(e) => setFormData({ ...formData, description: e.target.value })}
            />
            <FormControl fullWidth>
              <InputLabel>Sport Type</InputLabel>
              <Select
                value={formData.sport_type}
                label="Sport Type"
                onChange={(e) => setFormData({ ...formData, sport_type: e.target.value })}
              >
                {sportTypes.map((sport) => (
                  <MenuItem key={sport.value} value={sport.value}>
                    {sport.label}
                  </MenuItem>
                ))}
              </Select>
            </FormControl>
            <TextField
              label="Start Date"
              type="date"
              fullWidth
              InputLabelProps={{ shrink: true }}
              value={formData.start_date}
              onChange={(e) => setFormData({ ...formData, start_date: e.target.value })}
              required
            />
            <TextField
              label="End Date"
              type="date"
              fullWidth
              InputLabelProps={{ shrink: true }}
              value={formData.end_date}
              onChange={(e) => setFormData({ ...formData, end_date: e.target.value })}
              required
            />
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setDialogOpen(false)}>Cancel</Button>
          <Button
            onClick={handleCreatePlan}
            variant="contained"
            disabled={!formData.name || !formData.start_date || !formData.end_date}
          >
            Create
          </Button>
        </DialogActions>
      </Dialog>

      {/* Create Event Dialog */}
      <Dialog open={eventDialogOpen} onClose={() => setEventDialogOpen(false)} maxWidth="sm" fullWidth>
        <DialogTitle>Add Event</DialogTitle>
        <DialogContent>
          <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2, mt: 2 }}>
            <TextField
              label="Event Name"
              fullWidth
              value={eventFormData.name}
              onChange={(e) => setEventFormData({ ...eventFormData, name: e.target.value })}
              required
            />
            <TextField
              label="Event Date"
              type="date"
              fullWidth
              InputLabelProps={{ shrink: true }}
              value={eventFormData.event_date}
              onChange={(e) => setEventFormData({ ...eventFormData, event_date: e.target.value })}
              required
            />
            <FormControl fullWidth>
              <InputLabel>Event Type</InputLabel>
              <Select
                value={eventFormData.event_type}
                label="Event Type"
                onChange={(e) => setEventFormData({ ...eventFormData, event_type: e.target.value })}
              >
                <MenuItem value="race">Race</MenuItem>
                <MenuItem value="competition">Competition</MenuItem>
                <MenuItem value="challenge">Challenge</MenuItem>
                <MenuItem value="other">Other</MenuItem>
              </Select>
            </FormControl>
            <TextField
              label="Location"
              fullWidth
              value={eventFormData.location}
              onChange={(e) => setEventFormData({ ...eventFormData, location: e.target.value })}
            />
            <TextField
              label="Target Distance"
              fullWidth
              placeholder="e.g., 5K, 10K, Half Marathon, Full Marathon"
              value={eventFormData.target_distance}
              onChange={(e) => setEventFormData({ ...eventFormData, target_distance: e.target.value })}
            />
            <TextField
              label="Goal Time"
              fullWidth
              placeholder="e.g., 3:30:00"
              value={eventFormData.goal_time}
              onChange={(e) => setEventFormData({ ...eventFormData, goal_time: e.target.value })}
            />
            <TextField
              label="Description"
              fullWidth
              multiline
              rows={3}
              value={eventFormData.description}
              onChange={(e) => setEventFormData({ ...eventFormData, description: e.target.value })}
            />
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setEventDialogOpen(false)}>Cancel</Button>
          <Button
            onClick={handleCreateEvent}
            variant="contained"
            disabled={!eventFormData.name || !eventFormData.event_date}
          >
            Add Event
          </Button>
        </DialogActions>
      </Dialog>

      {/* AI Training Plan Import Dialog */}
      <AITrainingPlanImport
        open={aiImportOpen}
        onClose={() => setAiImportOpen(false)}
        onSuccess={() => {
          setAiImportOpen(false);
          fetchPlans();
        }}
      />

      {/* Plan Activation Confirmation Dialog */}
      <Dialog 
        open={activationDialogOpen} 
        onClose={handleCancelActivation}
        maxWidth="sm"
        fullWidth
      >
        <DialogTitle sx={{ pb: 1 }}>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            <CheckCircleIcon color="primary" />
            <Typography variant="h6">Activate Training Plan</Typography>
          </Box>
        </DialogTitle>
        <DialogContent>
          <Alert severity="info" sx={{ mb: 2 }}>
            <Typography variant="body2" gutterBottom>
              <strong>What happens when you activate this plan:</strong>
            </Typography>
            <Typography variant="body2" component="div" sx={{ pl: 2 }}>
              • All workouts from <strong>{selectedPlanForActivation?.name}</strong> will appear in your calendar
              <br />
              • Any currently active plan will be automatically deactivated
              <br />
              • Only one plan can be active at a time
              <br />
              • Completed activities remain unaffected
            </Typography>
          </Alert>

          {/* Activation Date Picker */}
          <Box sx={{ mb: 3 }}>
            <Typography variant="subtitle2" gutterBottom sx={{ fontWeight: 600 }}>
              When should this plan start?
            </Typography>
            <TextField
              type="date"
              fullWidth
              value={activationDate}
              onChange={(e) => setActivationDate(e.target.value)}
              helperText="This sets when the plan becomes active in your calendar. Choose today or a future start date."
              InputLabelProps={{ shrink: true }}
              sx={{ mt: 1 }}
            />
          </Box>

          {/* Workout Analysis */}
          {workoutAnalysis && (
            <Alert severity="warning" sx={{ mb: 2 }}>
              <Typography variant="body2" gutterBottom>
                <strong>📊 Workout Analysis:</strong>
              </Typography>
              <Typography variant="body2" component="div" sx={{ pl: 2 }}>
                • <strong>{workoutAnalysis.past}</strong> sessions are in the past
                {workoutAnalysis.past > 0 && (
                  <>
                    <br />
                    <span style={{ fontSize: '0.85em', opacity: 0.9 }}>
                      (Future: Match existing activities to these sessions automatically)
                    </span>
                  </>
                )}
                <br />
                • <strong>{workoutAnalysis.future}</strong> sessions are upcoming
                {workoutAnalysis.future > 0 && (
                  <>
                    <br />
                    <span style={{ fontSize: '0.85em', opacity: 0.9 }}>
                      (Future: Will contribute to prognostic TSS calculations)
                    </span>
                  </>
                )}
              </Typography>
            </Alert>
          )}
          
          {selectedPlanForActivation && (
            <Box sx={{ 
              p: 2, 
              bgcolor: 'background.default', 
              borderRadius: 1,
              border: 1,
              borderColor: 'divider',
            }}>
              <Typography variant="body2" color="text.secondary" gutterBottom>
                Plan Details:
              </Typography>
              <Typography variant="body1" gutterBottom>
                <strong>{selectedPlanForActivation.name}</strong>
              </Typography>
              <Typography variant="body2" color="text.secondary">
                {formatDate(selectedPlanForActivation.start_date)} - {formatDate(selectedPlanForActivation.end_date)}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                {selectedPlanForActivation.workout_count} workouts • {selectedPlanForActivation.sport_type}
              </Typography>
            </Box>
          )}
        </DialogContent>
        <DialogActions sx={{ px: 3, pb: 2 }}>
          <Button onClick={handleCancelActivation} color="inherit">
            Cancel
          </Button>
          <Button 
            onClick={handleConfirmActivation} 
            variant="contained" 
            color="primary"
            startIcon={<CheckCircleIcon />}
          >
            Activate Plan
          </Button>
        </DialogActions>
      </Dialog>

      {/* Plan Deactivation Confirmation Dialog */}
      <Dialog 
        open={deactivationDialogOpen} 
        onClose={handleCancelActivation}
        maxWidth="sm"
        fullWidth
      >
        <DialogTitle sx={{ pb: 1 }}>
          <Typography variant="h6">Deactivate Training Plan</Typography>
        </DialogTitle>
        <DialogContent>
          <Alert severity="warning" sx={{ mb: 2 }}>
            <Typography variant="body2" gutterBottom>
              <strong>What happens when you deactivate this plan:</strong>
            </Typography>
            <Typography variant="body2" component="div" sx={{ pl: 2 }}>
              • All planned workouts will disappear from your calendar
              <br />
              • Your completed activities remain unaffected
              <br />
              • You can reactivate this plan anytime
              <br />
              • The plan and its workouts are NOT deleted
            </Typography>
          </Alert>
          
          {selectedPlanForActivation && (
            <Box sx={{ 
              p: 2, 
              bgcolor: 'background.default', 
              borderRadius: 1,
              border: 1,
              borderColor: 'divider',
            }}>
              <Typography variant="body2" color="text.secondary" gutterBottom>
                Deactivating:
              </Typography>
              <Typography variant="body1" gutterBottom>
                <strong>{selectedPlanForActivation.name}</strong>
              </Typography>
              <Typography variant="body2" color="text.secondary">
                {selectedPlanForActivation.workout_count} workouts will be removed from calendar view
              </Typography>
            </Box>
          )}
        </DialogContent>
        <DialogActions sx={{ px: 3, pb: 2 }}>
          <Button onClick={handleCancelActivation} color="inherit">
            Cancel
          </Button>
          <Button 
            onClick={handleConfirmDeactivation} 
            variant="contained" 
            color="error"
          >
            Deactivate Plan
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default TrainingPlans;
