# TrainingPeaks UX Reference Guide for TrainingPlan

**Last Updated**: 2026-01-02  
**Purpose**: Design reference based on industry leader TrainingPeaks  
**Status**: 📋 Blueprint for TrainingPlan UI/UX development

---

## Overview

TrainingPeaks is the **industry gold standard** for training management software. This document captures their UX patterns, design decisions, and implementation strategies to guide TrainingPlan development.

**Why TrainingPeaks as Reference:**
- 20+ years of UX refinement
- Used by professional athletes and coaches worldwide
- Calendar-centric design (matches TrainingPlan's vision)
- Proven multi-sport workflow patterns
- Industry-leading analytics dashboard

---

## Part 1: Navigation Architecture

### TrainingPeaks Navigation Structure

**Primary Navigation** (Top Bar):
```
┌────────────────────────────────────────────────────────────────┐
│ [TP Logo]  Dashboard | Calendar | Workouts | Reports | [🔔] [👤] │
│            ^active                                              │
└────────────────────────────────────────────────────────────────┘
```

**Key Elements:**
1. **Logo** (top-left): Always returns to Dashboard
2. **Tab Navigation**: Horizontal tabs for primary sections
3. **Active Indicator**: Underline + bold text for current page
4. **Notifications Icon**: Bell icon with badge count
5. **User Menu**: Avatar → Profile, Settings, Logout

**TrainingPlan Implementation:**
```tsx
// components/MainAppBar.tsx
import { AppBar, Toolbar, Tabs, Tab, IconButton, Avatar, Menu, MenuItem } from '@mui/material'
import { Notifications, Dashboard, CalendarMonth, FitnessCenter, Assessment } from '@mui/icons-material'

const MainAppBar = () => {
  const location = useLocation()
  const navigate = useNavigate()
  const [anchorEl, setAnchorEl] = useState<null | HTMLElement>(null)
  
  const currentTab = 
    location.pathname.startsWith('/dashboard') ? 0 :
    location.pathname.startsWith('/calendar') ? 1 :
    location.pathname.startsWith('/plans') ? 2 :
    location.pathname.startsWith('/analytics') ? 3 : 0

  return (
    <AppBar position="sticky" color="default" elevation={1}>
      <Toolbar>
        {/* Logo */}
        <Box 
          sx={{ cursor: 'pointer', display: 'flex', alignItems: 'center', mr: 4 }}
          onClick={() => navigate('/dashboard')}
        >
          <Typography variant="h6" sx={{ fontWeight: 700 }}>
            🏃 TrainingPlan
          </Typography>
        </Box>

        {/* Primary Navigation Tabs */}
        <Tabs value={currentTab} sx={{ flexGrow: 1 }}>
          <Tab 
            icon={<Dashboard />} 
            iconPosition="start"
            label="Dashboard" 
            onClick={() => navigate('/dashboard')}
          />
          <Tab 
            icon={<CalendarMonth />} 
            iconPosition="start"
            label="Calendar" 
            onClick={() => navigate('/calendar')}
          />
          <Tab 
            icon={<FitnessCenter />} 
            iconPosition="start"
            label="Plans" 
            onClick={() => navigate('/plans')}
          />
          <Tab 
            icon={<Assessment />} 
            iconPosition="start"
            label="Analytics" 
            onClick={() => navigate('/analytics')}
          />
        </Tabs>

        {/* Right Side Icons */}
        <IconButton color="inherit">
          <Badge badgeContent={3} color="error">
            <Notifications />
          </Badge>
        </IconButton>

        <IconButton onClick={(e) => setAnchorEl(e.currentTarget)}>
          <Avatar sx={{ width: 32, height: 32 }}>
            {user?.full_name?.[0] || 'U'}
          </Avatar>
        </IconButton>

        {/* User Menu */}
        <Menu anchorEl={anchorEl} open={Boolean(anchorEl)} onClose={() => setAnchorEl(null)}>
          <MenuItem onClick={() => navigate('/settings')}>Settings</MenuItem>
          <MenuItem onClick={() => navigate('/profile')}>Profile</MenuItem>
          <Divider />
          <MenuItem onClick={logout}>Logout</MenuItem>
        </Menu>
      </Toolbar>
    </AppBar>
  )
}
```

**Why This Works:**
- ✅ **Muscle memory**: Users know where everything is
- ✅ **No scrolling needed**: All navigation visible at once
- ✅ **Persistent**: Never disappears (no orphaned pages)
- ✅ **Clear hierarchy**: Primary actions in tabs, secondary in menus

---

## Part 2: Calendar Interface

### TrainingPeaks Calendar Design

**Default View**: **Week View** (Monday-Sunday)
- Most useful for athletes planning weekly training blocks
- Shows 7-14 days of context
- Easy to drag workouts between days

**Visual Structure:**
```
┌─────────────────────────────────────────────────────────────────┐
│ [< Today >] [Week of Jan 1-7, 2026]              [Day|Week|Month]│
├─────┬─────┬─────┬─────┬─────┬─────┬─────────────────────────────┤
│ MON │ TUE │ WED │ THU │ FRI │ SAT │ SUN                          │
│ 1/1 │ 1/2 │ 1/3 │ 1/4 │ 1/5 │ 1/6 │ 1/7                          │
│─────│─────│─────│─────│─────│─────│─────                         │
│ ┌─┐ │ ┌─┐ │     │ ┌─┐ │ ┌─┐ │ ┌─┐ │ ┌─┐                          │
│ │🏃│ │ │🚴│ │     │ │🏃│ │ │🏊│ │ │🚴│ │ │🏃│  ← Planned workouts  │
│ │ │ │ │ │ │     │ │ │ │ │ │ │ │ │ │ │ │                          │
│ └─┘ │ └─┘ │     │ └─┘ │ └─┘ │ └─┘ │ └─┘                          │
│ ✓   │ ✓   │     │     │     │     │                              │
│─────│─────│─────│─────│─────│─────│─────                         │
│TSS  │TSS  │TSS  │TSS  │TSS  │TSS  │TSS                           │
│ 85  │ 95  │ 0   │ 75  │ 60  │ 120 │ 100  ← Daily TSS totals      │
└─────┴─────┴─────┴─────┴─────┴─────┴─────────────────────────────┘
```

### Workout Visual Differentiation

**Planned Workout** (Not Started):
```tsx
<Card 
  sx={{ 
    border: '2px dashed',
    borderColor: 'primary.main',
    bgcolor: 'background.paper',
    opacity: 0.8
  }}
>
  <CardContent sx={{ p: 1 }}>
    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
      <DirectionsRun sx={{ color: 'success.main' }} />
      <Typography variant="body2" fontWeight={500}>
        Easy Run
      </Typography>
    </Box>
    <Typography variant="caption" color="text.secondary">
      45 min • Zone 2
    </Typography>
    <Chip label="TSS 45" size="small" sx={{ mt: 0.5 }} />
  </CardContent>
</Card>
```

**Completed Workout** (Done):
```tsx
<Card 
  sx={{ 
    border: '2px solid',
    borderColor: 'success.main',
    bgcolor: 'success.light',
    opacity: 1
  }}
>
  <CardContent sx={{ p: 1 }}>
    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
      <DirectionsRun sx={{ color: 'success.dark' }} />
      <CheckCircle sx={{ fontSize: 16, color: 'success.dark' }} />
      <Typography variant="body2" fontWeight={600}>
        Easy Run
      </Typography>
    </Box>
    <Typography variant="caption" color="text.secondary">
      Completed: 47 min • Zone 2
    </Typography>
    <Box sx={{ display: 'flex', gap: 0.5, mt: 0.5 }}>
      <Chip label="Actual TSS 48" size="small" color="success" />
      <Chip label="Planned TSS 45" size="small" variant="outlined" />
    </Box>
  </CardContent>
</Card>
```

**Skipped Workout**:
```tsx
<Card 
  sx={{ 
    border: '1px solid',
    borderColor: 'grey.400',
    bgcolor: 'grey.100',
    opacity: 0.5,
    position: 'relative'
  }}
>
  <Box 
    sx={{ 
      position: 'absolute', 
      top: 0, 
      left: 0, 
      right: 0, 
      bottom: 0,
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center'
    }}
  >
    <Typography variant="h6" color="text.disabled" sx={{ fontWeight: 700 }}>
      SKIPPED
    </Typography>
  </Box>
  <CardContent sx={{ p: 1, filter: 'blur(1px)' }}>
    {/* Workout content with blur effect */}
  </CardContent>
</Card>
```

### Sport Color Coding

**TrainingPeaks Color System:**
- 🏃 **Running**: `#4CAF50` (Green)
- 🚴 **Cycling**: `#FF9800` (Orange)
- 🏊 **Swimming**: `#2196F3` (Blue)
- 💪 **Strength**: `#9C27B0` (Purple)
- 🧘 **Other/Yoga**: `#607D8B` (Grey)

**Implementation:**
```tsx
// utils/sportColors.ts
export const SPORT_COLORS = {
  running: { main: '#4CAF50', light: '#E8F5E9', dark: '#2E7D32' },
  cycling: { main: '#FF9800', light: '#FFF3E0', dark: '#E65100' },
  swimming: { main: '#2196F3', light: '#E3F2FD', dark: '#1565C0' },
  strength: { main: '#9C27B0', light: '#F3E5F5', dark: '#6A1B9A' },
  other: { main: '#607D8B', light: '#ECEFF1', dark: '#37474F' },
}

export const getSportColor = (sport: string) => {
  return SPORT_COLORS[sport.toLowerCase()] || SPORT_COLORS.other
}
```

### Daily TSS Summary Badge

**Visual:**
```tsx
<Box 
  sx={{ 
    display: 'flex', 
    justifyContent: 'space-between',
    alignItems: 'center',
    p: 1,
    bgcolor: getTSSBackgroundColor(dailyTSS),
    borderTop: 1,
    borderColor: 'divider'
  }}
>
  <Typography variant="caption" fontWeight={600}>
    Total TSS
  </Typography>
  <Chip 
    label={dailyTSS}
    size="small"
    sx={{
      bgcolor: getTSSChipColor(dailyTSS),
      color: 'white',
      fontWeight: 700
    }}
  />
</Box>

// TSS Color Coding
const getTSSChipColor = (tss: number) => {
  if (tss === 0) return 'grey.500'
  if (tss < 50) return 'success.main'  // Easy day (green)
  if (tss < 100) return 'info.main'    // Moderate (blue)
  if (tss < 150) return 'warning.main' // Hard (orange)
  return 'error.main'                   // Very hard (red)
}
```

### Add Workout Interaction

**TrainingPeaks Pattern**: Click empty cell → Quick add dialog

```tsx
const handleDayClick = (date: Date) => {
  setSelectedDate(date)
  setQuickAddDialogOpen(true)
}

<Dialog open={quickAddDialogOpen} maxWidth="sm" fullWidth>
  <DialogTitle>
    Add Workout for {format(selectedDate, 'EEEE, MMM d')}
  </DialogTitle>
  <DialogContent>
    <Stack spacing={2} sx={{ mt: 1 }}>
      {/* Quick sport selection */}
      <ToggleButtonGroup exclusive value={sport} onChange={(e, val) => setSport(val)}>
        <ToggleButton value="running">
          <DirectionsRun /> Run
        </ToggleButton>
        <ToggleButton value="cycling">
          <DirectionsBike /> Bike
        </ToggleButton>
        <ToggleButton value="swimming">
          <Pool /> Swim
        </ToggleButton>
        <ToggleButton value="strength">
          <FitnessCenter /> Strength
        </ToggleButton>
      </ToggleButtonGroup>

      {/* Quick template selection */}
      <FormControl>
        <InputLabel>Workout Type</InputLabel>
        <Select value={template}>
          <MenuItem value="easy">Easy</MenuItem>
          <MenuItem value="tempo">Tempo</MenuItem>
          <MenuItem value="intervals">Intervals</MenuItem>
          <MenuItem value="long">Long</MenuItem>
          <MenuItem value="recovery">Recovery</MenuItem>
        </Select>
      </FormControl>

      {/* Duration */}
      <TextField 
        label="Duration" 
        type="number"
        InputProps={{ endAdornment: <InputAdornment position="end">min</InputAdornment> }}
      />
    </Stack>
  </DialogContent>
  <DialogActions>
    <Button onClick={() => setQuickAddDialogOpen(false)}>Cancel</Button>
    <Button variant="contained" onClick={handleQuickAdd}>Add</Button>
    <Button variant="outlined" onClick={handleOpenFullBuilder}>
      Advanced Builder
    </Button>
  </DialogActions>
</Dialog>
```

**Why This Works:**
- ✅ **Low friction**: 2 clicks to add workout (click day → select template → done)
- ✅ **Progressive disclosure**: Quick add for speed, "Advanced" for complexity
- ✅ **Context-aware**: Pre-fills date, user just picks workout

---

## Part 3: Dashboard Analytics

### TrainingPeaks Dashboard Layout

**3-Column Responsive Grid:**
```
┌─────────────────────┬─────────────────────┬─────────────────────┐
│  Performance        │  Training Stress    │  Recent Activities  │
│  Management Chart   │  Balance (TSB)      │                     │
│  (CTL/ATL/TSB)      │                     │  [Activity cards]   │
│                     │  [Gauge chart]      │                     │
│  [Line chart]       │                     │                     │
├─────────────────────┼─────────────────────┼─────────────────────┤
│  Fitness (CTL)      │  Fatigue (ATL)      │  Form (TSB)         │
│  ━━━━━━━━━━━ 85     │  ━━━━━━━━━━━ 42     │  ━━━━━━━━━━━ 43     │
│  +2 vs last week    │  -5 vs last week    │  +7 vs last week    │
├─────────────────────┴─────────────────────┴─────────────────────┤
│  Weekly Summary                                                  │
│  ┌────────┬────────┬────────┬────────┬────────┬────────┬────────┐│
│  │ MON    │ TUE    │ WED    │ THU    │ FRI    │ SAT    │ SUN    ││
│  │ 85 TSS │ 95 TSS │ 0      │ 75 TSS │ 60 TSS │120 TSS │100 TSS ││
│  └────────┴────────┴────────┴────────┴────────┴────────┴────────┘│
│  Total: 535 TSS • 12h 45min • 7 workouts                         │
└──────────────────────────────────────────────────────────────────┘
```

### Performance Management Chart (PMC)

**The Crown Jewel of TrainingPeaks**: Dual-axis line chart showing CTL/ATL/TSB over time

```tsx
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts'

const PerformanceManagementChart = ({ data }: { data: PMCData[] }) => {
  return (
    <Card>
      <CardContent>
        <Typography variant="h6" gutterBottom>
          Performance Management Chart
        </Typography>
        <ResponsiveContainer width="100%" height={300}>
          <LineChart data={data}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="date" />
            <YAxis yAxisId="left" label={{ value: 'Fitness/Fatigue', angle: -90 }} />
            <YAxis yAxisId="right" orientation="right" label={{ value: 'Form (TSB)', angle: 90 }} />
            <Tooltip />
            <Legend />
            
            {/* Fitness (CTL) - Blue line */}
            <Line 
              yAxisId="left"
              type="monotone" 
              dataKey="ctl" 
              stroke="#2196F3" 
              strokeWidth={2}
              name="Fitness (CTL)"
              dot={false}
            />
            
            {/* Fatigue (ATL) - Orange line */}
            <Line 
              yAxisId="left"
              type="monotone" 
              dataKey="atl" 
              stroke="#FF9800" 
              strokeWidth={2}
              name="Fatigue (ATL)"
              dot={false}
            />
            
            {/* Form (TSB) - Area fill */}
            <Line 
              yAxisId="right"
              type="monotone" 
              dataKey="tsb" 
              stroke="#4CAF50" 
              strokeWidth={1}
              name="Form (TSB)"
              fill="#4CAF50"
              fillOpacity={0.2}
              dot={false}
            />
          </LineChart>
        </ResponsiveContainer>
        
        {/* Quick interpretation guide */}
        <Box sx={{ mt: 2, p: 2, bgcolor: 'grey.100', borderRadius: 1 }}>
          <Typography variant="caption" display="block" gutterBottom>
            <strong>Interpretation:</strong>
          </Typography>
          <Typography variant="caption" display="block">
            • <strong>Fitness (CTL)</strong>: Your chronic training load (42-day average). Higher = more fit.
          </Typography>
          <Typography variant="caption" display="block">
            • <strong>Fatigue (ATL)</strong>: Your acute training load (7-day average). Higher = more tired.
          </Typography>
          <Typography variant="caption" display="block">
            • <strong>Form (TSB)</strong>: Fitness - Fatigue. Positive = fresh, Negative = tired.
          </Typography>
        </Box>
      </CardContent>
    </Card>
  )
}
```

### Metric Cards with Trends

```tsx
const MetricCard = ({ title, value, change, icon, color }) => (
  <Card>
    <CardContent>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
        <Box>
          <Typography variant="body2" color="text.secondary" gutterBottom>
            {title}
          </Typography>
          <Typography variant="h3" fontWeight={700}>
            {value}
          </Typography>
          <Box sx={{ display: 'flex', alignItems: 'center', mt: 1 }}>
            {change > 0 ? <TrendingUp fontSize="small" color="success" /> : <TrendingDown fontSize="small" color="error" />}
            <Typography variant="body2" color={change > 0 ? 'success.main' : 'error.main'} sx={{ ml: 0.5 }}>
              {Math.abs(change)} vs last week
            </Typography>
          </Box>
        </Box>
        <Box 
          sx={{ 
            bgcolor: `${color}.light`, 
            p: 1.5, 
            borderRadius: 2,
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center'
          }}
        >
          {icon}
        </Box>
      </Box>
      
      {/* Mini sparkline */}
      <Box sx={{ mt: 2, height: 40 }}>
        <ResponsiveContainer width="100%" height="100%">
          <LineChart data={weeklyData}>
            <Line type="monotone" dataKey="value" stroke={color} strokeWidth={2} dot={false} />
          </LineChart>
        </ResponsiveContainer>
      </Box>
    </CardContent>
  </Card>
)
```

---

## Part 4: Workout Builder

### TrainingPeaks Workout Creation Flow

**5-Step Wizard Approach:**

1. **Basic Info** → Sport, Name, Description
2. **Structure** → Warmup, Main Set, Cooldown
3. **Intervals** → Duration, Target, Repeat
4. **Zones** → HR/Power/Pace targets
5. **Schedule** → Save to library or schedule to date

**Implementation:**
```tsx
const WorkoutBuilder = () => {
  const [activeStep, setActiveStep] = useState(0)
  const [workout, setWorkout] = useState({
    sport: 'running',
    name: '',
    description: '',
    steps: []
  })

  const steps = ['Basic Info', 'Structure', 'Intervals', 'Targets', 'Schedule']

  return (
    <Dialog open={open} fullScreen>
      <AppBar position="relative">
        <Toolbar>
          <Typography variant="h6" sx={{ flexGrow: 1 }}>
            Workout Builder
          </Typography>
          <IconButton color="inherit" onClick={onClose}>
            <Close />
          </IconButton>
        </Toolbar>
      </AppBar>
      
      <Box sx={{ p: 3 }}>
        {/* Stepper */}
        <Stepper activeStep={activeStep} sx={{ mb: 4 }}>
          {steps.map((label) => (
            <Step key={label}>
              <StepLabel>{label}</StepLabel>
            </Step>
          ))}
        </Stepper>

        {/* Step Content */}
        {activeStep === 0 && <BasicInfoStep workout={workout} onChange={setWorkout} />}
        {activeStep === 1 && <StructureStep workout={workout} onChange={setWorkout} />}
        {activeStep === 2 && <IntervalsStep workout={workout} onChange={setWorkout} />}
        {activeStep === 3 && <TargetsStep workout={workout} onChange={setWorkout} />}
        {activeStep === 4 && <ScheduleStep workout={workout} onChange={setWorkout} />}

        {/* Navigation Buttons */}
        <Box sx={{ display: 'flex', justifyContent: 'space-between', mt: 4 }}>
          <Button 
            disabled={activeStep === 0}
            onClick={() => setActiveStep(prev => prev - 1)}
          >
            Back
          </Button>
          <Box sx={{ display: 'flex', gap: 2 }}>
            <Button onClick={handleSaveAsDraft}>Save Draft</Button>
            {activeStep === steps.length - 1 ? (
              <Button variant="contained" onClick={handleFinish}>
                Save Workout
              </Button>
            ) : (
              <Button variant="contained" onClick={() => setActiveStep(prev => prev + 1)}>
                Next
              </Button>
            )}
          </Box>
        </Box>
      </Box>
    </Dialog>
  )
}
```

### Drag-and-Drop Interval Builder

**Visual Timeline Approach:**
```tsx
import { DragDropContext, Droppable, Draggable } from '@hello-pangea/dnd'

const IntervalTimeline = ({ steps, onReorder }) => {
  const handleDragEnd = (result) => {
    if (!result.destination) return
    const items = Array.from(steps)
    const [reorderedItem] = items.splice(result.source.index, 1)
    items.splice(result.destination.index, 0, reorderedItem)
    onReorder(items)
  }

  return (
    <DragDropContext onDragEnd={handleDragEnd}>
      <Droppable droppableId="steps">
        {(provided) => (
          <Box {...provided.droppableProps} ref={provided.innerRef}>
            {steps.map((step, index) => (
              <Draggable key={step.id} draggableId={step.id} index={index}>
                {(provided) => (
                  <Card
                    ref={provided.innerRef}
                    {...provided.draggableProps}
                    {...provided.dragHandleProps}
                    sx={{ mb: 2 }}
                  >
                    <CardContent>
                      <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                        {/* Drag Handle */}
                        <DragIndicator color="action" />
                        
                        {/* Step Number */}
                        <Chip label={index + 1} size="small" />
                        
                        {/* Step Details */}
                        <Box sx={{ flexGrow: 1 }}>
                          <Typography variant="body1" fontWeight={500}>
                            {step.type === 'warmup' && '🔥 Warmup'}
                            {step.type === 'interval' && '⚡ Interval'}
                            {step.type === 'recovery' && '😌 Recovery'}
                            {step.type === 'cooldown' && '❄️ Cooldown'}
                          </Typography>
                          <Typography variant="body2" color="text.secondary">
                            {step.duration} min • {step.target} • Zone {step.zone}
                          </Typography>
                          {step.repeat > 1 && (
                            <Chip label={`Repeat ${step.repeat}x`} size="small" sx={{ mt: 0.5 }} />
                          )}
                        </Box>
                        
                        {/* Actions */}
                        <IconButton size="small" onClick={() => handleEdit(step)}>
                          <Edit fontSize="small" />
                        </IconButton>
                        <IconButton size="small" onClick={() => handleDelete(step.id)}>
                          <Delete fontSize="small" />
                        </IconButton>
                      </Box>
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
  )
}
```

---

## Part 5: Ten Key Patterns to Adopt

### 1. Sport Color Coding ✅
**Priority**: MUST HAVE  
**Effort**: Easy (2 hours)

**What**: Consistent color scheme across all workout displays  
**Why**: Instant visual recognition, reduces cognitive load  
**How**: Use SPORT_COLORS constant everywhere

**Implementation**: Already detailed above in Sport Color Coding section

---

### 2. TSS Badge with Color Gradient ✅
**Priority**: MUST HAVE  
**Effort**: Easy (1 hour)

**What**: Daily TSS total displayed as color-coded badge  
**Why**: Quick visual assessment of training load  
**How**: 
```tsx
const getTSSColor = (tss: number) => {
  if (tss === 0) return 'grey'
  if (tss < 50) return 'success'  // Easy
  if (tss < 100) return 'info'     // Moderate
  if (tss < 150) return 'warning'  // Hard
  return 'error'                    // Very hard
}
```

---

### 3. Completed vs Planned Visual States ✅
**Priority**: MUST HAVE  
**Effort**: Medium (3 hours)

**What**: Clear visual differentiation (dashed border → solid + checkmark)  
**Why**: Users instantly see compliance with training plan  
**How**: Conditional styling based on `is_completed` flag

---

### 4. Quick Add Dialog ✅
**Priority**: SHOULD HAVE  
**Effort**: Medium (4 hours)

**What**: Click empty day → Simple dialog with templates  
**Why**: 80% of workouts are from templates (easy, tempo, long)  
**How**: Dialog with sport selector + template dropdown + duration

---

### 5. Week View as Default ✅
**Priority**: MUST HAVE  
**Effort**: Medium (6 hours)

**What**: 7-day horizontal calendar view  
**Why**: Athletes think in weekly training blocks  
**How**: FullCalendar library with custom week view or custom implementation

---

### 6. Performance Management Chart (PMC) ✅
**Priority**: SHOULD HAVE  
**Effort**: Hard (8 hours)

**What**: Dual-axis CTL/ATL/TSB line chart  
**Why**: Industry-standard fitness/fatigue visualization  
**How**: Recharts with two Y-axes, calculated metrics from backend

---

### 7. Metric Cards with Sparklines ✅
**Priority**: SHOULD HAVE  
**Effort**: Medium (4 hours)

**What**: Dashboard cards showing current value + trend + mini chart  
**Why**: Quick status check without clicking  
**How**: Card component + Recharts mini LineChart

---

### 8. Drag-and-Drop Workout Scheduling ✅
**Priority**: NICE TO HAVE  
**Effort**: Hard (8 hours)

**What**: Drag workout cards between days  
**Why**: Easier than click → edit → change date  
**How**: react-beautiful-dnd library

---

### 9. Workout Library with Preview Cards ✅
**Priority**: SHOULD HAVE  
**Effort**: Medium (5 hours)

**What**: Grid of workout cards with visual timeline preview  
**Why**: Users can browse and select without opening  
**How**: Card grid with SVG timeline bars

---

### 10. Context Menus on Hover ✅
**Priority**: NICE TO HAVE  
**Effort**: Medium (3 hours)

**What**: Hover workout → Quick actions menu (Edit, Delete, Duplicate, Schedule)  
**Why**: Power user efficiency (no need to open detail page)  
**How**: MUI Menu component + onMouseEnter state

---

## Part 6: What NOT to Copy from TrainingPeaks

### ❌ Over-Complicated Features
1. **Multi-athlete dashboard** (we're single-user for now)
2. **Coach/athlete messaging** (not in scope)
3. **Payment/subscription system** (self-hosted)
4. **Workout marketplace** (too complex for MVP)
5. **Advanced periodization models** (Friel, Coggan - Phase 2 feature)

### ❌ Enterprise Patterns
1. **Role-based access control** (single user)
2. **Team management** (not needed)
3. **API rate limiting UI** (unnecessary)
4. **White-label customization** (self-hosted)

### ❌ Premium-Only Features
1. **Advanced analytics** (WKO5 integration - requires paid API)
2. **Race predictions** (complex algorithms)
3. **Equipment tracking** (nice to have later)
4. **Nutrition planning** (out of scope)

---

## Part 7: Implementation Roadmap

### Phase 1: Core Navigation & Calendar (Week 1-2)
**Goal**: Match TrainingPeaks navigation UX

- [ ] Implement MainAppBar with tabs
- [ ] Create week view calendar
- [ ] Add sport color coding
- [ ] Implement completed vs planned visual states
- [ ] Add TSS badges to calendar days
- [ ] Create quick add dialog

**Deliverable**: Users can navigate app and view training calendar like TrainingPeaks

---

### Phase 2: Dashboard Analytics (Week 3-4)
**Goal**: Basic analytics dashboard

- [ ] Create metric cards (CTL, ATL, TSB, weekly total)
- [ ] Implement PMC line chart
- [ ] Add weekly summary bar chart
- [ ] Display recent activities list
- [ ] Add quick actions widget

**Deliverable**: Users see fitness metrics like TrainingPeaks dashboard

---

### Phase 3: Workout Builder (Week 5-6)
**Goal**: Create structured workouts

- [ ] Build 5-step workout wizard
- [ ] Create interval timeline component
- [ ] Add drag-and-drop reordering
- [ ] Implement zone target selector
- [ ] Add save to library vs schedule split

**Deliverable**: Users can build complex structured workouts

---

### Phase 4: Advanced Features (Week 7-8)
**Goal**: Polish and power user features

- [ ] Workout library with preview cards
- [ ] Context menus on workout hover
- [ ] Keyboard shortcuts
- [ ] Drag-and-drop calendar scheduling
- [ ] Mobile bottom navigation

**Deliverable**: Professional polish matching TrainingPeaks UX

---

## Part 8: Design System Tokens

### Color Palette (Based on TrainingPeaks)
```tsx
const theme = createTheme({
  palette: {
    primary: { main: '#2196F3' },  // Blue (matches TP brand)
    secondary: { main: '#FF9800' }, // Orange (accent)
    success: { main: '#4CAF50' },   // Green (running, success)
    warning: { main: '#FF9800' },   // Orange (cycling, moderate load)
    error: { main: '#F44336' },     // Red (high load, errors)
    info: { main: '#2196F3' },      // Blue (swimming, info)
    grey: { 
      50: '#FAFAFA',
      100: '#F5F5F5',
      200: '#EEEEEE',
      300: '#E0E0E0',
      400: '#BDBDBD',
      500: '#9E9E9E',
      600: '#757575',
      700: '#616161',
      800: '#424242',
      900: '#212121',
    }
  },
  typography: {
    fontFamily: '"Inter", "Roboto", "Helvetica", "Arial", sans-serif',
    h1: { fontSize: '2.5rem', fontWeight: 700 },
    h2: { fontSize: '2rem', fontWeight: 700 },
    h3: { fontSize: '1.75rem', fontWeight: 600 },
    h4: { fontSize: '1.5rem', fontWeight: 600 },
    h5: { fontSize: '1.25rem', fontWeight: 600 },
    h6: { fontSize: '1rem', fontWeight: 600 },
    body1: { fontSize: '1rem', lineHeight: 1.5 },
    body2: { fontSize: '0.875rem', lineHeight: 1.43 },
    caption: { fontSize: '0.75rem', lineHeight: 1.66 },
  },
  spacing: 8, // 8px base unit
  shape: { borderRadius: 8 },
})
```

### Spacing System
```tsx
sx={{ 
  p: 1,   // 8px
  p: 2,   // 16px
  p: 3,   // 24px
  p: 4,   // 32px
  gap: 2, // 16px gap
}}
```

---

## Part 9: Mobile Strategy

### TrainingPeaks Mobile App Patterns

**Bottom Navigation** (Primary):
```
┌─────────────────────────────────────┐
│                                     │
│   [Content Area]                    │
│                                     │
├─────┬────────┬────────┬────────┬────┤
│ 📊  │  📅   │   🏃   │   📈   │ ⚙️  │
│Home │Calendar│Workout │Reports │More │
└─────┴────────┴────────┴────────┴────┘
```

**Slide-Out Drawer** (Secondary Menu):
```
┌───────────────┐┌───────────────────┐
│ [User Avatar] ││                   │
│               ││   [Content]       │
│ • Profile     ││                   │
│ • Settings    ││                   │
│ • About       ││                   │
│ • Logout      ││                   │
│               ││                   │
└───────────────┘└───────────────────┘
```

**Implementation:**
```tsx
const isMobile = useMediaQuery(theme.breakpoints.down('md'))

return (
  <>
    {isMobile ? (
      <BottomNavigation showLabels value={currentTab}>
        <BottomNavigationAction label="Dashboard" icon={<Dashboard />} />
        <BottomNavigationAction label="Calendar" icon={<CalendarMonth />} />
        <BottomNavigationAction label="Plans" icon={<FitnessCenter />} />
        <BottomNavigationAction label="Analytics" icon={<Assessment />} />
      </BottomNavigation>
    ) : (
      <MainAppBar />
    )}
  </>
)
```

---

## Part 10: Success Metrics

### Before TrainingPeaks Patterns
- Navigation clicks per task: 3-5
- Time to add workout: 60 seconds
- Visual clarity: 6/10
- Mobile usability: 4/10

### After TrainingPeaks Patterns
- Navigation clicks per task: 1-2 (60% reduction)
- Time to add workout: 15 seconds (75% faster)
- Visual clarity: 9/10
- Mobile usability: 8/10

---

## Conclusion

TrainingPeaks has spent 20+ years refining their UX. This reference guide captures their proven patterns so TrainingPlan can:

✅ **Match industry standards** in navigation and calendar UX  
✅ **Reduce development time** with proven patterns  
✅ **Avoid UX mistakes** by following best practices  
✅ **Deliver professional experience** from day one

**Next Steps:**
1. Review this guide with development team
2. Prioritize Phase 1 (Core Navigation & Calendar)
3. Start with MainAppBar implementation (4 hours)
4. Build week view calendar with TSS badges (6 hours)
5. Add quick add dialog (4 hours)

**Total time for TrainingPeaks-level UX**: ~30-40 hours over 8 weeks

---

**Ready to build world-class training software! 🚀**
