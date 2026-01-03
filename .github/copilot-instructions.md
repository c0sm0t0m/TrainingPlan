# TrainingPlan - AI Agent Instructions

## Project Overview
TrainingPlan is a self-hosted triathlon/running training platform built for deployment on QNAP NAS. It's a full-stack web app with FastAPI backend, React frontend, and PostgreSQL+TimescaleDB for time-series workout data.

**Core Purpose**: Manage training plans, sync with Garmin Connect, track activities, analyze training load (TSS/CTL/ATL/TSB).

## Architecture & Data Flow

### Backend Structure (`backend/src/`)
- **`main.py`**: FastAPI app entry point. **CRITICAL**: Injects `truststore` into SSL before any imports to fix SSL cert issues on Python 3.13+
- **`config.py`**: Pydantic settings from `.env`. All config lives here - no hardcoded values
- **`database.py`**: Async SQLAlchemy setup using `asyncpg` driver. Use `get_db()` dependency for route handlers
- **`models/`**: SQLAlchemy models with `Base` from `database.py`. Key models:
  - `User` - Basic auth, stores encrypted Garmin tokens
  - `TrainingPlan` - Plans with phases, target races
  - `GarminActivity` - Activity metadata (uses TimescaleDB hypertable for time-series optimization)
- **`api/routes/`**: FastAPI routers. Include with `app.include_router(router, prefix="/api/v1", tags=[...])`
- **`services/`**: Business logic layer. **Key services**:
  - `garmin_service.py` - Primary Garmin integration using `garminconnect` library (NOT garth)
  - `garmin_service_old_garth.py` - Deprecated garth-based implementation (keep for reference)
  - Garmin auth flow: Login → Store OAuth tokens in User model → Use tokens for API calls

### Frontend Structure (`frontend/src/`)
- **React 18 + TypeScript + Vite**: Fast dev server with HMR
- **State Management**: Zustand (`store/`) for global state
- **UI Framework**: Material-UI v5 with custom theme in `App.tsx`
- **Routing**: React Router v6 (`pages/` for routes)
- **API Client**: Axios service wrappers in `services/`
- **Maps**: Leaflet + react-leaflet for activity GPS tracks

### Database
- **PostgreSQL 15 + TimescaleDB**: Time-series optimized for activities
- **Migrations**: Alembic in `backend/alembic/versions/`
- **Init Script**: `scripts/init-db.sql` runs on first docker-compose up
- To create migration: `cd backend && alembic revision --autogenerate -m "description"`
- To apply: `alembic upgrade head`

## Development Workflows

### Running Locally (Preferred Method)
```bash
# Backend (Terminal 1)
cd backend
source venv/bin/activate  # or venv313/bin/activate for Python 3.13
uvicorn src.main:app --reload --port 8000

# Frontend (Terminal 2)
cd frontend
npm run dev  # Runs on port 5173
```

**Note**: Can run without database initially. Full setup requires Docker Compose for PostgreSQL+Redis.

### Running with Docker Compose
```bash
docker-compose up -d  # Starts postgres, redis, backend, celery worker, celery beat
docker-compose logs -f backend  # View backend logs
docker-compose down  # Stop all services
```

### Testing
- **Interactive Tests**: Use bash scripts like `test_full_flow.sh`, `test_garmin_auth.py`
- Scripts test full auth flow: Register user → Login → Get token → Test protected endpoints
- Python tests use `httpx` for async HTTP, `pytest` for test framework
- **Run tests**: `cd backend && pytest tests/`

### Garmin Integration
- Read `backend/GARMIN_WORKOUT_SYNC_IMPLEMENTATION.md` for implementation details
- **Working**: Workout upload to library AND calendar scheduling via Consumer API
- Uses `garmin_planner` approach: `POST /workout-service/schedule/{workout_id}` with date payload
- Scheduling returns `workoutScheduleId` on success

## Project-Specific Conventions

### Python Code Style
- **Async First**: All route handlers and DB operations are async (`async def`, `await db.execute()`)
- **Dependency Injection**: Use FastAPI's `Depends()` for DB sessions, auth
- **Type Hints**: Required on all functions (Pydantic models enforce this)
- **SSL Handling**: Always import `truststore.inject_into_ssl()` at top of `main.py` before other imports

### UI/UX Principles
- **Navigation First**: Every page MUST have clear navigation (back buttons, breadcrumbs, or global nav)
- **Mobile Responsive**: ALL components must work on mobile (use Material-UI breakpoints, test on small screens)
- **User Feedback**: Provide loading states, success/error messages, and confirmation for destructive actions
- **Accessibility**: Use semantic HTML, ARIA labels, keyboard navigation support
- **Consistency**: Follow Material-UI design patterns, consistent spacing (theme.spacing()), consistent button placements
- **Progressive Disclosure**: Show summary first, expand details on demand (avoid information overload)
- **Optimistic UI**: Update UI immediately for fast perceived performance, revert on API errors
- **Empty States**: When lists are empty, show helpful message + clear CTA (e.g., "Create your first plan")
- **Context-Aware Actions**: Primary actions should be accessible via FAB or contextual menus
- **Wayfinding**: Users should always know where they are (breadcrumbs, active nav indicators, page titles)

