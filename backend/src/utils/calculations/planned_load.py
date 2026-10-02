"""
Planned-session targets and TSS.

Running paces are fractions of threshold speed (4:45/km = 285 sec/km):
  recovery  70–78%   warmup, cooldown, rest
  easy      76–84%   Z2 / long, midpoint 80%
  steady    85–95%   tempo
  threshold 95–105%
  strides   100–105% short, not faster than the threshold cap

TSS = hours × IF² × 100 (swim uses IF³).
IF is threshold pace / planned pace, or %FTP / 100.
"""
from __future__ import annotations

import copy
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple


@dataclass(frozen=True)
class AthleteThresholds:
    run_pace_sec_per_km: Optional[int] = None
    ftp_watts: Optional[int] = None
    swim_pace_sec_per_100m: Optional[int] = None


# (slower IF, faster IF). Pace seconds = threshold / IF.
_BANDS: Dict[str, Tuple[float, float]] = {
    "recovery": (0.70, 0.78),
    "easy": (0.76, 0.84),
    "steady": (0.85, 0.95),
    "threshold": (0.95, 1.05),
    "stride": (1.00, 1.05),
}

_OPEN_BIKE_IF = {
    "zone1": 0.50,
    "recovery": 0.50,
    "zone2": 0.65,
    "easy": 0.65,
    "long": 0.65,
    "zone3": 0.83,
    "tempo": 0.83,
    "zone4": 0.98,
    "threshold": 0.98,
    "interval": 0.98,
    "zone5": 1.05,
    "zone6": 1.10,
}


def format_pace(seconds: float) -> str:
    total = int(round(seconds))
    return f"{total // 60}:{total % 60:02d}"


def pace_prescription_text(threshold_sec: int) -> str:
    """Human pace bands for the plan prompt."""
    lines = [
        f"RUN PACES from threshold {format_pace(threshold_sec)}/km. "
        "Every running step is targetType \"pace\", targetUnit \"sec/km\". "
        "targetValueLow = faster bound (smaller seconds), targetValueHigh = slower bound. "
        "Do not prescribe running by heart rate."
    ]
    labels = (
        ("recovery", "Recovery / warmup / cooldown / rest"),
        ("easy", "Easy, long, Z2 (about 80% of threshold speed)"),
        ("steady", "Steady / tempo, 85–95%"),
        ("threshold", "Threshold, 95–105%"),
        ("stride", "Strides, short, 100–105%"),
    )
    for key, label in labels:
        slow_if, fast_if = _BANDS[key]
        fast = format_pace(threshold_sec / fast_if)
        slow = format_pace(threshold_sec / slow_if)
        lines.append(f"  • {label}: {fast}–{slow}/km")
    return "\n".join(lines)


def prepare_planned_session(
    steps: Optional[List[Dict[str, Any]]],
    *,
    sport: str,
    zone: Optional[str],
    workout_type: Optional[str],
    thresholds: AthleteThresholds,
) -> Tuple[List[Dict[str, Any]], int, Optional[int], Optional[str]]:
    """
    Rewrite run heart-rate steps to threshold paces and return
    (steps, tss, distance_km or None, pace label or None).
    """
    updated = [_convert_step(copy.deepcopy(step), sport, zone, workout_type, thresholds) for step in (steps or [])]
    tss, _intensity, distance_km, pace_label = _metrics(updated, sport, zone, workout_type, thresholds)
    return updated, tss, distance_km, pace_label


def session_intensity(
    steps: Optional[List[Dict[str, Any]]],
    *,
    sport: str,
    zone: Optional[str],
    workout_type: Optional[str],
    thresholds: AthleteThresholds,
) -> Tuple[Optional[float], Optional[float]]:
    """Duration-weighted IF and run pace (sec/km), for plan-vs-actual."""
    _tss, intensity, _distance, _label = _metrics(steps or [], sport, zone, workout_type, thresholds)
    pace = _weighted_run_pace(steps or [])
    return intensity, pace


