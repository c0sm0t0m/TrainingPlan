# HRV Data Model Implementation - Summary

**Date**: 2026-01-05  
**Status**: ✅ **COMPLETE**

## What Was Implemented

### 1. Database Model (`garmin_hrv` table)

Created a new table to store daily HRV data with:

**Primary Fields:**
- `calendar_date` - One record per day per user
- `last_night_avg` - **PRIMARY RMSSD VALUE** (nightly average in milliseconds)
- `weekly_avg` - 7-day rolling average
- `last_night_5min_high` - Highest 5-minute average during sleep

**Baseline Values:**
- `baseline_low_upper` - Upper bound of "low" zone
- `baseline_balanced_low` - Lower bound of "balanced" zone  
- `baseline_balanced_upper` - Upper bound of "balanced" zone
- `baseline_marker_value` - Normalized marker (0-1 scale)

**Status & Feedback:**
- `status` - BALANCED, LOW, UNBALANCED
- `feedback_phrase` - Garmin's feedback key
- `create_timestamp` - When Garmin processed the data

**Time Windows:**
- `sleep_start_time_gmt/local` - Sleep detection times
- `sleep_end_time_gmt/local`
- `start_time_gmt/local` - Measurement window
- `end_time_gmt/local`

**Time Series Data:**
- `hrv_readings` - **JSON array** containing ~60-100 individual HRV readings
  - Each reading: `{ "hrvValue": 45, "readingTimeGMT": "...", "readingTimeLocal": "..." }`
  - Measurements every 5 minutes during sleep
- `raw_data` - Full response from Garmin API

**Indexes:**
- Primary key on `id`
- Index on `calendar_date`
- **Unique composite index** on `(user_id, calendar_date)` - prevents duplicates

### 2. SQLAlchemy Model

File: `backend/src/models/garmin_hrv.py`

```python
class GarminHRV(Base):
    __tablename__ = "garmin_hrv"
    
    # One record per user per day
    calendar_date = Column(Date, nullable=False, index=True)
    last_night_avg = Column(Float, nullable=True)  # PRIMARY RMSSD
    hrv_readings = Column(JSON, nullable=True)  # COMPLETE TIME SERIES
    # ... other fields
```

### 3. Database Migration

File: `backend/alembic/versions/20260105_add_hrv_table.py`

- Migration ID: `20260105_add_hrv`
- Creates table with all fields
- Creates indexes
- ✅ **Successfully applied** to database

### 4. Service Method

File: `backend/src/services/garmin_service.py`

```python
async def sync_hrv_data(
    self,
    oauth1_token: str,
    oauth2_token: str,
    days_back: int = 30
) -> List[Dict]:
    """
    Fetch HRV data from Garmin Connect for the last N days.
    
    Returns list of dictionaries with:
    - calendar_date
    - last_night_avg (RMSSD)
    - weekly_avg
    - hrv_readings (complete time series)
    - baseline values
    - status
    - timestamps
    """
```

### 5. User Relationship

Updated `backend/src/models/user.py`:

```python
class User(Base):
    # Relationships
    garmin_hrv_data = relationship("GarminHRV", back_populates="user", cascade="all, delete-orphan")
```

## Data Examples

### Daily Summary (from database)
```
Date: 2026-01-05
Last Night Avg (RMSSD): 45.0 ms
Weekly Avg: 47.0 ms
Status: BALANCED
Time Series Readings: 66 measurements
Baseline Range: 38.0 - 58.0 ms
```

### Time Series Sample
```json
[
  {
    "hrvValue": 37,
    "readingTimeGMT": "2026-01-04T23:02:20.0",
    "readingTimeLocal": "2026-01-05T00:02:20.0"
  },
  {
    "hrvValue": 45,
    "readingTimeGMT": "2026-01-04T23:17:20.0",
    "readingTimeLocal": "2026-01-05T00:17:20.0"
  },
  // ... 60-100 readings per night
]
```

## Verification

### Test Results
✅ **7 days of HRV data synced successfully**

```bash
$ python3 test_hrv_sync.py

✅ Authentication successful
✅ Fetched 7 HRV records  
✅ Stored 7 new records
✅ Verified data in database:
   • Daily RMSSD values: 33-54 ms
   • Time series: 58-108 readings per night
   • All timestamps present
   • Baseline values stored
```

### Database Query
```sql
SELECT 
    calendar_date,
    last_night_avg,
    json_array_length(hrv_readings) as num_readings
FROM garmin_hrv
ORDER BY calendar_date DESC;

-- Results:
2026-01-05 | 45.0 | 66 readings
2026-01-04 | 50.0 | 94 readings
2026-01-03 | 53.0 | 72 readings
```

## Key Features

✅ **Daily RMSSD Value**: Primary recovery metric stored in `last_night_avg`  
✅ **Complete Time Series**: Full nightly HRV readings in `hrv_readings` JSON  
✅ **5-Minute Intervals**: ~60-100 measurements per night  
✅ **No Duplicates**: Unique constraint on (user_id, date)  
✅ **Update Support**: Can re-sync to update existing records  
✅ **Baseline Tracking**: Personalized ranges for status determination  
✅ **Status Classification**: BALANCED/LOW/UNBALANCED from Garmin  

## Next Steps (Not Yet Implemented)

### API Endpoints
- `POST /api/v1/garmin/sync-hrv` - Trigger HRV sync
- `GET /api/v1/garmin/hrv` - Get HRV history
- `GET /api/v1/garmin/hrv/{date}` - Get specific day
- `GET /api/v1/garmin/hrv/latest` - Get most recent HRV

### UI Components
- HRV trend chart (7-day, 30-day)
- Recovery status indicator
- Baseline range visualization
- Correlation with training load (TSB)
- Sleep quality comparison

### Analytics
- HRV trends over time
- Correlation with workout intensity
- Recovery recommendations
- Overtraining detection

## Files Created/Modified

**New Files:**
- `backend/src/models/garmin_hrv.py` - Model definition
- `backend/alembic/versions/20260105_add_hrv_table.py` - Migration
- `backend/test_hrv_sync.py` - Test script
- `backend/HRV_DATA_AVAILABILITY.md` - API documentation

**Modified Files:**
- `backend/src/models/user.py` - Added HRV relationship
- `backend/src/services/garmin_service.py` - Added `sync_hrv_data()` method

## Technical Notes

### RMSSD Definition
- **RMSSD**: Root Mean Square of Successive Differences
- Measures time variations between heartbeats
- Reflects parasympathetic nervous system activity
- Higher values = better recovery
- Individual baselines vary (20-100 ms typical)

### Storage Strategy
- **Daily summary** fields for quick queries
- **Full time series** in JSON for detailed analysis
- **Normalized timestamps** (GMT + Local) for timezone handling
- **Baseline history** to track long-term changes

### Data Quality
- Garmin measures during sleep (most accurate)
- Optical HR sensor (less accurate than chest strap)
- Individual variation is normal
- Trend more important than absolute values

## Conclusion

✅ **Data model successfully implemented**  
✅ **Both daily RMSSD and complete time series stored**  
✅ **Tested with real Garmin data**  
✅ **Ready for API endpoint integration**

The foundation is in place for comprehensive HRV tracking and recovery monitoring in TrainingPlan.
