"""
Training Stress Score (TSS) Calculator

TSS is a way to quantify training load. It takes into account:
- Duration of the workout
- Intensity of the workout

Formula variants:
- Running TSS (rTSS): Based on pace and heart rate
- Cycling TSS: Based on power (Normalized Power)
- Swimming TSS (sTSS): Based on pace
- Generic TSS: Based on duration and perceived intensity
"""
from typing import Any, Optional


def calculate_running_tss(
    duration_minutes: int,
    average_hr: Optional[int] = None,
    threshold_hr: int = 180,
    average_pace_min_per_km: Optional[float] = None,
    threshold_pace_min_per_km: Optional[float] = None,
) -> tuple[float, Optional[float]]:
    """
    Calculate running TSS (rTSS) and Intensity Factor (IF).
    
    Fallback hierarchy (matches TrainingPeaks):
    1. Pace-based with elevation (NGP) - most accurate when time-series elevation available
    2. HR-based - accurate fallback using lactate threshold HR
    3. Duration-based estimate
    
    Note: TrainingPeaks uses Normalized Graded Pace (NGP) which accounts for
    elevation changes using time-series elevation data. When NGP is available,
    it's more accurate than HR-based. We currently don't have time-series
    elevation data, so HR-based is used as the primary method.
    
    Args:
        duration_minutes: Duration of the run in minutes
        average_hr: Average heart rate during the run
        threshold_hr: Lactate threshold heart rate (default 180)
        average_pace_min_per_km: Average pace in minutes per kilometer
        threshold_pace_min_per_km: Threshold pace in minutes per kilometer (e.g., 4.0 = 4:00/km)
        
    Returns:
        Tuple of (TSS value, Intensity Factor or None)
    """
    # Priority 1: Pace-based (most accurate with NGP/elevation data)
    # TODO: When time-series elevation data is available, calculate NGP and use pace-based
    # For now, this is only used if pace data is available without elevation adjustment
    if average_pace_min_per_km and threshold_pace_min_per_km and threshold_pace_min_per_km > 0:
        # Pace-based rTSS (inverse - faster pace = higher intensity)
        # If average pace is 5:00/km and threshold is 4:00/km, IF = 4/5 = 0.8
        # This is equivalent to: speed/threshold_speed
        intensity_factor = threshold_pace_min_per_km / average_pace_min_per_km
        duration_hours = duration_minutes / 60
        tss = duration_hours * (intensity_factor ** 2) * 100
        return (tss, intensity_factor)
    
    # Priority 2: HR-based (accurate using lactate threshold HR)
    elif average_hr and threshold_hr and threshold_hr > 0:
        # HR-based rTSS: TSS = (duration_hours * intensity_factor^2 * 100)
        intensity_factor = average_hr / threshold_hr
        duration_hours = duration_minutes / 60
        tss = duration_hours * (intensity_factor ** 2) * 100
        return (tss, intensity_factor)
    
    # Priority 3: Duration-based estimate (assume moderate intensity)
    return (duration_minutes * 0.7, None)  # ~42 TSS per hour at moderate pace


def calculate_cycling_tss(
    duration_minutes: int,
    normalized_power: Optional[float] = None,
    threshold_power: Optional[float] = None,
    average_hr: Optional[int] = None,
    threshold_hr: int = 180,
) -> tuple[float, Optional[float]]:
    """
    Calculate cycling TSS and Intensity Factor (IF).
    
    Fallback hierarchy:
    1. Power-based (FTP) - most accurate
    2. HR-based - if no power meter
    3. Duration-based estimate
    
    Args:
        duration_minutes: Duration of the ride in minutes
        normalized_power: Normalized Power (NP) in watts
        threshold_power: Functional Threshold Power (FTP) in watts
        average_hr: Average heart rate (fallback if no power)
        threshold_hr: Lactate threshold heart rate
        
    Returns:
        Tuple of (TSS value, Intensity Factor or None)
    """
    # Priority 1: Power-based TSS (most accurate)
    if normalized_power and threshold_power and threshold_power > 0:
        # Power-based TSS formula: TSS = (duration_hours * NP * IF) / (FTP * 3600) * 100
        # Simplified: TSS = duration_hours * (IF^2) * 100
        # where IF = NP / FTP
        intensity_factor = normalized_power / threshold_power
        duration_hours = duration_minutes / 60
        tss = duration_hours * (intensity_factor ** 2) * 100
        return (tss, intensity_factor)
    
    # Priority 2: HR-based fallback
    elif average_hr and threshold_hr and threshold_hr > 0:
        # HR-based fallback
        intensity_factor = average_hr / threshold_hr
        duration_hours = duration_minutes / 60
        tss = duration_hours * (intensity_factor ** 2) * 100
        return (tss, intensity_factor)
    
    # Priority 3: Duration-based estimate
    return (duration_minutes * 0.8, None)  # ~48 TSS per hour at moderate pace


