import asyncio
from sqlalchemy import select
from src.database import AsyncSessionLocal
from src.models.garmin_activity import GarminActivity

async def main():
    async with AsyncSessionLocal() as db:
        query = select(GarminActivity).where(
            GarminActivity.user_id == 1,
            GarminActivity.activity_type.like('%running%'),
            GarminActivity.start_time_local >= '2024-01-01',
            GarminActivity.start_time_local < '2025-01-01',
            GarminActivity.average_hr.isnot(None),
            GarminActivity.duration_seconds >= 1200
        ).order_by(GarminActivity.average_hr.desc()).limit(15)
        
        result = await db.execute(query)
        acts = result.scalars().all()
        
        threshold_hr = 165
        print(f'\n🏃 Top 15 2024 Running Activities (20+ min, sorted by HR):\n')
        
        for a in acts:
            dur_min = a.duration_seconds / 60
            pace = 'N/A'
            if a.distance_meters:
                ps = a.duration_seconds / (a.distance_meters / 1000)
                pace = f'{int(ps//60)}:{int(ps%60):02d}'
            
            # Criteria
            is_key = False
            reason = ''
            if 20 <= dur_min <= 60:
                need = threshold_hr * 0.97
                is_key = a.average_hr >= need
                reason = f'' if is_key else f'Need {need:.0f}+ bpm'
            elif 60 < dur_min <= 75:
                need = threshold_hr * 0.95
                is_key = a.average_hr >= need
                reason = f'' if is_key else f'Need {need:.0f}+ bpm'
            elif dur_min > 75:
                need = threshold_hr * 0.90
                is_key = a.average_hr >= need
                reason = f'' if is_key else f'Need {need:.0f}+ bpm'
            
            print(f'{"✅" if is_key else "❌"} {a.start_time_local.strftime("%Y-%m-%d")} | '
                  f'HR {a.average_hr:3.0f} ({a.average_hr/threshold_hr*100:5.1f}%) | '
                  f'{dur_min:5.1f} min | {pace:>5} | {reason}')

asyncio.run(main())
