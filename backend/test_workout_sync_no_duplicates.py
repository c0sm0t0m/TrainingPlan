#!/usr/bin/env python3
"""
End-to-end test for workout sync without duplicates.

Tests that:
1. Each local workout is only uploaded to Garmin once (tracked by garmin_workout_id)
2. Same workout definition on different days creates separate Garmin workouts
3. Re-syncing the same local workout reuses the existing Garmin workout
"""
import asyncio
import sys
from datetime import datetime, timedelta
from src.services.garmin_service import garmin_service
from src.utils.garmin_workout_converter import workout_to_garmin_instance


async def test_workout_sync_no_duplicates():
    """Test complete workout sync flow with proper duplicate prevention."""
    
    print("=" * 70)
    print("🧪 Workout Sync Without Duplicates Test")
    print("=" * 70)
    print("\nThis test verifies:")
    print("- Local workouts are tracked and only uploaded once")
    print("- Same workout type on different days = different Garmin workouts")
    print("- Re-syncing uses existing Garmin workout ID")
    
    # Get credentials from environment or use test user
    import os
    from dotenv import load_dotenv
    load_dotenv()
    
    email = os.getenv('GARMIN_EMAIL', 'tboettger@gmail.com')
    password = os.getenv('GARMIN_PASSWORD')
    
    print(f"\n📧 Using account: {email}")
    
    # Initialize tokens as None
    oauth1_token = None
    oauth2_token = None
    
    # Try to get stored credentials from database if no password provided
    if not password:
        print("\n🔍 Attempting to fetch credentials from database...")
        try:
            from src.database import AsyncSessionLocal
            from src.models.user import User
            from sqlalchemy import select
            
            async with AsyncSessionLocal() as db:
                result = await db.execute(
                    select(User).where(User.email == email)
                )
                user = result.scalar_one_or_none()
                
                if user and user.garmin_oauth1_token and user.garmin_oauth2_token:
                    print(f"   ✅ Found stored tokens for {email}")
                    oauth1_token = user.garmin_oauth1_token
                    oauth2_token = user.garmin_oauth2_token
                    
                    # Test if tokens are still valid
                    is_valid = await garmin_service.test_connection(oauth1_token, oauth2_token)
                    if is_valid:
                        print("   ✅ Stored tokens are still valid, using them")
                    else:
                        print("   ⚠️  Stored tokens expired, need password")
                        password = None
                else:
                    print(f"   ⚠️  No stored tokens for {email}")
        except Exception as e:
            print(f"   ⚠️  Could not fetch from database: {e}")
    
    # Step 1: Authenticate
    print("\n[1/5] Authenticating with Garmin...")
    
    if password:
        # Login with password
        try:
            creds = await garmin_service.authenticate(email, password)
            oauth1_token = creds['oauth1_token']
            oauth2_token = creds['oauth2_token']
            print("   ✅ Authentication successful")
        except Exception as e:
            print(f"   ❌ Authentication failed: {e}")
            return False
    elif 'oauth1_token' in locals() and 'oauth2_token' in locals() and oauth1_token:
        print("   ✅ Using stored tokens from database")
    else:
        print("   ❌ No password provided and no stored tokens found")
        print("   Please either:")
        print("   1. Set GARMIN_PASSWORD in .env file")
        print("   2. Or authenticate via API first to store tokens")
        return False
    
    # Step 2: Create two test workouts (same type, different dates)
    print("\n[2/5] Creating test workouts...")
    workout_title_base = "🧪 Test Swim"
    date1 = (datetime.now() + timedelta(days=2)).strftime("%Y-%m-%d")
    date2 = (datetime.now() + timedelta(days=3)).strftime("%Y-%m-%d")
    
    workout_data = {
        'title': workout_title_base,
        'sport': 'swimming',
        'description': f'Test workout for duplicate prevention',
        'structure': {
            'warmup': {'duration_meters': 200, 'intensity': 'easy'},
            'main': [
                {'duration_meters': 400, 'intensity': 'moderate', 'repeats': 4, 'rest_seconds': 30}
            ],
            'cooldown': {'duration_meters': 200, 'intensity': 'easy'}
        }
    }
    
    try:
        workout_instance = workout_to_garmin_instance(workout_data)
        print(f"   ✅ Created workout definition: {workout_title_base}")
    except Exception as e:
        print(f"   ❌ Failed to create workout: {e}")
        return False
    
    # Step 3: Upload first workout (local_workout_id=1, no existing Garmin ID)
    print(f"\n[3/5] Upload LOCAL WORKOUT #1 for {date1}...")
    print(f"   (First time upload - should CREATE new Garmin workout)")
    try:
        workout_id_1, was_synced_1 = await garmin_service.upload_workout_to_garmin(
            oauth1_token,
            oauth2_token,
            workout_instance,
            scheduled_date=date1,
            local_workout_id=1,
            existing_garmin_workout_id=None  # First time - not synced yet
        )
        
        if was_synced_1:
            print(f"   ⚠️  Unexpected: workout marked as already synced")
        else:
            print(f"   ✅ Created NEW Garmin workout (ID: {workout_id_1})")
        
        print(f"   ✅ Scheduled to {date1}")
        print(f"   💾 Would save garmin_workout_id={workout_id_1} to local workout #1")
    except Exception as e:
        print(f"   ❌ Upload failed: {e}")
        return False
    
    # Step 4: Upload second workout (local_workout_id=2, different date)
    print(f"\n[4/5] Upload LOCAL WORKOUT #2 for {date2}...")
    print(f"   (Same workout type, different date - should CREATE new Garmin workout)")
    try:
        workout_id_2, was_synced_2 = await garmin_service.upload_workout_to_garmin(
            oauth1_token,
            oauth2_token,
            workout_instance,
            scheduled_date=date2,
            local_workout_id=2,
            existing_garmin_workout_id=None  # Different local workout
        )
        
        if was_synced_2:
            print(f"   ⚠️  Unexpected: workout marked as already synced")
        else:
            print(f"   ✅ Created NEW Garmin workout (ID: {workout_id_2})")
        
        print(f"   ✅ Scheduled to {date2}")
        print(f"   💾 Would save garmin_workout_id={workout_id_2} to local workout #2")
    except Exception as e:
        print(f"   ❌ Upload failed: {e}")
        return False
    
    # Step 5: Re-sync first workout (simulate second sync attempt)
    print(f"\n[5/5] Re-sync LOCAL WORKOUT #1...")
    print(f"   (Already uploaded - should REUSE existing Garmin workout)")
    try:
        workout_id_1_resync, was_synced_1_resync = await garmin_service.upload_workout_to_garmin(
            oauth1_token,
            oauth2_token,
            workout_instance,
            scheduled_date=date1,
            local_workout_id=1,
            existing_garmin_workout_id=workout_id_1  # Already synced!
        )
        
        if was_synced_1_resync:
            print(f"   ✅ REUSED existing Garmin workout (ID: {workout_id_1_resync})")
        else:
            print(f"   ⚠️  Created new workout instead of reusing (ID: {workout_id_1_resync})")
        
        print(f"   ✅ No duplicate created")
    except Exception as e:
        print(f"   ❌ Re-sync failed: {e}")
        return False
    
    # Verification
    print("\n" + "=" * 70)
    print("📊 Test Results")
    print("=" * 70)
    
    print(f"\n✅ LOCAL WORKOUT #1 (scheduled {date1}):")
    print(f"   - First upload: Created Garmin workout {workout_id_1}")
    print(f"   - Re-sync: Reused same Garmin workout {workout_id_1_resync}")
    print(f"   - Match: {workout_id_1 == workout_id_1_resync} ✅" if workout_id_1 == workout_id_1_resync else f"   - Match: False ⚠️")
    
    print(f"\n✅ LOCAL WORKOUT #2 (scheduled {date2}):")
    print(f"   - Created Garmin workout {workout_id_2}")
    print(f"   - Different from workout #1: {workout_id_1 != workout_id_2} ✅" if workout_id_1 != workout_id_2 else f"   - Same as workout #1 ⚠️")
    
    success = (workout_id_1 == workout_id_1_resync) and (workout_id_1 != workout_id_2)
    
    if success:
        print(f"\n✅ SUCCESS: Duplicate prevention working correctly!")
        print(f"   - Same local workout → Same Garmin workout")
        print(f"   - Different dates → Different Garmin workouts")
    else:
        print(f"\n⚠️  NOTICE: Unexpected behavior")
    
    print(f"\n📅 Check your Garmin Connect calendar:")
    print(f"   - {date1}: '{workout_title_base}' (Garmin ID: {workout_id_1})")
    print(f"   - {date2}: '{workout_title_base}' (Garmin ID: {workout_id_2})")
    
    print("\n" + "=" * 70)
    return success


if __name__ == '__main__':
    try:
        success = asyncio.run(test_workout_sync_no_duplicates())
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n⚠️  Test interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Test failed with exception: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
