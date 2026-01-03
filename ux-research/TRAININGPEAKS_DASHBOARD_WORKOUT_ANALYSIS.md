# TrainingPeaks Dashboard & Workout Management Analysis

> **Focus Areas**: Dashboard Analytics, Workout Builder, Workout Library, Key Patterns
> **Date**: January 2, 2026
> **Purpose**: Extract proven UX patterns for TrainingPlan implementation

---

## 1. TrainingPeaks Dashboard Analysis

### Layout Architecture
TrainingPeaks uses a **3-column responsive layout** on desktop:
- **Left Column (30%)**: Calendar widget + Quick Stats
- **Center Column (45%)**: Performance Management Chart (PMC) + Training Load Graph
- **Right Column (25%)**: Upcoming workouts + Recent activities

### Key Metrics Display

#### Performance Management Chart (PMC)
The cornerstone of TrainingPeaks is the **PMC graph** showing:
- **CTL (Chronic Training Load)**: 42-day rolling average - BLUE line, represents fitness
- **ATL (Acute Training Load)**: 7-day rolling average - PINK/MAGENTA line, represents fatigue
- **TSB (Training Stress Balance)**: CTL - ATL - YELLOW bars, represents form (readiness)
- **TSS (Training Stress Score)**: Daily points shown as bar height

**Visual Design**:
- Dual-axis chart (line chart + bar chart overlay)
- 12-week default view with zoom controls
- Hover tooltip shows exact values for each date
- Color-coded zones: TSB < -30 (red/overreaching), -10 to 5 (yellow/optimal), > 20 (blue/detraining)

#### Secondary Metrics Cards
Displayed as **metric cards** above the PMC:
1. **7-Day Training Load**: TSS sum with % change vs previous week
2. **Weekly Volume**: Hours/distance with trend indicator
3. **Intensity Factor (IF)**: Current week average (0.00-1.00 scale)
4. **Variability Index (VI)**: Pacing consistency (1.00 = perfect pacing)

**Card Design Pattern**:
```
┌─────────────────────────┐
│ METRIC LABEL            │
│ 342 TSS          ↑ 8%  │
│ ▁▂▃▄▅▆▇█ sparkline     │
└─────────────────────────┘
```

### Information Density Strategy
- **Progressive disclosure**: Summary cards → Click for detailed breakdown
- **Sparklines**: Mini trend graphs in metric cards (7-14 day history)
- **Status indicators**: Color-coded badges (green = on track, yellow = behind, red = overtraining)
- **Collapsible sections**: Upcoming workouts can expand/collapse

### Quick Actions Widget
Fixed position (top-right or FAB on mobile):
- **+ Add Workout** - Primary action
- **Upload Activity** - Secondary action
- **Quick Log** - Tertiary action (for manual entries)

### Recent Activities Display
Table format with columns:
- **Sport Icon** (run/bike/swim)
- **Date & Time**
- **Title** (clickable to detail)
- **Duration** / **Distance**
- **TSS** (bold, prominent)
- **Intensity** (IF badge)
- **Actions** (Edit, Analyze, Delete)

---

## 2. TrainingPeaks Workout Builder Analysis

### Workout Creation Flow (5-Step Process)

#### Step 1: Basic Info Modal
```
┌────────────────────────────────┐
│  Create New Workout            │
├────────────────────────────────┤
│  Workout Name: ________________│
│  Sport: [Dropdown: Run ▼]     │
│  Date: [2026-01-15] (optional)│
│                                │
│  [Cancel]         [Continue →]│
└────────────────────────────────┘
```

#### Step 2: Structured Workout Builder
**Interface Layout**:
- **Left Panel (25%)**: Step palette (Warmup, Intervals, Cooldown, Rest)
- **Center Panel (50%)**: Workout timeline (drag-and-drop steps)
- **Right Panel (25%)**: Step properties editor

**Timeline View** (Visual Workout Builder):
```
┌─────────────────────────────────────────────┐
│ Workout: Threshold Intervals               │
├─────────────────────────────────────────────┤
│ 🟢 Warmup      │ 10:00 │ Zone 2 │ [⋮]     │
│ 🔴 Interval 1  │  5:00 │ Zone 4 │ [⋮]     │
│ 🟡 Recovery    │  2:00 │ Zone 1 │ [⋮]     │
│ 🔴 Interval 2  │  5:00 │ Zone 4 │ [⋮]     │
│ 🟡 Recovery    │  2:00 │ Zone 1 │ [⋮]     │
│ 🔵 Cooldown    │ 10:00 │ Zone 2 │ [⋮]     │
├─────────────────────────────────────────────┤
│ Total: 34:00 │ Est. TSS: 45                │
└─────────────────────────────────────────────┘
```

#### Step 3: Step Properties Editor
When step is selected, right panel shows:
- **Duration Type**: Time / Distance / Lap Button / Open (until lap press)
- **Target Type**: Heart Rate / Power / Pace / Cadence / Open (no target)
- **Target Zone**: Dropdown with zones OR custom range
- **Notes**: Freeform text for instructions
- **Repeat**: Checkbox + count (for interval sets)

**Example - Interval Step Properties**:
```
┌─────────────────────────────┐
│ Interval Properties         │
├─────────────────────────────┤
│ Duration:                   │
│ ○ Time      [5:00]         │
│ ○ Distance  [____]         │
│ ○ Lap Button               │
│                             │
│ Target:                     │
│ ○ Heart Rate  [Zone 4 ▼]  │
│ ● Power       [Zone 4 ▼]  │
│ ○ Pace        [____]       │
│                             │
│ Custom Range:               │
│ [240] - [260] watts        │
│                             │
│ Notes:                      │
│ [Hold steady at FTP]       │
│                             │
│ ☑ Repeat 4x with 2:00 rest │
└─────────────────────────────┘
```

