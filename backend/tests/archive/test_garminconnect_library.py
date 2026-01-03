#!/usr/bin/env python3
"""
Test using the garminconnect library (same as external demo.py).
This is a different library than garth - it's a wrapper that may work better.
"""
import sys
import os
from datetime import datetime, timedelta

# Setup SSL first
try:
    import truststore
    truststore.inject_into_ssl()
    print("✓ Truststore injected into SSL")
except ImportError:
    print("⚠ Truststore not available")

from garminconnect import (
    Garmin,
    GarminConnectAuthenticationError,
    GarminConnectConnectionError,
    GarminConnectTooManyRequestsError,
)

GARMIN_EMAIL = os.getenv('GARMIN_EMAIL', 'th.boettger@web.de')
GARMIN_PASSWORD = os.getenv('GARMIN_PASSWORD', '2025Dpige.2025')


def main():
    """Test with garminconnect library."""
    print("=" * 80)
    print("Garminconnect Library Test")
    print("=" * 80)
    print()
    
    # Login
    print("1. Logging in...")
    try:
        api = Garmin(email=GARMIN_EMAIL, password=GARMIN_PASSWORD)
        api.login()
        print("✓ Login successful")
        print()
    except GarminConnectAuthenticationError as e:
        print(f"✗ Authentication failed: {e}")
        return
    except GarminConnectConnectionError as e:
        print(f"✗ Connection failed: {e}")
        return
    except Exception as e:
        print(f"✗ Error: {e}")
        return
    
    # Get user profile
    print("2. Getting user profile...")
    try:
        profile = api.get_full_name()
        print(f"   Name: {profile}")
    except Exception as e:
        print(f"   Error: {e}")
    print()
    
    # Get activities
    print("3. Getting recent activities...")
    try:
        activities = api.get_activities(0, 20)  # start=0, limit=20
        print(f"   Found: {len(activities) if activities else 0} activities")
        
        if activities and len(activities) > 0:
            print(f"\n   ✓ SUCCESS - Found {len(activities)} activities!")
            print(f"\n   First activity:")
            import json
            print(json.dumps(activities[0], indent=6, default=str)[:1000])
        else:
            print(f"   ⚠ No activities found")
    except Exception as e:
        print(f"   Error: {e}")
        import traceback
        print(traceback.format_exc())
    print()
    
    # Try activities by date
    print("4. Getting activities by date (last 30 days)...")
    try:
        start_date = datetime.now() - timedelta(days=30)
        end_date = datetime.now()
        activities = api.get_activities_by_date(
            start_date.strftime("%Y-%m-%d"),
            end_date.strftime("%Y-%m-%d")
        )
        print(f"   Found: {len(activities) if activities else 0} activities")
        
        if activities and len(activities) > 0:
            print(f"\n   ✓ SUCCESS - Found {len(activities)} activities!")
            import json
            print(json.dumps(activities[0], indent=6, default=str)[:1000])
    except Exception as e:
        print(f"   Error: {e}")
    print()
    
    # Try to get today's summary
    print("5. Getting today's summary...")
    try:
        today = datetime.now().strftime("%Y-%m-%d")
        summary = api.get_user_summary(today)
        if summary:
            print(f"   Steps: {summary.get('totalSteps', 'N/A')}")
            print(f"   Calories: {summary.get('totalKilocalories', 'N/A')}")
            print(f"   Distance: {summary.get('totalDistanceMeters', 'N/A')}m")
        else:
            print(f"   No summary data")
    except Exception as e:
        print(f"   Error: {e}")
    print()
    
    print("=" * 80)
    print()
    print("Conclusion:")
    print("-" * 80)
    if activities and len(activities) > 0:
        print("✓ garminconnect library WORKS and found activities!")
        print("  This library provides better access than raw garth.")
        print("  Recommendation: Switch to using garminconnect library")
    else:
        print("⚠ Even with garminconnect library, no activities found.")
        print("  The account genuinely appears to have no activities.")
    print()
    print("=" * 80)


if __name__ == "__main__":
    main()
