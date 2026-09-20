"""Test if sport-specific CTL also includes today's TSS correctly"""
import asyncio
import sys
from datetime import datetime

sys.path.insert(0, '/Users/boetthw3/Documents/99_Other/TrainingPlan/backend')

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select
from src.models.user import User
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
        
        today = datetime.now().date()
        
        print(f"🔍 Sport-Specific CTL for Today ({today})")
        print(f"=" * 80)
        
        sports = [
            (None, "Overall"),
            ("running", "Running"),
            ("cycling", "Cycling"),
        ]
        
        for sport_type, sport_name in sports:
            print(f"\n📊 {sport_name} CTL (last 3 days):")
            print("-" * 80)
            
            metrics = await calculate_training_load_metrics(
                db=db,
                user_id=user.id,
                days=3,
                sport_type=sport_type
            )
            
            for metric in metrics:
                marker = " ← TODAY" if metric['date'] == str(today) else ""
                print(f"{metric['date']}: CTL={metric['ctl']:.1f}, TSS={metric['tss']:.1f}{marker}")
        
        print(f"\n" + "=" * 80)
        print(f"✅ All sport-specific calculations should now include today's TSS")


if __name__ == "__main__":
    asyncio.run(main())