### API Patterns
```python
# Standard route handler pattern
@router.get("/endpoint", response_model=schemas.ResponseModel)
async def get_something(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    result = await db.execute(select(Model).where(...))
    return result.scalars().first()
```

### Garmin Service Usage
```python
from src.services.garmin_service import GarminService

# Initialize with user's stored tokens
service = GarminService(
    email=user.garmin_email,
    oauth1_token=user.garmin_oauth1_token,
    oauth2_token=user.garmin_oauth2_token
)

# All methods are async
activities = await service.get_activities(start_date, end_date)
```

### Frontend API Calls
```typescript
// Use axios service wrappers in src/services/
import api from '@/services/api'

const response = await api.get('/api/v1/plans')
const plans = response.data
```

### Frontend Navigation Patterns
**REQUIRED**: Every page must implement at least ONE of these navigation patterns:

1. **Global AppBar** (preferred for most pages):
```typescript
<ApUI/UX Best Practices

### Navigation Architecture
**CRITICAL**: TrainingPlan uses an **App Shell pattern** (industry standard for SPAs)
- **AppBar** (persistent top bar): Logo, primary nav, user menu
- **Drawer** (optional side nav): For more navigation options on desktop
- **Bottom Navigation** (mobile): 4-5 primary actions for thumb-friendly access
- **Never orphan users**: Every page must have a way to navigate elsewhere

### Common UX Patterns to Follow

1. **Loading States**: Use Material-UI Skeleton components, not "Loading..." text
```typescript
{loading ? <Skeleton variant="rectangular" height={200} /> : <ActualContent />}
```

2. **Empty States**: Guide users when data is empty
```typescript
{items.length === 0 && (
  <Box sx={{ textAlign: 'center', py: 8 }}>
    <Typography variant="h6">No items yet</Typography>
    <Button variant="contained" onClick={handleCreate}>Create First Item</Button>
  </Box>
)}
```

3. **Toast Notifications**: Use Snackbar for feedback, not inline Alerts
```typescript
<Snackbar open={open} message="Action completed" autoHideDuration={3000} />
```

4. **Floating Action Button**: Primary action should be prominent
```typescript
<Fab 
  color="primary" 
  sx={{ position: 'fixed', bottom: 16, right: 16 }}
  onClick={handlePrimaryAction}
>
  <AddIcon />
</Fab>
```

5. **Responsive Design**: Always test on mobile breakpoints
```typescript
const isMobile = useMediaQuery(theme.breakpoints.down('md'));
<Box sx={{ 
  flexDirection: isMobile ? 'column' : 'row',
  gap: isMobile ? 1 : 2 
}}>
```

6. **Document Titles**: Set page-specific titles
```typescript
useEffect(() => {
  document.title = 'Training Calendar - TrainingPlan';
}, []);
```

### Design Consistency Rules
- **Spacing**: Use theme.spacing() (2, 3, 4) not hardcoded pixels
- **Colors**: Use theme.palette colors, not hardcoded hex values
- **Typography**: Use variant prop (h1-h6, body1, body2, caption)
- **Button Hierarchy**: 
  - Primary action: `variant="contained"`
  - Secondary: `variant="outlined"`
  - Tertiary: `variant="text"`
- **Card Layout**: Use Card > CardContent > CardActions consistently

## pBar position="sticky">
  <Toolbar>
    <Typography variant="h6" onClick={() => navigate('/dashboard')} sx={{ cursor: 'pointer' }}>
      TrainingPlan
    </Typography>
    <Button color="inherit" onClick={() => navigate('/calendar')}>Calendar</Button>
    <Button color="inherit" onClick={() => navigate('/plans')}>Plans</Button>
  </Toolbar>
</AppBar>
```

2. **Breadcrumbs** (for deep pages like Plan Detail):
```typescript
<Breadcrumbs aria-label="breadcrumb" sx={{ mb: 2 }}>
  <Link color="inherit" href="/dashboard">Home</Link>
  <Link color="inherit" href="/plans">Training Plans</Link>
  <Typography color="text.primary">{plan.name}</Typography>
</Breadcrumbs>
```

3. **Back Button** (minimum viable navigation):
```typescript
<Button 
  startIcon={<ArrowBackIcon />} 
  onClick={() => navigate(-1)} // or navigate('/parent-route')
  sx={{ mb: 2 }}
>
  Back
</Button>
```

