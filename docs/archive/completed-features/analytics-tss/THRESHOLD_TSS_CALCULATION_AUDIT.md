# Threshold & TSS Calculation Chain Audit

**Date**: 2026-01-02  
**Auditor**: Code Review Agent  
**Status**: ⚠️ **CRITICAL ISSUE FOUND** - Thresholds NOT properly used in TSS calculations

---

## Executive Summary

### 🔴 Critical Finding
**TSS calculations are NOT using user thresholds correctly**. The `calculate_tss_from_activity()` function uses `max_hr` as `threshold_hr`, which is **incorrect**. This results in inflated TSS values and broken training load metrics.

### Impact
- All TSS calculations for HR-based activities are wrong
- CTL/ATL/TSB metrics are unreliable
- Dashboard displays incorrect fitness/fatigue/form values
- Users cannot trust training load recommendations

---

## Detailed Analysis

### 1. TSS Calculation Chain

#### Path 1: Activity Sync → TSS Calculation
```
Settings UI → Backend User Model → Activity Sync → TSS Calculator → Database → Dashboard
```

**Settings UI** (`frontend/src/pages/SettingsNew.tsx`):
- User enters: FTP, threshold pace, max HR, resting HR, threshold HR (cycling/running)
- Saved to backend via: `POST /api/v1/auth/update-thresholds`

**Backend User Model** (`backend/src/models/user.py`):
- Stores thresholds:
  - `ftp`: Functional Threshold Power (watts)
  - `threshold_pace`: Running threshold pace (seconds/km)
  - `max_hr`: Maximum heart rate (bpm)
  - `resting_hr`: Resting heart rate (bpm)
  - `cycling_threshold_hr`: Cycling lactate threshold HR (bpm)
  - `running_threshold_hr`: Running lactate threshold HR (bpm)
  - `swim_threshold_hr`: Swimming threshold HR (bpm)
  - `swim_threshold_pace`: Swimming threshold pace (seconds/100m)

**Activity Sync** (`backend/src/api/routes/garmin.py` line 319-328):
```python
# Get user thresholds from user settings
user_settings = {
    "ftp": current_user.ftp,
    "threshold_pace": current_user.threshold_pace,
    "max_hr": current_user.max_hr,           # ⚠️ WRONG - should be threshold_hr
    "resting_hr": current_user.resting_hr,
}
calculated_tss = calculate_tss_from_activity(activity, user_settings)
activity_data["calculated_tss"] = calculated_tss
```

**TSS Calculator** (`backend/src/utils/calculations/tss_calculator.py` line 252-293):
```python
def calculate_tss_from_activity(activity: dict, user_settings: dict) -> float:
    # Extract thresholds
    threshold_power = user_settings.get("ftp")
    threshold_hr = user_settings.get("max_hr", 180)  # ⚠️ WRONG - uses max_hr as threshold_hr!
    
    return calculate_activity_tss(
        sport_type=sport_type,
        duration_minutes=duration_minutes,
        average_hr=average_hr,
        threshold_hr=threshold_hr,  # ⚠️ This is actually max_hr, not threshold_hr!
        distance_meters=distance_meters,
        average_speed_mps=average_speed_mps,
        normalized_power=normalized_power,
        threshold_power=threshold_power,
        training_load=training_load
    )
```

**Running TSS Calculation** (`tss_calculator.py` line 16-47):
```python
def calculate_running_tss(
    duration_minutes: int,
    average_hr: Optional[int] = None,
    threshold_hr: int = 180,  # ⚠️ Receives max_hr, not actual threshold_hr!
    average_pace_min_per_km: Optional[float] = None,
    threshold_pace_min_per_km: float = 4.0,
) -> float:
    if average_hr and threshold_hr:
        # HR-based rTSS: TSS = (duration_hours * intensity_factor^2 * 100)
        intensity_factor = average_hr / threshold_hr  # ⚠️ WRONG FORMULA!
        # If average_hr = 150, max_hr = 180, this gives IF = 0.83 (too low)
        # Should be: average_hr = 150, threshold_hr = 165, IF = 0.91 (correct)
        duration_hours = duration_minutes / 60
        return duration_hours * (intensity_factor ** 2) * 100
```

**Example Impact**:
- Activity: 60 min run at 150 bpm average HR
- User: max_hr = 180, threshold_hr = 165
- **Current (WRONG)**: IF = 150/180 = 0.83 → TSS = 1.0 * 0.83² * 100 = **69 TSS**
- **Correct**: IF = 150/165 = 0.91 → TSS = 1.0 * 0.91² * 100 = **83 TSS**
- **Error**: 17% underestimation