def calculate_swimming_tss(
    duration_minutes: int,
    distance_meters: Optional[float] = None,
    threshold_pace_min_per_100m: Optional[float] = None,
) -> tuple[float, Optional[float]]:
    """
    Calculate swimming TSS (sTSS) and Intensity Factor (IF) using TrainingPeaks formula.
    
    Swimming TSS uses IF³ (cubed) instead of IF² because water resistance
    causes physiological stress to increase faster than in running/cycling.
    
    Formula: sTSS = (IF³) × hours × 100
    Where:
        - IF = Intensity Factor = NSS / FTP
        - NSS = Normalized Swim Speed (meters/minute)
        - FTP = Functional Threshold Pace (meters/minute)
    
    Reference: https://www.trainingpeaks.com/learn/articles/calculating-swimming-tss-score/
    
    Args:
        duration_minutes: Duration of the swim in minutes (excluding rest)
        distance_meters: Distance swum in meters
        threshold_pace_min_per_100m: User's threshold pace in minutes per 100m (from settings).
                                      If None, defaults to 1.5 min/100m.
        
    Returns:
        Tuple of (TSS value, Intensity Factor or None)
    """
    if distance_meters and distance_meters > 0:
        # Use default threshold if not provided
        if threshold_pace_min_per_100m is None:
            threshold_pace_min_per_100m = 1.5  # Default: 1.5 min/100m
        
        # Convert threshold pace to meters/minute (FTP)
        # Example: 1.5 min/100m = 100/1.5 = 66.67 meters/minute
        ftp_meters_per_min = 100 / threshold_pace_min_per_100m
        
        # Calculate normalized swim speed (NSS) in meters/minute
        nss_meters_per_min = distance_meters / duration_minutes
        
        # Calculate intensity factor
        intensity_factor = nss_meters_per_min / ftp_meters_per_min
        
        # Swimming TSS uses IF³ (cubed, not squared!)
        duration_hours = duration_minutes / 60
        return (duration_hours * (intensity_factor ** 3) * 100, intensity_factor)
    
    # Fallback: swimming is generally higher intensity
    return (duration_minutes * 0.9, None)  # ~54 TSS per hour


def calculate_generic_tss(
    duration_minutes: int,
    intensity_factor: float = 0.7,
) -> float:
    """
    Calculate generic TSS for activities without specific metrics.
    
    Args:
        duration_minutes: Duration in minutes
        intensity_factor: Perceived intensity (0.5-1.0)
                         0.5 = easy, 0.7 = moderate, 0.85 = hard, 1.0 = threshold
        
    Returns:
        Generic TSS value
    """
    duration_hours = duration_minutes / 60
    return duration_hours * (intensity_factor ** 2) * 100


