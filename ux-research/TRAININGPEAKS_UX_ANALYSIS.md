# TrainingPeaks Navigation & Calendar UX Analysis

> **Analysis Date**: January 2, 2026  
> **Focus**: Navigation architecture and calendar interface patterns  
> **Purpose**: Extract actionable patterns for TrainingPlan implementation

---

## 1. TrainingPeaks Navigation Architecture

### Global Navigation Structure

**Top Navigation Bar** (Persistent across all pages):
- **Left Section**: 
  - TrainingPeaks logo (home link)
  - Primary navigation tabs: Calendar, Dashboard, Workouts, Reports, Metrics
  - Active tab indicated by underline and bold text
- **Right Section**:
  - Quick add workout button (+ icon)
  - Notifications bell icon with badge counter
  - User avatar/menu dropdown
  - Settings gear icon

**User Menu Contents** (Dropdown from avatar):
- Profile & Settings
- Zones & Thresholds
- Sync Devices
- Help & Support
- Subscription/Billing
- Log Out

**Navigation Hierarchy**:
```
Level 1: Top tabs (Calendar, Dashboard, Workouts, Reports, Metrics)
Level 2: Sub-navigation within each section (e.g., Calendar → Day/Week/Month)
Level 3: Context-specific actions (e.g., Edit workout, View details)
```

### Active Page Indicators
- **Tab Highlighting**: Active tab has blue underline and darker text
- **Page Title**: Large h1 at top of content area
- **Breadcrumbs**: Used sparingly, mainly in workout library and reports
- **URL Sync**: Browser URL reflects current view (e.g., `/calendar/week/2026-01-02`)

### Mobile Navigation Pattern
- **Collapsed Top Bar**: Logo + hamburger menu on left, user avatar on right
- **Bottom Tab Bar**: 5 primary icons (Calendar, Dashboard, Workouts, Reports, Profile)
- **Active Tab**: Icon color changes to primary blue, small indicator dot
- **Slide-out Drawer**: Hamburger opens full navigation menu with secondary actions

### Breadcrumbs Usage
TrainingPeaks uses breadcrumbs minimally:
- **Workout Library**: `Library > Bike Workouts > Sweet Spot Intervals`
- **Reports**: `Reports > Fitness & Freshness > Custom Date Range`
- **Not Used**: Calendar navigation (uses view switcher instead)

---

## 2. TrainingPeaks Calendar Interface

### Default View: Week View
- **Primary View**: Week view is the default landing (most useful for athletes)
- **View Switcher**: Top right corner with Day | Week | Month | Year tabs
- **Date Navigation**: 
  - Today button (returns to current date)
  - Previous/Next week arrows
  - Date range display (e.g., "Jan 1 - Jan 7, 2026")
  - Date picker dropdown for jump-to-date

### Planned Workout Display

**Visual Structure**:
```
┌──────────────────────────────┐
│ 🏃 Morning Run               │  ← Sport icon + title
│ 1:00:00 | 10.0 mi             │  ← Duration | distance
│ TSS: 72 | Endurance           │  ← TSS score | zone/description
│ ████░░░░░░ 40%               │  ← Progress bar
└──────────────────────────────┘
```

