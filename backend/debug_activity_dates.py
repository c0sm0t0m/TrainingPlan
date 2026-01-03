#!/usr/bin/env python3
"""Debug script to check activity data and date ranges."""

import asyncio
from datetime import datetime, timedelta
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

async def check_activities():
    # Use the database URL from .env
    DATABASE_URL = "sqlite+aiosqlite:///./trainingplan.db"
    
    engine = create_async_engine(DATABASE_URL, echo=False)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    async with async_session() as session:
        from src.models.garmin_activity import GarminActivity
        from src.utils.datetime_helpers import date_to_string
        
        # Get total count
        count_query = select(func.count(GarminActivity.id))
        result = await session.execute(count_query)
        total = result.scalar()
        
        print(f"Total activities in database: {total}")
        print()
        
        if total == 0:
            print("No activities found! Database is empty.")
            return
        
        # Get date range
        query = select(
            func.min(GarminActivity.start_time_local),
            func.max(GarminActivity.start_time_local)
        )
        result = await session.execute(query)
        min_date, max_date = result.one()
        
        print(f"Earliest activity: {min_date}")
        print(f"Latest activity: {max_date}")
        print()
        
        # Get sample activities
        sample_query = select(GarminActivity).order_by(GarminActivity.start_time_local.desc()).limit(10)
        result = await session.execute(sample_query)
        activities = result.scalars().all()
        
        print("Last 10 activities:")
        print("-" * 80)
        for act in activities:
            date_str = date_to_string(act.start_time_local)
            print(f"{date_str} | {act.activity_name:30s} | TSS: {act.calculated_tss or 0:5.1f} | {act.activity_type}")
        
        print()
        print("Checking for activities outside December 2025 - January 2026...")
        
        # Check for older activities
        old_query = select(GarminActivity).where(
            GarminActivity.start_time_local < "2025-12-01"
        ).order_by(GarminActivity.start_time_local.desc()).limit(5)
        result = await session.execute(old_query)
        old_activities = result.scalars().all()
        
        if old_activities:
            print(f"Found {len(old_activities)} activities before December 2025:")
            for act in old_activities:
                date_str = date_to_string(act.start_time_local)
                print(f"  {date_str} | {act.activity_name}")
        else:
            print("No activities before December 2025")
        
        # Check CTL/ATL calculation date range
        print()
        print("Checking training load calculation date range...")
        today = datetime.utcnow()
        lookback = today - timedelta(days=84)  # CTL needs 84 days history
        
        count_query = select(func.count(GarminActivity.id)).where(
            GarminActivity.start_time_local >= lookback.strftime("%Y-%m-%d")
        )
        result = await session.execute(count_query)
        recent_count = result.scalar()
        
        print(f"Activities in last 84 days (for CTL calculation): {recent_count}")
        print(f"Date range: {lookback.date()} to {today.date()}")

if __name__ == "__main__":
    asyncio.run(check_activities())
