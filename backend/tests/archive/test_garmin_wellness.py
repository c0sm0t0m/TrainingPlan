#!/usr/bin/env python3
"""
Check if we can access ANY data from the account (wellness, stats, etc.)
"""
import sys
import os
from datetime import datetime, date, timedelta
import json

sys.path.insert(0, '/Users/boetthw3/Documents/99_Other/TrainingPlan/backend')

try:
    import truststore
    truststore.inject_into_ssl()
    print("✓ Truststore injected into SSL")
except ImportError:
    pass

import garth

GARMIN_EMAIL = os.getenv('GARMIN_EMAIL', 'th.boettger@web.de')
GARMIN_PASSWORD = os.getenv('GARMIN_PASSWORD', '2025Dpige.2025')


def main():
    """Check all available data types."""
    print("=" * 80)
    print("Garmin Account Data Availability Check")
    print("=" * 80)
    print()
    
    # Login
    print("1. Logging in...")
    garth.login(GARMIN_EMAIL, GARMIN_PASSWORD)
    print("✓ Login successful")
    print()
    
    # Get date range
    today = date.today()
    week_ago = today - timedelta(days=7)
    
    # Test all wellness data types using garth's high-level methods
    print("2. Testing wellness data access:")
    print("-" * 80)
    
    # Steps
    print("\n  A. Daily Steps...")
    try:
        steps = garth.DailySteps(today)
        print(f"     ✓ Success: {json.dumps(steps, indent=6, default=str)[:300]}")
    except Exception as e:
        print(f"     ✗ Error: {e}")
    
    # Sleep
    print("\n  B. Daily Sleep...")
    try:
        sleep = garth.DailySleep(today)
        print(f"     ✓ Success: {json.dumps(sleep, indent=6, default=str)[:300]}")
    except Exception as e:
        print(f"     ✗ Error: {e}")
    
    # Stress
    print("\n  C. Daily Stress...")
    try:
        stress = garth.DailyStress(today)
        print(f"     ✓ Success: {json.dumps(stress, indent=6, default=str)[:300]}")
    except Exception as e:
        print(f"     ✗ Error: {e}")
    
    # HRV
    print("\n  D. Daily HRV...")
    try:
        hrv = garth.DailyHRV(today)
        print(f"     ✓ Success: {json.dumps(hrv, indent=6, default=str)[:300]}")
    except Exception as e:
        print(f"     ✗ Error: {e}")
    
    # User Profile
    print("\n  E. User Profile...")
    try:
        profile = garth.UserProfile()
        print(f"     ✓ Success: {json.dumps(profile, indent=6, default=str)[:500]}")
    except Exception as e:
        print(f"     ✗ Error: {e}")
    
    # User Settings
    print("\n  F. User Settings...")
    try:
        settings = garth.UserSettings()
        print(f"     ✓ Success: {json.dumps(settings, indent=6, default=str)[:500]}")
    except Exception as e:
        print(f"     ✗ Error: {e}")
    
    print()
    print("=" * 80)
    print()
    print("Diagnosis:")
    print("-" * 80)
    print()
    print("If ALL data types return empty/error:")
    print("  → This suggests the account has NEVER been used with a Garmin device")
    print("  → Or this is a brand new account with no data")
    print()
    print("If some data works but activities don't:")
    print("  → The account is working, but has no recorded activities")
    print("  → Activities need to be recorded via:")
    print("     - Garmin device (watch, bike computer, etc.)")
    print("     - Garmin Connect mobile app (manual activity)")
    print("     - File upload on connect.garmin.com")
    print()
    print("Next steps:")
    print("  1. Record a test activity using Garmin Connect mobile app")
    print("  2. Or manually add an activity on connect.garmin.com")
    print("  3. Wait 5-10 minutes for sync")
    print("  4. Run this test again")
    print()
    print("=" * 80)


if __name__ == "__main__":
    main()
