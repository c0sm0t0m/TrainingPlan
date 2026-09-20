# HRV Sync Troubleshooting Guide

## Issue: "Failed to sync health data" Error (365 days)

### Problem
When syncing large date ranges (365+ days), the frontend shows "Failed to sync health data" and no progress bar is visible.

### Root Causes
1. **Frontend HTTP Timeout**: 365-day sync takes 8-12 minutes, but HTTP request times out (usually 60-120 seconds)
2. **Progress Logs Location**: Progress is only shown in **backend terminal**, not frontend UI
3. **Generic Error Message**: Original error didn't provide details

## Solution (2025-01-05 Update)

### ✅ Improvements Made

1. **Detailed Error Logging** - Backend now logs:
   - Exact error type and message
   - Full stack trace for debugging
   - Days requested when error occurred
   - Specific error messages (timeout, auth, rate limit, etc.)

2. **Immediate Progress Visibility** - All logs now use `flush=True`:
   - Progress appears immediately in terminal
   - No buffering delays
   - Real-time progress tracking

3. **Timeout Warnings** - Backend warns when syncing >180 days:
   ```
   ⚠️  WARNING: Syncing 365 days may take 8-12 minutes.
      Frontend timeout may occur. Consider syncing in smaller batches.
      Recommended: Sync 180 days at a time, then increase.
   ```

4. **Specific Error Messages** - Frontend gets clear error messages:
   - "Sync timed out after 365 days. Try syncing 180 days at a time instead."
   - "Garmin authentication expired. Please reconnect your account."
   - "Garmin API rate limit reached. Please wait a few minutes and try again."
   - "Network connection error. Please check your internet and try again."

## How to Use (Recommended Approach)

### Option 1: Sync in Batches (Recommended)
**Best for avoiding timeouts**

1. **First sync**: 180 days
   ```bash
   # In frontend, set days to 180
   ```
   - Wait for success
   - Check backend terminal for progress

2. **Second sync**: 365 days (fills in missing 185 days)
   ```bash
   # In frontend, set days to 365
   ```
   - Database skips unchanged records
   - Only fetches new data

### Option 2: Watch Backend Terminal During Long Syncs
**For brave souls syncing 365 days**

1. **Before starting**: Open backend terminal
   ```bash
   cd backend
   ./start-backend.sh
   # OR: uvicorn src.main:app --reload
   ```

2. **Start sync in UI**: Set days to 365

3. **Watch terminal** for real-time progress:
   ```
   ⚠️  WARNING: Syncing 365 days may take 8-12 minutes.
      Frontend timeout may occur. Consider syncing in smaller batches.
   
   🏥 Starting health data sync for 365 days...
      Check this terminal for real-time progress updates.
   
   🔄 Starting HRV data sync for 365 days...
      Date range: 2025-01-05 to 2026-01-05
      Progress updates every 18 days
   
      📊 Progress: 18/365 days (5%) | ✅ 15 found | ⏭️  3 no data | ❌ 0 errors
      📊 Progress: 36/365 days (10%) | ✅ 31 found | ⏭️  5 no data | ❌ 0 errors
      ⏸️  Pausing briefly to avoid rate limits (processed 50/365)...
      📊 Progress: 54/365 days (15%) | ✅ 47 found | ⏭️  7 no data | ❌ 0 errors
      ...
   ```

4. **If frontend times out**:
   - Backend continues running!
   - Check terminal for completion
   - Refresh UI to see new data
   - Data is already stored in database

### Option 3: Use curl (Advanced)
**For users comfortable with command line**

```bash
# Get your JWT token first (from browser DevTools or login)
export JWT_TOKEN="your-jwt-token-here"

# Sync with curl (no frontend timeout)
curl -X POST "http://localhost:8000/api/v1/garmin/sync-health-data" \
  -H "Authorization: Bearer $JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"days": 365}' \
  --max-time 900  # 15 minute timeout
```

## Understanding the Error

### Backend Terminal Output (When Error Occurs)

**Before (old - generic error)**:
```
Error syncing HRV data: timeout
```

**After (new - detailed error)**:
```
❌ HRV SYNC ERROR:
   Days requested: 365
   Error type: TimeoutError
   Error message: Request timed out after 120 seconds
   Full traceback:
   Traceback (most recent call last):
     File "src/api/routes/garmin.py", line 1595, in sync_health_data
       hrv_records = await garmin_service.sync_hrv_data(...)
     ...
   TimeoutError: Request timed out after 120 seconds
```

### Frontend Error Messages

| Scenario | Error Message |
|----------|---------------|
| **HTTP Timeout** | "Sync timed out after 365 days. Try syncing 180 days at a time instead." |
| **Auth Expired** | "Garmin authentication expired. Please reconnect your account." |
| **Rate Limited** | "Garmin API rate limit reached. Please wait a few minutes and try again." |
| **Network Issue** | "Network connection error. Please check your internet and try again." |
| **Unknown** | "Failed to sync health data: [specific error]" |

## Debugging Checklist

If you see "Failed to sync health data":

1. **Check backend terminal** for detailed error:
   ```bash
   # Look for lines starting with ❌ HRV SYNC ERROR
   ```

2. **Check error type**:
   - `TimeoutError` → Use batched sync (180 days)
   - `AuthenticationError` → Reconnect Garmin account
   - `RateLimitError` → Wait 5-10 minutes
   - `ConnectionError` → Check internet/Garmin status

3. **Verify progress was shown**:
   ```
   🔄 Starting HRV data sync for 365 days...
   ```
   - If NO progress shown → Backend didn't receive request
   - If progress shown → Sync is working, just slow

4. **Check database** to see if partial data was stored:
   ```bash
   cd backend
   sqlite3 trainingplan.db "SELECT COUNT(*) FROM garmin_hrv;"
   ```

## Performance Expectations

| Days | Expected Time | Progress Updates | Rate Limiting |
|------|---------------|------------------|---------------|
| 30   | 15-30 sec     | Every 2 days     | None |
| 90   | 1-2 min       | Every 5 days     | None |
| 180  | 3-5 min       | Every 9 days     | 3 pauses |
| 365  | 8-12 min      | Every 18 days    | 7 pauses |

## Best Practices

✅ **DO**:
- Sync 180 days first, then expand to 365
- Keep backend terminal visible during long syncs
- Wait for rate limit cooldowns (automatic)
- Check terminal for detailed progress

❌ **DON'T**:
- Try to sync 365+ days on first attempt
- Close terminal during long syncs
- Retry immediately after rate limit error
- Expect frontend to show progress (it's backend-only)

## Future Improvements (Roadmap)

1. **Background Jobs**: Move long syncs to Celery tasks
2. **SSE/WebSocket**: Stream progress to frontend in real-time
3. **Resume Capability**: Save checkpoint, resume on failure
4. **Smart Incremental**: Only fetch days after last successful sync
5. **Progress API**: Frontend can poll for progress updates

## Quick Reference

**Recommended workflow for initial sync**:
```
Day 1: Sync 180 days → Wait for success
Day 1: Sync 365 days → Fills in remaining 185 days
Day 7: Sync 30 days  → Weekly updates
```

**If error occurs**:
1. Check backend terminal logs
2. Read specific error message
3. Follow recommendation (batch sync, reconnect, wait, etc.)
4. Restart backend if needed
5. Try again with smaller range

## Status

**Issue**: ✅ FIXED (Enhanced error reporting and logging)  
**Date**: 2025-01-05  
**Recommendation**: Use batched sync (180 days) for best experience
