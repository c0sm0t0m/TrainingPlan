"""
Analytics API Routes
"""
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import load_only
from pydantic import BaseModel

from src.database import get_db
from src.models.user import User
from src.models.garmin_activity import GarminActivity
from src.api.routes.auth import get_current_user
from src.utils.datetime_helpers import compare_date_for_sqlite


router = APIRouter(prefix="/analytics", tags=["analytics"])

# Summary columns only — raw_data holds FIT time_series and dominates NAS transfer time.
_ACTIVITY_ANALYTICS_LOAD = load_only(
    GarminActivity.id,
    GarminActivity.user_id,
    GarminActivity.garmin_activity_id,
    GarminActivity.activity_name,
    GarminActivity.activity_type,
    GarminActivity.start_time_local,
    GarminActivity.duration_seconds,
    GarminActivity.moving_duration_seconds,
    GarminActivity.distance_meters,
    GarminActivity.average_speed_mps,
    GarminActivity.average_hr,
    GarminActivity.max_hr,
    GarminActivity.average_power_watts,
    GarminActivity.normalized_power_watts,
    GarminActivity.calculated_tss,
    GarminActivity.training_load,
    GarminActivity.calories,
    GarminActivity.intensity_factor,
)


async def _load_activities_lite(
    db: AsyncSession,
    user_id: int,
    start_date: datetime,
    end_date: datetime,
    *,
    order_desc: bool = False,
    extra_where: tuple = (),
) -> List[GarminActivity]:
    """Load activities for analytics without raw_data / FIT blobs."""
    order = (
        GarminActivity.start_time_local.desc()
        if order_desc
        else GarminActivity.start_time_local.asc()
    )
    result = await db.execute(
        select(GarminActivity)
        .options(_ACTIVITY_ANALYTICS_LOAD)
        .where(
            GarminActivity.user_id == user_id,
            GarminActivity.start_time_local >= compare_date_for_sqlite(start_date),
            GarminActivity.start_time_local <= compare_date_for_sqlite(end_date),
            *extra_where,
        )
        .order_by(order)
    )
    return list(result.scalars().all())


async def _load_splits_by_ids(
    db: AsyncSession, activity_ids: List[int]
) -> Dict[int, List[Any]]:
    """Fetch only raw_data.splits for candidate activities (skip FIT series)."""
    if not activity_ids:
        return {}
    result = await db.execute(
        select(
            GarminActivity.id,
            GarminActivity.raw_data["splits"].label("splits"),
        ).where(GarminActivity.id.in_(activity_ids))
    )
    out: Dict[int, List[Any]] = {}
    for row in result:
        splits = row.splits
        if isinstance(splits, list):
            out[row.id] = splits
        elif isinstance(splits, str):
            import json
            try:
                parsed = json.loads(splits)
                if isinstance(parsed, list):
                    out[row.id] = parsed
            except Exception:
                pass
    return out


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


class PerformanceTrendPoint(BaseModel):
    """Weekly performance aggregate for year trending."""
    week_start: str  # YYYY-MM-DD
    activity_count: int
    # Running: pace in min/km (lower is faster). Cycling: power in watts.
    best_value: float | None = None
    avg_value: float | None = None
    rolling_avg: float | None = None  # 4-week rolling average of avg_value
    metric: str  # "pace_min_per_km" | "normalized_power_watts" | "speed_kmh"
    best_activity_id: int | None = None
    best_activity_name: str | None = None


