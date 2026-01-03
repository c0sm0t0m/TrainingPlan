# Calendar-Based Duplicate Detection Test

## Overview

This test validates that the backend API correctly prevents duplicate workouts when syncing with Garmin Connect by checking the Garmin calendar before uploading.

## Test Procedure

For user `tboettger@gmail.com`:

1. **Retrieve Calendar**: Get upcoming workouts from database
2. **Check Garmin**: For each workout, check if it already exists in Garmin calendar
3. **Sync via API**: Use backend API to sync workouts with Garmin
4. **Verify Upload**: Only workouts that DON'T exist should be uploaded
5. **Test Duplicates**: Sync again to verify duplicate detection

## Running the Test

### Option 1: Using the script

```bash
cd backend
./run_duplicate_test.sh
```

### Option 2: Manual steps

**Terminal 1 - Start Backend:**
```bash
cd backend
source venv313/bin/activate
uvicorn src.main:app --reload
```

**Terminal 2 - Run Test:**
```bash
cd backend
source venv313/bin/activate
python test_calendar_duplicate_check.py
```

## What the Test Does

### Test 1-3: Service Layer Tests
- Direct testing of `garmin_service` methods
- Upload test workout to specific dates
- Verify duplicate detection on same date
- Verify same title allowed on different dates

### Test 4: Full API Flow (Main Test)

#### Step 1: Retrieve Database Calendar
```
✅ Found 3 workouts in database:
   - 2026-01-02: Test Sync Workout 1 (Status: pending)
   - 2026-01-03: Test Sync Workout 2 (Status: pending)
   - 2026-01-04: Test Sync Workout 3 (Status: pending)
```

#### Step 2: Check Garmin Calendar (Before Sync)
```
🔍 Checking Garmin calendar (before sync)...
   ❌ Test Sync Workout 1 NOT in Garmin on 2026-01-02
   ✅ Test Sync Workout 2 EXISTS in Garmin on 2026-01-03 (ID: 123456)
   ❌ Test Sync Workout 3 NOT in Garmin on 2026-01-04
```

#### Step 3: Sync via API
```
📤 Syncing via API...
✅ Sync complete:
   Newly created: 2 (Workout 1 and 3)
   Reused: 1 (Workout 2 already existed)
```

#### Step 4: Verify Garmin Calendar (After Sync)
```
🔍 Verifying Garmin calendar (after sync)...
   ✅ Test Sync Workout 1: Newly created (ID: 789012)
   ✅ Test Sync Workout 2: Existing workout preserved (ID: 123456)
   ✅ Test Sync Workout 3: Newly created (ID: 345678)
```

#### Step 5: Test Duplicate Detection
```
📤 Second sync (should detect all as duplicates)...
✅ Second sync results:
   Newly created: 0 (should be 0)
   Reused: 3 (should be 3)

✅✅✅ DUPLICATE DETECTION WORKING CORRECTLY!
```

## Expected Results

### First Sync
- **New workouts**: Uploaded to Garmin
- **Existing workouts**: Skipped (reused)
- **Database**: All workouts marked as `synced`

### Second Sync
- **All workouts**: Detected as duplicates
- **Newly created**: 0
- **Reused**: All workouts

### Modified Workout
- If you change a workout title, it will be treated as new
- New workout uploaded with new title
- Old workout remains in Garmin

## How It Works

The test validates the implementation in `garmin_service.py`:

```python
async def upload_workout_to_garmin(
    oauth1_token, oauth2_token, 
    workout_json, workout_title, 
    scheduled_date
):
    # 1. Query Garmin calendar for the scheduled date
    scheduled = await get_scheduled_workouts_for_date(
        oauth1_token, oauth2_token, scheduled_date
    )
    
    # 2. Check if workout with same title exists
    for workout in scheduled:
        if workout['workoutName'].lower() == workout_title.lower():
            # Duplicate found, return existing ID
            return (workout['workoutId'], True)
    
    # 3. No duplicate, upload new workout
    garmin_id = upload_to_garmin(workout_json)
    schedule_to_calendar(garmin_id, scheduled_date)
    return (garmin_id, False)
```

## Troubleshooting

### Test Fails: Server not running
**Error**: `Backend server not running, skipping API tests`

**Solution**:
```bash
cd backend
source venv313/bin/activate
uvicorn src.main:app --reload
```

### Test Fails: User not found
**Error**: `User not found or Garmin not connected`

**Solution**: Make sure user `tboettger@gmail.com` exists and is connected to Garmin

### Test Fails: Calendar endpoint 404
**Issue**: Calendar query returns 404

**Current Status**: Using `/trainingcalendar-service/calendar` endpoint with date range parameters. The original `/calendar-service/calendar/{date}` endpoint returned 404.

### Duplicate Detection Not Working
**Issue**: Second sync creates new workouts instead of detecting duplicates

**Check**:
1. Calendar query is working (step 2 should show existing workouts)
2. Title matching is case-insensitive and whitespace-trimmed
3. Garmin API responses are being parsed correctly

## Files Modified

- `src/services/garmin_service.py`: Added `get_scheduled_workouts_for_date()` method
- `src/api/routes/garmin.py`: Updated sync endpoints to use new duplicate check
- `test_calendar_duplicate_check.py`: Comprehensive test suite
- `run_duplicate_test.sh`: Helper script to run the test

## Success Criteria

✅ Service layer tests pass (Tests 1-3)
✅ API can retrieve workouts from database
✅ API checks Garmin calendar before syncing
✅ Existing workouts are not re-uploaded
✅ New workouts are uploaded successfully
✅ Second sync detects all workouts as duplicates
✅ Newly created count is 0 on second sync

## Next Steps

Once the test passes:
1. Test with real user workouts (not just test data)
2. Test with different sport types
3. Test with workouts that have special characters in titles
4. Monitor Garmin API rate limits during bulk syncs
