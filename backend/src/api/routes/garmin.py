"""
Garmin Connect Integration API Routes
"""
from typing import List, Optional
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, status, Body
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel, EmailStr

from src.database import get_db
from src.models.user import User
from src.api.routes.auth import get_current_user
from src.services.garmin_service import garmin_service
from src.models.garmin_activity import GarminActivity
from src.utils.calculations.tss_calculator import calculate_tss_from_activity
from src.utils.datetime_helpers import date_to_string, compare_date_for_sqlite
from src.utils.calculations.training_load import calculate_training_load_metrics, get_current_training_metrics
from src.utils.fit_parser import parse_fit_time_series, get_time_series_summary
from src.utils.calculations.tss_from_time_series import calculate_tss_from_time_series, get_time_series_tss_summary


router = APIRouter(prefix="/garmin", tags=["garmin"])


# Pydantic schemas
class GarminConnectRequest(BaseModel):
    """Request to connect Garmin account."""
    email: EmailStr
    password: str


class GarminConnectionStatus(BaseModel):
    """Garmin connection status response."""
    connected: bool
    email: str | None = None
    last_sync: datetime | None = None


class GarminActivity(BaseModel):
    """Garmin activity summary."""
    activity_id: int
    activity_name: str
    activity_type: str
    start_time: datetime
    duration: float  # seconds
    distance: float | None = None  # meters
    avg_heart_rate: int | None = None
    calories: int | None = None
    training_load: float | None = None  # Garmin's training load
    calculated_tss: float | None = None  # Our calculated TSS


