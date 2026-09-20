"""
Simple sync test to verify database access
"""
import sys
sys.path.insert(0, '/Users/boetthw3/Documents/99_Other/TrainingPlan/backend')

import sqlite3
from datetime import datetime, timedelta

# Connect to database
conn = sqlite3.connect('/Users/boetthw3/Documents/99_Other/TrainingPlan/backend/trainingplan.db')
cursor = conn.cursor()

print("=" * 80)
print("DATABASE CONNECTION TEST")
print("=" * 80)
print()

# Get user
cursor.execute("SELECT email, running_threshold_hr, ftp, max_hr FROM users WHERE email = 'tboettger@gmail.com'")
user = cursor.fetchone()

if user:
    print(f"✅ User found: {user[0]}")
    print(f"   Running HR: {user[1]}")
    print(f"   FTP: {user[2]}")
    print(f"   Max HR: {user[3]}")
else:
    print("❌ User not found")

print()

# Get activity count
cursor.execute("SELECT COUNT(*) FROM garmin_activities WHERE user_id = 1")
count = cursor.fetchone()[0]
print(f"📁 Total activities: {count}")

# Get activities from last 4 weeks
four_weeks_ago = (datetime.now() - timedelta(weeks=4)).strftime('%Y-%m-%d')
cursor.execute("""
    SELECT 
        strftime('%Y-%W', start_time_local) as week,
        activity_type,
        duration_seconds,
        average_hr
    FROM garmin_activities 
    WHERE user_id = 1 
    AND start_time_local >= ?
    ORDER BY start_time_local DESC
    LIMIT 20
""", (four_weeks_ago,))

activities = cursor.fetchall()
print(f"🏃 Recent activities (last 4 weeks): {len(activities)}")
print()

if activities:
    print("Sample activities:")
    for week, sport, duration, hr in activities[:10]:
        dur_min = duration / 60 if duration else 0
        print(f"   {week}: {sport} - {dur_min:.0f}min, HR={hr}")

print()
print("✅ Database access working!")
print()

conn.close()
