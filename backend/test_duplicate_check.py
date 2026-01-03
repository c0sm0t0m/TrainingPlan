"""
Test script to verify workout duplicate checking functionality.
"""
import asyncio
from src.services.garmin_service import garmin_service


async def test_duplicate_check():
    """Test the duplicate checking logic."""
    
    # Sample existing workouts data (simulating Garmin response)
    existing_workouts = [
        {
            'workoutId': '12345',
            'workoutName': 'Easy Run 5k',
            'sportType': {'sportTypeKey': 'running'}
        },
        {
            'workoutId': '12346',
            'workoutName': 'Tempo Run',
            'sportType': {'sportTypeKey': 'running'}
        },
        {
            'workoutId': '12347',
            'workoutName': 'Long Ride',
            'sportType': {'sportTypeKey': 'cycling'}
        }
    ]
    
    # Test 1: Exact match (should find it)
    print("\n🧪 Test 1: Exact match")
    result = garmin_service._workout_exists_in_garmin('Easy Run 5k', existing_workouts)
    print(f"   Result: {result}")
    assert result == '12345', f"Expected '12345', got {result}"
    print("   ✅ PASSED")
    
    # Test 2: Case insensitive match (should find it)
    print("\n🧪 Test 2: Case insensitive match")
    result = garmin_service._workout_exists_in_garmin('easy run 5k', existing_workouts)
    print(f"   Result: {result}")
    assert result == '12345', f"Expected '12345', got {result}"
    print("   ✅ PASSED")
    
    # Test 3: Match with whitespace differences (should find it)
    print("\n🧪 Test 3: Whitespace handling")
    result = garmin_service._workout_exists_in_garmin('  Easy Run 5k  ', existing_workouts)
    print(f"   Result: {result}")
    assert result == '12345', f"Expected '12345', got {result}"
    print("   ✅ PASSED")
    
    # Test 4: No match (should return None)
    print("\n🧪 Test 4: No match")
    result = garmin_service._workout_exists_in_garmin('Sprint Intervals', existing_workouts)
    print(f"   Result: {result}")
    assert result is None, f"Expected None, got {result}"
    print("   ✅ PASSED")
    
    # Test 5: Different sport type but same name (should still match by name)
    print("\n🧪 Test 5: Match second workout")
    result = garmin_service._workout_exists_in_garmin('Tempo Run', existing_workouts)
    print(f"   Result: {result}")
    assert result == '12346', f"Expected '12346', got {result}"
    print("   ✅ PASSED")
    
    print("\n✅ All duplicate check tests passed!")


if __name__ == '__main__':
    asyncio.run(test_duplicate_check())
