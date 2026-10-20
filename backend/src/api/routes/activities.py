"""
Activity Detail API Routes

Endpoints for viewing and managing individual activity details including:
- Full activity metadata
- GPS track points
- Time-series data (HR, power, pace)
- Lap splits
- Activity editing
"""
from typing import List, Optional, Dict, Any
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel, Field

from src.database import get_db
from src.models.user import User
from src.models.garmin_activity import GarminActivity
from src.models.training_plan import TrainingPlan, Workout
from src.api.routes.auth import get_current_user
from src.services.activity_match_service import (
    confirm_match,
    get_workout_linked_to_activity,
    link_manually,
    unlink_workout,
)
from src.services.activity_track_service import (
    ensure_time_series,
    extract_track_points,
)
from src.services.plan_vs_actual import build_plan_vs_actual
from src.utils.calculations.tss_calculator import display_load_for_activity


router = APIRouter(prefix="/activities", tags=["activities"])


# Pydantic schemas
class PlanActualRow(BaseModel):
    """One suggested-vs-actual metric."""
    label: str
    planned: Optional[str] = None
    actual: Optional[str] = None
    delta: Optional[str] = None
    tone: str = "neutral"  # high | low | ok | neutral


class MatchedWorkoutInfo(BaseModel):
    """Planned workout linked to this performed activity."""
    id: int
    training_plan_id: int
    title: str
    date: str
    sport_type: str
    duration_minutes: Optional[int] = None
    distance_km: Optional[float] = None
    target_tss: Optional[int] = None
    intensity_zone: Optional[str] = None
    match_confidence: Optional[float] = None
    match_status: Optional[str] = None
    match_needs_review: bool = False
    performed_on_planned_day: bool = True
    actual_date: Optional[str] = None
    comparison: List[PlanActualRow] = []


class ActivityDetailResponse(BaseModel):
    """Full activity detail response."""
    id: int
    garmin_activity_id: str
    activity_name: str
    activity_type: str
    sport_type_id: Optional[int] = None
    
    # Timing
    start_time_local: datetime
    start_time_gmt: datetime
    date: str  # YYYY-MM-DD format
    duration_seconds: Optional[float] = None
    elapsed_duration_seconds: Optional[float] = None
    moving_duration_seconds: Optional[float] = None
    
    # Distance & Speed
    distance_meters: Optional[float] = None
    average_speed_mps: Optional[float] = None
    max_speed_mps: Optional[float] = None
    
    # Elevation
    elevation_gain_meters: Optional[float] = None
    elevation_loss_meters: Optional[float] = None
    min_elevation_meters: Optional[float] = None
    max_elevation_meters: Optional[float] = None
    
    # Heart Rate
    average_hr: Optional[int] = None
    max_hr: Optional[int] = None
    
    # Power (Cycling)
    average_power_watts: Optional[float] = None
    max_power_watts: Optional[float] = None
    normalized_power_watts: Optional[float] = None
    threshold_power_watts: Optional[float] = None
    
    # Training Metrics
    calculated_tss: Optional[float] = None
    training_load: Optional[float] = None
    intensity_factor: Optional[float] = None
    vo2_max: Optional[float] = None
    aerobic_training_effect: Optional[float] = None
    anaerobic_training_effect: Optional[float] = None
    
    # Other
    calories: Optional[int] = None
    steps: Optional[int] = None
    average_cadence: Optional[float] = None
    location_name: Optional[str] = None
    
    # Flags
    has_polyline: bool = False
    manual_activity: bool = False

    # Planned workout link
    matched_workout: Optional[MatchedWorkoutInfo] = None
    
    # Metadata
    synced_at: datetime
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class LinkWorkoutRequest(BaseModel):
    workout_id: int = Field(..., description="Planned workout id to link")


class TrackPoint(BaseModel):
    """GPS track point."""
    lat: float
    lng: float
    ele: Optional[float] = None  # elevation in meters
    timestamp: Optional[datetime] = None


class ActivityTrackResponse(BaseModel):
    """GPS track response."""
    activity_id: int
    track_points: List[TrackPoint]
    total_points: int
    has_elevation: bool


