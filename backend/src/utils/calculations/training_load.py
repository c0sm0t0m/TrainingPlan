"""
Training Load Calculations (CTL, ATL, TSB)

Implements Performance Management Chart (PMC) metrics used in TrainingPeaks.

Formula:
    CTL = CTL_yesterday × e^(-1/42) + TSS_today × (1 - e^(-1/42))
    ATL = ATL_yesterday × e^(-1/7) + TSS_today × (1 - e^(-1/7))
    TSB = CTL - ATL
"""
import math
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.garmin_activity import GarminActivity
from src.utils.datetime_helpers import date_to_string, compare_date_for_sqlite
from src.utils.sport_types import matches_sport_filter

# Exponential decay factors (precomputed for performance)
CTL_TIME_CONSTANT = 42
ATL_TIME_CONSTANT = 7
CTL_DECAY = math.exp(-1 / CTL_TIME_CONSTANT)  # ≈ 0.976247
ATL_DECAY = math.exp(-1 / ATL_TIME_CONSTANT)  # ≈ 0.866058


async def calculate_training_load_metrics(
    db: AsyncSession,
    user_id: int,
    end_date: Optional[datetime] = None,
    days: int = 42,
    sport_type: Optional[str] = None
) -> List[Dict]:
    """
    Calculate CTL, ATL, and TSB for a user over a specified period.
    
    ⚠️ CRITICAL: CTL/ATL are cumulative metrics that MUST be calculated from
    the user's first activity to ensure consistency. The calculation ALWAYS
    starts from the beginning and returns only the requested number of days.
    
    CTL (Chronic Training Load): 42-day exponential moving average of TSS
        - Represents fitness
        - Long-term training stress
    
    ATL (Acute Training Load): 7-day exponential moving average of TSS
        - Represents fatigue
        - Short-term training stress
    
    TSB (Training Stress Balance): CTL - ATL
        - Represents form/freshness
        - Positive = fresh/rested, Negative = fatigued
    
    Args:
        db: Database session
        user_id: User ID to calculate for
        end_date: End date (defaults to today)
        days: Number of days to return (default 42)
        sport_type: Optional sport filter (running, cycling, swimming)
        
    Returns:
        List of daily metrics with date, tss, ctl, atl, tsb (only last 'days' entries)
    """
    if end_date is None:
        end_date = datetime.utcnow()
    
    # CRITICAL FIX: Find user's first activity to calculate from the beginning
    # This ensures CTL values are always consistent regardless of time range
    first_activity_query = select(
        func.min(GarminActivity.start_time_local)
    ).where(
        GarminActivity.user_id == user_id
    )
    
    result = await db.execute(first_activity_query)
    first_activity_date = result.scalar()
    
    if not first_activity_date:
        return []
    
    # Sport-filtered CTL must start from the first activity of that family
    # (Garmin keys like road_biking are not covered by brittle IN lists).
    if sport_type:
        all_dates = (
            await db.execute(
                select(
                    GarminActivity.start_time_local,
                    GarminActivity.activity_type,
                )
                .where(GarminActivity.user_id == user_id)
                .order_by(GarminActivity.start_time_local)
            )
        ).all()
        first_sport_date = next(
            (row.start_time_local for row in all_dates if matches_sport_filter(row.activity_type, sport_type)),
            None,
        )
        if not first_sport_date:
            return []
        first_activity_date = first_sport_date
    
    # Parse the date string (SQLite returns ISO string format)
    if isinstance(first_activity_date, str):
        # SQLite: "YYYY-MM-DD HH:MM:SS.ffffff"
        start_date = datetime.fromisoformat(first_activity_date.split('.')[0])
    else:
        start_date = first_activity_date
    
    # Always calculate from first activity (not from end_date - lookback_days)
    # This ensures CTL is consistent regardless of requested time range
    
    # Fetch ALL activities from first activity to end_date
    # CRITICAL: For end_date comparison, we need to include the entire day
    # SQLite TEXT comparison requires full timestamp, not just date
    from datetime import time
    end_date_inclusive = datetime.combine(end_date.date(), time.max) if isinstance(end_date, datetime) else datetime.combine(end_date, time.max)
    
    query = select(
        GarminActivity.start_time_local,
        GarminActivity.calculated_tss,
        GarminActivity.activity_type
    ).where(
        GarminActivity.user_id == user_id,
        GarminActivity.start_time_local >= compare_date_for_sqlite(start_date),
        GarminActivity.start_time_local <= end_date_inclusive,
    ).order_by(GarminActivity.start_time_local)
    
    result = await db.execute(query)
    activities = result.all()
    
    # Group activities by date and sum TSS (with optional sport filter)
    daily_tss: Dict[str, float] = {}
    for activity in activities:
        if sport_type and not matches_sport_filter(activity.activity_type, sport_type):
            continue
        
        date_str = date_to_string(activity.start_time_local)
        tss = activity.calculated_tss or 0
        
        if date_str in daily_tss:
            daily_tss[date_str] += tss
        else:
            daily_tss[date_str] = tss
    
    # Calculate CTL/ATL/TSB for each day using correct exponential formula
    metrics = []
    ctl = 0.0  # Initial CTL (starts at 0 on first activity date)
    atl = 0.0  # Initial ATL (starts at 0 on first activity date)
    
    # Generate data for ALL days from first activity to end_date
    current_date = start_date
    while current_date <= end_date:
        date_str = date_to_string(current_date)
        daily_tss_value = daily_tss.get(date_str, 0.0)
        
        # Exponential moving averages using correct formula:
        # EMA = EMA_yesterday × e^(-1/k) + TSS_today × (1 - e^(-1/k))
        # where k is the time constant (42 for CTL, 7 for ATL)
        
        # CTL: 42-day EMA
        ctl = ctl * CTL_DECAY + daily_tss_value * (1 - CTL_DECAY)
        
        # ATL: 7-day EMA
        atl = atl * ATL_DECAY + daily_tss_value * (1 - ATL_DECAY)
        
        # TSB: Fitness minus Fatigue
        tsb = ctl - atl
        
        metrics.append({
            'date': date_str,
            'tss': round(daily_tss_value, 1),
            'ctl': round(ctl, 1),
            'atl': round(atl, 1),
            'tsb': round(tsb, 1)
        })
        
        current_date += timedelta(days=1)
    
    # Return only the requested number of days (most recent)
    # This ensures CTL is always calculated from the beginning but we only
    # return the time range the caller requested
    if len(metrics) <= days:
        return metrics
    else:
        return metrics[-days:]