def calculate_activity_tss(
    sport_type: str,
    duration_minutes: int,
    average_hr: Optional[int] = None,
    threshold_hr: int = 180,
    distance_meters: Optional[float] = None,
    average_speed_mps: Optional[float] = None,
    normalized_power: Optional[float] = None,
    threshold_power: Optional[float] = None,
    threshold_pace_min_per_km: Optional[float] = None,
    threshold_pace_min_per_100m: Optional[float] = None,
    training_load: Optional[float] = None,
) -> tuple[float, Optional[float]]:
    """
    Calculate TSS and Intensity Factor (IF) for any activity type based on available data.
    
    Fallback strategy by sport (matches TrainingPeaks):
    - Cycling: FTP (power) > HR > Duration
    - Running: HR > Pace > Duration (HR preferred since we lack NGP elevation data)
    - Swimming: Pace > HR > Duration
    - Other: HR > Duration
    
    Note: We do NOT use Garmin's training_load because it uses different
    thresholds than the user's configured values. Always calculate TSS
    using the user's personal thresholds for consistency with TrainingPeaks.
    
    TrainingPeaks uses Normalized Graded Pace (NGP) for rTSS which requires
    elevation time-series data. Since we only have total elevation gain/loss,
    we prioritize HR-based calculation which is what TrainingPeaks does when
    NGP cannot be calculated.
    
    Args:
        sport_type: Type of sport (running, cycling, swimming, etc.)
        duration_minutes: Duration in minutes
        average_hr: Average heart rate
        threshold_hr: Lactate threshold heart rate
        distance_meters: Distance in meters
        average_speed_mps: Average speed in meters per second
        normalized_power: Normalized Power (cycling)
        threshold_power: FTP (cycling)
        threshold_pace_min_per_km: Threshold pace for running (min/km)
        threshold_pace_min_per_100m: Threshold pace for swimming (min/100m)
        training_load: Garmin's training load (IGNORED - we calculate our own)
        
    Returns:
        Tuple of (TSS value, Intensity Factor or None)
    """
    # DO NOT use Garmin's training_load - it uses different thresholds
    # Always calculate TSS using the user's configured thresholds
    
    sport_lower = sport_type.lower()
    
    # Running: Pace (with NGP if elevation available) > HR > Duration
    if 'run' in sport_lower:
        average_pace_min_per_km = None
        if distance_meters and distance_meters > 0 and average_speed_mps and average_speed_mps > 0:
            # Convert speed (m/s) to pace (min/km)
            km_per_hour = average_speed_mps * 3.6
            if km_per_hour > 0:
                average_pace_min_per_km = 60 / km_per_hour
        
        return calculate_running_tss(
            duration_minutes=duration_minutes,
            average_hr=average_hr,
            threshold_hr=threshold_hr,
            average_pace_min_per_km=average_pace_min_per_km,
            threshold_pace_min_per_km=threshold_pace_min_per_km,
        )
    
    # Cycling: FTP > HR > Duration
    elif 'cycl' in sport_lower or 'bike' in sport_lower:
        return calculate_cycling_tss(
            duration_minutes=duration_minutes,
            normalized_power=normalized_power,
            threshold_power=threshold_power,
            average_hr=average_hr,
            threshold_hr=threshold_hr,
        )
    
    # Tennis: stop-start. Heart rate stays high between points, so continuous
    # hrTSS treats a calm hit like a tempo session.
    elif 'tennis' in sport_lower:
        return calculate_tennis_tss(
            duration_minutes=duration_minutes,
            average_hr=average_hr,
            threshold_hr=threshold_hr,
        )

    # Swimming: Pace > HR > Duration
    elif 'swim' in sport_lower:
        # Check if we have HR data for fallback
        if distance_meters and distance_meters > 0:
            # Pace-based calculation using user's threshold
            return calculate_swimming_tss(
                duration_minutes=duration_minutes,
                distance_meters=distance_meters,
                threshold_pace_min_per_100m=threshold_pace_min_per_100m,
            )
        elif average_hr and threshold_hr and threshold_hr > 0:
            # HR-based fallback for swimming
            intensity_factor = average_hr / threshold_hr
            duration_hours = duration_minutes / 60
            return (duration_hours * (intensity_factor ** 2) * 100, intensity_factor)
        else:
            # Duration-based fallback
            return (duration_minutes * 0.9, None)  # Swimming is high intensity
    
    # Other Sports (cross-country skiing, strength, etc.): HR > Duration
    else:
        # Priority 1: HR-based calculation (if available)
        if average_hr and threshold_hr and threshold_hr > 0:
            intensity_factor = average_hr / threshold_hr
            duration_hours = duration_minutes / 60
            return (duration_hours * (intensity_factor ** 2) * 100, intensity_factor)
        
        # Priority 2: Duration-based estimate with moderate intensity
        return (calculate_generic_tss(duration_minutes, intensity_factor=0.6), 0.6)


# Continuous hrTSS overstates racket sports because HR stays elevated in the
# gaps. 0.45 keeps a calm 2h hit in the easy range and still rises when the
# session is actually hard.
TENNIS_HR_STRESS_SCALE = 0.45


def display_load_for_activity(activity: Any, threshold_hr: Optional[int]) -> Optional[tuple[float, Optional[float]]]:
    """Recompute tennis load from duration and HR. Other sports keep stored TSS."""
    sport = getattr(activity, "activity_type", None) or ""
    if "tennis" not in str(sport).lower():
        return None
    seconds = (
        getattr(activity, "elapsed_duration_seconds", None)
        or getattr(activity, "duration_seconds", None)
        or 0
    )
    return calculate_tennis_tss(float(seconds) / 60.0, getattr(activity, "average_hr", None), threshold_hr)


def calculate_tennis_tss(
    duration_minutes: float,
    average_hr: Optional[int] = None,
    threshold_hr: Optional[int] = None,
) -> tuple[float, Optional[float]]:
    """
    TSS for tennis.

    With heart rate, scale continuous hrTSS by TENNIS_HR_STRESS_SCALE.
    Without heart rate, use about 25 TSS per hour (calm play).
    """
    if not duration_minutes or duration_minutes <= 0:
        return (0.0, None)

    duration_hours = duration_minutes / 60.0
    if average_hr and threshold_hr and threshold_hr > 0:
        raw_if = average_hr / threshold_hr
        adjusted_if = raw_if * (TENNIS_HR_STRESS_SCALE ** 0.5)
        tss = duration_hours * (adjusted_if ** 2) * 100
        return (round(tss, 1), round(adjusted_if, 3))

    return (round(duration_hours * 25.0, 1), 0.50)


