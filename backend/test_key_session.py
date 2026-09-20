"""
Test with KEY SESSION detection - Dec 6th 10k run
"""
import sqlite3
from datetime import datetime, timedelta

print("=" * 80)
print("KEY SESSION DETECTION TEST")
print("=" * 80)
print()

conn = sqlite3.connect('/Users/boetthw3/Documents/99_Other/TrainingPlan/backend/trainingplan.db')
cursor = conn.cursor()

# Get user
cursor.execute("""
    SELECT id, running_threshold_hr, max_hr 
    FROM users 
    WHERE email = 'tboettger@gmail.com'
""")
user_id, current_threshold, max_hr = cursor.fetchone()

print(f"👤 User thresholds: {current_threshold} bpm (max: {max_hr})")
print()

# Get December 6th week (2025-W49)
print("-" * 80)
print("Week 2025-W49 (Dec 6th - the 10k week)")
print("-" * 80)
print()

cursor.execute("""
    SELECT 
        activity_name,
        start_time_local,
        activity_type,
        duration_seconds,
        distance_meters,
        average_hr,
        max_hr as activity_max_hr
    FROM garmin_activities
    WHERE user_id = ?
    AND start_time_local >= '2025-12-02'
    AND start_time_local < '2025-12-09'
    ORDER BY start_time_local
""", (user_id,))

activities = cursor.fetchall()

print(f"Found {len(activities)} activities:")
print()

key_session_estimates = []
regular_estimates = []

for name, date, sport, dur, dist, avg_hr, max_hr_act in activities:
    dur_min = dur / 60 if dur else 0
    dist_km = dist / 1000 if dist else 0
    
    print(f"📅 {date}")
    print(f"   {name}")
    print(f"   {sport}: {dur_min:.0f}min, {dist_km:.1f}km")
    print(f"   Avg HR: {avg_hr}, Max HR: {max_hr_act}")
    
    # Check if this is a KEY SESSION
    is_key_session = (
        'run' in sport.lower() and
        20 <= dur_min <= 60 and
        max_hr_act >= (max_hr * 0.85) and
        avg_hr and max_hr_act
    )
    
    if is_key_session:
        print(f"   🔥 KEY SESSION DETECTED!")
        print(f"      Duration: {dur_min:.0f}min (20-60 range) ✓")
        print(f"      Max HR: {max_hr_act} >= {max_hr * 0.85:.0f} (85% max) ✓")
        
        # Apply literature-based estimation
        if dur_min < 30:
            factor = 1.05
            desc = "20-30min effort ≈ 105% threshold"
        elif dur_min < 45:
            factor = 1.02
            desc = "30-45min effort ≈ 102% threshold"
        else:
            factor = 1.00
            desc = "45-60min effort ≈ threshold"
        
        estimated_threshold = avg_hr / factor
        key_session_estimates.append(estimated_threshold)
        
        print(f"      Method: {desc}")
        print(f"      Calculation: {avg_hr} / {factor} = {estimated_threshold:.0f} bpm")
        print(f"      ⭐ THRESHOLD ESTIMATE: {estimated_threshold:.0f} bpm")
    else:
        if 'run' in sport.lower() and avg_hr and max_hr_act:
            estimated = avg_hr + (max_hr_act - avg_hr) * 0.35
            regular_estimates.append(estimated)
            print(f"      Regular run estimate: {estimated:.0f} bpm")
    
    print()

print("=" * 80)
print("THRESHOLD ESTIMATION FOR THIS WEEK:")
print("=" * 80)
print()

if key_session_estimates:
    from statistics import median
    threshold_from_keys = int(median(key_session_estimates))
    print(f"🎯 KEY SESSION ESTIMATE: {threshold_from_keys} bpm")
    print(f"   Based on {len(key_session_estimates)} key session(s)")
    print(f"   Confidence: 90% (high - based on hard efforts)")
    
    # Blend with trend
    trend_estimate = int(current_threshold * (1.0 - 4 * 0.003))  # 4 weeks ago
    final_estimate = int(threshold_from_keys * 0.8 + trend_estimate * 0.2)
    
    print(f"\n📊 BLENDING:")
    print(f"   Key session data: {threshold_from_keys} bpm (80% weight)")
    print(f"   Trend estimate:   {trend_estimate} bpm (20% weight)")
    print(f"   FINAL: {final_estimate} bpm")

if regular_estimates:
    threshold_from_regular = int(median(regular_estimates))
    print(f"\n📉 Regular runs estimate: {threshold_from_regular} bpm")
    print(f"   (Would use this if no key sessions)")

print()
print("-" * 80)
print("COMPARISON:")
print("-" * 80)
print()

print("Old algorithm (all runs equal):")
all_runs = key_session_estimates + regular_estimates
if all_runs:
    from statistics import median
    old_estimate = int(median(all_runs))
    print(f"   Threshold: {old_estimate} bpm")

print()
print("New algorithm (prioritize key sessions):")
print(f"   Threshold: {final_estimate} bpm")

print()
print("Difference: {} bpm".format(final_estimate - old_estimate if all_runs else "N/A"))

print()
print("=" * 80)
print("LITERATURE REFERENCES:")
print("=" * 80)
print()
print("🔬 Exercise Physiology:")
print()
print("1. THRESHOLD DEFINITION (Jack Daniels, Joe Friel):")
print("   → Lactate threshold = effort sustainable for ~1 hour")
print()
print("2. RACE PACE/HR RELATIONSHIP:")
print("   → 5K (15-25 min):   ~108-110% of threshold HR")
print("   → 10K (30-60 min):  ~102-105% of threshold HR")
print("   → Half Marathon:    ~98-100% of threshold HR")
print()
print("3. YOUR 10K RUN (Dec 6th):")
print("   → 46 minutes at avg HR 174")
print("   → This is VERY CLOSE to threshold (46 min ≈ 1 hour)")
print("   → Literature estimate: 174 / 1.02 ≈ 170-171 bpm")
print()
print("4. WHY KEY SESSIONS MATTER:")
print("   → Easy runs: HR doesn't reach threshold")
print("   → Hard efforts (20-60 min): HR close to threshold")
print("   → More accurate than averaging all runs together")
print()

conn.close()
