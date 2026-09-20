import asyncio
import sys
sys.path.insert(0, 'src')

from database import async_session_maker
from models.garmin import GarminActivity
from sqlalchemy import select, func, extract
from datetime import datetime

async def check_2024_activities():
    async with async_session_maker() as db:
        # Get all 2024 running activities with HR data
        query = select(
            GarminActivity.activity_id,
            GarminActivity.activity_name,
            GarminActivity.start_time_local,
            GarminActivity.duration_seconds,
            GarminActivity.average_hr,
            GarminActivity.distance_meters
        ).where(
            GarminActivity.user_id == 1,
            GarminActivity.activity_type.like('%running%'),
            GarminActivity.start_time_local >= '2024-01-01',
            GarminActivity.start_time_local < '2025-01-01',
            GarminActivity.average_hr.isnot(None),
            GarminActivity.duration_seconds >= 1200  # 20+ minutes
        ).order_by(GarminActivity.average_hr.desc())
        
        result = await db.execute(query)
        activities = result.all()
        
        print(f"\n🏃 Running activities in 2024 with HR data (20+ min):")
        print(f"Total found: {len(activities)}\n")
        
        # Threshold for comparison
        threshold_hr = 165
        
        for act in activities[:20]:  # Show top 20 by HR
            duration_min = act.duration_seconds / 60
            pace = None
            if act.distance_meters and act.distance_meters > 0:
                pace_sec_per_km = act.duration_seconds / (act.distance_meters / 1000)
                pace_min = int(pace_sec_per_km // 60)
                pace_sec = int(pace_sec_per_km % 60)
                pace = f"{pace_min}:{pace_sec:02d}"
            
            # Check key session criteria
            is_threshold_effort = (20 <= duration_min <= 60) and (act.average_hr >= threshold_hr * 0.97)
            is_long_tempo = (60 < duration_min <= 75) and (act.average_hr >= threshold_hr * 0.95)
            is_very_long_tempo = (duration_min > 75) and (act.average_hr >= threshold_hr * 0.90)
            
            is_key = is_threshold_effort or is_long_tempo or is_very_long_tempo
            
            hr_pct = (act.average_hr / threshold_hr * 100) if threshold_hr else 0
            
            print(f"{'✅' if is_key else '❌'} {act.start_time_local.strftime('%Y-%m-%d')} | "
                  f"{act.activity_name[:30]:30} | "
                  f"{duration_min:5.1f}min | "
                  f"HR:{act.average_hr:3.0f} ({hr_pct:5.1f}%) | "
                  f"Pace:{pace or 'N/A'}")
            
            if not is_key:
                # Explain why it doesn't qualify
                reasons = []
                if duration_min < 20:
                    reasons.append("too short")
                elif 20 <= duration_min <= 60:
                    if act.average_hr < threshold_hr * 0.97:
                        reasons.append(f"HR too low (need {threshold_hr * 0.97:.0f}+)")
                elif 60 < duration_min <= 75:
                    if act.average_hr < threshold_hr * 0.95:
                        reasons.append(f"HR too low (need {threshold_hr * 0.95:.0f}+)")
                elif duration_min > 75:
                    if act.average_hr < threshold_hr * 0.90:
                        reasons.append(f"HR too low (need {threshold_hr * 0.90:.0f}+)")
                
                if reasons:
                    print(f"   → {', '.join(reasons)}")

if __name__ == '__main__':
    asyncio.run(check_2024_activities())
