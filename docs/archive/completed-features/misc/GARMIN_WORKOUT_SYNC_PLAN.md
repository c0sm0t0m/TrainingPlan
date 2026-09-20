# Garmin Workout Sync - Implementation Plan

## Feature: Sync Upcoming Trainings Back to Garmin

**Priority:** Top Priority (Next Feature)  
**Goal:** Push upcoming workouts from training plans to Garmin Connect so they appear on user's Garmin device

### Acceptance Criteria
✅ Upcoming trainings from training plans appear in Garmin Connect calendar  
✅ Workouts are visible on Garmin device when offline  
✅ Structured workouts display with proper intervals, targets, and zones  
✅ User can manually trigger sync or automatic daily sync  
✅ Avoid duplicate workouts (track sync status)

---

## Technical Analysis

### Garmin Connect API Capabilities
The `garminconnect` library provides these workout upload methods:
- `upload_workout()` - Generic workout upload
- `upload_running_workout()` - Running-specific
- `upload_cycling_workout()` - Cycling-specific  
- `upload_swimming_workout()` - Swimming-specific
- `upload_walking_workout()` - Walking-specific
- `get_workouts()` - List existing workouts
- `get_workout_by_id()` - Get workout details
- `download_workout()` - Download workout file

### Workout Format
Garmin workouts require:
1. **JSON structure** with workout definition
2. **FIT file** format (optional, for more complex workouts)
3. **Workout steps** with:
   - Duration (time, distance, calories, or open)
   - Target (pace, heart rate, power, cadence, or none)
   - Intensity (warmup, active, recovery, cooldown, rest)
   - Step type (interval, repeat, rest)

### Data Flow
```
Training Plan (DB)
  ↓
Workout Model
  ↓
Garmin Workout JSON Converter
  ↓
Garmin Connect API
  ↓
Garmin Device (sync)
```

---

## Implementation Plan

### Phase 1: Database Schema Enhancement (30 min)

**Task 1.1:** Add workout sync tracking fields to `Workout` model
```python
# Add to backend/src/models/training_plan.py
class Workout(Base):
    # ... existing fields ...
    
    # Garmin sync fields
    garmin_workout_id = Column(String, nullable=True)  # Garmin's workout ID
    garmin_synced_at = Column(DateTime, nullable=True)  # Last sync timestamp
    garmin_sync_status = Column(String, default="not_synced")  # not_synced, synced, failed, modified
```

**Task 1.2:** Create database migration
```bash
cd backend
alembic revision -m "add_garmin_workout_sync_fields"
alembic upgrade head
```

---

### Phase 2: Garmin Workout Converter (2 hours)

**Task 2.1:** Create workout JSON converter utility
```python
# backend/src/utils/garmin_workout_converter.py

def workout_to_garmin_json(workout: Workout) -> dict:
    """
    Convert our Workout model to Garmin workout JSON format.
    
    Returns dict with:
    - workoutName: str
    - sportType: dict (typeId, typeKey)
    - workoutSegments: list of steps
    """
    pass

def create_structured_workout(workout: Workout) -> dict:
    """
    Create structured workout with intervals from workout_structure JSON.
    Parse warmup, intervals, cooldown, etc.
    """
    pass

def create_simple_workout(workout: Workout) -> dict:
    """
    Create simple workout (distance/time goal) from basic workout data.
    """
    pass
```

**Task 2.2:** Implement sport type mapping
```python
SPORT_TYPE_MAP = {
    'running': {'typeId': 1, 'typeKey': 'running'},
    'cycling': {'typeId': 2, 'typeKey': 'cycling'},
    'swimming': {'typeId': 3, 'typeKey': 'lap_swimming'},
    'strength': {'typeId': 13, 'typeKey': 'strength_training'},
}
```

**Task 2.3:** Implement workout step conversion
- Duration types: time, distance, lap button press, open
- Target types: pace zone, HR zone, power zone, cadence, no target
- Intensity: warmup, active, recovery, cooldown, rest

---

### Phase 3: Garmin Service Enhancement (2 hours)

**Task 3.1:** Add workout upload method to `GarminService`
```python
# backend/src/services/garmin_service.py

async def upload_workout_to_garmin(
    self,
    oauth1_token: str,
    oauth2_token: str,
    workout: Workout
) -> str:
    """
    Upload a single workout to Garmin Connect.
    
    Returns:
        workout_id: Garmin's workout ID
    """
    pass

async def sync_upcoming_workouts(
    self,
    oauth1_token: str,
    oauth2_token: str,
    user_id: int,
    days_ahead: int = 14
) -> dict:
    """
    Sync upcoming workouts for next N days.
    
    Returns:
        {
            'synced': int,
            'failed': int,
            'skipped': int,
            'errors': list
        }
    """
    pass

async def delete_workout_from_garmin(
    self,
    oauth1_token: str,
    oauth2_token: str,
    garmin_workout_id: str
) -> bool:
    """Delete a workout from Garmin Connect."""
    pass
```

---

### Phase 4: API Endpoints (1 hour)

