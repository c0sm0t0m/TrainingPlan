"""Test CTL values for yesterday and today to debug the 675 -> 65.9 drop"""
import asyncio
import sys
from datetime import datetime, timedelta

# Add backend src to path
sys.path.insert(0, '/Users/boetthw3/Documents/99_Other/TrainingPlan/backend')

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select
from src.models.user import User
from src.models.garmin_activity import GarminActivity
from src.utils.calculations.training_load import calculate_training_load_metrics


async def main():
    # Create database connection
    engine = create_async_engine(
        "sqlite+aiosqlite:////Users/boetthw3/Documents/99_Other/TrainingPlan/backend/trainingplan.db",
        echo=False
    )
    
    async_session = sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )
    
    async with async_session() as db:
        # Get user
        result = await db.execute(select(User).where(User.email == "tboettger@gmail.com"))
        user = result.scalar_one()
        
        print(f"User: {user.email} (ID: {user.id})")
        print(f"=" * 80)
        
        # Get last 7 days of training load
        print("\n📊 Last 7 Days CTL/ATL/TSB:")
        print("-" * 80)
        
        today = datetime.now().date()
        metrics = await calculate_training_load_metrics(
            db=db,
            user_id=user.id,
            days=7,
            end_date=datetime.combine(today, datetime.min.time())
        )
        
        for metric in metrics:
            date_str = metric['date']
            ctl = metric['ctl']
            atl = metric['atl']
            tsb = metric['tsb']
            tss = metric['tss']
            
            # Highlight yesterday and today
            marker = ""
            if date_str == str(today - timedelta(days=1)):
                marker = " ← YESTERDAY"
            elif date_str == str(today):
                marker = " ← TODAY"
            
            print(f"{date_str}: CTL={ctl:.1f}, ATL={atl:.1f}, TSB={tsb:.1f}, TSS={tss:.1f}{marker}")
        
        # Check activities for yesterday and today
        print("\n\n🏃 Activities Yesterday and Today:")
        print("-" * 80)
        
        yesterday = today - timedelta(days=1)
        
        for check_date in [yesterday, today]:
            result = await db.execute(
                select(GarminActivity).where(
                    GarminActivity.user_id == user.id,
                    GarminActivity.start_time_local >= datetime.combine(check_date, datetime.min.time()),
                    GarminActivity.start_time_local < datetime.combine(check_date + timedelta(days=1), datetime.min.time())
                ).order_by(GarminActivity.start_time_local)
            )
            activities = result.scalars().all()
            
            total_tss = sum(a.calculated_tss or 0 for a in activities)
            
            print(f"\n{check_date} ({len(activities)} activities, Total TSS: {total_tss:.1f}):")
            for activity in activities:
                print(f"  - {activity.activity_name}: TSS={activity.calculated_tss or 0:.1f}, "
                      f"Type={activity.activity_type}, "
                      f"Time={activity.start_time_local.strftime('%H:%M')}")


if __name__ == "__main__":
    asyncio.run(main())
