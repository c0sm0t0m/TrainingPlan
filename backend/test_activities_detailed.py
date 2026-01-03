#!/usr/bin/env python3
"""
Detailed test for Garmin activities - to check the actual API response.
"""
import asyncio
import sys
import os
from datetime import datetime, timedelta
import json

sys.path.insert(0, '/Users/boetthw3/Documents/99_Other/TrainingPlan/backend')

from src.services.garmin_service import garmin_service

GARMIN_EMAIL = os.getenv('GARMIN_EMAIL', 'th.boettger@web.de')
GARMIN_PASSWORD = os.getenv('GARMIN_PASSWORD', '2025Dpige.2025')


async def test_activities():
    """Test fetching activities with detailed output."""
    print("=" * 80)
    print("Garmin Activities Detailed Test")
    print("=" * 80)
    print()
    
    # Step 1: Authenticate
    print("1. Authenticating...")
    try:
        result = await garmin_service.authenticate(GARMIN_EMAIL, GARMIN_PASSWORD)
        print("✓ Authentication successful")
        oauth1_token = result['oauth1_token']
        oauth2_token = result['oauth2_token']
    except Exception as e:
        print(f"✗ Authentication failed: {e}")
        return
    
    print()
    
    # Step 2: Test different date ranges
    test_ranges = [
        ("Last 7 days", 7),
        ("Last 30 days", 30),
        ("Last 90 days", 90),
        ("Last 365 days", 365),
    ]
    
    for description, days in test_ranges:
        print(f"2. Testing: {description}")
        print("-" * 80)
        
        try:
            start_date = datetime.utcnow() - timedelta(days=days)
            activities = await garmin_service.get_activities(
                oauth1_token,
                oauth2_token,
                start_date=start_date,
                limit=100
            )
            
            print(f"   Found: {len(activities)} activities")
            
            if activities:
                print(f"   First activity:")
                activity = activities[0] if isinstance(activities, list) else activities
                print(f"   {json.dumps(activity, indent=6, default=str)[:500]}...")
                break  # Found activities, stop testing
            
        except Exception as e:
            print(f"   ✗ Error: {e}")
            import traceback
            print(f"   {traceback.format_exc()[:500]}...")
        
        print()
    
    # Step 3: Try to get all activities without date filter
    print("3. Testing: All activities (no date filter)")
    print("-" * 80)
    
    try:
        activities = await garmin_service.get_activities(
            oauth1_token,
            oauth2_token,
            start_date=None,  # This should default to last 30 days
            limit=100
        )
        
        print(f"   Found: {len(activities)} activities")
        
        if activities:
            print(f"\n   Activity list structure:")
            print(f"   Type: {type(activities)}")
            if isinstance(activities, dict):
                print(f"   Keys: {activities.keys()}")
            elif isinstance(activities, list) and len(activities) > 0:
                print(f"   First item type: {type(activities[0])}")
                if isinstance(activities[0], dict):
                    print(f"   First item keys: {activities[0].keys()}")
                print(f"\n   Sample activity:")
                print(json.dumps(activities[0], indent=6, default=str))
        else:
            print("   ⚠ No activities found")
            print("\n   This could mean:")
            print("   - The account genuinely has no activities")
            print("   - The API endpoint structure changed")
            print("   - The date range calculation is incorrect")
            
    except Exception as e:
        print(f"   ✗ Error: {e}")
        import traceback
        print(f"\n   Full traceback:")
        print(traceback.format_exc())
    
    print()
    print("=" * 80)


if __name__ == "__main__":
    asyncio.run(test_activities())
