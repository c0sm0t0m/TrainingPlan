"""
Training Plan Database Models
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, Date, Enum
from sqlalchemy.orm import relationship
import enum

from src.database import Base


class SportType(str, enum.Enum):
    """Sport types for training plans and workouts"""
    RUNNING = "running"
    CYCLING = "cycling"
    SWIMMING = "swimming"
    TRIATHLON = "triathlon"
    GYM = "gym"
    OTHER = "other"


class WorkoutType(str, enum.Enum):
    """Types of workouts"""
    EASY = "easy"
    TEMPO = "tempo"
    INTERVAL = "interval"
    LONG = "long"
    RECOVERY = "recovery"
    RACE = "race"
    BRICK = "brick"  # Triathlon multi-sport workout
    STRENGTH = "strength"


class IntensityZone(str, enum.Enum):
    """Training intensity zones"""
    ZONE1 = "zone1"  # Recovery
    ZONE2 = "zone2"  # Endurance
    ZONE3 = "zone3"  # Tempo
    ZONE4 = "zone4"  # Threshold
    ZONE5 = "zone5"  # VO2 Max
    ZONE6 = "zone6"  # Anaerobic


class TrainingPlan(Base):
    """Training plan model"""
    __tablename__ = "training_plans"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    name = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    sport_type = Column(String, nullable=False, default=SportType.RUNNING.value)
    is_active = Column(Integer, default=1)  # SQLite doesn't have native boolean
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="training_plans")
    workouts = relationship("Workout", back_populates="training_plan", cascade="all, delete-orphan")


class Workout(Base):
    """Workout model"""
    __tablename__ = "workouts"

    id = Column(Integer, primary_key=True, index=True)
    training_plan_id = Column(Integer, ForeignKey("training_plans.id"), nullable=False)
    date = Column(Date, nullable=False)
    sport_type = Column(String, nullable=False)
    workout_type = Column(String, nullable=False)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    
    # Workout metrics
    duration_minutes = Column(Integer, nullable=True)  # Planned duration in minutes
    distance_km = Column(Integer, nullable=True)  # Planned distance in km (stored as integer for simplicity)
    intensity_zone = Column(String, nullable=True)
    tss = Column(Integer, nullable=True)  # Training Stress Score (planned)
    
    # Completion tracking
    is_completed = Column(Integer, default=0)  # SQLite boolean
    actual_duration_minutes = Column(Integer, nullable=True)
    actual_distance_km = Column(Integer, nullable=True)
    notes = Column(Text, nullable=True)
    
    # Garmin sync tracking
    garmin_workout_id = Column(String, nullable=True)  # Garmin's workout ID
    garmin_synced_at = Column(DateTime, nullable=True)  # Last sync timestamp
    garmin_sync_status = Column(String, default="not_synced")  # not_synced, synced, failed, modified
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    training_plan = relationship("TrainingPlan", back_populates="workouts")
