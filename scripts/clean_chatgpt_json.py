#!/usr/bin/env python3
"""
ChatGPT JSON Cleaner - Remove markdown code fences and validate JSON

Usage:
    python clean_chatgpt_json.py input.txt output.json
    
    Or with clipboard:
    pbpaste | python clean_chatgpt_json.py - output.json  # macOS
"""

import sys
import json
import re
from pathlib import Path


def clean_chatgpt_json(text: str) -> str:
    """
    Remove markdown code fences and clean up ChatGPT response.
    
    Args:
        text: Raw text from ChatGPT (may include ```json fences)
        
    Returns:
        Cleaned JSON string
    """
    # Remove markdown code fences at start
    text = re.sub(r'^```(?:json)?\s*\n?', '', text, flags=re.MULTILINE)
    
    # Remove markdown code fences at end
    text = re.sub(r'\n?```\s*$', '', text, flags=re.MULTILINE)
    
    # Remove any leading/trailing whitespace
    text = text.strip()
    
    # If text doesn't start with {, try to find the JSON
    if not text.startswith('{'):
        # Look for first { and last }
        start = text.find('{')
        end = text.rfind('}')
        if start != -1 and end != -1:
            text = text[start:end+1]
    
    return text


def validate_training_plan_json(data: dict) -> list:
    """
    Validate training plan JSON structure.
    
    Args:
        data: Parsed JSON data
        
    Returns:
        List of validation errors (empty if valid)
    """
    errors = []
    
    # Check root structure
    if 'trainingPlan' not in data:
        errors.append("Missing 'trainingPlan' root key")
        return errors
    
    plan = data['trainingPlan']
    
    # Required fields
    required_fields = ['name', 'startDate', 'endDate', 'sportType', 'workouts']
    for field in required_fields:
        if field not in plan:
            errors.append(f"Missing required field: {field}")
    
    # Validate sportType
    valid_sports = ['running', 'cycling', 'swimming', 'triathlon', 'gym']
    if plan.get('sportType') not in valid_sports:
        errors.append(f"Invalid sportType: {plan.get('sportType')} (must be one of {valid_sports})")
    
    # Validate dates
    try:
        from datetime import datetime
        start = datetime.strptime(plan.get('startDate', ''), '%Y-%m-%d')
        end = datetime.strptime(plan.get('endDate', ''), '%Y-%m-%d')
        if end <= start:
            errors.append(f"endDate ({plan.get('endDate')}) must be after startDate ({plan.get('startDate')})")
    except ValueError as e:
        errors.append(f"Invalid date format: {e}")
    
    # Validate workouts
    workouts = plan.get('workouts', [])
    if not isinstance(workouts, list):
        errors.append("'workouts' must be an array")
    elif len(workouts) == 0:
        errors.append("'workouts' array is empty (must have at least 1 workout)")
    else:
        # Validate each workout
        valid_workout_types = ['easy', 'tempo', 'interval', 'long', 'recovery', 'race', 'brick', 'strength']
        for i, workout in enumerate(workouts):
            if not isinstance(workout, dict):
                errors.append(f"Workout {i} is not a valid object")
                continue
            
            # Required workout fields
            workout_required = ['date', 'title', 'sportType', 'workoutType']
            for field in workout_required:
                if field not in workout:
                    errors.append(f"Workout {i} missing required field: {field}")
            
            # Validate workout type
            if workout.get('workoutType') not in valid_workout_types:
                errors.append(f"Workout {i} has invalid workoutType: {workout.get('workoutType')}")
    
    return errors


def main():
    """Main entry point."""
    if len(sys.argv) < 2:
        print("Usage: python clean_chatgpt_json.py <input_file> [output_file]")
        print("\nExamples:")
        print("  python clean_chatgpt_json.py chatgpt_response.txt plan.json")
        print("  pbpaste | python clean_chatgpt_json.py - plan.json  # macOS clipboard")
        print("  cat response.txt | python clean_chatgpt_json.py - plan.json  # stdin")
        sys.exit(1)
    
    input_file = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else None
    
    # Read input
    if input_file == '-':
        print("📖 Reading from stdin...")
        text = sys.stdin.read()
    else:
        print(f"📖 Reading from {input_file}...")
        text = Path(input_file).read_text()
    
    # Clean the JSON
    print("🧹 Cleaning JSON (removing markdown fences)...")
    cleaned = clean_chatgpt_json(text)
    
    # Parse JSON
    try:
        print("✅ Parsing JSON...")
        data = json.loads(cleaned)
    except json.JSONDecodeError as e:
        print(f"❌ JSON parsing error: {e}")
        print(f"\nFirst 500 characters of cleaned text:")
        print(cleaned[:500])
        sys.exit(1)
    
    # Validate structure
    print("🔍 Validating training plan structure...")
    errors = validate_training_plan_json(data)
    
    if errors:
        print(f"\n⚠️  Found {len(errors)} validation error(s):")
        for error in errors:
            print(f"  - {error}")
        print("\n💡 Fix these errors before importing into Kinesis")
    else:
        print("✅ Validation passed!")
        
        # Print statistics
        plan = data['trainingPlan']
        workouts = plan.get('workouts', [])
        print(f"\n📊 Plan Statistics:")
        print(f"  - Name: {plan.get('name')}")
        print(f"  - Date range: {plan.get('startDate')} to {plan.get('endDate')}")
        print(f"  - Sport: {plan.get('sportType')}")
        print(f"  - Total workouts: {len(workouts)}")
        
        if workouts:
            # Count by workout type
            workout_counts = {}
            for workout in workouts:
                wtype = workout.get('workoutType', 'unknown')
                workout_counts[wtype] = workout_counts.get(wtype, 0) + 1
            
            print(f"  - Workout breakdown:")
            for wtype, count in sorted(workout_counts.items()):
                print(f"    * {wtype}: {count}")
    
    # Write output
    if output_file:
        print(f"\n💾 Writing to {output_file}...")
        Path(output_file).write_text(json.dumps(data, indent=2))
        print(f"✅ Saved to {output_file}")
        print(f"\n🎯 Ready to import! Go to Kinesis → Training Plans → Import AI Plan")
    else:
        # Print to stdout
        print("\n" + "="*60)
        print(json.dumps(data, indent=2))
        print("="*60)


if __name__ == '__main__':
    main()
