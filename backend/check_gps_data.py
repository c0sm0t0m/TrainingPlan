"""
Check if GPS and time series data are stored in the database for activities.
"""
import asyncio
import json
from sqlalchemy import select
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from src.models.garmin_activity import GarminActivity
from src.config import settings


async def check_gps_data():
    """Check GPS and time series data in database."""
    # Create async engine
    engine = create_async_engine(settings.database_url, echo=False)
    
    # Create session
    async_session = sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )
    
    async with async_session() as session:
        # Get a few recent activities
        result = await session.execute(
            select(GarminActivity)
            .order_by(GarminActivity.start_time_local.desc())
            .limit(5)
        )
        activities = result.scalars().all()
        
        print(f"\n📊 Found {len(activities)} recent activities to check\n")
        print("=" * 80)
        
        for i, activity in enumerate(activities, 1):
            print(f"\n🏃 Activity {i}: {activity.activity_name}")
            print(f"   Date: {activity.start_time_local}")
            print(f"   Type: {activity.activity_type}")
            print(f"   has_polyline: {activity.has_polyline}")
            print(f"   Duration: {activity.duration_seconds}s")
            print(f"   Distance: {activity.distance_meters}m" if activity.distance_meters else "   Distance: None")
            
            # Check raw_data
            if activity.raw_data:
                raw = activity.raw_data
                print(f"\n   📦 raw_data type: {type(raw)}")
                
                if isinstance(raw, dict):
                    print(f"   📦 raw_data keys: {list(raw.keys())[:20]}")  # Show first 20 keys
                    
                    # Check for GPS data
                    gps_keys = ['samples', 'geoPolyline', 'activityDetailMetrics', 'summaryDTO']
                    for key in gps_keys:
                        if key in raw:
                            data = raw[key]
                            if isinstance(data, list):
                                print(f"   ✅ Found '{key}': list with {len(data)} items")
                                if len(data) > 0:
                                    print(f"      First item type: {type(data[0])}")
                                    if isinstance(data[0], dict):
                                        print(f"      First item keys: {list(data[0].keys())[:15]}")
                            elif isinstance(data, dict):
                                print(f"   ✅ Found '{key}': dict with keys {list(data.keys())[:10]}")
                            else:
                                print(f"   ⚠️  Found '{key}': {type(data)}")
                    
                    # Check samples in detail
                    if 'samples' in raw:
                        samples = raw['samples']
                        if len(samples) > 0:
                            first_sample = samples[0]
                            print(f"\n   📍 First sample analysis:")
                            print(f"      Keys: {list(first_sample.keys()) if isinstance(first_sample, dict) else 'Not a dict'}")
                            
                            # Check for GPS coordinates
                            has_lat = 'lat' in first_sample or 'latitude' in first_sample
                            has_lng = 'lng' in first_sample or 'longitude' in first_sample
                            has_hr = 'heartRate' in first_sample or 'hr' in first_sample
                            has_speed = 'speed' in first_sample
                            has_elevation = 'elevation' in first_sample or 'altitude' in first_sample
                            has_power = 'power' in first_sample or 'watts' in first_sample
                            has_timestamp = 'timestamp' in first_sample
                            
                            print(f"      ✅ GPS (lat/lng): {has_lat and has_lng}")
                            print(f"      ✅ Heart Rate: {has_hr}")
                            print(f"      ✅ Speed: {has_speed}")
                            print(f"      ✅ Elevation: {has_elevation}")
                            print(f"      ✅ Power: {has_power}")
                            print(f"      ✅ Timestamp: {has_timestamp}")
                            
                            # Show sample values
                            if has_lat and has_lng:
                                lat = first_sample.get('lat') or first_sample.get('latitude')
                                lng = first_sample.get('lng') or first_sample.get('longitude')
                                print(f"      Sample coords: lat={lat}, lng={lng}")
                            
                            if has_hr:
                                hr = first_sample.get('heartRate') or first_sample.get('hr')
                                print(f"      Sample HR: {hr} bpm")
                            
                            if has_speed:
                                speed = first_sample.get('speed')
                                print(f"      Sample speed: {speed} m/s")
                    
                    # Check for laps
                    if 'laps' in raw:
                        laps = raw['laps']
                        print(f"\n   🔄 Laps: {len(laps)} laps found")
                        if len(laps) > 0 and isinstance(laps[0], dict):
                            print(f"      First lap keys: {list(laps[0].keys())[:15]}")
                
                else:
                    print(f"   ⚠️  raw_data is not a dict: {type(raw)}")
                    
                # Show raw_data size
                raw_json = json.dumps(raw, default=str)
                print(f"   📏 raw_data size: {len(raw_json):,} bytes ({len(raw_json)/1024:.1f} KB)")
            else:
                print(f"   ❌ No raw_data stored!")
            
            print("\n" + "-" * 80)
        
        print("\n✅ Database check complete\n")
    
    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(check_gps_data())
