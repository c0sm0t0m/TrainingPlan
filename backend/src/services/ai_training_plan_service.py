"""
AI Training Plan Import Service
"""
import json
from datetime import date, timedelta
from typing import Dict, List, Any, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from src.models.training_plan import TrainingPlan, Workout
from src.models.user import User
from src.models.garmin_activity import GarminActivity
from src.models.weekly_threshold import WeeklyThreshold
from src.utils.calculations.planned_load import (
    AthleteThresholds,
    append_pace_label,
    pace_prescription_text,
    prepare_planned_session,
)
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
from src.services.plan_vs_actual import session_omits_distance
from src.services.ai_plan_phases import (
    compute_plan_phases,
    get_phase,
    distance_session_ceilings,
    format_pace_min_per_km,
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


async def load_athlete_thresholds(db: AsyncSession, user_id: int) -> AthleteThresholds:
    """FTP, run pace, and swim CSS from the user row. These override stale weekly rows."""
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        return AthleteThresholds()
    return AthleteThresholds(
        run_pace_sec_per_km=user.threshold_pace,
        ftp_watts=user.ftp,
        swim_pace_sec_per_100m=user.swim_threshold_pace,
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

    thresholds = await load_athlete_thresholds(db, user_id)
    
    # Create Workouts
    workouts_created = 0
    for workout_data in plan.workouts:
        steps_json = (
            [step.model_dump() for step in workout_data.structured_steps]
            if workout_data.structured_steps
            else []
        )
        steps_json, target_tss, distance_km, pace_label = prepare_planned_session(
            steps_json,
            sport=workout_data.sport_type,
            zone=workout_data.intensity_zone,
            workout_type=workout_data.workout_type,
            thresholds=thresholds,
        )
        description = append_pace_label(workout_data.description or "", pace_label)
        stored_distance = workout_data.distance_km
        if distance_km is not None:
            stored_distance = distance_km
        if session_omits_distance(workout_data.sport_type, steps_json, workout_data.duration_minutes):
            stored_distance = None
        workout = Workout(
            training_plan_id=training_plan.id,
            date=workout_data.date,
            sport_type=workout_data.sport_type,
            workout_type=workout_data.workout_type,
            title=workout_data.title,
            description=description,
            duration_minutes=workout_data.duration_minutes,
            distance_km=stored_distance,
            intensity_zone=workout_data.intensity_zone,
            target_tss=target_tss,
            notes=workout_data.notes or ""
        )
        
        if steps_json:
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
        Dict containing prompt, context, and phase metadata
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
    
    # Current settings on the user row. Weekly rows are historic and can be stale.
    user_result = await db.execute(select(User).where(User.id == user_id))
    user = user_result.scalar_one_or_none()
    threshold_result = await db.execute(
        select(WeeklyThreshold)
        .where(WeeklyThreshold.user_id == user_id)
        .order_by(WeeklyThreshold.year.desc(), WeeklyThreshold.week.desc())
        .limit(1)
    )
    latest_threshold = threshold_result.scalar_one_or_none()
    
    # Rough load estimates — labeled unreliable in the prompt (not true Banister CTL)
    estimated_ctl = avg_weekly_tss * 6
    estimated_atl = total_tss / 6
    estimated_tsb = estimated_ctl - estimated_atl
    
    athlete_data = {
        "recent_volume_km": round(total_distance_km, 1),
        "recent_duration_hours": round(total_duration_hours, 1),
        "avg_weekly_tss": round(avg_weekly_tss, 1),
        "estimated_ctl": round(estimated_ctl, 1),
        "estimated_atl": round(estimated_atl, 1),
        "estimated_tsb": round(estimated_tsb, 1),
        "activity_count": len(recent_activities),
        "ctl_reliable": False,
    }
    
    if user and user.threshold_pace:
        athlete_data["running_threshold_pace"] = user.threshold_pace
    elif latest_threshold and latest_threshold.threshold_pace:
        athlete_data["running_threshold_pace"] = latest_threshold.threshold_pace
    if user and user.swim_threshold_pace:
        athlete_data["swim_threshold_pace"] = user.swim_threshold_pace
    athlete_data["running_threshold_hr"] = (
        (user.running_threshold_hr if user else None)
        or (latest_threshold.running_threshold_hr if latest_threshold else None)
    )
    athlete_data["cycling_ftp"] = (
        (user.ftp if user else None)
        or (latest_threshold.ftp if latest_threshold else None)
    )
    athlete_data["max_hr"] = (
        (user.max_hr if user else None)
        or (latest_threshold.max_hr if latest_threshold else None)
    )
    athlete_data["resting_hr"] = (
        (user.resting_hr if user else None)
        or (latest_threshold.resting_hr if latest_threshold else None)
    )
    
    event_details = {
        "name": config.event_name or "Target Event",
        "date": str(config.event_date) if config.event_date else "TBD",
        "distance": config.event_distance or "Not specified",
        "goal_time": config.goal_time or "Not specified"
    }
    
    if config.event_date:
        duration_days = (config.event_date - config.start_date).days
        duration_weeks = max(1, duration_days // 7)
        end_date = config.event_date
    else:
        duration_weeks = 16
        end_date = config.start_date + timedelta(weeks=duration_weeks)
    
    generation_mode = getattr(config, "generation_mode", None) or "phased"
    if generation_mode not in ("full", "phased"):
        generation_mode = "phased"
    
    # Recommend phased for long plans (context limits)
    recommended_mode = "phased" if duration_weeks > 16 else "full"
    
    phases = compute_plan_phases(config.start_date, end_date)
    phase_index = getattr(config, "phase_index", None)
    if generation_mode == "phased":
        current = get_phase(phases, phase_index if phase_index is not None else 0)
        if current is None:
            current = phases[0] if phases else None
    else:
        current = None
    
    plan_config = {
        "start_date": str(config.start_date),
        "end_date": str(end_date),
        "duration_weeks": duration_weeks,
        "training_days_per_week": config.training_days_per_week,
        "preferred_training_days": config.preferred_training_days,
        "trainer_style": config.trainer_style,
        "custom_trainer_instructions": config.custom_trainer_instructions,
        "additional_notes": config.additional_notes or "",
        "generation_mode": generation_mode,
        "phase_index": current["index"] if current else None,
    }
    
    prompt = _build_prompt_text(
        athlete_data,
        event_details,
        plan_config,
        phases=phases,
        current_phase=current,
    )
    
    return {
        "prompt": prompt,
        "athlete_data": athlete_data,
        "event_details": event_details,
        "plan_config": plan_config,
        "generation_mode": generation_mode,
        "phases": phases,
        "current_phase": current,
        "recommended_mode": recommended_mode,
    }


def _build_prompt_text(
    athlete_data: Dict,
    event_details: Dict,
    plan_config: Dict,
    phases: Optional[List[Dict]] = None,
    current_phase: Optional[Dict] = None,
) -> str:
    """Build the full prompt text (ICU structuredSteps–first)."""
    phases = phases or []
    mode = plan_config.get("generation_mode", "full")
    ceilings = distance_session_ceilings(event_details.get("distance", ""))
    preferred = ", ".join(plan_config["preferred_training_days"])
    pace_str = format_pace_min_per_km(athlete_data.get("running_threshold_pace"))

    # Scope dates for this generation
    if mode == "phased" and current_phase:
        scope_start = current_phase["startDate"]
        scope_end = current_phase["endDate"]
        scope_label = (
            f"PHASE ONLY: {current_phase['name']} "
            f"(weeks {current_phase['weekStart']}–{current_phase['weekEnd']}, "
            f"{scope_start} → {scope_end})"
        )
        plan_name_hint = (
            f"{event_details['name']} — {current_phase['name']} "
            f"(Phase {current_phase['index'] + 1}/{len(phases)})"
        )
        workout_scope_rules = f"""
━━━ THIS REQUEST SCOPE (PHASED GENERATION) ━━━
Generate workouts ONLY for dates {scope_start} through {scope_end} inclusive.
Do NOT emit workouts outside this window.
JSON startDate/endDate MUST be {scope_start} / {scope_end}.
Plan name MUST include the phase: "{plan_name_hint}"
Include every preferred training day in this window ({plan_config['training_days_per_week']}/week on: {preferred}).
Phase focus: {current_phase['focus']}
Continue periodization consistently with the full-plan overview below
(assume prior phases already exist; do not re-generate them).
"""
    else:
        scope_start = plan_config["start_date"]
        scope_end = plan_config["end_date"]
        scope_label = f"FULL PLAN: {scope_start} → {scope_end} ({plan_config['duration_weeks']} weeks)"
        plan_name_hint = f"{event_details['name']} Training Plan"
        workout_scope_rules = f"""
━━━ THIS REQUEST SCOPE (FULL PLAN) ━━━
Generate the COMPLETE plan from {scope_start} through {scope_end}.
Include ALL {plan_config['duration_weeks']} weeks with no gaps.
{plan_config['training_days_per_week']} workouts/week on: {preferred}.
If context limits prevent a complete valid JSON, respond with:
{{"error":"context_limit","recommendedSplit":"phase"}}
instead of truncated JSON.
"""

    phase_overview = ""
    if phases:
        phase_overview = "\n━━━ FULL PLAN PHASE OVERVIEW ━━━\n"
        for p in phases:
            marker = " ← CURRENT" if current_phase and p["index"] == current_phase["index"] else ""
            phase_overview += (
                f"  • Phase {p['index'] + 1}: {p['name']} — "
                f"W{p['weekStart']}–W{p['weekEnd']} ({p['startDate']} → {p['endDate']}) — "
                f"{p['focus']}{marker}\n"
            )

    # Thresholds block
    thresholds_block = ""
    if pace_str:
        thresholds_block += f"\n  • Running threshold pace: {pace_str}"
    elif athlete_data.get("running_threshold_pace"):
        thresholds_block += (
            "\n  • Running threshold pace: INVALID/MISSING — "
            "use HR zones for run targets; do NOT invent absolute paces"
        )
    else:
        thresholds_block += (
            "\n  • Running threshold pace: not available — "
            "use HR zones for run targets"
        )
    if athlete_data.get("running_threshold_hr"):
        thresholds_block += f"\n  • Running threshold HR: {athlete_data['running_threshold_hr']} bpm"
    if athlete_data.get("cycling_ftp"):
        thresholds_block += f"\n  • Cycling FTP: {athlete_data['cycling_ftp']} watts"
    if athlete_data.get("swim_threshold_pace"):
        swim_sec = athlete_data["swim_threshold_pace"]
        thresholds_block += f"\n  • Swim CSS: {int(swim_sec) // 60}:{int(swim_sec) % 60:02d} /100m"
    if athlete_data.get("max_hr"):
        thresholds_block += f"\n  • Max HR: {athlete_data['max_hr']} bpm"
    if athlete_data.get("resting_hr"):
        thresholds_block += f"\n  • Resting HR: {athlete_data['resting_hr']} bpm"

    max_hr = athlete_data.get("max_hr") or 180
    thr_hr = athlete_data.get("running_threshold_hr") or int(max_hr * 0.92)
    run_pace_raw = athlete_data.get("running_threshold_pace")
    run_pace_sec = None
    if run_pace_raw:
        run_pace_sec = int(round(run_pace_raw * 60)) if run_pace_raw <= 20 else int(round(run_pace_raw))
    pace_rules = (
        pace_prescription_text(run_pace_sec)
        if run_pace_sec
        else "RUN PACES: threshold pace missing — do not invent absolute run paces."
    )

    notes_block = ""
    if plan_config.get("additional_notes"):
        notes_block = f"\n━━━ ADDITIONAL NOTES ━━━\n{plan_config['additional_notes']}\n"

    trainer_prompt = build_trainer_specific_prompt(plan_config.get("trainer_style", "joe_friel"))
    custom = plan_config.get("custom_trainer_instructions")
    custom_block = ""
    if custom:
        custom_block = f"""

━━━ CUSTOM TRAINING INSTRUCTIONS ━━━
{custom}

Apply these IN ADDITION TO the trainer methodology above.
"""

    detailed = get_detailed_workout_instructions()

    prompt = f"""━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
AI TRAINING PLAN GENERATION — KINESIS / INTERVALS.ICU
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

ROLE
You are a professional endurance coach. Produce a periodized training plan as
machine-parseable JSON for Kinesis (synced to Intervals.icu / Garmin).

OUTPUT CONTRACT (NON-NEGOTIABLE)
- Entire response = raw JSON only
- First character: {{   Last character: }}
- No markdown fences, no commentary, no partial workouts array
- Root key MUST be "trainingPlan"
- Every workout MUST include non-empty "structuredSteps"
- "description" = short human notes only (1–2 sentences)
- Session structure lives ONLY in structuredSteps

SCOPE: {scope_label}
{workout_scope_rules}
{phase_overview}

━━━ ATHLETE (last 6 weeks) ━━━
Use for load progression context. Do NOT invent missing metrics.
  • Total volume: {athlete_data['recent_volume_km']} km
  • Total training time: {athlete_data['recent_duration_hours']} hours
  • Average weekly TSS: {athlete_data['avg_weekly_tss']}
  • Activities: {athlete_data['activity_count']}
  • Rough load estimates (UNRELIABLE — ignore for periodization math):
      CTL≈{athlete_data['estimated_ctl']}, ATL≈{athlete_data['estimated_atl']}, TSB≈{athlete_data['estimated_tsb']}
  • Preserve recent capacity (~{athlete_data['recent_duration_hours'] / 6:.1f} h/week avg); do not dump volume suddenly

━━━ THRESHOLDS ━━━{thresholds_block}

{pace_rules}
BIKE: every cycling step is % of FTP ({athlete_data.get('cycling_ftp') or 'FTP'} W). targetUnit "%ftp". No absolute watts.
  Z1 <55% | Z2 56–75% | Z3/SS 76–90% | Z4 91–105% | Z5 >106%
SWIM: pace in sec/100m around the CSS above. Easy slower than CSS, quality at or slightly faster.
targetTSS may be 0. The app replaces it from these thresholds and the steps. Do not invent TSS.
HR (context only, not a run target): max {max_hr}, threshold ~{thr_hr}.

━━━ TARGET EVENT ━━━
  • Event: {event_details['name']}
  • Date: {event_details['date']}
  • Distance: {event_details['distance']}
  • Goal time: {event_details['goal_time']}

━━━ PLAN WINDOW ━━━
  • Full plan: {plan_config['start_date']} → {plan_config['end_date']} ({plan_config['duration_weeks']} weeks)
  • Training days/week: {plan_config['training_days_per_week']}
  • Preferred days: {preferred}
  • Days not listed = rest (omit workout objects on rest days)
{notes_block}
━━━ EVENT-SCALED SESSION CEILINGS ({ceilings['label']}) ━━━
Do NOT exceed these routinely (trainer templates that cite full-IM loads must be scaled):
  • Long bike: {ceilings['long_bike']}
  • Brick: {ceilings['brick']}
  • Race sim: {ceilings['race_sim']}
  • Long run: {ceilings['long_run']}
  • Heat: {ceilings['heat']}

{trainer_prompt}
{custom_block}
{detailed}

Intensity distribution (polarized-leaning unless trainer says otherwise):
  ~75–80% Z1–Z2 | ~15–20% Z3–Z4 | ≤5–8% Z5
Recovery weeks every 3–4 hard weeks (−30–40% volume, keep 1 short quality session).

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
JSON OUTPUT FORMAT
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

REQUIRED STRUCTURE (example pattern — expand to all workouts in scope):

{{
  "trainingPlan": {{
    "name": "{plan_name_hint}",
    "description": "2–3 sentence overview for this generation scope",
    "startDate": "{scope_start}",
    "endDate": "{scope_end}",
    "sportType": "triathlon",
    "targetEvent": "{event_details['name']}",
    "workouts": [
      {{
        "date": "YYYY-MM-DD",
        "title": "Aerobic Z2 Bike",
        "description": "Steady endurance; smooth cadence",
        "sportType": "cycling",
        "workoutType": "easy",
        "durationMinutes": 90,
        "intensityZone": "zone2",
        "targetTSS": 55,
        "structuredSteps": [
          {{
            "stepOrder": 1,
            "stepType": "warmup",
            "durationType": "time",
            "durationValue": 15,
            "durationUnit": "minutes",
            "targetType": "power",
            "targetValueLow": 50,
            "targetValueHigh": 60,
            "targetUnit": "%ftp",
            "description": "Easy spin"
          }},
          {{
            "stepOrder": 2,
            "stepType": "work",
            "durationType": "time",
            "durationValue": 60,
            "durationUnit": "minutes",
            "targetType": "power",
            "targetValueLow": 65,
            "targetValueHigh": 75,
            "targetUnit": "%ftp",
            "description": "Z2 endurance"
          }},
          {{
            "stepOrder": 3,
            "stepType": "cooldown",
            "durationType": "time",
            "durationValue": 15,
            "durationUnit": "minutes",
            "targetType": "power",
            "targetValueLow": 45,
            "targetValueHigh": 55,
            "targetUnit": "%ftp"
          }}
        ]
      }}
    ]
  }}
}}

For intervals (e.g. 3×15' sweetspot): EXPAND to sequential work/rest steps
(~88–92% FTP work, 45–55% rest) plus warmup/cooldown.

FIELD RULES
- Plan required: name, description, startDate, endDate, sportType, targetEvent, workouts
- Workout required: date, title, sportType, workoutType, durationMinutes, targetTSS, structuredSteps
- Optional: description, distanceKm, intensityZone, notes
- Cycling prescribed by time and power (%ftp or watts): omit distanceKm. Outdoor kilometres and speed depend on elevation, wind, and surface. Do not infer a target distance or km/h from watts. Run and swim may still use distanceKm.
- sportType: running|cycling|swimming|strength|triathlon
- workoutType: easy|tempo|interval|long|recovery|race|brick|strength
- Numbers are JSON numbers (not strings); dates YYYY-MM-DD; no trailing commas

VALIDATION CHECKLIST
  [ ] Pure JSON only
  [ ] trainingPlan wrapper
  [ ] Workouts only in scope dates; preferred days covered
  [ ] Every workout has structuredSteps length ≥ 2
  [ ] Bike steps use %ftp; run steps use pace sec/km from the threshold above
  [ ] Sessions respect event-scaled ceilings above

WHAT THE USER WILL DO
1. Save your entire response as a .json file
2. Upload to Kinesis → Import AI Plan (phase files can be merged)
3. Sync to Intervals.icu (uses structuredSteps)

MISSION: Emit valid downloadable JSON with structuredSteps on every workout.
First character: {{
Last character: }}
NOTHING ELSE!
"""
    return prompt
