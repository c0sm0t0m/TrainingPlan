"""Debug why today's TSS is not included in CTL calculation"""
import asyncio
import sys
from datetime import datetime, timedelta

sys.path.insert(0, '/Users/boetthw3/Documents/99_Other/TrainingPlan/backend')

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select
from src.models.user import User
from src.models.garmin_activity import GarminActivity
from src.utils.calculations.training_load import calculate_training_load_metrics


async def main():
    engine = create_async_engine(
        "sqlite+aiosqlite:////Users/boetthw3/Documents/99_Other/TrainingPlan/backend/trainingplan.db",
        echo=False
    )
    
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    async with async_session() as db:
        result = await db.execute(select(User).where(User.email == "tboettger@gmail.com"))
        user = result.scalar_one()
        
        print(f"🔍 Debugging Today's TSS Inclusion")
        print(f"=" * 80)
        
        # Current time info
        now = datetime.now()
        today = now.date()
        
        print(f"\nCurrent datetime: {now}")
        print(f"Today's date: {today}")
        print(f"Time: {now.time()}")
        
        # Check today's activities
        print(f"\n📋 Today's Activities ({today}):")
        result = await db.execute(
            select(GarminActivity).where(
                GarminActivity.user_id == user.id,
                GarminActivity.start_time_local >= datetime.combine(today, datetime.min.time()),
                GarminActivity.start_time_local < datetime.combine(today + timedelta(days=1), datetime.min.time())
            ).order_by(GarminActivity.start_time_local)
        )
        activities = result.scalars().all()
        
        total_tss = sum(a.calculated_tss or 0 for a in activities)
        print(f"Found {len(activities)} activities with total TSS: {total_tss:.1f}")
        for activity in activities:
            print(f"  - {activity.activity_name}: TSS={activity.calculated_tss or 0:.1f}, "
                  f"Time={activity.start_time_local}")
        
        # Test different end_date values
        print(f"\n📊 Testing Different end_date Values:")
        print("-" * 80)
        
        # Test 1: Without explicit end_date (should use datetime.now())
        print(f"\n1. No end_date specified (defaults to datetime.now()):")
        metrics1 = await calculate_training_load_metrics(
            db=db,
            user_id=user.id,
            days=3
        )
        print(f"   Last date in results: {metrics1[-1]['date'] if metrics1 else 'NONE'}")
        if metrics1:
            print(f"   CTL={metrics1[-1]['ctl']:.1f}, TSS={metrics1[-1]['tss']:.1f}")
        
        # Test 2: With end_date = datetime.combine(today, datetime.min.time())
        print(f"\n2. end_date = datetime.combine(today, datetime.min.time()) = {datetime.combine(today, datetime.min.time())}:")
        metrics2 = await calculate_training_load_metrics(
            db=db,
            user_id=user.id,
            days=3,
            end_date=datetime.combine(today, datetime.min.time())
        )
        print(f"   Last date in results: {metrics2[-1]['date'] if metrics2 else 'NONE'}")
        if metrics2:
            print(f"   CTL={metrics2[-1]['ctl']:.1f}, TSS={metrics2[-1]['tss']:.1f}")
        
        # Test 3: With end_date = datetime.combine(today, datetime.max.time())
        print(f"\n3. end_date = datetime.combine(today, datetime.max.time()) = {datetime.combine(today, datetime.max.time())}:")
        metrics3 = await calculate_training_load_metrics(
            db=db,
            user_id=user.id,
            days=3,
            end_date=datetime.combine(today, datetime.max.time())
        )
        print(f"   Last date in results: {metrics3[-1]['date'] if metrics3 else 'NONE'}")
        if metrics3:
            print(f"   CTL={metrics3[-1]['ctl']:.1f}, TSS={metrics3[-1]['tss']:.1f}")
        
        # Test 4: With end_date = now (current datetime)
        print(f"\n4. end_date = datetime.now() = {now}:")
        metrics4 = await calculate_training_load_metrics(
            db=db,
            user_id=user.id,
            days=3,
            end_date=now
        )
        print(f"   Last date in results: {metrics4[-1]['date'] if metrics4 else 'NONE'}")
        if metrics4:
            print(f"   CTL={metrics4[-1]['ctl']:.1f}, TSS={metrics4[-1]['tss']:.1f}")
        
        # Show all 3 days for comparison
        print(f"\n📈 Full 3-Day Comparison (using datetime.now()):")
        print("-" * 80)
        for metric in metrics4:
            marker = " ← TODAY" if metric['date'] == str(today) else ""
            print(f"{metric['date']}: CTL={metric['ctl']:.1f}, ATL={metric['atl']:.1f}, TSS={metric['tss']:.1f}{marker}")


if __name__ == "__main__":
    asyncio.run(main())