#### Step 4: TSS Estimation
Real-time TSS calculation shown at bottom:
- **Formula displayed**: IF² × Hours × 100
- **Per-step TSS breakdown** (hover tooltip)
- **Color indicator**: Green < 150, Yellow 150-300, Red > 300

#### Step 5: Save Options
Modal with two paths:
```
┌────────────────────────────────┐
│  Save Workout                  │
├────────────────────────────────┤
│  ☑ Save to Library             │
│  Folder: [Threshold ▼]        │
│                                │
│  ☐ Schedule to Calendar        │
│  Date: [2026-01-15]            │
│                                │
│  [Cancel]  [Save to Library]  │
│            [Schedule & Save]   │
└────────────────────────────────┘
```

### Sport-Specific Fields
Each sport has different target types:
- **Run**: Pace, HR, Cadence
- **Bike**: Power, HR, Cadence
- **Swim**: Pace, Stroke Rate

### Duplicate/Copy Patterns
- **Copy button** on every workout in library
- **Copy to Date** - Opens date picker to clone workout
- **Copy Structure Only** - Clones without notes/TSS targets

---

## 3. Workout Library Analysis

### Organization System

#### Folder Structure
```
📁 My Workouts
  📁 Bike
    📁 Threshold
    📁 VO2 Max
    📁 Endurance
  📁 Run
    📁 Intervals
    📁 Long Run
    📁 Tempo
  📁 Swim
```

#### Search & Filter Bar
```
┌────────────────────────────────────────────────────┐
│ 🔍 Search workouts...           [Sport ▼] [TSS ▼] │
└────────────────────────────────────────────────────┘
```

Filters available:
- **Sport**: All / Run / Bike / Swim
- **TSS Range**: 0-50, 50-100, 100-150, 150+
- **Duration**: < 30min, 30-60min, 60-90min, 90min+
- **Tags**: Custom tags (e.g., "intervals", "recovery")

### Preview Cards
Grid layout (3-4 columns on desktop):
```
┌─────────────────────────────┐
│ 🚴 Threshold Intervals      │
├─────────────────────────────┤
│ 60 min │ 75 TSS │ Zone 4   │
│                             │
│ 🟢──🔴──🟡──🔴──🟡──🔵   │
│                             │
│ [Schedule] [Edit] [⋮]      │
└─────────────────────────────┘
```

Card shows:
- **Sport icon** + **Workout name**
- **Duration** / **TSS** / **Primary zone**
- **Visual timeline** (simplified bar representation)
- **Action buttons**: Schedule, Edit, More menu

### Quick Edit Options
Hover/right-click menu:
- **Schedule to Calendar** - Date picker modal
- **Edit** - Opens builder
- **Duplicate** - Creates copy with "(Copy)" suffix
- **Move to Folder** - Folder picker
- **Add Tags** - Tag autocomplete
- **Delete** - Confirmation dialog

### Bulk Operations
Checkbox selection mode:
- **Select All** checkbox in header
- **Actions bar** appears when items selected: Move, Tag, Delete, Export

### Sort Options
Dropdown with:
- Name (A-Z)
- Date Created (Newest first)
- TSS (Low to High)
- Duration (Short to Long)
- Last Used

---

## 4. Code Examples

### Example 1: PMC Dashboard Widget

