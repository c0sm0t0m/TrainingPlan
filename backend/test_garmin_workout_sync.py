#!/usr/bin/env python3
"""
Test Garmin Workout Sync

This script:
1. Creates a test workout "easy run for today" in the database
2. Syncs it to Garmin Connect
3. Verifies the sync was successful
"""
import asyncio
import sys
from datetime import date, datetime, timedelta

sys.path.insert(0, '/Users/boetthw3/Documents/99_Other/TrainingPlan/backend')

from src.database import AsyncSessionLocal, engine
from src.models.training_plan import TrainingPlan, Workout
from src.models.user import User
from src.utils.garmin_workout_converter import workout_to_garmin_instance
from src.services.garmin_service import garmin_service
from sqlalchemy import select


async def create_test_workout():
    """Create a test workout in the database."""
    async with AsyncSessionLocal() as db:
        # Get the first user (assuming tboettger@gmail.com)
        result = await db.execute(select(User).where(User.email == 'tboettger@gmail.com'))
        user = result.scalar_one_or_none()
        
        if not user:
            print("❌ User not found. Please login first.")
            return None
        
        print(f"✓ Found user: {user.email}")
        
        # Check if user has Garmin connected
        if not user.garmin_connected:
            print("❌ Garmin not connected. Please connect Garmin account first.")
            return None
        
        print(f"✓ Garmin connected")
        
        # Check if we already have a training plan, if not create one
        result = await db.execute(
            select(TrainingPlan).where(TrainingPlan.user_id == user.id)
        )
        plan = result.scalars().first()
        
        if not plan:
            print("Creating test training plan...")
            plan = TrainingPlan(
                user_id=user.id,
                name="Test Training Plan",
                description="Test plan for workout sync",
                sport_type="running",
                start_date=date.today(),
                end_date=date.today() + timedelta(days=30),
                goal="Test sync to Garmin"
            )
            db.add(plan)
            await db.commit()
            await db.refresh(plan)
            print(f"✓ Created training plan: {plan.name}")
        else:
            print(f"✓ Using existing training plan: {plan.name}")
        
        # Check if workout already exists for today
        today = date.today()
        result = await db.execute(
            select(Workout).where(
                Workout.training_plan_id == plan.id,
                Workout.date == today,
                Workout.title == "Easy run for today"
            )
        )
        existing_workout = result.scalar_one_or_none()
        
        if existing_workout:
            print(f"✓ Found existing workout: {existing_workout.title} (ID: {existing_workout.id})")
            return existing_workout.id, user
        
        # Create test workout
        print(f"Creating test workout 'Easy run for today'...")
        workout = Workout(
            training_plan_id=plan.id,
            date=today,
            sport_type="running",
            workout_type="base",
            title="Easy run for today",
            description="30 minute easy run at comfortable pace",
            duration_minutes=30,
            distance_km=5,
            intensity_zone="zone2",
            is_completed=0,
            garmin_sync_status="not_synced"
        )
        
        db.add(workout)
        await db.commit()
        await db.refresh(workout)
        
        print(f"✓ Created workout: {workout.title} (ID: {workout.id})")
        print(f"  Date: {workout.date}")
        print(f"  Duration: {workout.duration_minutes} minutes")
        print(f"  Distance: {workout.distance_km} km")
        print(f"  Sport: {workout.sport_type}")
        
        return workout.id, user


