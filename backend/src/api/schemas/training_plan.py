"""
Training Plan API Schemas
"""
from datetime import date, datetime
from typing import Optional, List
from pydantic import BaseModel, Field
from enum import Enum


class SportType(str, Enum):
    """Sport types"""
    RUNNING = "running"
    CYCLING = "cycling"
    SWIMMING = "swimming"
    TRIATHLON = "triathlon"
    GYM = "gym"
    OTHER = "other"


class WorkoutType(str, Enum):
    """Workout types"""
    BASE = "base"
    EASY = "easy"
    TEMPO = "tempo"
    INTERVAL = "interval"
    LONG = "long"
    RECOVERY = "recovery"
    RACE = "race"
    BRICK = "brick"
    STRENGTH = "strength"


class IntensityZone(str, Enum):
    """Intensity zones"""
    ZONE1 = "zone1"
    ZONE2 = "zone2"
    ZONE3 = "zone3"
    ZONE4 = "zone4"
    ZONE5 = "zone5"
    ZONE6 = "zone6"


# Workout Schemas
class WorkoutBase(BaseModel):
    """Base workout schema"""
    date: date
    sport_type: SportType
    workout_type: WorkoutType
    title: str
    description: Optional[str] = None
    duration_minutes: Optional[int] = None
    distance_km: Optional[float] = None
    intensity_zone: Optional[IntensityZone] = None
    tss: Optional[int] = None


class WorkoutCreate(WorkoutBase):
    """Schema for creating a workout"""
    pass


class WorkoutUpdate(BaseModel):
    """Schema for updating a workout"""
    date: Optional[date] = None
    sport_type: Optional[SportType] = None
    workout_type: Optional[WorkoutType] = None
    title: Optional[str] = None
    description: Optional[str] = None
    duration_minutes: Optional[int] = None
    distance_km: Optional[float] = None
    intensity_zone: Optional[IntensityZone] = None
    tss: Optional[int] = None
    is_completed: Optional[bool] = None
    actual_duration_minutes: Optional[int] = None
    actual_distance_km: Optional[float] = None
    notes: Optional[str] = None


class Workout(WorkoutBase):
    """Workout response schema"""
    id: int
    training_plan_id: int
    is_completed: bool
    actual_duration_minutes: Optional[int] = None
    actual_distance_km: Optional[float] = None
    notes: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# Training Plan Schemas
class TrainingPlanBase(BaseModel):
    """Base training plan schema"""
    name: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None
    start_date: date
    end_date: date
    sport_type: SportType


class TrainingPlanCreate(TrainingPlanBase):
    """Schema for creating a training plan"""
    pass


class TrainingPlanUpdate(BaseModel):
    """Schema for updating a training plan"""
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    sport_type: Optional[SportType] = None
    is_active: Optional[bool] = None


class TrainingPlan(TrainingPlanBase):
    """Training plan response schema"""
    id: int
    user_id: int
    is_active: bool
    created_at: datetime
    updated_at: datetime
    workouts: List[Workout] = []

    class Config:
        from_attributes = True


class TrainingPlanSummary(BaseModel):
    """Training plan summary (without workouts)"""
    id: int
    user_id: int
    name: str
    description: Optional[str] = None
    start_date: date
    end_date: date
    sport_type: SportType
    is_active: bool
    created_at: datetime
    updated_at: datetime
    workout_count: int = 0
    completed_count: int = 0

    class Config:
        from_attributes = True