class PerformanceTrendsResponse(BaseModel):
    """Year / multi-month performance trend."""
    sport: str
    metric: str
    metric_label: str
    data_points: List[PerformanceTrendPoint]
    date_range_start: datetime
    date_range_end: datetime
    trend_direction: str | None = None  # "improving" | "declining" | "stable" | None
    trend_pct: float | None = None  # % change first half vs second half (pace inverted)


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

    from src.utils.sport_types import matches_sport_filter

    # Lightweight first pass (no FIT blobs), then splits-only for candidates
    activities = await _load_activities_lite(
        db, current_user.id, start_date, end_date, order_desc=True
    )
    candidates = []
    for activity in activities:
        if not matches_sport_filter(activity.activity_type, sport):
            continue
        duration_min = activity.duration_seconds / 60 if activity.duration_seconds else 0
        if duration_min < 20 or not activity.average_hr:
            continue
        candidates.append(activity)

    splits_by_id = await _load_splits_by_ids(db, [a.id for a in candidates])

    # Filter for key sessions
    key_sessions = []

    for activity in candidates:
        duration_min = activity.duration_seconds / 60 if activity.duration_seconds else 0
        avg_hr = activity.average_hr
        
        # ENHANCED: Analyze lap data for high-intensity segments (e.g., 5k tests within longer runs)
        # This catches sessions where warmup/cooldown dilute the overall average HR
        lap_based_session = False
        lap_segment_hr = None
        lap_segment_duration_min = None
        lap_segment_distance_meters = None
        lap_segment_pace = None
        
        splits = splits_by_id.get(activity.id) or []
        if splits and len(splits) >= 3:
            # Look for high-intensity segments (warmup/cooldown dilute overall avg HR)
            all_segments = []
            current_segment = []

            for lap in splits:
                lap_hr = lap.get('averageHR')
                lap_duration = lap.get('duration', 0)
                lap_distance = lap.get('distance', 0)

                if lap_hr and lap_duration > 60:  # Lap must be >1 minute
                    if lap_hr >= running_threshold_hr * 0.90:
                        current_segment.append({
                            'hr': lap_hr,
                            'duration': lap_duration,
                            'distance': lap_distance
                        })
                    else:
                        if len(current_segment) >= 3:
                            all_segments.append(current_segment)
                        current_segment = []

            if len(current_segment) >= 3:
                all_segments.append(current_segment)

            best_segment = None
            best_score = 0

            for segment in all_segments:
                segment_avg_hr = sum(l['hr'] for l in segment) / len(segment)
                segment_duration = sum(l['duration'] for l in segment) / 60  # minutes

                if segment_avg_hr >= running_threshold_hr * 0.90:
                    score = segment_duration * (segment_avg_hr / running_threshold_hr)
                    if score > best_score:
                        best_score = score
                        best_segment = segment

            if best_segment:
                segment_total_duration = sum(l['duration'] for l in best_segment)
                segment_total_distance = sum(l['distance'] for l in best_segment)
                segment_avg_hr = sum(l['hr'] for l in best_segment) / len(best_segment)
                lap_segment_duration_min = segment_total_duration / 60
                lap_segment_distance_meters = segment_total_distance

                if segment_total_distance > 0:
                    segment_pace_seconds_per_km = segment_total_duration / (segment_total_distance / 1000)
                    lap_segment_pace = round(segment_pace_seconds_per_km / 60, 2)  # min/km

                if 10 <= lap_segment_duration_min <= 60:
                    lap_based_session = True
                    lap_segment_hr = int(segment_avg_hr)
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

    # GROUP BY MONTH: Keep only ONE best session per month for cleaner visualization
    monthly_best = {}

    for session in key_sessions:
        if isinstance(session.date, str):
            session_date_obj = datetime.fromisoformat(session.date).date()
        else:
            session_date_obj = session.date

        month_key = session_date_obj.strftime('%Y-%m')

        performance_score = session.intensity_factor or 0
        if session.avg_pace:
            performance_score += (1 / session.avg_pace)

        if month_key not in monthly_best or performance_score > monthly_best[month_key]['score']:
            monthly_best[month_key] = {
                'session': session,
                'score': performance_score
            }

    filtered_sessions = [data['session'] for data in monthly_best.values()]
    filtered_sessions.sort(key=lambda x: x.date if isinstance(x.date, str) else x.date.isoformat())

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

    from src.utils.sport_types import matches_sport_filter

    activities = await _load_activities_lite(
        db, current_user.id, start_date, end_date, order_desc=False
    )
    candidates = []
    for activity in activities:
        if not matches_sport_filter(activity.activity_type, sport):
            continue
        duration_min = activity.duration_seconds / 60 if activity.duration_seconds else 0
        if duration_min < 20 or not activity.distance_meters or activity.distance_meters == 0:
            continue
        if not activity.average_hr:
            continue
        candidates.append(activity)

    splits_by_id = await _load_splits_by_ids(db, [a.id for a in candidates])

    # KEY SESSION SELECTION: ONE BEST SESSION PER MONTH
    monthly_best_sessions = {}  # month_key -> best_session_data

    for activity in candidates:
        duration_min = activity.duration_seconds / 60 if activity.duration_seconds else 0

        # Extract high-intensity segments from lap data (remove warmup/cooldown)
        avg_hr = activity.average_hr
        avg_pace_min_per_km = None
        duration_for_calculation = duration_min
        lap_based_session = False

        splits = splits_by_id.get(activity.id) or []
        if splits and len(splits) >= 3:
            all_segments = []
            current_segment = []

            for lap in splits:
                lap_hr = lap.get('averageHR')
                lap_duration = lap.get('duration', 0)
                lap_distance = lap.get('distance', 0)

                if lap_hr and lap_duration > 60:
                    if lap_hr >= running_threshold_hr * 0.90:
                        current_segment.append({
                            'hr': lap_hr,
                            'duration': lap_duration,
                            'distance': lap_distance
                        })
                    else:
                        if len(current_segment) >= 3:
                            all_segments.append(current_segment)
                        current_segment = []

            if len(current_segment) >= 3:
                all_segments.append(current_segment)

            best_segment = None
            best_score = 0

            for segment in all_segments:
                segment_avg_hr = sum(l['hr'] for l in segment) / len(segment)
                segment_duration = sum(l['duration'] for l in segment) / 60

                if segment_avg_hr >= running_threshold_hr * 0.90:
                    score = segment_duration * (segment_avg_hr / running_threshold_hr)
                    if score > best_score:
                        best_score = score
                        best_segment = segment

            if best_segment:
                segment_total_duration = sum(l['duration'] for l in best_segment)
                segment_total_distance = sum(l['distance'] for l in best_segment)
                segment_avg_hr = sum(l['hr'] for l in best_segment) / len(best_segment)

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
                
                # Interpolate values (pace may be missing on either side)
                interpolated_hr = int(prev_data['threshold_hr'] * (1 - weight) + next_data['threshold_hr'] * weight)
                prev_pace = prev_data.get('threshold_pace')
                next_pace = next_data.get('threshold_pace')
                interpolated_pace = None
                if prev_pace is not None and next_pace is not None:
                    interpolated_pace = round(prev_pace * (1 - weight) + next_pace * weight, 2)
                elif prev_pace is not None:
                    interpolated_pace = prev_pace
                elif next_pace is not None:
                    interpolated_pace = next_pace

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

    activities = await _load_activities_lite(
        db,
        current_user.id,
        start_date,
        end_date,
        order_desc=False,
        extra_where=(GarminActivity.calculated_tss.isnot(None),),
    )

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


