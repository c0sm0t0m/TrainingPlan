# Workout Sync Update Summary

## Changes Made

The workout sync functionality has been enhanced to **prevent duplicate workouts** from being uploaded to Garmin Connect.

## Key Features

✅ **Duplicate Detection**: Checks if a workout with the same title already exists in Garmin Connect before uploading

✅ **Efficient Batch Processing**: Fetches existing workouts once for multiple sync operations

✅ **Smart Reuse**: If a workout exists, it's scheduled to the calendar without re-uploading

✅ **Detailed Reporting**: Shows breakdown of newly created vs. reused workouts

## Files Modified

### Core Changes
1. **[garmin_service.py](src/services/garmin_service.py)**
   - Added `get_existing_workouts()` - fetches workouts from Garmin
   - Added `_workout_exists_in_garmin()` - checks for duplicate titles
   - Updated `upload_workout_to_garmin()` - now checks for duplicates and returns `(id, was_reused)`

2. **[garmin.py](src/api/routes/garmin.py)**
   - Updated `/sync-workouts` endpoint - fetches existing workouts and tracks reuse stats
   - Updated `/sync-workout/{workout_id}` endpoint - checks for duplicates before syncing

### Test Files Updated
All test files updated to handle the new tuple return from `upload_workout_to_garmin()`:
- `test_fe_sync_workouts.py`
- `test_workout_scheduling.py`
- `test_sync_training_plan.py`
- `test_garmin_workout_sync.py`
- `test_workout_sync.py`

### New Files
- **`test_duplicate_check.py`** - Unit tests for duplicate detection logic
- **`WORKOUT_DUPLICATE_PREVENTION.md`** - Detailed documentation

## API Response Changes

### Bulk Sync Response (Before)
```json
{
  "message": "Sync complete: 5 synced & scheduled, 1 skipped, 0 failed",
  "total_workouts": 6,
  "synced": 5,
  "scheduled": 5,
  "skipped": 1,
  "failed": 0
}
```

### Bulk Sync Response (After)
```json
{
  "message": "Sync complete: 3 new, 2 reused, 1 skipped, 0 failed",
  "total_workouts": 6,
  "synced": 5,
  "newly_created": 3,
  "reused": 2,
  "scheduled": 5,
  "skipped": 1,
  "failed": 0
}
```

### Single Workout Sync Response (New Fields)
```json
{
  "message": "Existing workout reused and scheduled",
  "workout_id": 123,
  "garmin_workout_id": "45678",
  "was_reused": true,  // ← NEW
  "synced_at": "2026-01-01T12:00:00"
}
```

## How to Test

1. **Run duplicate check tests:**
   ```bash
   cd backend
   source venv313/bin/activate
   python test_duplicate_check.py
   ```

2. **Test with real Garmin account:**
   - Sync some workouts to Garmin Connect
   - Sync the same workouts again
   - Check console output - should see "already exists in Garmin" messages
   - Verify in Garmin Connect that no duplicates were created

## Console Output Examples

**When a workout already exists:**
```
📋 Found 47 existing workouts in Garmin Connect
✅ Workout 'Easy Run 5k' already exists in Garmin (ID: 12345)
✅ Existing workout scheduled to calendar for 2026-01-15
```

**When a new workout is created:**
```
✅ Workout scheduled to calendar for 2026-01-15
```

## Matching Logic

Workouts are considered duplicates if their **titles match**:
- **Case-insensitive**: "Easy Run" = "easy run"
- **Whitespace trimmed**: "  Long Ride  " = "Long Ride"

## Notes

- The system fetches up to 200 existing workouts from Garmin for comparison
- Matching is based on workout title only (not duration, distance, or sport type)
- Existing workouts are still scheduled to the calendar on the requested date
- All scheduled workouts appear in your Garmin Connect calendar, whether new or reused

## Breaking Change

⚠️ **Important**: The `upload_workout_to_garmin()` method now returns a tuple:

```python
# Before
workout_id = await garmin_service.upload_workout_to_garmin(...)

# After
workout_id, was_reused = await garmin_service.upload_workout_to_garmin(...)
```

All existing code has been updated to handle this change.