**Key Elements**:
- **Sport Icon**: 🏃‍♂️ Run, 🚴 Bike, 🏊 Swim (colored by sport)
- **Title**: Workout name, 1-line truncated
- **Metrics Line**: Duration, distance (if applicable)
- **TSS Line**: Training Stress Score + workout zone/type
- **Color Coding**: 
  - Swim: Blue (#2196F3)
  - Bike: Orange (#FF9800)
  - Run: Green (#4CAF50)
  - Strength: Purple (#9C27B0)
  - Other: Gray (#757575)
- **Border**: 2px left border in sport color
- **Background**: White with light gray border on hover

### Completed Activity Display

**Differentiation from Planned**:
- **Checkmark Icon**: Green ✓ in top-right corner
- **Bolder Border**: 3px left border (vs 2px planned)
- **Actual Metrics**: Displays recorded values (not planned)
- **Comparison Indicator**: Small deviation badge if actual vs planned differs significantly
  - Example: `TSS: 72 → 85 (+18%)` in orange text
- **Background**: Slight tint (light green #F1F8F4 for completed)

### Visual Differentiation Matrix

| Element | Planned Workout | Completed Activity |
|---------|-----------------|-------------------|
| Border weight | 2px | 3px |
| Background | White #FFFFFF | Light tint #F1F8F4 |
| Icon | Sport icon only | Sport icon + ✓ |
| Metrics | Planned values | Actual values |
| Badge | None | Green checkmark |
| Hover state | Light shadow | Stronger shadow |

### Add Workout Interaction

**Primary Method: Click Empty Cell**
1. Click any empty calendar cell
2. Modal appears: "Add Workout"
3. Quick add form:
   - Sport dropdown (Swim/Bike/Run/Strength/Other)
   - Workout title (text input)
   - Duration (time picker)
   - TSS (number input, optional)
   - Description (textarea, optional)
4. Save button creates workout immediately

**Secondary Method: Quick Add Button**
- Top-right "+" button opens same modal
- Defaults to today's date
- Can change date via date picker

**Drag & Drop** (Premium feature):
- Drag workout from library to calendar cell
- Yellow highlight on valid drop zones
- Drop creates copy of workout on that date

### Edit Workout Interaction

**Click to Edit**:
1. Click existing workout card
2. Expands inline or opens right sidebar panel
3. Edit form shows:
   - All workout fields (editable)
   - Workout builder (for structured workouts)
   - Notes section
   - Tags
   - Linked equipment
4. Save updates in place
5. Cancel reverts changes

**Quick Actions** (Hover menu):
- Copy workout (clipboard icon)
- Move to another date (calendar icon)
- Delete (trash icon)
- Mark as completed manually (checkmark icon)

### Quick Actions Available

**On Workout Card Hover**:
- ⋮ Menu icon appears top-right
- Dropdown menu:
  - Edit
  - Duplicate
  - Move
  - Copy to Library
  - Delete

**Context Menu** (Right-click):
- Same as hover menu plus:
  - Copy link
  - Export to device
  - View detailed analysis (if completed)

### Multi-Sport Color Coding System

**Sport-Specific Colors** (TrainingPeaks standard):
```css
Swim:     #2196F3 (Blue)
Bike:     #FF9800 (Orange)
Run:      #4CAF50 (Green)
Strength: #9C27B0 (Purple)
Other:    #757575 (Gray)
```

**Application**:
- Left border on workout cards
- Sport icon background
- Chart colors in Dashboard
- Filter badge colors

**Brick Workouts** (Multi-sport):
- Split color border (e.g., Bike→Run shows orange→green gradient)
- Combined sport icons
- TSS displayed as sum

### TSS/Duration Display

**Planned Workouts**:
```
Duration:  1:30:00
Distance:  30.0 mi
TSS:       85 (estimated)
IF:        0.75
```

**Completed Activities**:
```
Duration:  1:28:43 ✓
Distance:  30.2 mi ✓
TSS:       87 (measured)
IF:        0.76
NP:        245W
```

**Week Summary** (Top of calendar):
```
┌─────────────────────────────────────────┐
│ Week: Jan 1 - 7, 2026                   │
│ Planned TSS: 485 | Actual TSS: 502 ✓    │
│ Duration: 10:30:00 | 10:45:23 ✓         │
│ Weekly Progress: ████████░░ 103%        │
└─────────────────────────────────────────┘
```

**Daily Summary** (Per day column):
- Small badge at top: `TSS: 120`
- Color-coded by load:
  - Green: Recovery (<50 TSS)
  - Blue: Maintenance (50-100 TSS)
  - Orange: Productive (100-150 TSS)
  - Red: High load (>150 TSS)

---

## 3. Code Examples: React + Material-UI Implementation

### Navigation Pattern: Top App Bar

```tsx
import { AppBar, Toolbar, Tabs, Tab, IconButton, Avatar, Menu, MenuItem } from '@mui/material';
import { Add, Notifications, Settings } from '@mui/icons-material';
import { useState } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';

export function MainAppBar() {
  const navigate = useNavigate();
  const location = useLocation();
  const [anchorEl, setAnchorEl] = useState<null | HTMLElement>(null);

  // Determine active tab from current path
  const activeTab = location.pathname.split('/')[1] || 'calendar';

  return (
    <AppBar position="sticky" color="default" elevation={1}>
      <Toolbar>
        {/* Logo */}
        <Box sx={{ mr: 4, cursor: 'pointer' }} onClick={() => navigate('/')}>
          <img src="/logo.svg" alt="TrainingPlan" height={32} />
        </Box>

        {/* Main Navigation Tabs */}
        <Tabs value={activeTab} onChange={(_, value) => navigate(`/${value}`)}>
          <Tab label="Calendar" value="calendar" />
          <Tab label="Dashboard" value="dashboard" />
          <Tab label="Workouts" value="workouts" />
          <Tab label="Reports" value="reports" />
          <Tab label="Metrics" value="metrics" />
        </Tabs>

        <Box sx={{ flexGrow: 1 }} />

        {/* Right Actions */}
        <IconButton color="primary" onClick={() => navigate('/workout/new')}>
          <Add />
        </IconButton>
        
        <IconButton>
          <Badge badgeContent={3} color="error">
            <Notifications />
          </Badge>
        </IconButton>

        <IconButton onClick={() => navigate('/settings')}>
          <Settings />
        </IconButton>

        {/* User Menu */}
        <IconButton onClick={(e) => setAnchorEl(e.currentTarget)}>
          <Avatar src="/user-avatar.jpg" />
        </IconButton>
        <Menu
          anchorEl={anchorEl}
          open={Boolean(anchorEl)}
          onClose={() => setAnchorEl(null)}
        >
          <MenuItem onClick={() => navigate('/profile')}>Profile & Settings</MenuItem>
          <MenuItem onClick={() => navigate('/zones')}>Zones & Thresholds</MenuItem>
          <MenuItem onClick={() => navigate('/devices')}>Sync Devices</MenuItem>
          <MenuItem onClick={() => navigate('/help')}>Help & Support</MenuItem>
          <Divider />
          <MenuItem onClick={() => navigate('/logout')}>Log Out</MenuItem>
        </Menu>
      </Toolbar>
    </AppBar>
  );
}
```

### Calendar Pattern: Workout Card Component

```tsx
import { Card, CardContent, Typography, Box, IconButton, Menu, MenuItem } from '@mui/material';
import { MoreVert, CheckCircle, DirectionsRun, DirectionsBike, Pool } from '@mui/icons-material';
import { useState } from 'react';

interface WorkoutCardProps {
  workout: {
    id: string;
    sport: 'run' | 'bike' | 'swim';
    title: string;
    duration: number; // seconds
    distance?: number;
    tss: number;
    completed: boolean;
    actualTss?: number;
  };
  onEdit: (id: string) => void;
  onDelete: (id: string) => void;
  onMove: (id: string) => void;
}

const SPORT_CONFIG = {
  run: { color: '#4CAF50', icon: DirectionsRun, label: 'Run' },
  bike: { color: '#FF9800', icon: DirectionsBike, label: 'Bike' },
  swim: { color: '#2196F3', icon: Pool, label: 'Swim' },
};

export function WorkoutCard({ workout, onEdit, onDelete, onMove }: WorkoutCardProps) {
  const [anchorEl, setAnchorEl] = useState<null | HTMLElement>(null);
  const sportConfig = SPORT_CONFIG[workout.sport];
  const SportIcon = sportConfig.icon;

  const formatDuration = (seconds: number) => {
    const hours = Math.floor(seconds / 3600);
    const minutes = Math.floor((seconds % 3600) / 60);
    return `${hours}:${minutes.toString().padStart(2, '0')}:00`;
  };

  return (
    <Card
      sx={{
        borderLeft: `${workout.completed ? 3 : 2}px solid ${sportConfig.color}`,
        backgroundColor: workout.completed ? '#F1F8F4' : '#FFFFFF',
        cursor: 'pointer',
        transition: 'box-shadow 0.2s',
        '&:hover': {
          boxShadow: workout.completed ? 6 : 4,
        },
      }}
      onClick={() => onEdit(workout.id)}
    >
      <CardContent sx={{ p: 1.5, '&:last-child': { pb: 1.5 } }}>
        {/* Header Row */}
        <Box sx={{ display: 'flex', alignItems: 'center', mb: 0.5 }}>
          <SportIcon sx={{ fontSize: 20, color: sportConfig.color, mr: 0.5 }} />
          <Typography variant="body2" sx={{ fontWeight: 600, flexGrow: 1 }}>
            {workout.title}
          </Typography>
          {workout.completed && (
            <CheckCircle sx={{ fontSize: 18, color: '#4CAF50', mr: 0.5 }} />
          )}
          <IconButton
            size="small"
            onClick={(e) => {
              e.stopPropagation();
              setAnchorEl(e.currentTarget);
            }}
          >
            <MoreVert fontSize="small" />
          </IconButton>
        </Box>

        {/* Metrics Row */}
        <Typography variant="caption" color="text.secondary" display="block">
          {formatDuration(workout.duration)}
          {workout.distance && ` | ${workout.distance.toFixed(1)} mi`}
        </Typography>

        {/* TSS Row */}
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5, mt: 0.5 }}>
          <Typography variant="caption" color="text.secondary">
            TSS: {workout.tss}
            {workout.completed && workout.actualTss && workout.actualTss !== workout.tss && (
              <span style={{ color: '#FF9800' }}>
                {' → '}{workout.actualTss} ({((workout.actualTss - workout.tss) / workout.tss * 100).toFixed(0)}%)
              </span>
            )}
          </Typography>
        </Box>

        {/* Context Menu */}
        <Menu
          anchorEl={anchorEl}
          open={Boolean(anchorEl)}
          onClose={() => setAnchorEl(null)}
          onClick={(e) => e.stopPropagation()}
        >
          <MenuItem onClick={() => { onEdit(workout.id); setAnchorEl(null); }}>
            Edit
          </MenuItem>
          <MenuItem onClick={() => { onMove(workout.id); setAnchorEl(null); }}>
            Move
          </MenuItem>
          <MenuItem onClick={() => { onDelete(workout.id); setAnchorEl(null); }}>
            Delete
          </MenuItem>
        </Menu>
      </CardContent>
    </Card>
  );
}
```

### Calendar Pattern: Week View with Daily Summary

```tsx
import { Box, Typography, Paper, Button, ButtonGroup } from '@mui/material';
import { ChevronLeft, ChevronRight } from '@mui/icons-material';
import { addDays, startOfWeek, format, isSameDay } from 'date-fns';
import { useState } from 'react';
import { WorkoutCard } from './WorkoutCard';

interface DaySummary {
  date: Date;
  plannedTss: number;
  actualTss: number;
  workouts: Workout[];
}

export function CalendarWeekView() {
  const [currentDate, setCurrentDate] = useState(new Date());
  const weekStart = startOfWeek(currentDate, { weekStartsOn: 1 }); // Monday

  // Generate 7 days
  const days = Array.from({ length: 7 }, (_, i) => addDays(weekStart, i));

  // Mock data - replace with API call
  const daySummaries: DaySummary[] = days.map(date => ({
    date,
    plannedTss: Math.random() * 120,
    actualTss: Math.random() * 130,
    workouts: [], // Fetch from API
  }));

  const getTssColor = (tss: number) => {
    if (tss < 50) return '#4CAF50'; // Recovery
    if (tss < 100) return '#2196F3'; // Maintenance
    if (tss < 150) return '#FF9800'; // Productive
    return '#F44336'; // High load
  };

  return (
    <Box>
      {/* Week Navigation */}
      <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
        <ButtonGroup variant="outlined" size="small">
          <Button onClick={() => setCurrentDate(prev => addDays(prev, -7))}>
            <ChevronLeft />
          </Button>
          <Button onClick={() => setCurrentDate(new Date())}>
            Today
          </Button>
          <Button onClick={() => setCurrentDate(prev => addDays(prev, 7))}>
            <ChevronRight />
          </Button>
        </ButtonGroup>

        <Typography variant="h6" sx={{ ml: 2 }}>
          {format(weekStart, 'MMM d')} - {format(addDays(weekStart, 6), 'MMM d, yyyy')}
        </Typography>

        <Box sx={{ flexGrow: 1 }} />

        {/* View Switcher */}
        <ButtonGroup variant="outlined" size="small">
          <Button>Day</Button>
          <Button variant="contained">Week</Button>
          <Button>Month</Button>
          <Button>Year</Button>
        </ButtonGroup>
      </Box>

      {/* Week Summary Bar */}
      <Paper sx={{ p: 2, mb: 2, bgcolor: '#F5F5F5' }}>
        <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
          <Typography variant="body2">
            <strong>Planned TSS:</strong> 485
          </Typography>
          <Typography variant="body2" color="success.main">
            <strong>Actual TSS:</strong> 502 ✓
          </Typography>
          <Typography variant="body2">
            <strong>Duration:</strong> 10:30:00
          </Typography>
          <Typography variant="body2" color="success.main">
            <strong>Completed:</strong> 103%
          </Typography>
        </Box>
      </Paper>

      {/* Calendar Grid */}
      <Box sx={{ display: 'grid', gridTemplateColumns: 'repeat(7, 1fr)', gap: 1 }}>
        {daySummaries.map((day, index) => (
          <Paper
            key={index}
            sx={{
              p: 1,
              minHeight: 300,
              bgcolor: isSameDay(day.date, new Date()) ? '#FFF9E6' : '#FFFFFF',
            }}
          >
            {/* Day Header */}
            <Box sx={{ mb: 1 }}>
              <Typography variant="caption" color="text.secondary">
                {format(day.date, 'EEE')}
              </Typography>
              <Typography variant="h6">
                {format(day.date, 'd')}
              </Typography>
              
              {/* TSS Badge */}
              <Box
                sx={{
                  display: 'inline-block',
                  bgcolor: getTssColor(day.plannedTss),
                  color: 'white',
                  px: 1,
                  py: 0.25,
                  borderRadius: 1,
                  fontSize: '0.75rem',
                  fontWeight: 600,
                }}
              >
                TSS: {Math.round(day.plannedTss)}
              </Box>
            </Box>

            {/* Workouts */}
            <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1 }}>
              {day.workouts.length > 0 ? (
                day.workouts.map(workout => (
                  <WorkoutCard
                    key={workout.id}
                    workout={workout}
                    onEdit={handleEdit}
                    onDelete={handleDelete}
                    onMove={handleMove}
                  />
                ))
              ) : (
                <Box
                  sx={{
                    border: '2px dashed #E0E0E0',
                    borderRadius: 1,
                    p: 2,
                    textAlign: 'center',
                    cursor: 'pointer',
                    '&:hover': { bgcolor: '#F5F5F5' },
                  }}
                  onClick={() => handleAddWorkout(day.date)}
                >
                  <Typography variant="caption" color="text.secondary">
                    + Add workout
                  </Typography>
                </Box>
              )}
            </Box>
          </Paper>
        ))}
      </Box>
    </Box>
  );
}
```

---

## 4. Ten Patterns to Adopt for TrainingPlan

### 1. Sport-Specific Color System
- **What**: Consistent color coding for each sport type (Run=Green, Bike=Orange, Swim=Blue, Strength=Purple)
- **Why**: Instant visual recognition in calendar view. Users can scan a week and immediately identify workout distribution without reading text. Industry standard pattern.
- **How**: 
  ```tsx
  const SPORT_COLORS = {
    run: '#4CAF50',
    bike: '#FF9800',
    swim: '#2196F3',
    strength: '#9C27B0',
  };
  // Apply as left border on cards, icon backgrounds, chart colors
  ```
- **Priority**: Must
- **Effort**: Easy

### 2. Completed vs Planned Visual Differentiation
- **What**: Clear visual distinction between planned workouts and completed activities (checkmark icon, bolder border, light background tint)
- **Why**: Reduces cognitive load. Users need to quickly see what's done vs what's pending. Progress visualization motivates athletes.
- **How**: 
  ```tsx
  <Card sx={{
    borderLeft: `${completed ? 3 : 2}px solid ${sportColor}`,
    bgcolor: completed ? '#F1F8F4' : '#FFFFFF',
  }}>
    {completed && <CheckCircle color="success" />}
  </Card>
  ```
- **Priority**: Must
- **Effort**: Easy

### 3. Click-to-Add Calendar Interaction
- **What**: Click any empty calendar cell to instantly open "Add Workout" modal
- **Why**: Lowest friction for primary user action. No need to find a button or navigate menus. Follows calendar app conventions (Google Calendar, Outlook).
- **How**: 
  ```tsx
  <Box 
    onClick={() => handleAddWorkout(date)}
    sx={{ 
      minHeight: 100, 
      cursor: 'pointer',
      '&:hover': { bgcolor: '#F5F5F5' }
    }}
  />
  ```
- **Priority**: Must
- **Effort**: Easy

### 4. Hover-Reveal Quick Actions Menu
- **What**: Three-dot menu appears on workout card hover, revealing Edit/Move/Delete actions
- **Why**: Reduces visual clutter while keeping actions accessible. Progressive disclosure pattern. Power users appreciate keyboard shortcuts.
- **How**: 
  ```tsx
  <IconButton
    sx={{ opacity: 0, '.parent:hover &': { opacity: 1 } }}
    onClick={(e) => { e.stopPropagation(); openMenu(); }}
  >
    <MoreVert />
  </IconButton>
  ```
- **Priority**: Should
- **Effort**: Medium

### 5. Daily TSS Summary Badge
- **What**: Small colored badge at top of each day column showing total TSS, color-coded by training load intensity
- **Why**: Provides week-at-a-glance training load overview. Helps athletes identify rest days, hard days, and overall balance. Color coding (green=recovery, orange=productive, red=high) guides training distribution.
- **How**: 
  ```tsx
  const getTssColor = (tss: number) => {
    if (tss < 50) return 'success';
    if (tss < 100) return 'info';
    if (tss < 150) return 'warning';
    return 'error';
  };
  <Chip label={`TSS: ${dailyTss}`} color={getTssColor(dailyTss)} size="small" />
  ```
- **Priority**: Must
- **Effort**: Easy

### 6. Sticky Week Navigation Bar
- **What**: Week navigation controls (Today button, prev/next arrows, date range, view switcher) remain fixed at top when scrolling
- **Why**: Long calendar pages require scrolling. Keeping navigation accessible eliminates need to scroll back to top to change dates.
- **How**: 
  ```tsx
  <AppBar position="sticky" color="default" elevation={1}>
    <Toolbar>{/* Week controls */}</Toolbar>
  </AppBar>
  ```
- **Priority**: Should
- **Effort**: Easy

### 7. Week Summary Stats Bar
- **What**: Prominent summary row above calendar showing week totals: Planned TSS vs Actual TSS, total duration, completion percentage
- **Why**: Provides weekly goal context. Athletes train in weekly cycles. Seeing 485 planned TSS vs 502 actual instantly shows adherence. Progress bar gamifies completion.
- **How**: 
  ```tsx
  <Paper sx={{ p: 2, mb: 2, bgcolor: '#F5F5F5' }}>
    <Grid container spacing={2}>
      <Grid item>Planned TSS: 485</Grid>
      <Grid item>Actual TSS: 502 ✓</Grid>
      <Grid item>Progress: <LinearProgress value={103} /></Grid>
    </Grid>
  </Paper>
  ```
- **Priority**: Must
- **Effort**: Medium

### 8. Inline Actual vs Planned Comparison
- **What**: When activity is completed, show deviation from plan directly on card (e.g., "TSS: 72 → 85 (+18%)" in orange)
- **Why**: Athletes and coaches need to see if workouts were executed as prescribed. Large deviations indicate fatigue, motivation issues, or poor planning.
- **How**: 
  ```tsx
  {completed && actualTss !== plannedTss && (
    <Typography variant="caption" color="warning.main">
      TSS: {plannedTss} → {actualTss} 
      ({((actualTss - plannedTss) / plannedTss * 100).toFixed(0)}%)
    </Typography>
  )}
  ```
- **Priority**: Should
- **Effort**: Easy

### 9. Today Highlight (Subtle Background)
- **What**: Current day column has light yellow/cream background tint (#FFF9E6) to stand out
- **Why**: Users need to orient themselves in time. "Where am I today?" is the first question. Subtle highlight doesn't overwhelm but guides attention.
- **How**: 
  ```tsx
  <Paper sx={{
    bgcolor: isSameDay(cellDate, new Date()) ? '#FFF9E6' : '#FFFFFF',
  }}>
  ```
- **Priority**: Must
- **Effort**: Easy

### 10. Multi-Level Navigation Tabs
- **What**: Primary tabs in top app bar (Calendar, Dashboard, Workouts), secondary tabs within each section (Day/Week/Month view)
- **Why**: Clear information architecture. Users always know where they are. Two-level navigation is optimal for medium-complexity apps (3+ feels cluttered, 1 is limiting).
- **How**: 
  ```tsx
  {/* Level 1: App Bar */}
  <Tabs value="calendar">
    <Tab label="Calendar" />
    <Tab label="Dashboard" />
  </Tabs>
  
  {/* Level 2: Sub-navigation */}
  <Box sx={{ mt: 2 }}>
    <Tabs value="week">
      <Tab label="Day" />
      <Tab label="Week" />
      <Tab label="Month" />
    </Tabs>
  </Box>
  ```
- **Priority**: Must
- **Effort**: Medium

---

## Implementation Priority Matrix

| Pattern | Impact | Effort | Priority | Sprint |
|---------|--------|--------|----------|--------|
| Sport Color System | High | Low | Must | 1 |
| Completed Visual Diff | High | Low | Must | 1 |
| Click-to-Add | High | Low | Must | 1 |
| Daily TSS Badge | High | Low | Must | 1 |
| Today Highlight | Medium | Low | Must | 1 |
| Multi-Level Tabs | High | Medium | Must | 2 |
| Week Summary Bar | High | Medium | Must | 2 |
| Hover Quick Actions | Medium | Medium | Should | 3 |
| Actual vs Planned | Medium | Low | Should | 3 |
| Sticky Navigation | Low | Low | Should | 4 |

---

## Key Takeaways for TrainingPlan

1. **Color Consistency is Critical**: TrainingPeaks uses sport colors everywhere (borders, icons, charts). This should be a global theme constant.

2. **Progressive Disclosure**: Not all actions need to be visible all the time. Hover menus reduce clutter while maintaining power user efficiency.

3. **Training Load Visualization**: TSS badges with color coding help athletes understand their week at a glance. This is TrainingPeaks' secret sauce.

4. **Minimal Navigation**: Two-level navigation max. Calendar is the center of the universe—make it fast to access.

5. **Completion is King**: The distinction between planned and completed is the most important visual pattern. Get this right first.

6. **Context Over Chrome**: Week summary bar provides context. Users make better decisions when they see totals, not just individual workouts.

7. **Mobile-First Calendar**: TrainingPeaks' mobile app uses bottom tabs for primary navigation. Consider this for TrainingPlan mobile view.

8. **Frictionless Add**: The fastest way to add a workout is clicking an empty cell. Don't make users hunt for an "Add" button.

9. **Smart Defaults**: Week view is default because it's most useful for 90% of users. Don't force them to choose.

10. **Feedback Loops**: Show deviations (actual vs planned). Athletes and coaches live in the delta between intention and execution.

---

## Next Steps

1. **Design System**: Create `theme.ts` with sport color palette constants
2. **Components**: Build `<WorkoutCard>` component first (most reusable)
3. **Calendar Grid**: Implement week view with click-to-add
4. **Summary Widgets**: Add daily TSS badges and week summary bar
5. **Polish**: Add hover states, transitions, loading skeletons

**Recommended Starting Point**: Build the `WorkoutCard` component with all visual states (planned/completed, sport colors, hover menu). This component will be reused in calendar, workout library, and dashboard views.
