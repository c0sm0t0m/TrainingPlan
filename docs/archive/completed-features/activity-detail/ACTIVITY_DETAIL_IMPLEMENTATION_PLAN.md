# Activity Detail Page - Implementation Plan

**Date**: January 5, 2026  
**Status**: Planning Phase  
**Goal**: Create dedicated activity detail pages for both desktop and mobile

## Current State Analysis

### What Exists Today

**Desktop Version (Calendar.tsx - Dialog)**
- ✅ Activity detail shown in Material-UI Dialog
- ✅ Key metrics: TSS, IF, Time, Distance (prominent display)
- ✅ Detailed stats: Location, pace, power (NP, avg), HR (avg, max), elevation, calories
- ✅ Two-column layout for detailed stats
- ✅ Color-coded TSS and IF values
- ✅ Intensity zone labels (Easy, Endurance, Tempo, Threshold, VO2max)
- ✅ Sport-specific icons
- ❌ No GPS map visualization
- ❌ No time-series charts (pace, HR, power over time)
- ❌ No lap splits display
- ❌ No notes/equipment/weather metadata
- ❌ No edit functionality
- ❌ Limited to dialog size (not full page)

**Navigation**
- Activities only accessible from Calendar page
- Dialog opens when clicking activity
- No dedicated route (`/activities/:id`)
- No swipe navigation between activities
- No deep linking support

**Data Available (Backend)**
```typescript
interface GarminActivity {
  id: number;
  garmin_activity_id: string;
  activity_name: string;
  activity_type: string;
  sport_type_id?: number;
  start_time_local: string;
  date: string;
  
  // Duration
  duration_seconds: number;
  moving_duration_seconds?: number;
  elapsed_duration_seconds?: number;
  
  // Distance & Speed
  distance_meters?: number;
  average_speed_mps?: number;
  
  // Heart Rate
  average_hr?: number;
  max_hr?: number;
  
  // Power (Cycling)
  average_power_watts?: number;
  normalized_power_watts?: number;
  threshold_power_watts?: number;
  
  // Training Metrics
  calculated_tss?: number;
  training_load?: number;
  intensity_factor?: number;
  
  // Other
  elevation_gain_meters?: number;
  calories?: number;
  location_name?: string;
}
```

### What's Missing

**Critical Data (Need Backend API)**
1. ❌ GPS track points (lat/lng array for mapping)
2. ❌ Time-series data (pace/HR/power by second/distance)
3. ❌ Lap splits data
4. ❌ Activity notes (user-added)
5. ❌ Equipment used (bike, shoes)
6. ❌ Weather data (temp, conditions)
7. ❌ Zone distribution (time in each HR/power zone)

**API Endpoints Needed**
- `GET /api/v1/activities/:id` - Full activity detail
- `GET /api/v1/activities/:id/track` - GPS track points
- `GET /api/v1/activities/:id/streams` - Time-series data (HR, power, pace)
- `GET /api/v1/activities/:id/splits` - Lap splits
- `PATCH /api/v1/activities/:id` - Update activity (title, notes, equipment)

---

## Implementation Plan

### Phase 1: Backend API Enhancement (Week 1)
**Goal**: Expose all activity data needed for detailed views

#### Step 1.1: Create Activity Detail API Endpoints
**Priority**: P0 (Blocker)  
**Effort**: 4-6 hours  
**Files to Create/Modify**:
- `backend/src/api/routes/activities.py` (new file)
- `backend/src/models/garmin_activity.py` (update model)
- `backend/src/services/garmin_service.py` (add methods)

**Tasks**:
```python
# 1. Add to main.py
app.include_router(
    activities_router,
    prefix="/api/v1/activities",
    tags=["activities"]
)

# 2. Create activities.py router
@router.get("/{activity_id}", response_model=ActivityDetailResponse)
async def get_activity_detail(
    activity_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get full activity details including metadata."""
    # Query activity with all fields
    # Return enriched response
    pass

@router.get("/{activity_id}/track", response_model=ActivityTrackResponse)
async def get_activity_track(activity_id: int, ...):
    """Get GPS track points for mapping."""
    # Query track_points table or fetch from Garmin
    # Return list of {lat, lng, ele, timestamp}
    pass

@router.get("/{activity_id}/streams", response_model=ActivityStreamsResponse)
async def get_activity_streams(activity_id: int, ...):
    """Get time-series data (HR, power, pace)."""
    # Query time_series table or fetch from Garmin
    # Return arrays of values with timestamps
    pass

@router.get("/{activity_id}/splits", response_model=ActivitySplitsResponse)
async def get_activity_splits(activity_id: int, ...):
    """Get lap splits."""
    # Query splits table or parse from activity
    # Return list of laps with stats
    pass

@router.patch("/{activity_id}", response_model=ActivityDetailResponse)
async def update_activity(
    activity_id: int,
    update: ActivityUpdate,
    ...
):
    """Update activity metadata (title, notes, equipment)."""
    # Update allowed fields only
    # Return updated activity
    pass
```

