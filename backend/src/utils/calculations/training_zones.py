"""
Training Zone Calculations

Implements various zone calculation methods from TrainingPeaks and other sources.
"""
from typing import List, Dict, Optional


# Power Zones (Cycling)

def calculate_power_zones_coggan(ftp: int) -> List[Dict]:
    """
    Andy Coggan 6-zone power model (TrainingPeaks default).
    Matches TrainingPeaks auto-calculation exactly.
    """
    # TrainingPeaks uses rounded boundaries with specific percentages
    z1_max = round(ftp * 0.555)
    z2_max = round(ftp * 0.755)
    z3_max = round(ftp * 0.905)
    z4_max = round(ftp * 1.057)
    z5_max = round(ftp * 1.208)
    z6_min = round(ftp * 1.212)
    
    return [
        {"zone": 1, "name": "Active Recovery", "min": 10, "max": z1_max},
        {"zone": 2, "name": "Endurance", "min": z1_max + 1, "max": z2_max},
        {"zone": 3, "name": "Tempo", "min": z2_max + 1, "max": z3_max},
        {"zone": 4, "name": "Lactate Threshold", "min": z3_max + 1, "max": z4_max},
        {"zone": 5, "name": "VO2 Max", "min": z4_max + 1, "max": z5_max},
        {"zone": 6, "name": "Anaerobic Capacity", "min": z6_min, "max": 2000}
    ]


# Heart Rate Zones

def _contiguous_hr_zones(boundaries: List[int], names: List[str], max_hr: int) -> List[Dict]:
    """
    Build contiguous HR zones from upper-bound percentages.

    Independent int(threshold * pct) cutoffs leave 1–2 bpm gaps; activities
    with avg HR in those gaps were silently dropped from zone distribution.
    """
    zones: List[Dict] = []
    prev_max = -1
    for i, (upper, name) in enumerate(zip(boundaries, names)):
        # Last zone always extends to max_hr
        zone_max = max_hr if i == len(boundaries) - 1 else min(upper, max_hr)
        zone_min = 0 if i == 0 else prev_max + 1
        if zone_min > zone_max:
            zone_max = zone_min
        zones.append({"zone": i + 1, "name": name, "min": zone_min, "max": zone_max})
        prev_max = zone_max
    return zones


def calculate_hr_zones_friel(threshold_hr: int, max_hr: int) -> List[Dict]:
    """Joe Friel 7-zone HR model (contiguous boundaries)."""
    boundaries = [
        int(threshold_hr * 0.82),
        int(threshold_hr * 0.89),
        int(threshold_hr * 0.94),
        int(threshold_hr * 0.99),
        int(threshold_hr * 1.02),
        int(threshold_hr * 1.06),
        max_hr,
    ]
    names = [
        "Recovery",
        "Aerobic",
        "Tempo",
        "Sub-Threshold",
        "Super-Threshold",
        "Aerobic Capacity",
        "Anaerobic Capacity",
    ]
    return _contiguous_hr_zones(boundaries, names, max_hr)


def calculate_hr_zones_coggan(threshold_hr: int, max_hr: int) -> List[Dict]:
    """Coggan 5-zone HR model (contiguous boundaries)."""
    boundaries = [
        int(threshold_hr * 0.82),
        int(threshold_hr * 0.89),
        int(threshold_hr * 0.94),
        int(threshold_hr * 1.05),
        max_hr,
    ]
    names = [
        "Active Recovery",
        "Endurance",
        "Tempo",
        "Lactate Threshold",
        "VO2 Max",
    ]
    return _contiguous_hr_zones(boundaries, names, max_hr)


def classify_hr_to_zone(avg_hr: int, zones: List[Dict]) -> Optional[int]:
    """Return zone number for avg_hr, or None if outside all zones."""
    for zone in zones:
        if zone["min"] <= avg_hr <= zone["max"]:
            return zone["zone"]
    return None


# Running Pace Zones

def calculate_pace_zones_friel(threshold_pace: int) -> List[Dict]:
    """
    Joe Friel 7-zone running pace model.
    
    Args:
        threshold_pace: Threshold pace in seconds per km
        
    Returns:
        List of zones with min/max pace in seconds per km (slower = higher number)
    """
    return [
        {"zone": 1, "name": "Recovery", "min": int(threshold_pace / 0.75), "max": 9999},  # >133% slower
        {"zone": 2, "name": "Aerobic", "min": int(threshold_pace / 0.85), "max": int(threshold_pace / 0.76)},
        {"zone": 3, "name": "Tempo", "min": int(threshold_pace / 0.90), "max": int(threshold_pace / 0.86)},
        {"zone": 4, "name": "Sub-Threshold", "min": int(threshold_pace / 0.96), "max": int(threshold_pace / 0.91)},
        {"zone": 5, "name": "Super-Threshold", "min": int(threshold_pace / 1.02), "max": int(threshold_pace / 0.97)},
        {"zone": 6, "name": "Aerobic Capacity", "min": int(threshold_pace / 1.10), "max": int(threshold_pace / 1.03)},
        {"zone": 7, "name": "Anaerobic Capacity", "min": 0, "max": int(threshold_pace / 1.11)}  # <91% faster
    ]