class TimeSeriesData(BaseModel):
    """Time-series data for charts (parallel arrays; None = missing sample)."""
    timestamps: List[datetime]
    distance_meters: Optional[List[Optional[float]]] = None
    pace_min_per_km: Optional[List[Optional[float]]] = None
    heart_rate_bpm: Optional[List[Optional[int]]] = None
    power_watts: Optional[List[Optional[float]]] = None
    cadence: Optional[List[Optional[float]]] = None
    elevation_meters: Optional[List[Optional[float]]] = None
    speed_mps: Optional[List[Optional[float]]] = None


class ActivityStreamsResponse(BaseModel):
    """Time-series streams response."""
    activity_id: int
    streams: TimeSeriesData
    total_samples: int


class LapSplit(BaseModel):
    """Lap/split data."""
    lap_number: int
    distance_meters: float
    duration_seconds: float
    average_speed_mps: Optional[float] = None
    average_hr: Optional[int] = None
    max_hr: Optional[int] = None
    average_power: Optional[float] = None
    elevation_gain_meters: Optional[float] = None
    elevation_loss_meters: Optional[float] = None
    average_cadence: Optional[float] = None


class ActivitySplitsResponse(BaseModel):
    """Lap splits response."""
    activity_id: int
    splits: List[LapSplit]
    total_laps: int


class ActivityUpdate(BaseModel):
    """Activity update request."""
    activity_name: Optional[str] = Field(None, min_length=1, max_length=200)
    notes: Optional[str] = Field(None, max_length=5000)
    # Future: equipment_id, custom fields


class ActivityListItem(BaseModel):
    """Activity list item (summary)."""
    id: int
    activity_name: str
    activity_type: str
    start_time_local: datetime
    date: str
    duration_seconds: Optional[float] = None
    distance_meters: Optional[float] = None
    calculated_tss: Optional[float] = None
    intensity_factor: Optional[float] = None
    average_hr: Optional[int] = None
    location_name: Optional[str] = None
    
    class Config:
        from_attributes = True


class ActivityListResponse(BaseModel):
    """Paginated activity list response."""
    activities: List[ActivityListItem]
    total: int
    page: int
    page_size: int


def _matched_workout_info(
    workout: Optional[Workout],
    activity: Optional[GarminActivity] = None,
    ftp: Optional[float] = None,
    run_threshold_sec: Optional[float] = None,
) -> Optional[MatchedWorkoutInfo]:
    if not workout:
        return None
    comparison = (
        build_plan_vs_actual(
            workout,
            activity,
            ftp=ftp,
            run_threshold_sec=run_threshold_sec,
        )
        if activity is not None
        else {"performed_on_planned_day": True, "actual_date": None, "rows": []}
    )
    return MatchedWorkoutInfo(
        id=workout.id,
        training_plan_id=workout.training_plan_id,
        title=workout.title,
        date=workout.date.isoformat() if workout.date else "",
        sport_type=workout.sport_type,
        duration_minutes=workout.duration_minutes,
        distance_km=workout.distance_km,
        target_tss=workout.target_tss,
        intensity_zone=workout.intensity_zone,
        match_confidence=workout.match_confidence,
        match_status=workout.match_status,
        match_needs_review=workout.match_status == "needs_review",
        performed_on_planned_day=bool(comparison["performed_on_planned_day"]),
        actual_date=comparison["actual_date"],
        comparison=[PlanActualRow(**row) for row in comparison["rows"]],
    )


def _cadence_from_raw(activity: GarminActivity) -> tuple[Optional[float], Optional[float]]:
    """Resolve avg/max cadence from columns, Garmin summary keys, or FIT stream stats."""
    avg = activity.average_cadence
    mx = activity.max_cadence
    raw = activity.raw_data if isinstance(activity.raw_data, dict) else {}

    if avg is None and raw:
        avg = (
            raw.get("averageRunningCadenceInStepsPerMinute")
            or raw.get("averageBikingCadenceInRevPerMinute")
            or raw.get("averageCadence")
        )
    if mx is None and raw:
        mx = (
            raw.get("maxRunningCadenceInStepsPerMinute")
            or raw.get("maxBikingCadenceInRevPerMinute")
            or raw.get("maxCadence")
        )

    # FIT metadata / stream fallback
    if (avg is None or mx is None) and raw:
        ts_wrap = raw.get("time_series") if isinstance(raw.get("time_series"), dict) else {}
        meta = ts_wrap.get("metadata") if isinstance(ts_wrap, dict) else {}
        stats = meta.get("cadence_stats") if isinstance(meta, dict) else None
        if isinstance(stats, dict):
            if avg is None and stats.get("avg") is not None:
                avg = float(stats["avg"])
            if mx is None and stats.get("max") is not None:
                mx = float(stats["max"])
        if avg is None or mx is None:
            inner = ts_wrap.get("time_series") if isinstance(ts_wrap, dict) else {}
            samples = inner.get("cadence") if isinstance(inner, dict) else None
            if isinstance(samples, list) and samples:
                nums = [float(v) for v in samples if v is not None and float(v) > 0]
                if nums:
                    if avg is None:
                        avg = sum(nums) / len(nums)
                    if mx is None:
                        mx = max(nums)

    return (
        float(avg) if avg is not None else None,
        float(mx) if mx is not None else None,
    )


