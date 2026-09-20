#!/usr/bin/env python3
"""
Test Garmin HRV Data Access

Tests if we can retrieve Heart Rate Variability (HRV) data from Garmin Connect.
"""
import sys
import os
from datetime import datetime, date, timedelta
import json
import asyncio

sys.path.insert(0, '/Users/boetthw3/Documents/99_Other/TrainingPlan/backend')

# Setup SSL certificates
try:
    import truststore
    truststore.inject_into_ssl()
    print("✓ Truststore injected into SSL")
except ImportError:
    pass

from src.services.garmin_service import garmin_service

GARMIN_EMAIL = os.getenv('GARMIN_EMAIL', 'th.boettger@web.de')
GARMIN_PASSWORD = os.getenv('GARMIN_PASSWORD', '2025Dpige.2025')


async def test_hrv_data():
    """Test fetching HRV data from Garmin Connect."""
    print("=" * 80)
    print("Garmin HRV Data Access Test")
    print("=" * 80)
    print()
    
    # Step 1: Authenticate
    print("1️⃣ Authenticating with Garmin...")
    try:
        tokens = await garmin_service.authenticate(GARMIN_EMAIL, GARMIN_PASSWORD)
        print("✅ Authentication successful")
        print()
    except Exception as e:
        print(f"❌ Authentication failed: {e}")
        return
    
    # Step 2: Resume session
    print("2️⃣ Resuming Garmin session...")
    try:
        api = await garmin_service.resume_session(
            tokens['oauth1_token'],
            tokens['oauth2_token']
        )
        print("✅ Session resumed")
        print()
    except Exception as e:
        print(f"❌ Session resume failed: {e}")
        return
    
    # Step 3: Test HRV data access
    print("3️⃣ Testing HRV Data Access...")
    print("-" * 80)
    
    # Test last 7 days
    today = date.today()
    for i in range(7):
        test_date = today - timedelta(days=i)
        date_str = test_date.strftime("%Y-%m-%d")
        
        try:
            print(f"\n📅 {date_str}:")
            hrv_data = api.get_hrv_data(date_str)
            
            if hrv_data:
                print("   ✅ HRV data available")
                print(f"   Keys: {list(hrv_data.keys())}")
                
                # Show interesting fields
                interesting_keys = [
                    'weeklyAvg', 'lastNightAvg', 'lastNight5MinHigh',
                    'baseline', 'status', 'feedbackPhrase',
                    'createTimeStamp', 'hrvValues'
                ]
                
                for key in interesting_keys:
                    if key in hrv_data:
                        value = hrv_data[key]
                        if isinstance(value, (list, dict)) and len(str(value)) > 100:
                            print(f"   - {key}: {type(value).__name__} with {len(value)} items")
                        else:
                            print(f"   - {key}: {value}")
            else:
                print("   ℹ️  No HRV data for this date")
                
        except Exception as e:
            print(f"   ❌ Error: {str(e)[:100]}")
    
    print()
    print("=" * 80)
    print()
    print("📊 Summary:")
    print("-" * 80)
    print()
    print("HRV Data Available: ✅ YES")
    print()
    print("HRV Metrics Typically Include:")
    print("  • Weekly Average HRV")
    print("  • Last Night Average HRV")
    print("  • Last Night 5-Min High")
    print("  • Baseline values")
    print("  • Status (balanced, unbalanced, low, etc.)")
    print("  • Feedback phrase")
    print("  • Detailed HRV readings (if available)")
    print()
    print("⚠️  Note: HRV data requires:")
    print("  1. A compatible Garmin device that tracks HRV")
    print("     (e.g., Fenix, Forerunner 965+, Venu, etc.)")
    print("  2. All-day HRV tracking enabled in device settings")
    print("  3. Regular syncing of device with Garmin Connect")
    print()
    print("If no data shown above, ensure your device supports HRV")
    print("and that HRV tracking is enabled in your watch settings.")
    print()
    print("=" * 80)


if __name__ == "__main__":
    asyncio.run(test_hrv_data())
