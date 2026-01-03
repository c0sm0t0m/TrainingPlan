#!/usr/bin/env python3
"""
Test Calendar-Based Duplicate Detection

Tests the new duplicate prevention logic that checks Garmin calendar
for existing workouts on specific dates.

Extended to test via API endpoints with database workouts.
"""
import asyncio
import sys
import httpx
from datetime import date, timedelta, datetime

sys.path.insert(0, '/Users/boetthw3/Documents/99_Other/TrainingPlan/backend')

from src.database import AsyncSessionLocal
from src.models.user import User
from src.models.training_plan import TrainingPlan, Workout
from src.services.garmin_service import garmin_service
from src.utils.garmin_workout_converter import workout_to_garmin_instance
from sqlalchemy import select, delete

# Test credentials
TEST_EMAIL = "tboettger@gmail.com"
TEST_PASSWORD = "test123"


async def test_sync_scheduled_workouts():
    """
    Test syncing scheduled workouts from Garmin Connect.
    
    Uses the new /garmin/sync endpoint that fetches both:
    - Completed activities (existing functionality)
    - Scheduled workouts (new functionality)
    
    This will import workouts from your Garmin calendar into the database.
    """
    print("\n" + "=" * 70)
    print("Test: Sync Scheduled Workouts from Garmin")
    print("=" * 70)
    
    # Check if server is running
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get("http://localhost:8000/health")
            if response.status_code != 200:
                print("⚠️  Backend server not healthy, skipping test")
                print("   Start server with: cd backend && uvicorn src.main:app --reload")
                return
    except Exception:
        print("⚠️  Backend server not running, skipping test")
        print("   Start server with: cd backend && uvicorn src.main:app --reload")
        return
    
    async with AsyncSessionLocal() as db:
        # Step 1: Get user
        result = await db.execute(select(User).where(User.email == 'tboettger@gmail.com'))
    print("\n📋 Step 1: Login to get auth token")
    async with httpx.AsyncClient(timeout=30.0) as client:
        # Login first to get token
        login_response = await client.post(
            "http://localhost:8000/api/v1/auth/login",
            data={
                "username": TEST_EMAIL,
                "password": TEST_PASSWORD
            }
        )
        
        if login_response.status_code != 200:
            print(f"❌ Login failed: {login_response.status_code}")
            print(f"   Response: {login_response.text}")
            return
        
        token_data = login_response.json()
        access_token = token_data.get("access_token")
        print(f"✅ Login successful")
        
        # Get current database state
        async with AsyncSessionLocal() as db:
            result = await db.execute(select(User).where(User.email == TEST_EMAIL))
            user = result.scalar_one_or_none()
            
            if not user or not user.garmin_connected:
                print("❌ User not connected to Garmin")
                return
            
            # Count existing workouts BEFORE sync
            result = await db.execute(
                select(Workout)
                .join(TrainingPlan)
                .where(TrainingPlan.user_id == user.id)
            )
            workouts_before = result.scalars().all()
            print(f"\n📊 Database state BEFORE sync:")
            print(f"   Workouts in database: {len(workouts_before)}")
            
            # Count how many have garmin_workout_id
            synced_before = sum(1 for w in workouts_before if w.garmin_workout_id)
            print(f"   Already synced from Garmin: {synced_before}")
        
        # Call sync endpoint for completed activities
        print(f"\n📤 Step 2: Call /garmin/sync-activities endpoint (TEMPORARY TEST)")
        print(f"   This will:")
        print(f"   - Fetch completed activities (past 30 days)")
        print(f"   - Import them into database")
        
        sync_response = await client.post(
            "http://localhost:8000/api/v1/garmin/sync-activities",
            headers={"Authorization": f"Bearer {access_token}"},
            json={"days": 30}
        )
        
        if sync_response.status_code != 200:
            print(f"❌ Sync failed: {sync_response.status_code}")
            print(f"   Response: {sync_response.text}")
            return
        
        sync_data = sync_response.json()
        
        # Display results
        print(f"\n✅ Sync completed successfully!")
        print(f"\n📊 Results:")
        print(f"   Message: {sync_data.get('message')}")
        
        print(f"\n   🏃 Activities:")
        print(f"      Found: {sync_data.get('activities_found', 0)}")
        print(f"      New: {sync_data.get('new_activities', 0)}")
        print(f"      Updated: {sync_data.get('updated_activities', 0)}")
        print(f"      Failed: {sync_data.get('failed_activities', 0)}")
        
        # Show errors if any
        if 'errors' in sync_data:
            print(f"\n   ⚠️  Errors:")
            for error in sync_data['errors'][:5]:  # Show first 5
                print(f"      - {error}")
        
        # Get updated database state
        async with AsyncSessionLocal() as db:
            result = await db.execute(select(User).where(User.email == TEST_EMAIL))
            user = result.scalar_one_or_none()
            
            # Check activities table
            from src.models.garmin_activity import GarminActivity
            result = await db.execute(
                select(GarminActivity)
                .where(GarminActivity.user_id == user.id)
                .order_by(GarminActivity.start_time_local.desc())
            )
            activities = result.scalars().all()
            
            print(f"\n📊 Database state AFTER sync:")
            print(f"   Total activities in database: {len(activities)}")
            
            if activities and len(activities) <= 10:
                print(f"\n   Recent activities:")
                for a in activities[:10]:
                    print(f"      - {a.start_time_local}: {a.activity_name} ({a.activity_type})")
            elif activities:
                print(f"\n   Showing first 5 activities:")
                for a in activities[:5]:
                    print(f"      - {a.start_time_local}: {a.activity_name} ({a.activity_type})")
                print(f"      ... and {len(activities) - 5} more")
        
        # Now search for activities matching workout dates
        print(f"\n{'='*70}")
        print("Step 3: Match workouts with activities by date")
        print(f"{'='*70}")
        
        async with AsyncSessionLocal() as db:
            result = await db.execute(select(User).where(User.email == TEST_EMAIL))
            user = result.scalar_one_or_none()
            
            # Get user's workouts
            result = await db.execute(
                select(Workout)
                .join(TrainingPlan)
                .where(TrainingPlan.user_id == user.id)
                .order_by(Workout.date)
            )
            workouts = result.scalars().all()
            
            if not workouts:
                print("   No workouts found in database")
                return
            
            print(f"\n   Found {len(workouts)} workouts to check")
            
            # Get all activities from DB for matching
            result = await db.execute(
                select(GarminActivity)
                .where(GarminActivity.user_id == user.id)
                .order_by(GarminActivity.start_time_local)
            )
            all_activities = result.scalars().all()
            
            # Create date index for quick lookup
            activities_by_date = {}
            for activity in all_activities:
                if activity.start_time_local:
                    activity_date = activity.start_time_local.date()
                    if activity_date not in activities_by_date:
                        activities_by_date[activity_date] = []
                    activities_by_date[activity_date].append(activity)
            
            print(f"\n   Checking workouts against activities...")
            matched_count = 0
            unmatched_count = 0
            
            for i, workout in enumerate(workouts[:10], 1):  # Check first 10 workouts
                workout_date = workout.date
                print(f"\n   Workout {i}: {workout.title}")
                print(f"      Date: {workout_date}")
                print(f"      Sport: {workout.sport_type}")
                
                # Find activities on this date
                matching_activities = activities_by_date.get(workout_date, [])
                
                if matching_activities:
                    print(f"      ✅ Found {len(matching_activities)} activity(ies) on this date:")
                    for act in matching_activities:
                        print(f"         - {act.activity_name} ({act.activity_type}) at {act.start_time_local.strftime('%H:%M')}")
                    matched_count += 1
                else:
                    print(f"      ❌ No activities found on this date")
                    unmatched_count += 1
            
            print(f"\n{'='*70}")
            print(f"   Summary:")
            print(f"   Workouts checked: {min(len(workouts), 10)}")
            print(f"   Matched with activities: {matched_count}")
            print(f"   No matching activities: {unmatched_count}")
            print(f"{'='*70}")


