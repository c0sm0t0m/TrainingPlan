import React from 'react';
import {
  Card,
  CardContent,
  Typography,
  Switch,
  FormControlLabel,
  Box,
  Chip,
  Button,
  Divider,
  Alert,
  Stack,
} from '@mui/material';
import {
  Science as ExperimentIcon,
  RestartAlt as ResetIcon,
  CheckCircle as EnableAllIcon,
  Cancel as DisableAllIcon,
} from '@mui/icons-material';
import { useFeatureFlags, FeatureFlags } from '../contexts/FeatureFlagsContext';

interface FeatureInfo {
  key: keyof FeatureFlags;
  label: string;
  description: string;
  priority: 'P0' | 'P1' | 'P2';
  effort: 'Small' | 'Medium' | 'Large';
}

// Add experimental features here as they are developed
const FEATURE_INFO: FeatureInfo[] = [
  {
    key: 'newColorTheme',
    label: 'Modern Athletic Theme',
    description: 'Updated color palette with vibrant blue (#0A7AFF), energetic orange, and modern styling',
    priority: 'P1',
    effort: 'Small',
  },
];

const getPriorityColor = (priority: string) => {
  switch (priority) {
    case 'P0': return 'error';
    case 'P1': return 'warning';
    case 'P2': return 'info';
    default: return 'default';
  }
};

const getEffortColor = (effort: string) => {
  switch (effort) {
    case 'Small': return 'success';
    case 'Medium': return 'warning';
    case 'Large': return 'error';
    default: return 'default';
  }
};

const FeatureFlagsPanel: React.FC = () => {
  const { features, toggleFeature, resetFeatures, enableAll, disableAll } = useFeatureFlags();

  const activeCount = Object.values(features).filter(Boolean).length;
  const totalCount = Object.keys(features).length;

  return (
    <Card>
      <CardContent>
        <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
          <ExperimentIcon sx={{ mr: 1, color: 'primary.main' }} />
          <Typography variant="h6">
            Beta Features
          </Typography>
          <Chip
            label={`${activeCount}/${totalCount} Active`}
            size="small"
            color={activeCount > 0 ? 'primary' : 'default'}
            sx={{ ml: 'auto' }}
          />
        </Box>

        <Alert severity="info" sx={{ mb: 2 }}>
          Toggle features to test new UI improvements. Changes are saved automatically.
        </Alert>

        <Stack direction="row" spacing={1} sx={{ mb: 2 }}>
          <Button
            size="small"
            startIcon={<EnableAllIcon />}
            onClick={enableAll}
            variant="outlined"
            color="success"
          >
            Enable All
          </Button>
          <Button
            size="small"
            startIcon={<DisableAllIcon />}
            onClick={disableAll}
            variant="outlined"
            color="error"
          >
            Disable All
          </Button>
          <Button
            size="small"
            startIcon={<ResetIcon />}
            onClick={resetFeatures}
            variant="outlined"
          >
            Reset to Defaults
          </Button>
        </Stack>

        <Divider sx={{ mb: 2 }} />

        {/* Group by priority */}
        {['P0', 'P1', 'P2'].map((priority) => {
          const priorityFeatures = FEATURE_INFO.filter((f) => f.priority === priority);
          
          return (
            <Box key={priority} sx={{ mb: 3 }}>
              <Typography variant="subtitle2" color="text.secondary" sx={{ mb: 1 }}>
                {priority === 'P0' && '🔥 Critical Improvements'}
                {priority === 'P1' && '⭐ High-Impact Features'}
                {priority === 'P2' && '✨ Polish & Enhancement'}
              </Typography>

              {priorityFeatures.map((feature) => (
                <Box
                  key={feature.key}
                  sx={{
                    display: 'flex',
                    alignItems: 'flex-start',
                    mb: 2,
                    p: 1.5,
                    borderRadius: 1,
                    bgcolor: features[feature.key] ? 'action.selected' : 'transparent',
                    border: 1,
                    borderColor: features[feature.key] ? 'primary.main' : 'divider',
                    transition: 'all 0.2s',
                  }}
                >
                  <Box sx={{ flex: 1 }}>
                    <Box sx={{ display: 'flex', alignItems: 'center', mb: 0.5 }}>
                      <Typography variant="body1" fontWeight={500}>
                        {feature.label}
                      </Typography>
                      <Chip
                        label={feature.priority}
                        size="small"
                        color={getPriorityColor(feature.priority)}
                        sx={{ ml: 1, height: 20, fontSize: '0.7rem' }}
                      />
                      <Chip
                        label={feature.effort}
                        size="small"
                        color={getEffortColor(feature.effort)}
                        variant="outlined"
                        sx={{ ml: 0.5, height: 20, fontSize: '0.7rem' }}
                      />
                    </Box>
                    <Typography variant="body2" color="text.secondary">
                      {feature.description}
                    </Typography>
                  </Box>

                  <FormControlLabel
                    control={
                      <Switch
                        checked={features[feature.key]}
                        onChange={() => toggleFeature(feature.key)}
                        color="primary"
                      />
                    }
                    label=""
                    sx={{ ml: 2, mr: 0 }}
                  />
                </Box>
              ))}
            </Box>
          );
        })}

        <Divider sx={{ my: 2 }} />

        <Typography variant="caption" color="text.secondary">
          💡 <strong>Pro tip:</strong> Use URL parameters for quick testing (e.g., ?newNavigation=true)
          <br />
          🔧 <strong>Console:</strong> localStorage.setItem('feature_newNavigation', 'true')
        </Typography>
      </CardContent>
    </Card>
  );
};

export default FeatureFlagsPanel;
