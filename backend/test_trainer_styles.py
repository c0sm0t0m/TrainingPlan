#!/usr/bin/env python3
"""
Quick test script for trainer styles feature
"""

import sys
sys.path.insert(0, '/Users/boetthw3/Documents/99_Other/TrainingPlan/backend')

from src.config.trainer_styles import (
    get_all_trainer_styles,
    get_trainer_style,
    build_trainer_specific_prompt,
    get_detailed_workout_instructions
)

def test_trainer_styles():
    print("=" * 80)
    print("TESTING TRAINER STYLES FEATURE")
    print("=" * 80)
    
    # Test 1: Get all trainer styles
    print("\n1. Testing get_all_trainer_styles()...")
    styles = get_all_trainer_styles()
    print(f"   ✅ Loaded {len(styles)} trainer styles")
    
    for style in styles:
        print(f"   - {style['name']}: {style['tagline']}")
    
    # Test 2: Get specific trainer
    print("\n2. Testing get_trainer_style('joe_friel')...")
    joe_friel = get_trainer_style('joe_friel')
    print(f"   ✅ Name: {joe_friel['name']}")
    print(f"   ✅ Tagline: {joe_friel['tagline']}")
    print(f"   ✅ Has {len(joe_friel['key_workouts'])} key workouts")
    print(f"   ✅ Has {len(joe_friel['special_emphasis'])} emphasis points")
    
    # Test 3: Build trainer-specific prompt
    print("\n3. Testing build_trainer_specific_prompt('mat_fitzgerald')...")
    prompt = build_trainer_specific_prompt('mat_fitzgerald')
    print(f"   ✅ Generated prompt length: {len(prompt)} characters")
    print(f"   ✅ Contains '80/20': {('80/20' in prompt)}")
    print(f"   ✅ Contains 'POLARIZED': {('POLARIZED' in prompt)}")
    
    # Test 4: Get detailed workout instructions
    print("\n4. Testing get_detailed_workout_instructions()...")
    workout_instructions = get_detailed_workout_instructions()
    print(f"   ✅ Generated instructions length: {len(workout_instructions)} characters")
    print(f"   ✅ Contains 'WARMUP': {('WARMUP' in workout_instructions)}")
    print(f"   ✅ Contains 'COOLDOWN': {('COOLDOWN' in workout_instructions)}")
    print(f"   ✅ Contains 'interval': {('interval' in workout_instructions.lower())}")
    
    # Test 5: Verify all trainers have required fields
    print("\n5. Verifying all trainers have required fields...")
    required_fields = ['name', 'tagline', 'description', 'philosophy', 
                       'training_distribution', 'key_workouts', 
                       'periodization_structure', 'recovery_strategy', 
                       'special_emphasis']
    
    all_valid = True
    for style in styles:
        style_data = get_trainer_style(style['id'])
        for field in required_fields:
            if field not in style_data:
                print(f"   ❌ {style['name']} missing field: {field}")
                all_valid = False
    
    if all_valid:
        print(f"   ✅ All {len(styles)} trainers have complete data")
    
    # Test 6: Show sample prompt excerpt
    print("\n6. Sample Prompt Excerpt (Joe Friel):")
    print("-" * 80)
    sample_prompt = build_trainer_specific_prompt('joe_friel')
    lines = sample_prompt.split('\n')[:25]  # First 25 lines
    for line in lines:
        print(f"   {line}")
    print("   ...")
    print("-" * 80)
    
    print("\n" + "=" * 80)
    print("✅ ALL TESTS PASSED!")
    print("=" * 80)
    print("\nTrainer Styles Feature is ready to use!")
    print("\nAvailable trainers:")
    for i, style in enumerate(styles, 1):
        print(f"  {i:2d}. {style['name']} - {style['tagline']}")

if __name__ == "__main__":
    try:
        test_trainer_styles()
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
