"""
Training Load Calculations (CTL, ATL, TSB)

Implements Performance Management Chart (PMC) metrics used in TrainingPeaks.
"""
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.garmin_activity import GarminActivity
from src.utils.datetime_helpers import date_to_string, compare_date_for_sqlite


async def calculate_training_load_metrics(
    db: AsyncSession,
    user_id: int,
    end_date: Optional[datetime] = None,
    days: int = 42,
    sport_type: Optional[str] = None
) -> List[Dict]:
    """
    Calculate CTL, ATL, and TSB for a user over a specified period.
    
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
        List of daily metrics with date, tss, ctl, atl, tsb
    """
    if end_date is None:
        end_date = datetime.utcnow()
    
    # We need extra history to prime the CTL/ATL calculations
    # CTL needs 42 days of history, so fetch 84 days to have good initial values
    lookback_days = days + 42
    start_date = end_date - timedelta(days=lookback_days)
    
    # Fetch all activities with TSS in date range
    query = select(
        GarminActivity.start_time_local,
        GarminActivity.calculated_tss,
        GarminActivity.activity_type
    ).where(
        GarminActivity.user_id == user_id,
        GarminActivity.start_time_local >= compare_date_for_sqlite(start_date),
        GarminActivity.start_time_local <= compare_date_for_sqlite(end_date)
    ).order_by(GarminActivity.start_time_local)
    
    result = await db.execute(query)
    activities = result.all()
    
    # Group activities by date and sum TSS (with optional sport filter)
    daily_tss: Dict[str, float] = {}
    for activity in activities:
        # Apply sport filter if specified
        if sport_type:
            activity_sport = (activity.activity_type or '').lower()
            filter_sport = sport_type.lower()
            
            # Check if activity matches the sport type
            if filter_sport == 'running' and 'running' not in activity_sport:
                continue
            elif filter_sport == 'cycling' and 'cycling' not in activity_sport and 'biking' not in activity_sport:
                continue
            elif filter_sport == 'swimming' and 'swimming' not in activity_sport:
                continue
        
        date_str = date_to_string(activity.start_time_local)
        tss = activity.calculated_tss or 0
        
        if date_str in daily_tss:
            daily_tss[date_str] += tss
        else:
            daily_tss[date_str] = tss
    
    # Calculate CTL/ATL/TSB for each day
    metrics = []
    ctl = 0.0  # Initial CTL
    atl = 0.0  # Initial ATL
    
    # Generate data for all days in range
    current_date = start_date
    while current_date <= end_date:
        date_str = date_to_string(current_date)
        daily_tss_value = daily_tss.get(date_str, 0.0)
        
        # Calculate exponential moving averages
        # CTL: 42-day EMA (time constant = 42)
        ctl = ctl * (1 - 1/42) + daily_tss_value * (1/42)
        
        # ATL: 7-day EMA (time constant = 7)
        atl = atl * (1 - 1/7) + daily_tss_value * (1/7)
        
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
    
    # Return only the requested number of days (not the priming period)
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
    
    # Calculate weekly TSS (last 7 days)
    weekly_tss = sum(day['tss'] for day in metrics[-7:])
    
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