def append_pace_label(description: Optional[str], label: Optional[str]) -> str:
    text = (description or "").strip()
    if not label or label in text:
        return text
    if not text:
        return label
    if text.endswith("."):
        return f"{text} {label}"
    return f"{text}. {label}"


def _metrics(
    steps: List[Dict[str, Any]],
    sport: str,
    zone: Optional[str],
    workout_type: Optional[str],
    thresholds: AthleteThresholds,
) -> Tuple[int, Optional[float], Optional[int], Optional[str]]:
    total_tss = 0.0
    weighted_if = 0.0
    weighted_hours = 0.0
    run_km = 0.0
    for step in steps:
        hours, factor, exponent, kind = _step_load(step, sport, zone, workout_type, thresholds)
        if hours is None or factor is None or hours <= 0:
            continue
        total_tss += hours * (factor ** exponent) * 100.0
        weighted_if += factor * hours
        weighted_hours += hours
        if kind == "run":
            pace = _pace_midpoint(step, "sec/km")
            if pace:
                run_km += hours * (3600.0 / pace)
    intensity = (weighted_if / weighted_hours) if weighted_hours else None
    distance = int(round(run_km)) if run_km >= 0.5 else None
    return int(round(total_tss)), intensity, distance, _pace_label(steps)


def _convert_step(
    step: Dict[str, Any],
    sport: str,
    zone: Optional[str],
    workout_type: Optional[str],
    thresholds: AthleteThresholds,
) -> Dict[str, Any]:
    if not _is_run_step(step, sport):
        return step
    if _pace_midpoint(step, "sec/km"):
        return step
    if not thresholds.run_pace_sec_per_km:
        return step
    band = _run_band(step, zone, workout_type)
    slow_if, fast_if = _BANDS[band]
    fast_sec = int(round(thresholds.run_pace_sec_per_km / fast_if))
    slow_sec = int(round(thresholds.run_pace_sec_per_km / slow_if))
    _set_target(step, "pace", "sec/km", fast_sec, slow_sec)
    return step


def _is_run_step(step: Dict[str, Any], sport: str) -> bool:
    family = _family(sport)
    target = _text(step, "target_type", "targetType")
    unit = _text(step, "target_unit", "targetUnit")
    if family == "run":
        return unit != "sec/100m"
    if family == "tri":
        if target == "power" or unit in ("%ftp", "ftp", "%", "percent", "watts", "w"):
            return False
        if unit == "sec/100m":
            return False
        return target in ("heart_rate", "pace", "open", "")
    return False


def _run_band(step: Dict[str, Any], zone: Optional[str], workout_type: Optional[str]) -> str:
    kind = _text(step, "step_type", "stepType") or "work"
    description = _text(step, "description") 
    minutes = _minutes(step)
    if "stride" in description:
        return "stride"
    if kind in ("warmup", "cooldown", "rest"):
        return "recovery"
    if minutes is not None and minutes <= 0.75 and _hr_mid(step) is not None and _hr_mid(step) >= 145:
        return "stride"
    hr = _hr_mid(step)
    if hr is not None and (minutes is None or minutes >= 1):
        if hr >= 148:
            return "threshold"
        if hr >= 132:
            return "steady"
        return "easy"
    zone_key = (zone or "").lower()
    type_key = (workout_type or "").lower()
    if zone_key in ("zone4", "zone5", "zone6") or type_key in ("interval", "race"):
        return "threshold"
    if zone_key == "zone3" or type_key == "tempo":
        return "steady"
    if zone_key == "zone1" or type_key == "recovery":
        return "recovery"
    return "easy"


