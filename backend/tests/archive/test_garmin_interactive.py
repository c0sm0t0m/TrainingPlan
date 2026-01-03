#!/usr/bin/env python3
"""
Interactive Garmin account test - to confirm actual activities exist.
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


async def interactive_test():
    """Interactive test to verify activities."""
    print("=" * 80)
    print("Garmin Account Interactive Test")
    print("=" * 80)
    print()
    print(f"Testing account: {GARMIN_EMAIL}")
    print()
    print("IMPORTANT: Before running this test, please confirm:")
    print("  1. You can log in to https://connect.garmin.com with these credentials")
    print("  2. You can see activities on your Garmin Connect dashboard")
    print("  3. The account has recorded or uploaded activities")
    print()
    input("Press Enter to continue...")
    print()
    
    # Authenticate
    print("1. Authenticating with Garmin...")
    print("-" * 80)
    try:
        result = await garmin_service.authenticate(GARMIN_EMAIL, GARMIN_PASSWORD)
        print("✓ Authentication successful")
        print()
    except Exception as e:
        print(f"✗ Authentication failed: {e}")
        print()
        print("Please verify:")
        print("  - Email is correct")
        print("  - Password is correct")
        print("  - Account doesn't have 2FA enabled")
        return
    
    # Display user info
    print("2. Fetching account information...")
    print("-" * 80)
    try:
        # Try to get display name
        try:
            social = garth.client.connectapi("/userprofile-service/socialProfile")
            if social and isinstance(social, dict):
                display_name = social.get('displayName', 'Unknown')
                print(f"  Display Name: {display_name}")
        except:
            pass
        
        # Try to get username from client
        username = garth.client.username
        print(f"  Username: {username}")
        print()
    except Exception as e:
        print(f"  ⚠ Could not fetch account info: {e}")
        print()
    
    # Test activities with various parameters
    print("3. Searching for activities...")
    print("-" * 80)
    
    # Try without any date parameters
    print("\n  A. Searching without date filter...")
    try:
        activities = garth.client.connectapi(
            "/activitylist-service/activities/search/activities",
            params={"start": 0, "limit": 10}
        )
        print(f"     Result: {len(activities)} activities")
        if activities:
            print(f"     Sample: {json.dumps(activities[0], indent=6, default=str)[:300]}")
    except Exception as e:
        print(f"     Error: {e}")
    
    # Try with very old start date
    print("\n  B. Searching from 2020-01-01...")
    try:
        activities = garth.client.connectapi(
            "/activitylist-service/activities/search/activities",
            params={
                "start": 0,
                "limit": 10,
                "startDate": "2020-01-01",
                "endDate": datetime.utcnow().strftime("%Y-%m-%d")
            }
        )
        print(f"     Result: {len(activities)} activities")
        if activities:
            print(f"     Sample: {json.dumps(activities[0], indent=6, default=str)[:300]}")
    except Exception as e:
        print(f"     Error: {e}")
    
    # Try the user's activity list endpoint
    print("\n  C. Using activitylist endpoint...")
    try:
        activities = garth.client.connectapi(
            f"/activitylist-service/activities/{garth.client.username}",
            params={"start": 0, "limit": 10}
        )
        print(f"     Result: {len(activities)} activities")
        if activities:
            print(f"     Sample: {json.dumps(activities[0], indent=6, default=str)[:300]}")
    except Exception as e:
        print(f"     Error: {e}")
    
    print()
    print("=" * 80)
    print()
    print("Summary:")
    print("-" * 80)
    print()
    print("If no activities were found, please verify on Garmin Connect:")
    print()
    print("  1. Go to https://connect.garmin.com")
    print("  2. Log in with the same credentials")
    print("  3. Click on 'Activities' in the left menu")
    print("  4. Check if you see any activities listed")
    print()
    print("Possible explanations if Connect shows activities but API doesn't:")
    print("  - Activities might be set to 'Private'")
    print("  - API permissions might need to be explicitly granted")
    print("  - Account might need to accept Terms of Service on connect.garmin.com")
    print("  - Activities might be on a different Garmin account")
    print()
    print("=" * 80)


if __name__ == "__main__":
    asyncio.run(interactive_test())
