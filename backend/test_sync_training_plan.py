#!/usr/bin/env python3
"""Test Training Plan Workout Sync to Garmin"""
import asyncio
import sys
from datetime import date, timedelta

sys.path.insert(0, '/Users/boetthw3/Documents/99_Other/TrainingPlan/backend')

from src.database import AsyncSessionLocal, engine
from src.models.user import User
from src.models.training_plan import TrainingPlan, Workout
from src.utils.garmin_workout_converter import workout_to_garmin_instance
from src.services.garmin_service import garmin_service
from sqlalchemy import select, and_


async def test_sync():
    """Test syncing workouts from training plan to Garmin."""
    print("=" * 60)
    print("Testing Training Plan -> Garmin Sync")
    print("=" * 60)
    
    try:
        async with AsyncSessionLocal() as db:
            # Get user
            result = await db.execute(select(User).where(User.email == 'tboettger@gmail.com'))
            user = result.scalar_one_or_none()
            
            if not user or not user.garmin_connected:
                print("❌ User not connected to Garmin")
                return
            
            print(f"✅ User: {user.email}")
            
            # Get upcoming workouts (next 7 days)
            today = date.today()
            end_date = today + timedelta(days=7)
            
            result = await db.execute(
                select(Workout).where(
                    and_(
                        Workout.date >= today,
                        Workout.date <= end_date
                    )
                ).order_by(Workout.date)
            )
            workouts = result.scalars().all()
            
            print(f"\n📋 Found {len(workouts)} workouts in next 7 days")
            
            if not workouts:
                # Create a test workout
                print("\n📝 Creating test workout...")
                plan = TrainingPlan(
                    user_id=user.id,
                    name="Test Plan",
                    start_date=today,
                    end_date=today + timedelta(days=30),
                    status="active"
                )
                db.add(plan)
                await db.flush()
                
                test_workout = Workout(
                    training_plan_id=plan.id,
                    date=today + timedelta(days=1),
                    title="Morning Run",
                    description="Easy 5K run",
                    sport_type="running",
                    duration_minutes=30,
                    distance_km=5.0,
                    is_completed=0
                )
                db.add(test_workout)
                await db.commit()
                
                workouts = [test_workout]
                print(f"✅ Created test workout for {test_workout.date}")
            
            # Sync workouts
            synced = 0
            scheduled = 0
            
            for workout in workouts:
                print(f"\n🏃 {workout.title} - {workout.date}")
                print(f"   Duration: {workout.duration_minutes} min, Distance: {workout.distance_km} km")
                
                try:
                    # Convert to Garmin format
                    workout_data = {
                        'title': workout.title,
                        'description': workout.description or '',
                        'sport_type': workout.sport_type,
                        'duration_minutes': workout.duration_minutes,
                        'distance_km': workout.distance_km,
                    }
                    
                    garmin_workout = workout_to_garmin_instance(workout_data)
                    scheduled_date = workout.date.strftime('%Y-%m-%d')
                    
                    # Upload and schedule
                    garmin_workout_id, was_reused = await garmin_service.upload_workout_to_garmin(
                        oauth1_token=user.garmin_oauth1_token,
                        oauth2_token=user.garmin_oauth2_token,
                        workout_json=garmin_workout,
                        scheduled_date=scheduled_date
                    )
                    
                    # Update DB
                    workout.garmin_workout_id = garmin_workout_id
                    workout.garmin_sync_status = 'synced'
                    
                    synced += 1
                    scheduled += 1
                    print(f"   ✅ Synced! Garmin ID: {garmin_workout_id}")
                    
                except Exception as e:
                    print(f"   ❌ Failed: {e}")
            
            await db.commit()
            
            print(f"\n{'='*60}")
            print(f"📊 Results: {synced} synced, {scheduled} scheduled")
            print(f"{'='*60}")
            print(f"\n💡 Check: https://connect.garmin.com/modern/calendar")
            
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        raise
    
    finally:
        await engine.dispose()


if __name__ == "__main__":
    try:
        asyncio.run(test_sync())
        sys.exit(0)
    except Exception:
        sys.exit(1)
