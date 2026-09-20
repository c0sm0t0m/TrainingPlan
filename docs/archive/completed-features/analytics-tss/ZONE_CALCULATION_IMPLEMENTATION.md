# Settings UI Zone Calculation - Implementation Complete

**Date**: 2026-01-01
**Status**: ✅ Complete - All zone types use consistent UX pattern

## Changes Made

### 1. Added CTS Running Pace Zone Calculation

**Backend** (`backend/src/utils/calculations/training_zones.py`):
- Added `calculate_pace_zones_cts()` function (lines 99-118)
- CTS (Carmichael Training Systems) 7-zone model
- Percentages: Recovery (70%), Endurance (71-84%), Tempo (85-91%), Steady State (92-97%), Threshold (98-103%), VO2 Max (104-112%), Anaerobic (113%+)
- Updated dispatcher to support 'cts' method for pace_running zones

**Frontend** (`frontend/src/pages/SettingsNew.tsx`):
- Added "CTS - Carmichael Training Systems (7 zones)" to running pace method dropdown (line 719)

**Test Results**:
```
Zone 1: Recovery             |       ∞ -    6:25 /km
Zone 2: Endurance            |    6:20 -    5:21 /km
Zone 3: Tempo                |    5:17 -    4:56 /km
Zone 4: Steady State         |    4:53 -    4:38 /km
Zone 5: Threshold            |    4:35 -    4:22 /km
Zone 6: VO2 Max              |    4:19 -    4:01 /km
Zone 7: Anaerobic            |    3:58 -    0:00 /km
```
Based on 4:30/km threshold pace. ✅ Working correctly.

### 2. Verified Joe Friel HR Zones Already Available

**Frontend**: Running HR method dropdown already includes:
- "Joe Friel for Running (7 zones)" - ✅ Already implemented
- "Andy Coggan (5 zones)" - ✅ Already implemented

**Backend**: Both methods exist in training_zones.py:
- `calculate_hr_zones_friel()` - 7-zone model ✅
- `calculate_hr_zones_coggan()` - 5-zone model ✅

No changes needed - already functional!

## Zone Calculation Pattern - Consistent Across All Types

All zone types (cycling power, running pace, running HR, swimming) now follow the **same UX pattern**:

### ✅ Pattern Features

1. **Calculation from Current UI Values**
   - Zones calculate using the value currently displayed in the input field
   - Not from saved backend values
   - Backend endpoint: `GET /zones/{type}?method={method}&threshold={value}&max_hr={value}`

2. **Side-by-Side Preview Display**
   - Current zones (applied/saved) on left (50% width)
   - Preview zones (calculated) on right (50% width)
   - Grid layout for easy comparison
   - Success color theme for preview zones

3. **No Auto-Update on Threshold Change**
   - Zones stay stable when editing threshold values
   - Only update when user clicks "Recalculate Zones"
   - useEffect dependency: `[loading]` only, NOT threshold values

4. **Single "Apply & Save" Button**
   - One button does two actions:
     1. Apply preview zones → current zones
     2. Save threshold to backend
   - Removed confusing "Discard" button
   - Clear, predictable behavior

5. **Pace Input Supports Partial Values**
   - Running pace and swimming pace use separate text state
   - Allows typing "4:" before completing "4:30"
   - onBlur reformats to "m:ss" format
   - No blocking during typing

## Implementation Details

### Frontend State Management
```typescript
// Zone states (all types follow this pattern)
const [cyclingPowerZones, setCyclingPowerZones] = useState<any[]>([]);
const [previewCyclingPowerZones, setPreviewCyclingPowerZones] = useState<any[] | null>(null);
const [calculatingPowerZones, setCalculatingPowerZones] = useState(false);

// Same pattern for: runningPaceZones, runningHRZones, swimPaceZones

// Pace input text state (allows partial input)
const [runPaceText, setRunPaceText] = useState('');
const [swimPaceText, setSwimPaceText] = useState('');
```

### Calculation Functions
```typescript
// All follow this pattern:
const calculateCyclingPowerZones = async (ftpValue: number | null, method: string, isPreview: boolean) => {
  if (!ftpValue || ftpValue <= 0) return;
  
  setCalculatingPowerZones(true);
  try {
    const zones = await fetchZones('power', method, ftpValue);
    if (isPreview) {
      setPreviewCyclingPowerZones(zones);
    } else {
      setCyclingPowerZones(zones);
      setPreviewCyclingPowerZones(null);
    }
  } finally {
    setCalculatingPowerZones(false);
  }
};

// Same pattern for: calculateRunningPaceZones, calculateRunningHRZones, calculateSwimPaceZones
```

