#!/usr/bin/env python3
"""
Test improved TSS calculation using time series data
Compare with old calculation method
"""
import asyncio
from src.utils.fit_parser import parse_fit_time_series
from src.utils.calculations.tss_from_time_series import calculate_tss_from_time_series, get_time_series_tss_summary
from src.utils.calculations.tss_calculator import calculate_tss_from_activity
from src.services.garmin_service import garmin_service
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select
from src.models.user import User
from src.models.garmin_activity import GarminActivity
from src.config import settings

async def test_tss_comparison():
    """Compare old vs new TSS calculation"""
    
    engine = create_async_engine(settings.database_url, echo=False)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    async with async_session() as session:
        # Get user
        result = await session.execute(
            select(User).where(User.email == "tboettger@gmail.com")
        )
        user = result.scalar_one_or_none()
        
        if not user or not user.garmin_connected:
            print("❌ User not found or Garmin not connected")
            return
        
        # Get skiing activity from today
        activity_result = await session.execute(
            select(GarminActivity).where(GarminActivity.id == 227)
        )
        activity = activity_result.scalar_one_or_none()
        
        if not activity:
            print("❌ Activity not found")
            return
        
        print(f"⛷️  Activity: {activity.activity_name}")
        print(f"   Type: {activity.activity_type}")
        print(f"   Duration: {activity.duration_seconds/60:.1f} min")
        print(f"   Avg HR: {activity.average_hr} bpm")
        print(f"   Garmin TSS: {activity.training_load}")
        print(f"   Current calculated TSS: {activity.calculated_tss}")
        
        # Download FIT file
        print(f"\n📥 Downloading FIT file...")
        fit_data = await garmin_service.download_activity_fit(
            user.garmin_oauth1_token,
            user.garmin_oauth2_token,
            int(activity.garmin_activity_id)
        )
        
        # Parse time series
        print(f"📊 Parsing time series...")
        time_series_result = parse_fit_time_series(fit_data)
        
        if "error" in time_series_result:
            print(f"❌ Error: {time_series_result['error']}")
            return
        
        # Show time series summary
        metadata = time_series_result.get("metadata", {})
        print(f"   Total samples: {metadata.get('total_points', 0)}")
        print(f"   Duration: {metadata.get('duration_seconds', 0)/60:.1f} min")
        print(f"   Has HR: {metadata.get('has_heart_rate', False)}")
        print(f"   Has Power: {metadata.get('has_power', False)}")
        
        # User settings (skiing now uses running threshold)
        user_settings = {
            "ftp": user.ftp,
            "threshold_pace": user.threshold_pace,
            "threshold_hr": user.running_threshold_hr,  # Use running threshold for all non-cycling/swimming
            "max_hr": user.max_hr,
            "resting_hr": user.resting_hr or 50,
        }
        
        print(f"\n👤 User Settings:")
        print(f"   FTP: {user.ftp}W")
        print(f"   Max HR: {user.max_hr} bpm")
        print(f"   Threshold HR (skiing uses running): {user.running_threshold_hr} bpm")
        print(f"   Resting HR: {user_settings['resting_hr']} bpm")
        
        # Calculate TSS using OLD method (summary data)
        print(f"\n📊 OLD Method (summary averages):")
        old_tss = calculate_tss_from_activity(activity.raw_data, user_settings)
        print(f"   TSS: {old_tss}")
        
        # Calculate TSS using NEW method (time series)
        print(f"\n📊 NEW Method (time series):")
        new_tss = calculate_tss_from_time_series(
            time_series_result,
            user_settings,
            activity.activity_type
        )
        
        if new_tss is not None:
            summary = get_time_series_tss_summary(time_series_result, new_tss)
            print(f"   {summary}")
        else:
            print(f"   Could not calculate from time series")
        
        # Comparison
        print(f"\n📈 COMPARISON:")
        print(f"   Garmin TSS:      {activity.training_load}")
        print(f"   OLD calculation: {old_tss}")
        print(f"   NEW calculation: {new_tss}")
        
        if new_tss and old_tss:
            diff = new_tss - old_tss
            pct_diff = (diff / old_tss * 100) if old_tss else 0
            print(f"   Difference:      {diff:+.1f} ({pct_diff:+.1f}%)")
        
        if activity.training_load and new_tss:
            garmin_diff = activity.training_load - new_tss
            garmin_pct = (garmin_diff / activity.training_load * 100) if activity.training_load else 0
            print(f"   vs Garmin:       {garmin_diff:+.1f} ({garmin_pct:+.1f}%)")
    
    await engine.dispose()

if __name__ == "__main__":
    asyncio.run(test_tss_comparison())
