# Workout Sync Duplicate Prevention

## Overview
The workout sync functionality prevents duplicate workouts from being uploaded to Garmin Connect by **checking the Garmin calendar** for each scheduled date. Before uploading, the system queries Garmin Connect to see if a workout with the same title already exists on the scheduled date.

## How It Works

### Date-Based Duplicate Check Strategy

For each scheduled workout:
1. **Query Garmin Calendar**: Check the specific date in Garmin Connect calendar
2. **Compare Workout Titles**: Match workout titles (case-insensitive, whitespace-trimmed)
3. **Skip if Exists**: If a workout with the same title exists on that date, skip upload
4. **Upload if New**: If no matching workout found, upload and schedule the workout

This approach ensures:
- ✅ No duplicate workouts on the same date
- ✅ Always uses the latest state from Garmin Connect
- ✅ Works even if local database is out of sync
- ✅ Handles manual edits in Garmin Connect

## Key Methods in `GarminService`

### `get_scheduled_workouts_for_date()`
Queries Garmin Connect calendar for a specific date.

```python
async def get_scheduled_workouts_for_date(
    oauth1_token: str,
    oauth2_token: str,
    date_str: str
) -> List[Dict]
```

- Queries `/calendar-service/calendar/{date}` endpoint
- Returns list of workouts scheduled on that date
- Each workout includes `workoutId`, `workoutName`, and `date`

### `upload_workout_to_garmin()`
Uploads workout with automatic duplicate detection.

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

**Parameters:**
- `workout_title`: Title to check for duplicates (required)
- `scheduled_date`: Date in YYYY-MM-DD format (optional)

**Returns:**
- `workout_id`: The Garmin workout ID
- `was_duplicate`: `True` if found existing workout, `False` if newly uploaded

**Behavior:**
1. If `scheduled_date` provided, query calendar for that date
2. Compare workout titles (case-insensitive)
3. If match found, return existing workout ID without uploading
4. If no match, upload new workout and schedule it

## Updated Sync Endpoints

### Bulk Sync (`/sync-workouts`)
- Processes upcoming workouts within specified date range
- Checks Garmin calendar for each workout's scheduled date
- Tracks duplicate vs. newly created workouts
- Reports detailed statistics

**Response Example:**
```json
{
  "message": "Sync complete: 3 new, 2 duplicates, 1 skipped, 0 failed",
  "total_workouts": 6,
  "synced": 5,
  "newly_created": 3,
  "reused": 2,
  "scheduled": 5,
  "skipped": 1,
  "failed": 0
}
```

### Single Workout Sync (`/sync-workout/{workout_id}`)
- Checks Garmin calendar before syncing
- Returns whether workout was duplicate or newly created

**Response Example:**
```json
{
  "message": "Workout already exists on this date, skipped",
  "workout_id": 123,
  "garmin_workout_id": "45678",
  "was_reused": true,
  "synced_at": "2026-01-01T12:00:00"
}
```

## Benefits of Calendar-Based Approach

### Advantages
✅ **Always Accurate**: Checks actual Garmin state, not local database  
✅ **Handles Manual Edits**: Works if user manually added/deleted workouts in Garmin  
✅ **Robust**: Prevents duplicates even if local database is cleared  
✅ **Date-Specific**: Allows same workout title on different dates  

### Comparison with Previous Approach

| Aspect | Old (Local Tracking) | New (Calendar Check) |
|--------|---------------------|----------------------|
| Duplicate Detection | Checks local DB field | Queries Garmin calendar |
| Manual Edits | May cause issues | Handles gracefully |
| Database Reset | Loses sync state | No impact |
| Same Workout on Different Dates | ❌ Would dedupe incorrectly | ✅ Allows correctly |
| API Calls | Fewer | More (1 per workout) |

## Usage Examples

### Example 1: Sync Training Plan
```python
# Workouts to sync
workouts = [
    {"title": "Easy Run 5k", "date": "2026-01-02"},
    {"title": "Interval Training", "date": "2026-01-03"},
    {"title": "Easy Run 5k", "date": "2026-01-04"},  # Same title, different date - OK
]

# Each workout will:
# 1. Query Garmin calendar for its specific date
# 2. Check if "Easy Run 5k" exists on that date
# 3. Upload only if not found
```

### Example 2: Re-sync After Manual Edit
```python
# User manually added "Morning Run" on 2026-01-05 in Garmin Connect
# Later, sync training plan that includes "Morning Run" on 2026-01-05

# Result: System detects existing workout, skips upload
# No duplicate created
```

## Technical Details

### Calendar API Endpoint
```
GET /calendar-service/calendar/{YYYY-MM-DD}
```

**Response Structure:**
```json
{
  "calendarItems": [
    {
      "itemType": "workout",
      "workoutId": "12345",
      "workoutName": "Easy Run 5k",
      "date": "2026-01-02"
    }
  ]
}
```

