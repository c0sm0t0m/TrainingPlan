# Weekly TSS Behavior Analysis

**Date**: 2026-01-06  
**Requirement**: "dashboard weekly tss shall display the tss of the current week."

---

## Current Behavior

### Implementation Location
- **Backend**: [`backend/src/utils/calculations/training_load.py`](backend/src/utils/calculations/training_load.py#L227)
- **Function**: `get_current_training_metrics()`
- **Frontend**: [`frontend/src/pages/Dashboard.tsx`](frontend/src/pages/Dashboard.tsx#L80-L88)

### Current Calculation

```python
# Calculate weekly TSS (last 7 days)
weekly_tss = sum(day['tss'] for day in metrics[-7:])
```

This takes the **last 7 entries** from the daily metrics array and sums their TSS values.

### What This Means

The current implementation calculates TSS from a **rolling 7-day window**:
- Takes the last 7 days up to and including today
- Example (if today is Monday, January 6, 2026):
  - **Last 7 days**: Tuesday, Dec 31 → Monday, Jan 6
  - **Includes**: Activities from previous week (Tue-Sun) + this week (Mon)

---

## Requirement Interpretation

### "Current Week" Definition

In fitness tracking and training platforms, "current week" typically means:
- **Calendar week boundaries**: Monday to Sunday (ISO 8601 standard)
- **Alternative**: Sunday to Saturday (US standard)

**NOT** a rolling 7-day window.

### Industry Standards

**TrainingPeaks**:
- Uses Monday-Sunday calendar weeks
- Weekly TSS metric shows TSS for the current calendar week
- Week boundaries are consistent and predictable

**Strava**:
- Uses Monday-Sunday calendar weeks
- "This Week" metric shows current week's activities

**Garmin Connect**:
- Uses Monday-Sunday calendar weeks
- Weekly summaries align with calendar weeks

---

## Discrepancy Analysis

### Example Scenario

**Today: Monday, January 6, 2026**

#### Current Implementation (Rolling 7 Days)
```
Last 7 Days: Tuesday, Dec 31 → Monday, Jan 6
├─ [✓] Tue, Dec 31 (previous week)
├─ [✓] Wed, Jan 01 (previous week)
├─ [✓] Thu, Jan 02 (previous week)
├─ [✓] Fri, Jan 03 (previous week)
├─ [✓] Sat, Jan 04 (previous week)
├─ [✓] Sun, Jan 05 (previous week)
└─ [✓] Mon, Jan 06 (current week) ← only 1 day from current week!
```

#### Expected Behavior (Calendar Week)
```
Current Week: Monday, Jan 6 → Sunday, Jan 12
├─ [ ] Mon, Jan 06 ← today
├─ [ ] Tue, Jan 07
├─ [ ] Wed, Jan 08
├─ [ ] Thu, Jan 09
├─ [ ] Fri, Jan 10
├─ [ ] Sat, Jan 11
└─ [ ] Sun, Jan 12
```

### Impact

On Monday morning:
- **Current behavior**: Shows TSS from 6 days of the previous week + 1 day of current week
- **Expected behavior**: Shows TSS from only the current day (Monday)
- **User confusion**: "Why does my weekly TSS already show 450 TSS on Monday morning?"

On Tuesday through Saturday:
- Rolling window includes more days from the previous week than the current week
- User sees inflated "weekly" TSS that includes old data

Only on **Sunday** do the two calculations align.

---

## User Experience Problems

1. **Confusing metrics on Monday**: Users expect weekly TSS to reset on Monday, but it shows carryover from the previous week.

2. **Inconsistent comparisons**: Users cannot compare "this week" vs "last week" because the windows overlap.

3. **Poor planning**: Athletes cannot see how much TSS they've accumulated in the current week for planning remaining workouts.

4. **Misleading progress**: A high "weekly TSS" on Monday doesn't reflect current week's training load.

---

## Recommendation

### Change Required

**Change from**: Rolling 7-day window  
**Change to**: Calendar week (Monday-Sunday)

### Benefits

✅ **Predictable**: Week boundaries are clear and consistent  
✅ **Intuitive**: Matches user mental model of "current week"  
✅ **Comparable**: Users can compare week-over-week progress  
✅ **Industry standard**: Aligns with TrainingPeaks, Strava, Garmin  
✅ **Better planning**: Users can see current week's load and plan accordingly

---

## Implementation Plan

### Backend Changes

Modify [`backend/src/utils/calculations/training_load.py`](backend/src/utils/calculations/training_load.py):

```python
async def get_current_training_metrics(
    db: AsyncSession,
    user_id: int,
    sport_type: Optional[str] = None
) -> Dict:
    """
    Get current training metrics (today's values).
    
    Returns:
        Dictionary with current ctl, atl, tsb, weekly_tss, trend
    """
    # Calculate last 50 days to get accurate current values
    metrics = await calculate_training_load_metrics(db, user_id, days=50, sport_type=sport_type)
    
    if not metrics:
        return {
            'ctl': 0,
            'atl': 0,
            'tsb': 0,
            'weekly_tss': 0,
            'trend': 'flat'
        }
    
    # Get today's metrics (last item)
    current = metrics[-1]
    
    # CHANGE: Calculate weekly TSS for current calendar week (Mon-Sun)
    from datetime import datetime, timedelta
    today = datetime.now().date()
    weekday = today.weekday()  # Monday=0, Sunday=6
    monday = today - timedelta(days=weekday)  # Start of current week
    
    # Filter metrics to only include current week
    weekly_tss = 0.0
    for day in metrics:
        day_date = datetime.fromisoformat(day['date']).date()
        if day_date >= monday and day_date <= today:
            weekly_tss += day['tss']
    
    # Determine trend by comparing to 7 days ago
    if len(metrics) >= 8:
        previous_ctl = metrics[-8]['ctl']
        trend = 'up' if current['ctl'] > previous_ctl else 'down' if current['ctl'] < previous_ctl else 'flat'
    else:
        trend = 'flat'
    
    return {
        'ctl': current['ctl'],
        'atl': current['atl'],
        'tsb': current['tsb'],
        'weekly_tss': round(weekly_tss, 1),  # Now uses calendar week
        'trend': trend
    }
```

### Testing Plan

1. **Test on Monday**: Verify weekly_tss only includes Monday's activities
2. **Test mid-week**: Verify weekly_tss includes Mon-Wed (if today is Wed)
3. **Test on Sunday**: Verify weekly_tss includes full Mon-Sun week
4. **Compare**: Check that values differ from rolling 7-day calculation

---

## Conclusion

**Current State**: ❌ Dashboard shows TSS from a rolling 7-day window  
**Requirement**: ✅ Dashboard should show TSS from the current calendar week (Monday-Sunday)  
**Action**: Change calculation to use calendar week boundaries instead of rolling window

**Priority**: Medium - Affects user understanding but doesn't break functionality  
**Effort**: Low - Simple calculation change, ~15 lines of code  
**Risk**: Low - Clear requirement, well-defined behavior