def calculate_pace_zones_8020(threshold_pace: int) -> List[Dict]:
    """80/20 Running 7-zone pace model."""
    return [
        {"zone": 1, "name": "Low Aerobic", "min": int(threshold_pace / 0.74), "max": 9999},
        {"zone": 2, "name": "Moderate Aerobic", "min": int(threshold_pace / 0.81), "max": int(threshold_pace / 0.75)},
        {"zone": 3, "name": "High Aerobic", "min": int(threshold_pace / 0.89), "max": int(threshold_pace / 0.82)},
        {"zone": 4, "name": "Threshold", "min": int(threshold_pace / 1.00), "max": int(threshold_pace / 0.90)},
        {"zone": 5, "name": "VO2 Max", "min": int(threshold_pace / 1.08), "max": int(threshold_pace / 1.01)},
        {"zone": 6, "name": "Speed", "min": int(threshold_pace / 1.18), "max": int(threshold_pace / 1.09)},
        {"zone": 7, "name": "Sprint", "min": 0, "max": int(threshold_pace / 1.19)}
    ]


def calculate_pace_zones_cts(threshold_pace: int) -> List[Dict]:
    """
    CTS (Carmichael Training Systems) 7-zone running pace model.
    
    Based on lactate threshold pace, commonly used for endurance training.
    
    Args:
        threshold_pace: Threshold pace in seconds per km
        
    Returns:
        List of zones with min/max pace in seconds per km (slower = higher number)
    """
    return [
        {"zone": 1, "name": "Recovery", "min": int(threshold_pace / 0.70), "max": 9999},  # >143% slower
        {"zone": 2, "name": "Endurance", "min": int(threshold_pace / 0.84), "max": int(threshold_pace / 0.71)},
        {"zone": 3, "name": "Tempo", "min": int(threshold_pace / 0.91), "max": int(threshold_pace / 0.85)},
        {"zone": 4, "name": "Steady State", "min": int(threshold_pace / 0.97), "max": int(threshold_pace / 0.92)},
        {"zone": 5, "name": "Threshold", "min": int(threshold_pace / 1.03), "max": int(threshold_pace / 0.98)},
        {"zone": 6, "name": "VO2 Max", "min": int(threshold_pace / 1.12), "max": int(threshold_pace / 1.04)},
        {"zone": 7, "name": "Anaerobic", "min": 0, "max": int(threshold_pace / 1.13)}  # <89% faster
    ]


# Swimming Pace Zones

def calculate_swim_zones_friel(threshold_pace_100m: int) -> List[Dict]:
    """
    Joe Friel 7-zone swimming pace model.
    
    Args:
        threshold_pace_100m: Threshold pace in seconds per 100m
        
    Returns:
        List of zones with min/max pace in seconds per 100m (slower = higher number)
    """
    return [
        {"zone": 1, "name": "Recovery", "min": int(threshold_pace_100m / 0.75), "max": 9999},
        {"zone": 2, "name": "Aerobic", "min": int(threshold_pace_100m / 0.85), "max": int(threshold_pace_100m / 0.76)},
        {"zone": 3, "name": "Tempo", "min": int(threshold_pace_100m / 0.90), "max": int(threshold_pace_100m / 0.86)},
        {"zone": 4, "name": "Sub-Threshold", "min": int(threshold_pace_100m / 0.96), "max": int(threshold_pace_100m / 0.91)},
        {"zone": 5, "name": "Super-Threshold", "min": int(threshold_pace_100m / 1.02), "max": int(threshold_pace_100m / 0.97)},
        {"zone": 6, "name": "Aerobic Capacity", "min": int(threshold_pace_100m / 1.10), "max": int(threshold_pace_100m / 1.03)},
        {"zone": 7, "name": "Anaerobic Capacity", "min": 0, "max": int(threshold_pace_100m / 1.11)}
    ]


# Zone Calculation Dispatcher

def calculate_zones(
    zone_type: str,
    method: str,
    threshold_value: int,
    max_hr: Optional[int] = None
) -> List[Dict]:
    """
    Calculate training zones based on type and method.
    
    Args:
        zone_type: 'power', 'hr_cycling', 'hr_running', 'pace_running', 'pace_swimming'
        method: Calculation method (e.g., 'coggan', 'friel', etc.)
        threshold_value: FTP, threshold HR, or threshold pace
        max_hr: Required for HR zones
        
    Returns:
        List of zone dictionaries
    """
    if zone_type == 'power':
        if method == 'coggan':
            return calculate_power_zones_coggan(threshold_value)
        elif method == 'coggan_6':
            return calculate_power_zones_coggan_6(threshold_value)
        # Add more power methods as needed
        
    elif zone_type == 'hr':
        if not max_hr:
            raise ValueError("max_hr required for HR zone calculation")
        if method == 'friel':
            return calculate_hr_zones_friel(threshold_value, max_hr)
        elif method == 'coggan':
            return calculate_hr_zones_coggan(threshold_value, max_hr)
        # Add more HR methods
        
    elif zone_type == 'pace_running':
        if method == 'friel':
            return calculate_pace_zones_friel(threshold_value)
        elif method == '8020':
            return calculate_pace_zones_8020(threshold_value)
        elif method == 'cts':
            return calculate_pace_zones_cts(threshold_value)
        # Add more pace methods
        
    elif zone_type == 'pace_swimming':
        if method == 'friel':
            return calculate_swim_zones_friel(threshold_value)
        # Add more swim methods
    
    raise ValueError(f"Unknown zone type or method: {zone_type}, {method}")


def format_pace_for_display(seconds: int) -> str:
    """Convert pace in seconds to min:sec format."""
    if seconds <= 0:
        return "0:00"
    minutes = seconds // 60
    secs = seconds % 60
    return f"{minutes}:{secs:02d}"