**Database Considerations**:
- Check if track_points and time_series tables exist
- May need to store data during Garmin sync or fetch on-demand
- Consider caching strategy (Redis) for track/streams data

**Testing**:
- Create `backend/test_activity_detail_api.py`
- Test each endpoint with real activity ID
- Verify response schemas
- Test user authorization (can only view own activities)

#### Step 1.2: Fetch Additional Data from Garmin
**Priority**: P1  
**Effort**: 3-4 hours  
**Files to Modify**:
- `backend/src/services/garmin_service.py`

**Tasks**:
```python
async def get_activity_splits(
    oauth1_token: str,
    oauth2_token: str,
    activity_id: int
) -> List[Dict]:
    """Fetch lap splits from Garmin."""
    api = await self.resume_session(oauth1_token, oauth2_token)
    splits = api.get_activity_splits(activity_id)
    return splits

async def get_activity_streams(
    oauth1_token: str,
    oauth2_token: str,
    activity_id: int,
    stream_types: List[str] = ['heartRate', 'power', 'pace']
) -> Dict[str, List]:
    """Fetch time-series streams from Garmin."""
    # May need to download FIT file and parse
    # Or use Garmin API if available
    pass
```

**Garmin API Research**:
- Check `garminconnect` library docs for splits/streams methods
- May need to parse FIT file directly using `fitparse`
- Store parsed data in database for performance

---

### Phase 2: Frontend - Desktop Detail Page (Week 1-2)
**Goal**: Create full-page activity detail view for desktop

#### Step 2.1: Create ActivityDetail Page Component
**Priority**: P0  
**Effort**: 6-8 hours  
**Files to Create**:
- `frontend/src/pages/ActivityDetail.tsx` (main page)
- `frontend/src/components/activity/ActivityMap.tsx` (map component)
- `frontend/src/components/activity/ActivityCharts.tsx` (charts component)
- `frontend/src/components/activity/ActivitySplits.tsx` (splits table)
- `frontend/src/components/activity/ActivityStats.tsx` (stats grid)

**Page Structure** (Desktop):
```typescript
// ActivityDetail.tsx
import { useParams } from 'react-router-dom';

const ActivityDetail: React.FC = () => {
  const { activityId } = useParams();
  const [activity, setActivity] = useState<Activity | null>(null);
  const [trackData, setTrackData] = useState<TrackPoint[]>([]);
  const [streamsData, setStreamsData] = useState<Streams | null>(null);
  const [splits, setSplits] = useState<Split[]>([]);
  
  // Desktop Layout (> md breakpoint)
  return (
    <Container maxWidth="xl">
      <Box sx={{ py: 3 }}>
        {/* Breadcrumbs */}
        <Breadcrumbs sx={{ mb: 2 }}>
          <Link href="/dashboard">Home</Link>
          <Link href="/calendar">Calendar</Link>
          <Typography color="text.primary">{activity?.activity_name}</Typography>
        </Breadcrumbs>

        {/* Hero Section */}
        <Card sx={{ mb: 3 }}>
          <CardContent>
            <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <Box>
                <Typography variant="h4" gutterBottom>{activity?.activity_name}</Typography>
                <Typography variant="body2" color="text.secondary">
                  {formatDate(activity?.start_time_local)}
                </Typography>
              </Box>
              <Box>
                <IconButton onClick={handleEdit}><EditIcon /></IconButton>
                <IconButton onClick={handleShare}><ShareIcon /></IconButton>
                <IconButton onClick={handleMore}><MoreVertIcon /></IconButton>
              </Box>
            </Box>

            {/* Key Metrics Row */}
            <Box sx={{ display: 'flex', gap: 4, mt: 3 }}>
              <MetricCard title="TSS" value={activity?.calculated_tss} />
              <MetricCard title="IF" value={activity?.intensity_factor} />
              <MetricCard title="Time" value={formatDuration(activity?.duration_seconds)} />
              <MetricCard title="Distance" value={`${activity?.distance_meters / 1000} km`} />
            </Box>
          </CardContent>
        </Card>

        {/* Main Content Grid */}
        <Grid container spacing={3}>
          {/* Left Column - Map & Charts (8 cols) */}
          <Grid item xs={12} md={8}>
            {/* Map Card */}
            <Card sx={{ mb: 3 }}>
              <CardContent>
                <Typography variant="h6" gutterBottom>Route</Typography>
                <ActivityMap trackPoints={trackData} height={400} />
              </CardContent>
            </Card>

            {/* Charts Card */}
            <Card>
              <CardContent>
                <ActivityCharts streams={streamsData} />
              </CardContent>
            </Card>
          </Grid>

          {/* Right Column - Stats & Splits (4 cols) */}
          <Grid item xs={12} md={4}>
            {/* Stats Card */}
            <Card sx={{ mb: 3 }}>
              <CardContent>
                <ActivityStats activity={activity} />
              </CardContent>
            </Card>

            {/* Splits Card */}
            <Card>
              <CardContent>
                <ActivitySplits splits={splits} />
              </CardContent>
            </Card>
          </Grid>
        </Grid>

        {/* Notes Section */}
        <Card sx={{ mt: 3 }}>
          <CardContent>
            <Typography variant="h6" gutterBottom>Notes</Typography>
            <Typography variant="body2" color="text.secondary">
              {activity?.notes || 'No notes for this activity'}
            </Typography>
          </CardContent>
        </Card>
      </Box>
    </Container>
  );
};
```

