"""
Garmin Workout Converter

Converts TrainingPlan workouts to Garmin Connect workout format.

This converter creates JSON structures compatible with Garmin's Connect API,
which internally uses the FIT (Flexible and Interoperable Data Transfer) protocol.

Important Notes:
- Uses Garmin Connect HTTP API (not raw FIT files)
- IDs and structure aligned with FIT Protocol specification
- Reference: https://developer.garmin.com/fit/protocol/
- Compatible with garminconnect library v0.2.x

FIT Protocol Alignment:
- Sport Types: running=1, cycling=2, swimming=3, etc.
- Step Types: warmup=1, cooldown=2, interval=3, recovery=4, rest=5
- Condition Types: distance=1, time=2, heart_rate=3, calories=4
- Target Types: no_target=1, heart_rate=2, cadence=3, speed=4, power=5
"""
from typing import Dict, List, Optional, Any
from datetime import datetime

try:
    from garminconnect.workout import (
        RunningWorkout,
        CyclingWorkout,
        SwimmingWorkout,
        WalkingWorkout,
        WorkoutSegment,
        ExecutableStep,
        StepType,
        ConditionType,
        TargetType,
        create_warmup_step,
        create_cooldown_step,
        create_interval_step,
    )
    GARMIN_WORKOUT_CLASSES_AVAILABLE = True
except ImportError:
    GARMIN_WORKOUT_CLASSES_AVAILABLE = False


# Sport type mapping: our type -> Garmin Connect format (aligned with FIT protocol)
SPORT_TYPE_MAP = {
    'running': {'sportTypeId': 1, 'sportTypeKey': 'running', 'displayOrder': 1},
    'cycling': {'sportTypeId': 2, 'sportTypeKey': 'cycling', 'displayOrder': 2},
    'swimming': {'sportTypeId': 3, 'sportTypeKey': 'lap_swimming', 'displayOrder': 3},
    'walking': {'sportTypeId': 4, 'sportTypeKey': 'walking', 'displayOrder': 4},
    'strength': {'sportTypeId': 13, 'sportTypeKey': 'strength_training', 'displayOrder': 13},
    'other': {'sportTypeId': 1, 'sportTypeKey': 'running', 'displayOrder': 1},  # Default to running
}

# Workout step types (aligned with FIT protocol)
STEP_TYPE_MAP = {
    'warmup': {'stepTypeId': 1, 'stepTypeKey': 'warmup', 'displayOrder': 1},
    'cooldown': {'stepTypeId': 2, 'stepTypeKey': 'cooldown', 'displayOrder': 2},
    'active': {'stepTypeId': 3, 'stepTypeKey': 'interval', 'displayOrder': 3},
    'interval': {'stepTypeId': 3, 'stepTypeKey': 'interval', 'displayOrder': 3},
    'recovery': {'stepTypeId': 4, 'stepTypeKey': 'recovery', 'displayOrder': 4},
    'rest': {'stepTypeId': 5, 'stepTypeKey': 'rest', 'displayOrder': 5},
}

# Duration/end condition types (aligned with FIT protocol)
DURATION_TYPE_MAP = {
    'distance': {'conditionTypeId': 1, 'conditionTypeKey': 'distance', 'displayOrder': 1, 'displayable': True},
    'time': {'conditionTypeId': 2, 'conditionTypeKey': 'time', 'displayOrder': 2, 'displayable': True},
    'heart_rate': {'conditionTypeId': 3, 'conditionTypeKey': 'heart.rate', 'displayOrder': 3, 'displayable': True},
    'calories': {'conditionTypeId': 4, 'conditionTypeKey': 'calories', 'displayOrder': 4, 'displayable': True},
    'lap_button': {'conditionTypeId': 1, 'conditionTypeKey': 'lap.button', 'displayOrder': 1, 'displayable': True},
    'open': {'conditionTypeId': 1, 'conditionTypeKey': 'lap.button', 'displayOrder': 1, 'displayable': True},
}

