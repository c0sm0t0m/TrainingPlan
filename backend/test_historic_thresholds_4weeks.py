"""
Test historic threshold calculation for 4 weeks
Shows detailed step-by-step process
"""
import asyncio
import sys
from datetime import datetime, timedelta
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

# Add backend to path
sys.path.insert(0, '/Users/boetthw3/Documents/99_Other/TrainingPlan/backend')

from src.database import get_db, engine
from src.models.user import User
from src.models.garmin_activity import GarminActivity
from src.models.weekly_threshold import WeeklyThreshold
from src.utils.historic_thresholds import calculate_historic_thresholds


async def test_4_weeks():
    """Test calculating historic thresholds for 4 weeks."""
    
    print("=" * 80)
    print("HISTORIC THRESHOLD CALCULATION TEST - 4 WEEKS")
    print("=" * 80)
    print()
    
    # Get database session
    async with AsyncSession(engine) as db:
        # Get user
        result = await db.execute(
            select(User).where(User.email == "tboettger@gmail.com")
        )
        user = result.scalar_one_or_none()
        
        if not user:
            print("❌ User not found")
            return
        
        print(f"👤 User: {user.email}")
        print(f"📊 Current Thresholds:")
        print(f"   - Running HR: {user.running_threshold_hr} bpm")
        print(f"   - Cycling HR: {user.cycling_threshold_hr} bpm")
        print(f"   - FTP: {user.ftp} W")
        print(f"   - Max HR: {user.max_hr} bpm")
        print(f"   - Resting HR: {user.resting_hr} bpm")
        print()
        
        # Get activity count
        result = await db.execute(
            select(GarminActivity).where(GarminActivity.user_id == user.id)
        )
        all_activities = result.scalars().all()
        print(f"📁 Total activities in database: {len(all_activities)}")
        print()
        
        # Show activities from last 4 weeks
        four_weeks_ago = datetime.now() - timedelta(weeks=4)
        recent_activities = [
            a for a in all_activities 
            if a.start_time_local and a.start_time_local >= four_weeks_ago
        ]
        print(f"🏃 Activities in last 4 weeks: {len(recent_activities)}")
        
        if recent_activities:
            print(f"\n   Recent activities breakdown:")
            activities_by_week = {}
            for activity in recent_activities:
                year, week, _ = activity.start_time_local.isocalendar()
                key = f"{year}-W{week:02d}"
                if key not in activities_by_week:
                    activities_by_week[key] = []
                activities_by_week[key].append(activity)
            
            for week_key in sorted(activities_by_week.keys(), reverse=True):
                activities = activities_by_week[week_key]
                print(f"   {week_key}: {len(activities)} activities")
                for act in activities[:3]:  # Show first 3
                    sport = act.activity_type or "Unknown"
                    duration = act.duration / 60 if act.duration else 0
                    avg_hr = act.average_hr or "N/A"
                    print(f"      • {sport}: {duration:.0f}min, HR={avg_hr}")
        
        print()
        print("-" * 80)
        print("CALCULATING HISTORIC THRESHOLDS (4 weeks)...")
        print("-" * 80)
        print()
        
        # Calculate thresholds
        stats = await calculate_historic_thresholds(
            user=user,
            db=db,
            lookback_weeks=4  # Only 4 weeks
        )
        
        print()
        print("-" * 80)
        print("CALCULATION COMPLETE")
        print("-" * 80)
        print()
        print(f"✅ Results:")
        print(f"   - Weeks calculated: {stats['weeks_calculated']}")
        print(f"   - Activities analyzed: {stats['activities_analyzed']}")
        print(f"   - Date range: {stats['oldest_week']} to {stats['newest_week']}")
        print()
        
        # Query and display the calculated thresholds
        result = await db.execute(
            select(WeeklyThreshold)
            .where(WeeklyThreshold.user_id == user.id)
            .order_by(WeeklyThreshold.year.desc(), WeeklyThreshold.week.desc())
            .limit(5)
        )
        thresholds = result.scalars().all()
        
        print("-" * 80)
        print("CALCULATED WEEKLY THRESHOLDS (newest first):")
        print("-" * 80)
        print()
        
        for t in thresholds:
            print(f"📅 {t.year}-W{t.week:02d}")
            print(f"   Running HR:  {t.running_threshold_hr} bpm")
            print(f"   Cycling HR:  {t.cycling_threshold_hr} bpm")
            print(f"   FTP:         {t.ftp} W")
            print(f"   Method:      {t.calculation_method}")
            print(f"   Confidence:  {t.confidence_score:.2f}")
            print(f"   Activities:  {t.activities_used}")
            print()
        
        print("=" * 80)
        print("HOW IT WORKS:")
        print("=" * 80)
        print()
        print("The historic threshold calculator uses this strategy:")
        print()
        print("1️⃣  CURRENT WEEK (weeks_ago = 0)")
        print("   → Uses your current threshold settings (no calculation)")
        print("   → Confidence: 1.0 (100% - these are your actual values)")
        print()
        print("2️⃣  RECENT WEEKS (weeks_ago = 1-4)")
        print("   → Assumes small degradation: 0.5% per week")
        print("   → Example: 3 weeks ago = 165 * 0.985 = ~162 bpm")
        print("   → Confidence: 0.95 (95% - conservative estimate)")
        print()
        print("3️⃣  OLDER WEEKS (weeks_ago > 4) - Not tested here")
        print("   → Analyzes actual activity performance")
        print("   → For running: Uses 85th percentile HR from hard efforts")
        print("   → For cycling: Uses 90th percentile power")
        print("   → Blends: 60% performance data + 40% trend extrapolation")
        print("   → Confidence: 0.5-0.7 (depends on activity count)")
        print()
        print("4️⃣  WEEKS WITHOUT ACTIVITIES")
        print("   → Uses trend-based degradation (0.3% per week)")
        print("   → Confidence: 0.4 (40% - estimation only)")
        print()
        print("This means historic TSS will be recalculated using thresholds")
        print("appropriate for your fitness level at that time.")
        print()


if __name__ == "__main__":
    asyncio.run(test_4_weeks())