#### Step 2.2: Implement ActivityMap Component
**Priority**: P1  
**Effort**: 3-4 hours  
**Dependencies**: Leaflet, react-leaflet  
**Files**: `frontend/src/components/activity/ActivityMap.tsx`

```typescript
import { MapContainer, TileLayer, Polyline, Marker } from 'react-leaflet';
import 'leaflet/dist/leaflet.css';

interface ActivityMapProps {
  trackPoints: Array<{ lat: number; lng: number; ele?: number }>;
  height?: number;
}

const ActivityMap: React.FC<ActivityMapProps> = ({ trackPoints, height = 400 }) => {
  const theme = useTheme();
  
  if (!trackPoints || trackPoints.length === 0) {
    return <EmptyState message="No GPS data available" />;
  }

  const center = trackPoints[Math.floor(trackPoints.length / 2)];
  const bounds = calculateBounds(trackPoints);

  return (
    <Box sx={{ height, width: '100%', position: 'relative' }}>
      <MapContainer
        bounds={bounds}
        style={{ height: '100%', width: '100%' }}
        scrollWheelZoom={false}
      >
        <TileLayer
          url={theme.palette.mode === 'dark'
            ? 'https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png'
            : 'https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png'
          }
          attribution='&copy; OpenStreetMap contributors'
        />
        <Polyline
          positions={trackPoints.map(p => [p.lat, p.lng])}
          color="#ff5722"
          weight={3}
        />
        {/* Start Marker */}
        <Marker position={[trackPoints[0].lat, trackPoints[0].lng]} />
        {/* End Marker */}
        <Marker position={[trackPoints[trackPoints.length - 1].lat, trackPoints[trackPoints.length - 1].lng]} />
      </MapContainer>

      {/* Fullscreen Button */}
      <IconButton
        sx={{ position: 'absolute', top: 8, right: 8, bgcolor: 'background.paper' }}
        onClick={() => setFullscreen(true)}
      >
        <FullscreenIcon />
      </IconButton>
    </Box>
  );
};
```

**Installation**:
```bash
cd frontend
npm install leaflet react-leaflet
npm install -D @types/leaflet
```

#### Step 2.3: Implement ActivityCharts Component
**Priority**: P1  
**Effort**: 4-5 hours  
**Dependencies**: recharts (already installed)  
**Files**: `frontend/src/components/activity/ActivityCharts.tsx`