# Target types (aligned with FIT protocol)
TARGET_TYPE_MAP = {
    'no_target': {'workoutTargetTypeId': 1, 'workoutTargetTypeKey': 'no.target', 'displayOrder': 1},
    'heart_rate': {'workoutTargetTypeId': 2, 'workoutTargetTypeKey': 'heart.rate.zone', 'displayOrder': 2},
    'cadence': {'workoutTargetTypeId': 3, 'workoutTargetTypeKey': 'cadence.zone', 'displayOrder': 3},
    'speed': {'workoutTargetTypeId': 4, 'workoutTargetTypeKey': 'speed.zone', 'displayOrder': 4},
    'pace': {'workoutTargetTypeId': 4, 'workoutTargetTypeKey': 'pace.zone', 'displayOrder': 4},  # Same as speed
    'power': {'workoutTargetTypeId': 5, 'workoutTargetTypeKey': 'power.zone', 'displayOrder': 5},
    'open': {'workoutTargetTypeId': 6, 'workoutTargetTypeKey': 'open', 'displayOrder': 6},
}


def workout_to_garmin_json(workout_data: Dict) -> Dict:
    """
    Convert our Workout model data to Garmin workout JSON format.
    
    Args:
        workout_data: Dictionary with workout fields (title, sport_type, duration_minutes, etc.)
        
    Returns:
        Garmin-compatible workout JSON
    """
    sport_type = workout_data.get('sport_type', 'running').lower()
    garmin_sport_type = SPORT_TYPE_MAP.get(sport_type, SPORT_TYPE_MAP['running'])
    
    # Check if we have structured workout data
    workout_structure = workout_data.get('workout_structure')
    if workout_structure and isinstance(workout_structure, dict):
        return create_structured_workout(workout_data, garmin_sport_type)
    else:
        return create_simple_workout(workout_data, garmin_sport_type)


def create_simple_workout(workout_data: Dict, garmin_sport_type: Dict) -> Dict:
    """
    Create a simple workout (single goal: time or distance).
    
    Args:
        workout_data: Workout data from our model
        garmin_sport_type: Garmin sport type dict
        
    Returns:
        Garmin workout JSON
    """
    title = workout_data.get('title', 'Workout')
    description = workout_data.get('description', '')
    duration_minutes = workout_data.get('duration_minutes')
    distance_km = workout_data.get('distance_km')
    
    # Determine workout goal
    steps = []
    step_order = 1
    
    if duration_minutes:
        # Time-based workout
        steps.append({
            'type': 'ExecutableStepDTO',
            'stepId': None,
            'stepOrder': step_order,
            'stepType': STEP_TYPE_MAP['active'],
            'endCondition': DURATION_TYPE_MAP['time'],
            'endConditionValue': duration_minutes * 60,  # Convert to seconds
            'targetType': TARGET_TYPE_MAP['no_target'],
            'targetValueOne': None,
            'targetValueTwo': None,
        })
    elif distance_km:
        # Distance-based workout
        steps.append({
            'type': 'ExecutableStepDTO',
            'stepId': None,
            'stepOrder': step_order,
            'stepType': STEP_TYPE_MAP['active'],
            'endCondition': DURATION_TYPE_MAP['distance'],
            'endConditionValue': distance_km * 1000,  # Convert to meters
            'targetType': TARGET_TYPE_MAP['no_target'],
            'targetValueOne': None,
            'targetValueTwo': None,
        })
    else:
        # Open workout (press lap button to complete)
        steps.append({
            'type': 'ExecutableStepDTO',
            'stepId': None,
            'stepOrder': step_order,
            'stepType': STEP_TYPE_MAP['active'],
            'endCondition': DURATION_TYPE_MAP['lap_button'],
            'endConditionValue': None,
            'targetType': TARGET_TYPE_MAP['no_target'],
            'targetValueOne': None,
            'targetValueTwo': None,
        })
    
    return {
        'workoutName': title,
        'description': description,
        'sportType': garmin_sport_type,
        'workoutSegments': [
            {
                'segmentOrder': 1,
                'sportType': garmin_sport_type,
                'workoutSteps': steps
            }
        ]
    }


