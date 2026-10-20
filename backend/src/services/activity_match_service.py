"""
Match performed Garmin activities to planned workouts.

Scoring: same sport required; date proximity + duration + distance similarity.
High confidence auto-links and marks the plan done. Medium confidence links
with needs_review so the user can confirm or unlink later.
"""
from __future__ import annotations

from datetime import date, datetime, timedelta
from typing import Any, Dict, List, Optional, Tuple

from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.models.garmin_activity import GarminActivity
from src.models.training_plan import TrainingPlan, Workout
from src.utils.sport_types import normalize_sport


# Thresholds
HIGH_CONFIDENCE = 0.75
REVIEW_CONFIDENCE = 0.45
DATE_WINDOW_DAYS = 1

MATCH_STATUS_AUTO_HIGH = "auto_high"
MATCH_STATUS_NEEDS_REVIEW = "needs_review"
MATCH_STATUS_CONFIRMED = "confirmed"
MATCH_STATUS_MANUAL = "manual"

# Re-export for existing callers
__all__ = [
    "normalize_sport",
    "sports_compatible",
    "score_match",
]


def sports_compatible(planned: Optional[str], performed: Optional[str]) -> bool:
    a = normalize_sport(planned)
    b = normalize_sport(performed)
    if a == b:
        return True
    # Strength / gym interchangeable
    if {a, b} <= {"strength", "gym"}:
        return True
    # Triathlon plans can absorb swim/bike/run
    if a == "triathlon" and b in ("running", "cycling", "swimming"):
        return True
    return False


def _ratio_similarity(planned: Optional[float], actual: Optional[float]) -> Optional[float]:
    """1.0 when equal; decays toward 0 as relative difference grows. None if either missing."""
    if planned is None or actual is None:
        return None
    if planned <= 0 or actual <= 0:
        return None
    ratio = min(planned, actual) / max(planned, actual)
    return float(ratio)


def score_match(workout: Workout, activity: GarminActivity) -> float:
    """
    Return confidence 0–1. Returns 0 if sport incompatible.
    """
    if not sports_compatible(workout.sport_type, activity.activity_type):
        return 0.0

    act_date = activity.start_time_local.date() if activity.start_time_local else None
    if act_date is None or workout.date is None:
        return 0.0

    day_delta = abs((act_date - workout.date).days)
    if day_delta > DATE_WINDOW_DAYS:
        return 0.0
    date_score = 1.0 if day_delta == 0 else 0.55

    planned_mins = workout.duration_minutes
    actual_mins = None
    if activity.moving_duration_seconds:
        actual_mins = activity.moving_duration_seconds / 60.0
    elif activity.duration_seconds:
        actual_mins = activity.duration_seconds / 60.0
    duration_score = _ratio_similarity(
        float(planned_mins) if planned_mins else None,
        actual_mins,
    )

    planned_km = float(workout.distance_km) if workout.distance_km else None
    actual_km = (activity.distance_meters / 1000.0) if activity.distance_meters else None
    distance_score = _ratio_similarity(planned_km, actual_km)

    # Weight available signals
    weights: List[Tuple[float, float]] = [(date_score, 0.35)]
    if duration_score is not None:
        weights.append((duration_score, 0.40))
    if distance_score is not None:
        weights.append((distance_score, 0.25))

    # If only date available, keep confidence modest
    if len(weights) == 1:
        return min(0.50, date_score * 0.5)

    total_w = sum(w for _, w in weights)
    return sum(score * w for score, w in weights) / total_w


def apply_link(
    workout: Workout,
    activity: GarminActivity,
    *,
    confidence: float,
    status: str,
) -> None:
    """Link workout ↔ activity and mark the planned session done."""
    workout.matched_activity_id = activity.id
    workout.match_confidence = round(confidence, 3)
    workout.match_status = status
    workout.matched_at = datetime.utcnow()
    workout.is_completed = 1

    if activity.duration_seconds:
        workout.actual_duration_minutes = int(round(activity.duration_seconds / 60.0))
    if activity.distance_meters:
        workout.actual_distance_km = int(round(activity.distance_meters / 1000.0))


def clear_link(workout: Workout) -> None:
    """Unlink and restore planned status."""
    workout.matched_activity_id = None
    workout.match_confidence = None
    workout.match_status = None
    workout.matched_at = None
    workout.is_completed = 0
    workout.actual_duration_minutes = None
    workout.actual_distance_km = None


