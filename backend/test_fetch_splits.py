#!/usr/bin/env python3
"""
Fetch detailed split/lap data from Garmin for Dec 6 activity
"""
import asyncio
import sys
import json
import sqlite3
sys.path.insert(0, '/Users/boetthw3/Documents/99_Other/TrainingPlan/backend')

from src.services.garmin_service import garmin_service

async def fetch_splits():
    # Get user tokens from database
    conn = sqlite3.connect('trainingplan.db')
    cursor = conn.cursor()
    
    cursor.execute("SELECT garmin_oauth1_token, garmin_oauth2_token FROM users WHERE email = 'tboettger@gmail.com'")
    oauth1, oauth2 = cursor.fetchone()
    
    cursor.execute("SELECT garmin_activity_id, activity_name, start_time_local FROM garmin_activities WHERE user_id = 1 AND start_time_local LIKE '2025-12-06%'")
    activity_id, name, date = cursor.fetchone()
    
    conn.close()
    
    print(f"\n{'='*100}")
    print(f"ACTIVITY: {name}")
    print(f"Date: {date}")
    print(f"Garmin ID: {activity_id}")
    print(f"{'='*100}\n")
    
    # Get splits data
    print("Fetching splits data from Garmin...")
    api = await garmin_service.resume_session(oauth1, oauth2)
    
    try:
        splits = api.get_activity_splits(activity_id)
        print(f"\n✓ GOT SPLITS DATA: {type(splits)}\n")
        
        if isinstance(splits, list):
            print(f"Number of splits: {len(splits)}\n")
            print(f"{'#':<4} {'Duration':<10} {'Distance':<10} {'Avg Pace':<12} {'Avg HR':<8} {'Max HR':<8}")
            print(f"{'-'*70}")
            
            for i, split in enumerate(splits, 1):
                duration = split.get('duration', 0) / 60  # Convert to minutes
                distance = split.get('distance', 0) / 1000  # Convert to km
                avg_speed = split.get('averageSpeed', 0)
                
                # Calculate pace from speed
                if avg_speed > 0:
                    pace_sec_per_km = 1000 / avg_speed
                    pace_min = int(pace_sec_per_km / 60)
                    pace_sec = int(pace_sec_per_km % 60)
                    pace_str = f"{pace_min}:{pace_sec:02d}/km"
                else:
                    pace_str = "N/A"
                
                avg_hr = split.get('averageHR', 0)
                max_hr = split.get('maxHR', 0)
                
                print(f"{i:<4} {duration:<10.2f} {distance:<10.2f} {pace_str:<12} {avg_hr:<8} {max_hr:<8}")
        
        else:
            print("Splits data structure:")
            print(json.dumps(splits, indent=2, default=str)[:1000])
    
    except Exception as e:
        print(f"Error fetching splits: {e}")
    
    # Try to get detailed HR data
    print(f"\n{'='*100}")
    print("Fetching HR time-zone data...")
    try:
        hr_data = api.get_activity_hr_in_timezones(activity_id)
        print(f"\n✓ GOT HR DATA: {type(hr_data)}")
        if hr_data:
            print(json.dumps(hr_data, indent=2, default=str)[:500])
    except Exception as e:
        print(f"Error fetching HR data: {e}")

if __name__ == '__main__':
    asyncio.run(fetch_splits())
