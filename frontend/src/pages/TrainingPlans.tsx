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
} from '@mui/material';
import { Add as AddIcon, Edit as EditIcon, Delete as DeleteIcon } from '@mui/icons-material';
import { useNavigate } from 'react-router-dom';
import { useAuthStore } from '../store/authStore';
import api from '../services/api';

interface TrainingPlan {
  id: number;
  name: string;
  description?: string;
  start_date: string;
  end_date: string;
  sport_type: string;
  is_active: boolean;
  workout_count: number;
  completed_count: number;
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
  const [plans, setPlans] = useState<TrainingPlan[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [dialogOpen, setDialogOpen] = useState(false);
  const [formData, setFormData] = useState({
    name: '',
    description: '',
    start_date: '',
    end_date: '',
    sport_type: 'running',
  });

  useEffect(() => {
    document.title = 'Training Plans - TrainingPlan';
  }, []);

  useEffect(() => {
    if (!user) {
      navigate('/login');
      return;
    }
    fetchPlans();
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

  return (
    <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Typography variant="h4" component="h1">
          Training Plans
        </Typography>
        <Button
          variant="contained"
          startIcon={<AddIcon />}
          onClick={() => setDialogOpen(true)}
        >
          New Plan
        </Button>
      </Box>

      {error && (
        <Alert severity="error" sx={{ mb: 2 }} onClose={() => setError(null)}>
          {error}
        </Alert>
      )}

      {loading ? (
        <Typography>Loading...</Typography>
      ) : plans.length === 0 ? (
        <Card>
          <CardContent>
            <Typography variant="h6" align="center" color="text.secondary">
              No training plans yet. Create your first plan to get started!
            </Typography>
          </CardContent>
        </Card>
      ) : (
        <Grid container spacing={3}>
          {plans.map((plan) => (
            <Grid item xs={12} md={6} key={plan.id}>
              <Card>
                <CardContent>
                  <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', mb: 2 }}>
                    <Typography variant="h5" component="h2">
                      {plan.name}
                    </Typography>
                    <Chip
                      label={plan.sport_type}
                      color={getSportColor(plan.sport_type)}
                      size="small"
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
                  <Box sx={{ display: 'flex', gap: 2 }}>
                    <Typography variant="body2">
                      <strong>{plan.workout_count}</strong> workouts
                    </Typography>
                    <Typography variant="body2">
                      <strong>{plan.completed_count}</strong> completed
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
    </Container>
  );
};

export default TrainingPlans;
