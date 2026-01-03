#!/usr/bin/env python3
"""
Verify Workout Schedule on Garmin

Checks if a specific workout is scheduled by querying the schedule details.
"""
import asyncio
import sys

sys.path.insert(0, '/Users/boetthw3/Documents/99_Other/TrainingPlan/backend')

from src.database import AsyncSessionLocal, engine
from src.models.user import User
from src.services.garmin_service import garmin_service
from sqlalchemy import select


async def verify_schedule():
    """Verify workout schedule."""
    print("=" * 60)
    print("Verifying Workout Schedule")
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
            
            # Get all workouts from library
            print(f"\n📚 Getting all workouts from library...")
            try:
                workouts = api.garth.connectapi(
                    "/workout-service/workouts",
                    method="GET",
                    params={
                        "start": 1,
                        "limit": 20,
                        "myWorkoutsOnly": True,
                        "sharedWorkoutsOnly": False,
                        "orderBy": "DATE_UPDATED",
                        "orderSeq": "DESC"
                    }
                )
                
                if workouts and isinstance(workouts, list):
                    print(f"\nFound {len(workouts)} recent workouts:")
                    for workout in workouts[:5]:  # Show first 5
                        workout_id = workout.get('workoutId')
                        workout_name = workout.get('workoutName')
                        updated = workout.get('updated', 'N/A')
                        
                        print(f"\n  🏃 {workout_name}")
                        print(f"     ID: {workout_id}")
                        print(f"     Updated: {updated}")
                        
                        # Check if this workout has a schedule
                        try:
                            schedule_check = api.garth.connectapi(
                                f"/workout-service/schedule/{workout_id}",
                                method="GET"
                            )
                            if schedule_check:
                                print(f"     📅 SCHEDULED: {schedule_check}")
                        except Exception as se:
                            # Not scheduled or can't query this way
                            pass
                else:
                    print(f"Response: {workouts}")
                    
            except Exception as e:
                print(f"Error: {e}")
                
            # Alternative: Try to get user's training calendar
            print(f"\n\n📅 Trying training calendar endpoint...")
            try:
                calendar = api.garth.connectapi(
                    "/trainingcalendar-service/calendar",
                    method="GET",
                    params={
                        "startDate": "2026-01-01",
                        "endDate": "2026-01-07"
                    }
                )
                print(f"Calendar response: {calendar}")
            except Exception as e:
                print(f"Error: {e}")
                
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        raise
    
    finally:
        await engine.dispose()


if __name__ == "__main__":
    try:
        asyncio.run(verify_schedule())
        print("\n" + "=" * 60)
        print("✅ Verification completed!")
        print("=" * 60)
        print("\n💡 Please check Garmin Connect web:")
        print("   https://connect.garmin.com/modern/calendar")
        print("   Look for date: 2026-01-02")
        sys.exit(0)
    except Exception as e:
        print("\n" + "=" * 60)
        print(f"❌ Verification failed: {e}")
        print("=" * 60)
        sys.exit(1)