def _threshold_hr_for_sport(user: User, sport_family: str) -> Optional[int]:
    """Pick LTHR for a sport family, falling back to running then cycling."""
    if sport_family == "cycling":
        return user.cycling_threshold_hr or user.running_threshold_hr
    if sport_family == "swimming":
        return user.swim_threshold_hr or user.running_threshold_hr or user.cycling_threshold_hr
    if sport_family == "running":
        return user.running_threshold_hr or user.cycling_threshold_hr
    return user.running_threshold_hr or user.cycling_threshold_hr or user.swim_threshold_hr


@router.get("/hr-zone-distribution", response_model=HRZoneDistributionResponse)
async def get_hr_zone_distribution(
    days_back: int = 90,
    sport_filter: str = "all",  # all, swimming, cycling, running, other
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get distribution of activities across HR zones based on average HR.

    Classifies each activity with sport-specific LTHR (cycling → cycling_threshold_hr).
    Sport filter uses coarse families so Garmin types like road_biking / gravel_cycling
    are included under Bike.

    Args:
        days_back: Number of days to look back
        sport_filter: Filter by sport type (all, swimming, cycling, running, other)
        current_user: Current authenticated user
        db: Database session

    Returns:
        HR zone distribution data
    """
    from src.utils.calculations.training_zones import calculate_zones, classify_hr_to_zone
    from src.utils.sport_types import matches_sport_filter, normalize_sport

    if not current_user.max_hr:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Max HR must be configured to view HR zone distribution"
        )

    # Zone axis boundaries come from the filtered sport's LTHR (running for all/other)
    display_family = sport_filter if sport_filter in ("running", "cycling", "swimming") else "running"
    display_threshold = _threshold_hr_for_sport(current_user, display_family)
    if not display_threshold:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Threshold HR must be configured to view HR zone distribution"
        )

    hr_zones = calculate_zones('hr', 'friel', display_threshold, current_user.max_hr)
    # Cache zone sets per threshold so mixed "all" classifications stay cheap
    zones_by_threshold: Dict[int, List] = {display_threshold: hr_zones}

    end_date = datetime.now() + timedelta(days=1)
    start_date = end_date - timedelta(days=days_back)

    lite = await _load_activities_lite(
        db,
        current_user.id,
        start_date,
        end_date,
        order_desc=False,
        extra_where=(GarminActivity.average_hr.isnot(None),),
    )
    activities = [
        a for a in lite
        if matches_sport_filter(a.activity_type, sport_filter)
    ]

    zone_counts = {zone['zone']: 0 for zone in hr_zones}
    classified = 0

    for activity in activities:
        family = normalize_sport(activity.activity_type)
        thr = _threshold_hr_for_sport(current_user, family) or display_threshold
        if thr not in zones_by_threshold:
            zones_by_threshold[thr] = calculate_zones('hr', 'friel', thr, current_user.max_hr)
        zone_num = classify_hr_to_zone(activity.average_hr, zones_by_threshold[thr])
        if zone_num is not None and zone_num in zone_counts:
            zone_counts[zone_num] += 1
            classified += 1

    total_activities = classified
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


@router.get("/performance-trends", response_model=PerformanceTrendsResponse)
async def get_performance_trends(
    sport: str = "running",
    days_back: int = 365,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Weekly performance trend for run pace or bike power over a long window.

    Running: best / avg pace (min/km) from sessions ≥ 3 km with speed data.
    Cycling: best / avg normalized power (fallback average power) from sessions ≥ 20 min.
    """
    from src.utils.sport_types import matches_sport_filter

    sport_key = sport.lower().strip()
    if sport_key not in ("running", "cycling"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="sport must be 'running' or 'cycling'",
        )

    end_date = datetime.now() + timedelta(days=1)
    start_date = end_date - timedelta(days=days_back)

    lite = await _load_activities_lite(
        db, current_user.id, start_date, end_date, order_desc=False
    )
    activities = [
        a for a in lite
        if matches_sport_filter(a.activity_type, sport_key)
    ]

    # Bucket by ISO week (Monday start)
    weeks: Dict[str, list] = {}
    for activity in activities:
        st = activity.start_time_local
        if st is None:
            continue
        if isinstance(st, str):
            try:
                st = datetime.fromisoformat(st.replace("Z", "+00:00"))
            except Exception:
                continue
        week_monday = (st - timedelta(days=st.weekday())).date()
        week_key = week_monday.isoformat()
        weeks.setdefault(week_key, []).append(activity)

    if sport_key == "running":
        metric = "pace_min_per_km"
        metric_label = "Pace (min/km)"
        lower_is_better = True
    else:
        metric = "normalized_power_watts"
        metric_label = "Normalized Power (W)"
        lower_is_better = False

    # Build continuous week axis from start→end
    cursor = (start_date.date() - timedelta(days=start_date.weekday()))
    end_week = (end_date.date() - timedelta(days=end_date.weekday()))
    week_keys: List[str] = []
    while cursor <= end_week:
        week_keys.append(cursor.isoformat())
        cursor += timedelta(days=7)

    raw_points: List[PerformanceTrendPoint] = []
    for week_key in week_keys:
        acts = weeks.get(week_key, [])
        values: List[tuple] = []  # (value, activity)

        for a in acts:
            if sport_key == "running":
                dist = a.distance_meters or 0
                speed = a.average_speed_mps
                if dist < 3000 or not speed or speed <= 0:
                    continue
                pace = (1000 / speed) / 60
                if pace < 2.5 or pace > 12:  # discard GPS junk
                    continue
                values.append((pace, a))
            else:
                duration = a.duration_seconds or a.moving_duration_seconds or 0
                if duration < 20 * 60:
                    continue
                power = a.normalized_power_watts or a.average_power_watts
                if not power or power < 50 or power > 600:
                    continue
                values.append((float(power), a))

        if not values:
            raw_points.append(
                PerformanceTrendPoint(
                    week_start=week_key,
                    activity_count=0,
                    best_value=None,
                    avg_value=None,
                    rolling_avg=None,
                    metric=metric,
                )
            )
            continue

        if lower_is_better:
            best_val, best_act = min(values, key=lambda x: x[0])
        else:
            best_val, best_act = max(values, key=lambda x: x[0])
        avg_val = sum(v for v, _ in values) / len(values)

        raw_points.append(
            PerformanceTrendPoint(
                week_start=week_key,
                activity_count=len(values),
                best_value=round(best_val, 2),
                avg_value=round(avg_val, 2),
                rolling_avg=None,
                metric=metric,
                best_activity_id=best_act.id,
                best_activity_name=best_act.activity_name,
            )
        )

    # 4-week rolling average of avg_value (skip empty weeks in window)
    for i, point in enumerate(raw_points):
        window = [
            p.avg_value
            for p in raw_points[max(0, i - 3) : i + 1]
            if p.avg_value is not None
        ]
        if window:
            point.rolling_avg = round(sum(window) / len(window), 2)

    # Trend: compare first vs second half rolling averages
    with_roll = [p.rolling_avg for p in raw_points if p.rolling_avg is not None]
    trend_direction = None
    trend_pct = None
    if len(with_roll) >= 8:
        mid = len(with_roll) // 2
        first = sum(with_roll[:mid]) / mid
        second = sum(with_roll[mid:]) / (len(with_roll) - mid)
        if first > 0:
            if lower_is_better:
                # Faster pace = lower number = improvement when second < first
                change = (first - second) / first * 100
            else:
                change = (second - first) / first * 100
            trend_pct = round(change, 1)
            if abs(change) < 2:
                trend_direction = "stable"
            elif change > 0:
                trend_direction = "improving"
            else:
                trend_direction = "declining"

    return PerformanceTrendsResponse(
        sport=sport_key,
        metric=metric,
        metric_label=metric_label,
        data_points=raw_points,
        date_range_start=start_date,
        date_range_end=end_date,
        trend_direction=trend_direction,
        trend_pct=trend_pct,
    )
