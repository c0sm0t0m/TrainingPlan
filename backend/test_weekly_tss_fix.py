"""
Test the fixed weekly TSS calculation (calendar week instead of rolling 7 days).
"""
import asyncio
from datetime import datetime, timedelta
from sqlalchemy import select

import sys
sys.path.insert(0, '/Users/boetthw3/Documents/99_Other/TrainingPlan/backend')

from src.database import AsyncSessionLocal
from src.models.user import User
from src.utils.calculations.training_load import get_current_training_metrics, calculate_training_load_metrics

async def main():
    async with AsyncSessionLocal() as db:
        result = await db.execute(select(User).limit(1))
        user = result.scalar_one_or_none()
        
        if not user:
            print("❌ No user found")
            return
        
        print("="*70)
        print("WEEKLY TSS FIX VERIFICATION")
        print("="*70)
        
        today = datetime.now().date()
        weekday = today.weekday()
        monday = today - timedelta(days=weekday)
        sunday = monday + timedelta(days=6)
        
        print(f"\n�� Today: {today.strftime('%A, %B %d, %Y')}")
        print(f"📅 Current Week: {monday.strftime('%a, %b %d')} to {sunday.strftime('%a, %b %d')}")
        print(f"   (Monday = {monday}, Sunday = {sunday})")
        
        # Get current metrics with the fix
        metrics = await get_current_training_metrics(db, user.id)
        
        print(f"\n📊 Fixed Metrics:")
        print(f"   Weekly TSS: {metrics['weekly_tss']:.1f}")
        print(f"   CTL: {metrics['ctl']:.1f}")
        print(f"   ATL: {metrics['atl']:.1f}")
        print(f"   TSB: {metrics['tsb']:.1f}")
        
        # Verify by manually calculating from daily metrics
        print(f"\n🔍 Verification:")
        daily_metrics = await calculate_training_load_metrics(db, user.id, days=14)
        
        manual_weekly_tss = 0.0
        print(f"   Days in current week:")
        for day in daily_metrics:
            day_date = datetime.fromisoformat(day['date']).date()
            if day_date >= monday and day_date <= today:
                manual_weekly_tss += day['tss']
                day_name = day_date.strftime('%a, %b %d')
                print(f"   ✓ {day_name}: {day['tss']:.1f} TSS")
        
        print(f"\n   Manual calculation: {manual_weekly_tss:.1f} TSS")
        print(f"   API returned: {metrics['weekly_tss']:.1f} TSS")
        
        if abs(manual_weekly_tss - metrics['weekly_tss']) < 0.1:
            print(f"\n✅ SUCCESS: Values match!")
        else:
            print(f"\n❌ ERROR: Values don't match!")
        
        # Show what the old calculation would have been
        print(f"\n📊 Comparison with old method (rolling 7 days):")
        last_7_days_tss = sum(day['tss'] for day in daily_metrics[-7:])
        print(f"   Old (rolling 7 days): {last_7_days_tss:.1f} TSS")
        print(f"   New (current week):   {metrics['weekly_tss']:.1f} TSS")
        difference = metrics['weekly_tss'] - last_7_days_tss
        print(f"   Difference: {difference:+.1f} TSS")
        
        if difference != 0:
            print(f"\n✅ Calculation changed as expected!")
        else:
            print(f"\n⚠️  Same result (might be Sunday)")
        
        print("\n" + "="*70)

if __name__ == '__main__':
    asyncio.run(main())
