#!/usr/bin/env python3
"""
Check Garmin activities in database
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import asyncio
from sqlalchemy import select, func
from src.database import AsyncSessionLocal
from src.models.garmin_activity import GarminActivity
from src.models.user import User

async def check_activities():
    async with AsyncSessionLocal() as db:
        # Count total activities
        result = await db.execute(select(func.count(GarminActivity.id)))
        total = result.scalar()
        
        print(f"📊 Total Garmin activities in database: {total}")
        
        if total == 0:
            print("\n⚠️  No activities found!")
            print("   You need to sync activities from Garmin first.")
            print("   Use: Settings > Garmin Connect > Sync Activities")
            return
        
        # Get activities by user
        result = await db.execute(
            select(User.id, User.email, func.count(GarminActivity.id))
            .join(GarminActivity, User.id == GarminActivity.user_id)
            .group_by(User.id, User.email)
        )
        
        print("\n📈 Activities by user:")
        for user_id, email, count in result:
            print(f"   User {user_id} ({email}): {count} activities")
        
        # Get sample activities
        result = await db.execute(
            select(GarminActivity)
            .order_by(GarminActivity.start_time_local.desc())
            .limit(5)
        )
        activities = result.scalars().all()
        
        print("\n🏃 Recent activities:")
        for act in activities:
            date = act.start_time_local.strftime("%Y-%m-%d") if act.start_time_local else "N/A"
            print(f"   {date}: {act.activity_name} ({act.activity_type})")

if __name__ == "__main__":
    asyncio.run(check_activities())
