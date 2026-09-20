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
from src.api.routes.auth import get_current_user


router = APIRouter(prefix="/activities", tags=["activities"])


# Pydantic schemas
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
    
    # Metadata
    synced_at: datetime
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


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
    """Time-series data for charts."""
    timestamps: List[datetime]
    distance_meters: Optional[List[float]] = None
    pace_min_per_km: Optional[List[float]] = None
    heart_rate_bpm: Optional[List[int]] = None
    power_watts: Optional[List[float]] = None
    cadence: Optional[List[float]] = None
    elevation_meters: Optional[List[float]] = None
    speed_mps: Optional[List[float]] = None


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
    
    # Convert to response model
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
        calculated_tss=activity.calculated_tss,
        training_load=activity.training_load,
        intensity_factor=activity.intensity_factor,
        vo2_max=activity.vo2_max,
        aerobic_training_effect=activity.aerobic_training_effect,
        anaerobic_training_effect=activity.anaerobic_training_effect,
        calories=activity.calories,
        steps=activity.steps,
        average_cadence=activity.average_cadence,
        location_name=activity.location_name,
        has_polyline=activity.has_polyline,
        manual_activity=activity.manual_activity,
        synced_at=activity.synced_at,
        created_at=activity.created_at,
        updated_at=activity.updated_at,
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
    
    # Check if activity has GPS data
    if not activity.has_polyline or not activity.raw_data:
        return ActivityTrackResponse(
            activity_id=activity_id,
            track_points=[],
            total_points=0,
            has_elevation=False
        )
    
    # Extract track from raw_data
    # GPS data is stored in time_series after FIT file parsing
    track_points = []
    has_elevation = False
    
    raw_data = activity.raw_data
    if isinstance(raw_data, dict):
        # Check for time_series data (from FIT file parsing)
        time_series_data = raw_data.get('time_series')
        
        if time_series_data and isinstance(time_series_data, dict):
            # Get the inner time_series object
            ts = time_series_data.get('time_series', {})
            
            # Extract arrays
            latitudes = ts.get('latitude', [])
            longitudes = ts.get('longitude', [])
            altitudes = ts.get('altitude', [])
            timestamps = ts.get('timestamps', [])
            
            # Build track points from arrays
            for i in range(len(latitudes)):
                lat = latitudes[i]
                lng = longitudes[i]
                
                if lat is not None and lng is not None:
                    ele = altitudes[i] if i < len(altitudes) else None
                    timestamp_str = timestamps[i] if i < len(timestamps) else None
                    timestamp = None
                    
                    if timestamp_str:
                        try:
                            timestamp = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
                        except:
                            pass
                    
                    if ele is not None:
                        has_elevation = True
                    
                    track_points.append(TrackPoint(
                        lat=lat,
                        lng=lng,
                        ele=ele,
                        timestamp=timestamp
                    ))
    
    # Downsample if too many points (keep max 2000 points)
    if len(track_points) > 2000:
        step = len(track_points) // 2000
        track_points = track_points[::step]
    
    return ActivityTrackResponse(
        activity_id=activity_id,
        track_points=track_points,
        total_points=len(track_points),
        has_elevation=has_elevation
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
    
    # Initialize empty streams
    timestamps: List[datetime] = []
    distance_meters: List[float] = []
    pace_min_per_km: List[float] = []
    heart_rate_bpm: List[int] = []
    power_watts: List[float] = []
    cadence: List[float] = []
    elevation_meters: List[float] = []
    speed_mps: List[float] = []
    
    # Extract time-series from raw_data
    if activity.raw_data and isinstance(activity.raw_data, dict):
        # Check for time_series data (from FIT file parsing)
        time_series_data = activity.raw_data.get('time_series')
        
        if time_series_data and isinstance(time_series_data, dict):
            # Get the inner time_series object
            ts = time_series_data.get('time_series', {})
            
            # Extract arrays
            timestamp_strs = ts.get('timestamps', [])
            distances = ts.get('distance', [])
            speeds = ts.get('speed', [])
            hrs = ts.get('heart_rate', [])
            powers = ts.get('power', [])
            cadences = ts.get('cadence', [])
            elevations = ts.get('altitude', [])
            
            # Convert arrays to time series
            for i in range(len(timestamp_strs)):
                # Timestamp
                timestamp_str = timestamp_strs[i] if i < len(timestamp_strs) else None
                if timestamp_str:
                    try:
                        ts_dt = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
                        timestamps.append(ts_dt)
                    except:
                        continue
                
                # Distance
                dist = distances[i] if i < len(distances) else None
                if dist is not None:
                    distance_meters.append(float(dist))
                
                # Speed/Pace
                speed = speeds[i] if i < len(speeds) else None
                if speed is not None and speed > 0:
                    speed_mps.append(float(speed))
                    # Convert to pace (min/km)
                    pace = (1000 / speed) / 60  # seconds per meter -> minutes per km
                    pace_min_per_km.append(pace)
                
                # Heart Rate
                hr = hrs[i] if i < len(hrs) else None
                if hr is not None:
                    heart_rate_bpm.append(int(hr))
                
                # Power
                pwr = powers[i] if i < len(powers) else None
                if pwr is not None:
                    power_watts.append(float(pwr))
                
                # Cadence
                cad = cadences[i] if i < len(cadences) else None
                if cad is not None:
                    cadence.append(float(cad))
                
                # Elevation
                ele = elevations[i] if i < len(elevations) else None
                if ele is not None:
                    elevation_meters.append(float(ele))
    
    # Downsample to ~500 points if needed
    max_points = 500
    if len(timestamps) > max_points:
        step = len(timestamps) // max_points
        timestamps = timestamps[::step]
        if distance_meters:
            distance_meters = distance_meters[::step]
        if pace_min_per_km:
            pace_min_per_km = pace_min_per_km[::step]
        if heart_rate_bpm:
            heart_rate_bpm = heart_rate_bpm[::step]
        if power_watts:
            power_watts = power_watts[::step]
        if cadence:
            cadence = cadence[::step]
        if elevation_meters:
            elevation_meters = elevation_meters[::step]
        if speed_mps:
            speed_mps = speed_mps[::step]
    
    streams = TimeSeriesData(
        timestamps=timestamps,
        distance_meters=distance_meters if distance_meters else None,
        pace_min_per_km=pace_min_per_km if pace_min_per_km else None,
        heart_rate_bpm=heart_rate_bpm if heart_rate_bpm else None,
        power_watts=power_watts if power_watts else None,
        cadence=cadence if cadence else None,
        elevation_meters=elevation_meters if elevation_meters else None,
        speed_mps=speed_mps if speed_mps else None,
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
