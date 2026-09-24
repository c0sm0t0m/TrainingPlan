"""
Periodization phase splitting for AI training plan generation.
"""
from datetime import date, timedelta
from typing import Any, Dict, List, Optional


def compute_plan_phases(start_date: date, end_date: date) -> List[Dict[str, Any]]:
    """
    Split a plan window into importable phases sized for LLM context limits.

    Short plans (<=14w): Build + Taper
    Medium (<=26w): Base + Build + Taper
    Long (>26w): Base + Build + Race Specific + Taper
    """
    if end_date <= start_date:
        end_date = start_date + timedelta(weeks=12)

    duration_weeks = max(1, (end_date - start_date).days // 7)
    taper_weeks = 2 if duration_weeks < 20 else 3

    if duration_weeks <= 14:
        remaining = max(1, duration_weeks - taper_weeks)
        defs = [
            ("Build", remaining, "Aerobic + quality work toward race"),
            ("Taper", taper_weeks, "Volume −50–70%; keep short race-pace efforts"),
        ]
    elif duration_weeks <= 26:
        remaining = max(2, duration_weeks - taper_weeks)
        base_w = max(1, remaining // 2)
        build_w = max(1, remaining - base_w)
        defs = [
            ("Base", base_w, "High aerobic volume, technique, introduce strength"),
            ("Build", build_w, "Add threshold; maintain volume; bricks if triathlon"),
            ("Taper", taper_weeks, "Volume −50–70%; keep short race-pace efforts"),
        ]
    else:
        remaining = max(3, duration_weeks - taper_weeks)
        base_w = max(6, int(remaining * 0.30))
        race_w = max(4, int(remaining * 0.30))
        build_w = max(1, remaining - base_w - race_w)
        defs = [
            ("Base", base_w, "High aerobic volume, technique, strength 1×/week"),
            ("Build", build_w, "Add threshold bike/run; maintain volume; weekly bricks"),
            ("Race Specific", race_w, "Race sims, longer bricks, sharpen execution"),
            ("Taper", taper_weeks, "Volume −50–70%; short race-pace openers into race week"),
        ]

    phases: List[Dict[str, Any]] = []
    cursor = start_date
    for idx, (name, weeks, focus) in enumerate(defs):
        is_last = idx == len(defs) - 1
        if is_last:
            phase_end = end_date
        else:
            phase_end = cursor + timedelta(weeks=weeks) - timedelta(days=1)
            if phase_end >= end_date:
                phase_end = end_date - timedelta(days=1)
        if phase_end < cursor:
            phase_end = cursor

        actual_weeks = max(1, ((phase_end - cursor).days // 7) + 1)
        phases.append({
            "index": idx,
            "id": f"phase_{idx + 1}",
            "name": name,
            "focus": focus,
            "weekStart": 0,
            "weekEnd": 0,
            "weeks": actual_weeks,
            "startDate": cursor.isoformat(),
            "endDate": phase_end.isoformat(),
            "isLast": is_last,
        })
        cursor = phase_end + timedelta(days=1)

    # Fill week numbers
    week_cursor = 1
    for p in phases:
        p["weekStart"] = week_cursor
        p["weekEnd"] = week_cursor + p["weeks"] - 1
        week_cursor = p["weekEnd"] + 1

    return phases


def get_phase(
    phases: List[Dict[str, Any]],
    phase_index: Optional[int],
) -> Optional[Dict[str, Any]]:
    if not phases:
        return None
    if phase_index is None:
        return phases[0]
    if phase_index < 0 or phase_index >= len(phases):
        return None
    return phases[phase_index]


def distance_session_ceilings(event_distance: str) -> Dict[str, str]:
    """
    Scale key session lengths to event distance so IM-centric coaches don't
    prescribe full-Ironman loads for Olympic / 70.3 goals.
    """
    d = (event_distance or "").lower()

    if any(x in d for x in ("ironman 70.3", "70.3", "half iron", "half-iron", "middle")):
        return {
            "label": "Half Ironman / 70.3",
            "long_bike": "3.0–4.5 h @ Z2–Z3 (not 5–7 h)",
            "brick": "2.5–3.5 h bike + 30–60 min run",
            "race_sim": "~3–4 h bike + 45–75 min run at goal effort",
            "long_run": "90–150 min progressive / aerobic",
            "heat": "Mild heat prep only if race climate warrants; skip Kona-style camps",
        }
    if any(x in d for x in ("olympic", "olympisch", "standard distance", "intl distance")):
        return {
            "label": "Olympic / Standard",
            "long_bike": "2–3 h @ Z2–Z3",
            "brick": "90–150 min bike + 20–40 min run",
            "race_sim": "~2 h bike + 30–45 min run at goal effort",
            "long_run": "60–100 min",
            "heat": "Usually not required",
        }
    if any(x in d for x in ("sprint",)):
        return {
            "label": "Sprint",
            "long_bike": "90–150 min",
            "brick": "60–90 min bike + 15–25 min run",
            "race_sim": "race-pace openers + short bricks",
            "long_run": "45–75 min",
            "heat": "Usually not required",
        }
    if any(x in d for x in ("full iron", "ironman", "140.6", "long course")) and "70.3" not in d:
        return {
            "label": "Full Ironman",
            "long_bike": "5–7 h @ IM pace with nutrition practice",
            "brick": "4 h bike + 60–90 min run (late build)",
            "race_sim": "5–6 h bike + 2–3 h run (peak camps)",
            "long_run": "2–3 h",
            "heat": "Heat adaptation if racing hot (e.g. Kona)",
        }
    if any(x in d for x in ("marathon", "42")):
        return {
            "label": "Marathon",
            "long_bike": "N/A (run-focused)",
            "brick": "N/A",
            "race_sim": "28–35 km progressive long run",
            "long_run": "build to 30–35 km",
            "heat": "As climate requires",
        }
    if any(x in d for x in ("half marathon", "half-marathon", "21.1")):
        return {
            "label": "Half Marathon",
            "long_bike": "N/A",
            "brick": "N/A",
            "race_sim": "16–20 km with race-pace segments",
            "long_run": "build to 18–22 km",
            "heat": "As climate requires",
        }

    return {
        "label": "General endurance",
        "long_bike": "Scale long sessions to ~50–70% of race duration",
        "brick": "If triathlon: progressive bricks peaking near race demands",
        "race_sim": "Practice goal pacing + nutrition under fatigue",
        "long_run": "Progressive long sessions appropriate to event",
        "heat": "Only if race climate requires",
    }


def format_pace_min_per_km(pace: Optional[float]) -> Optional[str]:
    """Format threshold pace stored as min/km (e.g. 4.8 → 4:48 /km)."""
    if pace is None or pace <= 0:
        return None
    # Detect accidental sec/km values (> 20 is not a sane min/km)
    if pace > 20:
        pace = pace / 60.0
    if pace < 2.0 or pace > 12.0:
        return None  # implausible — omit rather than poison the prompt
    minutes = int(pace)
    seconds = int(round((pace - minutes) * 60))
    if seconds == 60:
        minutes += 1
        seconds = 0
    return f"{minutes}:{seconds:02d} min/km"
