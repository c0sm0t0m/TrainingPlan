"""
Calculate historic thresholds for all 104 weeks (2 years)
"""
import asyncio
import sys
from datetime import datetime

sys.path.insert(0, '/Users/boetthw3/Documents/99_Other/TrainingPlan/backend')

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from src.database import engine
from src.models.user import User
from src.utils.historic_thresholds import calculate_historic_thresholds


async def main():
    print("=" * 80)
    print("CALCULATING HISTORIC THRESHOLDS - 104 WEEKS (2 YEARS)")
    print("=" * 80)
    print()
    
    async with AsyncSession(engine) as db:
        result = await db.execute(
            select(User).where(User.email == "tboettger@gmail.com")
        )
        user = result.scalar_one_or_none()
        
        if not user:
            print("❌ User not found")
            return
        
        print(f"👤 User: {user.email}")
        print(f"📊 Starting calculation...")
        print()
        
        start_time = datetime.now()
        
        stats = await calculate_historic_thresholds(
            user=user,
            db=db,
            lookback_weeks=104  # 2 years
        )
        
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        print()
        print("=" * 80)
        print("✅ CALCULATION COMPLETE!")
        print("=" * 80)
        print()
        print(f"Weeks calculated: {stats['weeks_calculated']}")
        print(f"Activities analyzed: {stats['activities_analyzed']}")
        print(f"Date range: {stats['oldest_week']} to {stats['newest_week']}")
        print(f"Duration: {duration:.1f} seconds")
        print()


if __name__ == "__main__":
    asyncio.run(main())
