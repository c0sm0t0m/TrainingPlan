"""
Historic Threshold Calculator - Estimate thresholds backwards based on performance trends
"""
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, func
from src.models.garmin_activity import GarminActivity
from src.models.user import User
from src.models.weekly_threshold import WeeklyThreshold
import statistics


async def calculate_historic_thresholds(
    user: User,
    db: AsyncSession,
    lookback_weeks: int = 104  # 2 years
) -> Dict[str, int]:
    """
    Calculate historic thresholds for each week going backwards from today.
    
    Strategy:
    1. Get all activities grouped by ISO week
    2. For each week, analyze performance metrics (avg HR, pace, power)
    3. Estimate threshold for that week based on activity intensity distribution
    4. Smooth values to avoid unrealistic jumps
    5. Store in weekly_thresholds table
    
    Args:
        user: User object with current thresholds
        db: Database session
        lookback_weeks: How many weeks to calculate backwards (default 104 = 2 years)
        
    Returns:
        Dict with statistics (weeks_calculated, activities_analyzed, etc.)
    """
    print(f"📊 Calculating historic thresholds for {user.email}")
    print(f"   Lookback period: {lookback_weeks} weeks ({lookback_weeks/52:.1f} years)")
    
    # Get all user's activities
    result = await db.execute(
        select(GarminActivity)
        .where(GarminActivity.user_id == user.id)
        .order_by(GarminActivity.start_time_local.desc())
    )
    all_activities = result.scalars().all()
    
    if not all_activities:
        print("   No activities found")
        return {"weeks_calculated": 0, "activities_analyzed": 0}
    
    print(f"   Total activities: {len(all_activities)}")
    
    # Current thresholds (baseline for latest week)
    current_thresholds = {
        "running_threshold_hr": user.running_threshold_hr or 165,
        "cycling_threshold_hr": user.cycling_threshold_hr or 160,
        "ftp": user.ftp or 220,
        "threshold_pace": user.threshold_pace or 5.0,
        "swim_threshold_pace": user.swim_threshold_pace or 120,
        "max_hr": user.max_hr or 179,
        "resting_hr": user.resting_hr or 55,
    }
    
    # Get current week/year
    today = datetime.now()
    current_year, current_week, _ = today.isocalendar()
    
    # Group activities by ISO week
    activities_by_week = {}
    for activity in all_activities:
        if not activity.start_time_local:
            continue
        
        year, week, _ = activity.start_time_local.isocalendar()
        key = (year, week)
        
        if key not in activities_by_week:
            activities_by_week[key] = []
        activities_by_week[key].append(activity)
    
    print(f"   Activities span {len(activities_by_week)} weeks")
    
    # Calculate thresholds for each week going backwards
    calculated_weeks = []
    
    # Start from current week and go backwards
    for weeks_ago in range(lookback_weeks + 1):
        target_date = today - timedelta(weeks=weeks_ago)
        year, week, _ = target_date.isocalendar()
        
        activities_this_week = activities_by_week.get((year, week), [])
        
        # Estimate thresholds for this week
        week_thresholds = await _estimate_week_thresholds(
            activities_this_week,
            current_thresholds,
            weeks_ago,
            all_activities
        )
        
        # Create or update weekly threshold record
        existing = await db.execute(
            select(WeeklyThreshold).where(
                and_(
                    WeeklyThreshold.user_id == user.id,
                    WeeklyThreshold.year == year,
                    WeeklyThreshold.week == week
                )
            )
        )
        threshold_record = existing.scalar_one_or_none()
        
        if threshold_record:
            # Update existing
            for key, value in week_thresholds.items():
                setattr(threshold_record, key, value)
        else:
            # Create new
            threshold_record = WeeklyThreshold(
                user_id=user.id,
                year=year,
                week=week,
                **week_thresholds
            )
            db.add(threshold_record)
        
        calculated_weeks.append((year, week))
        
        if weeks_ago < 5 or weeks_ago % 10 == 0:  # Show first 5 weeks and every 10th
            print(f"   {year}-W{week:02d}: HR={week_thresholds['running_threshold_hr']}, "
                  f"FTP={week_thresholds['ftp']}, activities={week_thresholds['activities_used']}")
    
    await db.commit()
    
    return {
        "weeks_calculated": len(calculated_weeks),
        "activities_analyzed": len(all_activities),
        "oldest_week": f"{calculated_weeks[-1][0]}-W{calculated_weeks[-1][1]:02d}",
        "newest_week": f"{calculated_weeks[0][0]}-W{calculated_weeks[0][1]:02d}",
    }


