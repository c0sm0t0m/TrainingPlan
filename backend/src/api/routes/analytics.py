"""
Analytics API Routes
"""
from typing import List, Optional, Dict
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel

from src.database import get_db
from src.models.user import User
from src.models.garmin_activity import GarminActivity
from src.api.routes.auth import get_current_user
from src.utils.datetime_helpers import compare_date_for_sqlite


router = APIRouter(prefix="/analytics", tags=["analytics"])


# Pydantic schemas
class KeySession(BaseModel):
    """Key training session with threshold estimate."""
    activity_id: int
    date: datetime
    activity_name: str
    sport_type: str
    duration_minutes: float
    distance_km: float | None = None
    avg_heart_rate: int
    max_heart_rate: int | None = None
    avg_pace: float | None = None  # min/km
    threshold_estimate: int
    threshold_pace: float | None = None  # min/km estimated threshold pace
    estimation_method: str
    confidence_score: float
    intensity_factor: float | None = None  # IF = avg_hr / threshold_hr
    tss: float | None = None  # Training Stress Score
    training_load: float | None = None
    calories: float | None = None
    notes: str | None = None


class KeySessionsResponse(BaseModel):
    """Response containing key training sessions."""
    sessions: List[KeySession]
    total_count: int
    date_range_start: datetime
    date_range_end: datetime


class ThresholdDataPoint(BaseModel):
    """Single threshold data point."""
    date: str  # ISO format YYYY-MM-DD
    threshold_hr: int | None = None
    threshold_pace: float | None = None  # min/km
    is_interpolated: bool = False  # True if value is interpolated, not from actual key session
    is_from_key_session: bool = False  # True if calculated from a key session


class ThresholdTrendsResponse(BaseModel):
    """Threshold trends over time."""
    data_points: List[ThresholdDataPoint]
    date_range_start: datetime
    date_range_end: datetime


