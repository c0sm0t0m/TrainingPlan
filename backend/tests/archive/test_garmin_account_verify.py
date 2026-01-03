#!/usr/bin/env python3
"""
Comprehensive Garmin account verification.
"""
import asyncio
import sys
import os
from datetime import datetime, timedelta
import json

sys.path.insert(0, '/Users/boetthw3/Documents/99_Other/TrainingPlan/backend')

from src.services.garmin_service import garmin_service
import garth

GARMIN_EMAIL = os.getenv('GARMIN_EMAIL', 'th.boettger@web.de')
GARMIN_PASSWORD = os.getenv('GARMIN_PASSWORD', '2025Dpige.2025')


async def verify_account():
    """Comprehensive account verification."""
    print("=" * 80)
    print("Garmin Account Comprehensive Verification")
    print("=" * 80)
    print()
    
    # Authenticate
    print("1. Authenticating...")
    result = await garmin_service.authenticate(GARMIN_EMAIL, GARMIN_PASSWORD)
    print("✓ Authentication successful")
    print()
    
    # Get user profile
    print("2. Fetching user profile...")
    print("-" * 80)
    try:
        profile = garth.client.connectapi("/userprofile-service/userprofile")
        print(f"  ✓ Success!")
        print(f"  Profile: {json.dumps(profile, indent=4, default=str)}")
    except Exception as e:
        print(f"  ✗ Error: {e}")
    print()
    
    # Get user social profile (contains display name, etc.)
    print("3. Fetching social profile...")
    print("-" * 80)
    try:
        social = garth.client.connectapi("/userprofile-service/socialProfile")
        print(f"  ✓ Success!")
        print(f"  Social: {json.dumps(social, indent=4, default=str)}")
    except Exception as e:
        print(f"  ✗ Error: {e}")
    print()
    
    # Get user settings
    print("4. Fetching user settings...")
    print("-" * 80)
    try:
        settings = garth.client.connectapi("/userprofile-service/userprofile/settings")
        print(f"  ✓ Success!")
        print(f"  Settings: {json.dumps(settings, indent=4, default=str)[:500]}...")
    except Exception as e:
        print(f"  ✗ Error: {e}")
    print()
    
    # Check activity count from user stats
    print("5. Checking user statistics...")
    print("-" * 80)
    try:
        # Try different date ranges
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=365)
        
        stats = garth.client.connectapi(
            "/userstats-service/statistics",
            params={
                "startDate": start_date.strftime("%Y-%m-%d"),
                "endDate": end_date.strftime("%Y-%m-%d")
            }
        )
        print(f"  ✓ Success!")
        print(f"  Stats: {json.dumps(stats, indent=4, default=str)}")
    except Exception as e:
        print(f"  ✗ Error: {e}")
    print()
    
    # Check activity summary
    print("6. Checking activity summary...")
    print("-" * 80)
    try:
        summary = garth.client.connectapi("/activitylist-service/activities/aggregated")
        print(f"  ✓ Success!")
        print(f"  Summary: {json.dumps(summary, indent=4, default=str)}")
    except Exception as e:
        print(f"  ✗ Error: {e}")
    print()
    
    # Try to get just activity IDs
    print("7. Trying to get activity IDs...")
    print("-" * 80)
    try:
        ids = garth.client.connectapi(
            "/activitylist-service/activities",
            params={"start": 0, "limit": 1}
        )
        print(f"  ✓ Success!")
        print(f"  Response: {json.dumps(ids, indent=4, default=str)}")
    except Exception as e:
        print(f"  ✗ Error: {e}")
    print()
    
    # Check if there are any workouts
    print("8. Checking workouts...")
    print("-" * 80)
    try:
        workouts = garth.client.connectapi("/workout-service/workouts")
        print(f"  ✓ Success!")
        print(f"  Workouts: {json.dumps(workouts, indent=4, default=str)[:500]}...")
    except Exception as e:
        print(f"  ✗ Error: {e}")
    print()
    
    print("=" * 80)
    print("\nConclusion:")
    print("-" * 80)
    print("If all endpoints return empty results, this account likely:")
    print("  - Has never recorded any activities")
    print("  - Is a newly created account")
    print("  - Has had all activities deleted")
    print()
    print("To test with activities:")
    print("  1. Use the Garmin Connect mobile app to record an activity")
    print("  2. Or manually create an activity on connect.garmin.com")
    print("  3. Then run this test again")
    print("=" * 80)


if __name__ == "__main__":
    asyncio.run(verify_account())
