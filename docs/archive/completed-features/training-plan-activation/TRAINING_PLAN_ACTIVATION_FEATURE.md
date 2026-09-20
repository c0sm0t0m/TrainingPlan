# Training Plan Activation Feature - Implementation Summary

**Date**: 2025-01-XX  
**Status**: ✅ Complete

## Overview

Implemented a training plan activation system that allows users to control which training plan's workouts appear in the calendar. Only one plan can be active at a time, and users must explicitly activate a plan for its workouts to show up.

## Problem Solved

Previously, ALL training plans' workouts would automatically show in the calendar, causing clutter when users had multiple plans. Users had no control over which plan's workouts were visible.

## Solution

### 1. Backend Changes

#### Modified Files:
- `backend/src/api/routes/training_plans.py`

#### Changes Made:

**A. Added Query Parameter to List Endpoint**
```python
@router.get("", response_model=List[TrainingPlanSummary])
async def list_training_plans(
    skip: int = 0,
    limit: int = 100,
    active_only: bool = False,  # NEW PARAMETER
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
```

- Added `active_only` boolean parameter
- When `True`, filters to only return plans where `is_active = 1`
- Calendar now uses this to fetch only active plans

**B. Activate Endpoint** (Already existed, lines 283-365)
```python
@router.post("/{plan_id}/activate", response_model=TrainingPlanSchema)
async def activate_training_plan(...)
```

- Deactivates all other plans for the user (mutual exclusion)
- Sets target plan's `is_active = 1`
- Returns full plan with workouts

**C. Deactivate Endpoint** (Already existed, lines 368-450)
```python
@router.post("/{plan_id}/deactivate", response_model=TrainingPlanSchema)
async def deactivate_training_plan(...)
```

- Sets plan's `is_active = 0`
- Returns full plan with workouts

### 2. Frontend Changes

#### Modified Files:
- `frontend/src/pages/TrainingPlans.tsx`
- `frontend/src/pages/Calendar.tsx`

#### A. TrainingPlans Page UI

**New Imports Added:**
```typescript
import { Switch, FormControlLabel, Badge, Tooltip } from '@mui/material';
import { CheckCircle as CheckCircleIcon } from '@mui/icons-material';
```

**New Handler Function:**
```typescript
const handleToggleActivePlan = async (planId: number, currentlyActive: boolean) => {
  try {
    if (currentlyActive) {
      await api.post(`/training-plans/${planId}/deactivate`);
    } else {
      await api.post(`/training-plans/${planId}/activate`);
    }
    fetchPlans(); // Refresh to show updated status
  } catch (err: any) {
    setError(err.response?.data?.detail || 'Failed to update plan status');
  }
};
```

**Plan Card UI Enhancements:**

1. **Active Plan Border**
   - Active plans have a 2px primary-colored border
   - Inactive plans have standard 1px divider border

2. **"ACTIVE" Badge**
   - Green chip with checkmark icon
   - Positioned top-right of card
   - Only shown on active plan

3. **Activation Toggle Switch**
   - Switch control labeled "Show in Calendar"
   - Located at bottom of card content
   - Separated by top border for visual grouping
   - Tooltip explains functionality

4. **Info Alert**
   - Shows helpful message above plan cards:
     > "💡 Calendar Control: Only workouts from active training plans appear in your calendar. Toggle 'Show in Calendar' to control which plan's workouts are displayed. Only one plan can be active at a time."

#### B. Calendar Page

**Updated Fetch Logic:**
```typescript
// OLD: Fetch ALL plans
const response = await api.get('/training-plans');

// NEW: Fetch ONLY active plans
const response = await api.get('/training-plans', {
  params: { active_only: true }
});
```

## User Experience Flow

### Activating a Plan:

1. User navigates to Plans tab
2. Sees all plans with current activation status
3. Toggles "Show in Calendar" switch on desired plan
4. Backend:
   - Deactivates any currently active plan
   - Activates selected plan
5. Frontend:
   - Refreshes plan list
   - Shows "ACTIVE" badge on newly activated plan
   - Previous active plan's badge disappears
6. Calendar now shows only the active plan's workouts

### Visual Indicators:

- **Active Plan Card:**
  - Green "ACTIVE" badge with checkmark (top-right)
  - Primary-colored border (2px)
  - Toggle switch is ON
  - Bold "Show in Calendar" label

- **Inactive Plan Card:**
  - No badge
  - Standard border (1px)
  - Toggle switch is OFF
  - Regular "Show in Calendar" label

## Technical Details

### Database Schema
Uses existing `is_active` column in `training_plans` table:
- Type: INTEGER (0 or 1 in SQLite, treated as boolean)
- Default: 0 (false)
- Only one plan per user should have `is_active = 1` at a time

### Mutual Exclusion Logic
When activating a plan:
```python
# Deactivate all other plans
all_plans = await db.execute(
    select(TrainingPlan).where(TrainingPlan.user_id == current_user.id)
)
for p in all_plans.scalars().all():
    p.is_active = 0

# Activate target plan
plan.is_active = 1
await db.commit()
```

### API Endpoints Summary

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/training-plans?active_only=true` | GET | Fetch only active plans (used by Calendar) |
| `/training-plans/{id}/activate` | POST | Activate a plan (deactivates others) |
| `/training-plans/{id}/deactivate` | POST | Deactivate a plan |

## Testing Checklist

- [x] Create multiple training plans
- [x] Verify all plans show in Plans tab
- [x] Activate one plan - verify "ACTIVE" badge appears
- [x] Check calendar - verify only active plan's workouts show
- [x] Activate different plan - verify badge moves, calendar updates
- [x] Deactivate all plans - verify calendar is empty
- [x] Verify info alert shows when plans exist
- [x] Verify toggle switch works smoothly
- [x] Verify tooltips provide helpful context

## Benefits

1. **User Control**: Explicit control over calendar visibility
2. **No Clutter**: Calendar only shows relevant workouts
3. **Clear Indication**: Visual badges and borders make active status obvious
4. **Smooth UX**: Toggle switch for easy activation/deactivation
5. **Helpful Guidance**: Info alert explains the feature
6. **Single Active Plan**: Prevents confusion from multiple overlapping plans

## Future Enhancements (Optional)

- [ ] Add confirmation dialog when activating a different plan
- [ ] Show active plan name in Calendar header/toolbar
- [ ] Add "Quick Activate" button in Calendar when no plan is active
- [ ] Allow filtering Calendar by inactive plans (view-only mode)
- [ ] Add activation history/log
- [ ] Email notification when plan becomes active
- [ ] Auto-activate plans based on start date

## Related Files

- Backend API: `/backend/src/api/routes/training_plans.py`
- Calendar Frontend: `/frontend/src/pages/Calendar.tsx`
- Plans Frontend: `/frontend/src/pages/TrainingPlans.tsx`
- Database Model: `/backend/src/models/training_plan.py` (uses existing is_active field)

## Conclusion

The training plan activation feature successfully provides users with explicit control over which training plan's workouts appear in their calendar, preventing clutter and improving the overall user experience.
