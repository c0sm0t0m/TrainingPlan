"""
Test FIT Workout Encoder

Tests the FIT file generation functionality.
"""
import sys
from datetime import datetime, date
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from utils.fit_workout_generator import FITWorkoutEncoder, create_fit_workout_file


def test_simple_workout():
    """Test creating a simple FIT workout file."""
    print("=" * 60)
    print("Testing FIT Workout Encoder")
    print("=" * 60)
    
    encoder = FITWorkoutEncoder()
    
    # Create a simple 30-minute running workout
    workout_file = encoder.create_workout_file(
        workout_name="Test Run",
        sport_type="running",
        duration_seconds=1800,  # 30 minutes
        scheduled_date=None,  # No scheduling for now
        output_path="test_workout.fit"
    )
    
    print(f"\n✅ Created FIT workout file: {workout_file}")
    
    # Check file size
    file_size = Path(workout_file).stat().st_size
    print(f"📁 File size: {file_size} bytes")
    
    if file_size < 100:
        print("⚠️  Warning: File seems too small, might be invalid")
    else:
        print("✅ File size looks reasonable")
    
    return workout_file


def test_distance_workout():
    """Test creating a distance-based workout."""
    print("\n" + "=" * 60)
    print("Testing Distance-Based Workout")
    print("=" * 60)
    
    encoder = FITWorkoutEncoder()
    
    # Create a 5km running workout
    workout_file = encoder.create_workout_file(
        workout_name="5K Run",
        sport_type="running",
        distance_meters=5000,
        output_path="test_5k_workout.fit"
    )
    
    print(f"\n✅ Created FIT workout file: {workout_file}")
    file_size = Path(workout_file).stat().st_size
    print(f"📁 File size: {file_size} bytes")
    
    return workout_file


def test_scheduled_workout():
    """Test creating a scheduled workout."""
    print("\n" + "=" * 60)
    print("Testing Scheduled Workout")
    print("=" * 60)
    
    encoder = FITWorkoutEncoder()
    
    # Create a workout scheduled for today
    today = date.today().strftime('%Y-%m-%d')
    print(f"📅 Scheduling workout for: {today}")
    
    workout_file = encoder.create_workout_file(
        workout_name="Morning Run",
        sport_type="running",
        duration_seconds=3600,  # 60 minutes
        scheduled_date=today,
        output_path="test_scheduled_workout.fit"
    )
    
    print(f"\n✅ Created FIT workout file: {workout_file}")
    file_size = Path(workout_file).stat().st_size
    print(f"📁 File size: {file_size} bytes")
    
    return workout_file


def verify_with_decoder():
    """Try to decode the FIT file to verify it's valid."""
    print("\n" + "=" * 60)
    print("Verifying FIT File with Decoder")
    print("=" * 60)
    
    try:
        from garmin_fit_sdk import Decoder, Stream
        
        # Decode the test file
        stream = Stream.from_file("test_workout.fit")
        decoder = Decoder(stream)
        messages, errors = decoder.read()
        
        print(f"\n✅ Successfully decoded FIT file")
        print(f"📊 Found {len(messages)} messages")
        print(f"⚠️  Errors: {len(errors)}")
        
        if errors:
            print("\nErrors found:")
            for error in errors[:5]:  # Show first 5 errors
                print(f"  - {error}")
        
        # Show message types
        mesg_types = {}
        for msg_name, msg_data in messages.items():
            if isinstance(msg_data, list):
                mesg_types[msg_name] = len(msg_data)
            else:
                mesg_types[msg_name] = 1
        
        print("\nMessage summary:")
        for msg_type, count in mesg_types.items():
            print(f"  {msg_type}: {count}")
        
        return True
        
    except ImportError:
        print("❌ garmin-fit-sdk not available for decoding")
        return False
    except Exception as e:
        print(f"❌ Error decoding: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    try:
        # Test 1: Simple time-based workout
        test_simple_workout()
        
        # Test 2: Distance-based workout
        test_distance_workout()
        
        # Test 3: Scheduled workout
        test_scheduled_workout()
        
        # Test 4: Verify with decoder
        verify_with_decoder()
        
        print("\n" + "=" * 60)
        print("✅ All tests completed!")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