```tsx
import React from 'react';
import {
  Card,
  CardContent,
  Typography,
  Box,
  useTheme,
} from '@mui/material';
import {
  LineChart,
  Line,
  BarChart,
  Bar,
  ComposedChart,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from 'recharts';
import TrendingUpIcon from '@mui/icons-material/TrendingUp';
import TrendingDownIcon from '@mui/icons-material/TrendingDown';

interface PMCData {
  date: string;
  ctl: number;
  atl: number;
  tsb: number;
  tss: number;
}

interface DashboardStats {
  weeklyTSS: number;
  weeklyTSSChange: number;
  weeklyVolume: number;
  averageIF: number;
  averageVI: number;
}

const PMCWidget: React.FC<{ data: PMCData[]; stats: DashboardStats }> = ({
  data,
  stats,
}) => {
  const theme = useTheme();

  const getTSBColor = (tsb: number) => {
    if (tsb < -30) return theme.palette.error.main;
    if (tsb < -10) return theme.palette.warning.main;
    if (tsb < 5) return theme.palette.success.main;
    if (tsb < 20) return theme.palette.info.main;
    return theme.palette.grey[500];
  };

  return (
    <Box>
      {/* Metric Cards Row */}
      <Box sx={{ display: 'flex', gap: 2, mb: 3 }}>
        <Card sx={{ flex: 1 }}>
          <CardContent>
            <Typography variant="caption" color="text.secondary">
              7-Day Training Load
            </Typography>
            <Box sx={{ display: 'flex', alignItems: 'baseline', gap: 1 }}>
              <Typography variant="h4">{stats.weeklyTSS}</Typography>
              <Typography variant="body2" color="text.secondary">
                TSS
              </Typography>
              <Box
                sx={{
                  display: 'flex',
                  alignItems: 'center',
                  color:
                    stats.weeklyTSSChange > 0
                      ? theme.palette.success.main
                      : theme.palette.error.main,
                }}
              >
                {stats.weeklyTSSChange > 0 ? (
                  <TrendingUpIcon fontSize="small" />
                ) : (
                  <TrendingDownIcon fontSize="small" />
                )}
                <Typography variant="body2">
                  {Math.abs(stats.weeklyTSSChange)}%
                </Typography>
              </Box>
            </Box>
          </CardContent>
        </Card>

        <Card sx={{ flex: 1 }}>
          <CardContent>
            <Typography variant="caption" color="text.secondary">
              Weekly Volume
            </Typography>
            <Box sx={{ display: 'flex', alignItems: 'baseline', gap: 1 }}>
              <Typography variant="h4">{stats.weeklyVolume}</Typography>
              <Typography variant="body2" color="text.secondary">
                hours
              </Typography>
            </Box>
          </CardContent>
        </Card>

        <Card sx={{ flex: 1 }}>
          <CardContent>
            <Typography variant="caption" color="text.secondary">
              Intensity Factor
            </Typography>
            <Typography variant="h4">{stats.averageIF.toFixed(2)}</Typography>
          </CardContent>
        </Card>

        <Card sx={{ flex: 1 }}>
          <CardContent>
            <Typography variant="caption" color="text.secondary">
              Variability Index
            </Typography>
            <Typography variant="h4">{stats.averageVI.toFixed(2)}</Typography>
          </CardContent>
        </Card>
      </Box>

      {/* Performance Management Chart */}
      <Card>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            Performance Management Chart
          </Typography>
          <ResponsiveContainer width="100%" height={400}>
            <ComposedChart data={data}>
              <CartesianGrid strokeDasharray="3 3" stroke={theme.palette.divider} />
              <XAxis
                dataKey="date"
                stroke={theme.palette.text.secondary}
                style={{ fontSize: '0.75rem' }}
              />
              <YAxis
                yAxisId="left"
                stroke={theme.palette.text.secondary}
                style={{ fontSize: '0.75rem' }}
                label={{ value: 'TSS', angle: -90, position: 'insideLeft' }}
              />
              <YAxis
                yAxisId="right"
                orientation="right"
                stroke={theme.palette.text.secondary}
                style={{ fontSize: '0.75rem' }}
                label={{ value: 'TSB', angle: 90, position: 'insideRight' }}
              />
              <Tooltip
                contentStyle={{
                  backgroundColor: theme.palette.background.paper,
                  border: `1px solid ${theme.palette.divider}`,
                }}
              />
              <Legend />
              
              {/* TSS Daily Bars */}
              <Bar
                yAxisId="left"
                dataKey="tss"
                fill={theme.palette.grey[400]}
                name="Daily TSS"
                opacity={0.3}
              />
              
              {/* CTL Line (Fitness) */}
              <Line
                yAxisId="left"
                type="monotone"
                dataKey="ctl"
                stroke={theme.palette.primary.main}
                strokeWidth={2}
                name="CTL (Fitness)"
                dot={false}
              />
              
              {/* ATL Line (Fatigue) */}
              <Line
                yAxisId="left"
                type="monotone"
                dataKey="atl"
                stroke={theme.palette.secondary.main}
                strokeWidth={2}
                name="ATL (Fatigue)"
                dot={false}
              />
              
              {/* TSB Bars (Form) */}
              <Bar
                yAxisId="right"
                dataKey="tsb"
                fill={theme.palette.warning.main}
                name="TSB (Form)"
                opacity={0.6}
              />
            </ComposedChart>
          </ResponsiveContainer>

          {/* Legend Explanation */}
          <Box sx={{ mt: 2, display: 'flex', gap: 3, flexWrap: 'wrap' }}>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
              <Box
                sx={{
                  width: 16,
                  height: 3,
                  bgcolor: theme.palette.primary.main,
                }}
              />
              <Typography variant="caption">
                CTL: Chronic Training Load (Fitness)
              </Typography>
            </Box>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
              <Box
                sx={{
                  width: 16,
                  height: 3,
                  bgcolor: theme.palette.secondary.main,
                }}
              />
              <Typography variant="caption">
                ATL: Acute Training Load (Fatigue)
              </Typography>
            </Box>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
              <Box
                sx={{
                  width: 16,
                  height: 16,
                  bgcolor: theme.palette.warning.main,
                  opacity: 0.6,
                }}
              />
              <Typography variant="caption">
                TSB: Training Stress Balance (Form)
              </Typography>
            </Box>
          </Box>
        </CardContent>
      </Card>
    </Box>
  );
};

export default PMCWidget;
```

### Example 2: Workout Builder Interface