```typescript
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import { Tabs, Tab } from '@mui/material';

interface ActivityChartsProps {
  streams: {
    pace?: number[];
    heartRate?: number[];
    power?: number[];
    cadence?: number[];
    elevation?: number[];
    distance?: number[]; // x-axis
  } | null;
}

const ActivityCharts: React.FC<ActivityChartsProps> = ({ streams }) => {
  const [activeTab, setActiveTab] = useState(0);
  const theme = useTheme();

  if (!streams) return <EmptyState message="No chart data available" />;

  const chartData = streams.distance?.map((d, i) => ({
    distance: d / 1000, // Convert to km
    pace: streams.pace?.[i],
    heartRate: streams.heartRate?.[i],
    power: streams.power?.[i],
    cadence: streams.cadence?.[i],
    elevation: streams.elevation?.[i],
  })) || [];

  const charts = [
    { label: 'Pace', dataKey: 'pace', unit: 'min/km', color: theme.palette.primary.main },
    { label: 'Heart Rate', dataKey: 'heartRate', unit: 'bpm', color: theme.palette.error.main },
    { label: 'Power', dataKey: 'power', unit: 'W', color: theme.palette.warning.main },
    { label: 'Elevation', dataKey: 'elevation', unit: 'm', color: theme.palette.success.main },
  ].filter(chart => streams[chart.dataKey as keyof typeof streams]);

  return (
    <Box>
      <Tabs value={activeTab} onChange={(e, v) => setActiveTab(v)} sx={{ mb: 2 }}>
        {charts.map((chart, i) => (
          <Tab key={i} label={chart.label} />
        ))}
      </Tabs>

      <ResponsiveContainer width="100%" height={300}>
        <LineChart data={chartData}>
          <CartesianGrid strokeDasharray="3 3" stroke={theme.palette.divider} />
          <XAxis
            dataKey="distance"
            label={{ value: 'Distance (km)', position: 'insideBottom', offset: -5 }}
            stroke={theme.palette.text.secondary}
          />
          <YAxis
            label={{ value: charts[activeTab].unit, angle: -90, position: 'insideLeft' }}
            stroke={theme.palette.text.secondary}
          />
          <Tooltip
            contentStyle={{
              backgroundColor: theme.palette.background.paper,
              border: `1px solid ${theme.palette.divider}`
            }}
          />
          <Line
            type="monotone"
            dataKey={charts[activeTab].dataKey}
            stroke={charts[activeTab].color}
            strokeWidth={2}
            dot={false}
            animationDuration={300}
          />
        </LineChart>
      </ResponsiveContainer>
    </Box>
  );
};
```

#### Step 2.4: Add Activity Detail Route
**Priority**: P0  
**Effort**: 30 minutes  
**Files**: `frontend/src/App.tsx`

```typescript
// Add to Routes
<Route path="/activities/:activityId" element={<ActivityDetail />} />
```

**Update Calendar.tsx**:
```typescript
const handleActivityClick = (activity: GarminActivity) => {
  // Navigate to detail page instead of opening dialog
  navigate(`/activities/${activity.id}`);
};
```

---

### Phase 3: Frontend - Mobile Detail Page (Week 2)
**Goal**: Create thumb-friendly mobile activity detail view

#### Step 3.1: Create Mobile-Optimized Layout
**Priority**: P1  
**Effort**: 5-6 hours  
**Files**: `frontend/src/components/activity/ActivityDetailMobile.tsx`