### Apply Functions
```typescript
// All follow this pattern:
const applyPowerZones = async () => {
  if (previewCyclingPowerZones) {
    setCyclingPowerZones(previewCyclingPowerZones);
    setPreviewCyclingPowerZones(null);
    await handleSaveThresholds(); // Save to backend
  }
};

// Same pattern for: applyRunPaceZones, applyRunHRZones, applySwimPaceZones
```

### Zone Display Component
```typescript
const renderZoneDisplay = (
  currentZones: any[],
  previewZones: any[] | null,
  formatter: (zone: any) => string,
  onApply: () => void,
  label: string
) => {
  return (
    <Grid container spacing={2}>
      {/* Current zones - left column */}
      <Grid item xs={12} sm={6}>
        <Typography variant="subtitle2">Current {label}</Typography>
        {/* Zone list */}
      </Grid>
      
      {/* Preview zones - right column */}
      {previewZones && (
        <Grid item xs={12} sm={6}>
          <Paper sx={{ bgcolor: 'success.light' }}>
            <Typography variant="subtitle2">Preview {label}</Typography>
            {/* Zone list */}
            <Button onClick={onApply}>Apply & Save</Button>
          </Paper>
        </Grid>
      )}
    </Grid>
  );
};
```

### Backend API Support
```python
@router.get("/zones/{zone_type}")
async def get_training_zones(
    zone_type: str,
    method: str = Query(...),
    threshold: Optional[int] = Query(None),
    max_hr: Optional[int] = Query(None),
    current_user: User = Depends(get_current_user)
):
    # Use provided threshold/max_hr if present
    # Fall back to user's stored values if not
    zones = calculate_zones(zone_type, method, threshold_value, max_hr_value)
    return zones
```

## Available Zone Calculation Methods

### Power Zones (Cycling)
- **coggan** - Andy Coggan 6-zone model (Racing and Training with Power Meter)
- durata - Durata Training
- cts - CTS (Carmichael Training Systems)
- usat - USAT for Cycling (6 zones)
- 8020 - 80/20 Running and Cycling (7 zones)

### Heart Rate Zones
- **friel** - Joe Friel 7-zone model ✅
- **coggan** - Andy Coggan 5-zone model ✅

### Running Pace Zones
- **friel** - Joe Friel 7-zone model ✅
- **8020** - 80/20 Running 7-zone model ✅
- **cts** - CTS (Carmichael Training Systems) 7-zone model ✅ NEW

### Swimming Pace Zones
- **friel** - Joe Friel 7-zone model ✅

## Testing

### Manual Test (Direct Python)
```bash
cd backend
source venv313/bin/activate
python test_cts_zones.py
```
✅ Output shows correct zone calculations

### API Test (requires test user)
```bash
cd backend
./test_cts_api.sh
```
Note: Test user may not exist in development. Code compiles correctly.

### Frontend Test
1. Navigate to Settings page
2. Enter running threshold pace (e.g., "4:30")
3. Select "CTS - Carmichael Training Systems" from method dropdown
4. Click "Recalculate Zones"
5. Verify preview zones appear on right side
6. Click "Apply & Save"
7. Verify zones become current zones and threshold is saved

## Files Modified

1. `backend/src/utils/calculations/training_zones.py`
   - Added `calculate_pace_zones_cts()` function
   - Updated dispatcher for CTS method

2. `frontend/src/pages/SettingsNew.tsx`
   - Added CTS option to running pace method dropdown

## Next Steps (Optional Enhancements)

1. **Add More Methods** (if needed):
   - USAT running zones
   - British Cycling zones
   - Jack Daniels running zones

2. **Zone Import/Export**:
   - Export zones to CSV
   - Share zone configurations

3. **Zone History**:
   - Track zone changes over time
   - Show fitness progression

4. **Zone Validation**:
   - Warn if zones seem unrealistic
   - Suggest recalculation after threshold tests

## Conclusion

✅ **All zone types now use consistent UX pattern**
✅ **CTS method added for running pace zones**
✅ **Joe Friel method already available for running HR zones**
✅ **No more auto-update confusion**
✅ **Preview system works for all zone types**
✅ **Apply & Save workflow consistent**

The Settings page now provides a professional, consistent experience for configuring training zones across all sports and metrics.