```tsx
import React, { useState } from 'react';
import {
  Box,
  Card,
  CardContent,
  TextField,
  Select,
  MenuItem,
  Button,
  IconButton,
  Typography,
  Divider,
  Chip,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  FormControl,
  InputLabel,
  RadioGroup,
  FormControlLabel,
  Radio,
  Checkbox,
} from '@mui/material';
import {
  Add as AddIcon,
  DragIndicator as DragIcon,
  Delete as DeleteIcon,
  ContentCopy as CopyIcon,
} from '@mui/icons-material';
import { DragDropContext, Droppable, Draggable } from 'react-beautiful-dnd';

interface WorkoutStep {
  id: string;
  type: 'warmup' | 'interval' | 'recovery' | 'cooldown' | 'rest';
  durationType: 'time' | 'distance' | 'lap' | 'open';
  duration: number;
  targetType: 'hr' | 'power' | 'pace' | 'cadence' | 'open';
  targetZone: string;
  targetMin?: number;
  targetMax?: number;
  notes: string;
  repeat?: number;
}

interface Workout {
  name: string;
  sport: 'run' | 'bike' | 'swim';
  steps: WorkoutStep[];
}

const WorkoutBuilder: React.FC = () => {
  const [workout, setWorkout] = useState<Workout>({
    name: '',
    sport: 'run',
    steps: [],
  });
  const [selectedStep, setSelectedStep] = useState<string | null>(null);
  const [editDialogOpen, setEditDialogOpen] = useState(false);

  const stepColors = {
    warmup: '#4CAF50',
    interval: '#F44336',
    recovery: '#FFC107',
    cooldown: '#2196F3',
    rest: '#9E9E9E',
  };

  const calculateTSS = (): number => {
    // Simplified TSS calculation
    let totalTSS = 0;
    workout.steps.forEach((step) => {
      const durationHours = step.duration / 3600;
      const if_estimate = step.type === 'interval' ? 0.95 : 0.65;
      totalTSS += Math.pow(if_estimate, 2) * durationHours * 100;
    });
    return Math.round(totalTSS);
  };

  const addStep = (type: WorkoutStep['type']) => {
    const newStep: WorkoutStep = {
      id: `step-${Date.now()}`,
      type,
      durationType: 'time',
      duration: 600, // 10 minutes default
      targetType: 'power',
      targetZone: 'Zone 2',
      notes: '',
    };
    setWorkout({ ...workout, steps: [...workout.steps, newStep] });
  };

  const handleDragEnd = (result: any) => {
    if (!result.destination) return;
    const items = Array.from(workout.steps);
    const [reorderedItem] = items.splice(result.source.index, 1);
    items.splice(result.destination.index, 0, reorderedItem);
    setWorkout({ ...workout, steps: items });
  };

  const formatDuration = (seconds: number): string => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  return (
    <Box sx={{ display: 'flex', height: '100vh', gap: 2, p: 2 }}>
      {/* Left Panel - Step Palette */}
      <Card sx={{ width: 250, height: 'fit-content' }}>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            Add Steps
          </Typography>
          <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1 }}>
            <Button
              variant="outlined"
              startIcon={<AddIcon />}
              onClick={() => addStep('warmup')}
              sx={{ justifyContent: 'flex-start' }}
            >
              Warmup
            </Button>
            <Button
              variant="outlined"
              startIcon={<AddIcon />}
              onClick={() => addStep('interval')}
              sx={{ justifyContent: 'flex-start' }}
            >
              Interval
            </Button>
            <Button
              variant="outlined"
              startIcon={<AddIcon />}
              onClick={() => addStep('recovery')}
              sx={{ justifyContent: 'flex-start' }}
            >
              Recovery
            </Button>
            <Button
              variant="outlined"
              startIcon={<AddIcon />}
              onClick={() => addStep('cooldown')}
              sx={{ justifyContent: 'flex-start' }}
            >
              Cooldown
            </Button>
          </Box>
        </CardContent>
      </Card>

      {/* Center Panel - Workout Timeline */}
      <Card sx={{ flex: 1 }}>
        <CardContent>
          <Box sx={{ mb: 3 }}>
            <TextField
              fullWidth
              label="Workout Name"
              value={workout.name}
              onChange={(e) => setWorkout({ ...workout, name: e.target.value })}
              sx={{ mb: 2 }}
            />
            <FormControl sx={{ minWidth: 200 }}>
              <InputLabel>Sport</InputLabel>
              <Select
                value={workout.sport}
                label="Sport"
                onChange={(e) =>
                  setWorkout({
                    ...workout,
                    sport: e.target.value as 'run' | 'bike' | 'swim',
                  })
                }
              >
                <MenuItem value="run">🏃 Run</MenuItem>
                <MenuItem value="bike">🚴 Bike</MenuItem>
                <MenuItem value="swim">🏊 Swim</MenuItem>
              </Select>
            </FormControl>
          </Box>

          <Divider sx={{ mb: 2 }} />

          <Typography variant="h6" gutterBottom>
            Workout Structure
          </Typography>

          <DragDropContext onDragEnd={handleDragEnd}>
            <Droppable droppableId="workout-steps">
              {(provided) => (
                <Box
                  {...provided.droppableProps}
                  ref={provided.innerRef}
                  sx={{ minHeight: 400 }}
                >
                  {workout.steps.map((step, index) => (
                    <Draggable key={step.id} draggableId={step.id} index={index}>
                      {(provided) => (
                        <Card
                          ref={provided.innerRef}
                          {...provided.draggableProps}
                          sx={{
                            mb: 1,
                            borderLeft: `4px solid ${stepColors[step.type]}`,
                            cursor: 'pointer',
                            '&:hover': { bgcolor: 'action.hover' },
                          }}
                          onClick={() => {
                            setSelectedStep(step.id);
                            setEditDialogOpen(true);
                          }}
                        >
                          <CardContent sx={{ display: 'flex', alignItems: 'center', py: 1 }}>
                            <Box {...provided.dragHandleProps}>
                              <DragIcon sx={{ color: 'text.secondary', mr: 1 }} />
                            </Box>
                            <Box sx={{ flex: 1 }}>
                              <Typography variant="body1" sx={{ fontWeight: 500 }}>
                                {step.type.charAt(0).toUpperCase() + step.type.slice(1)}
                              </Typography>
                              <Typography variant="caption" color="text.secondary">
                                {formatDuration(step.duration)} • {step.targetZone}
                              </Typography>
                            </Box>
                            <IconButton
                              size="small"
                              onClick={(e) => {
                                e.stopPropagation();
                                // Duplicate step
                              }}
                            >
                              <CopyIcon fontSize="small" />
                            </IconButton>
                            <IconButton
                              size="small"
                              onClick={(e) => {
                                e.stopPropagation();
                                setWorkout({
                                  ...workout,
                                  steps: workout.steps.filter((s) => s.id !== step.id),
                                });
                              }}
                            >
                              <DeleteIcon fontSize="small" />
                            </IconButton>
                          </CardContent>
                        </Card>
                      )}
                    </Draggable>
                  ))}
                  {provided.placeholder}
                </Box>
              )}
            </Droppable>
          </DragDropContext>

          {workout.steps.length === 0 && (
            <Box
              sx={{
                textAlign: 'center',
                py: 8,
                color: 'text.secondary',
              }}
            >
              <Typography variant="body1">
                Add steps from the left panel to build your workout
              </Typography>
            </Box>
          )}

          <Divider sx={{ my: 2 }} />

          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <Box>
              <Typography variant="h6">
                Total Duration:{' '}
                {formatDuration(workout.steps.reduce((sum, s) => sum + s.duration, 0))}
              </Typography>
            </Box>
            <Chip
              label={`Estimated TSS: ${calculateTSS()}`}
              color={calculateTSS() > 150 ? 'error' : 'primary'}
              sx={{ fontSize: '1rem', py: 2 }}
            />
          </Box>
        </CardContent>
      </Card>

      {/* Right Panel - Step Properties (in Dialog) */}
      <Dialog
        open={editDialogOpen}
        onClose={() => setEditDialogOpen(false)}
        maxWidth="sm"
        fullWidth
      >
        <DialogTitle>Step Properties</DialogTitle>
        <DialogContent>
          <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2, mt: 1 }}>
            <FormControl>
              <Typography variant="subtitle2" gutterBottom>
                Duration
              </Typography>
              <RadioGroup row defaultValue="time">
                <FormControlLabel value="time" control={<Radio />} label="Time" />
                <FormControlLabel value="distance" control={<Radio />} label="Distance" />
                <FormControlLabel value="lap" control={<Radio />} label="Lap Button" />
              </RadioGroup>
              <TextField
                type="number"
                label="Duration (seconds)"
                defaultValue={600}
                sx={{ mt: 1 }}
              />
            </FormControl>

            <FormControl>
              <Typography variant="subtitle2" gutterBottom>
                Target
              </Typography>
              <RadioGroup row defaultValue="power">
                <FormControlLabel value="hr" control={<Radio />} label="Heart Rate" />
                <FormControlLabel value="power" control={<Radio />} label="Power" />
                <FormControlLabel value="pace" control={<Radio />} label="Pace" />
              </RadioGroup>
              <Select defaultValue="Zone 4" sx={{ mt: 1 }}>
                <MenuItem value="Zone 1">Zone 1 (Recovery)</MenuItem>
                <MenuItem value="Zone 2">Zone 2 (Endurance)</MenuItem>
                <MenuItem value="Zone 3">Zone 3 (Tempo)</MenuItem>
                <MenuItem value="Zone 4">Zone 4 (Threshold)</MenuItem>
                <MenuItem value="Zone 5">Zone 5 (VO2 Max)</MenuItem>
              </Select>
            </FormControl>

            <TextField label="Custom Min" type="number" placeholder="240 watts" />
            <TextField label="Custom Max" type="number" placeholder="260 watts" />

            <TextField
              label="Notes"
              multiline
              rows={3}
              placeholder="Instructions for this step..."
            />

            <FormControlLabel
              control={<Checkbox />}
              label="Repeat this step"
            />
            <TextField label="Repeat Count" type="number" defaultValue={1} disabled />
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setEditDialogOpen(false)}>Cancel</Button>
          <Button variant="contained" onClick={() => setEditDialogOpen(false)}>
            Save
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default WorkoutBuilder;
```