**Mobile Structure** (from UX design):
```typescript
const ActivityDetailMobile: React.FC = () => {
  const isMobile = useMediaQuery(theme.breakpoints.down('md'));
  
  if (!isMobile) return <ActivityDetail />; // Desktop version

  return (
    <Box sx={{ minHeight: '100vh', pb: 10 }}>
      {/* Sticky AppBar */}
      <AppBar position="sticky" color="default" elevation={0}>
        <Toolbar>
          <IconButton edge="start" onClick={() => navigate(-1)}>
            <ArrowBackIcon />
          </IconButton>
          <Box sx={{ flexGrow: 1 }} />
          <IconButton onClick={handleShare}><ShareIcon /></IconButton>
          <IconButton onClick={handleMenu}><MoreVertIcon /></IconButton>
        </Toolbar>
      </AppBar>

      {/* Hero Card */}
      <Card elevation={0} sx={{ borderRadius: 0 }}>
        <CardContent>
          {/* Sport Type & Tags */}
          <Box sx={{ display: 'flex', gap: 1, mb: 1 }}>
            <Chip icon={<DirectionsRunIcon />} label="Running" size="small" color="primary" />
            <Chip label="Morning Run" size="small" variant="outlined" />
          </Box>

          {/* Activity Title */}
          <Typography variant="h5" fontWeight={600} gutterBottom>
            {activity.activity_name}
          </Typography>

          {/* Date/Time */}
          <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
            <AccessTimeIcon sx={{ fontSize: 16, verticalAlign: 'middle', mr: 0.5 }} />
            {formatDate(activity.start_time_local)}
          </Typography>

          {/* Primary Metrics - Large & Prominent */}
          <Box sx={{ display: 'flex', gap: 3, justifyContent: 'space-around' }}>
            <Box sx={{ textAlign: 'center' }}>
              <Typography variant="h4" fontWeight={700} color="primary">
                {(activity.distance_meters / 1000).toFixed(1)}
              </Typography>
              <Typography variant="caption" color="text.secondary">km</Typography>
            </Box>
            <Box sx={{ textAlign: 'center' }}>
              <Typography variant="h4" fontWeight={700} color="primary">
                {formatDuration(activity.duration_seconds)}
              </Typography>
              <Typography variant="caption" color="text.secondary">duration</Typography>
            </Box>
            <Box sx={{ textAlign: 'center' }}>
              <Typography variant="h4" fontWeight={700} color="primary">
                {formatPace(activity.average_speed_mps)}
              </Typography>
              <Typography variant="caption" color="text.secondary">avg pace</Typography>
            </Box>
          </Box>
        </CardContent>
      </Card>

      {/* Quick Stats Grid (2 cols) */}
      <Card sx={{ m: 2 }}>
        <CardContent>
          <Typography variant="subtitle2" fontWeight={600} gutterBottom>
            Performance
          </Typography>
          <Grid container spacing={2}>
            {[
              { label: 'Avg HR', value: `${activity.average_hr} bpm`, icon: <FavoriteIcon /> },
              { label: 'Max HR', value: `${activity.max_hr} bpm`, icon: <FavoriteIcon /> },
              { label: 'Elevation', value: `+${activity.elevation_gain_meters} m`, icon: <TerrainIcon /> },
              { label: 'TSS', value: activity.calculated_tss, icon: <FitnessCenterIcon /> },
              { label: 'Calories', value: activity.calories, icon: <LocalFireDepartmentIcon /> },
              { label: 'IF', value: activity.intensity_factor?.toFixed(2), icon: <SpeedIcon /> },
            ].map((stat) => (
              <Grid item xs={6} key={stat.label}>
                <Box sx={{
                  display: 'flex',
                  alignItems: 'center',
                  gap: 1,
                  p: 1.5,
                  bgcolor: theme.palette.mode === 'dark' ? 'rgba(255,255,255,0.05)' : 'rgba(0,0,0,0.02)',
                  borderRadius: 2
                }}>
                  <Box sx={{ color: 'text.secondary' }}>{stat.icon}</Box>
                  <Box>
                    <Typography variant="body2" fontWeight={600}>{stat.value}</Typography>
                    <Typography variant="caption" color="text.secondary">{stat.label}</Typography>
                  </Box>
                </Box>
              </Grid>
            ))}
          </Grid>
        </CardContent>
      </Card>

      {/* GPS Map (Collapsible) */}
      <Card sx={{ m: 2 }}>
        <CardContent sx={{ pb: 0 }}>
          <Box
            sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}
            onClick={() => setMapExpanded(!mapExpanded)}
          >
            <Typography variant="subtitle2" fontWeight={600}>Route Map</Typography>
            <IconButton size="small">
              {mapExpanded ? <ExpandLessIcon /> : <ExpandMoreIcon />}
            </IconButton>
          </Box>
        </CardContent>
        <Collapse in={mapExpanded}>
          <Box sx={{ height: 300 }}>
            {loading ? (
              <Skeleton variant="rectangular" height={300} />
            ) : (
              <ActivityMap trackPoints={trackData} height={300} />
            )}
          </Box>
        </Collapse>
      </Card>

      {/* Charts (Collapsible with Tabs) */}
      <Card sx={{ m: 2 }}>
        <CardContent sx={{ pb: 0 }}>
          <Box
            sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}
            onClick={() => setChartsExpanded(!chartsExpanded)}
          >
            <Typography variant="subtitle2" fontWeight={600}>Activity Charts</Typography>
            <IconButton size="small">
              {chartsExpanded ? <ExpandLessIcon /> : <ExpandMoreIcon />}
            </IconButton>
          </Box>
        </CardContent>
        <Collapse in={chartsExpanded}>
          <ActivityCharts streams={streamsData} />
        </Collapse>
      </Card>

      {/* Lap Splits (Collapsible List) */}
      <Card sx={{ m: 2 }}>
        <CardContent>
          <Box
            sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}
            onClick={() => setSplitsExpanded(!splitsExpanded)}
          >
            <Typography variant="subtitle2" fontWeight={600}>Splits ({splits.length})</Typography>
            <IconButton size="small">
              {splitsExpanded ? <ExpandLessIcon /> : <ExpandMoreIcon />}
            </IconButton>
          </Box>
        </CardContent>
        <Collapse in={splitsExpanded}>
          <List disablePadding>
            {splits.map((lap, index) => (
              <ListItem key={index} sx={{ borderTop: 1, borderColor: 'divider', py: 1.5 }}>
                <ListItemIcon>
                  <Avatar sx={{ width: 32, height: 32, bgcolor: 'primary.main', fontSize: '0.875rem' }}>
                    {index + 1}
                  </Avatar>
                </ListItemIcon>
                <ListItemText
                  primary={
                    <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
                      <Typography variant="body2" fontWeight={600}>
                        {lap.distance.toFixed(2)} km
                      </Typography>
                      <Typography variant="body2" fontWeight={600} color="primary">
                        {lap.pace}
                      </Typography>
                    </Box>
                  }
                  secondary={
                    <Box sx={{ display: 'flex', gap: 2, mt: 0.5 }}>
                      <Typography variant="caption" color="text.secondary">
                        HR: {lap.avgHr}
                      </Typography>
                      <Typography variant="caption" color="text.secondary">
                        Elev: +{lap.elevGain}m
                      </Typography>
                    </Box>
                  }
                />
              </ListItem>
            ))}
          </List>
        </Collapse>
      </Card>

      {/* Notes Section */}
      <Card sx={{ m: 2, mb: 10 }}>
        <CardContent>
          <Typography variant="subtitle2" fontWeight={600} gutterBottom>Notes</Typography>
          {activity.notes ? (
            <Typography variant="body2" color="text.secondary" sx={{ whiteSpace: 'pre-wrap' }}>
              {activity.notes}
            </Typography>
          ) : (
            <Box sx={{ textAlign: 'center', py: 3 }}>
              <NoteAddIcon sx={{ fontSize: 48, color: 'text.disabled', mb: 1 }} />
              <Typography variant="body2" color="text.secondary">
                No notes for this activity
              </Typography>
              <Button size="small" startIcon={<AddIcon />} onClick={handleAddNote} sx={{ mt: 1 }}>
                Add Note
              </Button>
            </Box>
          )}
        </CardContent>
      </Card>

      {/* Edit FAB */}
      <Fab
        color="primary"
        sx={{ position: 'fixed', bottom: 16, right: 16, zIndex: 1000 }}
        onClick={handleEdit}
      >
        <EditIcon />
      </Fab>
    </Box>
  );
};
```