async def _candidate_workouts(
    db: AsyncSession,
    user_id: int,
    activity_date: date,
) -> List[Workout]:
    """Unlinked planned workouts near the activity date for the user's active plans."""
    window_start = activity_date - timedelta(days=DATE_WINDOW_DAYS)
    window_end = activity_date + timedelta(days=DATE_WINDOW_DAYS)

    result = await db.execute(
        select(Workout)
        .join(TrainingPlan, Workout.training_plan_id == TrainingPlan.id)
        .where(
            and_(
                TrainingPlan.user_id == user_id,
                TrainingPlan.is_active == 1,
                Workout.date >= window_start,
                Workout.date <= window_end,
                Workout.matched_activity_id.is_(None),
            )
        )
    )
    return list(result.scalars().all())


async def match_activity_to_workout(
    db: AsyncSession,
    activity: GarminActivity,
    user_id: int,
) -> Optional[Dict[str, Any]]:
    """
    Try to auto-match one activity to the best unlinked planned workout.

    Returns match info dict if linked, else None.
    Skips if another workout already links to this activity.
    """
    if activity.id is None:
        return None

    # Already linked?
    existing = await db.execute(
        select(Workout).where(Workout.matched_activity_id == activity.id).limit(1)
    )
    if existing.scalar_one_or_none():
        return None

    act_date = activity.start_time_local.date() if activity.start_time_local else None
    if act_date is None:
        return None

    candidates = await _candidate_workouts(db, user_id, act_date)
    if not candidates:
        return None

    scored: List[Tuple[float, Workout]] = []
    for w in candidates:
        conf = score_match(w, activity)
        if conf >= REVIEW_CONFIDENCE:
            scored.append((conf, w))

    if not scored:
        return None

    scored.sort(key=lambda x: x[0], reverse=True)
    best_conf, best_workout = scored[0]

    # Avoid stealing if second-best is very close (ambiguous)
    if len(scored) > 1 and (best_conf - scored[1][0]) < 0.08 and best_conf < HIGH_CONFIDENCE:
        status = MATCH_STATUS_NEEDS_REVIEW
    elif best_conf >= HIGH_CONFIDENCE:
        status = MATCH_STATUS_AUTO_HIGH
    else:
        status = MATCH_STATUS_NEEDS_REVIEW

    apply_link(best_workout, activity, confidence=best_conf, status=status)
    return {
        "workout_id": best_workout.id,
        "activity_id": activity.id,
        "confidence": best_conf,
        "match_status": status,
    }


async def match_activities_batch(
    db: AsyncSession,
    activities: List[GarminActivity],
    user_id: int,
) -> List[Dict[str, Any]]:
    """Match a list of activities (e.g. after sync). Returns list of link results."""
    results = []
    for activity in activities:
        try:
            match = await match_activity_to_workout(db, activity, user_id)
            if match:
                results.append(match)
        except Exception as e:
            print(f"⚠️ Activity match failed for activity {activity.id}: {e}", flush=True)
    return results


async def get_workout_linked_to_activity(
    db: AsyncSession,
    activity_id: int,
    user_id: int,
) -> Optional[Workout]:
    result = await db.execute(
        select(Workout)
        .join(TrainingPlan, Workout.training_plan_id == TrainingPlan.id)
        .where(
            and_(
                Workout.matched_activity_id == activity_id,
                TrainingPlan.user_id == user_id,
            )
        )
        .options(selectinload(Workout.training_plan))
        .limit(1)
    )
    return result.scalar_one_or_none()


async def link_manually(
    db: AsyncSession,
    workout: Workout,
    activity: GarminActivity,
) -> Workout:
    """Manual drag-drop / explicit link. Replaces any prior link on either side."""
    # Clear previous link on this workout
    if workout.matched_activity_id and workout.matched_activity_id != activity.id:
        clear_link(workout)

    # Clear any other workout linked to this activity
    other = await db.execute(
        select(Workout).where(
            and_(
                Workout.matched_activity_id == activity.id,
                Workout.id != workout.id,
            )
        )
    )
    for w in other.scalars().all():
        clear_link(w)

    apply_link(workout, activity, confidence=1.0, status=MATCH_STATUS_MANUAL)
    return workout


async def confirm_match(workout: Workout) -> Workout:
    if not workout.matched_activity_id:
        raise ValueError("Workout is not linked to an activity")
    workout.match_status = MATCH_STATUS_CONFIRMED
    workout.matched_at = datetime.utcnow()
    return workout


async def unlink_workout(workout: Workout) -> Workout:
    clear_link(workout)
    return workout
