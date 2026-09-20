"""
4-Week Historic Threshold Calculator - Simple & Detailed
Shows exactly what happens step by step
"""
import sqlite3
from datetime import datetime, timedelta

print("=" * 80)
print("HISTORIC THRESHOLD CALCULATION - 4 WEEKS")
print("=" * 80)
print()

# Connect to database
conn = sqlite3.connect('/Users/boetthw3/Documents/99_Other/TrainingPlan/backend/trainingplan.db')
cursor = conn.cursor()

# Get user info
cursor.execute("""
    SELECT id, email, running_threshold_hr, cycling_threshold_hr, ftp, max_hr, resting_hr 
    FROM users 
    WHERE email = 'tboettger@gmail.com'
""")
user = cursor.fetchone()
user_id, email, run_hr, cyc_hr, ftp, max_hr, rest_hr = user

print(f"👤 User: {email}")
print(f"   Current Thresholds:")
print(f"   • Running HR: {run_hr} bpm")
print(f"   • Cycling HR: {cyc_hr} bpm")
print(f"   • FTP: {ftp} W")
print(f"   • Max HR: {max_hr} bpm")
print(f"   • Resting HR: {rest_hr} bpm")
print()

# Get today's week
today = datetime.now()
current_year, current_week, _ = today.isocalendar()

print(f"📅 Today: {today.strftime('%Y-%m-%d')} = ISO Week {current_year}-W{current_week:02d}")
print()

# Calculate for each of the last 4 weeks
print("-" * 80)
print("CALCULATING THRESHOLDS FOR EACH WEEK...")
print("-" * 80)
print()

thresholds_to_insert = []

for weeks_ago in range(5):  # 0, 1, 2, 3, 4 (5 weeks total including current)
    target_date = today - timedelta(weeks=weeks_ago)
    year, week, _ = target_date.isocalendar()
    
    print(f"📊 Week {year}-W{week:02d} ({weeks_ago} weeks ago)")
    print(f"   Date: {target_date.strftime('%Y-%m-%d')}")
    
    # Get activities for this week
    week_start = target_date - timedelta(days=target_date.weekday())
    week_end = week_start + timedelta(days=7)
    
    cursor.execute("""
        SELECT 
            activity_type,
            duration_seconds,
            average_hr,
            max_hr as activity_max_hr
        FROM garmin_activities
        WHERE user_id = ?
        AND start_time_local >= ?
        AND start_time_local < ?
        ORDER BY start_time_local DESC
    """, (user_id, week_start.strftime('%Y-%m-%d'), week_end.strftime('%Y-%m-%d')))
    
    activities = cursor.fetchall()
    
    print(f"   Activities this week: {len(activities)}")
    if activities:
        for sport, dur, avg_hr, max_hr_act in activities[:3]:  # Show first 3
            dur_min = dur / 60 if dur else 0
            print(f"      • {sport}: {dur_min:.0f}min, Avg HR={avg_hr}, Max HR={max_hr_act}")
    
    # Calculate thresholds based on logic
    if weeks_ago == 0:
        # Current week - use actual values
        est_run_hr = run_hr
        est_cyc_hr = cyc_hr
        est_ftp = ftp
        method = "current"
        confidence = 1.0
        print(f"   ✅ Using CURRENT thresholds")
        
    elif weeks_ago <= 4:
        # Recent weeks - linear degradation
        degradation = 1.0 - (weeks_ago * 0.005)  # 0.5% per week
        est_run_hr = int(run_hr * degradation)
        est_cyc_hr = int(cyc_hr * degradation)
        est_ftp = int(ftp * degradation)
        method = "linear_degradation"
        confidence = 0.95
        print(f"   📉 LINEAR DEGRADATION: {degradation:.3f}x (0.5% per week)")
        print(f"      Running: {run_hr} → {est_run_hr} bpm")
        print(f"      FTP: {ftp} → {est_ftp} W")
    
    print(f"   Confidence: {confidence:.0%}")
    print(f"   Method: {method}")
    print()
    
    # Store for database insert
    thresholds_to_insert.append((
        user_id, year, week,
        est_run_hr, est_cyc_hr, est_ftp,
        5.0,  # threshold_pace (placeholder)
        120.0,  # swim_threshold_pace (placeholder)
        max_hr, rest_hr,
        method, confidence, len(activities)
    ))