@router.post("/connect", response_model=GarminConnectionStatus)
async def connect_garmin(
    credentials: GarminConnectRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Connect user's Garmin account.
    
    Args:
        credentials: Garmin login credentials
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        Connection status
        
    Raises:
        HTTPException: If authentication fails
    """
    try:
        # Authenticate with Garmin
        tokens = await garmin_service.authenticate(
            credentials.email,
            credentials.password
        )
        
        # Store tokens in user record
        current_user.garmin_email = tokens["email"]
        current_user.garmin_oauth1_token = tokens["oauth1_token"]
        current_user.garmin_oauth2_token = tokens["oauth2_token"]
        current_user.garmin_connected = True
        current_user.garmin_last_sync = None
        
        await db.commit()
        
        return GarminConnectionStatus(
            connected=True,
            email=tokens["email"],
            last_sync=None
        )
    except ValueError as e:
        # Use 400 Bad Request instead of 401 to avoid triggering logout
        # 401 should be reserved for app authentication issues
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except ConnectionError as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Failed to connect to Garmin: {str(e)}"
        )
    except Exception as e:
        # Log the full error for debugging
        import traceback
        print(f"Garmin connection error: {traceback.format_exc()}")
        
        error_msg = str(e)
        # Make SSL errors more user-friendly
        if "SSL" in error_msg or "certificate" in error_msg.lower():
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="SSL certificate error. Please ensure Python SSL certificates are installed."
            )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to connect to Garmin: {str(e)}"
        )


@router.delete("/disconnect")
async def disconnect_garmin(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Disconnect user's Garmin account.
    
    Args:
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        Success message
    """
    current_user.garmin_email = None
    current_user.garmin_oauth1_token = None
    current_user.garmin_oauth2_token = None
    current_user.garmin_connected = False
    current_user.garmin_last_sync = None
    
    await db.commit()
    
    return {"message": "Garmin account disconnected"}


@router.get("/status", response_model=GarminConnectionStatus)
async def get_garmin_status(
    current_user: User = Depends(get_current_user)
):
    """
    Get Garmin connection status for current user.
    
    Args:
        current_user: Current authenticated user
        
    Returns:
        Connection status
    """
    return GarminConnectionStatus(
        connected=current_user.garmin_connected,
        email=current_user.garmin_email if current_user.garmin_connected else None,
        last_sync=current_user.garmin_last_sync
    )


@router.post("/sync-activities", response_model=dict)
async def sync_garmin_activities(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    days: int = Body(730, embed=True)  # Default 2 years (730 days)
):
    """
    Manually trigger sync of completed Garmin activities (past workouts).
    
    Args:
        current_user: Current authenticated user
        db: Database session
        days: Number of days to sync (default 730 = 2 years)
        
    Returns:
        Sync summary
        
    Raises:
        HTTPException: If not connected or sync fails
    """
    if not current_user.garmin_connected:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Garmin account not connected"
        )
    
    try:
        # Test connection first
        is_valid = await garmin_service.test_connection(
            current_user.garmin_oauth1_token,
            current_user.garmin_oauth2_token
        )
        
        if not is_valid:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Garmin connection expired. Please reconnect."
            )
        
        # Get activities from Garmin
        start_date = datetime.utcnow() - timedelta(days=days) if days else None
        activities = await garmin_service.get_activities(
            current_user.garmin_oauth1_token,
            current_user.garmin_oauth2_token,
            start_date=start_date,
            limit=50
        )
        
        # Import GarminActivity model and TSS calculator
        from src.models.garmin_activity import GarminActivity
        from sqlalchemy import select
        from src.utils.calculations.tss_calculator import calculate_tss_from_activity
        
        # Store activities in database
        new_count = 0
        updated_count = 0
        failed_count = 0
        errors = []
        
        for activity in activities:
            try:
                garmin_id = str(activity.get("activityId"))
                
                # Check if activity already exists
                result = await db.execute(
                    select(GarminActivity).where(
                        GarminActivity.garmin_activity_id == garmin_id
                    )
                )
                existing_activity = result.scalar_one_or_none()
                
                # Parse activity data
                activity_data = {
                    "user_id": current_user.id,
                    "garmin_activity_id": garmin_id,
                    "activity_name": activity.get("activityName", "Unnamed Activity"),
                    "activity_type": activity.get("activityType", {}).get("typeKey", "unknown"),
                    "sport_type_id": activity.get("sportTypeId"),
                    
                    # Timing - Handle multiple datetime formats from Garmin
                    "start_time_local": None,
                    "start_time_gmt": None,
                    "duration_seconds": activity.get("duration"),
                    "elapsed_duration_seconds": activity.get("elapsedDuration"),
                    "moving_duration_seconds": activity.get("movingDuration"),
                    
                    # Distance & Speed
                    "distance_meters": activity.get("distance"),
                    "average_speed_mps": activity.get("averageSpeed"),
                    "max_speed_mps": activity.get("maxSpeed"),
                    
                    # Elevation
                    "elevation_gain_meters": activity.get("elevationGain"),
                    "elevation_loss_meters": activity.get("elevationLoss"),
                    "min_elevation_meters": activity.get("minElevation"),
                    "max_elevation_meters": activity.get("maxElevation"),
                    
                    # Heart Rate
                    "average_hr": activity.get("averageHR"),
                    "max_hr": activity.get("maxHR"),
                    
                    # Calories & Steps
                    "calories": activity.get("calories"),
                    "steps": activity.get("steps"),
                    
                    # Running specific
                    "average_cadence": activity.get("averageRunningCadenceInStepsPerMinute"),
                    "max_cadence": activity.get("maxRunningCadenceInStepsPerMinute"),
                    "average_stride_length_meters": activity.get("avgStrideLength"),
                    
                    # Cycling specific (power)
                    "average_power_watts": activity.get("avgPower") or activity.get("averagePower"),
                    "max_power_watts": activity.get("maxPower"),
                    "normalized_power_watts": activity.get("normPower") or activity.get("normalizedPower"),
                    "threshold_power_watts": activity.get("ftpValue") or activity.get("thresholdPower"),
                    
                    # Training metrics
                    "aerobic_training_effect": activity.get("aerobicTrainingEffect"),
                    "anaerobic_training_effect": activity.get("anaerobicTrainingEffect"),
                    "training_load": activity.get("activityTrainingLoad"),
                    "vo2_max": activity.get("vO2MaxValue"),
                    
                    # Location
                    "location_name": activity.get("locationName"),
                    "start_latitude": activity.get("startLatitude"),
                    "start_longitude": activity.get("startLongitude"),
                    
                    # Flags
                    "has_polyline": activity.get("hasPolyline", False),
                    "manual_activity": activity.get("manualActivity", False),
                    
                    # Full data
                    "raw_data": activity,
                    "synced_at": datetime.utcnow()
                }
                
                # Parse datetime fields - Garmin returns ISO format with timezone
                # Try multiple formats to handle variations
                for time_field, time_key in [("start_time_local", "startTimeLocal"), ("start_time_gmt", "startTimeGMT")]:
                    time_str = activity.get(time_key)
                    if time_str:
                        try:
                            # Try ISO format first (e.g., "2025-01-02T10:30:00.0")
                            if 'T' in time_str:
                                activity_data[time_field] = datetime.fromisoformat(time_str.replace('Z', '+00:00').split('.')[0])
                            else:
                                # Try standard format
                                activity_data[time_field] = datetime.strptime(time_str, "%Y-%m-%d %H:%M:%S")
                        except (ValueError, AttributeError):
                            # If parsing fails, leave as None
                            pass
                
                # Calculate TSS from activity data
                # Get user thresholds from user settings
                # Determine sport-specific threshold HR
                sport_key = activity_data["activity_type"].lower()
                if 'cycl' in sport_key or 'bike' in sport_key:
                    threshold_hr = current_user.cycling_threshold_hr
                elif 'run' in sport_key:
                    threshold_hr = current_user.running_threshold_hr
                elif 'swim' in sport_key:
                    threshold_hr = current_user.swim_threshold_hr
                else:
                    # For other sports (skiing, hiking, etc.), use running threshold as baseline
                    threshold_hr = current_user.running_threshold_hr or 165
                
                user_settings = {
                    "ftp": current_user.ftp,
                    "threshold_pace": current_user.threshold_pace,
                    "threshold_hr": threshold_hr,
                    "max_hr": current_user.max_hr,
                    "resting_hr": current_user.resting_hr,
                }
                
                # Calculate TSS from summary data first (fallback)
                calculated_tss = calculate_tss_from_activity(activity, user_settings)
                
                # Check if time series data already exists (cached from previous sync)
                existing_time_series = None
                if existing_activity and existing_activity.raw_data:
                    existing_time_series = existing_activity.raw_data.get("time_series")
                    # Preserve cached time series in activity_data
                    if existing_time_series:
                        activity_data["raw_data"]["time_series"] = existing_time_series
                
                # Download and parse FIT file for time series data (only if not cached)
                # Only do this for activities with GPS/HR data to avoid unnecessary downloads
                if not existing_time_series and (activity.get("hasPolyline") or activity.get("averageHR")):
                    try:
                        fit_data = await garmin_service.download_activity_fit(
                            current_user.garmin_oauth1_token,
                            current_user.garmin_oauth2_token,
                            int(garmin_id)
                        )
                        
                        # Parse time series data
                        time_series_result = parse_fit_time_series(fit_data)
                        
                        if "error" not in time_series_result:
                            # Add time series to raw_data
                            activity_data["raw_data"]["time_series"] = time_series_result
                            existing_time_series = time_series_result
                        else:
                            print(f"  ⚠️  Time series parse failed: {time_series_result['error']}")
                    except Exception as e:
                        # Don't fail the entire sync if FIT download fails
                        print(f"  ⚠️  Failed to download/parse FIT file: {str(e)}")
                
                # Calculate TSS from time series (using cached or newly downloaded data)
                if existing_time_series:
                    try:
                        time_series_tss = calculate_tss_from_time_series(
                            existing_time_series,
                            user_settings,
                            activity_data["activity_type"]
                        )
                        
                        if time_series_tss is not None:
                            # Use time series TSS (more accurate)
                            calculated_tss = time_series_tss
                            summary = get_time_series_tss_summary(existing_time_series, time_series_tss)
                            print(f"  ✅ {summary}")
                        else:
                            # Fall back to summary-based TSS
                            summary = get_time_series_summary(existing_time_series)
                            print(f"  ✅ Time series: {summary} (TSS from summary)")
                    except Exception as e:
                        print(f"  ⚠️  TSS calculation failed: {str(e)}")
                
                # Store final TSS value
                activity_data["calculated_tss"] = calculated_tss
            
                if existing_activity:
                    # Update existing activity
                    for key, value in activity_data.items():
                        if key != "user_id" and key != "garmin_activity_id":  # Don't update IDs
                            setattr(existing_activity, key, value)
                    updated_count += 1
                else:
                    # Create new activity
                    new_activity = GarminActivity(**activity_data)
                    db.add(new_activity)
                    new_count += 1
            except Exception as e:
                failed_count += 1
                error_msg = f"Activity {activity.get('activityId')}: {str(e)}"
                errors.append(error_msg)
                print(f"Error importing activity: {error_msg}")
                continue
        
        # Update last sync time
        current_user.garmin_last_sync = datetime.utcnow()
        await db.commit()
        
        response = {
            "message": f"Synced {len(activities)} activities: {new_count} new, {updated_count} updated, {failed_count} failed",
            "activities_found": len(activities),
            "new_activities": new_count,
            "updated_activities": updated_count,
            "failed_activities": failed_count
        }
        
        if errors:
            response["errors"] = errors
        
        return response
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to sync activities: {str(e)}"
        )


