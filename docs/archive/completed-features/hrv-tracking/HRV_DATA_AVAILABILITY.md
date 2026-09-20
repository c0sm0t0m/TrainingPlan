# Garmin Heart Rate Variability (HRV) Data - API Access

**Date**: 2026-01-05  
**Status**: ✅ **FULLY AVAILABLE**

## Summary

The Garmin Connect API **DOES provide comprehensive HRV data** through the `garminconnect` library.

## API Access Method

### Python Library Support

```python
from garminconnect import Garmin

# After authentication
api = Garmin(email, password)
api.login()

# Get HRV data for a specific date
hrv_data = api.get_hrv_data("2026-01-05")  # YYYY-MM-DD format
```

### Underlying Library

The `garminconnect` library uses `garth` under the hood, which also provides direct HRV access:
- `garth.DailyHRV(date)` - Returns daily HRV summary

## Data Structure

### Complete HRV Response

```json
{
  "userProfilePk": 12345678,
  "hrvSummary": {
    "calendarDate": "2026-01-05",
    "weeklyAvg": 47,
    "lastNightAvg": 45,
    "lastNight5MinHigh": 64,
    "baseline": {
      "lowUpper": 35,
      "balancedLow": 38,
      "balancedUpper": 58,
      "markerValue": 0.475
    },
    "status": "BALANCED",
    "feedbackPhrase": "HRV_BALANCED_2",
    "createTimeStamp": "2026-01-05T06:17:34.503"
  },
  "hrvReadings": [
    {
      "hrvValue": 37,
      "readingTimeGMT": "2026-01-04T23:02:20.0",
      "readingTimeLocal": "2026-01-05T00:02:20.0"
    },
    {
      "hrvValue": 30,
      "readingTimeGMT": "2026-01-04T23:07:20.0",
      "readingTimeLocal": "2026-01-05T00:07:20.0"
    }
    // ... ~60-70 readings per night (5-minute intervals)
  ],
  "startTimestampGMT": "2026-01-04T23:01:00.0",
  "endTimestampGMT": "2026-01-05T04:27:20.0",
  "startTimestampLocal": "2026-01-05T00:01:00.0",
  "endTimestampLocal": "2026-01-05T05:27:20.0",
  "sleepStartTimestampGMT": "2026-01-04T23:01:00.0",
  "sleepEndTimestampGMT": "2026-01-05T04:28:00.0",
  "sleepStartTimestampLocal": "2026-01-05T00:01:00.0",
  "sleepEndTimestampLocal": "2026-01-05T05:28:00.0"
}
```

## Available HRV Metrics

### Summary Metrics (`hrvSummary`)
- **`weeklyAvg`**: 7-day rolling average HRV (ms)
- **`lastNightAvg`**: Average HRV during last night's sleep (ms)
- **`lastNight5MinHigh`**: Highest 5-minute average HRV reading (ms)
- **`status`**: HRV status classification
  - `"BALANCED"` - Within normal range
  - `"LOW"` - Below baseline
  - `"UNBALANCED"` - Outside normal range
- **`feedbackPhrase`**: Garmin's feedback key (e.g., `"HRV_BALANCED_2"`)
- **`createTimeStamp`**: When the HRV data was processed

### Baseline Values (`baseline`)
- **`lowUpper`**: Upper bound of "low" zone (ms)
- **`balancedLow`**: Lower bound of "balanced" zone (ms)
- **`balancedUpper`**: Upper bound of "balanced" zone (ms)
- **`markerValue`**: Normalized marker value (0-1 scale)

### Time Series Data (`hrvReadings`)
- **Individual readings** taken every **5 minutes** during sleep
- Each reading includes:
  - `hrvValue`: HRV in milliseconds (RMSSD)
  - `readingTimeGMT`: UTC timestamp
  - `readingTimeLocal`: Local time timestamp

### Temporal Data
- `startTimestampGMT/Local`: When HRV tracking started
- `endTimestampGMT/Local`: When HRV tracking ended
- `sleepStartTimestampGMT/Local`: Detected sleep start time
- `sleepEndTimestampGMT/Local`: Detected sleep end time

## HRV Measurement Details

### RMSSD (Root Mean Square of Successive Differences)
Garmin measures HRV using **RMSSD** methodology:
- Calculated from inter-beat intervals (R-R intervals)
- Represents parasympathetic nervous system activity
- Higher values generally indicate better recovery
- Normal ranges: 20-100 ms (varies by individual)

### Measurement Frequency
- Readings taken every **5 minutes** during sleep
- Typically **60-80 readings** per night
- Most accurate during deep sleep phases

### Data Collection Window
- Primary collection: **During sleep**
- Start: When user goes to bed (detected automatically)
- End: When user wakes up
- Can also track during the day with compatible devices

## Device Requirements

### Compatible Devices
HRV tracking requires a Garmin device with optical heart rate sensor:
- **Fenix Series**: Fenix 6, 7, 7S, 7X, 8
- **Forerunner Series**: Forerunner 255, 265, 955, 965
- **Venu Series**: Venu 2, 2 Plus, 3
- **Epix Series**: Epix Gen 2
- **Instinct Series**: Instinct 2 Solar
- Other devices with "All-Day Stress Tracking" support

