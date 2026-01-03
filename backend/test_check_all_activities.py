"""
Check all activities available from Garmin and compare with database
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from garminconnect import Garmin
import garth
import sqlite3
import json

def check_activities():
    # Load tokens from database
    conn = sqlite3.connect('trainingplan.db')
    cursor = conn.cursor()
    cursor.execute("SELECT garmin_oauth1_token, garmin_oauth2_token FROM users WHERE email = 'tboettger@gmail.com'")
    result = cursor.fetchone()
    
    if not result or not result[0]:
        print("No Garmin tokens found for tboettger@gmail.com")
        return
    
    oauth1_token_str = result[0]
    oauth2_token_str = result[1]
    
    print("Fetching activities from Garmin Connect...")
    
    # Parse tokens
    oauth1_token = json.loads(oauth1_token_str) if isinstance(oauth1_token_str, str) else oauth1_token_str
    oauth2_token = json.loads(oauth2_token_str) if isinstance(oauth2_token_str, str) else oauth2_token_str
    
    # Set tokens directly in garth
    garth.client.oauth1_token = garth.OAuth1Token(**oauth1_token)
    garth.client.oauth2_token = garth.OAuth2Token(**oauth2_token)
    
    # Create Garmin client
    client = Garmin()
    
    # Fetch activities
    print("\n=== Fetching last 50 activities ===")
    activities = client.get_activities(0, 50)
    
    print(f"\nTotal activities fetched: {len(activities)}")
    
    if activities:
        print("\nMost recent 10 activities from Garmin:")
        for i, activity in enumerate(activities[:10], 1):
            start_time = activity.get('startTimeLocal', 'Unknown')
            name = activity.get('activityName', 'Unnamed')
            activity_type = activity.get('activityType', {}).get('typeKey', 'unknown')
            activity_id = activity.get('activityId', 'unknown')
            print(f"{i}. {name} ({activity_type}) - {start_time} [ID: {activity_id}]")
        
        # Check database
        cursor.execute("SELECT MAX(start_time_local) FROM garmin_activities WHERE user_id = 1")
        latest_in_db = cursor.fetchone()[0]
        print(f"\n=== Database Check ===")
        print(f"Latest activity in database: {latest_in_db}")
        print(f"Latest activity from Garmin: {activities[0].get('startTimeLocal', 'Unknown')}")
        
        # Check for missing activities
        garmin_ids = {str(a.get('activityId')) for a in activities}
        cursor.execute("SELECT garmin_activity_id FROM garmin_activities WHERE user_id = 1")
        db_ids = {row[0] for row in cursor.fetchall()}
        
        missing = garmin_ids - db_ids
        if missing:
            print(f"\n⚠️  Found {len(missing)} activities in Garmin but not in database!")
            print("Missing activities:")
            for activity in activities:
                if str(activity.get('activityId')) in missing:
                    print(f"  - {activity.get('activityName')} ({activity.get('activityType', {}).get('typeKey')}) - {activity.get('startTimeLocal')}")
        else:
            print("\n✓ All Garmin activities are in the database")
    
    conn.close()

if __name__ == "__main__":
    check_activities()