@router.post("/sync-scheduled-workouts", response_model=dict)
async def sync_scheduled_workouts(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    past_days: int = Body(7, embed=True),
    future_days: int = Body(90, embed=True)
):
    """
    Sync scheduled workouts from Garmin Connect calendar.
    
    Fetches workouts that are scheduled in Garmin and imports them
    into the database. Creates a "Garmin Synced Workouts" training plan
    if it doesn't exist.
    
    Args:
        current_user: Current authenticated user
        db: Database session
        past_days: Number of past days to sync (default 7)
        future_days: Number of future days to sync (default 90)
        
    Returns:
        Sync summary with workout counts
        
    Raises:
        HTTPException: If not connected or sync fails
    """
    if not current_user.garmin_connected:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Garmin account not connected"
        )
    
    try:
        # Test connection first
        is_valid = await garmin_service.test_connection(
            current_user.garmin_oauth1_token,
            current_user.garmin_oauth2_token
        )
        
        if not is_valid:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Garmin connection expired. Please reconnect."
            )
        
        # Fetch scheduled workouts from Garmin
        from src.models.training_plan import Workout, TrainingPlan
        from sqlalchemy import select
        
        print(f"\n🔍 [API] Fetching scheduled workouts from Garmin...")
        print(f"[API] Date range: {datetime.utcnow() - timedelta(days=past_days)} to {datetime.utcnow() + timedelta(days=future_days)}")
        
        scheduled_workouts = await garmin_service.get_all_scheduled_workouts(
            current_user.garmin_oauth1_token,
            current_user.garmin_oauth2_token,
            start_date=datetime.utcnow() - timedelta(days=past_days),
            end_date=datetime.utcnow() + timedelta(days=future_days),
            limit=200
        )
        
        print(f"[API] ✅ Service returned {len(scheduled_workouts)} scheduled workouts")
        
        workout_new_count = 0
        workout_updated_count = 0
        workout_failed_count = 0
        workout_errors = []
        
        # Get or create a default training plan for Garmin synced workouts
        result = await db.execute(
            select(TrainingPlan).where(
                TrainingPlan.user_id == current_user.id,
                TrainingPlan.name == "Garmin Synced Workouts"
            )
        )
        default_plan = result.scalar_one_or_none()
        
        if not default_plan:
            # Create default plan for Garmin workouts
            default_plan = TrainingPlan(
                user_id=current_user.id,
                name="Garmin Synced Workouts",
                description="Workouts automatically synced from Garmin Connect",
                start_date=datetime.utcnow().date(),
                end_date=(datetime.utcnow() + timedelta(days=365)).date(),
                sport_type="triathlon",
                is_active=1
            )
            db.add(default_plan)
            await db.flush()  # Get the ID
        
        for garmin_workout in scheduled_workouts:
            try:
                garmin_workout_id = str(garmin_workout.get('workoutId'))
                
                # Check if workout already exists
                result = await db.execute(
                    select(Workout).where(
                        Workout.garmin_workout_id == garmin_workout_id
                    )
                )
                existing_workout = result.scalar_one_or_none()
                
                # Parse schedule date
                schedule_date_str = (
                    garmin_workout.get('scheduleDate') or
                    garmin_workout.get('scheduledDate') or
                    garmin_workout.get('date') or
                    garmin_workout.get('plannedDate')
                )
                
                if schedule_date_str:
                    schedule_str = str(schedule_date_str)
                    if 'T' in schedule_str:
                        workout_date = datetime.fromisoformat(schedule_str.split('T')[0]).date()
                    else:
                        workout_date = datetime.strptime(schedule_str[:10], '%Y-%m-%d').date()
                else:
                    continue  # Skip if no date
                
                # Parse workout data
                workout_name = garmin_workout.get('workoutName', 'Untitled Workout')
                sport_type_key = garmin_workout.get('sportType', {}).get('sportTypeKey', 'other') if isinstance(garmin_workout.get('sportType'), dict) else 'other'
                
                # Map Garmin sport types to our sport types
                sport_type_map = {
                    'running': 'running',
                    'cycling': 'cycling',
                    'lap_swimming': 'swimming',
                    'swimming': 'swimming',
                    'other': 'other'
                }
                sport_type = sport_type_map.get(sport_type_key, 'other')
                
                workout_data = {
                    "training_plan_id": default_plan.id,
                    "date": workout_date,
                    "sport_type": sport_type,
                    "workout_type": "easy",  # Default type
                    "title": workout_name,
                    "description": garmin_workout.get('description', ''),
                    "garmin_workout_id": garmin_workout_id,
                    "garmin_synced_at": datetime.utcnow(),
                    "garmin_sync_status": "synced",
                }
                
                if existing_workout:
                    # Update existing workout
                    for key, value in workout_data.items():
                        if key not in ["training_plan_id", "garmin_workout_id"]:
                            setattr(existing_workout, key, value)
                    workout_updated_count += 1
                else:
                    # Create new workout
                    new_workout = Workout(**workout_data)
                    db.add(new_workout)
                    workout_new_count += 1
                    
            except Exception as e:
                workout_failed_count += 1
                error_msg = f"Workout {garmin_workout.get('workoutId')}: {str(e)}"
                workout_errors.append(error_msg)
                print(f"Error importing workout: {error_msg}")
                continue
        
        # Update last sync time
        current_user.garmin_last_sync = datetime.utcnow()
        await db.commit()
        
        response = {
            "message": f"Synced {len(scheduled_workouts)} scheduled workouts: {workout_new_count} new, {workout_updated_count} updated, {workout_failed_count} failed",
            "workouts_found": len(scheduled_workouts),
            "new_workouts": workout_new_count,
            "updated_workouts": workout_updated_count,
            "failed_workouts": workout_failed_count,
            "date_range": {
                "start": (datetime.utcnow() - timedelta(days=past_days)).strftime("%Y-%m-%d"),
                "end": (datetime.utcnow() + timedelta(days=future_days)).strftime("%Y-%m-%d")
            }
        }
        
        if workout_errors:
            response["errors"] = workout_errors
        
        return response
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to sync scheduled workouts: {str(e)}"
        )


