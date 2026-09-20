"""
AI Training Plan Import Service
"""
import json
from datetime import date, timedelta
from typing import Dict, List, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from src.models.training_plan import TrainingPlan, Workout
from src.models.garmin_activity import GarminActivity
from src.models.weekly_threshold import WeeklyThreshold
from src.api.schemas.ai_training_plan import (
    TrainingPlanImport,
    ValidationResult,
    PlanPreview,
    ImportResponse
)
from src.trainer_config.trainer_styles import (
    build_trainer_specific_prompt,
    get_detailed_workout_instructions
)


def validate_training_plan(plan_data: TrainingPlanImport) -> ValidationResult:
    """
    Validate imported training plan data.
    
    Args:
        plan_data: Parsed training plan data
        
    Returns:
        ValidationResult with any errors or warnings
    """
    errors = []
    warnings = []
    
    plan = plan_data.training_plan
    
    # Check date range
    if plan.end_date <= plan.start_date:
        errors.append("End date must be after start date")
    
    # Check plan duration (reasonable limits)
    duration_days = (plan.end_date - plan.start_date).days
    if duration_days < 7:
        warnings.append("Plan duration is less than 1 week")
    elif duration_days > 365:
        warnings.append("Plan duration exceeds 1 year")
    
    # Check workouts
    if not plan.workouts:
        errors.append("Plan must contain at least 1 workout")
    
    # Validate workout dates within plan range
    for i, workout in enumerate(plan.workouts):
        if workout.date < plan.start_date:
            errors.append(f"Workout {i+1} date ({workout.date}) is before plan start date")
        if workout.date > plan.end_date:
            errors.append(f"Workout {i+1} date ({workout.date}) is after plan end date")
        
        # Validate structured steps if present
        if workout.structured_steps:
            step_orders = [step.step_order for step in workout.structured_steps]
            if len(step_orders) != len(set(step_orders)):
                errors.append(f"Workout {i+1} has duplicate step orders")
            if step_orders != sorted(step_orders):
                warnings.append(f"Workout {i+1} steps are not in order")
    
    # Check for reasonable workout distribution
    workout_dates = [w.date for w in plan.workouts]
    unique_dates = set(workout_dates)
    if len(workout_dates) != len(unique_dates):
        warnings.append("Some dates have multiple workouts")
    
    return ValidationResult(
        valid=len(errors) == 0,
        errors=errors,
        warnings=warnings
    )


def generate_plan_preview(plan_data: TrainingPlanImport) -> PlanPreview:
    """
    Generate preview data for imported plan.
    
    Args:
        plan_data: Parsed training plan data
        
    Returns:
        PlanPreview with summary statistics
    """
    plan = plan_data.training_plan
    
    # Calculate weeks
    duration_days = (plan.end_date - plan.start_date).days
    weeks = duration_days // 7 + (1 if duration_days % 7 > 0 else 0)
    
    # Calculate totals
    total_distance_km = sum(w.distance_km or 0 for w in plan.workouts)
    total_tss = sum(w.target_tss or 0 for w in plan.workouts)
    
    # Count workout types
    workout_type_breakdown = {}
    for workout in plan.workouts:
        workout_type = workout.workout_type
        workout_type_breakdown[workout_type] = workout_type_breakdown.get(workout_type, 0) + 1
    
    return PlanPreview(
        name=plan.name,
        start_date=plan.start_date,
        end_date=plan.end_date,
        sport_type=plan.sport_type,
        weeks=weeks,
        total_workouts=len(plan.workouts),
        total_distance_km=round(total_distance_km, 2),
        total_tss=total_tss,
        workout_type_breakdown=workout_type_breakdown
    )


async def import_training_plan(
    user_id: int,
    plan_data: TrainingPlanImport,
    db: AsyncSession
) -> ImportResponse:
    """
    Import validated training plan into database.
    
    Args:
        user_id: User ID
        plan_data: Validated training plan data
        db: Database session
        
    Returns:
        ImportResponse with created plan details
    """
    plan = plan_data.training_plan
    
    # Create TrainingPlan (inactive by default - user must manually activate)
    training_plan = TrainingPlan(
        user_id=user_id,
        name=plan.name,
        description=plan.description or "",
        start_date=plan.start_date,
        end_date=plan.end_date,
        sport_type=plan.sport_type,
        is_active=0  # Never auto-activate imported plans
    )
    
    db.add(training_plan)
    await db.flush()  # Get plan.id
    
    # Create Workouts
    workouts_created = 0
    for workout_data in plan.workouts:
        workout = Workout(
            training_plan_id=training_plan.id,
            date=workout_data.date,
            sport_type=workout_data.sport_type,
            workout_type=workout_data.workout_type,
            title=workout_data.title,
            description=workout_data.description or "",
            duration_minutes=workout_data.duration_minutes,
            distance_km=workout_data.distance_km,
            intensity_zone=workout_data.intensity_zone,
            target_tss=workout_data.target_tss,
            notes=workout_data.notes or ""
        )
        
        # Store structured steps as JSON if present
        if workout_data.structured_steps:
            steps_json = [step.model_dump() for step in workout_data.structured_steps]
            workout.structured_workout_json = json.dumps(steps_json)
        
        db.add(workout)
        workouts_created += 1
    
    await db.commit()
    
    return ImportResponse(
        plan_id=training_plan.id,
        name=training_plan.name,
        workouts_created=workouts_created,
        message=f"Successfully imported training plan with {workouts_created} workouts"
    )


