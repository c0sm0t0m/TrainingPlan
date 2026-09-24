"""
Static structured workout library (Zwift/Rouvy-style bike templates).
"""
from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path
from typing import Any, Dict, List, Optional, Set

LIBRARY_PATH = Path(__file__).with_name("bike_templates.json")

# Shown in Calendar until the user customizes Settings → Workout library
DEFAULT_CALENDAR_TEMPLATE_IDS: List[str] = [
    "bike-erg-smoke-30",
    "bike-recovery-45",
    "bike-endurance-60",
    "bike-endurance-90",
    "bike-ss-2x15",
    "bike-ss-3x10",
    "bike-ss-2x20-long",
    "bike-thr-3x12",
    "bike-thr-4x8",
    "bike-thr-seiler-4x8",
    "bike-thr-2x20-classic",
    "bike-vo2-5x3",
    "bike-vo2-30-30",
    "bike-rp-3x15",
    "bike-ftp-test-20",
    "bike-openers-40",
]


@lru_cache(maxsize=1)
def load_bike_templates() -> List[Dict[str, Any]]:
    with open(LIBRARY_PATH, encoding="utf-8") as fh:
        data = json.load(fh)
    if not isinstance(data, list):
        raise ValueError("bike_templates.json must be a JSON array")
    return data


def reload_templates() -> List[Dict[str, Any]]:
    load_bike_templates.cache_clear()
    return load_bike_templates()


def list_templates(
    category: Optional[str] = None,
    enabled_ids: Optional[Set[str]] = None,
) -> List[Dict[str, Any]]:
    templates = load_bike_templates()
    if category:
        cat = category.lower().strip()
        templates = [t for t in templates if str(t.get("category", "")).lower() == cat]
    if enabled_ids is not None:
        templates = [t for t in templates if t.get("id") in enabled_ids]
    return [
        {
            "id": t["id"],
            "name": t["name"],
            "category": t.get("category"),
            "description": t.get("description"),
            "sportType": t.get("sportType", "cycling"),
            "workoutType": t.get("workoutType"),
            "durationMinutes": t.get("durationMinutes"),
            "intensityZone": t.get("intensityZone"),
            "targetTSS": t.get("targetTSS"),
            "stepCount": len(t.get("structuredSteps") or []),
        }
        for t in templates
    ]


def get_template(template_id: str) -> Optional[Dict[str, Any]]:
    for t in load_bike_templates():
        if t.get("id") == template_id:
            return t
    return None


def parse_enabled_ids(raw: Optional[str]) -> Optional[List[str]]:
    """Return None if unset (use defaults), else a list (possibly empty)."""
    if raw is None or str(raw).strip() == "":
        return None
    try:
        parsed = json.loads(raw)
    except (json.JSONDecodeError, TypeError):
        return None
    if not isinstance(parsed, list):
        return None
    return [str(x) for x in parsed]


def resolve_calendar_enabled_ids(raw: Optional[str]) -> Set[str]:
    parsed = parse_enabled_ids(raw)
    if parsed is None:
        return set(DEFAULT_CALENDAR_TEMPLATE_IDS)
    return set(parsed)


def all_template_ids() -> List[str]:
    return [t["id"] for t in load_bike_templates()]