@router.get("/activities", response_model=List[dict])
async def get_recent_activities(
    current_user: User = Depends(get_current_user),
    limit: int = 20
):
    """
    Get recent Garmin activities from database.
    
    Args:
        current_user: Current authenticated user
        limit: Maximum number of activities to return
        
    Returns:
        List of recent activities
        
    Raises:
        HTTPException: If not connected
    """
    if not current_user.garmin_connected:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Garmin account not connected"
        )
    
    try:
        # This endpoint now returns stored activities from database
        # instead of fetching from Garmin API every time
        raise HTTPException(
            status_code=status.HTTP_501_NOT_IMPLEMENTED,
            detail="Use /garmin/activities/stored endpoint to get stored activities"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch activities: {str(e)}"
        )


@router.get("/activities/stored", response_model=List[dict])
async def get_stored_activities(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    limit: int = 100,
    skip: int = 0
):
    """
    Get stored Garmin activities from database.
    
    Args:
        current_user: Current authenticated user
        db: Database session
        limit: Maximum number of activities to return
        skip: Number of activities to skip (for pagination)
        
    Returns:
        List of stored activities
    """
    from src.models.garmin_activity import GarminActivity
    from sqlalchemy import select, desc
    
    # Query activities from database
    query = (
        select(GarminActivity)
        .where(GarminActivity.user_id == current_user.id)
        .order_by(desc(GarminActivity.start_time_local))
        .offset(skip)
        .limit(limit)
    )
    
    result = await db.execute(query)
    activities = result.scalars().all()
    
    # Convert to dict for response
    return [
        {
            "id": activity.id,
            "garmin_activity_id": activity.garmin_activity_id,
            "activity_name": activity.activity_name,
            "activity_type": activity.activity_type,
            "start_time_local": activity.start_time_local.isoformat() if activity.start_time_local else None,
            "duration_seconds": activity.duration_seconds,
            "distance_meters": activity.distance_meters,
            "calories": activity.calories,
            "average_hr": activity.average_hr,
            "training_load": activity.training_load,
            "calculated_tss": activity.calculated_tss,
            "location_name": activity.location_name,
            "synced_at": activity.synced_at.isoformat() if activity.synced_at else None,
        }
        for activity in activities
    ]


