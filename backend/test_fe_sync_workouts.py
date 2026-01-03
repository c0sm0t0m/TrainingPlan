"""
Test sync-workouts endpoint (simulating frontend call)
"""
import asyncio
import os
import sys

# Add backend to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy import text, select, and_
from datetime import date, timedelta

from src.config import settings
from src.models.user import User
from src.models.training_plan import Workout
from src.services.garmin_service import garmin_service
from src.utils.garmin_workout_converter import workout_to_garmin_instance


async def test_sync_workouts():
    """Test workout sync endpoint logic"""
    
    # Create database connection
    db_url = settings.database_url
    engine = create_async_engine(db_url, echo=False)
    async_session = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)
    
    async with async_session() as db:
        # Get test user (tboettger)
        result = await db.execute(
            text("SELECT * FROM users WHERE email = :email"),
            {"email": "tboettger@example.com"}
        )
        user_row = result.fetchone()
        
        if not user_row:
            print("❌ Test user not found")
            return
        
        # Create User object from row
        user = User(
            id=user_row.id,
            email=user_row.email,
            garmin_connected=user_row.garmin_connected,
            garmin_oauth1_token=user_row.garmin_oauth1_token,
            garmin_oauth2_token=user_row.garmin_oauth2_token,
            garmin_email=user_row.garmin_email
        )
        
        print(f"✓ Found user: {user.email}")
        print(f"  Garmin connected: {user.garmin_connected}")
        
        if not user.garmin_connected:
            print("❌ Garmin not connected")
            return
        
        # Simulate endpoint logic
        days_ahead = 14
        today = date.today()
        end_date = today + timedelta(days=days_ahead)
        
        print(f"\n📅 Looking for workouts between {today} and {end_date}")
        
        # Get upcoming workouts
        result = await db.execute(
            select(Workout).where(
                and_(
                    Workout.date >= today,
                    Workout.date <= end_date,
                    Workout.is_completed == 0
                )
            )
        )
        upcoming_workouts = result.scalars().all()
        
        print(f"✓ Found {len(upcoming_workouts)} upcoming workouts")
        
        synced = 0
        failed = 0
        skipped = 0
        scheduled = 0
        errors = []
        
        for workout in upcoming_workouts:
            print(f"\n📝 Processing: {workout.title} ({workout.date})")
            
            try:
                # Skip if already synced and not modified
                if workout.garmin_sync_status == 'synced' and workout.garmin_synced_at and workout.updated_at <= workout.garmin_synced_at:
                    print(f"  ⏩ Skipped (already synced)")
                    skipped += 1
                    continue
                
                # Convert workout to Garmin format
                workout_data = {
                    'title': workout.title,
                    'description': workout.description or '',
                    'sport_type': workout.sport_type,
                    'duration_minutes': workout.duration_minutes,
                    'distance_km': workout.distance_km,
                }
                
                print(f"  📋 Workout data: {workout_data}")
                
                # Create Garmin workout instance
                garmin_workout = workout_to_garmin_instance(workout_data)
                print(f"  ✓ Created Garmin workout instance: {type(garmin_workout).__name__}")
                
                # Format date for Garmin (YYYY-MM-DD)
                scheduled_date = workout.date.strftime('%Y-%m-%d')
                print(f"  📅 Scheduled date: {scheduled_date}")
                
                # Upload to Garmin with scheduling
                print(f"  ⬆️  Uploading to Garmin...")
                result = await garmin_service.upload_workout_to_garmin(
                    oauth1_token=user.garmin_oauth1_token,
                    oauth2_token=user.garmin_oauth2_token,
                    workout_json=garmin_workout,
                    scheduled_date=scheduled_date
                )
                
                garmin_workout_id, was_reused = result
                print(f"  ✅ Synced! Garmin Workout ID: {garmin_workout_id} (Reused: {was_reused})")
                
                # Update workout (not committing yet)
                workout.garmin_workout_id = garmin_workout_id
                workout.garmin_sync_status = 'synced'
                synced += 1
                scheduled += 1
                
            except Exception as e:
                failed += 1
                error_msg = f"Workout '{workout.title}' ({workout.date}): {str(e)}"
                errors.append(error_msg)
                print(f"  ❌ Failed: {e}")
        
        # Commit all changes
        await db.commit()
        
        # Print summary
        print("\n" + "="*60)
        print("🎯 SYNC SUMMARY")
        print("="*60)
        print(f"✅ Synced & Scheduled: {synced}")
        print(f"⏩ Skipped: {skipped}")
        print(f"❌ Failed: {failed}")
        print(f"📊 Total: {len(upcoming_workouts)}")
        
        if errors:
            print("\n❌ ERRORS:")
            for error in errors:
                print(f"  - {error}")
        
        print("\n✓ Test complete!")


if __name__ == "__main__":
    asyncio.run(test_sync_workouts())