def calculate_workout_tss(
    sport_type: str,
    duration_minutes: Optional[int] = None,
    distance_km: Optional[float] = None,
    intensity_zone: Optional[str] = None,
    workout_type: Optional[str] = None,
) -> float:
    """
    Calculate estimated TSS for a planned workout.
    
    Args:
        sport_type: Type of sport
        duration_minutes: Planned duration
        distance_km: Planned distance
        intensity_zone: Planned intensity zone
        workout_type: Type of workout (easy, tempo, interval, etc.)
        
    Returns:
        Estimated TSS value
    """
    if not duration_minutes:
        return 0.0
    
    # Map intensity zones and workout types to intensity factors
    intensity_map = {
        'zone1': 0.55, 'recovery': 0.55, 'easy': 0.65,
        'zone2': 0.70, 'long': 0.70,
        'zone3': 0.85, 'tempo': 0.85,
        'zone4': 0.95, 'threshold': 0.95,
        'zone5': 1.05, 'interval': 1.05,
        'zone6': 1.15, 'race': 1.00,
    }
    
    # Determine intensity factor
    intensity_factor = 0.70  # default moderate
    
    if intensity_zone:
        intensity_factor = intensity_map.get(intensity_zone.lower(), 0.70)
    elif workout_type:
        intensity_factor = intensity_map.get(workout_type.lower(), 0.70)
    
    return calculate_generic_tss(duration_minutes, intensity_factor)


def calculate_tss_from_activity(activity: dict, user_settings: dict) -> tuple[float, Optional[float]]:
    """
    Wrapper function to calculate TSS and Intensity Factor from a Garmin activity dict and user settings.
    
    Args:
        activity: Garmin activity dictionary
        user_settings: User settings dict with keys: ftp, threshold_pace, max_hr, resting_hr, threshold_hr
        
    Returns:
        Tuple of (TSS value, Intensity Factor or None)
    """
    # Extract activity data
    activity_type = activity.get("activityType", {})
    sport_type = activity_type.get("typeKey", "unknown") if isinstance(activity_type, dict) else str(activity_type)
    
    # Determine which duration to use based on sport type
    # For interval sports (tennis, strength), use elapsed duration (includes rest)
    # For continuous sports (skiing, running, cycling), use moving duration
    sport_lower = sport_type.lower()
    is_interval_sport = any(x in sport_lower for x in ['tennis', 'strength', 'training', 'workout'])
    
    if is_interval_sport:
        # Interval sports: use elapsed duration (includes rest periods)
        duration_seconds = activity.get("elapsedDuration") or activity.get("duration") or activity.get("movingDuration") or 0
    else:
        # Continuous sports: use moving duration (excludes stopped time)
        duration_seconds = activity.get("movingDuration") or activity.get("duration") or activity.get("elapsedDuration") or 0
    
    duration_minutes = duration_seconds / 60 if duration_seconds else 0
    
    # Extract metrics
    average_hr = activity.get("averageHR")
    distance_meters = activity.get("distance")
    average_speed_mps = activity.get("averageSpeed")
    
    # Power metrics (cycling)
    normalized_power = activity.get("normPower") or activity.get("normalizedPower") or activity.get("avgPower")
    
    # Garmin training load (use as-is if available)
    training_load = activity.get("activityTrainingLoad")
    
    # User thresholds
    threshold_power = user_settings.get("ftp")
    
    # Threshold pace (seconds per km) - convert to min/km if present
    threshold_pace_sec_per_km = user_settings.get("threshold_pace")
    threshold_pace_min_per_km = threshold_pace_sec_per_km / 60 if threshold_pace_sec_per_km else None
    
    # Swimming threshold pace (seconds per 100m) - convert to min/100m if present
    swim_threshold_pace_sec_per_100m = user_settings.get("swim_threshold_pace")
    threshold_pace_min_per_100m = swim_threshold_pace_sec_per_100m / 60 if swim_threshold_pace_sec_per_100m else None
    
    # Use threshold_hr (lactate threshold), not max_hr
    threshold_hr = user_settings.get("threshold_hr")
    if not threshold_hr:
        # Fallback: estimate as 90% of max_hr if threshold not set
        max_hr = user_settings.get("max_hr", 180)
        threshold_hr = int(max_hr * 0.9)
    
    return calculate_activity_tss(
        sport_type=sport_type,
        duration_minutes=duration_minutes,
        average_hr=average_hr,
        threshold_hr=threshold_hr,
        distance_meters=distance_meters,
        average_speed_mps=average_speed_mps,
        normalized_power=normalized_power,
        threshold_power=threshold_power,
        threshold_pace_min_per_km=threshold_pace_min_per_km,
        threshold_pace_min_per_100m=threshold_pace_min_per_100m,
        training_load=training_load,
    )