#### Step 3.2: Add Swipe Navigation
**Priority**: P2 (Nice to have)  
**Effort**: 2 hours  
**Files**: Same as above

```typescript
// Add swipe handlers
const handlers = useSwipeable({
  onSwipedLeft: () => {
    if (nextActivityId) navigate(`/activities/${nextActivityId}`);
  },
  onSwipedRight: () => {
    if (prevActivityId) navigate(`/activities/${prevActivityId}`);
  },
  trackMouse: false,
  preventDefaultTouchmoveEvent: true,
});

<Box {...handlers}>
  {/* Content */}
</Box>
```

---

### Phase 4: Edit & Additional Features (Week 3)
**Goal**: Enable activity editing and advanced features

#### Step 4.1: Activity Edit Dialog
**Priority**: P1  
**Effort**: 3-4 hours  
**Files**: `frontend/src/components/activity/ActivityEditDialog.tsx`

```typescript
interface ActivityEditDialogProps {
  activity: Activity;
  open: boolean;
  onClose: () => void;
  onSave: (updated: Partial<Activity>) => Promise<void>;
}

const ActivityEditDialog: React.FC<ActivityEditDialogProps> = ({
  activity,
  open,
  onClose,
  onSave,
}) => {
  const [title, setTitle] = useState(activity.activity_name);
  const [notes, setNotes] = useState(activity.notes || '');
  const [equipment, setEquipment] = useState('');
  const [saving, setSaving] = useState(false);

  const handleSave = async () => {
    setSaving(true);
    try {
      await onSave({
        activity_name: title,
        notes,
        // equipment
      });
      onClose();
    } catch (error) {
      // Handle error
    } finally {
      setSaving(false);
    }
  };

  return (
    <Dialog open={open} onClose={onClose} maxWidth="sm" fullWidth>
      <DialogTitle>Edit Activity</DialogTitle>
      <DialogContent>
        <TextField
          label="Activity Title"
          value={title}
          onChange={(e) => setTitle(e.target.value)}
          fullWidth
          sx={{ mt: 2 }}
        />
        <TextField
          label="Notes"
          value={notes}
          onChange={(e) => setNotes(e.target.value)}
          fullWidth
          multiline
          rows={4}
          sx={{ mt: 2 }}
        />
        {/* Add equipment selector */}
      </DialogContent>
      <DialogActions>
        <Button onClick={onClose}>Cancel</Button>
        <Button onClick={handleSave} variant="contained" disabled={saving}>
          {saving ? 'Saving...' : 'Save'}
        </Button>
      </DialogActions>
    </Dialog>
  );
};
```

