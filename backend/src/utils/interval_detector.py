"""
Interval and Sub-Activity Detection from Time-Series Data

Analyzes HR/pace streams to detect:
1. Fast sustained efforts (20+ min tempo sections)
2. Interval sessions (repeated high-intensity efforts)
"""
from typing import List, Dict, Optional, Tuple
from datetime import datetime, timedelta
import numpy as np


def detect_sustained_efforts(
    timestamps: List[float],
    paces: List[float],
    heart_rates: List[int],
    min_duration_minutes: float = 20,
    pace_threshold_percentile: float = 30  # Bottom 30% = fastest paces
) -> List[Dict]:
    """
    Detect sustained fast efforts within activity time series.
    
    Args:
        timestamps: Array of timestamps (seconds from start)
        paces: Array of pace values (min/km)
        heart_rates: Array of HR values (bpm)
        min_duration_minutes: Minimum duration for sustained effort
        pace_threshold_percentile: Percentile threshold for "fast" pace
        
    Returns:
        List of detected efforts with start/end indices and metrics
    """
    if len(paces) < 60:  # Need at least 1 minute of data
        return []
    
    efforts = []
    
    # Calculate pace threshold (30th percentile = faster than 70% of activity)
    pace_threshold = np.percentile(paces, pace_threshold_percentile)
    
    # Find continuous sections below threshold (faster)
    is_fast = np.array(paces) <= pace_threshold
    
    # Detect transitions
    transitions = np.diff(np.concatenate(([False], is_fast, [False])).astype(int))
    starts = np.where(transitions == 1)[0]
    ends = np.where(transitions == -1)[0]
    
    # Analyze each sustained effort
    for start_idx, end_idx in zip(starts, ends):
        duration_sec = timestamps[end_idx - 1] - timestamps[start_idx]
        duration_min = duration_sec / 60
        
        if duration_min >= min_duration_minutes:
            # Calculate metrics for this section
            section_paces = paces[start_idx:end_idx]
            section_hrs = heart_rates[start_idx:end_idx]
            
            effort = {
                'start_idx': int(start_idx),
                'end_idx': int(end_idx),
                'start_time': timestamps[start_idx],
                'end_time': timestamps[end_idx - 1],
                'duration_min': duration_min,
                'avg_pace': float(np.mean(section_paces)),
                'avg_hr': int(np.mean(section_hrs)),
                'max_hr': int(np.max(section_hrs)),
                'type': 'sustained_tempo'
            }
            
            efforts.append(effort)
    
    return efforts


def detect_intervals(
    timestamps: List[float],
    heart_rates: List[int],
    min_intervals: int = 3,
    min_interval_duration_sec: int = 120,  # 2 minutes
    hr_spike_threshold: float = 0.85  # 85% of max HR in activity
) -> Optional[Dict]:
    """
    Detect interval training patterns in HR time series.
    
    Args:
        timestamps: Array of timestamps
        heart_rates: Array of HR values
        min_intervals: Minimum number of intervals to detect
        min_interval_duration_sec: Minimum duration per interval
        hr_spike_threshold: Percentage of activity max HR to qualify as "hard"
        
    Returns:
        Dict with interval session details if detected, None otherwise
    """
    if len(heart_rates) < 300:  # Need at least 5 minutes
        return None
    
    max_hr = np.max(heart_rates)
    threshold = max_hr * hr_spike_threshold
    
    # Find high-intensity segments
    is_hard = np.array(heart_rates) >= threshold
    
    # Detect transitions
    transitions = np.diff(np.concatenate(([False], is_hard, [False])).astype(int))
    starts = np.where(transitions == 1)[0]
    ends = np.where(transitions == -1)[0]
    
    # Filter for minimum duration
    intervals = []
    for start_idx, end_idx in zip(starts, ends):
        duration = timestamps[end_idx - 1] - timestamps[start_idx]
        if duration >= min_interval_duration_sec:
            intervals.append({
                'start_idx': int(start_idx),
                'end_idx': int(end_idx),
                'duration_sec': duration,
                'avg_hr': int(np.mean(heart_rates[start_idx:end_idx]))
            })
    
    if len(intervals) >= min_intervals:
        # Detected interval session
        total_interval_time = sum(i['duration_sec'] for i in intervals)
        avg_interval_hr = int(np.mean([i['avg_hr'] for i in intervals]))
        
        return {
            'type': 'interval_session',
            'num_intervals': len(intervals),
            'total_interval_time_min': total_interval_time / 60,
            'avg_interval_hr': avg_interval_hr,
            'intervals': intervals
        }
    
    return None


def analyze_activity_streams(
    activity_id: int,
    timestamps: List[float],
    paces: Optional[List[float]] = None,
    heart_rates: Optional[List[int]] = None
) -> Dict:
    """
    Main entry point for analyzing activity time-series data.
    
    Args:
        activity_id: Activity identifier
        timestamps: Time series (seconds from start)
        paces: Pace series (min/km), optional
        heart_rates: HR series (bpm), optional
        
    Returns:
        Dict containing all detected sub-activities and intervals
    """
    results = {
        'activity_id': activity_id,
        'sustained_efforts': [],
        'interval_session': None
    }
    
    # Detect sustained tempo efforts
    if paces and heart_rates:
        sustained = detect_sustained_efforts(
            timestamps, paces, heart_rates,
            min_duration_minutes=20
        )
        results['sustained_efforts'] = sustained
    
    # Detect interval patterns
    if heart_rates:
        interval_session = detect_intervals(
            timestamps, heart_rates,
            min_intervals=3
        )
        results['interval_session'] = interval_session
    
    return results


def parse_fit_file_streams(fit_file_path: str) -> Optional[Dict]:
    """
    Parse FIT file to extract time-series data.
    
    Args:
        fit_file_path: Path to FIT file
        
    Returns:
        Dict with timestamps, paces, heart_rates, distances
    """
    try:
        from fitparse import FitFile
        
        fitfile = FitFile(fit_file_path)
        
        timestamps = []
        heart_rates = []
        speeds = []  # m/s
        
        start_time = None
        
        for record in fitfile.get_messages('record'):
            data = {}
            for field in record:
                data[field.name] = field.value
            
            # Extract timestamp
            if 'timestamp' in data:
                if start_time is None:
                    start_time = data['timestamp']
                
                elapsed = (data['timestamp'] - start_time).total_seconds()
                timestamps.append(elapsed)
            
            # Extract heart rate
            if 'heart_rate' in data and data['heart_rate']:
                heart_rates.append(int(data['heart_rate']))
            elif heart_rates:
                heart_rates.append(heart_rates[-1])  # Forward fill
            else:
                heart_rates.append(0)
            
            # Extract speed (convert to pace)
            if 'speed' in data and data['speed'] and data['speed'] > 0:
                speed_mps = data['speed']
                speeds.append(speed_mps)
            elif speeds:
                speeds.append(speeds[-1])  # Forward fill
            else:
                speeds.append(0)
        
        # Convert speeds to paces (min/km)
        paces = []
        for speed in speeds:
            if speed > 0:
                pace_sec_per_km = 1000 / speed  # seconds per km
                pace_min_per_km = pace_sec_per_km / 60
                paces.append(pace_min_per_km)
            else:
                paces.append(999)  # Invalid pace
        
        return {
            'timestamps': timestamps,
            'heart_rates': heart_rates,
            'paces': paces,
            'speeds': speeds
        }
        
    except Exception as e:
        print(f"Error parsing FIT file: {e}")
        return None
