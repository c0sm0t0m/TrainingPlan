"""
Enhanced TSS Calculation from Time Series Data

Uses second-by-second heart rate, power, and pace data for accurate TSS calculation.
Matches TrainingPeaks methodology.
"""
from typing import Dict, List, Optional
import math


def calculate_normalized_power(power_samples: List[Optional[float]]) -> Optional[float]:
    """
    Calculate Normalized Power (NP) from power time series.
    
    NP = 4th root of the average of 30-second rolling averages raised to 4th power.
    This accounts for the non-linear physiological response to power variations.
    
    Args:
        power_samples: List of power values in watts (one per second)
        
    Returns:
        Normalized Power in watts, or None if insufficient data
    """
    # Filter out None values
    valid_power = [p for p in power_samples if p is not None and p > 0]
    
    if len(valid_power) < 30:
        return None
    
    # Calculate 30-second rolling averages
    rolling_avgs = []
    for i in range(len(valid_power) - 29):
        window = valid_power[i:i+30]
        rolling_avgs.append(sum(window) / 30)
    
    # Raise each rolling average to 4th power, average them, then take 4th root
    fourth_powers = [avg ** 4 for avg in rolling_avgs]
    mean_fourth_power = sum(fourth_powers) / len(fourth_powers)
    np = mean_fourth_power ** 0.25
    
    return np


def calculate_intensity_factor(np: float, ftp: float) -> float:
    """
    Calculate Intensity Factor (IF).
    
    IF = Normalized Power / FTP
    
    Args:
        np: Normalized Power in watts
        ftp: Functional Threshold Power in watts
        
    Returns:
        Intensity Factor (dimensionless ratio)
    """
    if ftp <= 0:
        return 0
    return np / ftp


def calculate_tss_from_power_time_series(
    power_samples: List[Optional[float]],
    duration_seconds: int,
    ftp: float
) -> Optional[float]:
    """
    Calculate Training Stress Score from power time series.
    
    TSS = (duration_hours × NP × IF) / (FTP × 3600) × 100
    
    Args:
        power_samples: List of power values (one per second)
        duration_seconds: Total activity duration in seconds
        ftp: Functional Threshold Power in watts
        
    Returns:
        TSS value or None if insufficient data
    """
    if ftp <= 0:
        return None
    
    np = calculate_normalized_power(power_samples)
    if np is None:
        return None
    
    intensity_factor = calculate_intensity_factor(np, ftp)
    duration_hours = duration_seconds / 3600
    
    # TSS formula
    tss = (duration_hours * np * intensity_factor) / ftp * 100
    
    return round(tss, 1)


def calculate_tss_from_hr_time_series(
    hr_samples: List[Optional[int]],
    duration_seconds: int,
    threshold_hr: int,
    max_hr: int,
    resting_hr: int = 50
) -> Optional[float]:
    """
    Calculate Training Stress Score from heart rate time series.
    
    Uses TrainingPeaks TRIMP-based methodology:
    - Each HR sample contributes: ((HR - RestingHR) / (ThresholdHR - RestingHR))^2
    - Normalized to 100 TSS for 1 hour at threshold HR
    - Accounts for actual sample rate (typically 1 sample per 3-5 seconds)
    
    NOTE: Garmin's TSS values are typically 1.3-2.4x higher than this calculation.
    Garmin uses their own proprietary algorithm that accounts for additional factors
    (training effect, elevation, recent training history). Our calculation follows
    the TrainingPeaks standard which is widely used and mathematically consistent.
    
    Args:
        hr_samples: List of heart rate values from FIT file
        duration_seconds: Total activity duration
        threshold_hr: Lactate threshold heart rate
        max_hr: Maximum heart rate
        resting_hr: Resting heart rate (default 50)
        
    Returns:
        TSS value or None if insufficient data
    """
    if threshold_hr <= resting_hr or max_hr <= threshold_hr:
        return None
    
    # Filter valid HR samples
    valid_hr = [hr for hr in hr_samples if hr is not None and resting_hr < hr <= max_hr]
    
    if len(valid_hr) < 60:  # Need at least 1 minute of data
        return None
    
    # Calculate cumulative HR stress
    hr_stress_sum = 0.0
    hr_reserve = threshold_hr - resting_hr
    
    for hr in valid_hr:
        # HR ratio relative to threshold
        hr_ratio = (hr - resting_hr) / hr_reserve
        
        # Clip to reasonable range (0.3 to 2.0)
        hr_ratio = max(0.3, min(2.0, hr_ratio))
        
        # Accumulate squared ratio (stress is exponential with HR)
        hr_stress_sum += hr_ratio ** 2
    
    # Convert to TSS accounting for actual sample rate
    # Each sample represents (duration_seconds / num_samples) seconds of activity
    # TSS = (sum of hr_ratio^2 per sample) × (duration / num_samples) / 36
    # Where 36 = 3600 seconds/hour / 100 TSS at threshold
    sample_duration = duration_seconds / len(valid_hr)
    tss = (hr_stress_sum * sample_duration) / 36
    
    return round(tss, 1)