def create_structured_workout(workout_data: Dict, garmin_sport_type: Dict) -> Dict:
    """
    Create a structured workout with intervals, warmup, cooldown, etc.
    
    Args:
        workout_data: Workout data with workout_structure field
        garmin_sport_type: Garmin sport type dict
        
    Returns:
        Garmin workout JSON with structured steps
    """
    title = workout_data.get('title', 'Structured Workout')
    description = workout_data.get('description', '')
    structure = workout_data.get('workout_structure', {})
    
    steps = []
    step_order = 1
    
    # Process workout structure
    # Expected structure format:
    # {
    #   'warmup': {'duration_minutes': 10, 'intensity': 'easy'},
    #   'intervals': [
    #     {'duration_minutes': 5, 'intensity': 'hard', 'recovery_minutes': 2, 'repeats': 5}
    #   ],
    #   'cooldown': {'duration_minutes': 10, 'intensity': 'easy'}
    # }
    
    # Add warmup if present
    if 'warmup' in structure:
        warmup = structure['warmup']
        duration_minutes = warmup.get('duration_minutes', 10)
        steps.append({
            'type': 'ExecutableStepDTO',
            'stepId': None,
            'stepOrder': step_order,
            'stepType': STEP_TYPE_MAP['warmup'],
            'endCondition': DURATION_TYPE_MAP['time'],
            'endConditionValue': duration_minutes * 60,
            'targetType': TARGET_TYPE_MAP['no_target'],
            'targetValueOne': None,
            'targetValueTwo': None,
        })
        step_order += 1
    
    # Add intervals if present
    if 'intervals' in structure and isinstance(structure['intervals'], list):
        for interval_set in structure['intervals']:
            repeats = interval_set.get('repeats', 1)
            work_minutes = interval_set.get('duration_minutes', 5)
            recovery_minutes = interval_set.get('recovery_minutes', 2)
            
            # Create repeat step
            repeat_steps = []
            
            # Work interval
            repeat_steps.append({
                'type': 'ExecutableStepDTO',
                'stepId': None,
                'stepOrder': 1,
                'stepType': STEP_TYPE_MAP['active'],
                'endCondition': DURATION_TYPE_MAP['time'],
                'endConditionValue': work_minutes * 60,
                'targetType': TARGET_TYPE_MAP['no_target'],
                'targetValueOne': None,
                'targetValueTwo': None,
            })
            
            # Recovery interval
            if recovery_minutes > 0:
                repeat_steps.append({
                    'type': 'ExecutableStepDTO',
                    'stepId': None,
                    'stepOrder': 2,
                    'stepType': STEP_TYPE_MAP['recovery'],
                    'endCondition': DURATION_TYPE_MAP['time'],
                    'endConditionValue': recovery_minutes * 60,
                    'targetType': TARGET_TYPE_MAP['no_target'],
                    'targetValueOne': None,
                    'targetValueTwo': None,
                })
            
            # Add repeat group
            steps.append({
                'type': 'RepeatGroupDTO',
                'stepId': None,
                'stepOrder': step_order,
                'numberOfIterations': repeats,
                'smartRepeat': False,
                'workoutSteps': repeat_steps
            })
            step_order += 1
    
    # Add main activity if no intervals (fallback to simple workout)
    if 'intervals' not in structure:
        duration_minutes = structure.get('duration_minutes') or workout_data.get('duration_minutes')
        if duration_minutes:
            steps.append({
                'type': 'ExecutableStepDTO',
                'stepId': None,
                'stepOrder': step_order,
                'stepType': STEP_TYPE_MAP['active'],
                'endCondition': DURATION_TYPE_MAP['time'],
                'endConditionValue': duration_minutes * 60,
                'targetType': TARGET_TYPE_MAP['no_target'],
                'targetValueOne': None,
                'targetValueTwo': None,
            })
            step_order += 1
    
    # Add cooldown if present
    if 'cooldown' in structure:
        cooldown = structure['cooldown']
        duration_minutes = cooldown.get('duration_minutes', 10)
        steps.append({
            'type': 'ExecutableStepDTO',
            'stepId': None,
            'stepOrder': step_order,
            'stepType': STEP_TYPE_MAP['cooldown'],
            'endCondition': DURATION_TYPE_MAP['time'],
            'endConditionValue': duration_minutes * 60,
            'targetType': TARGET_TYPE_MAP['no_target'],
            'targetValueOne': None,
            'targetValueTwo': None,
        })
        step_order += 1
    
    return {
        'workoutName': title,
        'description': description,
        'sportType': garmin_sport_type,
        'workoutSegments': [
            {
                'segmentOrder': 1,
                'sportType': garmin_sport_type,
                'workoutSteps': steps
            }
        ]
    }


def format_workout_date(date_obj) -> str:
    """
    Format workout date for Garmin API.
    
    Args:
        date_obj: datetime.date or datetime.datetime object
        
    Returns:
        ISO format date string (YYYY-MM-DD)
    """
    if isinstance(date_obj, datetime):
        return date_obj.date().isoformat()
    return date_obj.isoformat()