@router.get("/activities/by-date-range", response_model=List[dict])
async def get_activities_by_date_range(
    start_date: str,
    end_date: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get activities within a date range for calendar display.
    
    Args:
        start_date: Start date (YYYY-MM-DD)
        end_date: End date (YYYY-MM-DD) - inclusive
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        List of activities in the date range
    """
    from src.models.garmin_activity import GarminActivity
    from sqlalchemy import select, and_
    from datetime import datetime
    from src.utils.datetime_helpers import compare_date_for_sqlite, date_to_string
    
    # Parse dates and validate
    try:
        start_dt = datetime.strptime(start_date, "%Y-%m-%d")
        end_dt = datetime.strptime(end_date, "%Y-%m-%d")
        # Add one day to end_date to make it inclusive
        end_dt = end_dt + timedelta(days=1)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid date format. Use YYYY-MM-DD"
        )
    
    # Convert to strings for SQLite TEXT comparison
    start_str = compare_date_for_sqlite(start_dt)
    end_str = compare_date_for_sqlite(end_dt)
    
    # Query activities using string comparison for SQLite TEXT fields
    query = (
        select(GarminActivity)
        .where(
            and_(
                GarminActivity.user_id == current_user.id,
                GarminActivity.start_time_local >= start_str,
                GarminActivity.start_time_local < end_str
            )
        )
        .order_by(GarminActivity.start_time_local)
    )
    
    result = await db.execute(query)
    activities = result.scalars().all()
    
    # Convert to dict for response
    return [
        {
            "id": activity.id,
            "garmin_activity_id": activity.garmin_activity_id,
            "activity_name": activity.activity_name,
            "activity_type": activity.activity_type,
            "sport_type_id": activity.sport_type_id,
            "start_time_local": str(activity.start_time_local) if activity.start_time_local else None,
            "date": date_to_string(activity.start_time_local),
            "duration_seconds": activity.duration_seconds,
            "distance_meters": activity.distance_meters,
            "calories": activity.calories,
            "average_hr": activity.average_hr,
            "max_hr": activity.max_hr,
            "elevation_gain_meters": activity.elevation_gain_meters,
            "average_speed_mps": activity.average_speed_mps,
            "training_load": activity.training_load,
            "calculated_tss": activity.calculated_tss,
            "location_name": activity.location_name,
        }
        for activity in activities
    ]


@router.get("/activities/stats", response_model=dict)
async def get_activity_stats(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get activity statistics for dashboard.
    
    Returns:
        Dictionary with activity counts and metrics
    """
    from src.models.garmin_activity import GarminActivity
    from sqlalchemy import select, func
    from datetime import datetime, timedelta
    
    now = datetime.now()
    week_ago = now - timedelta(days=7)
    month_ago = now - timedelta(days=30)
    
    # Convert to strings for SQLite TEXT comparison
    week_ago_str = week_ago.strftime("%Y-%m-%d")
    month_ago_str = month_ago.strftime("%Y-%m-%d")
    
    # Total activities
    total_query = select(func.count(GarminActivity.id)).where(
        GarminActivity.user_id == current_user.id
    )
    total_result = await db.execute(total_query)
    total_activities = total_result.scalar() or 0
    
    # This week (using string comparison)
    week_query = select(func.count(GarminActivity.id)).where(
        GarminActivity.user_id == current_user.id,
        GarminActivity.start_time_local >= week_ago_str
    )
    week_result = await db.execute(week_query)
    activities_this_week = week_result.scalar() or 0
    from src.utils.datetime_helpers import compare_date_for_sqlite
    
    now = datetime.now()
    week_ago = now - timedelta(days=7)
    month_ago = now - timedelta(days=30)
    
    # Convert to strings for SQLite TEXT comparison
    week_ago_str = compare_date_for_sqlite(week_ago)
    month_ago_str = compare_date_for_sqlite(month_ago)
    
    # Total activities
    total_query = select(func.count(GarminActivity.id)).where(
        GarminActivity.user_id == current_user.id
    )
    total_result = await db.execute(total_query)
    total_activities = total_result.scalar() or 0
    
    # This week (using string comparison)
    week_query = select(func.count(GarminActivity.id)).where(
        GarminActivity.user_id == current_user.id,
        GarminActivity.start_time_local >= week_ago_str
    )
    week_result = await db.execute(week_query)
    activities_this_week = week_result.scalar() or 0
    
    # This month (using string comparison)
    month_query = select(func.count(GarminActivity.id)).where(
        GarminActivity.user_id == current_user.id,
        GarminActivity.start_time_local >= month_ago_str
    )
    month_result = await db.execute(month_query)
    activities_this_month = month_result.scalar() or 0
    
    return {
        "total_activities": total_activities,
        "activities_this_week": activities_this_week,
        "activities_this_month": activities_this_month,
    }


@router.post("/sync-workouts")
async def sync_workouts_to_garmin(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    days_ahead: int = Body(14, embed=True)
):
    """
    Sync upcoming workouts from training plans to Garmin Connect.
    
    Args:
        current_user: Current authenticated user
        db: Database session
        days_ahead: Number of days ahead to sync (default 14)
        
    Returns:
        Sync summary with counts and errors
    """
    if not current_user.garmin_connected:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Garmin account not connected"
        )
    
    try:
        from src.models.training_plan import Workout
        from src.utils.garmin_workout_converter import workout_to_garmin_instance
        from sqlalchemy import select, and_
        from datetime import date
        
        # Get upcoming workouts
        today = date.today()
        end_date = today + timedelta(days=days_ahead)
        
        result = await db.execute(
            select(Workout).where(
                and_(
                    Workout.date >= today,
                    Workout.date <= end_date,
                    Workout.is_completed == 0
                )
            )
        )
        upcoming_workouts = result.scalars().all()
        
        synced = 0
        failed = 0
        skipped = 0
        scheduled = 0
        reused = 0
        errors = []
        
        for workout in upcoming_workouts:
            try:
                # Skip if already synced and not modified
                if workout.garmin_sync_status == 'synced' and workout.garmin_synced_at and workout.updated_at <= workout.garmin_synced_at:
                    skipped += 1
                    continue
                
                # Convert workout to Garmin format
                workout_data = {
                    'title': workout.title,
                    'description': workout.description or '',
                    'sport_type': workout.sport_type,
                    'duration_minutes': workout.duration_minutes,
                    'distance_km': workout.distance_km,
                }
                
                # Create Garmin workout instance
                garmin_workout = workout_to_garmin_instance(workout_data)
                
                # Format date for Garmin (YYYY-MM-DD)
                scheduled_date = workout.date.strftime('%Y-%m-%d')
                
                # Upload to Garmin (checks database for duplicates)
                result = await garmin_service.upload_workout_to_garmin(
                    oauth1_token=current_user.garmin_oauth1_token,
                    oauth2_token=current_user.garmin_oauth2_token,
                    workout_json=garmin_workout,
                    workout_title=workout.title,
                    scheduled_date=scheduled_date,
                    existing_garmin_workout_id=workout.garmin_workout_id
                )
                
                garmin_workout_id, was_reused = result
                
                # Update workout sync status
                workout.garmin_workout_id = garmin_workout_id
                workout.garmin_synced_at = datetime.utcnow()
                workout.garmin_sync_status = 'synced'
                
                # Commit immediately to save garmin_workout_id for future syncs
                await db.commit()
                
                synced += 1
                scheduled += 1
                
                if was_reused:
                    reused += 1
                
            except Exception as e:
                await db.commit()  # Save failure status
                print(f"Error syncing workout: {error_msg}")
        
        # Final commit (in case there are any remaining changes)        error_msg = f"Workout '{workout.title}' ({workout.date}): {str(e)}"
                errors.append(error_msg)
                workout.garmin_sync_status = 'failed'
                print(f"Error syncing workout: {error_msg}")
        
        await db.commit()
        
        # Calculate newly created workouts
        newly_created = synced - reused
        
        response = {
            "message": f"Sync complete: {newly_created} new, {reused} reused, {skipped} skipped, {failed} failed",
            "total_workouts": len(upcoming_workouts),
            "synced": synced,
            "newly_created": newly_created,
            "reused": reused,
            "scheduled": scheduled,
            "skipped": skipped,
            "failed": failed
        }
        
        if errors:
            response["errors"] = errors
        
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to sync workouts: {str(e)}"
        )


