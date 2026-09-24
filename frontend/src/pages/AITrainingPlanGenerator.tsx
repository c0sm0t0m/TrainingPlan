import React, { useState, useEffect, useMemo } from 'react';
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
  ToggleButton,
  ToggleButtonGroup,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
} from '@mui/material';
import {
  ArrowBack as ArrowBackIcon,
  ContentCopy as ContentCopyIcon,
  OpenInNew as OpenInNewIcon,
  AutoAwesome as AutoAwesomeIcon,
  Check as CheckIcon,
  CheckCircle as CheckCircleIcon,
  RadioButtonUnchecked as RadioButtonUncheckedIcon,
} from '@mui/icons-material';
import { useNavigate } from 'react-router-dom';
import { useAuthStore } from '../store/authStore';
import api from '../services/api';
import {
  generateAIPrompt,
  PromptGenerationConfig,
  getTrainerStyles,
  getTrainerStyleDetails,
  TrainerStyle,
  TrainerStyleDetail,
  PlanPhaseInfo,
} from '../services/aiTrainingPlan';

interface Event {
  id: number;
  name: string;
  event_date: string;
  target_distance?: string;
  goal_time?: string;
}

const AITrainingPlanGenerator: React.FC = () => {
  const navigate = useNavigate();
  const { user } = useAuthStore();
  const [activeStep, setActiveStep] = useState(0);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [events, setEvents] = useState<Event[]>([]);
  const [generatedPrompt, setGeneratedPrompt] = useState<string>('');
  const [copied, setCopied] = useState(false);

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

  const [generationMode, setGenerationMode] = useState<'full' | 'phased'>('phased');
  const [phases, setPhases] = useState<PlanPhaseInfo[]>([]);
  const [currentPhaseIndex, setCurrentPhaseIndex] = useState(0);
  const [completedPhaseIndexes, setCompletedPhaseIndexes] = useState<number[]>([]);
  const [recommendedMode, setRecommendedMode] = useState<'full' | 'phased'>('phased');

  const steps = ['Select Event', 'Configure Plan', 'Choose Trainer Style', 'Get Prompt'];
  const weekDays = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday'];

  const estimatedWeeks = useMemo(() => {
    if (!startDate || !eventDate) return null;
    const start = new Date(startDate);
    const end = new Date(eventDate);
    if (Number.isNaN(start.getTime()) || Number.isNaN(end.getTime()) || end <= start) return null;
    return Math.max(1, Math.floor((end.getTime() - start.getTime()) / (7 * 24 * 60 * 60 * 1000)));
  }, [startDate, eventDate]);

  useEffect(() => {
    document.title = 'AI Training Plan Generator - Kinesis';
  }, []);

  useEffect(() => {
    if (!user) {
      navigate('/login');
      return;
    }
    fetchEvents();
    fetchTrainerStyles();
    const nextMonday = getNextMonday();
    setStartDate(nextMonday.toISOString().split('T')[0]);
  }, [user, navigate]);

  useEffect(() => {
    if (estimatedWeeks != null) {
      const rec = estimatedWeeks > 16 ? 'phased' : 'full';
      setRecommendedMode(rec);
    }
  }, [estimatedWeeks]);

  if (!user) {
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
      const response = await api.get('/events');
      setEvents(response.data);
    } catch (err: any) {
      console.error('[AITrainingPlanGenerator] Failed to load events:', err);
    }
  };

  const fetchTrainerStyles = async () => {
    try {
      const styles = await getTrainerStyles();
      if (styles && Array.isArray(styles) && styles.length > 0) {
        setTrainerStyles(styles);
      }
    } catch (err: any) {
      console.error('[AITrainingPlanGenerator] Failed to load trainer styles:', err);
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
    const event = events.find((e) => e.id === eventId);
    if (event) {
      setEventName(event.name);
      setEventDate(event.event_date);
      setEventDistance(event.target_distance || '');
      setGoalTime(event.goal_time || '');
    }
  };

  const buildConfig = (phaseIndex?: number): PromptGenerationConfig => ({
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
    generationMode,
    phaseIndex: generationMode === 'phased' ? phaseIndex ?? currentPhaseIndex : undefined,
  });

  const runGenerate = async (phaseIndex?: number) => {
    setLoading(true);
    setError(null);
    try {
      const response = await generateAIPrompt(buildConfig(phaseIndex));
      setGeneratedPrompt(response.prompt);
      setPhases(response.phases || []);
      setRecommendedMode(response.recommendedMode || 'phased');
      if (response.currentPhase) {
        setCurrentPhaseIndex(response.currentPhase.index);
      }
      if (activeStep < 4) {
        setActiveStep(4);
      }
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
  };

  const handleNext = async () => {
    if (activeStep === 3) {
      await runGenerate(generationMode === 'phased' ? 0 : undefined);
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

  const markPhaseDoneAndAdvance = async () => {
    const done = Array.from(new Set([...completedPhaseIndexes, currentPhaseIndex]));
    setCompletedPhaseIndexes(done);
    const next = currentPhaseIndex + 1;
    if (next < phases.length) {
      await runGenerate(next);
    }
  };

  const selectPhase = async (index: number) => {
    await runGenerate(index);
  };

  const handleDayToggle = (day: string) => {
    if (preferredDays.includes(day)) {
      if (preferredDays.length > 3) {
        setPreferredDays(preferredDays.filter((d) => d !== day));
      }
    } else {
      setPreferredDays([...preferredDays, day]);
    }
  };

  const currentPhase = phases.find((p) => p.index === currentPhaseIndex) || null;
  const allPhasesDone =
    generationMode === 'phased' &&
    phases.length > 0 &&
    phases.every((p) => completedPhaseIndexes.includes(p.index));

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
        <Stepper activeStep={Math.min(activeStep, 3)} sx={{ mb: 4 }}>
          {steps.map((label) => (
            <Step key={label}>
              <StepLabel>{label}</StepLabel>
            </Step>
          ))}
        </Stepper>

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
              placeholder="e.g., Ironman 70.3, Olympic, Marathon"
              value={eventDistance}
              onChange={(e) => setEventDistance(e.target.value)}
              sx={{ mb: 2 }}
            />

            <TextField
              label="Goal Time"
              fullWidth
              placeholder="e.g., 4:50"
              value={goalTime}
              onChange={(e) => setGoalTime(e.target.value)}
              sx={{ mb: 2 }}
            />
          </Box>
        )}

        {activeStep === 1 && (
          <Box>
            <Typography variant="h6" gutterBottom>
              Configure Training Plan
            </Typography>
            <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
              Set your training preferences and how to generate the prompt
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
                  <MenuItem key={days} value={days}>
                    {days} days
                  </MenuItem>
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

            <Typography variant="subtitle2" gutterBottom>
              Generation mode
            </Typography>
            <ToggleButtonGroup
              exclusive
              value={generationMode}
              onChange={(_, v) => v && setGenerationMode(v)}
              sx={{ mb: 1 }}
            >
              <ToggleButton value="phased">Phase by phase</ToggleButton>
              <ToggleButton value="full">Full plan (one prompt)</ToggleButton>
            </ToggleButtonGroup>
            <Alert severity={recommendedMode === 'phased' ? 'info' : 'success'} sx={{ mb: 3 }}>
              {estimatedWeeks != null && (
                <>
                  Plan length ≈ <strong>{estimatedWeeks} weeks</strong>.{' '}
                </>
              )}
              {recommendedMode === 'phased'
                ? 'Recommended: generate one phase at a time, then merge JSON files on import. Long plans often truncate in a single chat response.'
                : 'A single prompt should work for shorter plans. You can still switch to phase-by-phase if the model truncates.'}
            </Alert>

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
                      <Typography variant="caption" color="text.secondary">
                        {trainer.tagline}
                      </Typography>
                    </Box>
                  </MenuItem>
                ))}
              </Select>
            </FormControl>

            {trainerStyles.find((t) => t.id === selectedTrainerStyle) && (
              <Alert severity="info" sx={{ mb: 3 }}>
                <AlertTitle>
                  {trainerStyles.find((t) => t.id === selectedTrainerStyle)?.name}
                </AlertTitle>
                {trainerStyles.find((t) => t.id === selectedTrainerStyle)?.description}
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
                <Typography variant="subtitle2" gutterBottom>
                  Training Philosophy:
                </Typography>
                <Typography
                  variant="body2"
                  component="pre"
                  sx={{ whiteSpace: 'pre-wrap', mb: 2, fontSize: '0.85rem' }}
                >
                  {trainerStyleDetails.philosophy}
                </Typography>

                <Typography variant="subtitle2" gutterBottom>
                  Key Workouts:
                </Typography>
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
              placeholder="e.g., Focus more on hill training, prefer shorter high-intensity intervals..."
              value={customTrainerInstructions}
              onChange={(e) => setCustomTrainerInstructions(e.target.value)}
              sx={{ mb: 2 }}
            />
          </Box>
        )}

        {activeStep === 3 && !generatedPrompt && (
          <Box sx={{ textAlign: 'center', py: 4 }}>
            <Typography variant="h6" gutterBottom>
              Ready to Generate Prompt
            </Typography>
            <Typography variant="body2" color="text.secondary">
              {generationMode === 'phased'
                ? 'You’ll get Phase 1 first, then step through remaining phases.'
                : 'One prompt will cover the full plan date range.'}
            </Typography>
          </Box>
        )}

        {activeStep === 4 && (
          <Box>
            {generationMode === 'phased' && phases.length > 0 && (
              <Paper variant="outlined" sx={{ p: 2, mb: 3 }}>
                <Typography variant="subtitle1" gutterBottom>
                  Phase progress
                </Typography>
                <List dense>
                  {phases.map((phase) => {
                    const done = completedPhaseIndexes.includes(phase.index);
                    const active = phase.index === currentPhaseIndex;
                    return (
                      <ListItem
                        key={phase.id}
                        secondaryAction={
                          <Button size="small" onClick={() => selectPhase(phase.index)} disabled={loading}>
                            {active ? 'Current' : 'Load'}
                          </Button>
                        }
                      >
                        <ListItemIcon sx={{ minWidth: 36 }}>
                          {done ? (
                            <CheckCircleIcon color="success" fontSize="small" />
                          ) : (
                            <RadioButtonUncheckedIcon
                              color={active ? 'primary' : 'disabled'}
                              fontSize="small"
                            />
                          )}
                        </ListItemIcon>
                        <ListItemText
                          primary={`${phase.name} (W${phase.weekStart}–W${phase.weekEnd})`}
                          secondary={`${phase.startDate} → ${phase.endDate} · ${phase.focus}`}
                          primaryTypographyProps={{ fontWeight: active ? 700 : 400 }}
                        />
                      </ListItem>
                    );
                  })}
                </List>
                {currentPhase && (
                  <Alert severity="info" sx={{ mt: 1 }}>
                    Working on <strong>{currentPhase.name}</strong>. Copy prompt → AI → save as{' '}
                    <code>phase_{currentPhase.index + 1}_{currentPhase.name.toLowerCase().replace(/\s+/g, '_')}.json</code>
                    , then mark done and continue.
                  </Alert>
                )}
              </Paper>
            )}

            <Alert severity="info" sx={{ mb: 3 }}>
              <AlertTitle>How to use this prompt (Gemini recommended)</AlertTitle>
              <ol style={{ margin: 0, paddingLeft: 20 }}>
                <li>Copy the prompt below</li>
                <li>Open Gemini (or ChatGPT / Claude)</li>
                <li>Paste and send — ask for a downloadable .json file if offered</li>
                <li>
                  Save the response as a .json file
                  {generationMode === 'phased' ? ' (one file per phase)' : ''}
                </li>
                <li>
                  Plans → Import AI Plan
                  {generationMode === 'phased'
                    ? ' → select all phase files to merge'
                    : ' → upload the file'}
                </li>
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

            <Stack direction="row" spacing={2} flexWrap="wrap" useFlexGap sx={{ gap: 1 }}>
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
                onClick={() => window.open('https://gemini.google.com/app', '_blank')}
              >
                Open Gemini
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
              {generationMode === 'phased' && currentPhase && !currentPhase.isLast && (
                <Button
                  variant="contained"
                  color="secondary"
                  disabled={loading}
                  onClick={markPhaseDoneAndAdvance}
                >
                  Mark phase done → next
                </Button>
              )}
              {generationMode === 'phased' && currentPhase?.isLast && (
                <Button
                  variant="contained"
                  color="secondary"
                  disabled={loading}
                  onClick={() =>
                    setCompletedPhaseIndexes(
                      Array.from(new Set([...completedPhaseIndexes, currentPhaseIndex]))
                    )
                  }
                >
                  Mark final phase done
                </Button>
              )}
            </Stack>

            {allPhasesDone && (
              <Alert severity="success" sx={{ mt: 3 }}>
                <AlertTitle>All phases prompted</AlertTitle>
                Import all phase .json files together on the Plans page (multi-select merges them into one plan).
              </Alert>
            )}

            <Alert severity="success" sx={{ mt: 3 }}>
              <AlertTitle>Next steps</AlertTitle>
              <ul style={{ margin: '8px 0 0 0', paddingLeft: 20 }}>
                <li>File must start with {'{'} and every workout needs structuredSteps</li>
                <li>Phase files: Import AI Plan → select multiple .json files to merge</li>
              </ul>
            </Alert>
          </Box>
        )}

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
                {activeStep === 3
                  ? generationMode === 'phased'
                    ? 'Generate Phase 1'
                    : 'Generate Prompt'
                  : 'Next'}
              </Button>
            )}
          </Box>
        </Box>
      </Paper>
    </Container>
  );
};

export default AITrainingPlanGenerator;
