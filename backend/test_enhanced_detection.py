#!/usr/bin/env python3
"""
Test enhanced key session detection with sub-activity analysis
"""
import sqlite3
from datetime import datetime, timedelta

conn = sqlite3.connect('trainingplan.db')
cursor = conn.cursor()

# Get running activities from last 6 months
six_months_ago = (datetime.now() - timedelta(days=180)).strftime('%Y-%m-%d')
query = """
SELECT 
    activity_name,
    start_time_local,
    duration_seconds,
    distance_meters,
    average_hr
FROM garmin_activities 
WHERE user_id = 1 
    AND activity_type LIKE '%running%'
    AND start_time_local >= ?
    AND duration_seconds >= 1200
    AND distance_meters > 0
ORDER BY start_time_local
"""

cursor.execute(query, (six_months_ago,))
activities = cursor.fetchall()

print(f"\n{'='*110}")
print(f"ENHANCED KEY SESSION DETECTION - with Sub-Activity Analysis")
print(f"{'='*110}\n")

# First pass: Top 5% by pace per month
from collections import defaultdict
monthly_activities = defaultdict(list)

for row in activities:
    name, date_str, duration_sec, distance_m, avg_hr = row
    duration_min = duration_sec / 60
    
    if duration_min < 20:
        continue
    
    avg_pace_min_per_km = (duration_sec / 60) / (distance_m / 1000)
    month_key = date_str[:7]
    
    monthly_activities[month_key].append({
        'date': date_str[:10],
        'name': name,
        'duration_min': duration_min,
        'avg_pace': avg_pace_min_per_km,
        'avg_hr': avg_hr if avg_hr else 0
    })

top_5_sessions = []
for month, month_acts in sorted(monthly_activities.items()):
    month_acts.sort(key=lambda x: x['avg_pace'])
    top_n = max(1, int(len(month_acts) * 0.05))
    top_5_sessions.extend(month_acts[:top_n])

print(f"✓ TOP 5% PACE SESSIONS: {len(top_5_sessions)} found\n")
for s in top_5_sessions:
    pace_str = f"{int(s['avg_pace'])}:{int((s['avg_pace'] % 1) * 60):02d}"
    print(f"  {s['date']} - {s['duration_min']:5.1f}min @ {pace_str}/km - {s['name'][:40]}")

# Second pass: Analyze for sub-activities (tempo sections in long runs)
print(f"\n{'='*110}")
print(f"✓ SUB-ACTIVITY DETECTION: Sustained tempo sections in longer runs\n")

sub_activities = []
for row in activities:
    name, date_str, duration_sec, distance_m, avg_hr = row
    duration_min = duration_sec / 60
    
    # Skip if already a top 5% session
    if any(s['date'] == date_str[:10] for s in top_5_sessions):
        continue
    
    # Look for long runs (60+ min) with decent pace
    if duration_min >= 60:
        avg_pace_min_per_km = (duration_sec / 60) / (distance_m / 1000)
        
        # If overall pace is reasonable (<5:45), likely has tempo section
        if avg_pace_min_per_km < 5.75 and avg_hr and avg_hr > 140:
            # Estimate tempo section: 35% of duration at 5% faster pace
            tempo_duration = duration_min * 0.35
            if tempo_duration >= 20:
                tempo_pace = avg_pace_min_per_km * 0.95
                
                sub_activities.append({
                    'date': date_str[:10],
                    'name': name,
                    'total_duration': duration_min,
                    'tempo_duration': tempo_duration,
                    'tempo_pace': tempo_pace,
                    'avg_hr': avg_hr
                })

print(f"Found {len(sub_activities)} activities with estimated tempo sections:\n")
for s in sub_activities:
    pace_str = f"{int(s['tempo_pace'])}:{int((s['tempo_pace'] % 1) * 60):02d}"
    print(f"  {s['date']} - {s['total_duration']:5.1f}min run with ~{s['tempo_duration']:.0f}min tempo @ {pace_str}/km - {s['name'][:40]}")

# Third pass: Interval detection (placeholder - needs FIT file parsing)
print(f"\n{'='*110}")
print(f"✓ INTERVAL SESSION DETECTION: (Requires FIT file time-series data)\n")
print(f"  TODO: Parse FIT files to detect repeated high-intensity efforts")
print(f"  - Look for 3+ intervals of 2-5 min at >85% max HR")
print(f"  - Detect VO2max sessions, threshold repeats, fartleks")
print(f"  - See: src/utils/interval_detector.py for implementation")

print(f"\n{'='*110}")
print(f"TOTAL KEY SESSIONS: {len(top_5_sessions) + len(sub_activities)}")
print(f"  - Top 5% pace: {len(top_5_sessions)}")
print(f"  - Tempo sub-sections: {len(sub_activities)}")
print(f"  - Intervals: 0 (TODO)")
print(f"{'='*110}\n")

conn.close()
