"""
Suggested plan vs performed activity, for the activity detail view.

Pure functions: no database. Callers pass the linked workout, the activity,
and an optional FTP (watts).
"""
from __future__ import annotations

import json
from datetime import date, datetime
from typing import Any, Dict, List, Optional

from src.utils.calculations.planned_load import AthleteThresholds, session_intensity


# Midpoint intensity factor for a prescribed zone or workout type.
ZONE_IF = {
    "zone1": 0.55,
    "recovery": 0.55,
    "easy": 0.65,
    "zone2": 0.70,
    "long": 0.70,
    "endurance": 0.70,
    "zone3": 0.85,
    "tempo": 0.85,
    "zone4": 0.95,
    "threshold": 0.95,
    "zone5": 1.05,
    "interval": 1.05,
    "zone6": 1.15,
    "race": 1.00,
}

ZONE_LABEL = {
    "zone1": "Z1",
    "zone2": "Z2",
    "zone3": "Z3",
    "zone4": "Z4",
    "zone5": "Z5",
    "zone6": "Z6",
}

# Relative gap that still counts as "on target".
_BAND = 0.08
_IF_BAND = 0.06


def _get(obj: Any, name: str, default: Any = None) -> Any:
    if obj is None:
        return default
    if isinstance(obj, dict):
        return obj.get(name, default)
    return getattr(obj, name, default)


def _as_date(value: Any) -> Optional[date]:
    if value is None:
        return None
    if isinstance(value, datetime):
        return value.date()
    if isinstance(value, date):
        return value
    if isinstance(value, str) and len(value) >= 10:
        try:
            return date.fromisoformat(value[:10])
        except ValueError:
            return None
    return None


def _fmt_if(value: float) -> str:
    return f"{value:.2f}"


def _fmt_duration_minutes(minutes: float) -> str:
    total = int(round(minutes))
    if total < 60:
        return f"{total} min"
    hours, mins = divmod(total, 60)
    if mins == 0:
        return f"{hours}h"
    return f"{hours}h {mins}m"


def _fmt_km(km: float) -> str:
    return f"{km:.1f} km"


def _fmt_watts(watts: float) -> str:
    return f"{int(round(watts))} W"


def _fmt_pct_ftp(pct: float) -> str:
    return f"{int(round(pct))}% FTP"


def _fmt_pace(seconds_per_unit: float, unit: str) -> str:
    total = int(round(seconds_per_unit))
    minutes, secs = divmod(max(total, 0), 60)
    return f"{minutes}:{secs:02d} {unit}"


def _fmt_speed(kmh: float) -> str:
    return f"{kmh:.1f} km/h"


def _sport_kind(activity_type: Optional[str], sport_type: Optional[str]) -> str:
    raw = f"{activity_type or ''} {sport_type or ''}".lower()
    if "swim" in raw:
        return "swim"
    if "cycl" in raw or "bike" in raw or "ride" in raw:
        return "bike"
    if "run" in raw:
        return "run"
    return "other"


def _parse_steps(raw: Any) -> List[Dict[str, Any]]:
    if not raw:
        return []
    try:
        parsed = json.loads(raw) if isinstance(raw, str) else raw
    except (json.JSONDecodeError, TypeError, ValueError):
        return []
    if isinstance(parsed, dict):
        parsed = parsed.get("steps") or []
    if not isinstance(parsed, list):
        return []
    return [s for s in parsed if isinstance(s, dict)]


def _step_minutes(step: Dict[str, Any]) -> Optional[float]:
    dur_type = str(step.get("durationType") or step.get("duration_type") or "time").lower()
    if dur_type in ("lap_button", "open"):
        return None
    value = step.get("durationValue")
    if value is None:
        value = step.get("duration_value")
    if value is None:
        return None
    try:
        amount = float(value)
    except (TypeError, ValueError):
        return None
    if amount <= 0:
        return None
    unit = str(step.get("durationUnit") or step.get("duration_unit") or "minutes").lower()
    if unit in ("seconds", "s", "sec"):
        return amount / 60.0
    if unit in ("hours", "h", "hr"):
        return amount * 60.0
    return amount


def _as_percent(value: Optional[float]) -> Optional[float]:
    """Accept 0–2.5 fractions (0.85) or already-percent values (85)."""
    if value is None:
        return None
    try:
        number = float(value)
    except (TypeError, ValueError):
        return None
    if number <= 0:
        return None
    if number <= 2.5:
        return number * 100.0
    return number


