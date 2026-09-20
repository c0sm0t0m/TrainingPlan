"""
Calculate historic thresholds for all 104 weeks - Direct SQL version
"""
import sqlite3
from datetime import datetime, timedelta
import statistics

print("=" * 80)
print("CALCULATING HISTORIC THRESHOLDS - 104 WEEKS (2 YEARS)")
print("=" * 80)
print()

conn = sqlite3.connect('/Users/boetthw3/Documents/99_Other/TrainingPlan/backend/trainingplan.db')
cursor = conn.cursor()

# Get user
cursor.execute("""
    SELECT id, email, running_threshold_hr, cycling_threshold_hr, ftp, max_hr, resting_hr 
    FROM users 
    WHERE email = 'tboettger@gmail.com'
""")
user = cursor.fetchone()
user_id, email, run_hr, cyc_hr, ftp, max_hr, rest_hr = user

print(f"👤 User: {email}")
print(f"   Thresholds: Run={run_hr}, Cycle={cyc_hr}, FTP={ftp}, Max={max_hr}")
print()

today = datetime.now()
start_time = datetime.now()

# Calculate for 104 weeks
weeks_calculated = 0
key_sessions_found = 0

for weeks_ago in range(105):  # 0 to 104
    target_date = today - timedelta(weeks=weeks_ago)
    year, week, _ = target_date.isocalendar()
    
    if weeks_ago % 10 == 0:
        print(f"Processing week {weeks_ago}/104... ({year}-W{week:02d})")
    
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
    """, (user_id, week_start.strftime('%Y-%m-%d'), week_end.strftime('%Y-%m-%d')))
    
    activities = cursor.fetchall()
    
    # Calculate threshold
    if weeks_ago == 0:
        est_run_hr = run_hr
        est_cyc_hr = cyc_hr
        est_ftp = ftp
        method = "current"
        confidence = 1.0
    else:
        # Analyze running activities
        key_session_hrs = []
        regular_hrs = []
        
        for sport, dur, avg_hr, max_hr_act in activities:
            if 'run' in sport.lower() and avg_hr and max_hr_act:
                dur_min = dur / 60 if dur else 0
                
                # Detect key sessions
                is_key = (20 <= dur_min <= 60 and max_hr_act >= (max_hr * 0.85))
                
                if is_key:
                    # Key session: use avg HR with duration adjustment
                    if dur_min < 30:
                        threshold_est = avg_hr / 1.05
                    elif dur_min < 45:
                        threshold_est = avg_hr / 1.02
                    else:
                        threshold_est = avg_hr
                    key_session_hrs.append(threshold_est)
                    key_sessions_found += 1
                else:
                    # Regular run
                    threshold_est = avg_hr + (max_hr_act - avg_hr) * 0.35
                    regular_hrs.append(threshold_est)
        
        # Calculate threshold
        trend_factor = 1.0 - (weeks_ago * 0.003)
        
        if key_session_hrs:
            perf_estimate = int(statistics.median(key_session_hrs))
            trend_estimate = int(run_hr * trend_factor)
            est_run_hr = int(perf_estimate * 0.8 + trend_estimate * 0.2)
            est_cyc_hr = est_run_hr - 5
            est_ftp = int(ftp * trend_factor)
            method = "performance_analysis"
            confidence = 0.90
        elif regular_hrs:
            perf_estimate = int(statistics.median(regular_hrs))
            trend_estimate = int(run_hr * trend_factor)
            est_run_hr = int(perf_estimate * 0.7 + trend_estimate * 0.3)
            est_cyc_hr = est_run_hr - 5
            est_ftp = int(ftp * trend_factor)
            method = "performance_analysis"
            confidence = 0.75 if len(activities) >= 3 else 0.65
        else:
            est_run_hr = int(run_hr * trend_factor)
            est_cyc_hr = int(cyc_hr * trend_factor)
            est_ftp = int(ftp * trend_factor)
            method = "trend_extrapolation"
            confidence = 0.4
    
    # Save to database
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
        """, (est_run_hr, est_cyc_hr, est_ftp, 5.0, 120.0, max_hr, rest_hr, 
              method, confidence, len(activities), user_id, year, week))
    else:
        cursor.execute("""
            INSERT INTO weekly_thresholds 
            (user_id, year, week, running_threshold_hr, cycling_threshold_hr, ftp,
             threshold_pace, swim_threshold_pace, max_hr, resting_hr,
             calculation_method, confidence_score, activities_used)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (user_id, year, week, est_run_hr, est_cyc_hr, est_ftp, 5.0, 120.0,
              max_hr, rest_hr, method, confidence, len(activities)))
    
    weeks_calculated += 1

conn.commit()

end_time = datetime.now()
duration = (end_time - start_time).total_seconds()

print()
print("=" * 80)
print("✅ CALCULATION COMPLETE!")
print("=" * 80)
print()
print(f"Weeks calculated: {weeks_calculated}")
print(f"Key sessions found: {key_sessions_found}")
print(f"Duration: {duration:.1f} seconds")
print()

# Show sample results
print("Sample thresholds (most recent 10 weeks):")
print()
cursor.execute("""
    SELECT year, week, running_threshold_hr, ftp, calculation_method, confidence_score, activities_used
    FROM weekly_thresholds
    WHERE user_id = ?
    ORDER BY year DESC, week DESC
    LIMIT 10
""", (user_id,))

for year, week, run_hr_t, ftp_t, method, conf, acts in cursor.fetchall():
    print(f"  {year}-W{week:02d}: HR={run_hr_t:3d}bpm, FTP={ftp_t:3d}W, {method:20s} ({conf:.0%}, {acts} activities)")

conn.close()
print()
print("✅ All done!")