@router.post("/sync-workout/{workout_id}")
async def sync_single_workout(
    workout_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Sync a single workout to Garmin Connect.
    
    Args:
        workout_id: ID of the workout to sync
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        Sync status and Garmin workout ID
    """
    if not current_user.garmin_connected:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Garmin account not connected"
        )
    
    try:
        from src.models.training_plan import Workout
        from src.utils.garmin_workout_converter import workout_to_garmin_json, format_workout_date
        from sqlalchemy import select
        
        # Get workout
        result = await db.execute(
            select(Workout).where(Workout.id == workout_id)
        )
        workout = result.scalar_one_or_none()
        
        if not workout:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Workout not found"
            )
        
        # Convert workout to Garmin format
        workout_data = {
            'title': workout.title,
            'description': workout.description,
            'sport_type': workout.sport_type,
            'duration_minutes': workout.duration_minutes,
            'distance_km': workout.distance_km,
            'workout_structure': None
        }
        
        garmin_json = workout_to_garmin_json(workout_data)
        
        # Upload to Garmin (checks database for duplicates)
        result = await garmin_service.upload_workout_to_garmin(
            current_user.garmin_oauth1_token,
            current_user.garmin_oauth2_token,
            garmin_json,
            workout_title=workout.title,
            scheduled_date=format_workout_date(workout.date),
            existing_garmin_workout_id=workout.garmin_workout_id
        )
        
        garmin_workout_id, was_reused = result
        
        # Update workout sync status
        workout.garmin_workout_id = garmin_workout_id
        workout.garmin_synced_at = datetime.utcnow()
        workout.garmin_sync_status = 'synced'
        
        await db.commit()
        
        message = "Workout already exists on this date, skipped" if was_reused else "Workout synced successfully"
        
        return {
            "message": message,
            "workout_id": workout_id,
            "garmin_workout_id": garmin_workout_id,
            "was_reused": was_reused,
            "synced_at": workout.garmin_synced_at
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to sync workout: {str(e)}"
        )


@router.delete("/workout/{workout_id}/garmin")
async def remove_workout_from_garmin(
    workout_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Remove a synced workout from Garmin Connect.
    
    Args:
        workout_id: ID of the workout to remove from Garmin
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        Removal status
    """
    if not current_user.garmin_connected:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Garmin account not connected"
        )
    
    try:
        from src.models.training_plan import Workout
        from sqlalchemy import select
        
        # Get workout
        result = await db.execute(
            select(Workout).where(Workout.id == workout_id)
        )
        workout = result.scalar_one_or_none()
        
        if not workout:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Workout not found"
            )
        
        if not workout.garmin_workout_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Workout is not synced to Garmin"
            )
        
        # Delete from Garmin
        success = await garmin_service.delete_workout_from_garmin(
            current_user.garmin_oauth1_token,
            current_user.garmin_oauth2_token,
            workout.garmin_workout_id
        )
        
        # Update workout sync status
        workout.garmin_workout_id = None
        workout.garmin_synced_at = None
        workout.garmin_sync_status = 'not_synced'
        
        await db.commit()
        
        return {
            "message": "Workout removed from Garmin" if success else "Workout unlinked (removal not supported)",
            "workout_id": workout_id,
            "success": success
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to remove workout: {str(e)}"
        )


