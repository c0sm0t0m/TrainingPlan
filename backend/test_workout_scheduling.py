#!/usr/bin/env python3
"""
Test Garmin Workout Scheduling

Tests the new garth.connectapi() approach for scheduling workouts to calendar.
Based on the garmin_planner implementation.
"""
import asyncio
import sys
from datetime import date, timedelta

sys.path.insert(0, '/Users/boetthw3/Documents/99_Other/TrainingPlan/backend')

from src.database import AsyncSessionLocal, engine
from src.models.training_plan import TrainingPlan, Workout
from src.models.user import User
from src.utils.garmin_workout_converter import workout_to_garmin_instance
from src.services.garmin_service import garmin_service
from sqlalchemy import select


async def test_workout_scheduling():
    """Test creating and scheduling a workout to Garmin calendar."""
    print("=" * 60)
    print("Testing Garmin Workout Scheduling (garth.connectapi)")
    print("=" * 60)
    
    try:
        async with AsyncSessionLocal() as db:
            # Get user
            result = await db.execute(select(User).where(User.email == 'tboettger@gmail.com'))
            user = result.scalar_one_or_none()
            
            if not user:
                print("❌ User not found")
                return
            
            if not user.garmin_connected:
                print("❌ Garmin not connected")
                return
            
            print(f"✅ Found user: {user.email}")
            
            # Create test workout
            tomorrow = date.today() + timedelta(days=1)
            tomorrow_str = tomorrow.strftime('%Y-%m-%d')
            
            print(f"\n📝 Creating test workout for {tomorrow_str}...")
            
            workout_data = {
                'title': 'Scheduled Test Run',
                'description': 'Testing calendar scheduling with garth.connectapi()',
                'sport_type': 'running',
                'duration_minutes': 45,
                'scheduled_date': tomorrow_str
            }
            
            # Convert workout data to Garmin format
            garmin_workout = workout_to_garmin_instance(workout_data)
            
            # Upload to Garmin
            print(f"\n📤 Uploading and scheduling to Garmin...")
            
            workout_id, was_reused = await garmin_service.upload_workout_to_garmin(
                oauth1_token=user.garmin_oauth1_token,
                oauth2_token=user.garmin_oauth2_token,
                workout_json=garmin_workout,
                scheduled_date=tomorrow_str
            )
            
            print(f"\n🎉 Success!")
            print(f"   Workout ID: {workout_id}")
            print(f"   Scheduled: {tomorrow_str}")
            print(f"\n✅ Check Garmin Connect calendar for tomorrow!")
            print(f"   https://connect.garmin.com/modern/calendar")
            
            return workout_id
    
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        raise
    
    finally:
        await engine.dispose()


if __name__ == "__main__":
    try:
        workout_id = asyncio.run(test_workout_scheduling())
        print("\n" + "=" * 60)
        print("✅ Test completed!")
        print("=" * 60)
        sys.exit(0)
    except Exception as e:
        print("\n" + "=" * 60)
        print(f"❌ Test failed: {e}")
        print("=" * 60)
        sys.exit(1)
