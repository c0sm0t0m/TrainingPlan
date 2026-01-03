#!/usr/bin/env python3
"""
Test different Garmin API endpoints to find activities.
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


async def test_endpoints():
    """Test different Garmin API endpoints."""
    print("=" * 80)
    print("Garmin API Endpoints Test")
    print("=" * 80)
    print()
    
    # Authenticate
    print("1. Authenticating...")
    result = await garmin_service.authenticate(GARMIN_EMAIL, GARMIN_PASSWORD)
    print("✓ Authentication successful")
    print()
    
    # Test different endpoints
    endpoints = [
        # Activity list endpoints
        ("/activitylist-service/activities/search/activities", {"start": 0, "limit": 20}),
        ("/activitylist-service/activities", {"start": 0, "limit": 20}),
        
        # User profile
        ("/userprofile-service/userprofile", {}),
        
        # Activity feed
        ("/activitylist-service/activities/search/activities", {
            "start": 0,
            "limit": 20
        }),
        
        # Wellness data
        ("/wellness-service/wellness/dailySummaryChart", {
            "date": datetime.utcnow().strftime("%Y-%m-%d")
        }),
        
        # Stats
        ("/userstats-service/statistics", {}),
    ]
    
    for endpoint, params in endpoints:
        print(f"Testing endpoint: {endpoint}")
        print(f"  Params: {params}")
        print("-" * 80)
        
        try:
            response = garth.client.connectapi(endpoint, params=params)
            
            print(f"  ✓ Success!")
            print(f"  Response type: {type(response)}")
            
            if isinstance(response, dict):
                print(f"  Keys: {list(response.keys())[:10]}")
                print(f"  Sample: {json.dumps(response, indent=4, default=str)[:500]}...")
            elif isinstance(response, list):
                print(f"  Length: {len(response)}")
                if len(response) > 0:
                    print(f"  First item: {json.dumps(response[0], indent=4, default=str)[:300]}...")
            else:
                print(f"  Content: {str(response)[:500]}")
            
        except Exception as e:
            print(f"  ✗ Error: {e}")
        
        print()
    
    # Try direct Garth stats method
    print("Testing garth.stats() method")
    print("-" * 80)
    try:
        # Get today's date
        today = datetime.utcnow().date()
        stats = garth.stats(today)
        print(f"  ✓ Success!")
        print(f"  Stats: {json.dumps(stats, indent=4, default=str)}")
    except Exception as e:
        print(f"  ✗ Error: {e}")
    
    print()
    print("=" * 80)


if __name__ == "__main__":
    asyncio.run(test_endpoints())
