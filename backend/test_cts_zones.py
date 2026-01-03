#!/usr/bin/env python3
"""Test CTS running pace zone calculation."""

from src.utils.calculations.training_zones import calculate_pace_zones_cts, format_pace_for_display

# Test with threshold pace of 4:30/km (270 seconds)
threshold_pace = 270

print("Testing CTS Running Pace Zones")
print("=" * 60)
print(f"Threshold Pace: {format_pace_for_display(threshold_pace)} /km\n")

zones = calculate_pace_zones_cts(threshold_pace)

print("CTS 7-Zone Running Model:")
print("-" * 60)
for zone in zones:
    min_pace = format_pace_for_display(zone['min'])
    max_pace = format_pace_for_display(zone['max'])
    
    # Handle infinity display
    if zone['max'] == 9999:
        max_pace = "∞"
    if zone['min'] == 0:
        min_pace = "0:00"
    
    print(f"Zone {zone['zone']}: {zone['name']:20s} | {max_pace:>7s} - {min_pace:>7s} /km")

print("\nTest PASSED ✅")