---

## 2. All FTP-Dependent UI Elements

### Complete Table of Calculation Chains

| UI Element | Location | Data Source | Calculation Chain | Uses Threshold? | Status |
|------------|----------|-------------|-------------------|-----------------|--------|
| **Dashboard - CTL (Fitness)** | Dashboard.tsx L156 | `/garmin/training-metrics` | Settings → User.ftp/threshold_hr → Activity TSS → CTL calculation | ❌ BROKEN | 🔴 Uses max_hr instead of threshold_hr |
| **Dashboard - ATL (Fatigue)** | Dashboard.tsx L166 | `/garmin/training-metrics` | Settings → User.ftp/threshold_hr → Activity TSS → ATL calculation | ❌ BROKEN | 🔴 Uses max_hr instead of threshold_hr |
| **Dashboard - TSB (Form)** | Dashboard.tsx L176 | `/garmin/training-metrics` | Settings → User.ftp/threshold_hr → Activity TSS → TSB = CTL - ATL | ❌ BROKEN | 🔴 Uses max_hr instead of threshold_hr |
| **Dashboard - Weekly TSS** | Dashboard.tsx L186 | `/garmin/training-metrics` | Settings → User.ftp/threshold_hr → Sum of daily TSS (last 7 days) | ❌ BROKEN | 🔴 Uses max_hr instead of threshold_hr |
| **Dashboard - Performance Chart** | Dashboard.tsx L196 | `/garmin/training-load?days=42` | Settings → User.ftp/threshold_hr → Daily TSS → CTL/ATL/TSB over time | ❌ BROKEN | 🔴 Uses max_hr instead of threshold_hr |
| **Calendar - Activity TSS** | Calendar.tsx L230-231 | Activity.calculated_tss or training_load | Settings → User.ftp/threshold_hr → Activity sync → calculated_tss | ❌ BROKEN | 🔴 Uses max_hr instead of threshold_hr |
| **Settings - Power Zones** | SettingsNew.tsx L652 | `/auth/zones/power?method={method}&threshold={ftp}` | Settings.ftp (UI) → calculate_power_zones_coggan(ftp) | ✅ YES | ✅ Correctly uses FTP from UI |
| **Settings - HR Zones (Cycling)** | SettingsNew.tsx L777 | `/auth/zones/hr_cycling?method={method}&threshold={threshold_hr}&max_hr={max_hr}` | Settings.cycling_threshold_hr + max_hr (UI) → calculate_hr_zones_friel() | ✅ YES | ✅ Correctly uses threshold_hr + max_hr from UI |
| **Settings - HR Zones (Running)** | SettingsNew.tsx L777 | `/auth/zones/hr_running?method={method}&threshold={threshold_hr}&max_hr={max_hr}` | Settings.running_threshold_hr + max_hr (UI) → calculate_hr_zones_friel() | ✅ YES | ✅ Correctly uses threshold_hr + max_hr from UI |
| **Settings - Pace Zones (Running)** | SettingsNew.tsx L738 | `/auth/zones/pace_running?method={method}&threshold={pace}` | Settings.threshold_pace (UI) → calculate_pace_zones_friel() | ✅ YES | ✅ Correctly uses threshold_pace from UI |
| **Settings - Pace Zones (Swimming)** | SettingsNew.tsx L861 | `/auth/zones/pace_swimming?method={method}&threshold={pace}` | Settings.swim_threshold_pace (UI) → calculate_swim_zones_friel() | ✅ YES | ✅ Correctly uses swim_threshold_pace from UI |

---

## 3. Detailed Calculation Chains

### Chain 1: Settings → TSS → CTL/ATL/TSB → Dashboard ❌ BROKEN

