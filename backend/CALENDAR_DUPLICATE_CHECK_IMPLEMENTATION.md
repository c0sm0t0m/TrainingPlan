# Duplicate Check Implementation - Calendar-Based Approach

**Date**: 2026-01-01  
**Status**: ✅ Implemented

## Summary

Changed the duplicate detection strategy from local database tracking to **querying Garmin Connect calendar** for each scheduled workout date. This ensures accurate duplicate prevention even when workouts are manually added/deleted in Garmin Connect.

## Changes Made

### 1. Service Layer (`garmin_service.py`)

#### New Method: `get_scheduled_workouts_for_date()`
```python
async def get_scheduled_workouts_for_date(
    oauth1_token: str,
    oauth2_token: str,
    date_str: str
) -> List[Dict]
```

- Queries `/calendar-service/calendar/{date}` endpoint
- Returns list of workouts scheduled on that specific date
- Used for duplicate detection before upload

#### Updated Method: `upload_workout_to_garmin()`

**Old Signature:**
```python
async def upload_workout_to_garmin(
    oauth1_token: str,
    oauth2_token: str,
    workout_json: Dict,
    scheduled_date: Optional[str] = None,
    local_workout_id: Optional[int] = None,
    existing_garmin_workout_id: Optional[str] = None
) -> tuple[str, bool]
```

**New Signature:**
```python
async def upload_workout_to_garmin(
    oauth1_token: str,
    oauth2_token: str,
    workout_json: Dict,
    workout_title: str,
    scheduled_date: Optional[str] = None
) -> tuple[str, bool]
```

**Changes:**
- ✅ Added: `workout_title` parameter (required for duplicate check)
- ❌ Removed: `local_workout_id` (no longer needed)
- ❌ Removed: `existing_garmin_workout_id` (no longer needed)

**New Behavior:**
1. If `scheduled_date` is provided, query Garmin calendar for that date
2. Compare workout titles (case-insensitive, whitespace-trimmed)
3. If matching workout found, return existing ID without uploading
4. If no match, upload new workout and schedule it

### 2. API Routes (`api/routes/garmin.py`)

#### Updated: `/sync-workouts` (Bulk Sync)
```python
# Old call
result = await garmin_service.upload_workout_to_garmin(
    oauth1_token=current_user.garmin_oauth1_token,
    oauth2_token=current_user.garmin_oauth2_token,
    workout_json=garmin_workout,
    scheduled_date=scheduled_date,
    local_workout_id=workout.id,
    existing_garmin_workout_id=workout.garmin_workout_id
)

# New call
result = await garmin_service.upload_workout_to_garmin(
    oauth1_token=current_user.garmin_oauth1_token,
    oauth2_token=current_user.garmin_oauth2_token,
    workout_json=garmin_workout,
    workout_title=workout.title,
    scheduled_date=scheduled_date
)
```

#### Updated: `/sync-workout/{workout_id}` (Single Sync)
- Same changes as bulk sync
- Updated response message: "Workout already exists on this date, skipped"

### 3. Documentation

#### Updated: `WORKOUT_DUPLICATE_PREVENTION.md`
- Comprehensive documentation of calendar-based approach
- Benefits and trade-offs comparison
- Usage examples and edge cases
- Performance considerations

### 4. Tests

#### New: `test_calendar_duplicate_check.py`
Comprehensive test script that:
1. Queries calendar for existing workouts
2. Uploads test workout (should create new)
3. Attempts duplicate upload (should detect existing)
4. Uploads same title to different date (should create new)

## How It Works

### Duplicate Detection Flow

```
┌─────────────────────────────────────┐
│ User triggers workout sync          │
└──────────────┬──────────────────────┘
               │
               ▼
┌─────────────────────────────────────┐
│ For each workout:                   │
│ - Get scheduled date                │
│ - Get workout title                 │
└──────────────┬──────────────────────┘
               │
               ▼
┌─────────────────────────────────────┐
│ Query Garmin calendar for that date │
│ GET /calendar-service/calendar/DATE │
└──────────────┬──────────────────────┘
               │
               ▼
┌─────────────────────────────────────┐
│ Check if any workout matches title  │
│ (case-insensitive, trimmed)         │
└──────────────┬──────────────────────┘
               │
       ┌───────┴───────┐
       ▼               ▼
┌─────────────┐ ┌─────────────┐
│ Match Found │ │  No Match   │
│ (Duplicate) │ │   (New)     │
└──────┬──────┘ └──────┬──────┘
       │               │
       ▼               ▼
┌─────────────┐ ┌─────────────┐
│ Skip upload │ │ Upload &    │
│ Return ID   │ │ Schedule    │
└─────────────┘ └─────────────┘
```

### Example Scenarios

#### Scenario 1: First-time sync
```
Action: Sync training plan for next 14 days
Result: 10 workouts uploaded to Garmin calendar
Status: All new workouts created
```

