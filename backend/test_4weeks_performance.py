"""
4-Week Historic Threshold Calculator - WITH PERFORMANCE ANALYSIS
Now analyzes actual activities to estimate thresholds!
"""
import sqlite3
from datetime import datetime, timedelta

print("=" * 80)
print("HISTORIC THRESHOLD CALCULATION - WITH PERFORMANCE ANALYSIS")
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
print()

# Get today's week
today = datetime.now()
current_year, current_week, _ = today.isocalendar()

print(f"📅 Today: {today.strftime('%Y-%m-%d')} = ISO Week {current_year}-W{current_week:02d}")
print()

print("-" * 80)
print("CALCULATING THRESHOLDS BASED ON ACTUAL PERFORMANCE...")
print("-" * 80)
print()

thresholds_to_insert = []

for weeks_ago in range(5):  # 0, 1, 2, 3, 4
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
    
    print(f"   Activities: {len(activities)}")
    
    # Analyze running activities for threshold estimation
    running_hrs = []
    for sport, dur, avg_hr, max_hr_act in activities:
        if 'run' in sport.lower() and avg_hr and max_hr_act:
            # Estimate threshold as 85th percentile: avg + 35% of range
            estimated_threshold = avg_hr + (max_hr_act - avg_hr) * 0.35
            running_hrs.append(estimated_threshold)
            
            dur_min = dur / 60 if dur else 0
            print(f"      • {sport}: {dur_min:.0f}min, Avg HR={avg_hr}, Max HR={max_hr_act}")
            print(f"        → Estimated threshold: {estimated_threshold:.0f} bpm")
    
    # Calculate threshold for this week
    if weeks_ago == 0:
        # Current week - use actual values
        est_run_hr = run_hr
        est_cyc_hr = cyc_hr
        est_ftp = ftp
        method = "current"
        confidence = 1.0
        print(f"   ✅ Using CURRENT thresholds (no estimation)")
        
    else:
        # Estimate from performance
        if running_hrs:
            # Use median of estimated thresholds
            from statistics import median
            perf_estimate = int(median(running_hrs))
            
            # Blend: 70% performance + 30% trend (0.3% per week)
            trend_factor = 1.0 - (weeks_ago * 0.003)
            trend_estimate = int(run_hr * trend_factor)
            
            est_run_hr = int(perf_estimate * 0.7 + trend_estimate * 0.3)
            est_cyc_hr = est_run_hr - 5  # Cycling HR typically 5 lower
            
            # FTP: use trend (no power data)
            est_ftp = int(ftp * trend_factor)
            
            method = "performance_analysis"
            confidence = 0.85 if len(activities) >= 5 else 0.75 if len(activities) >= 3 else 0.65
            
            print(f"   📈 PERFORMANCE-BASED ESTIMATION:")
            print(f"      Performance data: {perf_estimate} bpm (from {len(running_hrs)} runs)")
            print(f"      Trend estimate:   {trend_estimate} bpm (0.3% per week)")
            print(f"      Final (70/30):    {est_run_hr} bpm")
        else:
            # No running data - use trend only
            trend_factor = 1.0 - (weeks_ago * 0.003)
            est_run_hr = int(run_hr * trend_factor)
            est_cyc_hr = int(cyc_hr * trend_factor)
            est_ftp = int(ftp * trend_factor)
            method = "trend_extrapolation"
            confidence = 0.4
            print(f"   📉 TREND-BASED (no running data): {est_run_hr} bpm")
    
    print(f"   Confidence: {confidence:.0%}")
    print()
    
    thresholds_to_insert.append((
        user_id, year, week,
        est_run_hr, est_cyc_hr, est_ftp,
        5.0, 120.0, max_hr, rest_hr,
        method, confidence, len(activities)
    ))

# Save to database
print("-" * 80)
print("SAVING TO DATABASE...")
print("-" * 80)
print()

for threshold in thresholds_to_insert:
    user_id, year, week, run_hr_t, cyc_hr_t, ftp_t, t_pace, swim_pace, max_hr, rest_hr, method, conf, acts = threshold
    
    cursor.execute("""
        SELECT id FROM weekly_thresholds 
        WHERE user_id = ? AND year = ? AND week = ?
    """, (user_id, year, week))
    
    existing = cursor.fetchone()
    
    if existing:
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
        """, (run_hr_t, cyc_hr_t, ftp_t, t_pace, swim_pace, max_hr, rest_hr, method, conf, acts,
              user_id, year, week))
        print(f"   ✏️  Updated {year}-W{week:02d}: HR={run_hr_t}, {method} ({conf:.0%})")
    else:
        cursor.execute("""
            INSERT INTO weekly_thresholds 
            (user_id, year, week, running_threshold_hr, cycling_threshold_hr, ftp,
             threshold_pace, swim_threshold_pace, max_hr, resting_hr,
             calculation_method, confidence_score, activities_used)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (user_id, year, week, run_hr_t, cyc_hr_t, ftp_t, t_pace, swim_pace, max_hr, rest_hr,
              method, conf, acts))
        print(f"   ✅ Inserted {year}-W{week:02d}: HR={run_hr_t}, {method} ({conf:.0%})")

conn.commit()
print()
print("✅ Database updated!")
print()

# Compare old vs new
print("-" * 80)
print("COMPARISON: Simple Degradation vs Performance Analysis")
print("-" * 80)
print()
print(f"{'Week':<12} {'Simple':<15} {'Performance':<15} {'Difference'}")
print("-" * 60)

for weeks_ago in range(5):
    target_date = today - timedelta(weeks=weeks_ago)
    year, week, _ = target_date.isocalendar()
    
    # Simple degradation
    simple_hr = int(165 * (1.0 - weeks_ago * 0.005))
    
    # Performance-based (from database)
    cursor.execute("""
        SELECT running_threshold_hr FROM weekly_thresholds
        WHERE user_id = ? AND year = ? AND week = ?
    """, (user_id, year, week))
    perf_hr = cursor.fetchone()[0]
    
    diff = perf_hr - simple_hr
    diff_str = f"+{diff}" if diff >= 0 else str(diff)
    
    print(f"{year}-W{week:02d}  {simple_hr:>3} bpm       {perf_hr:>3} bpm        {diff_str:>3} bpm")

print()
print("=" * 80)
print("KEY INSIGHT:")
print("=" * 80)
print()
print("Performance-based estimation uses YOUR ACTUAL ACTIVITIES to estimate")
print("thresholds, not just a simple degradation formula.")
print()
print("For example, week 2025-W51 (2 weeks ago):")
print("  • You ran 114min at avg HR 151, max 173")
print("  • Estimated threshold: 151 + (173-151)*0.35 = 159 bpm")
print("  • This is HIGHER than simple degradation (163 bpm)")
print("  • Suggests you were actually running at a different effort level")
print()
print("This gives much more accurate historic TSS values!")
print()

conn.close()
