#!/usr/bin/env python3
"""
Test script for AI Training Plan feature
Tests prompt generation, validation, and import workflows
"""
import sys
import os

# Add backend src to Python path
backend_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(backend_dir))

import asyncio
import json
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from src.models.user import User
from src.models.event import Event
from src.models.garmin_activity import GarminActivity
from src.models.weekly_threshold import WeeklyThreshold
from src.services.ai_training_plan_service import (
    generate_ai_prompt,
    validate_training_plan,
    import_training_plan,
)
from src.api.schemas.ai_training_plan import (
    PromptGenerationConfig,
    ImportTrainingPlan,
    WorkoutStep,
)
from src.config import settings


async def setup_test_data():
    """Create test database with sample data"""
    print("Setting up test database...")
    
    # Use SQLite for testing
    engine = create_async_engine("sqlite+aiosqlite:///test_ai_plan.db", echo=False)
    
    # Create tables
    from src.database import Base
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    
    async_session = sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )
    
    async with async_session() as session:
        # Create test user
        user = User(
            email="test@example.com",
            hashed_password="dummy",
            full_name="Test Runner",
        )
        session.add(user)
        await session.flush()
        
        # Create test event
        event = Event(
            user_id=user.id,
            name="Berlin Marathon",
            event_date=datetime.now() + timedelta(days=120),
            event_type="race",
            target_distance="Marathon (42.2 km)",
            goal_time="3:30:00",
        )
        session.add(event)
        
        # Add some recent activities
        for i in range(10):
            activity = GarminActivity(
                user_id=user.id,
                garmin_activity_id=str(1000 + i),
                activity_name=f"Morning Run {i+1}",
                activity_type="running",
                start_time_local=datetime.now() - timedelta(days=i*3),
                distance=10.5,
                duration=3600,
                average_heart_rate=150,
                average_speed=2.92,  # ~5:42 min/km
                calories=700,
                avg_cadence=170,
            )
            session.add(activity)
        
        # Add weekly thresholds
        threshold = WeeklyThreshold(
            user_id=user.id,
            week_start_date=(datetime.now() - timedelta(days=7)).date(),
            week_end_date=datetime.now().date(),
            pace_threshold_seconds_per_km=240,  # 4:00 min/km
            hr_threshold_bpm=170,
            ftp_watts=250,
            calculated_at=datetime.now(),
        )
        session.add(threshold)
        
        await session.commit()
        
        print(f"✅ Created test user: {user.email} (ID: {user.id})")
        print(f"✅ Created test event: {event.name}")
        print(f"✅ Created {10} sample activities")
        print(f"✅ Created threshold data")
        
        return user.id, event.id
    
    return engine


async def test_prompt_generation(user_id: int, event_id: int):
    """Test AI prompt generation"""
    print("\n" + "="*60)
    print("TEST 1: Prompt Generation")
    print("="*60)
    
    config = PromptGenerationConfig(
        targetEventId=event_id,
        startDate=datetime.now().date(),
        trainingDaysPerWeek=5,
        preferredTrainingDays=["monday", "tuesday", "thursday", "saturday", "sunday"],
        additionalNotes="I prefer morning runs, have access to a track, avoid very long runs on weekdays",
    )
    
    # Use SQLite for testing
    engine = create_async_engine("sqlite+aiosqlite:///test_ai_plan.db", echo=False)
    async_session = sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )
    
    async with async_session() as db:
        result = await generate_ai_prompt(db, user_id, config)
        
        print(f"\n📋 Prompt Generated ({len(result['prompt'])} characters)")
        print("\nFirst 500 characters:")
        print(result["prompt"][:500])
        print("\n...")
        
        print("\n✅ Athlete Data:")
        print(f"   - Recent Activities: {len(result['athleteData']['recentActivities'])}")
        print(f"   - CTL: {result['athleteData']['trainingLoad']['ctl']}")
        print(f"   - ATL: {result['athleteData']['trainingLoad']['atl']}")
        print(f"   - TSB: {result['athleteData']['trainingLoad']['tsb']}")
        
        print("\n✅ Event Details:")
        print(f"   - Event: {result['eventDetails']['name']}")
        print(f"   - Date: {result['eventDetails']['date']}")
        print(f"   - Distance: {result['eventDetails']['distance']}")
        
        return result["prompt"]


