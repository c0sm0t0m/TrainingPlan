# Time Series Analysis for Enhanced Threshold Detection

## Current Limitation
The current threshold estimation uses **aggregate activity metrics** (avg HR, avg pace, total duration). This works reasonably well for steady-state efforts but has limitations:

- **Interval workouts**: A 30-minute session with 6×3min intervals at 180 bpm and 3min recovery at 130 bpm averages to ~155 bpm, missing the threshold signal
- **Progression runs**: Start easy (140 bpm), finish hard (175 bpm) - average doesn't capture threshold pace
- **Fartlek sessions**: Variable intensity makes aggregate metrics less meaningful
- **Warmup/cooldown contamination**: A 60-minute workout with 10 min warmup + 40 min threshold + 10 min cooldown has diluted metrics

## Proposed Solution: Time Series Analysis

### Data Sources

**Option 1: activity_samples table (if available)**
```sql
SELECT 
    timestamp,
    heart_rate,
    speed,
    cadence,
    altitude
FROM activity_samples
WHERE activity_id = ?
ORDER BY timestamp
```

**Option 2: Parse FIT files directly**
- Use `fitparse` library (already in requirements)
- Extract record messages with HR, speed, distance, timestamp
- Store in activity_samples table or analyze on-the-fly

### Detection Algorithms

#### 1. **Interval Detection**
Identify sustained high-intensity efforts within activities:

```python
def detect_intervals(hr_stream, pace_stream, threshold_hr):
    """
    Detect intervals using moving window analysis.
    
    Criteria for interval:
    - HR >= 95% threshold for >= 2 minutes
    - Preceded/followed by recovery (HR < 85% threshold)
    - Pace relatively steady (CV < 10%)
    """
    intervals = []
    window_size = 120  # seconds
    
    for i in range(len(hr_stream) - window_size):
        window_hr = hr_stream[i:i+window_size]
        if mean(window_hr) >= threshold_hr * 0.95:
            # Found potential interval
            interval_start = i
            interval_end = find_interval_end(hr_stream[i:], threshold_hr)
            intervals.append({
                'start': interval_start,
                'end': interval_end,
                'duration': interval_end - interval_start,
                'avg_hr': mean(hr_stream[interval_start:interval_end]),
                'avg_pace': mean(pace_stream[interval_start:interval_end])
            })
    
    return intervals
```

#### 2. **Threshold Pace from Intervals**
Extract threshold estimates from detected intervals:

```python
def estimate_threshold_from_intervals(intervals, threshold_hr):
    """
    Weight interval data by quality metrics.
    
    Higher weight for:
    - Longer duration (3-8 minutes optimal)
    - Steadier HR (lower variation)
    - HR closer to threshold (95-105%)
    """
    weighted_estimates = []
    
    for interval in intervals:
        # Duration weight (peak at 3-5 min intervals)
        duration_weight = gaussian_weight(interval['duration'], peak=240, sigma=60)
        
        # HR steadiness weight (lower CV = higher weight)
        hr_cv = coefficient_variation(interval['hr_samples'])
        steadiness_weight = 1.0 - min(hr_cv, 0.3)
        
        # Proximity to threshold weight
        hr_diff = abs(interval['avg_hr'] - threshold_hr)
        proximity_weight = max(0, 1.0 - hr_diff / 20)
        
        total_weight = duration_weight * steadiness_weight * proximity_weight
        
        # Calculate threshold pace for this interval
        IF = interval['avg_hr'] / threshold_hr
        threshold_pace_est = interval['avg_pace'] * IF
        
        weighted_estimates.append({
            'threshold_pace': threshold_pace_est,
            'weight': total_weight,
            'confidence': total_weight
        })
    
    # Weighted average
    total_weight = sum(e['weight'] for e in weighted_estimates)
    threshold_pace = sum(e['threshold_pace'] * e['weight'] for e in weighted_estimates) / total_weight
    
    return threshold_pace, max(e['confidence'] for e in weighted_estimates)
```

#### 3. **Workout Type Classification**
Identify training stimulus type:

