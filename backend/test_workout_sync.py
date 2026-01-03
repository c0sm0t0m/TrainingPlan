#!/usr/bin/env python3
"""
Test Garmin Workout Sync

Tests syncing planned workouts to Garmin Connect.
"""
import asyncio
import sys
sys.path.insert(0, '/Users/boetthw3/Documents/99_Other/TrainingPlan/backend')

from src.database import AsyncSessionLocal
from src.models.user import User
from src.models.training_plan import Workout
from src.services.garmin_service import garmin_service
from src.utils.garmin_workout_converter import workout_to_garmin_instance
from sqlalchemy import select
from datetime import date


async def test_workout_sync():
    """Test syncing workouts scheduled for January 1st, 2026."""
    print("=" * 80)
    print("Garmin Workout Sync Test")
    print("=" * 80)
    print()
    
    async with AsyncSessionLocal() as db:
        # Get user with Garmin connected
        result = await db.execute(
            select(User).where(User.garmin_connected == 1)
        )
        user = result.scalar_one_or_none()
        
        if not user:
            print("✗ No user with Garmin connected found")
            return
        
        print(f"✓ Found user: {user.email}")
        print(f"  Garmin connected: {bool(user.garmin_connected)}")
        print()
        
        # Get workouts for today (2026-01-01)
        today = date(2026, 1, 1)
        result = await db.execute(
            select(Workout).where(Workout.date == today)
        )
        workouts = result.scalars().all()
        
        print(f"Found {len(workouts)} workout(s) for {today}:")
        for w in workouts:
            print(f"  - ID: {w.id}, Title: '{w.title}', Sport: {w.sport_type}, "
                  f"Duration: {w.duration_minutes}min, Distance: {w.distance_km}km")
            print(f"    Sync status: {w.garmin_sync_status}, Garmin ID: {w.garmin_workout_id}")
        print()
        
        if not workouts:
            print("✗ No workouts found for today")
            return
        
        # Test each workout
        for workout in workouts:
            print(f"\n{'=' * 80}")
            print(f"Testing workout: '{workout.title}'")
            print('=' * 80)
            
            # Convert to Garmin format
            workout_data = {
                'title': workout.title,
                'description': workout.description or '',
                'sport_type': workout.sport_type,
                'duration_minutes': workout.duration_minutes,
                'distance_km': workout.distance_km,
                'workout_structure': None
            }
            
            print("\n1. Converting workout to Garmin format...")
            garmin_workout = workout_to_garmin_instance(workout_data)
            
            print(f"✓ Conversion successful:")
            print(f"  Workout instance: {garmin_workout.__class__.__name__}")
            print(f"  Workout Name: {garmin_workout.workoutName}")
            print(f"  Sport Type: {garmin_workout.sportType}")
            print(f"  Estimated Duration: {garmin_workout.estimatedDurationInSecs}s")
            print(f"  Segments: {len(garmin_workout.workoutSegments)}")
            
            # Try to upload to Garmin
            print("\n2. Uploading to Garmin Connect...")
            try:
                garmin_workout_id, was_reused = await garmin_service.upload_workout_to_garmin(
                    user.garmin_oauth1_token,
                    user.garmin_oauth2_token,
                    garmin_workout,
                    scheduled_date=str(workout.date)
                )
                
                print(f"✓ Upload successful!")
                print(f"  Garmin Workout ID: {garmin_workout_id}")
                
                # Update database
                workout.garmin_workout_id = garmin_workout_id
                workout.garmin_synced_at = asyncio.get_event_loop().time()
                workout.garmin_sync_status = 'synced'
                await db.commit()
                
                print(f"✓ Database updated")
                
            except Exception as e:
                print(f"✗ Upload failed: {str(e)}")
                workout.garmin_sync_status = 'failed'
                await db.commit()
        
        print("\n" + "=" * 80)
        print("Test Complete")
        print("=" * 80)
        print()
        print("Next steps:")
        print("1. Check Garmin Connect website/app")
        print("2. Verify workouts appear in calendar")
        print("3. Sync Garmin device to see workouts offline")


if __name__ == '__main__':
    asyncio.run(test_workout_sync())
