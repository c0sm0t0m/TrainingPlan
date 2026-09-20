import React, { useEffect, useState } from 'react';
import {
  Box,
  Button,
  Card,
  CardContent,
  Container,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  Typography,
  Chip,
  MenuItem,
  Select,
  FormControl,
  InputLabel,
  IconButton,
  Alert,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
} from '@mui/material';
import {
  Add as AddIcon,
  Delete as DeleteIcon,
  ArrowBack as ArrowBackIcon,
  CheckCircle as CheckCircleIcon,
  Upload as UploadIcon,
  FitnessCenter as FitnessCenterIcon,
} from '@mui/icons-material';
import { useNavigate, useParams } from 'react-router-dom';
import { useAuthStore } from '../store/authStore';
import api from '../services/api';
import Breadcrumbs from '../components/Breadcrumbs';

interface TrainingPlan {
  id: number;
  name: string;
  description?: string;
  start_date: string;
  end_date: string;
  sport_type: string;
  is_active: boolean;
  workouts: Workout[];
  created_at: string;
  updated_at: string;
}

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
  actual_duration_minutes?: number;
  actual_distance_km?: number;
  notes?: string;
}

const sportTypes = [
  { value: 'running', label: 'Running' },
  { value: 'cycling', label: 'Cycling' },
  { value: 'swimming', label: 'Swimming' },
  { value: 'triathlon', label: 'Triathlon' },
  { value: 'gym', label: 'Gym' },
  { value: 'other', label: 'Other' },
];

const workoutTypes = [
  { value: 'easy', label: 'Easy' },
  { value: 'tempo', label: 'Tempo' },
  { value: 'interval', label: 'Interval' },
  { value: 'long', label: 'Long' },
  { value: 'recovery', label: 'Recovery' },
  { value: 'race', label: 'Race' },
  { value: 'brick', label: 'Brick' },
  { value: 'strength', label: 'Strength' },
];

const intensityZones = [
  { value: 'zone1', label: 'Zone 1 (Recovery)' },
  { value: 'zone2', label: 'Zone 2 (Endurance)' },
  { value: 'zone3', label: 'Zone 3 (Tempo)' },
  { value: 'zone4', label: 'Zone 4 (Threshold)' },
  { value: 'zone5', label: 'Zone 5 (VO2 Max)' },
];