#### Scenario 2: Re-sync (no changes)
```
Action: Sync same training plan again
Result: 0 new uploads, 10 duplicates detected
Status: All workouts already exist on their dates
```

#### Scenario 3: Manual edit in Garmin
```
Action: User manually adds "Morning Run" on Jan 5 in Garmin
Action: Sync training plan with "Morning Run" on Jan 5
Result: Duplicate detected, skip upload
Status: No duplicate created
```

#### Scenario 4: Same workout, different dates
```
Action: Sync plan with "Easy Run 5k" on Jan 1, 3, 5, 7
Result: 4 workouts created (one for each date)
Status: Same title is OK on different dates
```

## Benefits

### ✅ Advantages

1. **Always Accurate**: Queries actual Garmin state, not local database
2. **Handles Manual Edits**: Works even if user edits workouts in Garmin Connect
3. **Robust**: Prevents duplicates even if local DB is cleared/reset
4. **Date-Specific**: Allows same workout title on different dates
5. **Self-Healing**: Automatically syncs with Garmin's current state

### ⚠️ Trade-offs

1. **More API Calls**: One calendar query per workout (instead of one batch query)
2. **Slightly Slower**: Each workout needs separate calendar check
3. **Rate Limits**: More calls count toward Garmin's rate limits

### 📊 Performance Impact

**For typical 14-day sync with 10 workouts:**
- Old approach: ~3 API calls total (fetch library + uploads)
- New approach: ~10-20 API calls (calendar checks + uploads)
- Time difference: Negligible (~1-2 seconds)
- Rate limit impact: Well within limits (100 req/15min)

## Testing

### Run Test Script

```bash
cd backend
python test_calendar_duplicate_check.py
```

**Expected Output:**
```
✅ Test 1 - First upload: Creates new workout
✅ Test 2 - Duplicate detection: Detects existing workout
✅ Test 3 - Different date: Creates new workout (same title, different date)
```

### Manual Testing Steps

1. **Clear Garmin calendar** (manually delete test workouts if any)
2. **Sync training plan** (14 days)
3. **Check Garmin Connect**: Verify workouts appear
4. **Re-sync same plan**: Should detect all duplicates
5. **Edit workout in Garmin**: Change a workout title
6. **Sync again**: Should respect the edit

## Migration Notes

### Breaking Changes

**API Method Signatures Changed:**
- `upload_workout_to_garmin()` signature changed
- Removed: `local_workout_id`, `existing_garmin_workout_id`
- Added: `workout_title` (required)

**Code Using Old Signature Must Update:**
```python
# OLD - Will fail
result = await garmin_service.upload_workout_to_garmin(
    oauth1_token, oauth2_token, workout_json,
    scheduled_date=date_str,
    local_workout_id=123,
    existing_garmin_workout_id="456"
)

# NEW - Correct
result = await garmin_service.upload_workout_to_garmin(
    oauth1_token, oauth2_token, workout_json,
    workout_title="Easy Run 5k",
    scheduled_date=date_str
)
```

### Database Fields (No Changes Required)

The following fields are **still used** for tracking:
- `garmin_workout_id`: Stored after upload
- `garmin_synced_at`: Updated on sync
- `garmin_sync_status`: Tracks success/failure

These fields are no longer used for duplicate detection but remain useful for:
- Tracking sync history
- Debugging sync issues
- Manual workout deletion

### Backward Compatibility

⚠️ **Not backward compatible** with code calling old method signature.

All callers must update to new signature.

## Future Enhancements

### Potential Improvements

1. **Batch Calendar Queries**: Query multiple dates in parallel
2. **Caching**: Cache calendar results for X minutes
3. **Smart Sync**: Only check dates that changed
4. **Fuzzy Matching**: Match similar titles (e.g., "5k run" vs "5K Run")
5. **Description Check**: Include workout description in duplicate logic

### Monitoring

Consider adding metrics:
- Number of duplicates detected per sync
- Calendar query performance
- API rate limit usage

## Rollback Plan

If issues arise, rollback by:

1. Revert `garmin_service.py` changes
2. Revert `api/routes/garmin.py` changes
3. Test with old signature
4. Restore previous documentation

Rollback time: ~5 minutes

## Related Files

- [garmin_service.py](src/services/garmin_service.py)
- [garmin.py routes](src/api/routes/garmin.py)
- [WORKOUT_DUPLICATE_PREVENTION.md](WORKOUT_DUPLICATE_PREVENTION.md)
- [test_calendar_duplicate_check.py](test_calendar_duplicate_check.py)

## Conclusion

The calendar-based duplicate detection provides more reliable duplicate prevention by querying Garmin Connect's actual state. While it requires slightly more API calls, the benefits of accuracy and robustness outweigh the performance trade-off for typical usage patterns.

---

**Implementation Status**: ✅ Complete  
**Testing Status**: ⏳ Pending user verification  
**Documentation**: ✅ Complete
