#!/usr/bin/env python3
"""
Quick script to display current key sessions detection
"""
import sys
import sqlite3
from datetime import datetime, timedelta

# Connect to database
conn = sqlite3.connect('trainingplan.db')
cursor = conn.cursor()

# User threshold
THRESHOLD_HR = 165

# Get running activities from last 6 months
six_months_ago = (datetime.now() - timedelta(days=180)).strftime('%Y-%m-%d')
query = """
SELECT 
    activity_name,
    start_time_local,
    duration_seconds,
    distance_meters,
    average_hr,
    activity_type
FROM garmin_activities 
WHERE user_id = 1 
    AND activity_type LIKE '%running%'
    AND start_time_local >= ?
    AND duration_seconds >= 1200
    AND average_hr IS NOT NULL
    AND distance_meters > 0
ORDER BY start_time_local
"""

cursor.execute(query, (six_months_ago,))
activities = cursor.fetchall()

print(f"\n{'='*100}")
print(f"CURRENT KEY SESSION DETECTION (HR-based criteria)")
print(f"Threshold HR: {THRESHOLD_HR} bpm")
print(f"{'='*100}\n")

key_sessions = []

for row in activities:
    name, date_str, duration_sec, distance_m, avg_hr, activity_type = row
    
    duration_min = duration_sec / 60
    avg_pace_sec_per_km = duration_sec / (distance_m / 1000)
    avg_pace_min_per_km = avg_pace_sec_per_km / 60
    
    # Current criteria
    is_threshold_effort = (20 <= duration_min <= 60) and (avg_hr >= THRESHOLD_HR * 0.97)
    is_long_tempo = (60 < duration_min <= 75) and (avg_hr >= THRESHOLD_HR * 0.95)
    is_very_long_tempo = (duration_min > 75) and (avg_hr >= THRESHOLD_HR * 0.90)
    
    if is_threshold_effort or is_long_tempo or is_very_long_tempo:
        # Calculate threshold estimate
        if duration_min < 30:
            threshold_hr = int(avg_hr / 1.05)
        elif duration_min < 45:
            threshold_hr = int(avg_hr / 1.02)
        else:
            threshold_hr = int(avg_hr)
        
        # Calculate IF and threshold pace
        intensity_factor = round(avg_hr / threshold_hr, 3)
        threshold_pace = round(avg_pace_min_per_km / intensity_factor, 2)
        
        key_sessions.append({
            'date': date_str[:10],
            'name': name,
            'duration_min': round(duration_min, 1),
            'avg_hr': avg_hr,
            'avg_pace': round(avg_pace_min_per_km, 2),
            'if': intensity_factor,
            'threshold_hr': threshold_hr,
            'threshold_pace': threshold_pace,
            'criteria': 'Threshold' if is_threshold_effort else ('Long Tempo' if is_long_tempo else 'Very Long Tempo')
        })

print(f"Found {len(key_sessions)} key sessions:\n")
print(f"{'Date':<12} {'Duration':<10} {'Avg HR':<8} {'Avg Pace':<10} {'IF':<6} {'Thresh HR':<10} {'Thresh Pace':<12} {'Criteria':<15} {'Name':<30}")
print(f"{'-'*130}")

for session in key_sessions:
    pace_str = f"{int(session['avg_pace'])}:{int((session['avg_pace'] % 1) * 60):02d}"
    thresh_pace_str = f"{int(session['threshold_pace'])}:{int((session['threshold_pace'] % 1) * 60):02d}"
    
    print(f"{session['date']:<12} {session['duration_min']:<10.1f} {session['avg_hr']:<8} {pace_str:<10} {session['if']:<6.3f} {session['threshold_hr']:<10} {thresh_pace_str:<12} {session['criteria']:<15} {session['name'][:30]:<30}")

print(f"\n{'='*100}\n")

# Now show top 5% by pace for comparison
print(f"NEW APPROACH: TOP 5% FASTEST SESSIONS BY PACE (per month)")
print(f"{'='*100}\n")

# Group activities by month
from collections import defaultdict
monthly_activities = defaultdict(list)

cursor.execute(query, (six_months_ago,))
all_activities = cursor.fetchall()

for row in all_activities:
    name, date_str, duration_sec, distance_m, avg_hr, activity_type = row
    
    duration_min = duration_sec / 60
    if duration_min < 20:  # Skip very short runs
        continue
    
    avg_pace_sec_per_km = duration_sec / (distance_m / 1000)
    avg_pace_min_per_km = avg_pace_sec_per_km / 60
    
    month_key = date_str[:7]  # YYYY-MM
    
    monthly_activities[month_key].append({
        'date': date_str[:10],
        'name': name,
        'duration_min': round(duration_min, 1),
        'distance_km': round(distance_m / 1000, 2),
        'avg_hr': avg_hr if avg_hr else 0,
        'avg_pace': round(avg_pace_min_per_km, 2)
    })

# For each month, find top 5%
top_5_percent_sessions = []

for month, activities in sorted(monthly_activities.items()):
    # Sort by pace (lower is faster)
    activities_sorted = sorted(activities, key=lambda x: x['avg_pace'])
    
    # Get top 5% (at least 1 session)
    top_n = max(1, int(len(activities_sorted) * 0.05))
    top_sessions = activities_sorted[:top_n]
    
    print(f"\n{month}: {len(activities)} activities, selecting top {top_n} (5%)")
    print(f"  {'Date':<12} {'Duration':<10} {'Distance':<10} {'Avg HR':<8} {'Avg Pace':<10} {'Name':<30}")
    print(f"  {'-'*100}")
    
    for session in top_sessions:
        pace_str = f"{int(session['avg_pace'])}:{int((session['avg_pace'] % 1) * 60):02d}"
        print(f"  {session['date']:<12} {session['duration_min']:<10.1f} {session['distance_km']:<10.2f} {session['avg_hr']:<8} {pace_str:<10} {session['name'][:30]:<30}")
        top_5_percent_sessions.append(session)

print(f"\n{'='*100}")
print(f"Total top 5% sessions: {len(top_5_percent_sessions)}")
print(f"{'='*100}\n")

conn.close()
