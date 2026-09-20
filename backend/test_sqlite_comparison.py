"""Test SQLite date comparison directly"""
import asyncio
import sys
from datetime import datetime, time

sys.path.insert(0, '/Users/boetthw3/Documents/99_Other/TrainingPlan/backend')

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select, text
from src.models.user import User
from src.models.garmin_activity import GarminActivity
from src.utils.datetime_helpers import compare_date_for_sqlite


async def main():
    engine = create_async_engine(
        "sqlite+aiosqlite:////Users/boetthw3/Documents/99_Other/TrainingPlan/backend/trainingplan.db",
        echo=False
    )
    
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    async with async_session() as db:
        result = await db.execute(select(User).where(User.email == "tboettger@gmail.com"))
        user = result.scalar_one()
        
        print(f"🔍 Testing SQLite String Comparison")
        print(f"=" * 80)
        
        today = datetime.now().date()
        print(f"\nToday: {today}")
        
        # Get today's activities with raw query
        print(f"\n📋 Today's Activities (Raw Times):")
        result = await db.execute(
            select(GarminActivity.start_time_local, GarminActivity.activity_name, GarminActivity.calculated_tss).where(
                GarminActivity.user_id == user.id,
                GarminActivity.start_time_local >= datetime.combine(today, datetime.min.time()),
                GarminActivity.start_time_local < datetime.combine(today + timedelta(days=1), datetime.min.time())
            )
        )
        activities = result.all()
        for act in activities:
            print(f"  {act[1]}: {act[0]} (stored as: {type(act[0])}) TSS={act[2]}")
        
        # Test different comparison strings
        print(f"\n🧪 Testing Different Comparison Strings:")
        
        test_comparisons = [
            ("2026-01-05", "Just date"),
            ("2026-01-05 23:59:59", "Date with time 23:59:59"),
            ("2026-01-05 23:59:59.999999", "Date with max time"),
            ("2026-01-06", "Next day"),
        ]
        
        for comp_str, desc in test_comparisons:
            result = await db.execute(
                select(GarminActivity.activity_name, GarminActivity.start_time_local).where(
                    GarminActivity.user_id == user.id,
                    GarminActivity.start_time_local <= comp_str
                ).order_by(GarminActivity.start_time_local.desc()).limit(3)
            )
            recent = result.all()
            print(f"\n  Comparison: start_time_local <= '{comp_str}' ({desc})")
            print(f"  Last 3 activities:")
            for act in recent:
                print(f"    - {act[1]}: {act[0]}")
        
        # Test what compare_date_for_sqlite returns
        print(f"\n🔧 compare_date_for_sqlite() Output:")
        test_dates = [
            datetime.now(),
            datetime.combine(today, time.max),
            today,
        ]
        for dt in test_dates:
            result = compare_date_for_sqlite(dt)
            print(f"  Input: {dt} (type: {type(dt).__name__})")
            print(f"  Output: '{result}'")


if __name__ == "__main__":
    from datetime import timedelta
    asyncio.run(main())
