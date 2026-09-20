"""
Garmin Activity Database Model
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Float, Boolean, Text, JSON
from sqlalchemy.orm import relationship

from src.database import Base


class GarminActivity(Base):
    """Garmin activity model - stores synced activities from Garmin Connect"""
    __tablename__ = "garmin_activities"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Garmin identifiers
    garmin_activity_id = Column(String, unique=True, nullable=False, index=True)
    
    # Basic info
    activity_name = Column(String, nullable=False)
    activity_type = Column(String, nullable=False)  # running, cycling, etc.
    sport_type_id = Column(Integer)
    
    # Timing
    start_time_local = Column(DateTime, nullable=False, index=True)
    start_time_gmt = Column(DateTime, nullable=False)
    duration_seconds = Column(Float)  # Total duration
    elapsed_duration_seconds = Column(Float)  # Including pauses
    moving_duration_seconds = Column(Float)  # Excluding pauses
    
    # Distance & Speed
    distance_meters = Column(Float)
    average_speed_mps = Column(Float)  # meters per second
    max_speed_mps = Column(Float)
    
    # Elevation
    elevation_gain_meters = Column(Float)
    elevation_loss_meters = Column(Float)
    min_elevation_meters = Column(Float)
    max_elevation_meters = Column(Float)
    
    # Heart Rate
    average_hr = Column(Integer)
    max_hr = Column(Integer)
    
    # Calories & Steps
    calories = Column(Integer)
    steps = Column(Integer)
    
    # Running specific
    average_cadence = Column(Float)  # steps per minute
    max_cadence = Column(Float)
    average_stride_length_meters = Column(Float)
    
    # Cycling specific (power)
    average_power_watts = Column(Float)
    max_power_watts = Column(Float)
    normalized_power_watts = Column(Float)  # Normalized Power (NP)
    threshold_power_watts = Column(Float)  # FTP
    
    # Training metrics
    aerobic_training_effect = Column(Float)
    anaerobic_training_effect = Column(Float)
    training_load = Column(Float)  # Garmin's training load
    calculated_tss = Column(Float)  # Our calculated TSS
    intensity_factor = Column(Float)  # Intensity Factor (IF) - workout intensity relative to threshold
    vo2_max = Column(Float)
    
    # Location
    location_name = Column(String)
    start_latitude = Column(Float)
    start_longitude = Column(Float)
    
    # Flags
    has_polyline = Column(Boolean, default=False)
    manual_activity = Column(Boolean, default=False)
    
    # Full activity data (JSON)
    raw_data = Column(JSON)  # Store complete Garmin response
    
    # Metadata
    synced_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationship to user
    user = relationship("User", back_populates="garmin_activities")
