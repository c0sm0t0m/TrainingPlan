"""
Intervals.icu workout converter.

Maps Kinesis Workout models to ICU calendar event payloads using
native ICU workout description text (v1 — no FIT/ZWO files).
"""
from __future__ import annotations

import json
from datetime import date
from typing import Any, Dict, List, Optional, Union


# ICU event "type" values used by their calendar / Garmin bridge
SPORT_TO_ICU_TYPE = {
    "running": "Run",
    "cycling": "Ride",
    "swimming": "Swim",
    "strength": "WeightTraining",
    "gym": "WeightTraining",
    "walking": "Walk",
    "triathlon": "Ride",  # multi-sport fallback; title/description carry detail
    "other": "Other",
}

ZONE_TO_ICU = {
    "zone1": "Z1",
    "zone2": "Z2",
    "zone3": "Z3",
    "zone4": "Z4",
    "zone5": "Z5",
    "zone6": "Z6",
}


def _icu_type(sport_type: Optional[str]) -> str:
    key = (sport_type or "other").lower()
    return SPORT_TO_ICU_TYPE.get(key, "Other")


def _format_duration_value(value: Optional[float], unit: Optional[str]) -> Optional[str]:
    if value is None:
        return None
    unit = (unit or "minutes").lower()
    if unit in ("seconds", "s", "sec"):
        secs = int(value)
        if secs % 60 == 0:
            return f"{secs // 60}m"
        return f"{secs}s"
    if unit in ("minutes", "m", "min"):
        mins = int(value) if float(value).is_integer() else value
        return f"{mins}m"
    if unit in ("kilometers", "km"):
        return f"{value}km"
    if unit in ("meters", "mtr", "meter"):
        return f"{int(value)}m"
    return f"{value}m"


def _format_power_pct(lo: Optional[float], hi: Optional[float]) -> Optional[str]:
    """ICU power syntax: 90% or 88-92%."""
    if lo is None and hi is None:
        return None
    if lo is None:
        return f"{int(round(hi))}%"
    if hi is None or abs(hi - lo) < 0.5:
        return f"{int(round(lo))}%"
    return f"{int(round(lo))}-{int(round(hi))}%"


def _step_power_target(step: Dict[str, Any]) -> Optional[str]:
    """Prefer explicit %FTP targets (Kickr ERG via Garmin)."""
    target_type = (step.get("target_type") or step.get("targetType") or "").lower()
    target_unit = (step.get("target_unit") or step.get("targetUnit") or "").lower()
    lo = step.get("target_value_low")
    if lo is None:
        lo = step.get("targetValueLow")
    hi = step.get("target_value_high")
    if hi is None:
        hi = step.get("targetValueHigh")

    is_power = target_type == "power" or target_unit in ("%ftp", "ftp", "%", "percent")
    if not is_power:
        return None
    if lo is None and hi is None:
        return None
    # Values may already be 0–1 fractions (ZWO-style) or 0–200 percent
    if lo is not None and 0 < lo <= 2.5:
        lo = lo * 100
    if hi is not None and 0 < hi <= 2.5:
        hi = hi * 100
    return _format_power_pct(
        float(lo) if lo is not None else None,
        float(hi) if hi is not None else None,
    )


def _format_pace_seconds(seconds: float) -> str:
    total = int(round(seconds))
    return f"{total // 60}:{total % 60:02d}"


def _step_pace_target(step: Dict[str, Any]) -> Optional[str]:
    """Run pace as 5:39-6:15/km. Low bound is the faster (smaller) number."""
    target_type = (step.get("target_type") or step.get("targetType") or "").lower()
    target_unit = (step.get("target_unit") or step.get("targetUnit") or "").lower()
    if target_type != "pace":
        return None
    lo = step.get("target_value_low")
    if lo is None:
        lo = step.get("targetValueLow")
    hi = step.get("target_value_high")
    if hi is None:
        hi = step.get("targetValueHigh")
    if not lo and not hi:
        return None
    suffix = "/100m" if "100" in target_unit else "/km"
    fast = _format_pace_seconds(min(v for v in (lo, hi) if v))
    slow = _format_pace_seconds(max(v for v in (lo, hi) if v))
    if fast == slow:
        return f"{fast}{suffix}"
    return f"{fast}-{slow}{suffix}"


