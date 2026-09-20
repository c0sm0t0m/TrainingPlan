"""
Test script to understand current behavior of weekly TSS calculation.
"""
import asyncio
from datetime import datetime, timedelta
from sqlalchemy import select

import sys
sys.path.insert(0, '/Users/boetthw3/Documents/99_Other/TrainingPlan/backend')

from src.database import AsyncSessionLocal
from src.models.user import User
from src.utils.calculations.training_load import get_current_training_metrics

async def main():
    async with AsyncSessionLocal() as db:
        # Get first user
        result = await db.execute(select(User).limit(1))
        user = result.scalar_one_or_none()
        
        if not user:
            print("❌ No user found")
            return
        
        print("="*70)
        print("WEEKLY TSS BEHAVIOR ANALYSIS")
        print("="*70)
        print(f"\n👤 User: {user.email}")
        print(f"📅 Today: {datetime.now().strftime('%A, %B %d, %Y')}")
        print(f"📆 Date: {datetime.now().date()}")
        
        # Calculate current week (Monday-Sunday)
        today = datetime.now().date()
        weekday = today.weekday()  # Monday=0, Sunday=6
        monday = today - timedelta(days=weekday)
        sunday = monday + timedelta(days=6)
        
        print(f"\n📅 CALENDAR WEEK (Monday-Sunday):")
        print(f"   Start: {monday.strftime('%A, %B %d, %Y')}")
        print(f"   End:   {sunday.strftime('%A, %B %d, %Y')}")
        
        # Calculate last 7 days (rolling window)
        last_7_start = today - timedelta(days=6)
        last_7_end = today
        
        print(f"\n🔄 LAST 7 DAYS (Rolling Window):")
        print(f"   Start: {last_7_start.strftime('%A, %B %d, %Y')}")
        print(f"   End:   {last_7_end.strftime('%A, %B %d, %Y')}")
        
        # Get current metrics
        metrics = await get_current_training_metrics(db, user.id)
        
        print(f"\n📊 CURRENT METRICS FROM API:")
        print(f"   CTL (Fitness):  {metrics['ctl']:.1f}")
        print(f"   ATL (Fatigue):  {metrics['atl']:.1f}")
        print(f"   TSB (Form):     {metrics['tsb']:.1f}")
        print(f"   Weekly TSS:     {metrics['weekly_tss']:.1f}")
        print(f"   Trend:          {metrics['trend']}")
        
        # Show the difference
        print(f"\n🔍 ANALYSIS:")
        print(f"   Current code calculates: sum(metrics[-7:])")
        print(f"   This means: TSS from last 7 entries in the daily metrics array")
        print(f"   ")
        print(f"   Last 7 days includes:")
        for i in range(7):
            date = today - timedelta(days=6-i)
            is_in_current_week = monday <= date <= sunday
            marker = "✓" if is_in_current_week else " "
            print(f"   [{marker}] {date.strftime('%a, %b %d')}")
        
        print(f"\n⚠️  COMPARISON:")
        print(f"   • Last 7 days: {last_7_start} to {last_7_end}")
        print(f"   • Current week: {monday} to {sunday}")
        
        if monday != last_7_start or sunday != last_7_end:
            print(f"\n❌ DISCREPANCY FOUND!")
            print(f"   These date ranges are DIFFERENT!")
            print(f"   ")
            print(f"   Example: If today is Wednesday (2026-01-08):")
            print(f"   • Last 7 days: Thursday 2026-01-02 → Wednesday 2026-01-08")
            print(f"   • Current week: Monday 2026-01-06 → Sunday 2026-01-12")
            print(f"   ")
            print(f"   This means the 'Weekly TSS' on the dashboard")
            print(f"   shows TSS from a rolling 7-day window,")
            print(f"   NOT from the current calendar week.")
        else:
            print(f"\n✅ Date ranges match (happens only on Sunday)")
        
        print("\n" + "="*70)
        print("REQUIREMENT: 'dashboard weekly tss shall display the tss of the current week.'")
        print("="*70)
        print("\nINTERPRETATION:")
        print("  'Current week' typically means: Monday to Sunday (or Sun to Sat)")
        print("  NOT a rolling 7-day window.")
        print("\nCURRENT BEHAVIOR:")
        print("  ❌ Shows TSS from last 7 days (rolling window)")
        print("\nEXPECTED BEHAVIOR:")
        print("  ✅ Should show TSS from Monday to Sunday of current week")
        print("\nRECOMMENDATION:")
        print("  Change the calculation to use calendar week boundaries")
        print("  instead of a rolling 7-day window.")
        print("="*70)

if __name__ == '__main__':
    asyncio.run(main())