async def get_current_training_metrics(
    db: AsyncSession,
    user_id: int,
    sport_type: Optional[str] = None
) -> Dict:
    """
    Get current training metrics (today's values).
    
    Args:
        db: Database session
        user_id: User ID
        sport_type: Optional sport filter (running, cycling, swimming)
        
    Returns:
        Dictionary with current ctl, atl, tsb, weekly_tss, trend
    """
    # Calculate last 50 days to get accurate current values
    metrics = await calculate_training_load_metrics(db, user_id, days=50, sport_type=sport_type)
    
    if not metrics:
        return {
            'ctl': 0,
            'atl': 0,
            'tsb': 0,
            'weekly_tss': 0,
            'trend': 'flat'
        }
    
    # Get today's metrics (last item)
    current = metrics[-1]
    
    # Calculate weekly TSS for current calendar week (Monday-Sunday)
    today = datetime.now().date()
    weekday = today.weekday()  # Monday=0, Sunday=6
    monday = today - timedelta(days=weekday)  # Start of current week
    
    # Sum TSS only from days in current week (Monday to today)
    weekly_tss = 0.0
    for day in metrics:
        day_date = datetime.fromisoformat(day['date']).date()
        if day_date >= monday and day_date <= today:
            weekly_tss += day['tss']
    
    # Determine trend by comparing to 7 days ago
    if len(metrics) >= 8:
        previous_ctl = metrics[-8]['ctl']
        trend = 'up' if current['ctl'] > previous_ctl else 'down' if current['ctl'] < previous_ctl else 'flat'
    else:
        trend = 'flat'
    
    return {
        'ctl': current['ctl'],
        'atl': current['atl'],
        'tsb': current['tsb'],
        'weekly_tss': round(weekly_tss, 1),
        'trend': trend
    }