```
┌─────────────────────────────────────────────────────────────────────────────┐
│ 1. User Input (Settings UI)                                                  │
│    - FTP: 250W                                                                │
│    - Running Threshold HR: 165 bpm                                            │
│    - Max HR: 180 bpm                                                          │
└──────────────────────────────┬────────────────────────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│ 2. Backend User Model                                                         │
│    user.ftp = 250                                                             │
│    user.running_threshold_hr = 165  ← CORRECT VALUE                          │
│    user.max_hr = 180                                                          │
└──────────────────────────────┬────────────────────────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│ 3. Activity Sync (garmin.py L319-328)                                        │
│    user_settings = {                                                          │
│        "ftp": current_user.ftp,                    ✅ CORRECT                │
│        "threshold_pace": current_user.threshold_pace,  ✅ CORRECT            │
│        "max_hr": current_user.max_hr,              ❌ WRONG KEY!             │
│        "resting_hr": current_user.resting_hr,      ✅ CORRECT                │
│    }                                                                           │
│    ⚠️ Missing: "threshold_hr": current_user.running_threshold_hr             │
└──────────────────────────────┬────────────────────────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│ 4. TSS Calculator (tss_calculator.py L252-293)                               │
│    threshold_hr = user_settings.get("max_hr", 180)  ❌ USES MAX_HR!         │
│    ⚠️ Expected: user_settings.get("threshold_hr")                            │
│                                                                                │
│    Calculate: IF = average_hr / max_hr  ← WRONG DENOMINATOR                  │
│    Example: 150 / 180 = 0.83  (underestimates intensity)                     │
│    Should be: 150 / 165 = 0.91  (correct intensity)                          │
└──────────────────────────────┬────────────────────────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│ 5. GarminActivity Model                                                       │
│    activity.calculated_tss = 69  ❌ WRONG (should be 83)                     │
│    Stored in database                                                         │
└──────────────────────────────┬────────────────────────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│ 6. Training Load Calculation (training_load.py)                              │
│    CTL = 42-day EMA of daily TSS  ❌ WRONG (TSS is underestimated)          │
│    ATL = 7-day EMA of daily TSS   ❌ WRONG                                   │
│    TSB = CTL - ATL                ❌ WRONG                                   │
└──────────────────────────────┬────────────────────────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│ 7. Dashboard Display                                                          │
│    CTL: 45 ← Should be ~54 (20% higher)                                      │
│    ATL: 38 ← Should be ~46 (21% higher)                                      │
│    TSB: 7  ← Should be ~8 (different)                                        │
│    Weekly TSS: 280 ← Should be ~336 (20% higher)                             │
│    ⚠️ ALL METRICS UNRELIABLE                                                 │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Chain 2: Settings → Zone Calculation → Settings UI ✅ WORKING

```
┌─────────────────────────────────────────────────────────────────────────────┐
│ 1. User Input (Settings UI)                                                  │
│    - FTP: 250W (typed in input field)                                        │
│    - Method: Coggan                                                           │
└──────────────────────────────┬────────────────────────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│ 2. API Call with Current UI Value                                            │
│    GET /auth/zones/power?method=coggan&threshold=250                         │
│    ✅ Passes current input value, not saved backend value                    │
└──────────────────────────────┬────────────────────────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│ 3. Backend Zone Calculation (training_zones.py)                              │
│    calculate_power_zones_coggan(250)                                         │
│    Returns zones: Z1: 0-137W, Z2: 138-185W, etc.                             │
│    ✅ Correctly uses provided threshold                                      │
└──────────────────────────────┬────────────────────────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│ 4. Frontend Display (Settings UI)                                            │
│    Shows zones side-by-side (current vs preview)                             │
│    User clicks "Apply & Save"                                                 │
│    ✅ Saves FTP to backend, applies zones to current                         │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 4. Root Cause Analysis

### Primary Issue
The `calculate_tss_from_activity()` function incorrectly maps user settings:

**Current Code** (WRONG):
```python
user_settings = {
    "ftp": current_user.ftp,
    "threshold_pace": current_user.threshold_pace,
    "max_hr": current_user.max_hr,  # ⚠️ This gets used as threshold_hr
    "resting_hr": current_user.resting_hr,
}

# Later in tss_calculator.py:
threshold_hr = user_settings.get("max_hr", 180)  # ⚠️ Wrong key!
```

**Should Be** (CORRECT):
```python
user_settings = {
    "ftp": current_user.ftp,
    "threshold_pace": current_user.threshold_pace,
    "threshold_hr": current_user.running_threshold_hr,  # ✅ Correct for running
    "max_hr": current_user.max_hr,
    "resting_hr": current_user.resting_hr,
}

# Later in tss_calculator.py:
threshold_hr = user_settings.get("threshold_hr", 165)  # ✅ Correct key
```

### Secondary Issue
The function doesn't differentiate between cycling, running, and swimming threshold HR:
- **Cycling**: Should use `user.cycling_threshold_hr`
- **Running**: Should use `user.running_threshold_hr`
- **Swimming**: Should use `user.swim_threshold_hr`

---

## 5. Impact Assessment