### Example 3: Workout Library Grid

```tsx
import React, { useState } from 'react';
import {
  Box,
  Card,
  CardContent,
  CardActions,
  Grid,
  TextField,
  Select,
  MenuItem,
  Button,
  IconButton,
  Typography,
  Chip,
  Menu,
  ListItemIcon,
  ListItemText,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Checkbox,
  FormControl,
  InputLabel,
  InputAdornment,
} from '@mui/material';
import {
  Search as SearchIcon,
  MoreVert as MoreIcon,
  Event as ScheduleIcon,
  Edit as EditIcon,
  ContentCopy as CopyIcon,
  Folder as FolderIcon,
  Delete as DeleteIcon,
  FilterList as FilterIcon,
  Add as AddIcon,
} from '@mui/icons-material';
import { DatePicker } from '@mui/x-date-pickers';

interface Workout {
  id: string;
  name: string;
  sport: 'run' | 'bike' | 'swim';
  duration: number;
  tss: number;
  primaryZone: string;
  steps: number;
  tags: string[];
  folder: string;
}

const WorkoutLibrary: React.FC = () => {
  const [workouts, setWorkouts] = useState<Workout[]>([
    {
      id: '1',
      name: 'Threshold Intervals',
      sport: 'bike',
      duration: 3600,
      tss: 75,
      primaryZone: 'Zone 4',
      steps: 6,
      tags: ['intervals', 'threshold'],
      folder: 'Bike/Threshold',
    },
    // More workouts...
  ]);

  const [searchQuery, setSearchQuery] = useState('');
  const [sportFilter, setSportFilter] = useState('all');
  const [tssFilter, setTssFilter] = useState('all');
  const [anchorEl, setAnchorEl] = useState<null | HTMLElement>(null);
  const [selectedWorkout, setSelectedWorkout] = useState<string | null>(null);
  const [scheduleDialogOpen, setScheduleDialogOpen] = useState(false);
  const [selectedDate, setSelectedDate] = useState<Date | null>(new Date());

  const sportIcons = {
    run: '🏃',
    bike: '🚴',
    swim: '🏊',
  };

  const stepColors = ['#4CAF50', '#F44336', '#FFC107', '#2196F3', '#9E9E9E'];

  const handleMenuClick = (event: React.MouseEvent<HTMLElement>, workoutId: string) => {
    setAnchorEl(event.currentTarget);
    setSelectedWorkout(workoutId);
  };

  const handleSchedule = () => {
    setScheduleDialogOpen(true);
    setAnchorEl(null);
  };

  const formatDuration = (seconds: number): string => {
    const hours = Math.floor(seconds / 3600);
    const mins = Math.floor((seconds % 3600) / 60);
    return hours > 0 ? `${hours}h ${mins}m` : `${mins} min`;
  };

  return (
    <Box sx={{ p: 3 }}>
      {/* Header */}
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Typography variant="h4">Workout Library</Typography>
        <Button variant="contained" startIcon={<AddIcon />}>
          Create Workout
        </Button>
      </Box>

      {/* Search & Filters */}
      <Box sx={{ display: 'flex', gap: 2, mb: 3 }}>
        <TextField
          fullWidth
          placeholder="Search workouts..."
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
          InputProps={{
            startAdornment: (
              <InputAdornment position="start">
                <SearchIcon />
              </InputAdornment>
            ),
          }}
        />
        <FormControl sx={{ minWidth: 150 }}>
          <InputLabel>Sport</InputLabel>
          <Select
            value={sportFilter}
            label="Sport"
            onChange={(e) => setSportFilter(e.target.value)}
          >
            <MenuItem value="all">All Sports</MenuItem>
            <MenuItem value="run">🏃 Run</MenuItem>
            <MenuItem value="bike">🚴 Bike</MenuItem>
            <MenuItem value="swim">🏊 Swim</MenuItem>
          </Select>
        </FormControl>
        <FormControl sx={{ minWidth: 150 }}>
          <InputLabel>TSS Range</InputLabel>
          <Select
            value={tssFilter}
            label="TSS Range"
            onChange={(e) => setTssFilter(e.target.value)}
          >
            <MenuItem value="all">All TSS</MenuItem>
            <MenuItem value="0-50">0-50</MenuItem>
            <MenuItem value="50-100">50-100</MenuItem>
            <MenuItem value="100-150">100-150</MenuItem>
            <MenuItem value="150+">150+</MenuItem>
          </Select>
        </FormControl>
      </Box>

      {/* Workout Grid */}
      <Grid container spacing={2}>
        {workouts.map((workout) => (
          <Grid item xs={12} sm={6} md={4} lg={3} key={workout.id}>
            <Card
              sx={{
                height: '100%',
                display: 'flex',
                flexDirection: 'column',
                '&:hover': { boxShadow: 6 },
                transition: 'box-shadow 0.3s',
              }}
            >
              <CardContent sx={{ flex: 1 }}>
                <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                  <Typography variant="h6" component="div">
                    {sportIcons[workout.sport]} {workout.name}
                  </Typography>
                  <IconButton
                    size="small"
                    onClick={(e) => handleMenuClick(e, workout.id)}
                  >
                    <MoreIcon />
                  </IconButton>
                </Box>

                <Box sx={{ display: 'flex', gap: 2, mb: 2 }}>
                  <Chip label={formatDuration(workout.duration)} size="small" />
                  <Chip
                    label={`${workout.tss} TSS`}
                    size="small"
                    color={workout.tss > 100 ? 'error' : 'default'}
                  />
                  <Chip label={workout.primaryZone} size="small" variant="outlined" />
                </Box>

                {/* Visual Timeline */}
                <Box sx={{ display: 'flex', height: 8, gap: 0.5, mb: 2 }}>
                  {Array.from({ length: workout.steps }).map((_, i) => (
                    <Box
                      key={i}
                      sx={{
                        flex: 1,
                        bgcolor: stepColors[i % stepColors.length],
                        borderRadius: 0.5,
                      }}
                    />
                  ))}
                </Box>

                <Box sx={{ display: 'flex', gap: 0.5, flexWrap: 'wrap' }}>
                  {workout.tags.map((tag) => (
                    <Chip key={tag} label={tag} size="small" variant="outlined" />
                  ))}
                </Box>
              </CardContent>

              <CardActions>
                <Button size="small" startIcon={<ScheduleIcon />} onClick={handleSchedule}>
                  Schedule
                </Button>
                <Button size="small" startIcon={<EditIcon />}>
                  Edit
                </Button>
              </CardActions>
            </Card>
          </Grid>
        ))}
      </Grid>

      {/* Context Menu */}
      <Menu
        anchorEl={anchorEl}
        open={Boolean(anchorEl)}
        onClose={() => setAnchorEl(null)}
      >
        <MenuItem onClick={handleSchedule}>
          <ListItemIcon>
            <ScheduleIcon fontSize="small" />
          </ListItemIcon>
          <ListItemText>Schedule to Calendar</ListItemText>
        </MenuItem>
        <MenuItem onClick={() => setAnchorEl(null)}>
          <ListItemIcon>
            <EditIcon fontSize="small" />
          </ListItemIcon>
          <ListItemText>Edit</ListItemText>
        </MenuItem>
        <MenuItem onClick={() => setAnchorEl(null)}>
          <ListItemIcon>
            <CopyIcon fontSize="small" />
          </ListItemIcon>
          <ListItemText>Duplicate</ListItemText>
        </MenuItem>
        <MenuItem onClick={() => setAnchorEl(null)}>
          <ListItemIcon>
            <FolderIcon fontSize="small" />
          </ListItemIcon>
          <ListItemText>Move to Folder</ListItemText>
        </MenuItem>
        <MenuItem onClick={() => setAnchorEl(null)}>
          <ListItemIcon>
            <DeleteIcon fontSize="small" />
          </ListItemIcon>
          <ListItemText>Delete</ListItemText>
        </MenuItem>
      </Menu>

      {/* Schedule Dialog */}
      <Dialog
        open={scheduleDialogOpen}
        onClose={() => setScheduleDialogOpen(false)}
        maxWidth="xs"
        fullWidth
      >
        <DialogTitle>Schedule Workout</DialogTitle>
        <DialogContent>
          <DatePicker
            label="Select Date"
            value={selectedDate}
            onChange={(date) => setSelectedDate(date)}
            sx={{ mt: 2, width: '100%' }}
          />
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setScheduleDialogOpen(false)}>Cancel</Button>
          <Button variant="contained" onClick={() => setScheduleDialogOpen(false)}>
            Schedule
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default WorkoutLibrary;
```