**Task 4.1:** Create workout sync endpoints
```python
# backend/src/api/routes/garmin.py

@router.post("/sync-workouts")
async def sync_workouts_to_garmin(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    days_ahead: int = Body(14, embed=True)
):
    """
    Sync upcoming workouts to Garmin Connect.
    
    Body:
        days_ahead: Number of days to sync (default 14)
    
    Returns:
        Sync summary with counts and errors
    """
    pass

@router.post("/sync-workout/{workout_id}")
async def sync_single_workout(
    workout_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Sync a single workout to Garmin."""
    pass

@router.delete("/workout/{workout_id}/garmin")
async def remove_workout_from_garmin(
    workout_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Remove a synced workout from Garmin Connect."""
    pass
```

---

### Phase 5: Frontend UI (2 hours)

**Task 5.1:** Add sync button to training plan detail page
```tsx
// frontend/src/pages/PlanDetail.tsx

<Button 
  onClick={handleSyncToGarmin}
  disabled={syncing}
>
  {syncing ? 'Syncing...' : 'Sync to Garmin'}
</Button>
```

**Task 5.2:** Add sync status indicators
- Show sync status per workout (synced icon, not synced, failed)
- Display last sync time
- Show error messages if sync fails

**Task 5.3:** Add sync settings
- Auto-sync toggle
- Days ahead configuration
- Sync frequency

---

### Phase 6: Background Sync (Optional - 1 hour)

**Task 6.1:** Create Celery task for daily sync
```python
# backend/src/tasks/garmin_sync.py

@celery_app.task
def sync_upcoming_workouts_task(user_id: int):
    """Background task to sync workouts daily."""
    pass
```

**Task 6.2:** Schedule daily sync
- Run at configurable time (e.g., midnight)
- Only for users with auto-sync enabled

---

## Testing Strategy

### Unit Tests
- [ ] Test workout JSON conversion
- [ ] Test sport type mapping
- [ ] Test workout step creation
- [ ] Test sync status tracking

### Integration Tests
- [ ] Test single workout upload
- [ ] Test bulk workout sync
- [ ] Test duplicate detection
- [ ] Test error handling

### Manual Testing
- [ ] Create simple workout → Verify in Garmin Connect
- [ ] Create structured workout with intervals → Verify structure
- [ ] Sync 14 days of workouts → Check all appear
- [ ] Modify synced workout → Re-sync → Verify update
- [ ] Delete workout → Verify removal from Garmin
- [ ] Check workout on Garmin device (offline)

---

## Error Handling

### Common Errors
1. **Authentication expired** → Prompt re-authentication
2. **Invalid workout format** → Log error, skip workout
3. **Network timeout** → Retry with exponential backoff
4. **Rate limiting** → Queue and retry later
5. **Duplicate workout** → Skip or update existing

### User Notifications
- Success: "Synced 12 workouts to Garmin"
- Partial: "Synced 10/12 workouts (2 failed)"
- Failure: "Failed to sync. Please reconnect Garmin account"

---

## Timeline Estimate

| Phase | Task | Time | 
|-------|------|------|
| 1 | Database schema | 30 min |
| 2 | Workout converter | 2 hours |
| 3 | Garmin service | 2 hours |
| 4 | API endpoints | 1 hour |
| 5 | Frontend UI | 2 hours |
| 6 | Background sync (optional) | 1 hour |
| Testing | Manual & unit tests | 1.5 hours |
| **Total** | | **10 hours** |

---

## Success Metrics

- [ ] User can sync workouts with one click
- [ ] Workouts appear in Garmin Connect within 30 seconds
- [ ] Workouts are visible on Garmin device offline
- [ ] Structured workouts display all intervals correctly
- [ ] No duplicate workouts created
- [ ] Sync works for running, cycling, and swimming
- [ ] Error messages are clear and actionable

---

## Future Enhancements

1. **Bi-directional sync**: Import workout completions from Garmin
2. **Workout templates**: Pre-defined workout structures
3. **FIT file generation**: For more advanced workout features
4. **Workout notes**: Sync workout descriptions to Garmin
5. **Calendar integration**: Sync to Garmin calendar events
6. **Smart scheduling**: Suggest optimal workout placement based on recovery

---

## API Research Notes

### Garmin Workout JSON Structure
```json
{
  "workoutName": "5K Easy Run",
  "sportType": {
    "typeId": 1,
    "typeKey": "running"
  },
  "workoutSegments": [
    {
      "segmentOrder": 1,
      "sportType": {"typeId": 1, "typeKey": "running"},
      "workoutSteps": [
        {
          "type": "ExecutableStepDTO",
          "stepId": null,
          "stepOrder": 1,
          "stepType": {
            "stepTypeId": 3,
            "stepTypeKey": "warmup"
          },
          "endCondition": {
            "conditionTypeKey": "time",
            "conditionTypeId": 2
          },
          "endConditionValue": 600,  // 10 minutes in seconds
          "targetType": {
            "workoutTargetTypeId": 1,
            "workoutTargetTypeKey": "no.target"
          }
        }
      ]
    }
  ]
}
```

---

## Next Steps

1. ✅ Review and approve plan
2. Start with Phase 1: Database schema
3. Implement Phase 2: Workout converter
4. Test with sample workout upload
5. Complete remaining phases
6. Deploy and test with real Garmin device
