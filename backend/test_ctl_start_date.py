#!/usr/bin/env python3
import asyncio
from sqlalchemy import select, func
from src.database import get_db
from src.models.garmin_activity import GarminActivity
from src.models.user import User
from datetime import datetime

async def check_first_activity():
    async for db in get_db():
        # Get user
        user_result = await db.execute(
            select(User).where(User.email == "tboettger@gmail.com")
        )
        user = user_result.scalar_one()
        
        # Query for first cycling activity
        first_activity_query = select(
            func.min(GarminActivity.start_time_local)
        ).where(
            GarminActivity.user_id == user.id,
            GarminActivity.activity_type.in_(['cycling', 'virtual_ride', 'indoor_cycling', 'mountain_biking'])
        )
        
        result = await db.execute(first_activity_query)
        first_date = result.scalar()
        
        print(f"User ID: {user.id}")
        print(f"First cycling activity date (from query): {first_date}")
        print(f"Type: {type(first_date)}")
        
        if isinstance(first_date, str):
            parsed = datetime.fromisoformat(first_date.split('.')[0])
            print(f"Parsed date: {parsed}")
        
        break

asyncio.run(check_first_activity())
