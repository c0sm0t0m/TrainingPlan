# Weekly TSS Fix - Implementation Summary

**Date**: 2026-01-06  
**Status**: ✅ **IMPLEMENTED & TESTED**

---

## Problem

Dashboard "Weekly TSS" metric was showing TSS from a **rolling 7-day window** instead of the **current calendar week** (Monday-Sunday).

### Before (Incorrect)
- On Tuesday, January 6, 2026:
  - Showed: **611.8 TSS** (from Dec 31 - Jan 6, including 5 days from previous week)
  - Expected: **185.6 TSS** (from Mon Jan 5 - Tue Jan 6, only current week)

---

## Solution

Changed the calculation in [`backend/src/utils/calculations/training_load.py`](backend/src/utils/calculations/training_load.py) to use **calendar week boundaries**.

### Implementation

```python
# Calculate weekly TSS for current calendar week (Monday-Sunday)
today = datetime.now().date()
weekday = today.weekday()  # Monday=0, Sunday=6
monday = today - timedelta(days=weekday)  # Start of current week

# Sum TSS only from days in current week (Monday to today)
weekly_tss = 0.0
for day in metrics:
    day_date = datetime.fromisoformat(day['date']).date()
    if day_date >= monday and day_date <= today:
        weekly_tss += day['tss']
```

### Key Changes

1. ✅ Calculate Monday of current week: `today - timedelta(days=weekday)`
2. ✅ Sum TSS only from days >= Monday and <= today
3. ✅ Properly resets at the start of each week

---

## Test Results

```
WEEKLY TSS FIX VERIFICATION
======================================================================

📅 Today: Tuesday, January 06, 2026
📅 Current Week: Mon, Jan 05 to Sun, Jan 11

📊 Fixed Metrics:
   Weekly TSS: 185.6
   CTL: 68.6
   ATL: 81.3
   TSB: -12.7

🔍 Verification:
   Days in current week:
   ✓ Mon, Jan 05: 108.7 TSS
   ✓ Tue, Jan 06: 76.9 TSS

   Manual calculation: 185.6 TSS
   API returned: 185.6 TSS

✅ SUCCESS: Values match!

📊 Comparison with old method (rolling 7 days):
   Old (rolling 7 days): 611.8 TSS
   New (current week):   185.6 TSS
   Difference: -426.2 TSS

✅ Calculation changed as expected!
```

---

## Impact

### User Experience Improvements

✅ **Monday clarity**: Weekly TSS now correctly resets on Monday  
✅ **Intuitive values**: Metric matches user expectation of "current week"  
✅ **Week-over-week comparison**: Users can now compare weeks consistently  
✅ **Better planning**: Users see current week's load for planning remaining workouts  
✅ **Industry standard**: Aligns with TrainingPeaks, Strava, and Garmin Connect

### Breaking Changes

⚠️ **Values will differ**: Users will see different "Weekly TSS" values after update
- On Monday-Saturday: Values will be LOWER (only current week)
- On Sunday: Values will be similar (both methods align)

### Communication

Users should be informed:
- "Weekly TSS now shows the current calendar week (Monday-Sunday) instead of the last 7 days"
- "This provides a clearer view of your training load for the week"

---

## Files Modified

1. [`backend/src/utils/calculations/training_load.py`](backend/src/utils/calculations/training_load.py)
   - Modified: `get_current_training_metrics()` function
   - Lines changed: ~10 lines
   - Change type: Logic update (rolling window → calendar week)

---

## Deployment Status

✅ **Code deployed**: Backend restarted with fix  
✅ **Tests passing**: Verified with test script  
✅ **No breaking changes**: API contract unchanged  
✅ **Documentation**: Analysis and fix documented

---

## Related Documents

- [WEEKLY_TSS_BEHAVIOR_ANALYSIS.md](WEEKLY_TSS_BEHAVIOR_ANALYSIS.md) - Detailed problem analysis
- [backend/src/utils/calculations/training_load.py](backend/src/utils/calculations/training_load.py) - Implementation

---

## Conclusion

**Requirement**: "dashboard weekly tss shall display the tss of the current week."

✅ **Status**: SATISFIED

The dashboard now correctly displays TSS for the current calendar week (Monday-Sunday), not a rolling 7-day window.