### Device Settings
To collect HRV data:
1. **Enable All-Day Stress Tracking** in device settings
2. **Wear watch during sleep** (snug but comfortable fit)
3. **Regular syncing** with Garmin Connect app
4. **Optical HR sensor** must be in contact with skin

## Integration with TrainingPlan

### Current Status
- ✅ API method available in `garmin_service.py`
- ❌ Not yet integrated into database
- ❌ Not yet exposed via REST API
- ❌ No UI for HRV display

### Implementation Path

#### 1. Add HRV Data Model
```python
# backend/src/models/garmin_hrv.py
class GarminHRV(Base):
    __tablename__ = "garmin_hrv"
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    date = Column(Date, nullable=False, index=True)
    
    # Summary metrics
    weekly_avg = Column(Float)
    last_night_avg = Column(Float)
    last_night_5min_high = Column(Float)
    
    # Baseline
    baseline_low_upper = Column(Float)
    baseline_balanced_low = Column(Float)
    baseline_balanced_upper = Column(Float)
    
    # Status
    status = Column(String)  # BALANCED, LOW, UNBALANCED
    feedback_phrase = Column(String)
    
    # Sleep times
    sleep_start = Column(DateTime)
    sleep_end = Column(DateTime)
    
    # Full data
    raw_data = Column(JSON)  # Store full response
    
    synced_at = Column(DateTime, default=datetime.utcnow)
```

#### 2. Add Sync Method
```python
# backend/src/services/garmin_service.py
async def sync_hrv_data(
    self,
    oauth1_token: str,
    oauth2_token: str,
    days_back: int = 30
) -> List[Dict]:
    """Fetch HRV data for the last N days."""
    api = await self.resume_session(oauth1_token, oauth2_token)
    
    hrv_records = []
    today = date.today()
    
    for i in range(days_back):
        target_date = today - timedelta(days=i)
        date_str = target_date.strftime("%Y-%m-%d")
        
        try:
            hrv_data = api.get_hrv_data(date_str)
            if hrv_data:
                hrv_records.append({
                    "date": target_date,
                    "data": hrv_data
                })
        except Exception as e:
            print(f"Failed to fetch HRV for {date_str}: {e}")
    
    return hrv_records
```

#### 3. Add API Endpoint
```python
# backend/src/api/routes/garmin.py
@router.post("/sync-hrv")
async def sync_hrv_data(
    days: int = 30,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Sync HRV data from Garmin Connect."""
    if not current_user.garmin_connected:
        raise HTTPException(status_code=400, detail="Garmin not connected")
    
    hrv_data = await garmin_service.sync_hrv_data(
        current_user.garmin_oauth1_token,
        current_user.garmin_oauth2_token,
        days_back=days
    )
    
    # Store in database...
    return {"synced": len(hrv_data)}

@router.get("/hrv")
async def get_hrv_data(
    days: int = 30,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get HRV data for last N days."""
    # Query from database...
    pass
```

#### 4. UI Components
- **HRV Trend Chart**: 7-day / 30-day rolling average
- **Recovery Status Indicator**: Color-coded status (green/yellow/red)
- **Baseline Range Visualization**: Show current value vs. baseline
- **Sleep Quality Correlation**: Compare HRV with sleep duration/quality
- **Training Load Correlation**: Show HRV vs. TSB (Training Stress Balance)

## Use Cases in Training

### Recovery Monitoring
- **Low HRV + High TSS** → Need rest
- **High HRV + Low TSB** → Ready for hard workout
- **Declining HRV trend** → Overtraining risk

### Training Plan Adaptation
- Adjust workout intensity based on HRV status
- Recommend rest days when HRV is consistently low
- Identify optimal training load for individual recovery

### Long-Term Trends
- Track baseline changes over months
- Correlate with performance improvements
- Detect illness/overtraining early

## Technical Notes

### Data Retention
- Garmin stores HRV data indefinitely
- Can query historical data back to device purchase
- No known API rate limits for HRV endpoint

### Data Quality
- Most reliable during **deep sleep phases**
- Optical HR sensors less accurate than chest straps
- Individual variation is normal (baseline matters more than absolute values)

### Privacy Considerations
- HRV data can indicate health status
- Should be treated as sensitive health information
- Recommend encryption at rest in database

## References

- **Test Script**: [backend/test_garmin_hrv.py](test_garmin_hrv.py)
- **Garmin API Docs**: Consumer API (unofficial, community-documented)
- **HRV Science**: [HRV4Training](https://www.hrv4training.com/science)
- **RMSSD Methodology**: Standard measure for parasympathetic activity

## Conclusion

✅ **Garmin provides comprehensive HRV data via their API**  
✅ **Data includes summary metrics, baseline, and time-series readings**  
✅ **Integration into TrainingPlan is feasible with existing infrastructure**  
✅ **HRV can enhance recovery monitoring and training optimization**

**Recommendation**: Prioritize HRV integration as a Phase 2 feature after core activity sync is stable.