def _step_to_icu_line(step: Dict[str, Any]) -> str:
    """Convert one structured step dict to an ICU description line."""
    # Support both camelCase (API) and snake_case
    duration_type = step.get("duration_type") or step.get("durationType") or "time"
    duration_value = step.get("duration_value") if step.get("duration_value") is not None else step.get("durationValue")
    duration_unit = step.get("duration_unit") or step.get("durationUnit") or "minutes"
    intensity = (
        step.get("intensity_zone")
        or step.get("intensityZone")
        or step.get("zone")
        or step.get("target_zone")
    )
    step_type = (step.get("step_type") or step.get("stepType") or step.get("type") or "").lower()
    note = step.get("description") or step.get("name") or step.get("title") or ""

    if duration_type == "lap_button":
        dur = "lap"
    else:
        dur = _format_duration_value(duration_value, duration_unit) or "10m"

    # Prefer %FTP for smart-trainer ERG (Garmin → Kickr)
    power_pct = _step_power_target(step)
    if power_pct:
        line = f"- {dur} {power_pct}"
        if note:
            line += f" {note}"
        return line

    pace = _step_pace_target(step)
    if pace:
        line = f"- {dur} {pace}"
        if note:
            line += f" {note}"
        return line

    zone = ZONE_TO_ICU.get(str(intensity).lower(), None) if intensity else None
    if not zone and step_type in ("warmup", "cooldown", "recovery", "rest", "easy"):
        zone = "Z1"
    if not zone and step_type in ("tempo", "threshold"):
        zone = "Z3"
    if not zone and step_type in ("interval", "active", "vo2"):
        zone = "Z4"
    zone = zone or "Z2"

    line = f"- {dur} {zone}"
    if note:
        line += f" {note}"
    return line


def structured_steps_to_description(steps: List[Dict[str, Any]]) -> str:
    lines = [_step_to_icu_line(s) for s in steps if isinstance(s, dict)]
    return "\n".join(lines) if lines else ""


def build_icu_description(workout: Any) -> str:
    """
    Build ICU workout description text from a Workout ORM object or dict-like.
    Prefer structured_workout_json; fall back to plain description + duration/zone.
    """
    structured_raw = getattr(workout, "structured_workout_json", None)
    if isinstance(workout, dict):
        structured_raw = workout.get("structured_workout_json")

    if structured_raw:
        try:
            parsed = json.loads(structured_raw) if isinstance(structured_raw, str) else structured_raw
            if isinstance(parsed, list) and parsed:
                return structured_steps_to_description(parsed)
            if isinstance(parsed, dict) and "steps" in parsed:
                return structured_steps_to_description(parsed["steps"])
        except (json.JSONDecodeError, TypeError, ValueError):
            pass

    description = getattr(workout, "description", None)
    if isinstance(workout, dict):
        description = workout.get("description")
    description = (description or "").strip()

    duration = getattr(workout, "duration_minutes", None)
    if isinstance(workout, dict):
        duration = workout.get("duration_minutes")
    zone_raw = getattr(workout, "intensity_zone", None)
    if isinstance(workout, dict):
        zone_raw = workout.get("intensity_zone")
    zone = ZONE_TO_ICU.get(str(zone_raw).lower(), "Z2") if zone_raw else "Z2"

    if duration:
        header = f"- {int(duration)}m {zone}"
        return f"{header}\n{description}" if description else header
    return description or f"- 30m {zone}"


def workout_to_icu_event(workout: Any, external_id: str) -> Dict[str, Any]:
    """
    Convert a Workout to an Intervals.icu calendar event payload.

    Args:
        workout: ORM Workout (or dict with same fields)
        external_id: Stable id for upsert (e.g. kinesis-workout-{id})
    """
    if isinstance(workout, dict):
        workout_date: date = workout["date"]
        title = workout.get("title") or "Workout"
        sport_type = workout.get("sport_type")
        duration_minutes = workout.get("duration_minutes")
        distance_km = workout.get("distance_km")
        target_tss = workout.get("target_tss")
    else:
        workout_date = workout.date
        title = workout.title or "Workout"
        sport_type = workout.sport_type
        duration_minutes = workout.duration_minutes
        distance_km = workout.distance_km
        target_tss = workout.target_tss

    if isinstance(workout_date, date):
        start_date_local = workout_date.strftime("%Y-%m-%dT00:00:00")
    else:
        start_date_local = f"{str(workout_date)[:10]}T00:00:00"

    description = build_icu_description(workout)
    event: Dict[str, Any] = {
        "category": "WORKOUT",
        "start_date_local": start_date_local,
        "name": title,
        "type": _icu_type(sport_type),
        "description": description,
        "external_id": external_id,
    }

    # Power % in description → tell ICU this is a power-target ride (ERG-capable)
    sport_key = (sport_type or "").lower()
    if sport_key in ("cycling", "ride", "triathlon") and "%" in description:
        event["target"] = "POWER"

    if duration_minutes:
        event["moving_time"] = int(duration_minutes) * 60
    if distance_km:
        # model may store distance as int km
        event["distance"] = float(distance_km) * 1000
    if target_tss:
        event["icu_training_load"] = int(target_tss)

    return event


KINESIS_EXTERNAL_ID_PREFIX = "kinesis-workout-"


def kinesis_external_id(workout_id: Union[int, str]) -> str:
    return f"{KINESIS_EXTERNAL_ID_PREFIX}{workout_id}"


def is_kinesis_external_id(external_id: Optional[str]) -> bool:
    return bool(external_id) and str(external_id).startswith(KINESIS_EXTERNAL_ID_PREFIX)
