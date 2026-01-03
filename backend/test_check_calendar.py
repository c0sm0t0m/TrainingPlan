#!/usr/bin/env python3
"""
Check Garmin Calendar for Scheduled Workouts

Queries the Garmin calendar to see what workouts are scheduled.
"""
import asyncio
import sys
from datetime import date, timedelta

sys.path.insert(0, '/Users/boetthw3/Documents/99_Other/TrainingPlan/backend')

from src.database import AsyncSessionLocal, engine
from src.models.user import User
from src.services.garmin_service import garmin_service
from sqlalchemy import select


async def check_calendar():
    """Check what's on the Garmin calendar."""
    print("=" * 60)
    print("Checking Garmin Calendar")
    print("=" * 60)
    
    try:
        async with AsyncSessionLocal() as db:
            # Get user
            result = await db.execute(select(User).where(User.email == 'tboettger@gmail.com'))
            user = result.scalar_one_or_none()
            
            if not user:
                print("❌ User not found")
                return
            
            print(f"✅ Found user: {user.email}")
            
            # Resume Garmin session
            api = await garmin_service.resume_session(
                user.garmin_oauth1_token,
                user.garmin_oauth2_token
            )
            
            # Check today and next 7 days
            today = date.today()
            print(f"\n📅 Checking calendar from {today} onwards...")
            
            for i in range(7):
                check_date = today + timedelta(days=i)
                date_str = check_date.strftime('%Y-%m-%d')
                
                try:
                    # Try to get calendar data for this date
                    # Use garth.connectapi to query the calendar
                    response = api.garth.connectapi(
                        f"/calendar-service/calendar/{date_str}",
                        method="GET"
                    )
                    
                    if response:
                        print(f"\n{check_date} ({check_date.strftime('%A')}):")
                        
                        # Check for workouts
                        if isinstance(response, dict):
                            if 'calendarItems' in response:
                                items = response['calendarItems']
                                if items:
                                    for item in items:
                                        if item.get('itemType') == 'workout':
                                            workout_name = item.get('workoutName', 'Unknown')
                                            workout_id = item.get('workoutId', 'N/A')
                                            print(f"  🏃 Workout: {workout_name} (ID: {workout_id})")
                                else:
                                    print(f"  - No workouts scheduled")
                            else:
                                print(f"  - Response: {list(response.keys())}")
                        else:
                            print(f"  - Unexpected response type: {type(response)}")
                    else:
                        print(f"\n{check_date}: No data")
                        
                except Exception as e:
                    print(f"\n{check_date}: Error - {e}")
            
            # Also try to get all scheduled workouts
            print("\n\n📋 Getting all scheduled workouts...")
            try:
                scheduled = api.garth.connectapi(
                    "/workout-service/schedule",
                    method="GET",
                    params={"start": 1, "limit": 100}
                )
                
                if scheduled:
                    print(f"Found scheduled workouts: {scheduled}")
                else:
                    print("No scheduled workouts found")
                    
            except Exception as e:
                print(f"Error getting scheduled workouts: {e}")
    
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        raise
    
    finally:
        await engine.dispose()


if __name__ == "__main__":
    try:
        asyncio.run(check_calendar())
        print("\n" + "=" * 60)
        print("✅ Check completed!")
        print("=" * 60)
        sys.exit(0)
    except Exception as e:
        print("\n" + "=" * 60)
        print(f"❌ Check failed: {e}")
        print("=" * 60)
        sys.exit(1)