# Insert into database
print("-" * 80)
print("SAVING TO DATABASE...")
print("-" * 80)
print()

for threshold in thresholds_to_insert:
    user_id, year, week, run_hr, cyc_hr, ftp, t_pace, swim_pace, max_hr, rest_hr, method, conf, acts = threshold
    
    # Check if already exists
    cursor.execute("""
        SELECT id FROM weekly_thresholds 
        WHERE user_id = ? AND year = ? AND week = ?
    """, (user_id, year, week))
    
    existing = cursor.fetchone()
    
    if existing:
        # Update
        cursor.execute("""
            UPDATE weekly_thresholds
            SET running_threshold_hr = ?,
                cycling_threshold_hr = ?,
                ftp = ?,
                threshold_pace = ?,
                swim_threshold_pace = ?,
                max_hr = ?,
                resting_hr = ?,
                calculation_method = ?,
                confidence_score = ?,
                activities_used = ?
            WHERE user_id = ? AND year = ? AND week = ?
        """, (run_hr, cyc_hr, ftp, t_pace, swim_pace, max_hr, rest_hr, method, conf, acts,
              user_id, year, week))
        print(f"   ✏️  Updated {year}-W{week:02d}: HR={run_hr}, FTP={ftp}")
    else:
        # Insert
        cursor.execute("""
            INSERT INTO weekly_thresholds 
            (user_id, year, week, running_threshold_hr, cycling_threshold_hr, ftp,
             threshold_pace, swim_threshold_pace, max_hr, resting_hr,
             calculation_method, confidence_score, activities_used)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (user_id, year, week, run_hr, cyc_hr, ftp, t_pace, swim_pace, max_hr, rest_hr,
              method, conf, acts))
        print(f"   ✅ Inserted {year}-W{week:02d}: HR={run_hr}, FTP={ftp}")

conn.commit()
print()
print("✅ Database updated successfully!")
print()

# Read back to verify
print("-" * 80)
print("VERIFICATION - Reading from database:")
print("-" * 80)
print()

cursor.execute("""
    SELECT year, week, running_threshold_hr, ftp, calculation_method, confidence_score, activities_used
    FROM weekly_thresholds
    WHERE user_id = ?
    ORDER BY year DESC, week DESC
    LIMIT 5
""", (user_id,))

results = cursor.fetchall()
for year, week, run_hr, ftp, method, conf, acts in results:
    print(f"   {year}-W{week:02d}: HR={run_hr}bpm, FTP={ftp}W, {method} ({conf:.0%}), {acts} activities")

print()
print("=" * 80)
print("HOW THIS WORKS:")
print("=" * 80)
print()
print("🎯 THRESHOLD CALCULATION STRATEGY:")
print()
print("1. CURRENT WEEK (this week)")
print("   → Uses your ACTUAL current thresholds")
print("   → No estimation needed")
print("   → Confidence: 100%")
print()
print("2. RECENT PAST (1-4 weeks ago)")
print("   → Assumes LINEAR DEGRADATION: 0.5% per week")
print("   → Logic: If you're at 165 bpm now, you were probably slightly")
print("     higher before (e.g., 3 weeks ago = 165 * 0.985 = 162 bpm)")
print("   → This is CONSERVATIVE - assumes small fitness changes")
print("   → Confidence: 95%")
print()
print("3. DISTANT PAST (5+ weeks ago) - NOT DONE YET")
print("   → Would analyze ACTUAL PERFORMANCE from activities")
print("   → For running: Look at HR during hard efforts")
print("   → For cycling: Look at power during hard efforts")
print("   → Blend: 60% performance + 40% trend")
print("   → Confidence: 50-70% (depends on data quality)")
print()
print("📈 WHY THIS MATTERS:")
print()
print("When we recalculate TSS for old activities, we'll use the")
print("threshold that was appropriate for THAT WEEK, not today's.")
print()
print("Example:")
print(f"   • Activity from {(today - timedelta(weeks=3)).strftime('%Y-%m-%d')} (3 weeks ago)")
print(f"   • OLD TSS: Used today's threshold ({run_hr} bpm)")
print(f"   • NEW TSS: Will use week's threshold (~{int(run_hr * 0.985)} bpm)")
print(f"   • Result: Slightly higher TSS (you were fitter then!)")
print()

conn.close()

print("✅ Test complete!")
print()
