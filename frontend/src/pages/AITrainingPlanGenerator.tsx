import React, { useState, useEffect } from 'react';
import {
  Box,
  Button,
  Container,
  Stepper,
  Step,
  StepLabel,
  Typography,
  TextField,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Paper,
  Alert,
  AlertTitle,
  Chip,
  Stack,
} from '@mui/material';
import {
  ArrowBack as ArrowBackIcon,
  ContentCopy as ContentCopyIcon,
  OpenInNew as OpenInNewIcon,
  AutoAwesome as AutoAwesomeIcon,
  Check as CheckIcon,
} from '@mui/icons-material';
import { useNavigate } from 'react-router-dom';
import { useAuthStore } from '../store/authStore';
import api from '../services/api';
import { generateAIPrompt, PromptGenerationConfig, getTrainerStyles, getTrainerStyleDetails, TrainerStyle, TrainerStyleDetail } from '../services/aiTrainingPlan';

interface Event {
  id: number;
  name: string;
  event_date: string;
  target_distance?: string;
  goal_time?: string;
}

const AITrainingPlanGenerator: React.FC = () => {
  console.log('[AITrainingPlanGenerator] Component rendering');
  const navigate = useNavigate();
  const { user } = useAuthStore();
  console.log('[AITrainingPlanGenerator] User from store:', user);
  const [activeStep, setActiveStep] = useState(0);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [events, setEvents] = useState<Event[]>([]);
  const [generatedPrompt, setGeneratedPrompt] = useState<string>('');
  const [copied, setCopied] = useState(false);

  // Form state
  const [selectedEventId, setSelectedEventId] = useState<number | null>(null);
  const [eventName, setEventName] = useState('');
  const [eventDate, setEventDate] = useState('');
  const [eventDistance, setEventDistance] = useState('');
  const [goalTime, setGoalTime] = useState('');
  const [startDate, setStartDate] = useState('');
  const [trainingDaysPerWeek, setTrainingDaysPerWeek] = useState(5);
  const [preferredDays, setPreferredDays] = useState<string[]>(['monday', 'tuesday', 'thursday', 'saturday', 'sunday']);
  const [trainerStyles, setTrainerStyles] = useState<TrainerStyle[]>([]);
  const [selectedTrainerStyle, setSelectedTrainerStyle] = useState<string>('joe_friel');
  const [trainerStyleDetails, setTrainerStyleDetails] = useState<TrainerStyleDetail | null>(null);
  const [customTrainerInstructions, setCustomTrainerInstructions] = useState('');
  const [showTrainerDetails, setShowTrainerDetails] = useState(false);
  const [additionalNotes, setAdditionalNotes] = useState('');

  const steps = ['Select Event', 'Configure Plan', 'Choose Trainer Style', 'Get Prompt'];
  const weekDays = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday'];

  useEffect(() => {
    document.title = 'AI Training Plan Generator - Kinesis';
  }, []);

  useEffect(() => {
    console.log('[AITrainingPlanGenerator] useEffect triggered, user:', user);
    if (!user) {
      console.log('[AITrainingPlanGenerator] No user, redirecting to login');
      navigate('/login');
      return;
    }
    console.log('[AITrainingPlanGenerator] User authenticated, fetching events and trainer styles');
    fetchEvents();
    fetchTrainerStyles();
    
    // Set default start date to next Monday
    const nextMonday = getNextMonday();
    setStartDate(nextMonday.toISOString().split('T')[0]);
    console.log('[AITrainingPlanGenerator] Default start date set to:', nextMonday.toISOString().split('T')[0]);
  }, [user, navigate]);

  // Early return if no user to prevent flash of content
  if (!user) {
    console.log('[AITrainingPlanGenerator] Rendering null (no user)');
    return null;
  }

  const getNextMonday = () => {
    const today = new Date();
    const day = today.getDay();
    const daysUntilMonday = day === 0 ? 1 : day === 1 ? 7 : 8 - day;
    const nextMonday = new Date(today);
    nextMonday.setDate(today.getDate() + daysUntilMonday);
    return nextMonday;
  };

  const fetchEvents = async () => {
    try {
      console.log('[AITrainingPlanGenerator] Fetching events...');
      const response = await api.get('/events');
      console.log('[AITrainingPlanGenerator] Events loaded:', response.data?.length || 0, 'events');
      setEvents(response.data);
    } catch (err: any) {
      console.error('[AITrainingPlanGenerator] Failed to load events:', err);
    }
  };

  const fetchTrainerStyles = async () => {
    try {
      console.log('[AITrainingPlanGenerator] Fetching trainer styles from API...');
      const styles = await getTrainerStyles();
      console.log('[AITrainingPlanGenerator] Trainer styles API response:', styles);
      console.log('[AITrainingPlanGenerator] Trainer styles count:', styles?.length || 0);
      if (styles && Array.isArray(styles) && styles.length > 0) {
        setTrainerStyles(styles);
        console.log('[AITrainingPlanGenerator] ✅ Trainer styles set in state:', styles.length);
      } else {
        console.error('[AITrainingPlanGenerator] ❌ No trainer styles received or invalid format');
      }
    } catch (err: any) {
      console.error('[AITrainingPlanGenerator] ❌ Failed to load trainer styles:', err);
      console.error('[AITrainingPlanGenerator] Error details:', {
        message: err.message,
        response: err.response?.data,
        status: err.response?.status
      });
    }
  };

  const fetchTrainerStyleDetails = async (styleId: string) => {
    try {
      const details = await getTrainerStyleDetails(styleId);
      setTrainerStyleDetails(details);
    } catch (err: any) {
      console.error('[AITrainingPlanGenerator] Failed to load trainer style details:', err);
    }
  };

  const handleEventSelect = (eventId: number) => {
    setSelectedEventId(eventId);
    const event = events.find(e => e.id === eventId);
    if (event) {
      setEventName(event.name);
      setEventDate(event.event_date);
      setEventDistance(event.target_distance || '');
      setGoalTime(event.goal_time || '');
    }
  };

  const handleNext = async () => {
    if (activeStep === 3) {
      // Generate prompt
      setLoading(true);
      setError(null);
      
      try {
        const config: PromptGenerationConfig = {
          targetEventId: selectedEventId || undefined,
          eventName: eventName || undefined,
          eventDate: eventDate || undefined,
          eventDistance: eventDistance || undefined,
          goalTime: goalTime || undefined,
          startDate,
          trainingDaysPerWeek,
          preferredTrainingDays: preferredDays,
          trainerStyle: selectedTrainerStyle,
          customTrainerInstructions: customTrainerInstructions || undefined,
          additionalNotes: additionalNotes || undefined,
        };
        
        const response = await generateAIPrompt(config);
        setGeneratedPrompt(response.prompt);
        setActiveStep(activeStep + 1);
      } catch (err: any) {
        const errorDetail = err.response?.data?.detail;
        let errorMessage = 'Failed to generate prompt';
        
        if (typeof errorDetail === 'string') {
          errorMessage = errorDetail;
        } else if (errorDetail && typeof errorDetail === 'object') {
          errorMessage = JSON.stringify(errorDetail);
        } else if (err.message) {
          errorMessage = err.message;
        }
        
        setError(errorMessage);
      } finally {
        setLoading(false);
      }
    } else {
      setActiveStep(activeStep + 1);
    }
  };

  const handleBack = () => {
    setActiveStep(activeStep - 1);
  };

  const handleCopyPrompt = () => {
    navigator.clipboard.writeText(generatedPrompt);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const handleDayToggle = (day: string) => {
    if (preferredDays.includes(day)) {
      if (preferredDays.length > 3) {
        setPreferredDays(preferredDays.filter(d => d !== day));
      }
    } else {
      setPreferredDays([...preferredDays, day]);
    }
  };

  console.log('[AITrainingPlanGenerator] Rendering container, activeStep:', activeStep);

  return (
    <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
      <Button startIcon={<ArrowBackIcon />} onClick={() => navigate('/plans')} sx={{ mb: 2 }}>
        Back to Plans
      </Button>

      <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 3 }}>
        <AutoAwesomeIcon sx={{ fontSize: 40, color: 'primary.main' }} />
        <Typography variant="h4" component="h1">
          AI Training Plan Generator
        </Typography>
      </Box>

      {error && (
        <Alert severity="error" sx={{ mb: 2 }} onClose={() => setError(null)}>
          {error}
        </Alert>
      )}

      <Paper sx={{ p: 3 }}>
        <Stepper activeStep={activeStep} sx={{ mb: 4 }}>
          {steps.map((label) => (
            <Step key={label}>
              <StepLabel>{label}</StepLabel>
            </Step>
          ))}
        </Stepper>

        {/* Step 1: Select Event */}
        {activeStep === 0 && (
          <Box>
            <Typography variant="h6" gutterBottom>
              Select Target Event
            </Typography>
            <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
              Choose an existing event or enter new event details
            </Typography>

            {events.length > 0 && (
              <FormControl fullWidth sx={{ mb: 3 }}>
                <InputLabel>Select Existing Event</InputLabel>
                <Select
                  value={selectedEventId || ''}
                  label="Select Existing Event"
                  onChange={(e) => handleEventSelect(e.target.value as number)}
                >
                  <MenuItem value="">
                    <em>Create new event details</em>
                  </MenuItem>
                  {events.map((event) => (
                    <MenuItem key={event.id} value={event.id}>
                      {event.name} - {new Date(event.event_date).toLocaleDateString()}
                    </MenuItem>
                  ))}
                </Select>
              </FormControl>
            )}

            <TextField
              label="Event Name"
              fullWidth
              value={eventName}
              onChange={(e) => setEventName(e.target.value)}
              sx={{ mb: 2 }}
              required
            />

            <TextField
              label="Event Date"
              type="date"
              fullWidth
              InputLabelProps={{ shrink: true }}
              value={eventDate}
              onChange={(e) => setEventDate(e.target.value)}
              sx={{ mb: 2 }}
              required
            />

            <TextField
              label="Target Distance"
              fullWidth
              placeholder="e.g., Marathon, Half Marathon, 10K"
              value={eventDistance}
              onChange={(e) => setEventDistance(e.target.value)}
              sx={{ mb: 2 }}
            />

            <TextField
              label="Goal Time"
              fullWidth
              placeholder="e.g., 3:30:00"
              value={goalTime}
              onChange={(e) => setGoalTime(e.target.value)}
              sx={{ mb: 2 }}
            />
          </Box>
        )}

        {/* Step 2: Configure Plan */}
        {activeStep === 1 && (
          <Box>
            <Typography variant="h6" gutterBottom>
              Configure Training Plan
            </Typography>
            <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
              Set your training preferences and constraints
            </Typography>

            <TextField
              label="Plan Start Date"
              type="date"
              fullWidth
              InputLabelProps={{ shrink: true }}
              value={startDate}
              onChange={(e) => setStartDate(e.target.value)}
              sx={{ mb: 3 }}
              required
            />

            <FormControl fullWidth sx={{ mb: 3 }}>
              <InputLabel>Training Days Per Week</InputLabel>
              <Select
                value={trainingDaysPerWeek}
                label="Training Days Per Week"
                onChange={(e) => setTrainingDaysPerWeek(e.target.value as number)}
              >
                {[3, 4, 5, 6, 7].map((days) => (
                  <MenuItem key={days} value={days}>{days} days</MenuItem>
                ))}
              </Select>
            </FormControl>

            <Typography variant="subtitle2" gutterBottom>
              Preferred Training Days
            </Typography>
            <Stack direction="row" spacing={1} flexWrap="wrap" sx={{ mb: 3, gap: 1 }}>
              {weekDays.map((day) => (
                <Chip
                  key={day}
                  label={day.charAt(0).toUpperCase() + day.slice(1)}
                  color={preferredDays.includes(day) ? 'primary' : 'default'}
                  onClick={() => handleDayToggle(day)}
                  sx={{ cursor: 'pointer' }}
                />
              ))}
            </Stack>
            <Typography variant="caption" color="text.secondary" sx={{ mb: 3, display: 'block' }}>
              Select at least 3 days. AI will distribute workouts across these days.
            </Typography>

            <TextField
              label="Additional Notes/Constraints"
              fullWidth
              multiline
              rows={4}
              placeholder="e.g., I have a gym membership, prefer morning runs, avoid hills..."
              value={additionalNotes}
              onChange={(e) => setAdditionalNotes(e.target.value)}
            />
          </Box>
        )}

        {/* Step 3: Choose Trainer Style */}
        {activeStep === 2 && (
          <Box>
            <Typography variant="h6" gutterBottom>
              Choose Your Trainer Style
            </Typography>
            <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
              Select a coaching methodology that matches your training philosophy
            </Typography>

            <FormControl fullWidth sx={{ mb: 3 }}>
              <InputLabel>Trainer Style</InputLabel>
              <Select
                value={selectedTrainerStyle}
                label="Trainer Style"
                onChange={(e) => {
                  setSelectedTrainerStyle(e.target.value);
                  fetchTrainerStyleDetails(e.target.value);
                }}
              >
                {trainerStyles.map((trainer) => (
                  <MenuItem key={trainer.id} value={trainer.id}>
                    <Box>
                      <Typography variant="body1">{trainer.name}</Typography>
                      <Typography variant="caption" color="text.secondary">{trainer.tagline}</Typography>
                    </Box>
                  </MenuItem>
                ))}
              </Select>
            </FormControl>

            {trainerStyles.find(t => t.id === selectedTrainerStyle) && (
              <Alert severity="info" sx={{ mb: 3 }}>
                <AlertTitle>
                  {trainerStyles.find(t => t.id === selectedTrainerStyle)?.name}
                </AlertTitle>
                {trainerStyles.find(t => t.id === selectedTrainerStyle)?.description}
              </Alert>
            )}

            <Button
              variant="outlined"
              size="small"
              onClick={() => {
                setShowTrainerDetails(!showTrainerDetails);
                if (!trainerStyleDetails && !showTrainerDetails) {
                  fetchTrainerStyleDetails(selectedTrainerStyle);
                }
              }}
              sx={{ mb: 2 }}
            >
              {showTrainerDetails ? 'Hide' : 'Show'} Detailed Methodology
            </Button>

            {showTrainerDetails && trainerStyleDetails && (
              <Paper sx={{ p: 2, bgcolor: 'grey.50', mb: 3, maxHeight: 300, overflow: 'auto' }}>
                <Typography variant="subtitle2" gutterBottom>Training Philosophy:</Typography>
                <Typography variant="body2" component="pre" sx={{ whiteSpace: 'pre-wrap', mb: 2, fontSize: '0.85rem' }}>
                  {trainerStyleDetails.philosophy}
                </Typography>
                
                <Typography variant="subtitle2" gutterBottom>Key Workouts:</Typography>
                <Box component="ul" sx={{ pl: 2, mb: 2 }}>
                  {trainerStyleDetails.key_workouts.map((workout, idx) => (
                    <Typography component="li" variant="body2" key={idx} sx={{ fontSize: '0.85rem' }}>
                      {workout}
                    </Typography>
                  ))}
                </Box>
              </Paper>
            )}

            <Typography variant="subtitle2" gutterBottom>
              Custom Training Instructions (Optional)
            </Typography>
            <Typography variant="caption" color="text.secondary" sx={{ mb: 1, display: 'block' }}>
              Add your own training philosophy or modifications. This extends the selected trainer style.
            </Typography>
            <TextField
              fullWidth
              multiline
              rows={6}
              placeholder="e.g., Focus more on hill training, prefer shorter high-intensity intervals, include swimming-specific drills..."
              value={customTrainerInstructions}
              onChange={(e) => setCustomTrainerInstructions(e.target.value)}
              sx={{ mb: 2 }}
            />
            <Typography variant="caption" color="text.secondary">
              💡 Tip: Your custom instructions will be applied IN ADDITION TO the selected trainer methodology.
            </Typography>
          </Box>
        )}

        {/* Step 4: Get Prompt */}
        {activeStep === 3 && !generatedPrompt && (
          <Box sx={{ textAlign: 'center', py: 4 }}>
            <Typography variant="h6" gutterBottom>
              Ready to Generate Prompt
            </Typography>
            <Typography variant="body2" color="text.secondary">
              Click "Generate Prompt" to create your personalized AI training plan prompt
            </Typography>
          </Box>
        )}

        {/* Step 5: Show Prompt */}
        {activeStep === 4 && (
          <Box>
            <Alert severity="info" sx={{ mb: 3 }}>
              <AlertTitle>How to use this prompt</AlertTitle>
              <ol style={{ margin: 0, paddingLeft: 20 }}>
                <li>Copy the prompt below</li>
                <li>Open ChatGPT or Claude AI</li>
                <li>Paste and send the prompt</li>
                <li>Wait for AI response (JSON format)</li>
                <li>Copy the JSON and go to Plans → Import AI Plan</li>
              </ol>
            </Alert>

            <Paper sx={{ p: 2, bgcolor: 'grey.100', maxHeight: 400, overflow: 'auto', mb: 2 }}>
              <Typography
                variant="body2"
                component="pre"
                sx={{
                  fontFamily: 'monospace',
                  whiteSpace: 'pre-wrap',
                  wordBreak: 'break-word',
                  fontSize: '0.8rem',
                }}
              >
                {generatedPrompt}
              </Typography>
            </Paper>

            <Stack direction="row" spacing={2}>
              <Button
                variant="contained"
                startIcon={copied ? <CheckIcon /> : <ContentCopyIcon />}
                onClick={handleCopyPrompt}
                color={copied ? 'success' : 'primary'}
              >
                {copied ? 'Copied!' : 'Copy to Clipboard'}
              </Button>
              <Button
                variant="outlined"
                startIcon={<OpenInNewIcon />}
                onClick={() => window.open('https://chat.openai.com', '_blank')}
              >
                Open ChatGPT
              </Button>
              <Button
                variant="outlined"
                startIcon={<OpenInNewIcon />}
                onClick={() => window.open('https://claude.ai', '_blank')}
              >
                Open Claude
              </Button>
            </Stack>

            <Alert severity="success" sx={{ mt: 3 }}>
              <AlertTitle>Next Steps</AlertTitle>
              Once you have the JSON response from the AI:
              <ul style={{ margin: '8px 0 0 0', paddingLeft: 20 }}>
                <li>Go to Plans tab</li>
                <li>Click "Import AI Plan"</li>
                <li>Upload the JSON file</li>
              </ul>
            </Alert>
          </Box>
        )}

        {/* Navigation Buttons */}
        <Box sx={{ display: 'flex', justifyContent: 'space-between', mt: 4 }}>
          <Button onClick={handleBack} disabled={activeStep === 0 || activeStep === 4}>
            Back
          </Button>
          <Box sx={{ display: 'flex', gap: 2 }}>
            {activeStep === 4 ? (
              <Button variant="contained" onClick={() => navigate('/plans')}>
                Go to Plans
              </Button>
            ) : (
              <Button
                variant="contained"
                onClick={handleNext}
                disabled={
                  loading ||
                  (activeStep === 0 && (!eventName || !eventDate)) ||
                  (activeStep === 1 && (!startDate || preferredDays.length < 3))
                }
              >
                {activeStep === 3 ? 'Generate Prompt' : 'Next'}
              </Button>
            )}
          </Box>
        </Box>
      </Paper>
    </Container>
  );
};

export default AITrainingPlanGenerator;
