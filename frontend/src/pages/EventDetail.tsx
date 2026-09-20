import React, { useEffect, useState } from 'react';
import {
  Box,
  Button,
  Card,
  CardContent,
  Container,
  Typography,
  Chip,
  Grid,
  TextField,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Alert,
  Divider,
  Stack,
} from '@mui/material';
import {
  ArrowBack as ArrowBackIcon,
  Edit as EditIcon,
  Delete as DeleteIcon,
  Event as EventIcon,
  LocationOn as LocationIcon,
  Timer as TimerIcon,
  EmojiEvents as TrophyIcon,
  Check as CheckIcon,
} from '@mui/icons-material';
import { useNavigate, useParams } from 'react-router-dom';
import { useAuthStore } from '../store/authStore';
import api from '../services/api';

interface Event {
  id: number;
  name: string;
  event_date: string;
  event_type: string;
  location?: string;
  description?: string;
  goal_time?: string;
  target_distance?: string;
  registration_link?: string;
  cost?: string;
  notes?: string;
  is_completed: boolean;
  actual_time?: string;
  actual_result?: string;
  created_at: string;
  updated_at: string;
}

const EventDetail: React.FC = () => {
  const navigate = useNavigate();
  const { eventId } = useParams<{ eventId: string }>();
  const { user } = useAuthStore();
  const [event, setEvent] = useState<Event | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [editDialogOpen, setEditDialogOpen] = useState(false);
  const [formData, setFormData] = useState({
    name: '',
    event_date: '',
    event_type: 'race',
    location: '',
    description: '',
    goal_time: '',
    target_distance: '',
    registration_link: '',
    cost: '',
    notes: '',
    is_completed: false,
    actual_time: '',
    actual_result: '',
  });

  useEffect(() => {
    document.title = 'Event Details - Kinesis';
  }, []);

  useEffect(() => {
    if (!user) {
      navigate('/login');
      return;
    }
    fetchEvent();
  }, [user, navigate, eventId]);

  const fetchEvent = async () => {
    try {
      setLoading(true);
      const response = await api.get(`/events/${eventId}`);
      setEvent(response.data);
      setFormData({
        name: response.data.name,
        event_date: response.data.event_date,
        event_type: response.data.event_type,
        location: response.data.location || '',
        description: response.data.description || '',
        goal_time: response.data.goal_time || '',
        target_distance: response.data.target_distance || '',
        registration_link: response.data.registration_link || '',
        cost: response.data.cost || '',
        notes: response.data.notes || '',
        is_completed: response.data.is_completed,
        actual_time: response.data.actual_time || '',
        actual_result: response.data.actual_result || '',
      });
      setError(null);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to load event');
    } finally {
      setLoading(false);
    }
  };

  const handleUpdateEvent = async () => {
    try {
      await api.put(`/events/${eventId}`, formData);
      setEditDialogOpen(false);
      fetchEvent();
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to update event');
    }
  };

  const handleDeleteEvent = async () => {
    if (!confirm('Are you sure you want to delete this event?')) {
      return;
    }
    try {
      await api.delete(`/events/${eventId}`);
      navigate('/plans');
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to delete event');
    }
  };

  const handleMarkComplete = async () => {
    try {
      await api.put(`/events/${eventId}`, { is_completed: true });
      fetchEvent();
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to mark event as complete');
    }
  };

  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', {
      weekday: 'long',
      year: 'numeric',
      month: 'long',
      day: 'numeric',
    });
  };

  if (!user) {
    return null;
  }

  if (loading) {
    return (
      <Container maxWidth="md" sx={{ mt: 4 }}>
        <Typography>Loading event...</Typography>
      </Container>
    );
  }

  if (!event) {
    return (
      <Container maxWidth="md" sx={{ mt: 4 }}>
        <Alert severity="error">Event not found</Alert>
        <Button startIcon={<ArrowBackIcon />} onClick={() => navigate('/plans')} sx={{ mt: 2 }}>
          Back to Plans
        </Button>
      </Container>
    );
  }

  return (
    <Container maxWidth="md" sx={{ mt: 4, mb: 4 }}>
      <Button startIcon={<ArrowBackIcon />} onClick={() => navigate('/plans')} sx={{ mb: 2 }}>
        Back to Plans & Events
      </Button>

      {error && (
        <Alert severity="error" sx={{ mb: 2 }} onClose={() => setError(null)}>
          {error}
        </Alert>
      )}

      <Card>
        <CardContent>
          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', mb: 3 }}>
            <Box>
              <Typography variant="h4" component="h1" gutterBottom>
                {event.name}
              </Typography>
              <Box sx={{ display: 'flex', gap: 1, alignItems: 'center', mb: 2 }}>
                <Chip label={event.event_type} color="primary" size="small" />
                {event.is_completed && <Chip label="Completed" color="success" size="small" icon={<CheckIcon />} />}
              </Box>
            </Box>
            <Box sx={{ display: 'flex', gap: 1 }}>
              <Button variant="outlined" startIcon={<EditIcon />} onClick={() => setEditDialogOpen(true)}>
                Edit
              </Button>
              <Button variant="outlined" color="error" startIcon={<DeleteIcon />} onClick={handleDeleteEvent}>
                Delete
              </Button>
            </Box>
          </Box>

          <Divider sx={{ mb: 3 }} />

          <Grid container spacing={3}>
            <Grid item xs={12}>
              <Stack direction="row" spacing={1} alignItems="center">
                <EventIcon color="action" />
                <Typography variant="body1" color="text.secondary">
                  Date:
                </Typography>
                <Typography variant="body1">{formatDate(event.event_date)}</Typography>
              </Stack>
            </Grid>

            {event.location && (
              <Grid item xs={12}>
                <Stack direction="row" spacing={1} alignItems="center">
                  <LocationIcon color="action" />
                  <Typography variant="body1" color="text.secondary">
                    Location:
                  </Typography>
                  <Typography variant="body1">{event.location}</Typography>
                </Stack>
              </Grid>
            )}

            {event.target_distance && (
              <Grid item xs={12} sm={6}>
                <Stack direction="row" spacing={1} alignItems="center">
                  <TrophyIcon color="action" />
                  <Typography variant="body1" color="text.secondary">
                    Distance:
                  </Typography>
                  <Typography variant="body1">{event.target_distance}</Typography>
                </Stack>
              </Grid>
            )}

            {event.goal_time && (
              <Grid item xs={12} sm={6}>
                <Stack direction="row" spacing={1} alignItems="center">
                  <TimerIcon color="action" />
                  <Typography variant="body1" color="text.secondary">
                    Goal Time:
                  </Typography>
                  <Typography variant="body1">{event.goal_time}</Typography>
                </Stack>
              </Grid>
            )}

            {event.cost && (
              <Grid item xs={12}>
                <Typography variant="body1" color="text.secondary">
                  Cost: {event.cost}
                </Typography>
              </Grid>
            )}

            {event.registration_link && (
              <Grid item xs={12}>
                <Typography variant="body1" color="text.secondary">
                  Registration:{' '}
                  <a href={event.registration_link} target="_blank" rel="noopener noreferrer">
                    {event.registration_link}
                  </a>
                </Typography>
              </Grid>
            )}

            {event.description && (
              <Grid item xs={12}>
                <Typography variant="body1" color="text.secondary" gutterBottom>
                  Description:
                </Typography>
                <Typography variant="body1">{event.description}</Typography>
              </Grid>
            )}

            {event.notes && (
              <Grid item xs={12}>
                <Typography variant="body1" color="text.secondary" gutterBottom>
                  Notes:
                </Typography>
                <Typography variant="body1">{event.notes}</Typography>
              </Grid>
            )}

            {event.is_completed && (
              <>
                <Grid item xs={12}>
                  <Divider />
                  <Typography variant="h6" sx={{ mt: 2, mb: 2 }}>
                    Results
                  </Typography>
                </Grid>
                {event.actual_time && (
                  <Grid item xs={12} sm={6}>
                    <Typography variant="body1" color="text.secondary">
                      Finish Time:
                    </Typography>
                    <Typography variant="h6">{event.actual_time}</Typography>
                  </Grid>
                )}
                {event.actual_result && (
                  <Grid item xs={12} sm={6}>
                    <Typography variant="body1" color="text.secondary">
                      Result:
                    </Typography>
                    <Typography variant="h6">{event.actual_result}</Typography>
                  </Grid>
                )}
              </>
            )}
          </Grid>

          {!event.is_completed && (
            <Box sx={{ mt: 3 }}>
              <Button variant="contained" startIcon={<CheckIcon />} onClick={handleMarkComplete}>
                Mark as Completed
              </Button>
            </Box>
          )}
        </CardContent>
      </Card>

      {/* Edit Event Dialog */}
      <Dialog open={editDialogOpen} onClose={() => setEditDialogOpen(false)} maxWidth="sm" fullWidth>
        <DialogTitle>Edit Event</DialogTitle>
        <DialogContent>
          <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2, mt: 2 }}>
            <TextField
              label="Event Name"
              fullWidth
              value={formData.name}
              onChange={(e) => setFormData({ ...formData, name: e.target.value })}
              required
            />
            <TextField
              label="Event Date"
              type="date"
              fullWidth
              InputLabelProps={{ shrink: true }}
              value={formData.event_date}
              onChange={(e) => setFormData({ ...formData, event_date: e.target.value })}
              required
            />
            <TextField
              label="Location"
              fullWidth
              value={formData.location}
              onChange={(e) => setFormData({ ...formData, location: e.target.value })}
            />
            <TextField
              label="Target Distance"
              fullWidth
              value={formData.target_distance}
              onChange={(e) => setFormData({ ...formData, target_distance: e.target.value })}
            />
            <TextField
              label="Goal Time"
              fullWidth
              value={formData.goal_time}
              onChange={(e) => setFormData({ ...formData, goal_time: e.target.value })}
            />
            <TextField
              label="Cost"
              fullWidth
              value={formData.cost}
              onChange={(e) => setFormData({ ...formData, cost: e.target.value })}
            />
            <TextField
              label="Registration Link"
              fullWidth
              value={formData.registration_link}
              onChange={(e) => setFormData({ ...formData, registration_link: e.target.value })}
            />
            <TextField
              label="Description"
              fullWidth
              multiline
              rows={3}
              value={formData.description}
              onChange={(e) => setFormData({ ...formData, description: e.target.value })}
            />
            <TextField
              label="Notes"
              fullWidth
              multiline
              rows={3}
              value={formData.notes}
              onChange={(e) => setFormData({ ...formData, notes: e.target.value })}
            />
            {formData.is_completed && (
              <>
                <TextField
                  label="Actual Time"
                  fullWidth
                  value={formData.actual_time}
                  onChange={(e) => setFormData({ ...formData, actual_time: e.target.value })}
                />
                <TextField
                  label="Result"
                  fullWidth
                  value={formData.actual_result}
                  onChange={(e) => setFormData({ ...formData, actual_result: e.target.value })}
                />
              </>
            )}
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setEditDialogOpen(false)}>Cancel</Button>
          <Button onClick={handleUpdateEvent} variant="contained" disabled={!formData.name || !formData.event_date}>
            Save Changes
          </Button>
        </DialogActions>
      </Dialog>
    </Container>
  );
};

export default EventDetail;