def _step_power_pct(step: Dict[str, Any]) -> Optional[float]:
    target_type = str(step.get("targetType") or step.get("target_type") or "").lower()
    target_unit = str(step.get("targetUnit") or step.get("target_unit") or "").lower()
    is_power = target_type == "power" or target_unit in ("%ftp", "ftp", "%", "percent", "watts", "w")
    if not is_power:
        return None
    lo = _as_percent(step.get("targetValueLow") if step.get("targetValueLow") is not None else step.get("target_value_low"))
    hi = _as_percent(step.get("targetValueHigh") if step.get("targetValueHigh") is not None else step.get("target_value_high"))
    # Absolute watts are not a percent. Skip them here; zone/duration still cover intensity.
    if target_unit in ("watts", "w") and target_type != "power":
        return None
    if target_unit in ("watts", "w"):
        return None
    if lo is None and hi is None:
        return None
    if lo is None:
        return hi
    if hi is None:
        return lo
    return (lo + hi) / 2.0


def _step_is_power(step: Dict[str, Any]) -> bool:
    target_type = str(step.get("targetType") or step.get("target_type") or "").lower()
    target_unit = str(step.get("targetUnit") or step.get("target_unit") or "").lower()
    return target_type == "power" or target_unit in ("%ftp", "ftp", "%", "percent", "watts", "w")


def session_omits_distance(
    sport: Optional[str],
    steps: List[Dict[str, Any]],
    duration_minutes: Any,
) -> bool:
    """True when a bike session is prescribed by time and power.

    Kilometres and speed then depend on elevation, wind, and surface, so they
    are not targets.
    """
    if _sport_kind(None, sport) != "bike":
        return False
    try:
        minutes = float(duration_minutes) if duration_minutes else 0.0
    except (TypeError, ValueError):
        return False
    if minutes <= 0:
        return False
    saw_power = False
    for step in steps:
        dur_type = str(step.get("durationType") or step.get("duration_type") or "time").lower()
        if dur_type == "distance":
            return False
        if dur_type == "time" and _step_is_power(step) and _step_minutes(step):
            saw_power = True
    return saw_power


def _weighted_power_pct(steps: List[Dict[str, Any]]) -> Optional[float]:
    weighted = 0.0
    total = 0.0
    for step in steps:
        minutes = _step_minutes(step)
        pct = _step_power_pct(step)
        if minutes is None or pct is None:
            continue
        weighted += pct * minutes
        total += minutes
    if total <= 0:
        return None
    return weighted / total


def _planned_if(workout: Any, power_pct: Optional[float]) -> Optional[float]:
    if power_pct is not None:
        return power_pct / 100.0
    zone = _get(workout, "intensity_zone")
    workout_type = _get(workout, "workout_type")
    for key in (zone, workout_type):
        if key and str(key).lower() in ZONE_IF:
            return ZONE_IF[str(key).lower()]
    return None


def _intensity_label(workout: Any, planned_if: Optional[float]) -> Optional[str]:
    if planned_if is None:
        return None
    zone = _get(workout, "intensity_zone")
    label = ZONE_LABEL.get(str(zone).lower()) if zone else None
    number = _fmt_if(planned_if)
    if label:
        return f"{label} · {number}"
    return number


def _tone_higher(planned: float, actual: float, *, band: float, high: str, low: str) -> tuple[str, str]:
    if planned == 0:
        return "neutral", ""
    gap = (actual - planned) / abs(planned)
    if gap > band:
        return "high", high
    if gap < -band:
        return "low", low
    return "ok", "on target"


def _tone_if(planned: float, actual: float) -> tuple[str, str]:
    gap = actual - planned
    if gap > _IF_BAND:
        return "high", "too high"
    if gap < -_IF_BAND:
        return "low", "easier"
    return "ok", "on target"


def _pct_label(planned: float, actual: float) -> tuple[str, str]:
    if planned == 0:
        return "neutral", ""
    pct = (actual - planned) / planned * 100.0
    if abs(pct) < _BAND * 100:
        return "ok", "on target"
    tone = "high" if pct > 0 else "low"
    rounded = int(round(pct))
    sign = "+" if rounded > 0 else ""
    return tone, f"{sign}{rounded}%"


