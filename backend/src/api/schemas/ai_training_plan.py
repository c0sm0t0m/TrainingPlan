"""
AI Training Plan Pydantic Schemas
"""
from datetime import date, datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, validator, ConfigDict, AliasChoices


# ===== Prompt Generation Schemas =====

class PromptGenerationConfig(BaseModel):
    """Configuration for AI prompt generation"""
    model_config = ConfigDict(populate_by_name=True)
    
    target_event_id: Optional[int] = Field(None, alias='targetEventId')
    event_name: Optional[str] = Field(None, alias='eventName')
    event_date: Optional[date] = Field(None, alias='eventDate')
    event_distance: Optional[str] = Field(None, alias='eventDistance')
    goal_time: Optional[str] = Field(None, alias='goalTime')
    start_date: date = Field(alias='startDate')
    training_days_per_week: int = Field(5, ge=3, le=7, alias='trainingDaysPerWeek')
    preferred_training_days: List[str] = Field(
        default=["monday", "tuesday", "thursday", "saturday", "sunday"],
        alias='preferredTrainingDays'
    )
    trainer_style: str = Field(
        default="joe_friel",
        alias='trainerStyle',
        description="Selected trainer methodology (e.g., joe_friel, mat_fitzgerald, etc.)"
    )
    custom_trainer_instructions: Optional[str] = Field(
        None,
        alias='customTrainerInstructions',
        description="Optional custom training philosophy to override/extend selected trainer style"
    )
    additional_notes: Optional[str] = Field(None, alias='additionalNotes')


class PromptGenerationResponse(BaseModel):
    """Response containing generated prompt"""
    model_config = ConfigDict(populate_by_name=True, by_alias=True)
    
    prompt: str
    athlete_data: Dict[str, Any] = Field(alias='athleteData')
    event_details: Dict[str, Any] = Field(alias='eventDetails')
    plan_config: Dict[str, Any] = Field(alias='planConfig')
# ===== Import Schemas =====

class WorkoutStep(BaseModel):
    """Structured workout step"""
    model_config = ConfigDict(populate_by_name=True)
    
    step_order: int = Field(ge=1, alias='stepOrder')
    step_type: str = Field(pattern="^(warmup|work|cooldown|rest|repeat)$", alias='stepType')
    duration_type: str = Field(pattern="^(time|distance|lap_button)$", alias='durationType')
    duration_value: Optional[float] = Field(None, alias='durationValue')
    duration_unit: Optional[str] = Field(None, pattern="^(seconds|minutes|meters|kilometers)$", alias='durationUnit')
    target_type: Optional[str] = Field(None, pattern="^(pace|heart_rate|power|cadence|open)$", alias='targetType')
    target_value_low: Optional[float] = Field(None, alias='targetValueLow')
    target_value_high: Optional[float] = Field(None, alias='targetValueHigh')
    target_unit: Optional[str] = Field(None, alias='targetUnit')
    description: Optional[str] = None
    repeat_count: Optional[int] = Field(None, ge=1, alias='repeatCount')


class ImportWorkout(BaseModel):
    """Workout data for import"""
    model_config = ConfigDict(populate_by_name=True)
    
    date: date
    title: str = Field(min_length=1)
    description: Optional[str] = None
    sport_type: str = Field(pattern="^(running|cycling|swimming|strength|brick|triathlon)$", alias='sportType')
    workout_type: str = Field(pattern="^(easy|tempo|interval|long|recovery|race|brick|strength)$", alias='workoutType')
    duration_minutes: Optional[int] = Field(None, ge=0, alias='durationMinutes')
    distance_km: Optional[float] = Field(None, ge=0, alias='distanceKm')
    intensity_zone: Optional[str] = Field(None, pattern="^(zone1|zone2|zone3|zone4|zone5|zone6)$", alias='intensityZone')
    target_tss: Optional[int] = Field(
        None, 
        ge=0, 
        validation_alias=AliasChoices('targetTss', 'targetTSS', 'target_tss'),
        serialization_alias='targetTss'
    )
    structured_steps: Optional[List[WorkoutStep]] = Field(None, alias='structuredSteps')
    notes: Optional[str] = None


class ImportTrainingPlan(BaseModel):
    """Training plan data for import"""
    model_config = ConfigDict(populate_by_name=True)
    
    name: str = Field(min_length=1, max_length=200)
    description: Optional[str] = None
    start_date: date = Field(alias='startDate')
    end_date: date = Field(alias='endDate')
    sport_type: str = Field(pattern="^(running|cycling|swimming|triathlon|gym)$", alias='sportType')
    target_event: Optional[str] = Field(None, alias='targetEvent')
    workouts: List[ImportWorkout] = Field(min_items=1)

    @validator('end_date')
    def end_date_after_start(cls, v, values):
        if 'start_date' in values and v <= values['start_date']:
            raise ValueError('end_date must be after start_date')
        return v


class TrainingPlanImport(BaseModel):
    """Root schema for import"""
    model_config = ConfigDict(populate_by_name=True)
    
    training_plan: ImportTrainingPlan = Field(alias="trainingPlan")


# ===== Validation & Preview Schemas =====

class ValidationResult(BaseModel):
    """Result of plan validation"""
    valid: bool
    errors: List[str] = []
    warnings: List[str] = []


class PlanPreview(BaseModel):
    """Preview data for imported plan"""
    model_config = ConfigDict(populate_by_name=True, by_alias=True)
    
    name: str
    start_date: date = Field(alias='startDate')
    end_date: date = Field(alias='endDate')
    sport_type: str = Field(alias='sportType')
    weeks: int
    total_workouts: int = Field(alias='totalWorkouts')
    total_distance_km: float = Field(alias='totalDistanceKm')
    total_tss: int = Field(alias='totalTss')
    workout_type_breakdown: Dict[str, int] = Field(alias='workoutTypeBreakdown')


class ImportResponse(BaseModel):
    """Response after successful import"""
    model_config = ConfigDict(populate_by_name=True, by_alias=True)
    
    plan_id: int = Field(alias='planId')
    name: str
    workouts_created: int = Field(alias='workoutsCreated')
    message: str
    plan_id: int
    name: str
    workouts_created: int
    message: str