const PlanDetail: React.FC = () => {
  const navigate = useNavigate();
  const { planId } = useParams<{ planId: string }>();
  const { user } = useAuthStore();
  const [plan, setPlan] = useState<TrainingPlan | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [dialogOpen, setDialogOpen] = useState(false);
  const [importDialogOpen, setImportDialogOpen] = useState(false);
  const [xmlContent, setXmlContent] = useState('');
  const [importDate, setImportDate] = useState('');
  const [formData, setFormData] = useState({
    date: '',
    sport_type: 'running',
    workout_type: 'easy',
    title: '',
    description: '',
    duration_minutes: '',
    distance_km: '',
    intensity_zone: 'zone2',
  });

  useEffect(() => {
    if (plan) {
      document.title = `${plan.name} - Kinesis`;
    }
  }, [plan]);

  useEffect(() => {
    if (!user) {
      navigate('/login');
      return;
    }
    if (planId) {
      fetchPlan();
    }
  }, [user, navigate, planId]);

  const fetchPlan = async () => {
    try {
      setLoading(true);
      const response = await api.get(`/training-plans/${planId}`);
      setPlan(response.data);
      setError(null);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to load training plan');
    } finally {
      setLoading(false);
    }
  };

  const handleCreateWorkout = async () => {
    try {
      const workoutData = {
        ...formData,
        duration_minutes: formData.duration_minutes ? parseInt(formData.duration_minutes) : undefined,
        distance_km: formData.distance_km ? parseFloat(formData.distance_km) : undefined,
      };
      await api.post(`/training-plans/${planId}/workouts`, workoutData);
      setDialogOpen(false);
      setFormData({
        date: '',
        sport_type: 'running',
        workout_type: 'easy',
        title: '',
        description: '',
        duration_minutes: '',
        distance_km: '',
        intensity_zone: 'zone2',
      });
      fetchPlan();
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to create workout');
    }
  };

  const handleDeleteWorkout = async (workoutId: number) => {
    if (!confirm('Are you sure you want to delete this workout?')) {
      return;
    }
    try {
      await api.delete(`/training-plans/${planId}/workouts/${workoutId}`);
      fetchPlan();
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to delete workout');
    }
  };

  const handleToggleComplete = async (workout: Workout) => {
    try {
      await api.put(`/training-plans/${planId}/workouts/${workout.id}`, {
        is_completed: !workout.is_completed,
      });
      fetchPlan();
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to update workout');
    }
  };

  const handleImportXML = async () => {
    if (!importDate || !xmlContent) {
      setError('Please provide both date and XML content');
      return;
    }

    try {
      await api.post(`/training-plans/${planId}/workouts/import-xml`, {
        workout_date: importDate,
        xml_content: xmlContent,
      });
      setImportDialogOpen(false);
      setXmlContent('');
      setImportDate('');
      fetchPlan();
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to import workout from XML');
    }
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString();
  };

  if (!user) {
    return null;
  }

  if (loading) {
    return (
      <Container maxWidth="lg" sx={{ mt: 4 }}>
        <Typography>Loading...</Typography>
      </Container>
    );
  }

  if (!plan) {
    return (
      <Container maxWidth="lg" sx={{ mt: 4 }}>
        <Alert severity="error">Training plan not found</Alert>
      </Container>
    );
  }

  return (
    <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
      <Breadcrumbs
        items={[
          { label: 'Home', path: '/dashboard' },
          { label: 'Training Plans', path: '/plans' },
          { label: plan.name, icon: <FitnessCenterIcon fontSize="small" /> },
        ]}
      />
      
      <Box sx={{ mb: 3 }}>
        <Button startIcon={<ArrowBackIcon />} onClick={() => navigate('/plans')}>
          Back to Plans
        </Button>
      </Box>

      {error && (
        <Alert severity="error" sx={{ mb: 2 }} onClose={() => setError(null)}>
          {error}
        </Alert>
      )}

      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', mb: 2 }}>
            <Typography variant="h4" component="h1">
              {plan.name}
            </Typography>
            <Chip label={plan.sport_type} color="primary" />
          </Box>
          {plan.description && (
            <Typography variant="body1" color="text.secondary" sx={{ mb: 2 }}>
              {plan.description}
            </Typography>
          )}
          <Typography variant="body2" color="text.secondary">
            {formatDate(plan.start_date)} - {formatDate(plan.end_date)}
          </Typography>
        </CardContent>
      </Card>

      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
        <Typography variant="h5">Workouts ({plan.workouts.length})</Typography>
        <Box sx={{ display: 'flex', gap: 1 }}>
          <Button variant="outlined" startIcon={<UploadIcon />} onClick={() => setImportDialogOpen(true)}>
            Import XML
          </Button>
          <Button variant="contained" startIcon={<AddIcon />} onClick={() => setDialogOpen(true)}>
            Add Workout
          </Button>
        </Box>
      </Box>

      {plan.workouts.length === 0 ? (
        <Card>
          <CardContent>
            <Typography variant="body1" align="center" color="text.secondary">
              No workouts scheduled yet. Add your first workout!
            </Typography>
          </CardContent>
        </Card>
      ) : (
        <TableContainer component={Paper}>
          <Table>
            <TableHead>
              <TableRow>
                <TableCell>Date</TableCell>
                <TableCell>Title</TableCell>
                <TableCell>Type</TableCell>
                <TableCell>Duration</TableCell>
                <TableCell>Distance</TableCell>
                <TableCell>Status</TableCell>
                <TableCell>Actions</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {plan.workouts
                .sort((a, b) => new Date(a.date).getTime() - new Date(b.date).getTime())
                .map((workout) => (
                  <TableRow key={workout.id}>
                    <TableCell>{formatDate(workout.date)}</TableCell>
                    <TableCell>
                      <Typography variant="body2" fontWeight="medium">
                        {workout.title}
                      </Typography>
                      {workout.description && (
                        <Typography variant="caption" color="text.secondary">
                          {workout.description}
                        </Typography>
                      )}
                    </TableCell>
                    <TableCell>
                      <Chip label={workout.workout_type} size="small" />
                    </TableCell>
                    <TableCell>{workout.duration_minutes ? `${workout.duration_minutes} min` : '-'}</TableCell>
                    <TableCell>{workout.distance_km ? `${workout.distance_km} km` : '-'}</TableCell>
                    <TableCell>
                      <IconButton
                        size="small"
                        onClick={() => handleToggleComplete(workout)}
                        color={workout.is_completed ? 'success' : 'default'}
                      >
                        <CheckCircleIcon />
                      </IconButton>
                    </TableCell>
                    <TableCell>
                      <IconButton size="small" color="error" onClick={() => handleDeleteWorkout(workout.id)}>
                        <DeleteIcon />
                      </IconButton>
                    </TableCell>
                  </TableRow>
                ))}
            </TableBody>
          </Table>
        </TableContainer>
      )}

      {/* Create Workout Dialog */}
      <Dialog open={dialogOpen} onClose={() => setDialogOpen(false)} maxWidth="sm" fullWidth>
        <DialogTitle>Add Workout</DialogTitle>
        <DialogContent>
          <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2, mt: 2 }}>
            <TextField
              label="Date"
              type="date"
              fullWidth
              InputLabelProps={{ shrink: true }}
              value={formData.date}
              onChange={(e) => setFormData({ ...formData, date: e.target.value })}
              required
            />
            <TextField
              label="Title"
              fullWidth
              value={formData.title}
              onChange={(e) => setFormData({ ...formData, title: e.target.value })}
              required
            />
            <TextField
              label="Description"
              fullWidth
              multiline
              rows={2}
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
            <FormControl fullWidth>
              <InputLabel>Workout Type</InputLabel>
              <Select
                value={formData.workout_type}
                label="Workout Type"
                onChange={(e) => setFormData({ ...formData, workout_type: e.target.value })}
              >
                {workoutTypes.map((type) => (
                  <MenuItem key={type.value} value={type.value}>
                    {type.label}
                  </MenuItem>
                ))}
              </Select>
            </FormControl>
            <TextField
              label="Duration (minutes)"
              type="number"
              fullWidth
              value={formData.duration_minutes}
              onChange={(e) => setFormData({ ...formData, duration_minutes: e.target.value })}
            />
            <TextField
              label="Distance (km)"
              type="number"
              fullWidth
              inputProps={{ step: '0.1' }}
              value={formData.distance_km}
              onChange={(e) => setFormData({ ...formData, distance_km: e.target.value })}
            />
            <FormControl fullWidth>
              <InputLabel>Intensity Zone</InputLabel>
              <Select
                value={formData.intensity_zone}
                label="Intensity Zone"
                onChange={(e) => setFormData({ ...formData, intensity_zone: e.target.value })}
              >
                {intensityZones.map((zone) => (
                  <MenuItem key={zone.value} value={zone.value}>
                    {zone.label}
                  </MenuItem>
                ))}
              </Select>
            </FormControl>
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setDialogOpen(false)}>Cancel</Button>
          <Button
            onClick={handleCreateWorkout}
            variant="contained"
            disabled={!formData.title || !formData.date}
          >
            Add Workout
          </Button>
        </DialogActions>
      </Dialog>

      {/* Import XML Dialog */}
      <Dialog open={importDialogOpen} onClose={() => setImportDialogOpen(false)} maxWidth="md" fullWidth>
        <DialogTitle>Import Workout from XML</DialogTitle>
        <DialogContent>
          <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2, mt: 2 }}>
            <Alert severity="info">
              Paste XML workout definition from ChatGPT or other sources. The workout will be parsed and added to your plan.
            </Alert>
            <TextField
              label="Workout Date"
              type="date"
              fullWidth
              InputLabelProps={{ shrink: true }}
              value={importDate}
              onChange={(e) => setImportDate(e.target.value)}
              required
            />
            <TextField
              label="XML Content"
              fullWidth
              multiline
              rows={12}
              value={xmlContent}
              onChange={(e) => setXmlContent(e.target.value)}
              placeholder={`<workout_file>
  <author>ChatGPT</author>
  <name>Interval Training</name>
  <sportType>Run</sportType>
  <workout>
    <Warmup duration="600" pace="5:30" />
    <Repeat count="6">
      <Interval duration="120" pace="4:00" />
      <Rest duration="90" pace="5:30" />
    </Repeat>
    <Cooldown duration="600" pace="5:30" />
  </workout>
</workout_file>`}
              required
              helperText="Supports: Warmup, Cooldown, Interval, Rest, Repeat blocks"
            />
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setImportDialogOpen(false)}>Cancel</Button>
          <Button
            onClick={handleImportXML}
            variant="contained"
            disabled={!importDate || !xmlContent}
          >
            Import Workout
          </Button>
        </DialogActions>
      </Dialog>
    </Container>
  );
};

export default PlanDetail;