def _step_load(
    step: Dict[str, Any],
    sport: str,
    zone: Optional[str],
    workout_type: Optional[str],
    thresholds: AthleteThresholds,
) -> Tuple[Optional[float], Optional[float], int, str]:
    """hours, IF, exponent, kind (run|bike|swim|other)."""
    family = _family(sport)
    target = _text(step, "target_type", "targetType")
    unit = _text(step, "target_unit", "targetUnit")
    kind = _step_kind(family, target, unit)

    if kind == "run" and thresholds.run_pace_sec_per_km:
        pace = _pace_midpoint(step, "sec/km")
        if pace:
            hours = _hours(step, pace, 1000)
            return hours, thresholds.run_pace_sec_per_km / pace, 2, "run"
    if kind == "bike":
        factor = _power_if(step, thresholds.ftp_watts)
        if factor is not None:
            return _hours(step, None, None), factor, 2, "bike"
    if kind == "swim" and thresholds.swim_pace_sec_per_100m:
        pace = _pace_midpoint(step, "sec/100m")
        if pace:
            hours = _hours(step, pace, 100)
            return hours, thresholds.swim_pace_sec_per_100m / pace, 3, "swim"

    factor = _fallback_if(step, kind, zone, workout_type)
    hours = _hours(step, _fallback_pace(kind, thresholds), 100 if kind == "swim" else 1000)
    exponent = 3 if kind == "swim" else 2
    return hours, factor, exponent, kind if kind != "run" else "other"


def _step_kind(family: str, target: str, unit: str) -> str:
    if target == "power" or unit in ("%ftp", "ftp", "%", "percent", "watts", "w"):
        return "bike"
    if unit == "sec/100m" or (family == "swim" and target == "pace"):
        return "swim"
    if family == "swim":
        return "swim"
    if family == "bike":
        return "bike"
    if family in ("run", "tri") and (target in ("pace", "heart_rate") or unit == "sec/km" or family == "run"):
        return "run"
    return "other"


def _power_if(step: Dict[str, Any], ftp: Optional[int]) -> Optional[float]:
    unit = _text(step, "target_unit", "targetUnit")
    lo, hi = _bounds(step)
    if lo is not None and lo <= 0:
        lo = None
    if hi is not None and hi <= 0:
        hi = None
    if lo is None and hi is None:
        return None
    if unit in ("watts", "w"):
        if not ftp:
            return None
        mid = _mid(lo, hi)
        return None if mid is None else mid / float(ftp)
    mid = _mid(lo, hi)
    if mid is None:
        return None
    if mid <= 2.5:
        mid *= 100.0
    return mid / 100.0


def _fallback_if(step: Dict[str, Any], kind: str, zone: Optional[str], workout_type: Optional[str]) -> float:
    step_type = _text(step, "step_type", "stepType")
    if step_type == "rest":
        return 0.45
    key = ((zone or workout_type or "zone2") or "").lower()
    if kind == "bike":
        return _OPEN_BIKE_IF.get(key, 0.65)
    if kind == "swim":
        return 0.75 if key not in ("zone4", "zone5", "threshold", "interval") else 0.95
    if kind == "other":
        return 0.50
    return 0.80 if key not in ("zone1", "recovery") else 0.74


def _fallback_pace(kind: str, thresholds: AthleteThresholds) -> Optional[float]:
    if kind == "swim" and thresholds.swim_pace_sec_per_100m:
        return thresholds.swim_pace_sec_per_100m / 0.75
    if kind == "run" and thresholds.run_pace_sec_per_km:
        return thresholds.run_pace_sec_per_km / 0.80
    return None


def _hours(step: Dict[str, Any], pace_sec: Optional[float], per_meters: Optional[int]) -> Optional[float]:
    value = _num(step, "duration_value", "durationValue")
    if value is None or value <= 0:
        return None
    unit = _text(step, "duration_unit", "durationUnit") or "minutes"
    dur_type = _text(step, "duration_type", "durationType") or "time"
    if dur_type == "distance" or unit in ("meters", "kilometers", "km"):
        if not pace_sec or not per_meters:
            return None
        meters = value * 1000.0 if unit in ("kilometers", "km") else value
        return (meters / per_meters) * pace_sec / 3600.0
    if unit in ("seconds", "s", "sec"):
        return value / 3600.0
    if unit in ("hours", "h", "hr"):
        return value
    return value / 60.0