---

## 5. Ten Key Patterns to Adopt

### Pattern 1: **Progressive Metric Display** (Priority: HIGH, Effort: MEDIUM)
**Description**: Show summary metrics in cards with sparklines, drill down to detailed charts on click.

**Implementation**:
- 4-card metric row above PMC chart
- Each card shows: primary value, % change, mini trend graph (7-14 days)
- Click card → Opens modal with detailed breakdown

**Why**: Reduces cognitive load, faster page load, user controls detail level

---

### Pattern 2: **Dual-Axis Composite Chart** (Priority: HIGH, Effort: HIGH)
**Description**: PMC chart combines lines (CTL/ATL) + bars (TSS/TSB) on different Y-axes.

**Implementation**:
- Use `recharts` ComposedChart with multiple `yAxisId` values
- Left axis: TSS/CTL/ATL (0-200 range)
- Right axis: TSB (-50 to +50 range)
- Bars for daily/balance, lines for trends

**Why**: Industry-standard visualization, shows all training load data in one view

---

### Pattern 3: **Drag-and-Drop Workout Builder** (Priority: HIGH, Effort: HIGH)
**Description**: Visual timeline where users drag steps from palette and reorder.

**Implementation**:
- Use `react-beautiful-dnd` library
- Left palette with step types (Warmup, Interval, etc.)
- Center timeline with colored step cards
- Click step → Right panel shows properties editor