async def generate_ai_prompt(
    user_id: int,
    config: Any,
    db: AsyncSession
) -> Dict[str, Any]:
    """
    Generate AI prompt with user's fitness data.
    
    Args:
        user_id: User ID
        config: Prompt generation configuration
        db: Database session
        
    Returns:
        Dict containing prompt and context data
    """
    # Fetch user's recent activities (last 6 weeks)
    six_weeks_ago = date.today() - timedelta(days=42)
    
    result = await db.execute(
        select(GarminActivity)
        .where(GarminActivity.user_id == user_id)
        .where(GarminActivity.start_time_local >= six_weeks_ago)
        .order_by(GarminActivity.start_time_local.desc())
    )
    recent_activities = result.scalars().all()
    
    # Calculate activity statistics
    total_distance_km = sum(a.distance_meters / 1000 for a in recent_activities if a.distance_meters)
    total_duration_hours = sum(a.duration_seconds / 3600 for a in recent_activities if a.duration_seconds)
    total_tss = sum(a.calculated_tss or 0 for a in recent_activities)
    avg_weekly_tss = total_tss / 6 if total_tss > 0 else 0
    
    # Get latest thresholds
    threshold_result = await db.execute(
        select(WeeklyThreshold)
        .where(WeeklyThreshold.user_id == user_id)
        .order_by(WeeklyThreshold.year.desc(), WeeklyThreshold.week.desc())
        .limit(1)
    )
    latest_threshold = threshold_result.scalar_one_or_none()
    
    # For CTL/ATL/TSB, we'd need to calculate them from all historical data
    # For now, provide a simple estimate based on recent TSS
    # (In production, these should come from a daily metrics table)
    estimated_ctl = avg_weekly_tss * 6  # Rough estimate: 6 weeks of average weekly TSS
    estimated_atl = total_tss / 6  # Last week's average
    estimated_tsb = estimated_ctl - estimated_atl
    
    # Build athlete data
    athlete_data = {
        "recent_volume_km": round(total_distance_km, 1),
        "recent_duration_hours": round(total_duration_hours, 1),
        "avg_weekly_tss": round(avg_weekly_tss, 1),
        "estimated_ctl": round(estimated_ctl, 1),
        "estimated_atl": round(estimated_atl, 1),
        "estimated_tsb": round(estimated_tsb, 1),
        "activity_count": len(recent_activities)
    }
    
    # Add thresholds if available
    if latest_threshold:
        athlete_data["running_threshold_pace"] = latest_threshold.threshold_pace
        athlete_data["running_threshold_hr"] = latest_threshold.running_threshold_hr
        athlete_data["cycling_ftp"] = latest_threshold.ftp
        athlete_data["max_hr"] = latest_threshold.max_hr
        athlete_data["resting_hr"] = latest_threshold.resting_hr
    
    # Build event details
    event_details = {
        "name": config.event_name or "Target Event",
        "date": str(config.event_date) if config.event_date else "TBD",
        "distance": config.event_distance or "Not specified",
        "goal_time": config.goal_time or "Not specified"
    }
    
    # Calculate plan duration
    if config.event_date:
        duration_days = (config.event_date - config.start_date).days
        duration_weeks = duration_days // 7
    else:
        duration_weeks = 16  # Default
    
    # Build plan config
    plan_config = {
        "start_date": str(config.start_date),
        "end_date": str(config.event_date) if config.event_date else str(config.start_date + timedelta(weeks=duration_weeks)),
        "duration_weeks": duration_weeks,
        "training_days_per_week": config.training_days_per_week,
        "preferred_training_days": config.preferred_training_days,
        "trainer_style": config.trainer_style,
        "custom_trainer_instructions": config.custom_trainer_instructions,
        "additional_notes": config.additional_notes or ""
    }
    
    # Generate prompt
    prompt = _build_prompt_text(athlete_data, event_details, plan_config)
    
    return {
        "prompt": prompt,
        "athlete_data": athlete_data,
        "event_details": event_details,
        "plan_config": plan_config
    }