def _activity_detail_response(
    activity: GarminActivity,
    matched: Optional[Workout] = None,
    ftp: Optional[float] = None,
    run_threshold_sec: Optional[float] = None,
    threshold_hr: Optional[int] = None,
) -> ActivityDetailResponse:
    load = display_load_for_activity(activity, threshold_hr)
    calculated_tss = load[0] if load else activity.calculated_tss
    intensity_factor = load[1] if load else activity.intensity_factor
    avg_cadence, _max_cadence = _cadence_from_raw(activity)
    return ActivityDetailResponse(
        id=activity.id,
        garmin_activity_id=activity.garmin_activity_id,
        activity_name=activity.activity_name,
        activity_type=activity.activity_type,
        sport_type_id=activity.sport_type_id,
        start_time_local=activity.start_time_local,
        start_time_gmt=activity.start_time_gmt,
        date=activity.start_time_local.strftime("%Y-%m-%d"),
        duration_seconds=activity.duration_seconds,
        elapsed_duration_seconds=activity.elapsed_duration_seconds,
        moving_duration_seconds=activity.moving_duration_seconds,
        distance_meters=activity.distance_meters,
        average_speed_mps=activity.average_speed_mps,
        max_speed_mps=activity.max_speed_mps,
        elevation_gain_meters=activity.elevation_gain_meters,
        elevation_loss_meters=activity.elevation_loss_meters,
        min_elevation_meters=activity.min_elevation_meters,
        max_elevation_meters=activity.max_elevation_meters,
        average_hr=activity.average_hr,
        max_hr=activity.max_hr,
        average_power_watts=activity.average_power_watts,
        max_power_watts=activity.max_power_watts,
        normalized_power_watts=activity.normalized_power_watts,
        threshold_power_watts=activity.threshold_power_watts,
        calculated_tss=calculated_tss,
        training_load=activity.training_load,
        intensity_factor=intensity_factor,
        vo2_max=activity.vo2_max,
        aerobic_training_effect=activity.aerobic_training_effect,
        anaerobic_training_effect=activity.anaerobic_training_effect,
        calories=activity.calories,
        steps=activity.steps,
        average_cadence=avg_cadence,
        location_name=activity.location_name,
        has_polyline=activity.has_polyline or False,
        manual_activity=activity.manual_activity or False,
        matched_workout=_matched_workout_info(
            matched,
            activity,
            ftp=ftp,
            run_threshold_sec=run_threshold_sec,
        ),
        synced_at=activity.synced_at,
        created_at=activity.created_at,
        updated_at=activity.updated_at,
    )


async def _get_user_activity(
    db: AsyncSession,
    activity_id: int,
    user_id: int,
) -> GarminActivity:
    result = await db.execute(
        select(GarminActivity)
        .where(GarminActivity.id == activity_id)
        .where(GarminActivity.user_id == user_id)
    )
    activity = result.scalar_one_or_none()
    if not activity:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Activity not found",
        )
    return activity


# API Endpoints

