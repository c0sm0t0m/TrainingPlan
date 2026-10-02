"""True TSS and run paces from threshold, not the flat zone guess."""
from src.utils.calculations.planned_load import (
    AthleteThresholds,
    prepare_planned_session,
)

THRESHOLDS = AthleteThresholds(
    run_pace_sec_per_km=285,  # 4:45
    ftp_watts=240,
    swim_pace_sec_per_100m=110,
)


def _step(step_type, minutes, low, high, target="heart_rate", unit="bpm", duration_unit="minutes"):
    return {
        "step_type": step_type,
        "duration_type": "time",
        "duration_value": minutes,
        "duration_unit": duration_unit,
        "target_type": target,
        "target_value_low": low,
        "target_value_high": high,
        "target_unit": unit,
        "description": step_type,
    }


def test_easy_run_pace_and_tss_from_threshold():
    steps = [
        _step("warmup", 8, 95, 110),
        _step("work", 37, 108, 134),
        _step("cooldown", 5, 95, 110),
    ]
    updated, tss, distance, label = prepare_planned_session(
        steps,
        sport="running",
        zone="zone2",
        workout_type="easy",
        thresholds=THRESHOLDS,
    )
    work = updated[1]
    assert work["target_type"] == "pace"
    assert work["target_unit"] == "sec/km"
    # 76–84% of 4:45 → 6:15–5:39
    assert work["target_value_low"] == 339
    assert work["target_value_high"] == 375
    assert label == "6:15–5:39/km"
    assert tss >= 45
    assert tss != 27
    assert distance == 8


def test_threshold_rep_is_near_4_45():
    steps = [
        _step("warmup", 12, 95, 107),
        _step("work", 20, 153, 165, ),
        _step("cooldown", 8, 95, 107),
    ]
    steps[1]["description"] = "20-min threshold test"
    updated, tss, _distance, label = prepare_planned_session(
        steps,
        sport="running",
        zone="zone4",
        workout_type="interval",
        thresholds=THRESHOLDS,
    )
    work = updated[1]
    # 95–105% of 4:45 → 5:00–4:31
    assert work["target_value_low"] == 271
    assert work["target_value_high"] == 300
    assert label == "5:00–4:31/km"
    assert tss > 30


def test_bike_tss_uses_ftp_percent_not_flat_rate():
    steps = [
        _step("warmup", 15, 40, 55, target="power", unit="%ftp"),
        _step("work", 60, 56, 75, target="power", unit="%ftp"),
        _step("cooldown", 11, 40, 55, target="power", unit="%ftp"),
    ]
    _updated, tss, distance, label = prepare_planned_session(
        steps,
        sport="cycling",
        zone="zone2",
        workout_type="easy",
        thresholds=THRESHOLDS,
    )
    # 60 min at 65.5% is ~43, plus easy spin. The old plan scored this shape ~47 for 86 min.
    assert tss > 47
    assert distance is None
    assert label is None


def test_stride_stays_at_or_below_105_percent():
    step = _step("work", 20, 153, 165, duration_unit="seconds")
    step["description"] = "Stride 1/6"
    updated, _tss, _distance, _label = prepare_planned_session(
        [step],
        sport="running",
        zone="zone2",
        workout_type="easy",
        thresholds=THRESHOLDS,
    )
    assert updated[0]["target_value_low"] == 271  # 4:31, 105%
    assert updated[0]["target_value_high"] == 285  # 4:45
