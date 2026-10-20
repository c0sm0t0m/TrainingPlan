"""Suggested vs actual comparison for a matched activity."""
from datetime import datetime
from types import SimpleNamespace

from src.services.plan_vs_actual import build_plan_vs_actual


def _workout(**kwargs):
    base = dict(
        date="2026-09-29",
        sport_type="cycling",
        workout_type="tempo",
        intensity_zone="zone2",
        duration_minutes=60,
        distance_km=30,
        target_tss=50,
        structured_workout_json=None,
    )
    base.update(kwargs)
    return SimpleNamespace(**base)


def _activity(**kwargs):
    base = dict(
        activity_type="cycling",
        start_time_local=datetime(2026, 10, 2, 18, 0),
        duration_seconds=72 * 60,
        moving_duration_seconds=70 * 60,
        distance_meters=32000,
        calculated_tss=78,
        intensity_factor=0.92,
        average_power_watts=210,
        normalized_power_watts=245,
        threshold_power_watts=250,
        average_speed_mps=32 / 3.6,
    )
    base.update(kwargs)
    return SimpleNamespace(**base)


def test_off_plan_day_and_intensity_too_high():
    steps = [
        {
            "durationValue": 60,
            "durationUnit": "minutes",
            "targetType": "power",
            "targetValueLow": 65,
            "targetValueHigh": 75,
            "targetUnit": "%ftp",
        }
    ]
    result = build_plan_vs_actual(
        _workout(structured_workout_json=__import__("json").dumps(steps)),
        _activity(),
        ftp=250,
    )
    assert result["performed_on_planned_day"] is False
    assert result["actual_date"] == "2026-10-02"
    by_label = {row["label"]: row for row in result["rows"]}
    assert by_label["Intensity"]["tone"] == "high"
    assert by_label["Intensity"]["delta"] == "too high"
    assert by_label["Power"]["planned"] == "175 W"
    assert by_label["Power"]["actual"] == "245 W"
    assert by_label["Power"]["delta"] == "too high"
    assert "Speed" not in by_label
    assert "Distance" not in by_label
    assert "Duration" in by_label


def test_same_day_on_target_zone():
    result = build_plan_vs_actual(
        _workout(date="2026-10-02"),
        _activity(
            start_time_local=datetime(2026, 10, 2, 7, 0),
            intensity_factor=0.70,
            normalized_power_watts=175,
            calculated_tss=50,
            duration_seconds=60 * 60,
            moving_duration_seconds=60 * 60,
            distance_meters=30000,
        ),
        ftp=250,
    )
    assert result["performed_on_planned_day"] is True
    intensity = next(row for row in result["rows"] if row["label"] == "Intensity")
    assert intensity["planned"].startswith("Z2")
    assert intensity["delta"] == "on target"
    by_label = {row["label"]: row for row in result["rows"]}
    assert by_label["Speed"]["planned"] == "30.0 km/h"
    assert by_label["Distance"]["delta"] == "on target"