def create_sample_training_plan():
    """Create a sample training plan JSON for testing"""
    print("\n" + "="*60)
    print("TEST 2: Creating Sample Training Plan JSON")
    print("="*60)
    
    plan = {
        "name": "12-Week Marathon Training Plan",
        "description": "Progressive build plan targeting sub-3:30 marathon finish",
        "sportType": "running",
        "startDate": datetime.now().strftime("%Y-%m-%d"),
        "endDate": (datetime.now() + timedelta(days=84)).strftime("%Y-%m-%d"),
        "targetEventId": 1,
        "workouts": []
    }
    
    # Add sample workouts for first 2 weeks
    current_date = datetime.now()
    days = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]
    
    for week in range(2):
        for day_idx, day in enumerate([0, 1, 3, 5, 6]):  # Mon, Tue, Thu, Sat, Sun
            workout_date = current_date + timedelta(days=week*7 + day)
            
            if day_idx == 4:  # Sunday long run
                workout = {
                    "date": workout_date.strftime("%Y-%m-%d"),
                    "name": f"Week {week+1} Long Run",
                    "workoutType": "long_run",
                    "description": "Easy aerobic long run",
                    "plannedDistance": 18.0 + week * 2,
                    "plannedDuration": 120 + week * 10,
                    "targetPace": "5:30-6:00/km",
                    "targetHeartRate": "145-160 bpm",
                    "estimatedTss": 85 + week * 5,
                    "steps": [
                        {
                            "stepOrder": 1,
                            "stepType": "interval",
                            "duration": 120 + week * 10,
                            "targetPace": "5:30-6:00/km",
                            "targetHeartRateZone": 2,
                            "description": "Easy aerobic pace"
                        }
                    ]
                }
            else:
                workout = {
                    "date": workout_date.strftime("%Y-%m-%d"),
                    "name": f"Week {week+1} Easy Run",
                    "workoutType": "easy",
                    "description": "Recovery/easy aerobic run",
                    "plannedDistance": 8.0 + day_idx,
                    "plannedDuration": 45 + day_idx * 5,
                    "targetPace": "5:45-6:15/km",
                    "targetHeartRate": "135-150 bpm",
                    "estimatedTss": 45 + day_idx * 5,
                    "steps": [
                        {
                            "stepOrder": 1,
                            "stepType": "interval",
                            "duration": 45 + day_idx * 5,
                            "targetPace": "5:45-6:15/km",
                            "targetHeartRateZone": 2,
                            "description": "Easy pace"
                        }
                    ]
                }
            
            plan["workouts"].append(workout)
    
    # Save to file
    filename = "sample_training_plan.json"
    with open(filename, "w") as f:
        json.dump(plan, f, indent=2)
    
    print(f"\n✅ Sample plan created: {filename}")
    print(f"   - Name: {plan['name']}")
    print(f"   - Duration: {plan['startDate']} to {plan['endDate']}")
    print(f"   - Workouts: {len(plan['workouts'])}")
    
    return filename


async def test_validation(plan_file: str):
    """Test training plan validation"""
    print("\n" + "="*60)
    print("TEST 3: Validation")
    print("="*60)
    
    with open(plan_file, "r") as f:
        plan_data = json.load(f)
    
    result = validate_training_plan(plan_data)
    
    print(f"\n✅ Validation: {'PASSED' if result['validation']['valid'] else 'FAILED'}")
    
    if result["validation"]["errors"]:
        print("\n❌ Errors:")
        for error in result["validation"]["errors"]:
            print(f"   - {error}")
    
    if result["validation"]["warnings"]:
        print("\n⚠️  Warnings:")
        for warning in result["validation"]["warnings"]:
            print(f"   - {warning}")
    
    if result["preview"]:
        preview = result["preview"]
        print(f"\n📊 Plan Preview:")
        print(f"   - Name: {preview['name']}")
        print(f"   - Duration: {preview['weeks']} weeks")
        print(f"   - Workouts: {preview['totalWorkouts']}")
        print(f"   - Distance: {preview['totalDistanceKm']:.1f} km")
        print(f"   - TSS: {preview['totalTss']}")
    
    return result


async def test_import(user_id: int, plan_file: str):
    """Test training plan import"""
    print("\n" + "="*60)
    print("TEST 4: Import")
    print("="*60)
    
    with open(plan_file, "r") as f:
        plan_data = json.load(f)
    
    # Use SQLite for testing
    engine = create_async_engine("sqlite+aiosqlite:///test_ai_plan.db", echo=False)
    async_session = sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )
    
    async with async_session() as db:
        result = await import_training_plan(db, user_id, plan_data)
        
        print(f"\n✅ Import Successful!")
        print(f"   - Plan ID: {result['planId']}")
        print(f"   - Name: {result['name']}")
        print(f"   - Workouts Created: {result['workoutsCreated']}")
        print(f"   - Message: {result['message']}")
    
    return result


async def main():
    """Run all tests"""
    print("\n🚀 AI Training Plan Feature Test Suite")
    print("="*60)
    
    try:
        # Setup
        user_id, event_id = await setup_test_data()
        
        # Test 1: Prompt generation
        prompt = await test_prompt_generation(user_id, event_id)
        
        # Test 2: Create sample plan
        plan_file = create_sample_training_plan()
        
        # Test 3: Validation
        validation_result = await test_validation(plan_file)
        
        # Test 4: Import (only if validation passed)
        if validation_result["validation"]["valid"]:
            import_result = await test_import(user_id, plan_file)
        
        print("\n" + "="*60)
        print("✅ ALL TESTS PASSED!")
        print("="*60)
        
        print("\n📝 Next Steps:")
        print("1. Copy the generated prompt to ChatGPT/Claude")
        print("2. Save the AI response as a JSON file")
        print("3. Use the frontend 'Import AI Plan' feature")
        print(f"\n💡 Sample plan file created: {plan_file}")
        print("   You can test the import with this file in the UI\n")
        
    except Exception as e:
        print(f"\n❌ Test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
