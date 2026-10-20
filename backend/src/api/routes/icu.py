"""
Intervals.icu Integration API Routes

One-way sync: Kinesis active-plan workouts ↔ ICU calendar (manual sync).
Pushes upcoming workouts and removes ICU orphans no longer on the Kinesis plan.
"""
from datetime import date, datetime, timedelta
from typing import Optional

from fastapi import APIRouter, Body, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.database import get_db
from src.models.user import User
from src.models.training_plan import TrainingPlan, Workout
from src.api.routes.auth import get_current_user
from src.services.icu_service import icu_service
from src.utils.icu_workout_converter import (
    is_kinesis_external_id,
    kinesis_external_id,
    workout_to_icu_event,
)


router = APIRouter(prefix="/icu", tags=["Intervals.icu"])


class IcuConnectRequest(BaseModel):
    api_key: str = Field(..., min_length=8, description="Intervals.icu API key")
    athlete_id: Optional[str] = Field(
        None, description='ICU athlete id; omit or "0" for the key owner'
    )


class IcuConnectionStatus(BaseModel):
    connected: bool
    athlete_id: Optional[str] = None
    athlete_name: Optional[str] = None
    last_sync: Optional[datetime] = None


class IcuSyncWorkoutsRequest(BaseModel):
    days_ahead: int = Field(14, ge=1, le=90)


@router.post("/connect", response_model=IcuConnectionStatus)
async def connect_icu(
    credentials: IcuConnectRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Connect Intervals.icu using an API key from Settings → Developer."""
    try:
        athlete = await icu_service.test_connection(
            credentials.api_key.strip(),
            credentials.athlete_id,
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Failed to reach Intervals.icu: {e}",
        )

    athlete_id = str(athlete.get("id") or credentials.athlete_id or "0")
    athlete_name = athlete.get("name") or athlete.get("firstname") or None

    current_user.icu_api_key = credentials.api_key.strip()
    current_user.icu_athlete_id = athlete_id
    current_user.icu_connected = True
    current_user.icu_last_sync = None
    await db.commit()

    return IcuConnectionStatus(
        connected=True,
        athlete_id=athlete_id,
        athlete_name=athlete_name,
        last_sync=None,
    )


@router.delete("/disconnect")
async def disconnect_icu(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Disconnect Intervals.icu and clear stored credentials."""
    current_user.icu_api_key = None
    current_user.icu_athlete_id = None
    current_user.icu_connected = False
    current_user.icu_last_sync = None
    await db.commit()
    return {"message": "Disconnected from Intervals.icu"}


@router.get("/status", response_model=IcuConnectionStatus)
async def get_icu_status(current_user: User = Depends(get_current_user)):
    """Return Intervals.icu connection status (never exposes the API key)."""
    return IcuConnectionStatus(
        connected=bool(current_user.icu_connected and current_user.icu_api_key),
        athlete_id=current_user.icu_athlete_id if current_user.icu_connected else None,
        athlete_name=None,
        last_sync=current_user.icu_last_sync if current_user.icu_connected else None,
    )


@router.post("/sync-workouts")
async def sync_workouts_to_icu(
    payload: IcuSyncWorkoutsRequest = Body(default=IcuSyncWorkoutsRequest()),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Sync upcoming workouts from the active training plan to Intervals.icu.

    Upserts with external_id = kinesis-workout-{id}, then deletes any ICU
    workouts in the same date window that still have a Kinesis external_id
    but are no longer on the active plan calendar.
    """
    if not current_user.icu_connected or not current_user.icu_api_key:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Intervals.icu account not connected",
        )

    days_ahead = payload.days_ahead
    today = date.today()
    end_date = today + timedelta(days=days_ahead)
    athlete_id = current_user.icu_athlete_id or "0"
    api_key = current_user.icu_api_key

    # Active plan for this user
    plan_result = await db.execute(
        select(TrainingPlan)
        .where(
            and_(
                TrainingPlan.user_id == current_user.id,
                TrainingPlan.is_active == 1,
            )
        )
        .order_by(TrainingPlan.id.desc())
        .limit(1)
    )
    active_plan = plan_result.scalar_one_or_none()
    if not active_plan:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No active training plan. Activate a plan before syncing to Intervals.icu.",
        )

    workouts_result = await db.execute(
        select(Workout).where(
            and_(
                Workout.training_plan_id == active_plan.id,
                Workout.date >= today,
                Workout.date <= end_date,
                Workout.is_completed == 0,
            )
        ).order_by(Workout.date.asc())
    )
    upcoming = list(workouts_result.scalars().all())

    events = []
    workout_by_external: dict[str, Workout] = {}
    desired_external_ids: set[str] = set()
    for workout in upcoming:
        ext_id = workout.icu_external_id or kinesis_external_id(workout.id)
        event = workout_to_icu_event(workout, ext_id)
        events.append(event)
        workout_by_external[ext_id] = workout
        desired_external_ids.add(ext_id)

    synced = 0
    failed = 0
    deleted = 0
    errors: list[str] = []
    results = []
    now = datetime.utcnow()

    try:
        if events:
            print(
                f"🔄 ICU sync: {len(events)} workouts from plan '{active_plan.name}' "
                f"(next {days_ahead} days)",
                flush=True,
            )
            results = await icu_service.upsert_events_bulk(api_key, events, athlete_id)

            for ext_id, workout in workout_by_external.items():
                try:
                    workout.icu_external_id = ext_id
                    workout.icu_synced_at = now
                    workout.icu_sync_status = "synced"
                    synced += 1
                except Exception as e:
                    workout.icu_sync_status = "failed"
                    failed += 1
                    errors.append(f"Workout {workout.id}: {e}")

        # Remove ICU events pushed by Kinesis that are no longer on the calendar
        icu_events = await icu_service.list_events(
            api_key,
            oldest=today.isoformat(),
            newest=end_date.isoformat(),
            athlete_id=athlete_id,
            category="WORKOUT",
        )
        orphans = [
            {"external_id": ext_id}
            for ev in icu_events
            if is_kinesis_external_id(ext_id := ev.get("external_id"))
            and ext_id not in desired_external_ids
        ]
        if orphans:
            print(
                f"🗑️ ICU sync: removing {len(orphans)} orphan workout(s) "
                f"not on plan '{active_plan.name}'",
                flush=True,
            )
            deleted = await icu_service.delete_events_bulk(api_key, orphans, athlete_id)

    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Intervals.icu sync failed: {e}",
        )

    current_user.icu_last_sync = now
    await db.commit()

    print(
        f"✅ ICU sync done: {synced} synced, {deleted} deleted, {failed} failed "
        f"(API returned {len(results or [])} events)",
        flush=True,
    )

    parts = []
    if synced:
        parts.append(f"pushed {synced}")
    if deleted:
        parts.append(f"removed {deleted}")
    if not parts:
        parts.append("nothing to update")
    summary = ", ".join(parts)

    return {
        "message": (
            f"Synced Intervals.icu from '{active_plan.name}' ({summary}) "
            f"for the next {days_ahead} days"
        ),
        "plan_id": active_plan.id,
        "plan_name": active_plan.name,
        "synced": synced,
        "deleted": deleted,
        "failed": failed,
        "skipped": 0,
        "total": len(upcoming),
        "days_ahead": days_ahead,
        "errors": errors or None,
    }