@router.get("/{activity_id}", response_model=ActivityDetailResponse)
async def get_activity_detail(
    activity_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get full activity details.
    
    Returns all stored metadata for the activity including timing, distance,
    heart rate, power, training metrics, and location data.
    """
    activity = await _get_user_activity(db, activity_id, current_user.id)
    matched = await get_workout_linked_to_activity(db, activity_id, current_user.id)
    threshold_hr = current_user.running_threshold_hr or (
        int(current_user.max_hr * 0.9) if current_user.max_hr else 165
    )
    return _activity_detail_response(
        activity,
        matched,
        ftp=current_user.ftp,
        run_threshold_sec=current_user.threshold_pace,
        threshold_hr=threshold_hr,
    )


@router.get("/{activity_id}/track", response_model=ActivityTrackResponse)
async def get_activity_track(
    activity_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get GPS track points for mapping.
    
    Returns list of latitude/longitude coordinates with optional elevation data.
    Track is downsampled if needed to keep response size manageable.
    Downloads and caches FIT time_series on demand when missing.
    """
    activity = await _get_user_activity(db, activity_id, current_user.id)

    # Lazy-load FIT when polyline expected or raw_data has no series yet
    time_series_payload = await ensure_time_series(db, activity, current_user)

    if not time_series_payload:
        return ActivityTrackResponse(
            activity_id=activity_id,
            track_points=[],
            total_points=0,
            has_elevation=False,
        )

    point_dicts, has_elevation = extract_track_points(time_series_payload)
    track_points = [
        TrackPoint(
            lat=p["lat"],
            lng=p["lng"],
            ele=p.get("ele"),
            timestamp=p.get("timestamp"),
        )
        for p in point_dicts
    ]

    # Downsample if too many points (keep max 2000 points)
    if len(track_points) > 2000:
        step = max(1, len(track_points) // 2000)
        track_points = track_points[::step]

    return ActivityTrackResponse(
        activity_id=activity_id,
        track_points=track_points,
        total_points=len(track_points),
        has_elevation=has_elevation,
    )


@router.get("/{activity_id}/streams", response_model=ActivityStreamsResponse)
async def get_activity_streams(
    activity_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get time-series data for charts (HR, power, pace, etc.).
    
    Returns arrays of values sampled over time/distance for visualization.
    Data is downsampled to ~500 points for performance.
    """
    activity = await _get_user_activity(db, activity_id, current_user.id)

    # Ensure FIT time_series is cached (same path as /track)
    await ensure_time_series(db, activity, current_user)
    
    # Parallel arrays — append None when a sample is missing so indices stay aligned
    timestamps: List[datetime] = []
    distance_meters: List[Optional[float]] = []
    pace_min_per_km: List[Optional[float]] = []
    heart_rate_bpm: List[Optional[int]] = []
    power_watts: List[Optional[float]] = []
    cadence: List[Optional[float]] = []
    elevation_meters: List[Optional[float]] = []
    speed_mps: List[Optional[float]] = []

    if activity.raw_data and isinstance(activity.raw_data, dict):
        time_series_data = activity.raw_data.get('time_series')

        if time_series_data and isinstance(time_series_data, dict):
            ts = time_series_data.get('time_series', {})

            timestamp_strs = ts.get('timestamps', [])
            distances = ts.get('distance', [])
            speeds = ts.get('speed', [])
            hrs = ts.get('heart_rate', [])
            powers = ts.get('power', [])
            cadences = ts.get('cadence', [])
            elevations = ts.get('altitude', [])

            for i in range(len(timestamp_strs)):
                timestamp_str = timestamp_strs[i] if i < len(timestamp_strs) else None
                if not timestamp_str:
                    continue
                try:
                    ts_dt = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
                except Exception:
                    continue

                timestamps.append(ts_dt)

                dist = distances[i] if i < len(distances) else None
                distance_meters.append(float(dist) if dist is not None else None)

                speed = speeds[i] if i < len(speeds) else None
                if speed is not None and float(speed) > 0:
                    speed_val = float(speed)
                    speed_mps.append(speed_val)
                    pace_min_per_km.append((1000 / speed_val) / 60)
                else:
                    speed_mps.append(None)
                    pace_min_per_km.append(None)

                hr = hrs[i] if i < len(hrs) else None
                heart_rate_bpm.append(int(hr) if hr is not None else None)

                pwr = powers[i] if i < len(powers) else None
                power_watts.append(float(pwr) if pwr is not None else None)

                cad = cadences[i] if i < len(cadences) else None
                cadence.append(float(cad) if cad is not None else None)

                ele = elevations[i] if i < len(elevations) else None
                elevation_meters.append(float(ele) if ele is not None else None)

    # Downsample to ~500 points if needed (same step for all series)
    max_points = 500
    if len(timestamps) > max_points:
        step = max(1, len(timestamps) // max_points)
        timestamps = timestamps[::step]
        distance_meters = distance_meters[::step]
        pace_min_per_km = pace_min_per_km[::step]
        heart_rate_bpm = heart_rate_bpm[::step]
        power_watts = power_watts[::step]
        cadence = cadence[::step]
        elevation_meters = elevation_meters[::step]
        speed_mps = speed_mps[::step]

    def _any_present(values: List) -> bool:
        return any(v is not None for v in values)

    streams = TimeSeriesData(
        timestamps=timestamps,
        distance_meters=distance_meters if _any_present(distance_meters) else None,
        pace_min_per_km=pace_min_per_km if _any_present(pace_min_per_km) else None,
        heart_rate_bpm=heart_rate_bpm if _any_present(heart_rate_bpm) else None,
        power_watts=power_watts if _any_present(power_watts) else None,
        cadence=cadence if _any_present(cadence) else None,
        elevation_meters=elevation_meters if _any_present(elevation_meters) else None,
        speed_mps=speed_mps if _any_present(speed_mps) else None,
    )
    
    return ActivityStreamsResponse(
        activity_id=activity_id,
        streams=streams,
        total_samples=len(timestamps)
    )


@router.get("/{activity_id}/splits", response_model=ActivitySplitsResponse)
async def get_activity_splits(
    activity_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get lap splits for the activity.
    
    Returns stats for each lap/split including distance, pace, HR, power, etc.
    """
    # Query activity
    result = await db.execute(
        select(GarminActivity)
        .where(GarminActivity.id == activity_id)
        .where(GarminActivity.user_id == current_user.id)
    )
    activity = result.scalar_one_or_none()
    
    if not activity:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Activity not found"
        )
    
    splits: List[LapSplit] = []
    
    # Extract splits from raw_data
    if activity.raw_data and isinstance(activity.raw_data, dict):
        # Check for splits data (stored by Garmin sync)
        laps = activity.raw_data.get('splits', [])
        
        for i, lap in enumerate(laps, start=1):
            if not isinstance(lap, dict):
                continue
            
            split = LapSplit(
                lap_number=i,
                distance_meters=lap.get('distance', 0),
                duration_seconds=lap.get('duration', 0) or lap.get('elapsedDuration', 0),
                average_speed_mps=lap.get('averageSpeed'),
                average_hr=lap.get('averageHR') or lap.get('averageHeartRate'),
                max_hr=lap.get('maxHR') or lap.get('maxHeartRate'),
                average_power=lap.get('averagePower'),
                elevation_gain_meters=lap.get('elevationGain'),
                elevation_loss_meters=lap.get('elevationLoss'),
                average_cadence=lap.get('averageCadence') or lap.get('averageRunCadence'),
            )
            splits.append(split)
    
    return ActivitySplitsResponse(
        activity_id=activity_id,
        splits=splits,
        total_laps=len(splits)
    )


@router.patch("/{activity_id}", response_model=ActivityDetailResponse)
async def update_activity(
    activity_id: int,
    update: ActivityUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Update activity metadata (title, notes, etc.).
    
    Only user-editable fields can be modified. Activity data synced from
    Garmin (times, distances, metrics) cannot be changed.
    """
    # Query activity
    result = await db.execute(
        select(GarminActivity)
        .where(GarminActivity.id == activity_id)
        .where(GarminActivity.user_id == current_user.id)
    )
    activity = result.scalar_one_or_none()
    
    if not activity:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Activity not found"
        )
    
    # Update allowed fields
    if update.activity_name is not None:
        activity.activity_name = update.activity_name
    
    # Note: We don't have a notes field yet in the model
    # This will be added in a future migration
    
    activity.updated_at = datetime.utcnow()
    
    await db.commit()
    await db.refresh(activity)
    
    # Return updated activity
    return await get_activity_detail(activity_id, db, current_user)


@router.post("/{activity_id}/link-workout", response_model=ActivityDetailResponse)
async def link_activity_to_workout(
    activity_id: int,
    payload: LinkWorkoutRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Manually link a performed activity to a planned workout."""
    activity = await _get_user_activity(db, activity_id, current_user.id)

    result = await db.execute(
        select(Workout)
        .join(TrainingPlan, Workout.training_plan_id == TrainingPlan.id)
        .where(
            Workout.id == payload.workout_id,
            TrainingPlan.user_id == current_user.id,
        )
    )
    workout = result.scalar_one_or_none()
    if not workout:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Workout not found",
        )

    await link_manually(db, workout, activity)
    await db.commit()
    return await get_activity_detail(activity_id, db, current_user)


@router.post("/{activity_id}/unlink-workout", response_model=ActivityDetailResponse)
async def unlink_activity_from_workout(
    activity_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Unlink planned workout; restores it to planned and shows it on the calendar again."""
    await _get_user_activity(db, activity_id, current_user.id)
    workout = await get_workout_linked_to_activity(db, activity_id, current_user.id)
    if not workout:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No linked workout for this activity",
        )
    await unlink_workout(workout)
    await db.commit()
    return await get_activity_detail(activity_id, db, current_user)


@router.post("/{activity_id}/confirm-match", response_model=ActivityDetailResponse)
async def confirm_activity_match(
    activity_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Confirm a low-confidence auto-match."""
    await _get_user_activity(db, activity_id, current_user.id)
    workout = await get_workout_linked_to_activity(db, activity_id, current_user.id)
    if not workout:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No linked workout for this activity",
        )
    try:
        await confirm_match(workout)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    await db.commit()
    return await get_activity_detail(activity_id, db, current_user)


@router.get("", response_model=ActivityListResponse)
async def list_activities(
    page: int = 1,
    page_size: int = 50,
    sport_type: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    List activities with pagination and filtering.
    
    Query parameters:
    - page: Page number (1-indexed)
    - page_size: Number of items per page (max 100)
    - sport_type: Filter by activity type (running, cycling, etc.)
    - start_date: Filter activities after this date (YYYY-MM-DD)
    - end_date: Filter activities before this date (YYYY-MM-DD)
    """
    # Validate pagination
    if page < 1:
        page = 1
    if page_size < 1 or page_size > 100:
        page_size = 50
    
    # Build query
    query = select(GarminActivity).where(GarminActivity.user_id == current_user.id)
    
    # Apply filters
    if sport_type:
        query = query.where(GarminActivity.activity_type.ilike(f"%{sport_type}%"))
    
    if start_date:
        try:
            start_dt = datetime.fromisoformat(start_date)
            query = query.where(GarminActivity.start_time_local >= start_dt)
        except ValueError:
            pass
    
    if end_date:
        try:
            end_dt = datetime.fromisoformat(end_date)
            query = query.where(GarminActivity.start_time_local <= end_dt)
        except ValueError:
            pass
    
    # Order by date descending (newest first)
    query = query.order_by(GarminActivity.start_time_local.desc())
    
    # Count total
    count_query = select(GarminActivity.id).where(GarminActivity.user_id == current_user.id)
    if sport_type:
        count_query = count_query.where(GarminActivity.activity_type.ilike(f"%{sport_type}%"))
    if start_date:
        try:
            start_dt = datetime.fromisoformat(start_date)
            count_query = count_query.where(GarminActivity.start_time_local >= start_dt)
        except ValueError:
            pass
    if end_date:
        try:
            end_dt = datetime.fromisoformat(end_date)
            count_query = count_query.where(GarminActivity.start_time_local <= end_dt)
        except ValueError:
            pass
    
    total_result = await db.execute(count_query)
    total = len(total_result.all())
    
    # Apply pagination
    offset = (page - 1) * page_size
    query = query.offset(offset).limit(page_size)
    
    # Execute query
    result = await db.execute(query)
    activities = result.scalars().all()
    
    # Convert to list items
    activity_items = [
        ActivityListItem(
            id=a.id,
            activity_name=a.activity_name,
            activity_type=a.activity_type,
            start_time_local=a.start_time_local,
            date=a.start_time_local.strftime("%Y-%m-%d"),
            duration_seconds=a.duration_seconds,
            distance_meters=a.distance_meters,
            calculated_tss=a.calculated_tss,
            intensity_factor=a.intensity_factor,
            average_hr=a.average_hr,
            location_name=a.location_name,
        )
        for a in activities
    ]
    
    return ActivityListResponse(
        activities=activity_items,
        total=total,
        page=page,
        page_size=page_size
    )