def _pace_midpoint(step: Dict[str, Any], unit: str) -> Optional[float]:
    target = _text(step, "target_type", "targetType")
    step_unit = _text(step, "target_unit", "targetUnit")
    if target != "pace" or step_unit != unit:
        return None
    lo, hi = _bounds(step)
    if lo is None and hi is None:
        return None
    if lo is not None and lo <= 0:
        lo = None
    if hi is not None and hi <= 0:
        hi = None
    return _mid(lo, hi)


def _weighted_run_pace(steps: List[Dict[str, Any]]) -> Optional[float]:
    weighted = 0.0
    total = 0.0
    for step in steps:
        pace = _pace_midpoint(step, "sec/km")
        hours = _hours(step, pace, 1000) if pace else _hours(step, None, None)
        if pace is None or hours is None:
            continue
        weighted += pace * hours
        total += hours
    if total <= 0:
        return None
    return weighted / total


def _pace_label(steps: List[Dict[str, Any]]) -> Optional[str]:
    candidates = []
    for step in steps:
        if (_text(step, "step_type", "stepType") or "work") != "work":
            continue
        lo, hi = _bounds(step)
        if _text(step, "target_type", "targetType") != "pace":
            continue
        if _text(step, "target_unit", "targetUnit") != "sec/km":
            continue
        if lo is None or hi is None:
            continue
        minutes = _minutes(step) or 0
        if minutes < 3:
            continue
        candidates.append(( _mid(lo, hi), lo, hi))
    if not candidates:
        return None
    _midpace, fast, slow = min(candidates, key=lambda item: item[0])
    # low is the faster (smaller) bound
    slower = max(fast, slow)
    faster = min(fast, slow)
    if abs(slower - faster) < 1:
        return f"{format_pace(faster)}/km"
    return f"{format_pace(slower)}–{format_pace(faster)}/km"


def _set_target(step: Dict[str, Any], target_type: str, unit: str, fast: int, slow: int) -> None:
    camel = "targetType" in step or "stepType" in step
    if camel:
        step["targetType"] = target_type
        step["targetUnit"] = unit
        step["targetValueLow"] = fast
        step["targetValueHigh"] = slow
    else:
        step["target_type"] = target_type
        step["target_unit"] = unit
        step["target_value_low"] = fast
        step["target_value_high"] = slow


def _hr_mid(step: Dict[str, Any]) -> Optional[float]:
    if _text(step, "target_type", "targetType") != "heart_rate":
        return None
    lo, hi = _bounds(step)
    if lo is None and hi is None:
        return None
    return _mid(lo, hi)


def _minutes(step: Dict[str, Any]) -> Optional[float]:
    hours = _hours(step, None, None)
    if hours is None:
        return None
    return hours * 60.0


def _bounds(step: Dict[str, Any]) -> Tuple[Optional[float], Optional[float]]:
    return _num(step, "target_value_low", "targetValueLow"), _num(step, "target_value_high", "targetValueHigh")


def _mid(lo: Optional[float], hi: Optional[float]) -> Optional[float]:
    if lo is None and hi is None:
        return None
    if lo is None:
        return hi
    if hi is None:
        return lo
    return (lo + hi) / 2.0


def _family(sport: str) -> str:
    key = (sport or "").lower()
    if "swim" in key:
        return "swim"
    if "cycl" in key or "bike" in key or key == "ride":
        return "bike"
    if "run" in key:
        return "run"
    if "tri" in key or "brick" in key:
        return "tri"
    return "other"


def _text(step: Dict[str, Any], *names: str) -> str:
    for name in names:
        value = step.get(name)
        if value is not None and str(value).strip() != "":
            return str(value).strip().lower()
    return ""


def _num(step: Dict[str, Any], *names: str) -> Optional[float]:
    for name in names:
        value = step.get(name)
        if value is None or value == "":
            continue
        try:
            return float(value)
        except (TypeError, ValueError):
            continue
    return None
