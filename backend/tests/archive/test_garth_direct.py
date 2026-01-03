#!/usr/bin/env python3
"""
Test using garth's direct methods instead of raw API calls.
"""
import sys
import os
from datetime import datetime, timedelta
import json

sys.path.insert(0, '/Users/boetthw3/Documents/99_Other/TrainingPlan/backend')

# Setup SSL first
try:
    import truststore
    truststore.inject_into_ssl()
    print("✓ Truststore injected into SSL")
except ImportError:
    print("⚠ Truststore not available")

import garth

GARMIN_EMAIL = os.getenv('GARMIN_EMAIL', 'th.boettger@web.de')
GARMIN_PASSWORD = os.getenv('GARMIN_PASSWORD', '2025Dpige.2025')


def main():
    """Test with direct garth methods."""
    print("=" * 80)
    print("Garth Direct Methods Test")
    print("=" * 80)
    print()
    
    # Login
    print("1. Logging in...")
    garth.login(GARMIN_EMAIL, GARMIN_PASSWORD)
    print("✓ Login successful")
    print()
    
    # Check what methods are available
    print("2. Available garth methods:")
    methods = [m for m in dir(garth) if not m.startswith('_') and callable(getattr(garth, m))]
    for method in methods:
        print(f"   - {method}")
    print()
    
    # Try different approaches
    print("3. Trying to fetch activities with different methods:")
    print("-" * 80)
    
    # Method 1: Direct connectapi call with minimal params
    print("\n  A. Using connectapi with minimal params...")
    try:
        response = garth.connectapi("/activitylist-service/activities")
        print(f"     Type: {type(response)}")
        print(f"     Length: {len(response) if isinstance(response, list) else 'N/A'}")
        if response and isinstance(response, list) and len(response) > 0:
            print(f"     First item: {json.dumps(response[0], indent=6, default=str)[:500]}")
    except Exception as e:
        print(f"     Error: {e}")
    
    # Method 2: Try with different parameters
    print("\n  B. Using search endpoint with all null dates...")
    try:
        response = garth.connectapi(
            "/activitylist-service/activities/search/activities",
            params={"limit": 100}
        )
        print(f"     Type: {type(response)}")
        print(f"     Length: {len(response) if isinstance(response, list) else 'N/A'}")
        if response and isinstance(response, list) and len(response) > 0:
            print(f"     First item: {json.dumps(response[0], indent=6, default=str)[:500]}")
    except Exception as e:
        print(f"     Error: {e}")
    
    # Method 3: Check the user's display name
    print("\n  C. Getting user display name...")
    try:
        username = garth.client.username
        print(f"     Username: {username}")
        
        # Try to get activities by username
        response = garth.connectapi(f"/activitylist-service/activities/{username}")
        print(f"     Type: {type(response)}")
        print(f"     Length: {len(response) if isinstance(response, list) else 'N/A'}")
        if response and isinstance(response, list) and len(response) > 0:
            print(f"     First item: {json.dumps(response[0], indent=6, default=str)[:500]}")
    except Exception as e:
        print(f"     Error: {e}")
    
    # Method 4: Try the profile to see if we get any user info
    print("\n  D. Getting user profile...")
    try:
        profile = garth.connectapi("/userprofile-service/userprofile")
        print(f"     Profile: {json.dumps(profile, indent=6, default=str)[:500]}")
    except Exception as e:
        print(f"     Error: {e}")
    
    # Method 5: Try daily summary
    print("\n  E. Getting daily summary...")
    try:
        today = datetime.utcnow().strftime("%Y-%m-%d")
        summary = garth.connectapi(f"/usersummary-service/usersummary/daily/{garth.client.username}", 
                                   params={"calendarDate": today})
        print(f"     Summary: {json.dumps(summary, indent=6, default=str)[:500]}")
    except Exception as e:
        print(f"     Error: {e}")
    
    print()
    print("=" * 80)
    print()
    print("Conclusion:")
    print("-" * 80)
    print("If all methods return empty results, possible issues:")
    print("  1. Privacy settings might need time to propagate (wait 5-10 minutes)")
    print("  2. Account might need to be accessed via Garmin Connect app once")
    print("  3. There might be a different Garmin account with the activities")
    print("  4. Activities might be in a different data store (Garmin Coach, etc.)")
    print()
    print("=" * 80)


if __name__ == "__main__":
    main()