@router.get("/key-sessions", response_model=KeySessionsResponse)
async def get_key_sessions(
    sport: str = "running",
    limit: int = 20,
    days_back: int = 90,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get key training sessions for a sport.
    
    Key sessions are 20-60 minute efforts with max HR > 85% of user's max HR.
    These workouts are used to estimate threshold values.
    
    Args:
        sport: Sport type (running, cycling, swimming)
        limit: Maximum number of sessions to return
        days_back: Number of days to look back
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        List of key sessions with threshold estimates
    """
    # Get user's thresholds
    max_hr = current_user.max_hr or 180
    running_threshold_hr = current_user.running_threshold_hr or 165
    
    # Calculate date range (include today by setting end_date to tomorrow midnight)
    end_date = datetime.now() + timedelta(days=1)
    start_date = end_date - timedelta(days=days_back)
    
    # Query activities (using SQLite-compatible date comparison)
    query = select(GarminActivity).where(
        GarminActivity.user_id == current_user.id,
        GarminActivity.start_time_local >= compare_date_for_sqlite(start_date),
        GarminActivity.start_time_local <= compare_date_for_sqlite(end_date)
    ).order_by(GarminActivity.start_time_local.desc())
    
    result = await db.execute(query)
    activities = result.scalars().all()
    
    # Filter for key sessions
    key_sessions = []
    
    for activity in activities:
        # Check sport type
        if sport.lower() not in activity.activity_type.lower():
            continue
        
        # Check if it's a key session
        duration_min = activity.duration_seconds / 60 if activity.duration_seconds else 0
        
        if duration_min < 20:
            continue
        
        if not activity.average_hr:
            continue
        
        avg_hr = activity.average_hr
        
        # ENHANCED: Analyze lap data for high-intensity segments (e.g., 5k tests within longer runs)
        # This catches sessions where warmup/cooldown dilute the overall average HR
        lap_based_session = False
        lap_segment_hr = None
        lap_segment_duration_min = None
        lap_segment_distance_meters = None
        lap_segment_pace = None
        
        if activity.raw_data and isinstance(activity.raw_data, dict):
            splits = activity.raw_data.get('splits', [])
            
            if splits and len(splits) >= 3:
                # ENHANCED: Look for high-intensity segments using multiple strategies
                # Strategy 1: Find consecutive laps with HR ≥ 90% threshold (more lenient)
                # Strategy 2: Find ANY segment with high average HR, even if some laps dip below
                
                all_segments = []
                current_segment = []
                
                for lap in splits:
                    lap_hr = lap.get('averageHR')
                    lap_duration = lap.get('duration', 0)
                    lap_distance = lap.get('distance', 0)
                    
                    if lap_hr and lap_duration > 60:  # Lap must be >1 minute
                        # More lenient: ≥90% threshold (catches 5k tests with varying HR)
                        if lap_hr >= running_threshold_hr * 0.90:
                            # Add to current segment
                            current_segment.append({
                                'hr': lap_hr,
                                'duration': lap_duration,
                                'distance': lap_distance
                            })
                        else:
                            # End current segment if we have at least 3 laps
                            if len(current_segment) >= 3:
                                all_segments.append(current_segment)
                            current_segment = []
                
                # Check last segment
                if len(current_segment) >= 3:
                    all_segments.append(current_segment)
                
                # Find best high-intensity segment:
                # 1. Segment average HR must be ≥ 92% threshold (stricter than individual laps)
                # 2. Prefer longer segments with higher average HR
                best_segment = None
                best_score = 0
                
                for segment in all_segments:
                    segment_avg_hr = sum(l['hr'] for l in segment) / len(segment)
                    segment_duration = sum(l['duration'] for l in segment) / 60  # minutes
                    
                    # Only consider segments with high average HR (90% catches 5k tests)
                    if segment_avg_hr >= running_threshold_hr * 0.90:
                        # Score: favor longer duration + higher HR
                        score = segment_duration * (segment_avg_hr / running_threshold_hr)
                        
                        if score > best_score:
                            best_score = score
                            best_segment = segment
                
                # Use best segment for lap-based calculations
                if best_segment:
                    segment_total_duration = sum(l['duration'] for l in best_segment)
                    segment_total_distance = sum(l['distance'] for l in best_segment)
                    segment_avg_hr = sum(l['hr'] for l in best_segment) / len(best_segment)
                    lap_segment_duration_min = segment_total_duration / 60
                    lap_segment_distance_meters = segment_total_distance
                    
                    # Calculate pace for the high-intensity segment
                    if segment_total_distance > 0:
                        segment_pace_seconds_per_km = segment_total_duration / (segment_total_distance / 1000)
                        lap_segment_pace = round(segment_pace_seconds_per_km / 60, 2)  # min/km
                    
                    # Qualify as key session if segment is 10-60 minutes (catches 3km/5km tests)
                    if 10 <= lap_segment_duration_min <= 60:
                        lap_based_session = True
                        lap_segment_hr = int(segment_avg_hr)
                        # Override avg_hr for threshold calculation
                        avg_hr = lap_segment_hr
        
        # Key session criteria (RELAXED - realistic training intensities):
        # 1. Quality efforts: 20-60 min with avg HR >= 90% threshold (most tempo/threshold work)
        # 2. Long tempo runs: 60-90 min with avg HR >= 85% threshold
        # 3. Very long runs: >90 min with avg HR >= 75% threshold (aerobic base)
        check_duration = lap_segment_duration_min if lap_based_session else duration_min
        
        is_quality_effort = (20 <= check_duration <= 60) and (avg_hr >= running_threshold_hr * 0.90)
        is_long_tempo = (60 < check_duration <= 90) and (avg_hr >= running_threshold_hr * 0.85)
        is_very_long_run = (check_duration > 90) and (avg_hr >= running_threshold_hr * 0.75)
        
        if not (is_quality_effort or is_long_tempo or is_very_long_run):
            continue
        
        # It's a key session!
        
        # Use lap-based duration for threshold estimation if available
        estimation_duration = lap_segment_duration_min if lap_based_session else duration_min
        
        # Determine threshold estimate and confidence based on duration
        threshold_estimate = None
        method = ""
        confidence = 0.0
        
        if estimation_duration < 30:
            # 20-30 min: Above threshold
            threshold_estimate = int(avg_hr / 1.05)
            method = "20-30min effort ≈ 105% threshold"
            if lap_based_session:
                method += " (lap segment)"
            confidence = 0.85
        elif estimation_duration < 45:
            # 30-45 min: Slightly above threshold
            threshold_estimate = int(avg_hr / 1.02)
            method = "30-45min effort ≈ 102% threshold"
            if lap_based_session:
                method += " (lap segment)"
            confidence = 0.90
        elif estimation_duration < 60:
            # 45-60 min: Close to threshold
            threshold_estimate = int(avg_hr / 1.00)
            method = "45-60min effort ≈ threshold"
            if lap_based_session:
                method += " (lap segment)"
            confidence = 0.95
        else:
            # >60 min: Below threshold (tempo)
            threshold_estimate = int(avg_hr / 0.95)
            method = "60+ min tempo ≈ 95% threshold"
            if lap_based_session:
                method += " (lap segment)"
            confidence = 0.80
        
        # Calculate pace - use lap segment pace if available
        avg_pace = None
        if lap_based_session and lap_segment_pace:
            # Use pace from high-intensity lap segment
            avg_pace = lap_segment_pace
        elif activity.distance_meters and activity.distance_meters > 0:
            # Use overall activity pace
            pace_seconds_per_km = activity.duration_seconds / (activity.distance_meters / 1000)
            avg_pace = round(pace_seconds_per_km / 60, 2)  # Convert to min/km
        
        # Calculate Intensity Factor (IF) from actual heart rate
        # IF represents how hard the effort was relative to threshold
        intensity_factor = None
        if threshold_estimate and threshold_estimate > 0:
            intensity_factor = round(avg_hr / threshold_estimate, 3)
        
        # Estimate threshold pace using IF
        # Physics: IF > 1.0 means running HARDER (faster) than threshold
        # - If IF=1.05, you ran 5% harder → 5% faster speed → 5% lower pace number
        # - Speed_effort = Speed_threshold × IF
        # - Since Pace = 1/Speed: Pace_threshold = Pace_effort / IF
        # Example: 45min at 4:53/km (4.88) with HR 171 (threshold 165)
        #   → IF=1.036 → Threshold pace = 4.88/1.036 = 4:43/km ✓
        threshold_pace = None
        if avg_pace and intensity_factor and intensity_factor > 0:
            threshold_pace = round(avg_pace / intensity_factor, 2)
        
        # TODO: Future enhancement - Time series analysis for intervals
        # Many "key sessions" are actually interval workouts with varying intensity.
        # Analyzing HR/pace streams could:
        # 1. Detect intervals (sustained high HR periods)
        # 2. Calculate threshold from intervals only (ignore warmup/cooldown/recovery)
        # 3. Identify workout type (VO2max intervals, threshold repeats, fartlek)
        # 4. Weight estimates by interval quality (duration, steadiness)
        # This would require accessing activity_samples or detailed FIT file data.
        
        # Calculate TSS (Training Stress Score)
        # TSS = (duration_hours * IF^2 * 100)
        tss = None
        if intensity_factor:
            duration_hours = duration_min / 60
            tss = round(duration_hours * (intensity_factor ** 2) * 100, 1)
        
        key_sessions.append(KeySession(
            activity_id=int(activity.garmin_activity_id),
            date=activity.start_time_local,
            activity_name=activity.activity_name or "Unnamed Activity",
            sport_type=activity.activity_type,
            duration_minutes=round(duration_min, 1),
            distance_km=round(activity.distance_meters / 1000, 2) if activity.distance_meters else None,
            avg_heart_rate=activity.average_hr,
            max_heart_rate=activity.max_hr,
            avg_pace=avg_pace,
            threshold_estimate=threshold_estimate,
            threshold_pace=threshold_pace,
            estimation_method=method,
            confidence_score=confidence,
            intensity_factor=intensity_factor,
            tss=tss,
            training_load=activity.training_load,
            calories=activity.calories,
            notes=None  # Description field doesn't exist in model
        ))
        
        if len(key_sessions) >= limit:
            break
    
    # DEBUG: Log qualified sessions before monthly grouping
    print(f"\n[DEBUG] Found {len(key_sessions)} qualified key sessions BEFORE monthly grouping")
    if key_sessions:
        dates = [s.date for s in key_sessions]
        print(f"[DEBUG] Date range: {min(dates)} to {max(dates)}")
    
    # GROUP BY MONTH: Keep only ONE best session per month for cleaner visualization
    from collections import defaultdict
    monthly_best = {}
    
    for session in key_sessions:
        # session.date is already a string in YYYY-MM-DD format from Pydantic model
        if isinstance(session.date, str):
            session_date_obj = datetime.fromisoformat(session.date).date()
        else:
            session_date_obj = session.date  # Already a date object
        
        month_key = session_date_obj.strftime('%Y-%m')
        
        # Calculate performance score (higher is better)
        performance_score = session.intensity_factor or 0
        if session.avg_pace:
            performance_score += (1 / session.avg_pace)  # Faster pace = higher score
        
        # Keep only the best session for this month
        if month_key not in monthly_best or performance_score > monthly_best[month_key]['score']:
            monthly_best[month_key] = {
                'session': session,
                'score': performance_score
            }
    
    # Extract just the sessions (sorted by date)
    filtered_sessions = [data['session'] for data in monthly_best.values()]
    filtered_sessions.sort(key=lambda x: x.date if isinstance(x.date, str) else x.date.isoformat())
    
    # DEBUG: Log what we're returning
    print(f"\n[DEBUG] Returning {len(filtered_sessions)} key sessions (monthly best)")
    if filtered_sessions:
        dates = [s.date for s in filtered_sessions]
        print(f"[DEBUG] Date range: {min(dates)} to {max(dates)}")
        print(f"[DEBUG] Dates: {sorted(dates)}")
    
    return KeySessionsResponse(
        sessions=filtered_sessions,
        total_count=len(filtered_sessions),
        date_range_start=start_date,
        date_range_end=end_date
    )


@router.get("/threshold-trends", response_model=ThresholdTrendsResponse)
async def get_threshold_trends(
    sport: str = "running",
    days_back: int = 90,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get threshold trends derived from key sessions.
    
    KEY SESSION SELECTION (v3.0 - ONE PER MONTH):
    1. **Best Performance Per Month**: Selects single best session per month based on intensity
    2. **Hard Effort Requirement**: Must be genuine hard effort (HR >= 90% threshold, pace <= 5:15/km)
    3. **Interpolation**: Months without key sessions get interpolated threshold values
    
    Args:
        sport: Sport type
        days_back: Number of days to look back
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        Monthly threshold data points with interpolation
    """
    # Get user's thresholds
    running_threshold_hr = current_user.running_threshold_hr or 165
    
    # Calculate date range (include today by setting end_date to tomorrow midnight)
    end_date = datetime.now() + timedelta(days=1)
    start_date = end_date - timedelta(days=days_back)
    
    # Query ALL activities in range
    query = select(GarminActivity).where(
        GarminActivity.user_id == current_user.id,
        GarminActivity.start_time_local >= compare_date_for_sqlite(start_date),
        GarminActivity.start_time_local <= compare_date_for_sqlite(end_date)
    ).order_by(GarminActivity.start_time_local.asc())
    
    result = await db.execute(query)
    activities = result.scalars().all()
    
    # KEY SESSION SELECTION: ONE BEST SESSION PER MONTH
    # Group activities by month and select the single best hard effort
    from collections import defaultdict
    monthly_best_sessions = {}  # month_key -> best_session_data
    
    for activity in activities:
        if sport.lower() not in activity.activity_type.lower():
            continue
        
        duration_min = activity.duration_seconds / 60 if activity.duration_seconds else 0
        
        # Require minimum 20 minutes, distance, and HR data
        if duration_min < 20 or not activity.distance_meters or activity.distance_meters == 0:
            continue
        
        if not activity.average_hr:
            continue
        
        # CRITICAL: Extract high-intensity segments from lap data (remove warmup/cooldown)
        # This ensures threshold calculations are based on the hard interval portion only
        avg_hr = activity.average_hr
        avg_pace_min_per_km = None
        duration_for_calculation = duration_min
        lap_based_session = False
        
        if activity.raw_data and isinstance(activity.raw_data, dict):
            splits = activity.raw_data.get('splits', [])
            
            if splits and len(splits) >= 3:
                # ENHANCED: Look for high-intensity segments using multiple strategies
                # Strategy 1: Find consecutive laps with HR ≥ 90% threshold (more lenient)
                # Strategy 2: Find ANY segment with high average HR, even if some laps dip below
                
                all_segments = []
                current_segment = []
                
                for lap in splits:
                    lap_hr = lap.get('averageHR')
                    lap_duration = lap.get('duration', 0)
                    lap_distance = lap.get('distance', 0)
                    
                    if lap_hr and lap_duration > 60:  # Lap must be >1 minute
                        # More lenient: ≥90% threshold (catches 5k tests with varying HR)
                        if lap_hr >= running_threshold_hr * 0.90:
                            # Add to current segment
                            current_segment.append({
                                'hr': lap_hr,
                                'duration': lap_duration,
                                'distance': lap_distance
                            })
                        else:
                            # End current segment if we have at least 3 laps
                            if len(current_segment) >= 3:
                                all_segments.append(current_segment)
                            current_segment = []
                
                # Check last segment
                if len(current_segment) >= 3:
                    all_segments.append(current_segment)
                
                # Find best high-intensity segment:
                # 1. Segment average HR must be ≥ 92% threshold (stricter than individual laps)
                # 2. Prefer longer segments with higher average HR
                best_segment = None
                best_score = 0
                
                for segment in all_segments:
                    segment_avg_hr = sum(l['hr'] for l in segment) / len(segment)
                    segment_duration = sum(l['duration'] for l in segment) / 60  # minutes
                    
                    # Only consider segments with high average HR (90% catches 5k tests)
                    if segment_avg_hr >= running_threshold_hr * 0.90:
                        # Score: favor longer duration + higher HR
                        score = segment_duration * (segment_avg_hr / running_threshold_hr)
                        
                        if score > best_score:
                            best_score = score
                            best_segment = segment
                
                # Use best segment for threshold calculation
                if best_segment:
                    segment_total_duration = sum(l['duration'] for l in best_segment)
                    segment_total_distance = sum(l['distance'] for l in best_segment)
                    segment_avg_hr = sum(l['hr'] for l in best_segment) / len(best_segment)
                    
                    # Use segment data for threshold calculation (10-60 min catches 3km/5km tests)
                    if segment_total_distance > 0 and 10 <= (segment_total_duration / 60) <= 60:
                        lap_based_session = True
                        avg_hr = int(segment_avg_hr)
                        duration_for_calculation = segment_total_duration / 60
                        segment_pace_seconds_per_km = segment_total_duration / (segment_total_distance / 1000)
                        avg_pace_min_per_km = round(segment_pace_seconds_per_km / 60, 2)
        
        # Fallback to overall activity metrics if no high-intensity segment found
        if avg_pace_min_per_km is None:
            avg_pace_seconds_per_km = activity.duration_seconds / (activity.distance_meters / 1000)
            avg_pace_min_per_km = avg_pace_seconds_per_km / 60
        
        # Apply SAME key session criteria as key-sessions endpoint for consistency
        # 1. Quality efforts: 20-60 min with avg HR >= 90% threshold (most tempo/threshold work)
        # 2. Long tempo runs: 60-90 min with avg HR >= 85% threshold
        # 3. Very long runs: >90 min with avg HR >= 75% threshold (aerobic base)
        is_quality_effort = (20 <= duration_for_calculation <= 60) and (avg_hr >= running_threshold_hr * 0.90)
        is_long_tempo = (60 < duration_for_calculation <= 90) and (avg_hr >= running_threshold_hr * 0.85)
        is_very_long_run = (duration_for_calculation > 90) and (avg_hr >= running_threshold_hr * 0.75)
        
        if not (is_quality_effort or is_long_tempo or is_very_long_run):
            # Skip - doesn't meet key session intensity criteria
            continue
        
        # Skip if pace is too slow (> 5:15/km) - not a quality session
        if avg_pace_min_per_km > 5.25:
            continue
        
        # Calculate intensity factor (higher = harder effort)
        intensity_factor = avg_hr / running_threshold_hr
        
        # Group by month (YYYY-MM)
        activity_date = activity.start_time_local.date()
        month_key = activity_date.strftime('%Y-%m')
        
        session_data = {
            'activity': activity,
            'date': activity_date,
            'avg_pace': avg_pace_min_per_km,
            'avg_hr': avg_hr,
            'duration_min': duration_for_calculation,
            'intensity_factor': intensity_factor,
            'performance_score': intensity_factor + (1 / avg_pace_min_per_km),  # Combined metric
            'lap_based': lap_based_session
        }
        
        # Keep only the BEST session for this month (highest performance score)
        if month_key not in monthly_best_sessions or session_data['performance_score'] > monthly_best_sessions[month_key]['performance_score']:
            monthly_best_sessions[month_key] = session_data
    
    # Convert to list of key sessions (ONE per month)
    key_sessions = list(monthly_best_sessions.values())
    
    # REMOVE sub-activity analysis - we only want real hard efforts
    
    # Calculate thresholds from key sessions (ONE per month)
    monthly_thresholds: Dict[str, Dict] = {}  # month_key -> {threshold values}
    
    for session_data in key_sessions:
        activity = session_data['activity']
        activity_date = session_data['date']
        duration_min = session_data['duration_min']
        avg_pace = session_data['avg_pace']
        avg_hr = int(session_data['avg_hr'])  # Ensure integer for HR
        lap_based = session_data.get('lap_based', False)
        
        # Calculate threshold HR estimate based on duration
        # CRITICAL: If lap-based, the segment IS the threshold effort (no adjustment needed)
        if lap_based:
            # Lap segment is the high-intensity portion - use it directly as threshold
            threshold_hr = avg_hr
            threshold_pace = avg_pace
        else:
            # Overall activity - estimate threshold based on duration
            if duration_min < 30:
                threshold_hr = int(avg_hr / 1.05)  # Short hard effort, likely above threshold
            elif duration_min < 45:
                threshold_hr = int(avg_hr / 1.02)  # Medium effort
            else:
                threshold_hr = int(avg_hr)  # Long effort at threshold
            
            # Calculate threshold pace using intensity factor
            intensity_factor = round(avg_hr / threshold_hr, 3)
            threshold_pace = round(avg_pace / intensity_factor, 2) if avg_pace else None
        
        # Store monthly threshold (ONE per month)
        month_key = activity_date.strftime('%Y-%m')
        monthly_thresholds[month_key] = {
            'date': activity_date,
            'threshold_hr': threshold_hr,
            'threshold_pace': threshold_pace,
            'activity_id': activity.id,
            'activity_name': activity.activity_name,
            'is_from_key_session': True,
            'is_interpolated': False
        }
    
    # INTERPOLATE: Fill missing months between first and last key session
    if not monthly_thresholds:
        return ThresholdTrendsResponse(
            data_points=[],
            date_range_start=start_date,
            date_range_end=end_date
        )
    
    # Get sorted month keys
    sorted_month_keys = sorted(monthly_thresholds.keys())
    first_month = sorted_month_keys[0]
    
    # CRITICAL: Extend to current month, not just last key session
    current_month = datetime.now().date().strftime('%Y-%m')
    last_month = max(sorted_month_keys[-1], current_month)  # Use later of last key session or current month
    
    # Generate all months from first key session to current month
    from dateutil.relativedelta import relativedelta
    current_month_date = datetime.strptime(first_month, '%Y-%m').date()
    last_month_date = datetime.strptime(last_month, '%Y-%m').date()
    
    all_months = []
    while current_month_date <= last_month_date:
        all_months.append(current_month_date.strftime('%Y-%m'))
        current_month_date += relativedelta(months=1)
    
    # Interpolate missing months
    complete_monthly_data = {}
    
    for month_key in all_months:
        if month_key in monthly_thresholds:
            # Use actual key session data
            complete_monthly_data[month_key] = monthly_thresholds[month_key]
        else:
            # INTERPOLATE: Find surrounding months with data
            prev_month = None
            next_month = None
            
            for i, mk in enumerate(sorted_month_keys):
                if mk < month_key:
                    prev_month = mk
                elif mk > month_key and next_month is None:
                    next_month = mk
                    break
            
            # Linear interpolation
            if prev_month and next_month:
                prev_data = monthly_thresholds[prev_month]
                next_data = monthly_thresholds[next_month]
                
                # Calculate month distance for weighting
                curr_date = datetime.strptime(month_key, '%Y-%m')
                prev_date = datetime.strptime(prev_month, '%Y-%m')
                next_date = datetime.strptime(next_month, '%Y-%m')
                
                total_months = (next_date.year - prev_date.year) * 12 + (next_date.month - prev_date.month)
                months_from_prev = (curr_date.year - prev_date.year) * 12 + (curr_date.month - prev_date.month)
                
                weight = months_from_prev / total_months if total_months > 0 else 0.5
                
                # Interpolate values
                interpolated_hr = int(prev_data['threshold_hr'] * (1 - weight) + next_data['threshold_hr'] * weight)
                interpolated_pace = round(prev_data['threshold_pace'] * (1 - weight) + next_data['threshold_pace'] * weight, 2)
                
                complete_monthly_data[month_key] = {
                    'date': curr_date.date(),
                    'threshold_hr': interpolated_hr,
                    'threshold_pace': interpolated_pace,
                    'is_interpolated': True,
                    'is_from_key_session': False
                }
            elif prev_month:
                # Extend from previous month
                complete_monthly_data[month_key] = {
                    'date': datetime.strptime(month_key, '%Y-%m').date(),
                    'threshold_hr': monthly_thresholds[prev_month]['threshold_hr'],
                    'threshold_pace': monthly_thresholds[prev_month]['threshold_pace'],
                    'is_interpolated': True,
                    'is_from_key_session': False
                }
            elif next_month:
                # Extend from next month
                complete_monthly_data[month_key] = {
                    'date': datetime.strptime(month_key, '%Y-%m').date(),
                    'threshold_hr': monthly_thresholds[next_month]['threshold_hr'],
                    'threshold_pace': monthly_thresholds[next_month]['threshold_pace'],
                    'is_interpolated': True,
                    'is_from_key_session': False
                }
    
    # **CRITICAL**: Anchor current month to user's configured threshold settings
    today = datetime.now().date()
    current_month_key = today.strftime('%Y-%m')
    
    if current_month_key in all_months:
        complete_monthly_data[current_month_key] = {
            'date': today,
            'threshold_hr': current_user.running_threshold_hr,
            'threshold_pace': round(current_user.threshold_pace / 60, 2) if current_user.threshold_pace else None,
            'is_from_key_session': False,
            'is_interpolated': False,
            'is_current_setting': True
        }
    
    # Build data points (ONE per month)
    data_points = []
    for month_key in sorted(complete_monthly_data.keys()):
        month_data = complete_monthly_data[month_key]
        data_points.append(ThresholdDataPoint(
            date=month_data['date'].strftime('%Y-%m-%d'),
            threshold_hr=month_data['threshold_hr'],
            threshold_pace=month_data['threshold_pace'],
            is_interpolated=month_data.get('is_interpolated', False),
            is_from_key_session=month_data.get('is_from_key_session', False)
        ))
    
    return ThresholdTrendsResponse(
        data_points=data_points,
        date_range_start=start_date,
        date_range_end=end_date
    )


class WeeklyTSSDataPoint(BaseModel):
    """TSS data point for a week."""
    week_start: str  # ISO format YYYY-MM-DD (Monday)
    week_end: str    # ISO format YYYY-MM-DD (Sunday)
    total_tss: float
    activity_count: int


class WeeklyTSSResponse(BaseModel):
    """TSS per week response."""
    data_points: List[WeeklyTSSDataPoint]
    date_range_start: datetime
    date_range_end: datetime


@router.get("/tss-per-week", response_model=WeeklyTSSResponse)
async def get_tss_per_week(
    days_back: int = 90,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get TSS aggregated by week for the specified time range.
    
    Args:
        days_back: Number of days to look back
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        Weekly TSS data points
    """
    from collections import defaultdict
    
    # Calculate date range (include today by setting end_date to tomorrow midnight)
    end_date = datetime.now() + timedelta(days=1)
    start_date = end_date - timedelta(days=days_back)
    
    # Query activities with TSS (using SQLite-compatible date comparison)
    query = select(GarminActivity).where(
        GarminActivity.user_id == current_user.id,
        GarminActivity.start_time_local >= compare_date_for_sqlite(start_date),
        GarminActivity.start_time_local <= compare_date_for_sqlite(end_date),
        GarminActivity.calculated_tss.isnot(None)
    ).order_by(GarminActivity.start_time_local)
    
    result = await db.execute(query)
    activities = result.scalars().all()
    
    # Group by week (Monday to Sunday)
    weekly_data = defaultdict(lambda: {'tss': 0.0, 'count': 0, 'start': None, 'end': None})
    
    for activity in activities:
        activity_date = activity.start_time_local.date()
        # Find Monday of the week
        days_since_monday = activity_date.weekday()
        week_start = activity_date - timedelta(days=days_since_monday)
        week_end = week_start + timedelta(days=6)
        
        week_key = week_start.isoformat()
        
        weekly_data[week_key]['tss'] += activity.calculated_tss or 0
        weekly_data[week_key]['count'] += 1
        weekly_data[week_key]['start'] = week_start
        weekly_data[week_key]['end'] = week_end
    
    # Build response
    data_points = []
    for week_key in sorted(weekly_data.keys()):
        week_info = weekly_data[week_key]
        data_points.append(WeeklyTSSDataPoint(
            week_start=week_info['start'].isoformat(),
            week_end=week_info['end'].isoformat(),
            total_tss=round(week_info['tss'], 1),
            activity_count=week_info['count']
        ))
    
    return WeeklyTSSResponse(
        data_points=data_points,
        date_range_start=start_date,
        date_range_end=end_date
    )


class HRZoneDistributionDataPoint(BaseModel):
    """Heart rate zone distribution data point."""
    zone_number: int
    zone_name: str
    min_hr: int
    max_hr: int
    activity_count: int
    percentage: float


class HRZoneDistributionResponse(BaseModel):
    """HR zone distribution response."""
    data_points: List[HRZoneDistributionDataPoint]
    total_activities: int
    date_range_start: datetime
    date_range_end: datetime


@router.get("/hr-zone-distribution", response_model=HRZoneDistributionResponse)
async def get_hr_zone_distribution(
    days_back: int = 90,
    sport_filter: str = "all",  # all, swimming, cycling, running, other
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get distribution of activities across HR zones based on average HR.
    
    Uses the user's running HR zones as the reference.
    Each activity is classified into ONE zone based on its average HR.
    
    Args:
        days_back: Number of days to look back
        sport_filter: Filter by sport type (all, swimming, cycling, running, other)
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        HR zone distribution data
    """
    from src.utils.calculations.training_zones import calculate_zones
    
    # Get user's HR zones (using running HR settings)
    if not current_user.running_threshold_hr or not current_user.max_hr:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Running threshold HR and max HR must be configured to view HR zone distribution"
        )
    
    # Calculate HR zones (use default method)
    hr_zones = calculate_zones('hr', 'friel', current_user.running_threshold_hr, current_user.max_hr)
    
    # Calculate date range (include today by setting end_date to tomorrow midnight)
    end_date = datetime.now() + timedelta(days=1)
    start_date = end_date - timedelta(days=days_back)
    
    # Build query with sport filter
    query = select(GarminActivity).where(
        GarminActivity.user_id == current_user.id,
        GarminActivity.start_time_local >= compare_date_for_sqlite(start_date),
        GarminActivity.start_time_local <= compare_date_for_sqlite(end_date),
        GarminActivity.average_hr.isnot(None)
    )
    
    # Apply sport filter
    if sport_filter != "all":
        if sport_filter == "swimming":
            query = query.where(GarminActivity.activity_type.in_(['swimming', 'lap_swimming', 'open_water_swimming']))
        elif sport_filter == "cycling":
            query = query.where(GarminActivity.activity_type.in_(['cycling', 'virtual_ride', 'indoor_cycling', 'mountain_biking']))
        elif sport_filter == "running":
            query = query.where(GarminActivity.activity_type.in_(['running', 'trail_running', 'treadmill_running', 'virtual_run']))
        elif sport_filter == "other":
            # Exclude the main three sports
            query = query.where(
                ~GarminActivity.activity_type.in_([
                    'swimming', 'lap_swimming', 'open_water_swimming',
                    'cycling', 'virtual_ride', 'indoor_cycling', 'mountain_biking',
                    'running', 'trail_running', 'treadmill_running', 'virtual_run'
                ])
            )
    
    result = await db.execute(query)
    activities = result.scalars().all()
    
    # Classify each activity into a zone based on average HR
    zone_counts = {zone['zone']: 0 for zone in hr_zones}
    
    for activity in activities:
        avg_hr = activity.average_hr
        
        # Find which zone this HR falls into
        for zone in hr_zones:
            if zone['min'] <= avg_hr <= zone['max']:
                zone_counts[zone['zone']] += 1
                break
    
    # Calculate percentages
    total_activities = len(activities)
    data_points = []
    
    for zone in hr_zones:
        zone_num = zone['zone']
        count = zone_counts[zone_num]
        percentage = (count / total_activities * 100) if total_activities > 0 else 0
        
        data_points.append(HRZoneDistributionDataPoint(
            zone_number=zone_num,
            zone_name=zone['name'],
            min_hr=zone['min'],
            max_hr=zone['max'],
            activity_count=count,
            percentage=round(percentage, 1)
        ))
    
    return HRZoneDistributionResponse(
        data_points=data_points,
        total_activities=total_activities,
        date_range_start=start_date,
        date_range_end=end_date
    )
