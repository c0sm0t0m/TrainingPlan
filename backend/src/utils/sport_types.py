"""
Coarse sport-family helpers for Garmin activity types.

Garmin uses many type keys (road_biking, gravel_cycling, indoor_cycling, …).
Analytics, CTL, and matching must classify via family, not brittle exact lists.
"""
from __future__ import annotations

from typing import Optional


def normalize_sport(raw: Optional[str]) -> str:
    """Map Garmin / Kinesis sport strings to a coarse family."""
    s = (raw or "").lower().replace("_", "").replace("-", "").replace(" ", "")
    # Check cycling before running: "road_biking" → "roadbiking" contains neither
    # "bike" nor "run", but does contain "bik". Prefer "bik" over "bike".
    if any(k in s for k in ("cycl", "bik", "ride", "gravel", "mtb", "ebike", "virtualride")):
        return "cycling"
    if any(k in s for k in ("run", "trail", "treadmill", "virtualrun")):
        return "running"
    if "swim" in s or "pool" in s or "openwater" in s:
        return "swimming"
    if any(k in s for k in ("strength", "weight", "gym", "fitness", "crossfit")):
        return "strength"
    if "walk" in s or "hike" in s:
        return "walking"
    if "tri" in s or "multisport" in s:
        return "triathlon"
    return s or "other"


def matches_sport_filter(activity_type: Optional[str], sport_filter: str) -> bool:
    """
    Return True if activity_type belongs to sport_filter.

    sport_filter: all | running | cycling | swimming | other
    """
    if not sport_filter or sport_filter == "all":
        return True

    family = normalize_sport(activity_type)
    filter_key = sport_filter.lower()

    if filter_key in ("running", "cycling", "swimming"):
        return family == filter_key

    if filter_key == "other":
        return family not in ("running", "cycling", "swimming")

    return family == filter_key
