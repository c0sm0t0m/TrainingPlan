#!/usr/bin/env python3
"""
Test time series import for skiing activity from 2.1.26
"""
import asyncio
import json
from src.utils.fit_parser import parse_fit_time_series, get_time_series_summary
from src.services.garmin_service import garmin_service
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select
from src.models.user import User
from src.models.garmin_activity import GarminActivity
from src.config import settings

async def test_skiing_activity():
    """Test FIT parsing with skiing activity"""
    
    # Setup database
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
        
        print(f"✅ User: {user.email}")
        print(f"   Garmin connected: {user.garmin_email}")
        
        # Get skiing activity
        activity_result = await session.execute(
            select(GarminActivity).where(
                GarminActivity.id == 227
            )
        )
        activity = activity_result.scalar_one_or_none()
        
        if not activity:
            print("❌ Activity not found")
            return
        
        print(f"\n🎿 Activity: {activity.activity_name}")
        print(f"   Type: {activity.activity_type}")
        print(f"   Date: {activity.start_time_local}")
        print(f"   Distance: {activity.distance_meters/1000:.2f} km")
        print(f"   Duration: {activity.duration_seconds/60:.1f} min")
        print(f"   Avg HR: {activity.average_hr} bpm")
        print(f"   Elevation gain: {activity.elevation_gain_meters:.0f} m")
        
        # Download FIT file
        print(f"\n📥 Downloading FIT file (activity ID: {activity.garmin_activity_id})...")
        fit_data = await garmin_service.download_activity_fit(
            user.garmin_oauth1_token,
            user.garmin_oauth2_token,
            int(activity.garmin_activity_id)
        )
        
        print(f"✅ Downloaded {len(fit_data):,} bytes")
        
        # Parse time series
        print(f"\n📊 Parsing time series data...")
        result = parse_fit_time_series(fit_data)
        
        if "error" in result:
            print(f"❌ Error: {result['error']}")
            return
        
        # Show summary
        summary = get_time_series_summary(result)
        print(f"\n✨ {summary}")
        
        # Show detailed metadata
        metadata = result.get("metadata", {})
        print(f"\n📈 Detailed Metrics:")
        print(f"   📍 Total data points: {metadata.get('total_points'):,}")
        print(f"   ⏱️  Duration: {metadata.get('duration_seconds')}s ({metadata.get('duration_seconds', 0)//60} min {metadata.get('duration_seconds', 0)%60} sec)")
        
        if metadata.get('has_heart_rate'):
            hr_stats = metadata.get('heart_rate_stats', {})
            print(f"   ❤️  Heart Rate:")
            print(f"      Min: {hr_stats.get('min')} bpm")
            print(f"      Max: {hr_stats.get('max')} bpm")
            print(f"      Avg: {hr_stats.get('avg'):.1f} bpm")
            print(f"      Samples: {hr_stats.get('count'):,}")
        
        if metadata.get('has_altitude'):
            alt_stats = metadata.get('altitude_stats', {})
            print(f"   🏔️  Elevation:")
            print(f"      Min: {alt_stats.get('min'):.1f} m")
            print(f"      Max: {alt_stats.get('max'):.1f} m")
            print(f"      Samples: {alt_stats.get('count'):,}")
        
        if metadata.get('has_power'):
            power_stats = metadata.get('power_stats', {})
            print(f"   ⚡ Power:")
            print(f"      Min: {power_stats.get('min')} W")
            print(f"      Max: {power_stats.get('max')} W")
            print(f"      Avg: {power_stats.get('avg'):.1f} W")
        
        speed_stats = metadata.get('speed_stats', {})
        if speed_stats.get('count', 0) > 0:
            print(f"   🏃 Speed:")
            print(f"      Min: {speed_stats.get('min', 0)*3.6:.1f} km/h")
            print(f"      Max: {speed_stats.get('max', 0)*3.6:.1f} km/h")
            print(f"      Avg: {speed_stats.get('avg', 0)*3.6:.1f} km/h")
        
        cadence_stats = metadata.get('cadence_stats', {})
        if cadence_stats.get('count', 0) > 0:
            print(f"   🦵 Cadence:")
            print(f"      Avg: {cadence_stats.get('avg', 0):.1f} spm")
        
        print(f"\n📊 Data Arrays:")
        time_series = result.get("time_series", {})
        for key in ['timestamps', 'heart_rate', 'altitude', 'speed', 'cadence', 'power', 'latitude', 'longitude', 'temperature', 'distance']:
            if key in time_series:
                non_null = sum(1 for v in time_series[key] if v is not None)
                total = len(time_series[key])
                percentage = (non_null / total * 100) if total > 0 else 0
                print(f"   - {key:15s}: {non_null:,}/{total:,} values ({percentage:.1f}%)")
        
        # Show sample of first 5 data points
        print(f"\n📋 Sample Data (first 5 points):")
        for i in range(min(5, len(time_series.get('timestamps', [])))):
            print(f"\n   Point {i+1}:")
            print(f"      Time: {time_series['timestamps'][i]}")
            print(f"      Elapsed: {time_series['elapsed_time'][i]}s")
            if time_series['heart_rate'][i]:
                print(f"      HR: {time_series['heart_rate'][i]} bpm")
            if time_series['altitude'][i]:
                print(f"      Altitude: {time_series['altitude'][i]:.1f} m")
            if time_series['speed'][i]:
                print(f"      Speed: {time_series['speed'][i]*3.6:.1f} km/h")
            if time_series['latitude'][i] and time_series['longitude'][i]:
                print(f"      GPS: {time_series['latitude'][i]:.6f}, {time_series['longitude'][i]:.6f}")
        
        print(f"\n✅ Time series parsing successful!")
        print(f"\n💾 Would store this in raw_data.time_series JSON column")

asyncio.run(test_skiing_activity())