### Title Matching Logic
```python
workout_title_normalized = workout_title.strip().lower()
scheduled_title = scheduled_workout.get('workoutName', '').strip().lower()

if scheduled_title == workout_title_normalized:
    # Duplicate detected
    return (existing_workout_id, True)
```

## Performance Considerations

### API Call Volume
- **Previous**: 1 call per batch (fetch workout library)
- **Current**: 1 call per workout (query calendar date)

For 14-day sync with 10 workouts: ~10 additional API calls

### Rate Limiting
Garmin Connect has rate limits (~100 requests per 15 minutes). For typical usage (syncing 10-20 workouts), this is well within limits.

### Optimization Tips
- Use appropriate `days_ahead` parameter (default: 14 days)
- Avoid frequent re-syncs (once per day is sufficient)
- Local database still tracks sync status to skip unchanged workouts

## Error Handling

### Calendar Query Failure
If calendar query fails (network issue, API error):
- Returns empty list
- Workout proceeds to upload
- Logs error for debugging

### Title Mismatch Edge Cases
- Whitespace differences: Handled by `.strip()`
- Case differences: Handled by `.lower()`
- Special characters: Exact match required
- Different descriptions: Only title is compared

## Migration Notes

### Removed Parameters
The following parameters were removed from `upload_workout_to_garmin()`:
- `local_workout_id`: No longer needed
- `existing_garmin_workout_id`: No longer needed

### Added Parameters
- `workout_title` (required): Used for duplicate detection

### Database Fields Still Used
- `garmin_workout_id`: Stored for reference
- `garmin_synced_at`: Tracks last sync time
- `garmin_sync_status`: Tracks sync state

These fields are still updated but no longer used for duplicate detection.

## Conclusion

The calendar-based duplicate prevention provides a more robust and accurate solution by querying the actual state of Garmin Connect rather than relying on local database tracking. While it requires more API calls, the improved reliability and handling of edge cases make it the preferred approach.


## Benefits

1. **Prevents Duplicates**: No more duplicate workouts cluttering your Garmin library
2. **Efficient**: Fetches existing workouts once for batch operations
3. **Smart Scheduling**: Reuses existing workouts and just schedules them to the calendar
4. **Better Feedback**: Clear reporting of what was created vs. reused
5. **Robust Matching**: Case-insensitive and whitespace-tolerant matching

## How It Works

### Workflow

1. **Pre-fetch existing workouts** (once for batch sync)
   ```
   GET existing workouts from Garmin Connect (up to 200)
   ```

2. **For each workout to sync:**
   - Check if workout title exists in fetched workouts
   - If **exists**: 
     - Use existing workout ID
     - Schedule to calendar if date provided
     - Mark as "reused"
   - If **does not exist**:
     - Upload new workout to Garmin
     - Schedule to calendar if date provided
     - Mark as "newly created"

3. **Return statistics** showing breakdown of actions taken

### Matching Logic

Workouts are considered duplicates if:
- Titles match (case-insensitive)
- Whitespace is trimmed and normalized

Example matches:
- "Easy Run 5k" == "easy run 5k" ✅
- "  Long Ride  " == "Long Ride" ✅
- "Sprint Intervals" != "Intervals" ❌

## Testing

A test suite has been created in `test_duplicate_check.py` to verify:
- Exact title matching
- Case-insensitive matching
- Whitespace handling
- Non-matching scenarios

Run tests with:
```bash
cd backend
source venv313/bin/activate
python test_duplicate_check.py
```

## Migration Notes

### Breaking Changes

The `upload_workout_to_garmin()` method now returns a tuple instead of a single value:

**Before:**
```python
workout_id = await garmin_service.upload_workout_to_garmin(...)
```

**After:**
```python
workout_id, was_reused = await garmin_service.upload_workout_to_garmin(...)
```

All test files have been updated to handle the new return format.

## Future Enhancements

Potential improvements:
1. **Fuzzy matching**: Match similar titles (e.g., "5k Run" vs "Run 5k")
2. **Sport type filtering**: Only check duplicates within the same sport
3. **Date-based deduplication**: Consider scheduled date in duplicate detection
4. **Configurable limit**: Allow users to configure how many workouts to check
5. **Cache optimization**: Cache fetched workouts for a session

## Console Output Examples

### New Workout Created
```
✅ Workout scheduled to calendar for 2026-01-15
```

### Existing Workout Reused
```
✅ Workout 'Easy Run 5k' already exists in Garmin (ID: 12345)
✅ Existing workout scheduled to calendar for 2026-01-15
```

### Bulk Sync Summary
```
📋 Found 47 existing workouts in Garmin Connect
✅ Workout 'Morning Run' already exists in Garmin (ID: 23456)
✅ Existing workout scheduled to calendar for 2026-01-02
...
Sync complete: 3 new, 2 reused, 1 skipped, 0 failed
```
