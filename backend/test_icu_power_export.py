import json
from types import SimpleNamespace

from src.utils.icu_workout_converter import (
    build_icu_description,
    structured_steps_to_description,
    workout_to_icu_event,
)


def test_power_pct_range_line():
    steps = [
        {
            "stepOrder": 1,
            "stepType": "work",
            "durationType": "time",
            "durationValue": 15,
            "durationUnit": "minutes",
            "targetType": "power",
            "targetValueLow": 88,
            "targetValueHigh": 92,
            "targetUnit": "%ftp",
            "description": "Sweet spot",
        }
    ]
    text = structured_steps_to_description(steps)
    assert "- 15m 88-92% Sweet spot" in text


def test_power_pct_single_and_fraction():
    steps = [
        {
            "stepType": "work",
            "durationType": "time",
            "durationValue": 5,
            "durationUnit": "minutes",
            "targetType": "power",
            "targetValueLow": 0.95,
            "targetValueHigh": 0.95,
            "targetUnit": "%ftp",
        }
    ]
    text = structured_steps_to_description(steps)
    assert "- 5m 95%" in text


def test_workout_event_sets_power_target():
    workout = SimpleNamespace(
        date=__import__("datetime").date(2026, 9, 24),
        title="ERG Smoke Test",
        sport_type="cycling",
        duration_minutes=30,
        distance_km=None,
        target_tss=28,
        description=None,
        structured_workout_json=json.dumps(
            [
                {
                    "stepType": "work",
                    "durationType": "time",
                    "durationValue": 3,
                    "durationUnit": "minutes",
                    "targetType": "power",
                    "targetValueLow": 88,
                    "targetValueHigh": 92,
                    "targetUnit": "%ftp",
                    "description": "ERG check",
                }
            ]
        ),
    )
    event = workout_to_icu_event(workout, "kinesis-workout-1")
    assert event["type"] == "Ride"
    assert event["target"] == "POWER"
    assert "88-92%" in event["description"]
    assert build_icu_description(workout)
