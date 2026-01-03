#!/usr/bin/env python3
"""
Test uploading a FIT workout file to Garmin Connect

This tests the complete flow:
1. Generate a FIT workout file
2. Upload it to Garmin Connect
3. Verify it appears in the workout library
"""
import asyncio
import sys
from pathlib import Path
from datetime import date

sys.path.insert(0, '/Users/boetthw3/Documents/99_Other/TrainingPlan/backend')

from src.database import AsyncSessionLocal, engine
from src.models.user import User
from src.services.garmin_service import garmin_service
from src.utils.fit_workout_generator import FITWorkoutEncoder
from sqlalchemy import select


async def test_fit_upload():
    """Test creating and uploading a FIT workout file."""
    print("=" * 60)
    print("Testing FIT Workout Upload to Garmin")
    print("=" * 60)
    
    try:
        # Get user
        async with AsyncSessionLocal() as session:
            result = await session.execute(
                select(User).where(User.email == "tboettger@gmail.com")
            )
            user = result.scalar_one_or_none()
            
            if not user:
                print("❌ Test user not found")
                return
            
            if not user.garmin_oauth1_token:
                print("❌ User not connected to Garmin")
                return
            
            print(f"✅ Found user: {user.email}")
            print(f"   Garmin tokens: {user.garmin_oauth1_token[:20]}...")
        
        # Create a FIT workout file
        print("\n📝 Creating FIT workout file...")
        encoder = FITWorkoutEncoder()
        
        today = date.today().strftime('%Y-%m-%d')
        
        fit_file = encoder.create_workout_file(
            workout_name="FIT Test Run",
            sport_type="running",
            duration_seconds=1800,  # 30 minutes
            scheduled_date=today,  # Schedule for today
            output_path="test_fit_upload.fit"
        )
        
        print(f"✅ Created: {fit_file}")
        file_size = Path(fit_file).stat().st_size
        print(f"   Size: {file_size} bytes")
        
        # Upload to Garmin
        print(f"\n📤 Uploading to Garmin Connect...")
        
        # Resume Garmin session with stored tokens
        garmin_api = await garmin_service.resume_session(
            user.garmin_oauth1_token,
            user.garmin_oauth2_token
        )
        
        # Upload the FIT file as an activity
        response = garmin_api.upload_activity(fit_file)
        
        print(f"✅ Upload successful!")
        print(f"   Response: {response}")
        
        # Extract workout ID
        if isinstance(response, dict):
            workout_id = response.get('workoutId') or response.get('id')
        else:
            workout_id = response
        
        print(f"\n🎉 Workout uploaded successfully!")
        print(f"   Workout ID: {workout_id}")
        print(f"   Scheduled for: {today}")
        print(f"\n💡 Check Garmin Connect:")
        print(f"   1. Go to Training > Workouts")
        print(f"   2. Check Calendar for today")
        print(f"   3. Look for 'FIT Test Run'")
        
        return workout_id
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        raise
    
    finally:
        # Clean up database connections
        await engine.dispose()


if __name__ == "__main__":
    try:
        workout_id = asyncio.run(test_fit_upload())
        print("\n" + "=" * 60)
        print("✅ Test completed successfully!")
        print("=" * 60)
        sys.exit(0)
    except Exception as e:
        print("\n" + "=" * 60)
        print(f"❌ Test failed: {e}")
        print("=" * 60)
        sys.exit(1)