#### Step 4.2: Activity Sharing
**Priority**: P2  
**Effort**: 2 hours

```typescript
const handleShare = async () => {
  if (navigator.share) {
    // Use Web Share API
    await navigator.share({
      title: activity.activity_name,
      text: `Check out my ${activity.activity_type}: ${(activity.distance_meters / 1000).toFixed(1)} km in ${formatDuration(activity.duration_seconds)}`,
      url: window.location.href,
    });
  } else {
    // Fallback: Copy link
    navigator.clipboard.writeText(window.location.href);
    setSnackbar('Link copied to clipboard');
  }
};
```

#### Step 4.3: Activity List Page
**Priority**: P2  
**Effort**: 4-5 hours  
**Files**: `frontend/src/pages/Activities.tsx`

**Features**:
- Sortable/filterable activity list
- Virtual scrolling for performance (react-window)
- Sport type filters
- Date range filters
- Search by title
- Thumbnail map previews (optional)

---

### Phase 5: Testing & Polish (Week 3-4)
**Goal**: Ensure quality and performance

#### Step 5.1: Performance Optimization
**Priority**: P1  
**Effort**: 2-3 hours

**Tasks**:
- [ ] Lazy load map component (`React.lazy`)
- [ ] Lazy load charts component
- [ ] Implement intersection observer for collapsible sections
- [ ] Add skeleton loading states
- [ ] Optimize bundle size (check with `npm run build`)
- [ ] Cache track/streams data (React Query or SWR)
- [ ] Add service worker caching for offline support (PWA)

#### Step 5.2: Responsive Testing
**Priority**: P1  
**Effort**: 2-3 hours

**Test Matrix**:
| Device | Screen Size | Browser | Test |
|--------|-------------|---------|------|
| iPhone SE | 375px | Safari | ✅ Navigation, touch targets, readability |
| iPhone 14 | 390px | Safari | ✅ All features |
| Pixel 5 | 393px | Chrome | ✅ All features |
| iPad Mini | 768px | Safari | ✅ Tablet layout |
| Desktop | 1920px | Chrome | ✅ Desktop layout |

**Checklist**:
- [ ] All touch targets min 44x44px
- [ ] Text readable without zooming
- [ ] Charts render correctly on small screens
- [ ] Maps are usable (pan, zoom)
- [ ] Collapsible sections work smoothly
- [ ] No horizontal scrolling
- [ ] Dark mode tested
- [ ] Loading states work
- [ ] Empty states look good

#### Step 5.3: Accessibility Audit
**Priority**: P1  
**Effort**: 2 hours

**Tools**:
- Lighthouse (Chrome DevTools)
- axe DevTools extension
- Screen reader testing (VoiceOver, TalkBack)

**Checklist**:
- [ ] All images have alt text
- [ ] Semantic HTML (headings, landmarks)
- [ ] ARIA labels on icons/buttons
- [ ] Keyboard navigation works
- [ ] Focus visible on interactive elements
- [ ] Color contrast meets WCAG AA
- [ ] Screen reader announces state changes

#### Step 5.4: Error Handling
**Priority**: P1  
**Effort**: 2 hours

**Scenarios**:
- [ ] Activity not found (404)
- [ ] Network error fetching data
- [ ] No GPS data available
- [ ] No heart rate data
- [ ] Failed to load map tiles
- [ ] Chart data parsing error
- [ ] User not authorized (403)