def calculate_tss_from_time_series(
    time_series_data: Dict,
    user_settings: Dict,
    activity_type: str
) -> Optional[float]:
    """
    Calculate TSS from time series data, choosing best method available.
    
    Priority:
    1. Power-based TSS for cycling (most accurate)
    2. HR-based TSS with time series (accounts for variability)
    3. Fall back to None (will use summary-based calculation)
    
    Args:
        time_series_data: Parsed time series from FIT file
        user_settings: User thresholds (ftp, threshold_hr, max_hr, resting_hr)
        activity_type: Sport type (running, cycling, etc.)
        
    Returns:
        TSS value or None if time series calculation not possible
    """
    if "error" in time_series_data:
        return None
    
    metadata = time_series_data.get("metadata", {})
    time_series = time_series_data.get("time_series", {})
    
    duration_seconds = metadata.get("duration_seconds", 0)
    if duration_seconds < 60:  # Need at least 1 minute
        return None
    
    # Method 1: Power-based TSS (cycling)
    if "cycling" in activity_type.lower() or "bike" in activity_type.lower():
        ftp = user_settings.get("ftp")
        if ftp and ftp > 0 and metadata.get("has_power"):
            power_samples = time_series.get("power", [])
            tss = calculate_tss_from_power_time_series(
                power_samples,
                duration_seconds,
                ftp
            )
            if tss is not None:
                return tss
    
    # Method 2: HR-based TSS (all activities with HR data)
    if metadata.get("has_heart_rate"):
        threshold_hr = user_settings.get("threshold_hr")
        max_hr = user_settings.get("max_hr")
        resting_hr = user_settings.get("resting_hr", 50)
        
        # If threshold_hr equals max_hr (e.g., skiing uses max_hr), use 85% of max_hr as threshold
        if threshold_hr and max_hr and threshold_hr >= max_hr:
            threshold_hr = int(max_hr * 0.85)
        
        if threshold_hr and max_hr and threshold_hr < max_hr:
            hr_samples = time_series.get("heart_rate", [])
            tss = calculate_tss_from_hr_time_series(
                hr_samples,
                duration_seconds,
                threshold_hr,
                max_hr,
                resting_hr
            )
            if tss is not None:
                return tss
    
    # No time series calculation possible
    return None


def get_time_series_tss_summary(time_series_data: Dict, calculated_tss: Optional[float]) -> str:
    """
    Get a summary of how TSS was calculated from time series.
    
    Args:
        time_series_data: Parsed time series data
        calculated_tss: TSS value that was calculated
        
    Returns:
        Human-readable summary string
    """
    if calculated_tss is None:
        return "TSS: Using summary data (no time series)"
    
    metadata = time_series_data.get("metadata", {})
    
    if metadata.get("has_power"):
        return f"TSS: {calculated_tss:.1f} (from power time series)"
    elif metadata.get("has_heart_rate"):
        return f"TSS: {calculated_tss:.1f} (from HR time series)"
    else:
        return f"TSS: {calculated_tss:.1f} (calculated)"