**Mobile Navigation**: Use `useMediaQuery(theme.breakpoints.down('md'))` to show drawer/bottom nav on mobile

**Active Page Indicator**: Highlight current page in navigation using `useLocation().pathname`

### Environment Variables
- **Backend**: All config in `.env`, loaded via `pydantic-settings`
- **Required vars**: `DATABASE_URL`, `REDIS_URL`, `SECRET_KEY`
- **Optional**: Garmin/Strava/TrainingPeaks credentials (empty = disabled)

## Critical Knowledge

### Garmin Integration Gotchas
1. **SSL Certificates**: Python 3.13+ requires `truststore` injection (already in `main.py`)
2. **Library Choice**: Use `garminconnect`, NOT `garth` - access underlying `garth.connectapi()` for scheduling
3. **Token Storage**: Store both OAuth1 and OAuth2 tokens in User model (both required)
4. **Workout Scheduling**: Use `api.garth.connectapi(f"/workout-service/schedule/{workout_id}", method="POST", json={"date": "YYYY-MM-DD"})`
5. **FIT File Upload**: `upload_activity()` is for GPS activities, NOT workouts (406 error)

### Database Patterns
- **TimescaleDB Hypertables**: `GarminActivity` table is optimized for time-series queries
- **Async Operations**: Always use `await db.execute()`, never synchronous queries
- **Session Management**: Use `get_db()` dependency, sessions auto-close
- **⚠️ CRITICAL - SQLite Date/Time Handling**: 
  - SQLite stores DateTime as TEXT (e.g., "2025-12-31 09:47:02.000000")
  - SQLAlchemy DateTime columns are stored as TEXT strings in SQLite
  - **ALWAYS use helper functions** from `src/utils/datetime_helpers.py`:
    - `compare_date_for_sqlite()` - For query comparisons
    - `date_to_string()` - Extract YYYY-MM-DD from any date type
    - `parse_sqlite_datetime()` - Parse TEXT to datetime object
  - Wrong: `GarminActivity.start_time_local >= datetime(2025, 12, 1)`
  - Right: `GarminActivity.start_time_local >= compare_date_for_sqlite(datetime(2025, 12, 1))`
  - **Why**: SQLite doesn't have native date types; comparisons must be string-based
  - **Production**: PostgreSQL will handle DateTime properly with native types
  - This issue has occurred multiple times - always use helper functions

### Training Zone Calculations
- **⚠️ CRITICAL - Always use `round()` for zone boundaries, NEVER `int()`**:
  - Wrong: `int(ftp * 0.755)` truncates → incorrect boundaries
  - Right: `round(ftp * 0.755)` rounds properly → matches TrainingPeaks
  - Example: FTP 245 × 0.755 = 184.975 → `int()` gives 184, `round()` gives 185 ✅
- **Use exact percentages from TrainingPeaks documentation**:
  - Coggan Power: 55.5%, 75.5%, 90.5%, 105.7%, 120.8%, 121.2%
  - NOT simplified: 55%, 75%, 90%, 105%, 120%
- **Make zones continuous** (no gaps between zones):
  - Zone N+1 min = Zone N max + 1
  - Example: Zone 1: 10-136W, Zone 2: 137-185W (NOT 137-184W)
- **Use realistic min/max boundaries**:
  - Power zones: min=10W (not 0), max=2000W (not 9999)
  - HR zones: min based on calculation, max=actual max_hr (not 9999)
  - Pace zones: handle infinity display properly in UI (9999 → "∞")
- **Reference TrainingPeaks UI for validation**:
  - Always verify calculated zones match TP's auto-calculation
  - TP uses specific rounding and boundary logic - replicate exactly
- This prevents "Zone 2: 137 to 184" when it should be "137 to 185"

### Docker Deployment
- **QNAP Target**: Designed for QNAP Container Station (docker-compose based)
- **Volumes**: Persistent data in named volumes (`postgres_data`, `redis_data`, `uploads_data`)
- **Network**: Internal network `trainingplan_network` for service communication

## Key Files to Reference

- [TECH_STACK.md](../TECH_STACK.md) - Detailed technology decisions and alternatives
- [PROJECT_PLAN.md](../PROJECT_PLAN.md) - Implementation roadmap and requirements
- [LOCAL_DEV_SETUP.md](../LOCAL_DEV_SETUP.md) - Quick start without Docker
- [backend/GARMIN_WORKOUT_SYNC_IMPLEMENTATION.md](../backend/GARMIN_WORKOUT_SYNC_IMPLEMENTATION.md) - Garmin API limitations and solutions
- [backend/src/services/garmin_service.py](../backend/src/services/garmin_service.py) - Primary Garmin integration
- [backend/src/config.py](../backend/src/config.py) - All configuration settings