```python
def classify_workout(hr_stream, intervals):
    """
    Classify workout type based on HR distribution and interval structure.
    """
    if not intervals:
        return "steady_state"
    
    interval_durations = [i['duration'] for i in intervals]
    
    if all(120 <= d <= 180 for d in interval_durations):
        return "vo2max_intervals"  # 2-3 min intervals
    elif all(180 <= d <= 360 for d in interval_durations):
        return "threshold_repeats"  # 3-6 min intervals
    elif all(360 <= d <= 600 for d in interval_durations):
        return "tempo_intervals"  # 6-10 min intervals
    elif len(intervals) > 10 and all(d < 120 for d in interval_durations):
        return "fartlek"  # Many short surges
    else:
        return "mixed_intervals"
```

### Implementation Strategy

#### Phase 1: Data Collection (Week 1-2)
1. Add `activity_samples` table if not exists:
```sql
CREATE TABLE activity_samples (
    id SERIAL PRIMARY KEY,
    activity_id INTEGER REFERENCES garmin_activities(id),
    timestamp TIMESTAMP NOT NULL,
    heart_rate INTEGER,
    speed FLOAT,  -- m/s
    cadence INTEGER,
    altitude FLOAT,
    distance FLOAT,  -- cumulative meters
    INDEX(activity_id, timestamp)
);
```

2. Parse FIT files during activity sync to populate samples

#### Phase 2: Analysis Functions (Week 3-4)
1. Implement interval detection algorithm
2. Implement threshold estimation from intervals
3. Implement workout classification

#### Phase 3: Integration (Week 5)
1. Modify `get_key_sessions` endpoint to use time series analysis
2. Add new fields:
   - `workout_type`: "steady_state", "intervals", "fartlek", etc.
   - `interval_count`: Number of detected intervals
   - `threshold_pace_from_intervals`: More accurate estimate
3. Weight threshold estimates:
   - Steady state: Use whole activity
   - Intervals: Use interval segments only
   - Mixed: Weighted combination

#### Phase 4: UI Enhancements (Week 6)
1. Show workout type badge on key sessions
2. Display interval structure in tooltip
3. Add "Interval Analysis" tab showing detected intervals
4. Visualize HR/pace time series with interval overlays

### Expected Improvements

**Accuracy**:
- ±2-3 seconds/km threshold pace estimate (vs current ±10-15 sec/km)
- Properly handle interval workouts (currently ignored or misestimated)
- Identify best threshold indicators (specific intervals vs steady runs)

**Intelligence**:
- Differentiate between VO2max work (170-180 bpm, 3min) and threshold work (160-165 bpm, 10min)
- Detect progression: Is threshold improving over time with same RPE?
- Warn about overtraining: HR drift in threshold efforts

**User Value**:
- "Your 5×1000m intervals averaged 3:45/km at 172 bpm → estimated threshold 4:02/km"
- "In your last 3 threshold sessions, your threshold pace improved by 8 sec/km"
- "Today's tempo run showed 5% HR drift - consider more recovery"

### Technical Considerations

**Performance**:
- Time series analysis is CPU-intensive
- Cache analyzed results in activity table
- Run analysis async via Celery task
- Only re-analyze if activity data changes

**Data Volume**:
- 1 hour activity × 1 sample/second = 3600 records
- 1000 activities = 3.6M records
- Use time-series database features (TimescaleDB hypertables)

**Accuracy Validation**:
- Compare time-series estimates vs steady-state estimates
- Track user feedback: "Was this threshold estimate accurate?"
- Cross-validate against lab-tested thresholds if available

## Next Steps

1. ✅ Fix immediate threshold pace calculation (use IF instead of fixed factors)
2. ⏳ Parse FIT files to extract time series data (Week 1-2)
3. ⏳ Build interval detection algorithm (Week 3)
4. ⏳ Integrate into key sessions endpoint (Week 4-5)
5. ⏳ Add UI visualizations (Week 6)

## References

- **Interval Detection**: Similar to Garmin's Auto Lap feature and TrainingPeaks' interval detection
- **Workout Classification**: Based on Coggan/Allen "Training and Racing with a Power Meter" (adapted for running)
- **Threshold Estimation**: Jack Daniels' VDOT methodology + Andrew Coggan's TSS/IF framework