**Implementation**:
```typescript
// Error boundary for charts
<ErrorBoundary fallback={<ChartErrorFallback />}>
  <ActivityCharts streams={streamsData} />
</ErrorBoundary>

// Graceful degradation
{trackData.length === 0 ? (
  <Alert severity="info">
    No GPS data available for this activity
  </Alert>
) : (
  <ActivityMap trackPoints={trackData} />
)}
```

---

## Success Criteria

### Functional Requirements
- ✅ Activity detail page accessible via `/activities/:id`
- ✅ Full activity data displayed (summary, stats, map, charts, splits)
- ✅ Responsive design works on mobile (375px+) and desktop
- ✅ Dark mode support
- ✅ Edit activity metadata (title, notes)
- ✅ Share activity (Web Share API)
- ✅ Navigation from Calendar to detail page
- ✅ Breadcrumbs/back button navigation

### Performance Requirements
- ✅ Page load time < 2 seconds on 4G
- ✅ Lighthouse score > 90 (Performance, Accessibility, Best Practices)
- ✅ No layout shift (CLS < 0.1)
- ✅ Smooth scrolling and interactions (60fps)
- ✅ Bundle size increase < 100KB gzipped

### UX Requirements
- ✅ Mobile-first design with progressive disclosure
- ✅ All touch targets min 44x44px
- ✅ Clear visual hierarchy
- ✅ Loading states for all async operations
- ✅ Empty states for missing data
- ✅ Error messages are helpful and actionable
- ✅ Consistent with existing TrainingPlan design language

---

## Risk Management

| Risk | Impact | Mitigation |
|------|--------|------------|
| **GPS data not available** | High | Show empty state, hide map section |
| **Time-series data too large** | Medium | Downsample data (1 point per 5 seconds), lazy load |
| **Garmin API rate limits** | Medium | Cache data in database, limit requests |
| **Map tile loading slow** | Medium | Show skeleton, cache tiles, use CDN |
| **Mobile performance issues** | High | Lazy load components, virtual scrolling for splits |
| **Dark mode map readability** | Low | Use dark map tiles, test contrast |

---

## Timeline Summary

| Phase | Duration | Key Deliverables |
|-------|----------|------------------|
| **Phase 1: Backend API** | Week 1 | Activity detail endpoints, track/streams/splits APIs |
| **Phase 2: Desktop Detail** | Week 1-2 | Full-page detail view, map, charts, splits |
| **Phase 3: Mobile Detail** | Week 2 | Mobile-optimized collapsible layout |
| **Phase 4: Edit & Features** | Week 3 | Edit dialog, sharing, activity list |
| **Phase 5: Testing & Polish** | Week 3-4 | Performance, responsive, accessibility |

**Total Duration**: 3-4 weeks (part-time)

---

## Post-Launch Enhancements

### Future Features (Phase 6+)
- [ ] Activity comparison (compare 2 activities side-by-side)
- [ ] Segment analysis (custom segments with leaderboards)
- [ ] Photo upload (attach photos to activities)
- [ ] Social features (comments, kudos)
- [ ] Export activity (GPX, TCX, FIT formats)
- [ ] Print activity summary
- [ ] Heatmap view (all activities overlay)
- [ ] 3D elevation profile
- [ ] Video analysis integration
- [ ] Weather data integration (historical weather)
- [ ] Training zones overlay on charts
- [ ] Anomaly detection (unusual HR spikes, etc.)
- [ ] AI-powered insights ("This was your fastest 5K pace!")

---

## Dependencies

### Backend
- Python 3.11+
- FastAPI
- SQLAlchemy (async)
- PostgreSQL + TimescaleDB
- garminconnect library
- fitparse (FIT file parsing)

### Frontend
- React 18
- TypeScript
- Material-UI v5
- React Router v6
- Leaflet + react-leaflet
- Recharts
- react-swipeable
- React Query (optional, for caching)

### DevOps
- Docker (for local development)
- GitHub Actions (CI/CD)

---

## References

- [TrainingPeaks Activity Detail](https://www.trainingpeaks.com/) - Inspiration for desktop layout
- [Strava Activity Page](https://www.strava.com/) - Inspiration for charts and stats
- [Material Design Guidelines](https://m3.material.io/) - Mobile patterns
- [Leaflet Documentation](https://leafletjs.com/) - Map integration
- [Recharts Examples](https://recharts.org/en-US/examples) - Chart patterns

---

**Last Updated**: January 5, 2026  
**Next Review**: After Phase 1 completion