def workout_to_garmin_instance(workout_data: Dict) -> Any:
    """
    Convert our Workout model data to Garmin workout instance (RunningWorkout, CyclingWorkout, etc.).
    
    This is the preferred method for uploading workouts to Garmin as it uses the typed workout classes
    from the garminconnect library.
    
    Args:
        workout_data: Dictionary with workout fields (title, sport_type, duration_minutes, etc.)
        
    Returns:
        Garmin workout instance (RunningWorkout, CyclingWorkout, SwimmingWorkout, or WalkingWorkout)
        
    Raises:
        ImportError: If garminconnect workout classes are not available
        ValueError: If sport type is not supported
    """
    if not GARMIN_WORKOUT_CLASSES_AVAILABLE:
        raise ImportError("garminconnect workout classes not available. Please update garminconnect library.")
    
    sport_type = workout_data.get('sport_type', 'running').lower()
    title = workout_data.get('title', 'Workout')
    description = workout_data.get('description', '')
    duration_minutes = workout_data.get('duration_minutes')
    distance_km = workout_data.get('distance_km')
    
    # Get Garmin sport type config
    garmin_sport_type = SPORT_TYPE_MAP.get(sport_type, SPORT_TYPE_MAP['running'])
    
    # Create workout steps
    workout_steps = []
    
    # Check if we have structured workout data
    workout_structure = workout_data.get('workout_structure')
    if workout_structure and isinstance(workout_structure, dict):
        workout_steps = _create_structured_steps(workout_structure, duration_minutes, distance_km)
    else:
        workout_steps = _create_simple_steps(duration_minutes, distance_km)
    
    # Calculate estimated duration
    estimated_duration = _calculate_estimated_duration(workout_steps, duration_minutes, distance_km)
    
    # Create workout segment
    segment = WorkoutSegment(
        segmentOrder=1,
        sportType=garmin_sport_type,
        workoutSteps=workout_steps
    )
    
    # Select appropriate workout class based on sport type
    workout_class_map = {
        'running': RunningWorkout,
        'cycling': CyclingWorkout,
        'swimming': SwimmingWorkout,
        'lap_swimming': SwimmingWorkout,
        'walking': WalkingWorkout,
    }
    
    WorkoutClass = workout_class_map.get(sport_type, RunningWorkout)
    
    # Create and return workout instance
    return WorkoutClass(
        workoutName=title,
        description=description,
        sportType=garmin_sport_type,
        estimatedDurationInSecs=estimated_duration,
        workoutSegments=[segment]
    )


def _create_simple_steps(duration_minutes: Optional[float], distance_km: Optional[float]) -> List[Any]:
    """
    Create simple workout steps (single activity).
    
    Args:
        duration_minutes: Duration in minutes
        distance_km: Distance in kilometers
        
    Returns:
        List of workout steps
    """
    steps = []
    
    if duration_minutes:
        # Time-based workout - create a single interval step
        steps.append(ExecutableStep(
            stepOrder=1,
            stepType={
                "stepTypeId": StepType.INTERVAL,
                "stepTypeKey": "interval",
                "displayOrder": 3,
            },
            endCondition={
                "conditionTypeId": ConditionType.TIME,
                "conditionTypeKey": "time",
                "displayOrder": 2,
                "displayable": True,
            },
            endConditionValue=duration_minutes * 60,  # Convert to seconds
            targetType={
                "workoutTargetTypeId": TargetType.NO_TARGET,
                "workoutTargetTypeKey": "no.target",
                "displayOrder": 1,
            },
        ))
    elif distance_km:
        # Distance-based workout
        steps.append(ExecutableStep(
            stepOrder=1,
            stepType={
                "stepTypeId": StepType.INTERVAL,
                "stepTypeKey": "interval",
                "displayOrder": 3,
            },
            endCondition={
                "conditionTypeId": ConditionType.DISTANCE,
                "conditionTypeKey": "distance",
                "displayOrder": 1,
                "displayable": True,
            },
            endConditionValue=distance_km * 1000,  # Convert to meters
            targetType={
                "workoutTargetTypeId": TargetType.NO_TARGET,
                "workoutTargetTypeKey": "no.target",
                "displayOrder": 1,
            },
        ))
    else:
        # Open workout - 30 minute default
        steps.append(ExecutableStep(
            stepOrder=1,
            stepType={
                "stepTypeId": StepType.INTERVAL,
                "stepTypeKey": "interval",
                "displayOrder": 3,
            },
            endCondition={
                "conditionTypeId": ConditionType.TIME,
                "conditionTypeKey": "time",
                "displayOrder": 2,
                "displayable": True,
            },
            endConditionValue=1800,
            targetType={
                "workoutTargetTypeId": TargetType.NO_TARGET,
                "workoutTargetTypeKey": "no.target",
                "displayOrder": 1,
            },
        ))
    
    return steps


