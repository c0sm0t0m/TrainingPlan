"""
Extract GPS / time-series from Garmin activities.

Quick sync stores only summary metadata in raw_data. FIT time_series is
downloaded on demand (or during include_details sync) and cached.
"""
from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm.attributes import flag_modified

from src.models.garmin_activity import GarminActivity
from src.models.user import User
from src.services.garmin_service import garmin_service
from src.utils.fit_parser import parse_fit_time_series


def get_cached_time_series(raw_data: Any) -> Optional[Dict[str, Any]]:
    """Return parsed FIT payload {time_series, metadata} if present."""
    if not isinstance(raw_data, dict):
        return None
    ts = raw_data.get("time_series")
    if not isinstance(ts, dict) or "error" in ts:
        return None
    # Expected shape from parse_fit_time_series
    if isinstance(ts.get("time_series"), dict):
        return ts
    # Flat arrays stored directly under time_series
    if "latitude" in ts and "longitude" in ts:
        return {"time_series": ts, "metadata": ts.get("metadata") or {}}
    return None


def extract_track_points(
    time_series_payload: Dict[str, Any],
) -> Tuple[List[Dict[str, Any]], bool]:
    """
    Build track point dicts from a parse_fit_time_series payload.
    Returns (points, has_elevation).
    """
    ts = time_series_payload.get("time_series") or {}
    latitudes = ts.get("latitude") or []
    longitudes = ts.get("longitude") or []
    altitudes = ts.get("altitude") or []
    timestamps = ts.get("timestamps") or []

    points: List[Dict[str, Any]] = []
    has_elevation = False
    n = min(len(latitudes), len(longitudes))
    for i in range(n):
        lat = latitudes[i]
        lng = longitudes[i]
        if lat is None or lng is None:
            continue
        ele = altitudes[i] if i < len(altitudes) else None
        timestamp = None
        if i < len(timestamps) and timestamps[i]:
            try:
                timestamp = datetime.fromisoformat(
                    str(timestamps[i]).replace("Z", "+00:00")
                )
            except Exception:
                timestamp = None
        if ele is not None:
            has_elevation = True
        points.append(
            {
                "lat": lat,
                "lng": lng,
                "ele": ele,
                "timestamp": timestamp,
            }
        )
    return points, has_elevation


async def ensure_time_series(
    db: AsyncSession,
    activity: GarminActivity,
    user: User,
) -> Optional[Dict[str, Any]]:
    """
    Return cached time_series, or download+parse FIT and cache it.
    Returns None if unavailable.
    """
    cached = get_cached_time_series(activity.raw_data)
    if cached is not None:
        inner = cached.get("time_series") or {}
        lats = inner.get("latitude") or []
        if any(lat is not None for lat in lats) or not activity.has_polyline:
            return cached
        # Cached but no GPS points — try re-download if polyline expected

    if not user.garmin_connected:
        return cached
    if not user.garmin_oauth1_token or not user.garmin_oauth2_token:
        return cached
    if not activity.garmin_activity_id:
        return cached

    try:
        fit_data = await garmin_service.download_activity_fit(
            user.garmin_oauth1_token,
            user.garmin_oauth2_token,
            int(activity.garmin_activity_id),
        )
        parsed = parse_fit_time_series(fit_data)
        if "error" in parsed:
            print(
                f"⚠️ FIT parse failed for activity {activity.id}: {parsed['error']}",
                flush=True,
            )
            return cached

        raw = dict(activity.raw_data or {})
        raw["time_series"] = parsed
        activity.raw_data = raw
        flag_modified(activity, "raw_data")
        # Mark polyline if GPS present
        inner = parsed.get("time_series") or {}
        if any(lat is not None for lat in (inner.get("latitude") or [])):
            activity.has_polyline = True
        await db.commit()
        await db.refresh(activity)
        return parsed
    except Exception as e:
        print(
            f"⚠️ FIT download failed for activity {activity.id}: {e}",
            flush=True,
        )
        return cached
