import React, { useState } from 'react';
import {
  Box,
  Button,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Typography,
  Alert,
  AlertTitle,
  Paper,
  Chip,
  Stack,
  LinearProgress,
  Card,
  CardContent,
  Grid,
} from '@mui/material';
import {
  CloudUpload as CloudUploadIcon,
  CheckCircle as CheckCircleIcon,
} from '@mui/icons-material';
import {
  validateAIPlan,
  importAIPlan,
  ValidationResponse,
  mergePhasePlanFiles,
} from '../services/aiTrainingPlan';

interface AITrainingPlanImportProps {
  open: boolean;
  onClose: () => void;
  onSuccess: () => void;
}

function cleanChatJson(text: string): string {
  let t = text.trim();
  t = t.replace(/^```(?:json)?\s*/i, '');
  t = t.replace(/\s*```$/i, '');
  if (!t.startsWith('{')) {
    const start = t.indexOf('{');
    const end = t.lastIndexOf('}');
    if (start !== -1 && end > start) {
      t = t.slice(start, end + 1);
    }
  }
  return t.trim();
}

const AITrainingPlanImport: React.FC<AITrainingPlanImportProps> = ({
  open,
  onClose,
  onSuccess,
}) => {
  const [step, setStep] = useState<'upload' | 'preview' | 'importing'>('upload');
  const [file, setFile] = useState<File | null>(null);
  const [fileLabel, setFileLabel] = useState<string>('');
  const [validationResult, setValidationResult] = useState<ValidationResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [dragActive, setDragActive] = useState(false);

  const handleClose = () => {
    setStep('upload');
    setFile(null);
    setFileLabel('');
    setValidationResult(null);
    setError(null);
    onClose();
  };

  const handleDrag = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === 'dragenter' || e.type === 'dragover') {
      setDragActive(true);
    } else if (e.type === 'dragleave') {
      setDragActive(false);
    }
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);

    if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
      handleFilesSelect(Array.from(e.dataTransfer.files));
    }
  };

  const handleFileInput = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files.length > 0) {
      handleFilesSelect(Array.from(e.target.files));
    }
  };

  const handleFilesSelect = async (selectedFiles: File[]) => {
    const jsonFiles = selectedFiles.filter((f) => f.name.toLowerCase().endsWith('.json'));
    if (!jsonFiles.length) {
      setError('Please upload one or more .json files');
      return;
    }

    for (const f of jsonFiles) {
      if (f.size > 5 * 1024 * 1024) {
        setError(`File ${f.name} exceeds 5MB`);
        return;
      }
    }

    setError(null);

    try {
      let uploadFile: File;

      if (jsonFiles.length === 1) {
        uploadFile = jsonFiles[0];
        setFileLabel(jsonFiles[0].name);
      } else {
        const parsed: any[] = [];
        for (const f of jsonFiles) {
          const text = cleanChatJson(await f.text());
          parsed.push(JSON.parse(text));
        }
        const merged = mergePhasePlanFiles(parsed);
        const blob = new Blob([JSON.stringify(merged, null, 2)], { type: 'application/json' });
        uploadFile = new File([blob], 'merged_training_plan.json', { type: 'application/json' });
        setFileLabel(`${jsonFiles.length} phase files → merged`);
      }

      setFile(uploadFile);
      const result = await validateAIPlan(uploadFile);
      setValidationResult(result);

      if (result.validation.valid) {
        setStep('preview');
      } else {
        setError(`Validation failed: ${result.validation.errors.join(', ')}`);
      }
    } catch (err: any) {
      setError(err.response?.data?.detail || err.message || 'Failed to validate plan');
    }
  };

  const handleImport = async () => {
    if (!file) return;

    setStep('importing');
    setError(null);

    try {
      await importAIPlan(file);
      onSuccess();
      handleClose();
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to import plan');
      setStep('preview');
    }
  };

  return (
    <Dialog open={open} onClose={handleClose} maxWidth="md" fullWidth>
      <DialogTitle>Import AI Training Plan</DialogTitle>

      <DialogContent>
        {error && (
          <Alert severity="error" sx={{ mb: 2 }} onClose={() => setError(null)}>
            {error}
          </Alert>
        )}

        {step === 'upload' && (
          <Box>
            <Alert severity="info" sx={{ mb: 3 }}>
              <AlertTitle>How to import</AlertTitle>
              <ol style={{ margin: 0, paddingLeft: 20 }}>
                <li>Get pure JSON from Gemini/ChatGPT/Claude (no markdown fences)</li>
                <li>Save as .json (one file, or multiple phase files)</li>
                <li>
                  Upload here — select <strong>multiple phase files</strong> to merge into one plan
                </li>
                <li>Workouts should include structuredSteps</li>
              </ol>
            </Alert>

            <Paper
              sx={{
                p: 4,
                textAlign: 'center',
                border: '2px dashed',
                borderColor: dragActive ? 'primary.main' : 'grey.400',
                bgcolor: dragActive ? 'action.hover' : 'background.paper',
                cursor: 'pointer',
                transition: 'all 0.2s',
                '&:hover': {
                  borderColor: 'primary.main',
                  bgcolor: 'action.hover',
                },
              }}
              onDragEnter={handleDrag}
              onDragLeave={handleDrag}
              onDragOver={handleDrag}
              onDrop={handleDrop}
              onClick={() => document.getElementById('file-upload')?.click()}
            >
              <input
                id="file-upload"
                type="file"
                accept=".json"
                multiple
                style={{ display: 'none' }}
                onChange={handleFileInput}
              />

              <CloudUploadIcon sx={{ fontSize: 64, color: 'primary.main', mb: 2 }} />

              <Typography variant="h6" gutterBottom>
                Drop JSON file(s) here
              </Typography>

              <Typography variant="body2" color="text.secondary" gutterBottom>
                or click to browse (multi-select for phases)
              </Typography>

              <Typography variant="caption" color="text.secondary">
                Supports: .json up to 5MB each
              </Typography>
            </Paper>
          </Box>
        )}

        {step === 'preview' && validationResult && (
          <Box>
            <Alert severity="success" icon={<CheckCircleIcon />} sx={{ mb: 3 }}>
              <AlertTitle>Plan Validated Successfully</AlertTitle>
              {fileLabel || 'Your training plan'} is ready to import
            </Alert>

            <Grid container spacing={2} sx={{ mb: 3 }}>
              <Grid item xs={6} sm={3}>
                <Card variant="outlined">
                  <CardContent sx={{ textAlign: 'center' }}>
                    <Typography variant="h4" color="primary">
                      {validationResult.preview?.weeks || 0}
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      Weeks
                    </Typography>
                  </CardContent>
                </Card>
              </Grid>
              <Grid item xs={6} sm={3}>
                <Card variant="outlined">
                  <CardContent sx={{ textAlign: 'center' }}>
                    <Typography variant="h4" color="primary">
                      {validationResult.preview?.totalWorkouts || 0}
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      Workouts
                    </Typography>
                  </CardContent>
                </Card>
              </Grid>
              <Grid item xs={6} sm={3}>
                <Card variant="outlined">
                  <CardContent sx={{ textAlign: 'center' }}>
                    <Typography variant="h4" color="primary">
                      {validationResult.preview?.totalTss || 0}
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      Total TSS
                    </Typography>
                  </CardContent>
                </Card>
              </Grid>
              <Grid item xs={6} sm={3}>
                <Card variant="outlined">
                  <CardContent sx={{ textAlign: 'center' }}>
                    <Typography variant="h4" color="primary">
                      {(validationResult.preview?.totalDistanceKm ?? 0).toFixed(1)}
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      km
                    </Typography>
                  </CardContent>
                </Card>
              </Grid>
            </Grid>

            <Paper sx={{ p: 2, mb: 2 }}>
              <Typography variant="subtitle2" gutterBottom>
                Plan Details
              </Typography>
              <Typography variant="body2">
                <strong>Name:</strong> {validationResult.preview?.name}
              </Typography>
              <Typography variant="body2">
                <strong>Start:</strong>{' '}
                {validationResult.preview
                  ? new Date(validationResult.preview.startDate).toLocaleDateString()
                  : ''}
              </Typography>
              <Typography variant="body2">
                <strong>End:</strong>{' '}
                {validationResult.preview
                  ? new Date(validationResult.preview.endDate).toLocaleDateString()
                  : ''}
              </Typography>
            </Paper>

            {validationResult.preview?.workoutTypeBreakdown &&
              Object.keys(validationResult.preview.workoutTypeBreakdown).length > 0 && (
                <Paper sx={{ p: 2 }}>
                  <Typography variant="subtitle2" gutterBottom>
                    Workouts by Type
                  </Typography>
                  <Stack direction="row" spacing={1} flexWrap="wrap" sx={{ gap: 1 }}>
                    {Object.entries(validationResult.preview.workoutTypeBreakdown).map(
                      ([type, count]) => (
                        <Chip
                          key={type}
                          label={`${type}: ${count}`}
                          color="primary"
                          variant="outlined"
                        />
                      )
                    )}
                  </Stack>
                </Paper>
              )}

            {validationResult.validation.warnings.length > 0 && (
              <Alert severity="warning" sx={{ mt: 2 }}>
                <AlertTitle>Warnings</AlertTitle>
                <ul style={{ margin: 0, paddingLeft: 20 }}>
                  {validationResult.validation.warnings.map((warning, idx) => (
                    <li key={idx}>{warning}</li>
                  ))}
                </ul>
              </Alert>
            )}
          </Box>
        )}

        {step === 'importing' && (
          <Box sx={{ py: 4, textAlign: 'center' }}>
            <Typography variant="h6" gutterBottom>
              Importing Training Plan...
            </Typography>
            <LinearProgress sx={{ mt: 2 }} />
          </Box>
        )}
      </DialogContent>

      <DialogActions>
        <Button onClick={handleClose} disabled={step === 'importing'}>
          Cancel
        </Button>
        {step === 'preview' && (
          <Button
            variant="contained"
            onClick={handleImport}
            disabled={!validationResult?.validation.valid}
          >
            Import Plan
          </Button>
        )}
      </DialogActions>
    </Dialog>
  );
};

export default AITrainingPlanImport;
