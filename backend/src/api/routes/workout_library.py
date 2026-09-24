"""
Workout library API — browse templates, preferences, and schedule onto calendar.
"""
from __future__ import annotations

import json
from datetime import date, datetime
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field
from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.routes.auth import get_current_active_user
from src.database import get_db
from src.models.training_plan import TrainingPlan, Workout
from src.models.user import User
from src.services.icu_service import icu_service
from src.utils.icu_workout_converter import kinesis_external_id, workout_to_icu_event
from src.workout_library import (
    DEFAULT_CALENDAR_TEMPLATE_IDS,
    get_template,
    list_templates,
    parse_enabled_ids,
    resolve_calendar_enabled_ids,
)

router = APIRouter(prefix="/workout-library", tags=["Workout Library"])


class TemplateSummary(BaseModel):
    id: str
    name: str
    category: Optional[str] = None
    description: Optional[str] = None
    sportType: str = "cycling"
    workoutType: Optional[str] = None
    durationMinutes: Optional[int] = None
    intensityZone: Optional[str] = None
    targetTSS: Optional[int] = None
    stepCount: int = 0


class LibraryPreferences(BaseModel):
    """enabled_ids null = not customized (Calendar uses starter defaults)."""
    enabled_ids: Optional[List[str]] = None
    using_defaults: bool = True
    default_ids: List[str] = Field(default_factory=lambda: list(DEFAULT_CALENDAR_TEMPLATE_IDS))


class LibraryPreferencesUpdate(BaseModel):
    enabled_ids: List[str] = Field(
        ..., description="Template ids to show in Calendar → Bike library"
    )


class ScheduleTemplateRequest(BaseModel):
    date: date
    plan_id: Optional[int] = Field(
        None, description="Defaults to the user's active training plan"
    )
    sync_to_icu: bool = Field(
        False,
        description="If true and ICU connected, push this workout immediately",
    )


class ScheduleTemplateResponse(BaseModel):
    workout_id: int
    plan_id: int
    date: date
    title: str
    icu_synced: bool = False
    icu_message: Optional[str] = None


@router.get("/templates", response_model=List[TemplateSummary])
async def get_templates(
    category: Optional[str] = Query(None),
    for_calendar: bool = Query(
        False,
        description="If true, only templates enabled in Settings (or starter defaults)",
    ),
    current_user: User = Depends(get_current_active_user),
):
    """List structured workout templates."""
    enabled = None
    if for_calendar:
        enabled = resolve_calendar_enabled_ids(current_user.workout_library_enabled_ids)
    return list_templates(category=category, enabled_ids=enabled)


@router.get("/templates/{template_id}")
async def get_template_detail(
    template_id: str,
    current_user: User = Depends(get_current_active_user),
) -> Dict[str, Any]:
    """Full template including structuredSteps."""
    template = get_template(template_id)
    if not template:
        raise HTTPException(status_code=404, detail="Template not found")
    return template


@router.get("/preferences", response_model=LibraryPreferences)
async def get_library_preferences(
    current_user: User = Depends(get_current_active_user),
):
    parsed = parse_enabled_ids(current_user.workout_library_enabled_ids)
    return LibraryPreferences(
        enabled_ids=parsed,
        using_defaults=parsed is None,
        default_ids=list(DEFAULT_CALENDAR_TEMPLATE_IDS),
    )


@router.put("/preferences", response_model=LibraryPreferences)
async def update_library_preferences(
    payload: LibraryPreferencesUpdate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    valid = {t["id"] for t in list_templates()}
    cleaned = [i for i in payload.enabled_ids if i in valid]
    current_user.workout_library_enabled_ids = json.dumps(cleaned)
    await db.commit()
    await db.refresh(current_user)
    return LibraryPreferences(
        enabled_ids=cleaned,
        using_defaults=False,
        default_ids=list(DEFAULT_CALENDAR_TEMPLATE_IDS),
    )


@router.post(
    "/templates/{template_id}/schedule",
    response_model=ScheduleTemplateResponse,
    status_code=status.HTTP_201_CREATED,
)
async def schedule_template(
    template_id: str,
    payload: ScheduleTemplateRequest,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Add a library workout to the calendar on the given date.
    Optionally sync immediately to Intervals.icu (→ Garmin).
    """
    template = get_template(template_id)
    if not template:
        raise HTTPException(status_code=404, detail="Template not found")

    plan = await _resolve_plan(db, current_user, payload.plan_id)
    steps = template.get("structuredSteps") or []
    if not steps:
        raise HTTPException(
            status_code=400, detail="Template has no structuredSteps"
        )

    workout = Workout(
        training_plan_id=plan.id,
        date=payload.date,
        sport_type=template.get("sportType") or "cycling",
        workout_type=template.get("workoutType") or "interval",
        title=template["name"],
        description=template.get("description"),
        duration_minutes=template.get("durationMinutes"),
        intensity_zone=template.get("intensityZone"),
        target_tss=template.get("targetTSS"),
        structured_workout_json=json.dumps(steps),
    )
    db.add(workout)
    await db.commit()
    await db.refresh(workout)

    icu_synced = False
    icu_message = None
    if payload.sync_to_icu:
        if not current_user.icu_connected or not current_user.icu_api_key:
            icu_message = "Workout saved; ICU not connected — sync from Settings"
        else:
            try:
                ext_id = kinesis_external_id(workout.id)
                event = workout_to_icu_event(workout, ext_id)
                await icu_service.upsert_events_bulk(
                    current_user.icu_api_key,
                    [event],
                    current_user.icu_athlete_id or "0",
                )
                workout.icu_external_id = ext_id
                workout.icu_synced_at = datetime.utcnow()
                workout.icu_sync_status = "synced"
                current_user.icu_last_sync = datetime.utcnow()
                await db.commit()
                icu_synced = True
                icu_message = "Synced to Intervals.icu"
            except Exception as e:
                workout.icu_sync_status = "failed"
                await db.commit()
                icu_message = f"Saved to calendar; ICU sync failed: {e}"

    return ScheduleTemplateResponse(
        workout_id=workout.id,
        plan_id=plan.id,
        date=workout.date,
        title=workout.title,
        icu_synced=icu_synced,
        icu_message=icu_message,
    )


async def _resolve_plan(
    db: AsyncSession, user: User, plan_id: Optional[int]
) -> TrainingPlan:
    if plan_id is not None:
        result = await db.execute(
            select(TrainingPlan).where(
                TrainingPlan.id == plan_id,
                TrainingPlan.user_id == user.id,
            )
        )
        plan = result.scalar_one_or_none()
        if not plan:
            raise HTTPException(status_code=404, detail="Training plan not found")
        return plan

    result = await db.execute(
        select(TrainingPlan)
        .where(
            and_(
                TrainingPlan.user_id == user.id,
                TrainingPlan.is_active == 1,
            )
        )
        .order_by(TrainingPlan.id.desc())
        .limit(1)
    )
    plan = result.scalar_one_or_none()
    if not plan:
        raise HTTPException(
            status_code=400,
            detail="No active training plan. Activate a plan before scheduling library workouts.",
        )
    return plan