async def sync_workout_to_garmin(workout_id: int, user):
    """Sync the workout to Garmin Connect."""
    async with AsyncSessionLocal() as db:
        # Get the workout
        result = await db.execute(select(Workout).where(Workout.id == workout_id))
        workout = result.scalar_one_or_none()
        
        if not workout:
            print(f"❌ Workout {workout_id} not found")
            return False
        
        print(f"\n{'='*60}")
        print(f"Syncing workout to Garmin Connect...")
        print(f"{'='*60}")
        
        # Convert workout to Garmin format
        workout_data = {
            'title': workout.title,
            'description': workout.description,
            'sport_type': workout.sport_type,
            'duration_minutes': workout.duration_minutes,
            'distance_km': workout.distance_km,
            'workout_structure': None
        }
        
        print(f"\nWorkout data:")
        print(f"  Title: {workout_data['title']}")
        print(f"  Description: {workout_data['description']}")
        print(f"  Sport: {workout_data['sport_type']}")
        print(f"  Duration: {workout_data['duration_minutes']} min")
        print(f"  Distance: {workout_data['distance_km']} km")
        
        try:
            # Convert to Garmin workout instance
            print(f"\nConverting to Garmin workout instance...")
            garmin_workout = workout_to_garmin_instance(workout_data)
            print(f"✓ Conversion successful")
            print(f"  Garmin workout name: {garmin_workout.workoutName}")
            print(f"  Sport type: {garmin_workout.sportType}")
            print(f"  Segments: {len(garmin_workout.workoutSegments)}")
            
            # Upload to Garmin
            print(f"\nUploading to Garmin Connect...")
            garmin_workout_id, was_reused = await garmin_service.upload_workout_to_garmin(
                user.garmin_oauth1_token,
                user.garmin_oauth2_token,
                garmin_workout,
                scheduled_date=workout.date.isoformat()
            )
            
            print(f"✓ Upload successful!")
            print(f"  Garmin Workout ID: {garmin_workout_id}")
            
            # Update workout in database
            workout.garmin_workout_id = garmin_workout_id
            workout.garmin_synced_at = datetime.utcnow()
            workout.garmin_sync_status = 'synced'
            await db.commit()
            
            print(f"✓ Database updated")
            print(f"  Sync status: {workout.garmin_sync_status}")
            print(f"  Synced at: {workout.garmin_synced_at}")
            
            return True
            
        except Exception as e:
            print(f"❌ Sync failed: {str(e)}")
            import traceback
            print(traceback.format_exc())
            
            # Update status to failed
            workout.garmin_sync_status = 'failed'
            await db.commit()
            
            return False


async def verify_sync():
    """Verify the workout was synced successfully."""
    async with AsyncSessionLocal() as db:
        print(f"\n{'='*60}")
        print(f"Verifying sync in database...")
        print(f"{'='*60}\n")
        
        # Get all workouts with sync status
        result = await db.execute(
            select(Workout).where(Workout.title == "Easy run for today")
        )
        workouts = result.scalars().all()
        
        if not workouts:
            print("❌ No workouts found")
            return
        
        for workout in workouts:
            print(f"Workout: {workout.title}")
            print(f"  ID: {workout.id}")
            print(f"  Date: {workout.date}")
            print(f"  Garmin Workout ID: {workout.garmin_workout_id}")
            print(f"  Sync Status: {workout.garmin_sync_status}")
            print(f"  Synced At: {workout.garmin_synced_at}")
            print()
            
            if workout.garmin_sync_status == 'synced' and workout.garmin_workout_id:
                print("✅ Workout successfully synced to Garmin!")
                print(f"\nYou can now check your Garmin Connect calendar for today's workout:")
                print(f"https://connect.garmin.com/modern/calendar")
            elif workout.garmin_sync_status == 'failed':
                print("❌ Workout sync failed")
            else:
                print("⚠️  Workout not yet synced")


async def main():
    """Main test function."""
    print("=" * 60)
    print("Garmin Workout Sync Test")
    print("=" * 60)
    print()
    
    try:
        # Step 1: Create test workout
        result = await create_test_workout()
        if not result:
            print("\n❌ Test setup failed")
            return False
        
        workout_id, user = result
        
        # Step 2: Sync to Garmin
        success = await sync_workout_to_garmin(workout_id, user)
        
        # Step 3: Verify
        await verify_sync()
        
        # Summary
        print("\n" + "=" * 60)
        print("Test Summary")
        print("=" * 60)
        
        if success:
            print("✅ Test PASSED - Workout synced to Garmin successfully!")
            print("\nNext steps:")
            print("1. Check Garmin Connect web: https://connect.garmin.com/modern/calendar")
            print("2. Sync your Garmin device to see the workout")
            print("3. The workout should appear in today's calendar")
        else:
            print("❌ Test FAILED - See errors above")
        
        print()
        return success
        
    finally:
        # Clean up database connections
        await engine.dispose()


if __name__ == '__main__':
    import sys
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\nTest interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\nTest failed with error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    
    # Ensure clean exit
    sys.exit(0)