async def _estimate_week_thresholds(
    week_activities: List[GarminActivity],
    current_thresholds: Dict,
    weeks_ago: int,
    all_activities: List[GarminActivity]
) -> Dict:
    """
    Estimate thresholds for a specific week based on ACTUAL PERFORMANCE.
    
    Strategy:
    - Current week (weeks_ago=0): Use user's current thresholds
    - ALL other weeks: Analyze actual activity performance
      * For running: Look at HR during runs (85th percentile estimation)
      * For cycling: Look at power during rides
      * Blend: 70% performance data + 30% trend-based extrapolation
    
    For running: Estimate threshold as avg_hr + (max_hr - avg_hr) * 0.35
    For cycling: Use 90th percentile power
    """
    # Base threshold values
    thresholds = current_thresholds.copy()
    
    # If current week, use current values
    if weeks_ago == 0:
        method = "current"
        confidence = 1.0
        # ALL weeks (not current) - analyze actual performance
        if week_activities:
            running_hrs = []
            running_hrs_key_sessions = []  # Prioritize hard efforts
            cycling_powers = []
            
            for activity in week_activities:
                sport = activity.activity_type.lower()
                duration_min = (activity.duration_seconds / 60) if activity.duration_seconds else 0
                
                # Running: collect HR values with special handling for key sessions
                if 'run' in sport and activity.average_hr and activity.max_hr:
                    # Detect KEY SESSIONS: 20-60 min hard efforts (max HR > 85% of user max)
                    is_key_session = (
                        20 <= duration_min <= 60 and
                        activity.max_hr >= (current_thresholds["max_hr"] * 0.85)
                    )
                    
                    if is_key_session:
                        # KEY SESSION: Use avg HR as threshold estimate (1-hour effort principle)
                        # For 20-60 min hard efforts, avg HR ≈ threshold HR
                        # Adjust slightly based on duration:
                        # - 20-30 min: avg HR ≈ 105% of threshold → divide by 1.05
                        # - 30-45 min: avg HR ≈ 102% of threshold → divide by 1.02  
                        # - 45-60 min: avg HR ≈ threshold → use as-is
                        if duration_min < 30:
                            estimated_threshold = activity.average_hr / 1.05
                        elif duration_min < 45:
                            estimated_threshold = activity.average_hr / 1.02
                        else:
                            estimated_threshold = activity.average_hr  # ~1 hour = threshold
                        
                        running_hrs_key_sessions.append(estimated_threshold)
                    else:
                        # Regular run: Use 85th percentile estimation
                        # Logic: avg_hr + 35% of the way to max_hr
                        estimated_threshold = activity.average_hr + (activity.max_hr - activity.average_hr) * 0.35
                        running_hrs.append(estimated_threshold)
                
                # Cycling: collect high-intensity power values
                elif ('cycl' in sport or 'bike' in sport or 'ride' in sport) and activity.raw_data:
                    # Check if we have power data
                    time_series = activity.raw_data.get('time_series', {})
                    if time_series.get('metadata', {}).get('has_power'):
                        power_stats = time_series.get('metadata', {}).get('power_stats', {})
                        if power_stats.get('avg'):
                            # For 20-60 min hard efforts, use avg power more directly
                            is_hard_ride = duration_min >= 20 and activity.average_hr and activity.average_hr >= (current_thresholds["max_hr"] * 0.80)
                            if is_hard_ride:
                                # Hard ride: avg power ≈ 95% of FTP for <1 hour
                                estimated_ftp = power_stats['avg'] / 0.95
                            else:
                                # Easy ride: more conservative estimate
                                estimated_ftp = power_stats['avg'] * 1.15
            elif running_hrs:
                # Regular runs only (no key sessions) cycling_powers.append(estimated_ftp)
            
            # Calculate thresholds from this week's performance
            # PRIORITIZE key sessions if available
            trend_factor = 1.0 - (weeks_ago * 0.003)  # 0.3% per week baseline
            
            if running_hrs_key_sessions:
                # We have KEY SESSIONS - use these preferentially!
                estimated_run_hr = int(statistics.median(running_hrs_key_sessions))
                # High confidence: 80% from key session data, 20% from trend
                thresholds["running_threshold_hr"] = int(
                    estimated_run_hr * 0.8 + current_thresholds["running_threshold_hr"] * trend_factor * 0.2
                )
                thresholds["cycling_threshold_hr"] = thresholds["running_threshold_hr"] - 5
            elif running_hrs:
                estimated_run_hr = int(statistics.median(running_hrs))
                # Blend: 70% from performance, 30% from trend
                thresholds["running_threshold_hr"] = int(
                    estimated_run_hr * 0.7 + current_thresholds["running_threshold_hr"] * trend_factor * 0.3
                )
                # Also update cycling HR (correlated with running fitness)
                thresholds["cycling_threshold_hr"] = thresholds["running_threshold_hr"] - 5  # Typically 5 bpm lower
            else:
                # No running data, use trend-based estimate
                thresholds["running_threshold_hr"] = int(current_thresholds["running_threshold_hr"] * trend_factor)
                thresholds["cycling_threshold_hr"] = int(current_thresholds["cycling_threshold_hr"] * trend_factor)
            
            if cycling_powers:
                estimated_ftp = int(statistics.median(cycling_powers))
                # Blend: 70% from performance, 30% from trend
                thresholds["ftp"] = int(
                    estimated_ftp * 0.7 + current_thresholds["ftp"] * trend_factor * 0.3
                )
            else:
                # No cycling data, use trend-based estimate
                thresholds["ftp"] = int(current_thresholds["ftp"] * trend_factor)
            
            method = "performance_anakey sessions or more activities
            if running_hrs_key_sessions:
                confidence = 0.90  # Very high confidence from key sessions
            el# Higher confidence with more activities
            if len(week_activities) >= 5:
                confidence = 0.85
            elif len(week_activities) >= 3:
                confidence = 0.75
            else:
                confidence = 0.65
        else:
            # No activities this week - use trend extrapolation only
            trend_factor = 1.0 - (weeks_ago * 0.003)
            thresholds["running_threshold_hr"] = int(current_thresholds["running_threshold_hr"] * trend_factor)
            thresholds["cycling_threshold_hr"] = int(current_thresholds["cycling_threshold_hr"] * trend_factor)
            thresholds["ftp"] = int(current_thresholds["ftp"] * trend_factor)
            method = "trend_extrapolation"
            confidence = 0.4
    
    return {
        "running_threshold_hr": thresholds["running_threshold_hr"],
        "cycling_threshold_hr": thresholds["cycling_threshold_hr"],
        "ftp": thresholds["ftp"],
        "threshold_pace": thresholds["threshold_pace"],
        "swim_threshold_pace": thresholds["swim_threshold_pace"],
        "max_hr": thresholds["max_hr"],
        "resting_hr": thresholds["resting_hr"],
        "calculation_method": method,
        "confidence_score": confidence,
        "activities_used": len(week_activities),
    }


async def get_thresholds_for_date(
    user_id: int,
    activity_date: datetime,
    db: AsyncSession
) -> Optional[Dict]:
    """
    Get threshold values for a specific date.
    
    Looks up the weekly threshold for the week containing this date.
    
    Args:
        user_id: User ID
        activity_date: Date of the activity
        db: Database session
        
    Returns:
        Dict with threshold values, or None if not found
    """
    year, week, _ = activity_date.isocalendar()
    
    result = await db.execute(
        select(WeeklyThreshold).where(
            and_(
                WeeklyThreshold.user_id == user_id,
                WeeklyThreshold.year == year,
                WeeklyThreshold.week == week
            )
        )
    )
    
    threshold = result.scalar_one_or_none()
    
    if not threshold:
        return None
    
    return {
        "running_threshold_hr": threshold.running_threshold_hr,
        "cycling_threshold_hr": threshold.cycling_threshold_hr,
        "ftp": threshold.ftp,
        "threshold_pace": threshold.threshold_pace,
        "swim_threshold_pace": threshold.swim_threshold_pace,
        "max_hr": threshold.max_hr,
        "resting_hr": threshold.resting_hr,
        "confidence": threshold.confidence_score,
        "method": threshold.calculation_method,
    }