### Affected Features
1. ✅ **Zone Calculations** - Working correctly (uses UI values directly)
2. ❌ **TSS Calculations** - BROKEN (uses wrong threshold)
3. ❌ **CTL/ATL/TSB** - BROKEN (derived from wrong TSS)
4. ❌ **Dashboard Metrics** - BROKEN (displays wrong values)
5. ❌ **Training Load Chart** - BROKEN (wrong historical data)
6. ✅ **Settings UI** - Working correctly (saves thresholds properly)

### User Impact
- **Low FTP/Threshold**: Users with lower thresholds will see artificially inflated TSS
- **High FTP/Threshold**: Users with higher thresholds will see underestimated TSS
- **Training Plans**: Workout recommendations based on incorrect fitness levels
- **Recovery**: Wrong fatigue estimates could lead to overtraining or undertraining

---

## 6. Recommended Fixes

### Fix 1: Update Activity Sync (garmin.py)
```python
# Line 319-328 - Determine sport-specific threshold HR
sport_type = activity.get("activityType", {})
sport_key = sport_type.get("typeKey", "").lower() if isinstance(sport_type, dict) else ""

# Map sport to correct threshold HR
if 'cycl' in sport_key or 'bike' in sport_key:
    threshold_hr = current_user.cycling_threshold_hr
elif 'run' in sport_key:
    threshold_hr = current_user.running_threshold_hr
elif 'swim' in sport_key:
    threshold_hr = current_user.swim_threshold_hr
else:
    threshold_hr = current_user.running_threshold_hr  # Default

user_settings = {
    "ftp": current_user.ftp,
    "threshold_pace": current_user.threshold_pace,
    "threshold_hr": threshold_hr,  # ✅ Sport-specific threshold HR
    "max_hr": current_user.max_hr,
    "resting_hr": current_user.resting_hr,
}
```

### Fix 2: Update TSS Calculator (tss_calculator.py)
```python
# Line 286 - Use correct key
threshold_hr = user_settings.get("threshold_hr")  # ✅ Not "max_hr"
if not threshold_hr:
    # Fallback to max_hr if threshold not set (but warn user)
    threshold_hr = user_settings.get("max_hr", 165)
```

### Fix 3: Recalculate Historical Activities
After fixing the code, all existing activities need TSS recalculation:
```python
# Migration script to recalculate all TSS values
async def recalculate_all_tss(db: AsyncSession):
    activities = await db.execute(select(GarminActivity))
    for activity in activities.scalars():
        user = activity.user
        
        # Determine correct threshold HR by sport
        sport_key = activity.activity_type.lower()
        if 'cycl' in sport_key or 'bike' in sport_key:
            threshold_hr = user.cycling_threshold_hr
        elif 'run' in sport_key:
            threshold_hr = user.running_threshold_hr
        elif 'swim' in sport_key:
            threshold_hr = user.swim_threshold_hr
        else:
            threshold_hr = user.running_threshold_hr
        
        user_settings = {
            "ftp": user.ftp,
            "threshold_pace": user.threshold_pace,
            "threshold_hr": threshold_hr,
            "max_hr": user.max_hr,
            "resting_hr": user.resting_hr,
        }
        
        # Recalculate TSS
        new_tss = calculate_tss_from_activity(activity.raw_data, user_settings)
        activity.calculated_tss = new_tss
    
    await db.commit()
```

---

## 7. Testing Plan

### Unit Tests
1. Test TSS calculation with correct threshold HR
2. Test sport-specific threshold HR selection
3. Verify CTL/ATL/TSB calculations with corrected TSS

### Integration Tests
1. Sync activities and verify TSS uses correct threshold
2. Check Dashboard displays correct metrics
3. Verify historical recalculation script

### Manual Verification
1. Check Settings page saves all thresholds correctly
2. Sync an activity and verify TSS matches expected value
3. Compare CTL/ATL/TSB before and after fix

---

## 8. Conclusion

### Summary
- ❌ **CRITICAL BUG**: TSS calculations use max_hr instead of threshold_hr
- ❌ **IMPACT**: All training load metrics (CTL/ATL/TSB) are unreliable
- ✅ **GOOD**: Zone calculations work correctly
- ✅ **GOOD**: Settings save thresholds properly

### Priority
**🔴 CRITICAL** - This bug affects core functionality and user trust. Should be fixed immediately before users rely on incorrect training metrics.

### Estimated Fix Time
- Code changes: 30 minutes
- Testing: 1 hour
- Historical recalculation: 5 minutes per 1000 activities
- Total: ~2 hours

---

**Audit Date**: 2026-01-02  
**Next Review**: After fixes are implemented and tested