**Why**: Intuitive, visual, reduces errors vs text-based entry

---

### Pattern 4: **Color-Coded Training Zones** (Priority: HIGH, Effort: LOW)
**Description**: Consistent color scheme for workout intensity across all views.

**Implementation**:
```typescript
const zoneColors = {
  warmup: '#4CAF50',    // Green
  interval: '#F44336',  // Red
  recovery: '#FFC107',  // Yellow
  cooldown: '#2196F3',  // Blue
  rest: '#9E9E9E',      // Gray
};
```

**Why**: Instant visual recognition, reduces reading time

---

### Pattern 5: **Contextual Quick Actions Menu** (Priority: MEDIUM, Effort: LOW)
**Description**: Three-dot menu (⋮) on every workout card with common actions.

**Implementation**:
- Material-UI `Menu` component triggered by `MoreVertIcon`
- Actions: Schedule, Edit, Duplicate, Move, Delete
- Context-aware (disabled states based on permissions)

**Why**: Reduces clicks, discoverable, mobile-friendly

---

### Pattern 6: **Real-Time TSS Calculation** (Priority: MEDIUM, Effort: MEDIUM)
**Description**: Show estimated TSS as workout is built, updates live.

**Implementation**:
```typescript
const calculateTSS = (steps: WorkoutStep[]): number => {
  return steps.reduce((total, step) => {
    const hours = step.duration / 3600;
    const if_value = getIntensityFactor(step.zone);
    return total + (Math.pow(if_value, 2) * hours * 100);
  }, 0);
};
```
- Display as Chip with color coding (green < 150, yellow 150-300, red > 300)

**Why**: Prevents accidental overtraining, educational

---

### Pattern 7: **Folder Hierarchy with Breadcrumbs** (Priority: MEDIUM, Effort: LOW)
**Description**: Nested folders for workouts with breadcrumb navigation.

**Implementation**:
```tsx
<Breadcrumbs>
  <Link href="/library">My Workouts</Link>
  <Link href="/library/bike">Bike</Link>
  <Typography color="text.primary">Threshold</Typography>
</Breadcrumbs>
```

**Why**: Scales to hundreds of workouts, familiar pattern

---

### Pattern 8: **Preview Timeline Visualization** (Priority: LOW, Effort: LOW)
**Description**: Small colored bar showing workout structure on library cards.

**Implementation**:
```tsx
<Box sx={{ display: 'flex', height: 8, gap: 0.5 }}>
  {steps.map((step, i) => (
    <Box key={i} sx={{ flex: 1, bgcolor: zoneColors[step.type] }} />
  ))}
</Box>
```

**Why**: Quick visual scan, no need to open workout to understand structure

---

### Pattern 9: **Bulk Selection with Action Bar** (Priority: LOW, Effort: MEDIUM)
**Description**: Checkbox mode for selecting multiple workouts, sticky action bar appears.

**Implementation**:
- Checkbox on each card (hidden until first selection)
- Sticky bar at top: "3 selected | Move | Tag | Delete"
- Cancel button exits selection mode

**Why**: Power user feature, efficient for organizing large libraries

---

### Pattern 10: **Split Save Actions** (Priority: HIGH, Effort: LOW)
**Description**: Two save buttons: "Save to Library" vs "Schedule & Save".

**Implementation**:
```tsx
<DialogActions>
  <Button variant="outlined">Save to Library</Button>
  <Button variant="contained">Schedule & Save</Button>
</DialogActions>
```

**Why**: Clarifies intent, prevents accidental scheduling, reduces steps for common flow

---

## 6. Implementation Priority Matrix

| Pattern | Priority | Effort | Impact | Implement First |
|---------|----------|--------|--------|-----------------|
| Progressive Metric Display | HIGH | MEDIUM | HIGH | ✅ Phase 1 |
| Dual-Axis PMC Chart | HIGH | HIGH | HIGH | ✅ Phase 1 |
| Drag-and-Drop Builder | HIGH | HIGH | HIGH | ✅ Phase 2 |
| Color-Coded Zones | HIGH | LOW | HIGH | ✅ Phase 1 |
| Split Save Actions | HIGH | LOW | MEDIUM | ✅ Phase 2 |
| Real-Time TSS Calc | MEDIUM | MEDIUM | MEDIUM | Phase 2 |
| Quick Actions Menu | MEDIUM | LOW | MEDIUM | Phase 2 |
| Folder Hierarchy | MEDIUM | LOW | MEDIUM | Phase 3 |
| Preview Timeline | LOW | LOW | LOW | Phase 3 |
| Bulk Selection | LOW | MEDIUM | LOW | Phase 4 |