async def test_duplicate_check():
    print("=" * 70)
    
    async with AsyncSessionLocal() as db:
        # Get user
        result = await db.execute(select(User).where(User.email == 'tboettger@gmail.com'))
        user = result.scalar_one_or_none()
        
        if not user or not user.garmin_connected:
            print("❌ User not found or Garmin not connected")
            return
        
        print(f"✅ User: {user.email}")
        print(f"✅ Garmin connected: {user.garmin_connected}")
        
        # Test 1: Check calendar for today
        today = date.today()
        print(f"\n{'='*70}")
        print(f"Test 1: Check calendar for {today}")
        print(f"{'='*70}")
        
        scheduled_today = await garmin_service.get_scheduled_workouts_for_date(
            user.garmin_oauth1_token,
            user.garmin_oauth2_token,
            today.strftime('%Y-%m-%d')
        )
        
        if scheduled_today:
            print(f"📅 Found {len(scheduled_today)} workout(s) scheduled:")
            for workout in scheduled_today:
                print(f"  - {workout['workoutName']} (ID: {workout['workoutId']})")
        else:
            print("📅 No workouts scheduled for today")
        
        # Test 2: Try to upload a test workout
        test_date = today + timedelta(days=1)
        test_date_str = test_date.strftime('%Y-%m-%d')
        
        print(f"\n{'='*70}")
        print(f"Test 2: Upload test workout for {test_date}")
        print(f"{'='*70}")
        
        test_workout = {
            'title': 'Test Duplicate Check - Easy Run',
            'description': 'Testing calendar-based duplicate detection',
            'sport_type': 'running',
            'duration_minutes': 30,
            'distance_km': 5.0
        }
        
        # Check if workout already exists
        print(f"\n🔍 Checking if workout exists on {test_date_str}...")
        scheduled_test_date = await garmin_service.get_scheduled_workouts_for_date(
            user.garmin_oauth1_token,
            user.garmin_oauth2_token,
            test_date_str
        )
        
        if scheduled_test_date:
            print(f"📅 Found {len(scheduled_test_date)} workout(s) on {test_date}:")
            for workout in scheduled_test_date:
                print(f"  - {workout['workoutName']} (ID: {workout['workoutId']})")
        else:
            print(f"📅 No workouts found on {test_date}")
        
        # Convert to Garmin format
        garmin_workout = workout_to_garmin_instance(test_workout)
        
        # First upload (should create new workout)
        print(f"\n📤 First upload attempt...")
        try:
            workout_id1, was_duplicate1 = await garmin_service.upload_workout_to_garmin(
                oauth1_token=user.garmin_oauth1_token,
                oauth2_token=user.garmin_oauth2_token,
                workout_json=garmin_workout,
                workout_title=test_workout['title'],
                scheduled_date=test_date_str
            )
            
            if was_duplicate1:
                print(f"✅ First attempt: Workout already exists (ID: {workout_id1})")
                print(f"   This is expected if you ran this test before")
            else:
                print(f"✅ First attempt: New workout created (ID: {workout_id1})")
            
            # Second upload (should detect duplicate)
            print(f"\n📤 Second upload attempt (should detect duplicate)...")
            workout_id2, was_duplicate2 = await garmin_service.upload_workout_to_garmin(
                oauth1_token=user.garmin_oauth1_token,
                oauth2_token=user.garmin_oauth2_token,
                workout_json=garmin_workout,
                workout_title=test_workout['title'],
                scheduled_date=test_date_str
            )
            
            if was_duplicate2:
                print(f"✅ Second attempt: Duplicate detected correctly! (ID: {workout_id2})")
                print(f"   Same ID as first upload: {workout_id1 == workout_id2}")
            else:
                print(f"❌ Second attempt: Should have detected duplicate but didn't")
                print(f"   New workout ID: {workout_id2}")
            
            # Test 3: Different date, same title (should NOT detect duplicate)
            different_date = today + timedelta(days=2)
            different_date_str = different_date.strftime('%Y-%m-%d')
            
            print(f"\n{'='*70}")
            print(f"Test 3: Same workout title, different date ({different_date})")
            print(f"{'='*70}")
            
            print(f"\n📤 Upload to {different_date} (should create new workout)...")
            workout_id3, was_duplicate3 = await garmin_service.upload_workout_to_garmin(
                oauth1_token=user.garmin_oauth1_token,
                oauth2_token=user.garmin_oauth2_token,
                workout_json=garmin_workout,
                workout_title=test_workout['title'],
                scheduled_date=different_date_str
            )
            
            if not was_duplicate3:
                print(f"✅ Different date: New workout created correctly (ID: {workout_id3})")
            else:
                print(f"❌ Different date: Should NOT have detected duplicate")
                print(f"   Workout ID: {workout_id3}")
            
            # Summary
            print(f"\n{'='*70}")
            print("Test Summary")
            print(f"{'='*70}")
            print(f"Test 1 - First upload: {'✅ PASS' if not was_duplicate1 else '✅ PASS (already existed)'}")
            print(f"Test 2 - Duplicate detection: {'✅ PASS' if was_duplicate2 else '❌ FAIL'}")
            print(f"Test 3 - Different date: {'✅ PASS' if not was_duplicate3 else '❌ FAIL'}")
            
            print(f"\n💡 Note: You can check Garmin Connect calendar to verify:")
            print(f"   {test_date}: Should have 1 workout")
            print(f"   {different_date}: Should have 1 workout")
            print(f"   Both with title: '{test_workout['title']}'")
            
        except Exception as e:
            print(f"❌ Error during test: {str(e)}")
            import traceback
            traceback.print_exc()


async def main():
    """Run all tests."""
    try:
        # Test syncing scheduled workouts from Garmin
        await test_sync_scheduled_workouts()
        
        print("\n" + "=" * 70)
        print("Test Complete!")
        print("=" * 70)
        print("\n💡 Next steps:")
        print("   1. Check your 'Garmin Synced Workouts' training plan in the database")
        print("   2. Verify workouts have garmin_workout_id populated")
        print("   3. Run sync again to test duplicate detection")
        
    except Exception as e:
        print(f"\n❌ Test suite failed: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())

