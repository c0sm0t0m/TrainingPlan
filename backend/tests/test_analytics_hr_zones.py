"""
Unit tests for analytics HR zone distribution and sport filtering.

Covers regressions:
- Garmin bike types (road_biking, gravel_cycling) must match cycling filter
- Bike activities must use cycling LTHR (not running) for zone classification
- Friel HR zones must be contiguous (no silent bpm gaps)
"""
from types import SimpleNamespace

from src.utils.sport_types import matches_sport_filter, normalize_sport
from src.utils.calculations.training_zones import (
    calculate_hr_zones_friel,
    calculate_hr_zones_coggan,
    classify_hr_to_zone,
)


BIKE_TYPES = [
    ("road_biking", "cycling"),
    ("gravel_cycling", "cycling"),
    ("indoor_cycling", "cycling"),
    ("virtual_ride", "cycling"),
    ("mountain_biking", "cycling"),
    ("cycling", "cycling"),
]

OTHER_TYPES = [
    ("running", "running"),
    ("trail_running", "running"),
    ("lap_swimming", "swimming"),
    ("open_water_swimming", "swimming"),
    ("strength_training", "strength"),
    ("tennis_v2", "tennisv2"),
    ("multi_sport", "triathlon"),
]


class TestNormalizeSport:
    def test_normalize_sport_families(self):
        for raw, expected in BIKE_TYPES + OTHER_TYPES:
            assert normalize_sport(raw) == expected, raw

    def test_cycling_filter_includes_road_and_gravel(self):
        assert matches_sport_filter("road_biking", "cycling")
        assert matches_sport_filter("gravel_cycling", "cycling")
        assert matches_sport_filter("indoor_cycling", "cycling")
        assert matches_sport_filter("mountain_biking", "cycling")
        assert not matches_sport_filter("running", "cycling")
        assert not matches_sport_filter("road_biking", "running")

    def test_road_biking_not_swallowed_by_run_token(self):
        """Regression: stripping '_' makes 'road_biking' → 'roadbiking'.
        'bike' is NOT a substring of 'roadbiking' (no 'e'); must use 'bik'.
        """
        assert normalize_sport("road_biking") == "cycling"
        assert normalize_sport("mountain_biking") == "cycling"
        assert "bike" not in "road_biking".replace("_", "")
        assert "bik" in "road_biking".replace("_", "")

    def test_other_excludes_main_endurance_sports(self):
        assert matches_sport_filter("tennis_v2", "other")
        assert matches_sport_filter("strength_training", "other")
        assert not matches_sport_filter("road_biking", "other")
        assert not matches_sport_filter("running", "other")
        assert not matches_sport_filter("lap_swimming", "other")


class TestHrZonesContiguous:
    def test_friel_zones_cover_every_bpm(self):
        max_hr = 190
        for threshold in (150, 160, 165, 170, 175):
            zones = calculate_hr_zones_friel(threshold, max_hr)
            assert zones[0]["min"] == 0
            assert zones[-1]["max"] == max_hr
            for i in range(1, len(zones)):
                assert zones[i]["min"] == zones[i - 1]["max"] + 1
            for hr in range(0, max_hr + 1):
                assert classify_hr_to_zone(hr, zones) is not None

    def test_coggan_zones_contiguous(self):
        zones = calculate_hr_zones_coggan(165, 180)
        for i in range(1, len(zones)):
            assert zones[i]["min"] == zones[i - 1]["max"] + 1


class TestSportSpecificZoneClassification:
    """Reproduce the Over-Unders bug: avg HR 133 with run LTHR 165 → Recovery;
    with bike LTHR 160 → Aerobic."""

    def test_over_under_avg_hr_not_recovery_on_bike_zones(self):
        run_zones = calculate_hr_zones_friel(165, 180)
        bike_zones = calculate_hr_zones_friel(160, 180)
        avg_hr = 133  # Over-Unders 4×8 indoor_cycling from 2026-09-24

        assert classify_hr_to_zone(avg_hr, run_zones) == 1  # Recovery (wrong for bike)
        assert classify_hr_to_zone(avg_hr, bike_zones) == 2  # Aerobic

    def test_classify_activity_like_endpoint(self):
        """Mirrors analytics._threshold_hr_for_sport + classify path."""
        user = SimpleNamespace(
            running_threshold_hr=165,
            cycling_threshold_hr=160,
            swim_threshold_hr=None,
            max_hr=180,
        )

        def threshold_for(family: str):
            if family == "cycling":
                return user.cycling_threshold_hr or user.running_threshold_hr
            return user.running_threshold_hr

        activities = [
            SimpleNamespace(activity_type="indoor_cycling", average_hr=133),
            SimpleNamespace(activity_type="road_biking", average_hr=140),
            SimpleNamespace(activity_type="running", average_hr=140),
        ]

        bike_only = [
            a for a in activities if matches_sport_filter(a.activity_type, "cycling")
        ]
        assert len(bike_only) == 2  # includes road_biking

        bike_zones = calculate_hr_zones_friel(threshold_for("cycling"), user.max_hr)
        zone_counts = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0, 6: 0, 7: 0}
        for a in bike_only:
            z = classify_hr_to_zone(a.average_hr, bike_zones)
            zone_counts[z] += 1

        # Neither bike sits in Recovery when using cycling LTHR
        assert zone_counts[1] == 0
        assert zone_counts[2] == 2