def _create_structured_steps(structure: Dict, duration_minutes: Optional[float], distance_km: Optional[float]) -> List[Any]:
    """
    Create structured workout steps with intervals, warmup, cooldown, etc.
    
    Args:
        structure: Workout structure dictionary
        duration_minutes: Fallback duration in minutes
        distance_km: Fallback distance in kilometers
        
    Returns:
        List of workout steps
    """
    steps = []
    step_order = 1
    
    # Add warmup if present
    if 'warmup' in structure:
        warmup = structure['warmup']
        warmup_minutes = warmup.get('duration_minutes', 10)
        steps.append(create_warmup_step(warmup_minutes * 60, step_order))
        step_order += 1
    
    # Add intervals if present
    if 'intervals' in structure and isinstance(structure['intervals'], list):
        for interval_set in structure['intervals']:
            work_minutes = interval_set.get('duration_minutes', 5)
            recovery_minutes = interval_set.get('recovery_minutes', 2)
            repeats = interval_set.get('repeats', 1)
            
            # Create work interval and recovery
            for _ in range(repeats):
                steps.append(create_interval_step(work_minutes * 60, step_order))
                step_order += 1
                if recovery_minutes > 0:
                    steps.append(ExecutableStep(
                        stepOrder=step_order,
                        stepType={
                            "stepTypeId": StepType.RECOVERY,
                            "stepTypeKey": "recovery",
                            "displayOrder": 4,
                        },
                        endCondition={
                            "conditionTypeId": ConditionType.TIME,
                            "conditionTypeKey": "time",
                            "displayOrder": 2,
                            "displayable": True,
                        },
                        endConditionValue=recovery_minutes * 60,
                        targetType={
                            "workoutTargetTypeId": TargetType.NO_TARGET,
                            "workoutTargetTypeKey": "no.target",
                            "displayOrder": 1,
                        },
                    ))
                    step_order += 1
    
    # Add main activity if no intervals
    elif duration_minutes or distance_km:
        if duration_minutes:
            steps.append(ExecutableStep(
                stepOrder=step_order,
                stepType={
                    "stepTypeId": StepType.INTERVAL,
                    "stepTypeKey": "interval",
                    "displayOrder": 3,
                },
                endCondition={
                    "conditionTypeId": ConditionType.TIME,
                    "conditionTypeKey": "time",
                    "displayOrder": 2,
                    "displayable": True,
                },
                endConditionValue=duration_minutes * 60,
                targetType={
                    "workoutTargetTypeId": TargetType.NO_TARGET,
                    "workoutTargetTypeKey": "no.target",
                    "displayOrder": 1,
                },
            ))
            step_order += 1
        elif distance_km:
            steps.append(ExecutableStep(
                stepOrder=step_order,
                stepType={
                    "stepTypeId": StepType.INTERVAL,
                    "stepTypeKey": "interval",
                    "displayOrder": 3,
                },
                endCondition={
                    "conditionTypeId": ConditionType.DISTANCE,
                    "conditionTypeKey": "distance",
                    "displayOrder": 1,
                    "displayable": True,
                },
                endConditionValue=distance_km * 1000,
                targetType={
                    "workoutTargetTypeId": TargetType.NO_TARGET,
                    "workoutTargetTypeKey": "no.target",
                    "displayOrder": 1,
                },
            ))
            step_order += 1
    
    # Add cooldown if present
    if 'cooldown' in structure:
        cooldown = structure['cooldown']
        cooldown_minutes = cooldown.get('duration_minutes', 10)
        steps.append(create_cooldown_step(cooldown_minutes * 60, step_order))
        step_order += 1
    
    return steps


def _calculate_estimated_duration(steps: List[Any], duration_minutes: Optional[float], distance_km: Optional[float]) -> int:
    """
    Calculate estimated workout duration in seconds.
    
    Args:
        steps: List of workout steps
        duration_minutes: Duration in minutes
        distance_km: Distance in kilometers
        
    Returns:
        Estimated duration in seconds
    """
    # Try to calculate from duration_minutes first
    if duration_minutes:
        return int(duration_minutes * 60)
    
    # Estimate from distance (assuming 5 min/km for running)
    if distance_km:
        return int(distance_km * 5 * 60)
    
    # Default to 30 minutes
    return 1800