def _build_prompt_text(athlete_data: Dict, event_details: Dict, plan_config: Dict) -> str:
    """Build the full prompt text."""
    
    prompt = f"""━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🏃 AI TRAINING PLAN GENERATION PROMPT
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

You are a professional endurance sports coach. Create a comprehensive, 
periodized training plan based on the athlete data below.


━━━ ATHLETE FITNESS DATA (Last 6 Weeks) ━━━
  • Total volume: {athlete_data['recent_volume_km']} km
  • Total training time: {athlete_data['recent_duration_hours']} hours  
  • Average weekly TSS: {athlete_data['avg_weekly_tss']}
  • CTL (Fitness): {athlete_data['estimated_ctl']}
  • ATL (Fatigue): {athlete_data['estimated_atl']}
  • TSB (Form): {athlete_data['estimated_tsb']}
  • Activities: {athlete_data['activity_count']}

━━━ CURRENT THRESHOLDS ━━━"""
    
    if 'running_threshold_pace' in athlete_data and athlete_data['running_threshold_pace']:
        pace_min_per_km = athlete_data['running_threshold_pace'] / 60
        prompt += f"\n  • Running threshold pace: {pace_min_per_km:.2f} min/km"
    if 'running_threshold_hr' in athlete_data and athlete_data['running_threshold_hr']:
        prompt += f"\n  • Running threshold HR: {athlete_data['running_threshold_hr']} bpm"
    if 'cycling_ftp' in athlete_data and athlete_data['cycling_ftp']:
        prompt += f"\n  • Cycling FTP: {athlete_data['cycling_ftp']} watts"
    if 'max_hr' in athlete_data and athlete_data['max_hr']:
        prompt += f"\n  • Max HR: {athlete_data['max_hr']} bpm"
    if 'resting_hr' in athlete_data and athlete_data['resting_hr']:
        prompt += f"\n  • Resting HR: {athlete_data['resting_hr']} bpm"
    
    prompt += f"""

━━━ TARGET EVENT ━━━
  • Event: {event_details['name']}
  • Date: {event_details['date']}
  • Distance: {event_details['distance']}
  • Goal time: {event_details['goal_time']}

━━━ PLAN REQUIREMENTS ━━━
  • Start date: {plan_config['start_date']}
  • End date: {plan_config['end_date']}
  • Duration: {plan_config['duration_weeks']} weeks
  • Training days/week: {plan_config['training_days_per_week']}
  • Preferred days: {', '.join(plan_config['preferred_training_days'])}
"""
    
    if plan_config['additional_notes']:
        prompt += f"\n━━━ ADDITIONAL NOTES ━━━\n{plan_config['additional_notes']}\n"
    
    # Add trainer-specific methodology
    trainer_style_id = plan_config.get('trainer_style', 'joe_friel')
    trainer_prompt = build_trainer_specific_prompt(trainer_style_id)
    prompt += trainer_prompt
    
    # Add custom trainer instructions if provided
    custom_instructions = plan_config.get('custom_trainer_instructions')
    if custom_instructions:
        prompt += f"""

━━━ CUSTOM TRAINING INSTRUCTIONS ━━━
{custom_instructions}

⚠️  Apply these custom instructions IN ADDITION TO the trainer methodology above.
"""
    
    # Add detailed workout instructions
    detailed_instructions = get_detailed_workout_instructions()
    prompt += detailed_instructions
    
    prompt += """

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📋 JSON OUTPUT FORMAT - CRITICAL!
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🚨 CRITICAL INSTRUCTION: PRODUCE A DOWNLOADABLE JSON FILE! 🚨

Your response will be SAVED AS A .JSON FILE by the user.
This means your output must be 100% VALID, PURE JSON.

⚠️  YOUR ENTIRE RESPONSE = THE CONTENTS OF THE .JSON FILE

✅ CORRECT OUTPUT (DOWNLOADABLE JSON):
   • First character: {{
   • Last character: }}
   • NOTHING ELSE - no explanations, no markdown, no commentary

❌ WRONG OUTPUT (NOT DOWNLOADABLE):
   • Starting with "Here's the JSON:" ❌
   • Wrapping in ```json or ``` markdown ❌
   • Adding explanations before/after ❌
   • Outputting just the workouts array ❌
   • Including comments or notes ❌

━━━ HOW TO FORMAT YOUR RESPONSE ━━━

Imagine the user will click "Download" on your response.
The file must open correctly in a JSON viewer.

✅ First line MUST be: {{ "trainingPlan": {{
✅ Last line MUST be: }} }}
✅ NO text before the opening {{
✅ NO text after the closing }}

REQUIRED JSON STRUCTURE:

{{
  "trainingPlan": {{
    "name": "YOUR PLAN NAME HERE",
    "description": "YOUR PLAN DESCRIPTION HERE",
    "startDate": "{plan_config['start_date']}",
    "endDate": "{plan_config['end_date']}",
    "sportType": "triathlon",
    "targetEvent": "{event_details['name']}",
    "workouts": [
      {{
        "date": "YYYY-MM-DD",
        "title": "Workout Title",
        "description": "Detailed workout description with warmup/intervals/cooldown",
        "sportType": "running",
        "workoutType": "easy",
        "durationMinutes": 45,
        "intensityZone": "zone2",
        "targetTSS": 40,
        "distanceKm": 7.5
      }},
      {{
        "date": "YYYY-MM-DD",
        "title": "Bike Threshold Intervals",
        "description": "Warmup: 15min easy spinning\\nMain: 3x12min at FTP with 5min recovery\\nCooldown: 10min easy",
        "sportType": "cycling",
        "workoutType": "interval",
        "durationMinutes": 90,
        "intensityZone": "zone4",
        "targetTSS": 75,
        "distanceKm": 35
      }}
    ]
  }}
}}

━━━ FIELD REFERENCE ━━━

Plan metadata (ALL REQUIRED):
  • name: descriptive plan name (e.g., "16-Week Marathon Build")
  • description: 2-3 sentence overview of plan approach
  • startDate: "{plan_config['start_date']}" (YYYY-MM-DD format)
  • endDate: "{plan_config['end_date']}" (YYYY-MM-DD format)
  • sportType: "triathlon" OR "running" OR "cycling" OR "swimming"
  • targetEvent: "{event_details['name']}"
  • workouts: [array of workout objects]

Each workout object (REQUIRED FIELDS):
  • date: "YYYY-MM-DD" (must be between start and end dates)
  • title: short workout name (e.g., "Long Run with MP Finish")
  • sportType: "running" / "cycling" / "swimming" / "strength" / "triathlon"
  • workoutType: "easy" / "tempo" / "interval" / "long" / "recovery" / "race"
  • durationMinutes: integer (total workout time)
  • targetTSS: integer (Training Stress Score - lowercase 'ss'!)

Each workout object (OPTIONAL BUT RECOMMENDED):
  • description: detailed instructions (warmup, main set, cooldown, notes)
  • distanceKm: float (planned distance in kilometers)
  • intensityZone: "zone1" / "zone2" / "zone3" / "zone4" / "zone5"

━━━ CRITICAL DATA TYPE RULES ━━━

✅ CORRECT:
  "durationMinutes": 60      ← number (no quotes)
  "targetTSS": 45            ← number (no quotes)
  "distanceKm": 10.5         ← number (no quotes)
  "date": "2024-01-15"       ← string (with quotes)

❌ WRONG:
  "durationMinutes": "60"    ← string (has quotes) - BREAKS IMPORT!
  "targetTSS": "45"          ← string (has quotes) - BREAKS IMPORT!

━━━ WORKOUT DISTRIBUTION RULES ━━━

✅ Plan MUST include:
  • ALL {plan_config['duration_weeks']} weeks (no gaps)
  • {plan_config['training_days_per_week']} workouts per week
  • Workouts on preferred days: {', '.join(plan_config['preferred_training_days'])}
  • Progressive build with periodization phases
  • Explicit taper phase (final 2-3 weeks before race)
  • Recovery weeks every 3-4 weeks

✅ Workout descriptions MUST include:
  • Warmup details (duration, intensity)
  • Main workout specifics (e.g., "5x1000m at threshold pace with 400m jog recovery")
  • Cooldown details (duration, intensity)
  • Notes (e.g., "Focus on negative splits", "Practice race nutrition")

━━━ VALIDATION CHECKLIST ━━━

Before submitting, verify:
  ✅ First character is: {{
  ✅ Last character is: }}
  ✅ NO markdown fences (```)
  ✅ NO explanatory text before/after JSON
  ✅ ALL dates in YYYY-MM-DD format
  ✅ ALL numeric fields are numbers (not strings)
  ✅ NO trailing commas
  ✅ All {plan_config['duration_weeks']} weeks have workouts
  ✅ Workouts progress logically (base → build → peak → taper)
  ✅ Each workout has detailed description
  ✅ Taper phase explicitly included

━━━ EXAMPLE OF WHAT USER WILL DO ━━━

1. User copies your ENTIRE response
2. User saves as "training_plan.json"
3. User uploads to Kinesis platform
4. System parses JSON and creates workouts

If your JSON is malformed, the import FAILS.
If you add text before/after JSON, the import FAILS.
If you use wrong data types, the import FAILS.

🎯 YOUR MISSION: Produce a PERFECT, DOWNLOADABLE JSON FILE!

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Generate the complete training plan now.

🚨 REMINDER: Your response IS the .json file contents!
    First character: {{
    Last character: }}
    NOTHING ELSE!
"""
    
    return prompt