def _row(
    label: str,
    planned: Optional[str],
    actual: Optional[str],
    delta: str = "",
    tone: str = "neutral",
) -> Optional[Dict[str, str]]:
    if not planned and not actual:
        return None
    if not planned:
        return None
    return {
        "label": label,
        "planned": planned,
        "actual": actual or "—",
        "delta": delta,
        "tone": tone,
    }


def _actual_minutes(activity: Any) -> Optional[float]:
    moving = _get(activity, "moving_duration_seconds")
    elapsed = _get(activity, "duration_seconds")
    seconds = moving or elapsed
    if not seconds:
        return None
    return float(seconds) / 60.0


def _actual_km(activity: Any) -> Optional[float]:
    meters = _get(activity, "distance_meters")
    if not meters:
        return None
    return float(meters) / 1000.0


def _actual_watts(activity: Any) -> Optional[float]:
    normalized = _get(activity, "normalized_power_watts")
    average = _get(activity, "average_power_watts")
    watts = normalized or average
    if not watts:
        return None
    return float(watts)


def build_plan_vs_actual(
    workout: Any,
    activity: Any,
    *,
    ftp: Optional[float] = None,
    run_threshold_sec: Optional[float] = None,
) -> Dict[str, Any]:
    """
    Compare a linked planned workout with the performed activity.

    Returns performed_on_planned_day, actual_date, and comparison rows.
    Rows are omitted when the plan has no value for that metric.
    """
    planned_day = _as_date(_get(workout, "date"))
    actual_day = _as_date(_get(activity, "start_time_local")) or _as_date(_get(activity, "date"))
    on_day = bool(planned_day and actual_day and planned_day == actual_day)

    steps = _parse_steps(_get(workout, "structured_workout_json"))
    power_pct = _weighted_power_pct(steps)
    step_if, run_pace_sec = session_intensity(
        steps,
        sport=_get(workout, "sport_type") or "",
        zone=_get(workout, "intensity_zone"),
        workout_type=_get(workout, "workout_type"),
        thresholds=AthleteThresholds(
            run_pace_sec_per_km=int(run_threshold_sec) if run_threshold_sec else None,
            ftp_watts=int(ftp) if ftp else None,
        ),
    )
    planned_if = step_if if step_if is not None else _planned_if(workout, power_pct)
    sport = _sport_kind(_get(activity, "activity_type"), _get(workout, "sport_type"))

    ftp_watts = None
    if ftp:
        ftp_watts = float(ftp)
    elif _get(activity, "threshold_power_watts"):
        ftp_watts = float(_get(activity, "threshold_power_watts"))

    planned_minutes = _get(workout, "duration_minutes")
    planned_km = _get(workout, "distance_km")
    planned_tss = _get(workout, "target_tss")
    actual_minutes = _actual_minutes(activity)
    actual_km = _actual_km(activity)
    actual_tss = _get(activity, "calculated_tss")
    if actual_tss is None:
        actual_tss = _get(activity, "training_load")
    actual_if = _get(activity, "intensity_factor")
    actual_watts = _actual_watts(activity)
    if actual_if is None and actual_watts and ftp_watts:
        actual_if = actual_watts / ftp_watts

    rows: List[Dict[str, str]] = []

    planned_intensity = (
        _fmt_if(planned_if)
        if power_pct is not None
        else _intensity_label(workout, planned_if)
    )
    intensity = _row(
        "Intensity",
        planned_intensity,
        _fmt_if(float(actual_if)) if actual_if else None,
    )
    if intensity and planned_if and actual_if:
        tone, delta = _tone_if(planned_if, float(actual_if))
        intensity["tone"] = tone
        intensity["delta"] = delta
    if intensity:
        rows.append(intensity)

    if power_pct is not None or actual_watts:
        if power_pct is not None and ftp_watts:
            planned_power = _fmt_watts(ftp_watts * power_pct / 100.0)
        elif power_pct is not None:
            planned_power = _fmt_pct_ftp(power_pct)
        else:
            planned_power = None
        actual_power = _fmt_watts(actual_watts) if actual_watts else None
        power = _row("Power", planned_power, actual_power)
        if power and power_pct is not None and actual_watts and ftp_watts:
            tone, delta = _tone_higher(
                ftp_watts * power_pct / 100.0,
                actual_watts,
                band=_BAND,
                high="too high",
                low="easier",
            )
            power["tone"] = tone
            power["delta"] = delta
        elif power and power_pct is not None and actual_watts and not ftp_watts:
            power["delta"] = ""
        if power:
            rows.append(power)

    planned_minutes_f = float(planned_minutes) if planned_minutes else None
    planned_km_f = float(planned_km) if planned_km else None
    distance_is_target = bool(
        planned_km_f and planned_km_f > 0 and not session_omits_distance(
            _get(workout, "sport_type"),
            steps,
            planned_minutes,
        )
    )
    if planned_minutes_f and distance_is_target and planned_minutes_f > 0:
        if sport == "swim":
            planned_pace = (planned_minutes_f * 60.0) / (planned_km_f * 10.0)
            actual_pace = None
            speed = _get(activity, "average_speed_mps")
            if speed and float(speed) > 0:
                actual_pace = 100.0 / float(speed)
            pace = _row(
                "Pace",
                _fmt_pace(planned_pace, "/100m"),
                _fmt_pace(actual_pace, "/100m") if actual_pace else None,
            )
            if pace and actual_pace:
                # Lower seconds is faster.
                tone, delta = _tone_higher(
                    actual_pace,
                    planned_pace,
                    band=_BAND,
                    high="too fast",
                    low="too slow",
                )
                pace["tone"] = tone
                pace["delta"] = delta
            if pace:
                rows.append(pace)
        elif sport == "bike":
            planned_kmh = planned_km_f / (planned_minutes_f / 60.0)
            speed = _get(activity, "average_speed_mps")
            actual_kmh = float(speed) * 3.6 if speed else (
                actual_km / (actual_minutes / 60.0) if actual_km and actual_minutes else None
            )
            speed_row = _row("Speed", _fmt_speed(planned_kmh), _fmt_speed(actual_kmh) if actual_kmh else None)
            if speed_row and actual_kmh:
                tone, delta = _tone_higher(
                    planned_kmh,
                    actual_kmh,
                    band=_BAND,
                    high="too fast",
                    low="too slow",
                )
                speed_row["tone"] = tone
                speed_row["delta"] = delta
            if speed_row:
                rows.append(speed_row)
        else:
            if run_pace_sec:
                planned_pace = run_pace_sec
            elif planned_minutes_f and planned_km_f and planned_minutes_f > 0 and planned_km_f > 0:
                planned_pace = (planned_minutes_f * 60.0) / planned_km_f
            else:
                planned_pace = None
            speed = _get(activity, "average_speed_mps")
            actual_pace = (1000.0 / float(speed)) if speed and float(speed) > 0 else None
            pace = _row(
                "Pace",
                _fmt_pace(planned_pace, "/km"),
                _fmt_pace(actual_pace, "/km") if actual_pace else None,
            )
            if pace and actual_pace:
                tone, delta = _tone_higher(
                    actual_pace,
                    planned_pace,
                    band=_BAND,
                    high="too fast",
                    low="too slow",
                )
                pace["tone"] = tone
                pace["delta"] = delta
            if pace:
                rows.append(pace)

    if planned_minutes_f:
        duration = _row(
            "Duration",
            _fmt_duration_minutes(planned_minutes_f),
            _fmt_duration_minutes(actual_minutes) if actual_minutes else None,
        )
        if duration and actual_minutes:
            tone, delta = _pct_label(planned_minutes_f, actual_minutes)
            duration["tone"] = tone
            duration["delta"] = delta
        if duration:
            rows.append(duration)

    if distance_is_target and planned_km_f:
        distance = _row(
            "Distance",
            _fmt_km(planned_km_f),
            _fmt_km(actual_km) if actual_km else None,
        )
        if distance and actual_km:
            tone, delta = _pct_label(planned_km_f, actual_km)
            distance["tone"] = tone
            distance["delta"] = delta
        if distance:
            rows.append(distance)

    if planned_tss:
        tss = _row(
            "TSS",
            str(int(planned_tss)),
            str(int(round(float(actual_tss)))) if actual_tss else None,
        )
        if tss and actual_tss:
            tone, delta = _pct_label(float(planned_tss), float(actual_tss))
            tss["tone"] = tone
            tss["delta"] = delta
        if tss:
            rows.append(tss)

    return {
        "performed_on_planned_day": on_day if planned_day and actual_day else True,
        "actual_date": actual_day.isoformat() if actual_day else None,
        "rows": rows,
    }
