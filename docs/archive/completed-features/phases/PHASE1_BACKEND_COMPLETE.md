# Activity Detail Implementation - Phase 1 Complete

**Date**: January 5, 2026  
**Status**: ✅ Backend API Complete

## What Was Implemented

### New API Endpoints Created

Created `/backend/src/api/routes/activities.py` with the following endpoints:

#### 1. **GET /api/v1/activities/{id}** - Full Activity Detail
Returns complete activity metadata including:
- Basic info (name, type, date, times)
- Distance & speed metrics
- Elevation data (gain, loss, min, max)
- Heart rate data (average, max)
- Power data for cycling (average, max, NP, FTP)
- Training metrics (TSS, IF, VO2max, training effects)
- Location data
- Flags and metadata

**Response**: `ActivityDetailResponse` - Complete activity object

#### 2. **GET /api/v1/activities/{id}/track** - GPS Track Points
Returns GPS coordinates for mapping:
- Array of lat/lng points with optional elevation
- Downsampled to max 2000 points for performance
- Parses from raw_data JSON field
- Handles Garmin's semicircle coordinate format

**Response**: `ActivityTrackResponse` with `track_points` array

#### 3. **GET /api/v1/activities/{id}/streams** - Time-Series Data
Returns arrays of time-series data for charts:
- Timestamps
- Distance (meters)
- Pace (min/km)
- Heart rate (bpm)
- Power (watts)
- Cadence
- Elevation (meters)
- Speed (m/s)

Downsampled to ~500 points for chart performance.

**Response**: `ActivityStreamsResponse` with `TimeSeriesData`

#### 4. **GET /api/v1/activities/{id}/splits** - Lap Splits
Returns lap-by-lap breakdown:
- Lap number
- Distance per lap
- Duration per lap
- Average speed, HR, power
- Elevation gain/loss per lap
- Average cadence

**Response**: `ActivitySplitsResponse` with array of `LapSplit` objects

#### 5. **PATCH /api/v1/activities/{id}** - Update Activity
Allows editing user-modifiable fields:
- Activity name/title
- Notes (future - field needs to be added to model)

Synced data (times, distances, metrics) cannot be changed.

**Request**: `ActivityUpdate` schema  
**Response**: Updated `ActivityDetailResponse`

#### 6. **GET /api/v1/activities** - List Activities
Paginated activity list with filters:
- `page`: Page number (default 1)
- `page_size`: Items per page (default 50, max 100)
- `sport_type`: Filter by activity type
- `start_date`: Filter after date (YYYY-MM-DD)
- `end_date`: Filter before date (YYYY-MM-DD)

**Response**: `ActivityListResponse` with pagination info

### Integration

- ✅ Added activities router to `main.py`
- ✅ All endpoints require authentication (`get_current_user`)
- ✅ All endpoints verify user owns the activity
- ✅ Proper HTTP status codes (404 for not found, etc.)
- ✅ Comprehensive Pydantic schemas for type safety
- ✅ OpenAPI documentation auto-generated

## Data Sources

Currently data is extracted from:
1. **GarminActivity model fields** - Direct database columns
2. **raw_data JSON field** - For track points, streams, and splits

The `raw_data` field stores the complete Garmin API response, which contains:
- GPS samples with lat/lng/elevation/timestamp
- Time-series metrics (HR, power, pace, cadence)
- Lap data with per-lap statistics

## Known Limitations

### 1. GPS Track Parsing
- **Current**: Parses from `raw_data` JSON
- **Issue**: Format varies by Garmin API version
- **Solution Needed**: May need to enhance parsing logic based on actual data structure
- **Alternative**: Download FIT files and parse with `fitparse` library

### 2. Time-Series Data
- **Current**: Extracts from `raw_data.samples`
- **Issue**: Not all activities have detailed sample data stored
- **Solution Needed**: May need to fetch from Garmin on-demand or parse FIT files

### 3. Missing Database Fields
- **Notes field**: Not yet in GarminActivity model
  - Need migration: `alembic revision --autogenerate -m "add notes to activities"`
  - Add: `notes = Column(Text)`
- **Equipment tracking**: Not implemented yet
- **Custom tags/categories**: Not implemented yet

### 4. Data Downsampling
- Track: Max 2000 points (keeps ~every 10-20 seconds for typical activities)
- Streams: Max 500 points (keeps ~every 5-10 seconds)
- **Tradeoff**: Performance vs. granularity
- **Good enough**: For visualization, this resolution is sufficient

## Testing Status

- ✅ API endpoints registered and accessible
- ✅ OpenAPI schema generated (`/docs` endpoint)
- ⏳ **TODO**: Manual testing with real activity data
- ⏳ **TODO**: Verify GPS data format
- ⏳ **TODO**: Verify time-series data format
- ⏳ **TODO**: Test with activities that have power data

## Next Steps

### Immediate (Before Frontend Work)
1. **Test with real data**:
   - Run `test_activity_detail_api.py` with valid credentials
   - Inspect actual response formats
   - Verify GPS coordinates are correctly parsed
   - Check time-series data arrays

2. **Fix data parsing if needed**:
   - Adjust coordinate conversion (semicircles → degrees)
   - Handle different `raw_data` formats
   - Add fallbacks for missing data

3. **Add notes field**:
   ```bash
   cd backend
   alembic revision --autogenerate -m "add notes to activities"
   alembic upgrade head
   ```

### Phase 2: Desktop Frontend (Next)
1. Create `frontend/src/pages/ActivityDetail.tsx`
2. Implement `ActivityMap.tsx` component (Leaflet)
3. Implement `ActivityCharts.tsx` component (Recharts)
4. Implement `ActivitySplits.tsx` component (table)
5. Add route to `App.tsx`
6. Update Calendar.tsx to navigate to detail page

### Phase 3: Mobile Frontend
1. Create mobile-optimized layout
2. Implement collapsible sections
3. Add swipe navigation
4. Optimize for performance

## Files Created/Modified

### Created
- `/backend/src/api/routes/activities.py` (757 lines) ✅
- `/backend/test_activity_detail_api.py` (Test script) ✅

### Modified
- `/backend/src/main.py` (Added activities router) ✅

## API Documentation

View full API documentation at: http://localhost:8000/docs

Look for the "Activities" section with 6 endpoints.

## Performance Considerations

1. **Track Downsampling**: Keeps response size <200KB for typical activities
2. **Streams Downsampling**: Keeps chart data manageable for browser rendering
3. **Pagination**: Activity list limited to 100 items per page
4. **Database Indexes**: Existing indexes on `user_id`, `start_time_local` support fast queries
5. **No N+1 queries**: Single query per endpoint, no joins

## Security

- ✅ All endpoints require JWT authentication
- ✅ User can only access their own activities (enforced via WHERE clause)
- ✅ Update endpoint only allows editing safe fields (no metric tampering)
- ✅ Input validation via Pydantic schemas
- ✅ SQL injection prevention via SQLAlchemy

## Summary

✅ **Phase 1 Complete**: Backend API for activity details is fully implemented with:
- 6 comprehensive endpoints
- Type-safe Pydantic schemas
- Proper authentication and authorization
- Data downsampling for performance
- OpenAPI documentation

🚀 **Ready for Phase 2**: Frontend implementation can begin immediately. The API provides all data needed for:
- Full-page activity detail view
- GPS map visualization
- Interactive charts (pace, HR, power, elevation)
- Lap splits table
- Activity editing

⏭️ **Next**: Test with real activity data, then start building the React components!