---

## 7. Design System Tokens

### Colors (Training Zones)
```typescript
export const trainingZones = {
  zone1: { name: 'Recovery', color: '#90EE90', range: '< 55% FTP' },
  zone2: { name: 'Endurance', color: '#4CAF50', range: '55-75% FTP' },
  zone3: { name: 'Tempo', color: '#FFC107', range: '75-90% FTP' },
  zone4: { name: 'Threshold', color: '#FF9800', range: '90-105% FTP' },
  zone5: { name: 'VO2 Max', color: '#F44336', range: '105-120% FTP' },
  zone6: { name: 'Anaerobic', color: '#9C27B0', range: '> 120% FTP' },
};
```

### Typography Scale
```typescript
export const typography = {
  metricValue: { fontSize: '2rem', fontWeight: 700 },
  metricLabel: { fontSize: '0.75rem', fontWeight: 500, textTransform: 'uppercase' },
  workoutTitle: { fontSize: '1.125rem', fontWeight: 600 },
  stepLabel: { fontSize: '0.875rem', fontWeight: 500 },
};
```

### Spacing
```typescript
export const spacing = {
  cardPadding: theme.spacing(2),
  cardGap: theme.spacing(2),
  metricCardMinHeight: 120,
  chartHeight: 400,
  stepCardHeight: 56,
};
```

---

## 8. Mobile Responsiveness Strategy

### Breakpoint Behavior
```typescript
const isMobile = useMediaQuery(theme.breakpoints.down('md'));

// Dashboard Layout
{isMobile ? (
  // Stack metric cards vertically, PMC chart full width
  <Box sx={{ flexDirection: 'column' }}>
    <Grid container spacing={1}>
      {metricCards.map(card => (
        <Grid item xs={6}>{card}</Grid>
      ))}
    </Grid>
    <Box sx={{ mt: 2 }}>{pmcChart}</Box>
  </Box>
) : (
  // Desktop 3-column layout
  <Grid container spacing={2}>
    <Grid item xs={3}>{leftPanel}</Grid>
    <Grid item xs={6}>{centerPanel}</Grid>
    <Grid item xs={3}>{rightPanel}</Grid>
  </Grid>
)}
```

### Touch-Friendly Targets
- Minimum button height: 44px
- Card tap area: Full card clickable
- Swipe gestures: Left swipe on workout card reveals actions
- Bottom sheet: Use drawer from bottom for mobile forms

---

## 9. Accessibility Considerations

### ARIA Labels
```tsx
<IconButton aria-label="Edit workout">
  <EditIcon />
</IconButton>

<Chip 
  label="75 TSS" 
  aria-label="Training Stress Score 75"
/>
```

### Keyboard Navigation
- Tab order: Logical flow through form fields
- Enter key: Submits forms, opens dialogs
- Escape key: Closes dialogs, cancels selections
- Arrow keys: Navigate through workout steps in builder

### Screen Reader Support
```tsx
<Box role="region" aria-labelledby="pmc-chart-title">
  <Typography id="pmc-chart-title" variant="h6">
    Performance Management Chart
  </Typography>
  <ResponsiveContainer>
    {/* Chart with descriptive labels */}
  </ResponsiveContainer>
</Box>
```

---

## 10. Performance Optimization

### Chart Rendering
- Debounce chart updates on window resize (300ms)
- Virtualize long workout lists (react-window)
- Lazy load chart library (dynamic import)
- Use `useMemo` for expensive TSS calculations

### Data Loading
```typescript
// Fetch dashboard data in parallel
const fetchDashboard = async () => {
  const [stats, activities, workouts] = await Promise.all([
    api.get('/stats/weekly'),
    api.get('/activities/recent'),
    api.get('/workouts/upcoming'),
  ]);
  return { stats, activities, workouts };
};
```

### Image Optimization
- Use SVG icons (Material-UI icons)
- Sport icons as emoji (no image requests)
- Lazy load activity maps (only when expanded)

---

## 11. Next Steps for TrainingPlan

### Immediate Actions (This Week)
1. **Implement Pattern #4**: Color-coded training zones (LOW effort, HIGH impact)
2. **Create metric cards**: Weekly TSS, Volume, IF, VI (Pattern #1)
3. **Add quick actions menu**: To existing workout cards (Pattern #5)

### Phase 1 (Next 2 Weeks)
1. **PMC Chart Component**: Dual-axis with CTL/ATL/TSB (Pattern #2)
2. **Dashboard Layout**: Implement 3-column responsive grid
3. **Workout Library Grid**: Replace list view with cards (Pattern #8)

### Phase 2 (Next Month)
1. **Workout Builder**: Drag-and-drop interface (Pattern #3)
2. **Real-time TSS**: Live calculation display (Pattern #6)
3. **Split Save Actions**: Library vs Schedule buttons (Pattern #10)

### Phase 3 (Future)
1. Folder hierarchy for workouts
2. Bulk operations
3. Advanced filters and search

---

## Conclusion

TrainingPeaks excels at **information density without overwhelming users**. Key takeaways:

1. **Progressive disclosure**: Show summaries first, details on demand
2. **Visual hierarchy**: Use color, size, spacing to guide attention
3. **Consistent patterns**: Same actions work same way everywhere
4. **Real-time feedback**: Users always know current state (TSS, form, etc.)
5. **Mobile-first actions**: Touch targets, swipe gestures, bottom sheets

Adopt these patterns incrementally, starting with high-impact/low-effort changes (color zones, metric cards, quick actions). Build momentum toward complex features (PMC chart, workout builder).

**Success Metric**: Users should be able to check their training status in < 5 seconds and schedule a workout in < 30 seconds.
