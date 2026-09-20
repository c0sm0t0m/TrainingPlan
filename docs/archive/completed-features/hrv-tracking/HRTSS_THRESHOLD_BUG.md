# hrTSS Threshold Bug - "Other" Sports Using MAX HR Instead of Threshold

**Date**: 2026-01-04  
**Status**: 🐛 BUG IDENTIFIED - Needs Fix  
**Impact**: ALL non-primary sports (tennis, skiing, strength, hiking, etc.)

---

## Problem Summary

Activities for "other" sports (not cycling/running/swimming) are using **MAX_HR** as the threshold for hrTSS calculation instead of the appropriate **threshold HR** (usually running threshold). This significantly **underestimates training stress** for these activities.

---

## Example: Tennis Activity (Dec 29, 2025)

### Activity Data
- **Activity**: Erlangen Tennis
- **Duration**: 91.6 minutes (5496 seconds elapsed)
- **Average HR**: 101 bpm
- **User Max HR**: 179 bpm
- **User Running Threshold HR**: 165 bpm

### Current Calculation (WRONG)
```python
threshold_hr = user.max_hr  # 179 bpm ❌ WRONG!
IF = 101 / 179 = 0.564
hrTSS = (91.6/60) × (0.564)² × 100 = 48.6 TSS
```

### Correct Calculation
```python
threshold_hr = user.running_threshold_hr  # 165 bpm ✅ CORRECT
IF = 101 / 165 = 0.612
hrTSS = (91.6/60) × (0.612)² × 100 = 57.2 TSS
```

### Impact
- **Current TSS**: 48.6  
- **Correct TSS**: 57.2  
- **Difference**: +8.6 TSS (+17.7%)

---

## Root Cause

### File: `/backend/recalculate_tss.py`

**Lines 64-72** (threshold selection logic):

```python
if 'cycl' in sport_key or 'bike' in sport_key:
    threshold_hr = user.cycling_threshold_hr
elif 'run' in sport_key:
    threshold_hr = user.running_threshold_hr
elif 'swim' in sport_key:
    threshold_hr = user.swim_threshold_hr
else:
    # ❌ BUG: For 'other' sports, uses max_hr instead of threshold
    threshold_hr = user.max_hr if user.max_hr else (user.running_threshold_hr or 165)
```

**Why this is wrong**:
1. **MAX HR is not a threshold** - it's the maximum heart rate capacity, not a sustainable intensity level
2. **Threshold HR** (~90-95% of max) represents lactate threshold - the intensity you can sustain for 1 hour
3. Using max_hr as the denominator makes the Intensity Factor (IF) artificially low
4. This underestimates TSS for all "other" sports by ~15-20%

---

## Correct Approach (from TrainingPeaks)

TrainingPeaks uses:
- **Cycling**: Cycling threshold HR
- **Running**: Running threshold HR
- **Swimming**: Swimming threshold HR (or running if not set)
- **Other**: **Running threshold HR** (default aerobic threshold)

**The running threshold HR is the appropriate default** because:
- It represents general aerobic fitness
- Most "other" sports are aerobic in nature (tennis, skiing, hiking)
- It's more accurate than using max_hr (which is just a ceiling)

---

## Fix Required

### Option 1: Use Running Threshold as Default (RECOMMENDED)

Change line 72 in `recalculate_tss.py`:

```python
# OLD (WRONG):
threshold_hr = user.max_hr if user.max_hr else (user.running_threshold_hr or 165)

# NEW (CORRECT):
threshold_hr = user.running_threshold_hr if user.running_threshold_hr else (user.max_hr * 0.9)
```

**Benefits**:
- ✅ Matches TrainingPeaks behavior
- ✅ More accurate TSS for all "other" sports
- ✅ Still has fallback (90% of max_hr) if no threshold set
- ✅ No breaking changes needed

### Option 2: Add Sport-Specific Thresholds (FUTURE ENHANCEMENT)

Add threshold HR settings for each sport category:
- `tennis_threshold_hr`
- `skiing_threshold_hr`
- `strength_threshold_hr`
- etc.

This would be more accurate but requires:
- Database schema changes
- UI changes for threshold settings
- More user configuration burden

---

## Affected Sports

All sports **not** in [cycling, running, swimming]:

- Tennis (tennis_v2, tennis_v8)
- Skiing (cross_country_skiing, downhill_skiing, skate_skiing)
- Strength training (strength_training, cardio_training)
- Hiking (hiking, mountaineering)
- Walking (walking, casual_walking)
- Other (elliptical, rowing, yoga, etc.)

### How Many Activities?

```sql
SELECT activity_type, COUNT(*) as count
FROM garmin_activities
WHERE activity_type NOT LIKE '%cycling%'
  AND activity_type NOT LIKE '%running%'
  AND activity_type NOT LIKE '%swimming%'
  AND calculated_tss IS NOT NULL
GROUP BY activity_type;
```

---

## Implementation Plan

### 1. Apply Fix to recalculate_tss.py

```bash
cd backend
# Edit line 72 in recalculate_tss.py
nano recalculate_tss.py
```

Change:
```python
threshold_hr = user.max_hr if user.max_hr else (user.running_threshold_hr or 165)
```

To:
```python
threshold_hr = user.running_threshold_hr if user.running_threshold_hr else (user.max_hr * 0.9)
```

### 2. Rerun Recalculation

```bash
source venv313/bin/activate
python3 recalculate_tss.py
```

**Expected impact**: All "other" sports TSS values will increase by ~15-20%

### 3. Restart Backend

```bash
../../stop-all.sh
../../start-all.sh
```

### 4. Verify

Check dashboard CTL/ATL/TSB metrics reflect updated TSS values.

---

## Verification

### Test Case: Tennis Dec 29, 2025

After fix:
```python
# Should calculate:
threshold_hr = 165  # running threshold
IF = 101 / 165 = 0.612
hrTSS = 1.527 × (0.612)² × 100 = 57.2 TSS

# Database should show:
calculated_tss = 57.2  # (instead of 48.6)
```

Query to verify:
```sql
SELECT activity_name, start_time_local, calculated_tss
FROM garmin_activities
WHERE activity_name = 'Erlangen Tennis'
  AND start_time_local LIKE '2025-12-29%';
```

---

## References

- TrainingPeaks TSS Documentation: https://www.trainingpeaks.com/learn/articles/normalized-power-intensity-factor-training-stress/
- hrTSS Formula: Duration(hours) × IF² × 100
- IF = Average HR / Threshold HR
- Threshold HR ≈ 90-95% of Max HR (lactate threshold)

---

## Notes

- This bug has existed since initial commit (76f356e)
- Affects ALL historical "other" sport activities
- Swimming bug (missing swim_threshold_pace) was fixed separately on Jan 3-4, 2026
- Tennis interval sport detection (using elapsed duration) is working correctly ✅

---

**Next Action**: Apply fix to line 72 and rerun recalculation.