# Training Load / PMC Endpoints

class TrainingLoadMetrics(BaseModel):
    """Training load metrics for Performance Management Chart."""
    date: str
    tss: float
    ctl: float  # Chronic Training Load (fitness)
    atl: float  # Acute Training Load (fatigue)
    tsb: float  # Training Stress Balance (form)


class CurrentMetrics(BaseModel):
    """Current training metrics summary."""
    ctl: float
    atl: float
    tsb: float
    weekly_tss: float
    trend: str  # 'up', 'down', or 'flat'


@router.get("/training-load", response_model=List[TrainingLoadMetrics])
async def get_training_load(
    days: int = 42,
    sport_type: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get training load metrics (CTL, ATL, TSB) for Performance Management Chart.
    
    Returns daily TSS and calculated fitness/fatigue/form metrics.
    
    Args:
        days: Number of days to return (default 42)
        sport_type: Optional sport filter (running, cycling, swimming)
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        List of daily training load metrics
    """
    from src.utils.calculations.training_load import calculate_training_load_metrics
    
    metrics = await calculate_training_load_metrics(
        db=db,
        user_id=current_user.id,
        days=days,
        sport_type=sport_type
    )
    
    return metrics


@router.get("/training-metrics", response_model=CurrentMetrics)
async def get_current_training_metrics(
    sport_type: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get current training metrics summary.
    
    Args:
        sport_type: Optional sport filter (running, cycling, swimming)
    
    Returns:
        Current CTL, ATL, TSB, weekly TSS, and trend
    """
    from src.utils.calculations.training_load import get_current_training_metrics
    
    metrics = await get_current_training_metrics(
        db=db,
        user_id=current_user.id,
        sport_type=sport_type
    )
    
    return metrics


@router.get("/activities/{activity_id}/time-series")
async def get_activity_time_series(
    activity_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get time series data (HR, elevation, speed, etc.) for a specific activity.
    
    Returns the parsed time series data from the FIT file if available.
    
    Args:
        activity_id: Internal activity ID (not Garmin ID)
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        Time series data with timestamps, HR, elevation, speed, etc.
    """
    # Get activity from database
    result = await db.execute(
        select(GarminActivity).where(
            GarminActivity.id == activity_id,
            GarminActivity.user_id == current_user.id
        )
    )
    activity = result.scalar_one_or_none()
    
    if not activity:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Activity not found"
        )
    
    # Check if time series data exists in raw_data
    if activity.raw_data and "time_series" in activity.raw_data:
        return activity.raw_data["time_series"]
    
    # If not, try to download and parse FIT file now
    if current_user.garmin_connected:
        try:
            fit_data = await garmin_service.download_activity_fit(
                current_user.garmin_oauth1_token,
                current_user.garmin_oauth2_token,
                int(activity.garmin_activity_id)
            )
            
            # Parse time series data
            time_series_result = parse_fit_time_series(fit_data)
            
            if "error" not in time_series_result:
                # Save to database for future requests
                if not activity.raw_data:
                    activity.raw_data = {}
                activity.raw_data["time_series"] = time_series_result
                await db.commit()
                
                return time_series_result
            else:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"Failed to parse FIT file: {time_series_result['error']}"
                )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to download FIT file: {str(e)}"
            )
    
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Time series data not available for this activity"
    )
