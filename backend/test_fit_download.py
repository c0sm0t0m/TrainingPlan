"""
Test FIT file download and parsing for recent activities
"""
import asyncio
import sys
from pathlib import Path

# Add backend src to path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

from src.database import engine, AsyncSessionLocal
from src.models.user import User
from src.models.garmin_activity import GarminActivity
from src.services.garmin_service import garmin_service
from src.utils.fit_parser import parse_fit_time_series
from sqlalchemy import select


async def test_fit_download():
    """Test downloading and parsing FIT files for recent activities."""
    
    # Create async session
    async with AsyncSessionLocal() as db:
        # Get first user with Garmin connected
        result = await db.execute(
            select(User).where(User.garmin_connected == True).limit(1)
        )
        user = result.scalar_one_or_none()
        
        if not user:
            print("❌ No user with Garmin connected found")
            return
        
        print(f"✅ Found user: {user.email}")
        print(f"   Garmin connected: {user.garmin_connected}")
        print(f"   Has OAuth tokens: {bool(user.garmin_oauth1_token and user.garmin_oauth2_token)}\n")
        
        # Get recent activities that should have GPS data
        result = await db.execute(
            select(GarminActivity)
            .where(GarminActivity.user_id == user.id)
            .where(GarminActivity.has_polyline == True)
            .order_by(GarminActivity.start_time_local.desc())
            .limit(3)
        )
        activities = result.scalars().all()
        
        if not activities:
            print("❌ No activities with GPS data found")
            return
        
        print(f"🏃 Found {len(activities)} activities with has_polyline=True\n")
        
        # Test each activity
        for i, activity in enumerate(activities, 1):
            print(f"{'='*80}")
            print(f"Activity {i}: {activity.activity_name}")
            print(f"{'='*80}")
            print(f"Garmin ID: {activity.garmin_activity_id}")
            print(f"Date: {activity.start_time_local}")
            print(f"Type: {activity.activity_type}")
            print(f"Distance: {activity.distance_meters}m")
            print(f"Duration: {activity.duration_seconds}s")
            print(f"Has polyline: {activity.has_polyline}")
            print(f"Average HR: {activity.average_hr}")
            
            # Check if time series already cached
            has_cached_time_series = False
            if activity.raw_data and "time_series" in activity.raw_data:
                has_cached_time_series = True
                ts = activity.raw_data["time_series"]["time_series"]
                print(f"\n✅ Activity already has cached time series data:")
                print(f"   Total points: {len(ts['timestamps'])}")
                print(f"   Has GPS: {any(lat is not None for lat in ts['latitude'])}")
                print(f"   Has HR: {any(hr is not None for hr in ts['heart_rate'])}")
                print(f"   Has power: {any(p is not None for p in ts['power'])}")
            else:
                print(f"\n⚠️  NO cached time series data in raw_data")
            
            # Test FIT download
            print(f"\n📥 Testing FIT file download...")
            try:
                fit_data = await garmin_service.download_activity_fit(
                    user.garmin_oauth1_token,
                    user.garmin_oauth2_token,
                    int(activity.garmin_activity_id)
                )
                
                print(f"✅ FIT file downloaded successfully")
                print(f"   Size: {len(fit_data):,} bytes ({len(fit_data)/1024:.1f} KB)")
                
                # Test parsing
                print(f"\n🔍 Parsing FIT file...")
                parsed = parse_fit_time_series(fit_data)
                
                if "error" in parsed:
                    print(f"❌ Parse error: {parsed['error']}")
                else:
                    ts = parsed["time_series"]
                    meta = parsed["metadata"]
                    print(f"✅ FIT file parsed successfully")
                    print(f"\n📊 Time Series Data:")
                    print(f"   Total points: {meta['total_points']}")
                    print(f"   Duration: {meta['duration_seconds']}s")
                    print(f"   Has GPS: {meta['has_gps']} ({sum(1 for lat in ts['latitude'] if lat is not None)} points)")
                    print(f"   Has HR: {meta['has_heart_rate']} ({meta['heart_rate_stats']['count']} points)")
                    if meta['heart_rate_stats']['avg']:
                        print(f"      HR: {meta['heart_rate_stats']['min']:.0f} - {meta['heart_rate_stats']['max']:.0f} bpm (avg {meta['heart_rate_stats']['avg']:.0f})")
                    print(f"   Has altitude: {meta['has_altitude']} ({meta['altitude_stats']['count']} points)")
                    print(f"   Has power: {meta['has_power']} ({meta['power_stats']['count']} points)")
                    
                    # Show sample of GPS data
                    if meta['has_gps']:
                        gps_points = [(lat, lon) for lat, lon in zip(ts['latitude'], ts['longitude']) if lat is not None]
                        print(f"\n🗺️  Sample GPS points (first 3):")
                        for j, (lat, lon) in enumerate(gps_points[:3], 1):
                            print(f"      {j}. ({lat:.6f}, {lon:.6f})")
                    
                    # Compare with cached data
                    if has_cached_time_series:
                        cached_ts = activity.raw_data["time_series"]["time_series"]
                        cached_points = len(cached_ts["timestamps"])
                        new_points = meta["total_points"]
                        if cached_points == new_points:
                            print(f"\n✅ Cached data matches downloaded data ({cached_points} points)")
                        else:
                            print(f"\n⚠️  Cached data has different point count: {cached_points} vs {new_points}")
                    
            except Exception as e:
                print(f"❌ FIT download/parse failed: {str(e)}")
                import traceback
                print(f"\nFull error:\n{traceback.format_exc()}")
            
            print("\n")


if __name__ == "__main__":
    asyncio.run(test_fit_download())
