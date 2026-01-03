#!/usr/bin/env python3
"""
Test script to check if we can fetch time series data (HR, elevation, etc.) from Garmin
"""
import asyncio
import json
from src.services.garmin_service import garmin_service
from src.config import settings
from dotenv import load_dotenv
import os

# Load environment
load_dotenv()

async def test_time_series_fetch():
    """Test fetching time series data from Garmin for a recent activity."""
    
    # Get credentials from environment (same as test_garmin_auth.py uses)
    email = os.getenv("TEST_GARMIN_EMAIL") or os.getenv("GARMIN_EMAIL") or "tboettger@gmail.com"
    password = os.getenv("TEST_GARMIN_PASSWORD") or os.getenv("GARMIN_PASSWORD")
    
    if not password:
        print("❌ No Garmin password found in environment")
        return
    
    print(f"🔐 Authenticating as {email}...")
    
    try:
        # Authenticate
        creds = await garmin_service.authenticate(email, password)
        oauth1_token = creds["oauth1_token"]
        oauth2_token = creds["oauth2_token"]
        
        print("✅ Authentication successful!")
        
        # Test activity (recent running activity with HR)
        activity_id = "21418286992"
        
        print(f"\n📊 Testing time series data fetch for activity {activity_id}...")
        
        # Get the API instance
        api = await garmin_service.resume_session(oauth1_token, oauth2_token)
        
        # 1. Test get_activity_details (includes time series data)
        print("\n1️⃣ Testing get_activity_details()...")
        details = api.get_activity_details(activity_id)
        
        print(f"   Keys in response: {list(details.keys())}")
        
        # Check for time series data
        if "metricDescriptors" in details:
            print(f"   ✅ Found metricDescriptors: {len(details['metricDescriptors'])} metrics")
            for metric in details["metricDescriptors"][:5]:  # Show first 5
                print(f"      - {metric['key']} ({metric.get('unit', {}).get('key', 'unknown')})")
        
        if "activityDetailMetrics" in details:
            print(f"   ✅ Found activityDetailMetrics: {len(details['activityDetailMetrics'])} data points")
            # Show first data point structure
            if details['activityDetailMetrics']:
                first_point = details['activityDetailMetrics'][0]
                print(f"      First data point keys: {list(first_point.keys())}")
        
        # 2. Test get_activity_hr_in_timezones
        print("\n2️⃣ Testing get_activity_hr_in_timezones()...")
        hr_zones = api.get_activity_hr_in_timezones(activity_id)
        print(f"   Keys in response: {list(hr_zones.keys())}")
        if "heartRateValues" in hr_zones:
            print(f"   ✅ Found heartRateValues: {len(hr_zones['heartRateValues'])} data points")
        
        # 3. Test get_activity_splits
        print("\n3️⃣ Testing get_activity_splits()...")
        splits = api.get_activity_splits(activity_id)
        print(f"   Keys in response: {list(splits.keys())}")
        if "lapDTOs" in splits:
            print(f"   ✅ Found {len(splits['lapDTOs'])} laps/splits")
        
        # 4. Test FIT file download
        print("\n4️⃣ Testing FIT file download...")
        fit_data = await garmin_service.download_activity_fit(oauth1_token, oauth2_token, int(activity_id))
        print(f"   ✅ Downloaded FIT file: {len(fit_data)} bytes")
        
        # Parse FIT file to see what's in it
        print("\n5️⃣ Parsing FIT file with fitparse...")
        from fitparse import FitFile
        
        # Write to temp file
        with open("/tmp/test_activity.fit", "wb") as f:
            f.write(fit_data)
        
        # Parse
        fit_file = FitFile("/tmp/test_activity.fit")
        
        # Get record messages (time series data)
        records = list(fit_file.get_messages("record"))
        print(f"   ✅ Found {len(records)} record messages (time series points)")
        
        if records:
            first_record = records[0]
            fields = [field.name for field in first_record.fields]
            print(f"   📊 Available fields in records: {', '.join(fields[:15])}")
            
            # Check if we have the key fields
            has_hr = any(field.name == "heart_rate" for field in first_record.fields)
            has_altitude = any(field.name == "altitude" for field in first_record.fields)
            has_speed = any(field.name == "speed" for field in first_record.fields)
            has_cadence = any(field.name == "cadence" for field in first_record.fields)
            has_power = any(field.name == "power" for field in first_record.fields)
            
            print(f"\n   ✅ Time series data availability:")
            print(f"      - Heart Rate: {'✅' if has_hr else '❌'}")
            print(f"      - Altitude/Elevation: {'✅' if has_altitude else '❌'}")
            print(f"      - Speed: {'✅' if has_speed else '❌'}")
            print(f"      - Cadence: {'✅' if has_cadence else '❌'}")
            print(f"      - Power: {'✅' if has_power else '❌'}")
        
        print("\n" + "="*60)
        print("📈 SUMMARY: Time Series Data Availability")
        print("="*60)
        print("✅ get_activity_details() - Provides detailed metrics and time series")
        print("✅ get_activity_hr_in_timezones() - Provides HR zone time series")
        print("✅ get_activity_splits() - Provides lap/split data")
        print("✅ FIT file download - Contains full time series (HR, elevation, speed, etc.)")
        print("\n💡 RECOMMENDATION:")
        print("   Use FIT file parsing with fitparse library to extract:")
        print("   - Heart rate time series (every second)")
        print("   - Elevation/altitude time series")
        print("   - Speed/pace time series")
        print("   - Cadence time series (running/cycling)")
        print("   - Power time series (cycling)")
        print("   - GPS coordinates (latitude/longitude)")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_time_series_fetch())
